#!/usr/bin/env python3
"""
Waveform Engine Backend Module

Handles waveform generation and management for the AudioBrowser QML application.
Provides QML-accessible waveform data generation, caching, and progressive loading.
"""

import wave
import struct
from array import array
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QThread, QRunnable, QThreadPool
import json

# Try to import optional dependencies
try:
    import numpy as np
    HAVE_NUMPY = True
except ImportError:
    HAVE_NUMPY = False

try:
    from pydub import AudioSegment
    HAVE_PYDUB = True
except ImportError:
    HAVE_PYDUB = False
    AudioSegment = None


# Constants
WAVEFORM_COLUMNS = 2000
WAVEFORM_CACHE_FILE = ".waveform_cache.json"


def convert_audio_samples(data: bytes, old_width: int, new_width: int) -> bytes:
    """
    Convert audio samples from one width to another.
    Replacement for deprecated audioop.lin2lin().
    
    Args:
        data: Raw audio data as bytes
        old_width: Original sample width in bytes (1, 2, 3, or 4)
        new_width: Target sample width in bytes (1, 2, 3, or 4)
    
    Returns:
        Converted audio data as bytes
    """
    if old_width == new_width:
        return data
    
    # Format strings for struct: 'b'=int8, 'h'=int16, 'i'=int32
    old_fmt = {1: 'b', 2: 'h', 3: 'i', 4: 'i'}[old_width]
    new_fmt = {1: 'b', 2: 'h', 3: 'i', 4: 'i'}[new_width]
    
    # Calculate number of samples
    num_samples = len(data) // old_width
    
    # Unpack old samples
    if old_width == 3:
        # 24-bit samples need special handling
        samples = []
        for i in range(num_samples):
            byte_offset = i * 3
            # Little-endian 24-bit to int32
            sample_bytes = data[byte_offset:byte_offset+3] + b'\x00'
            sample = struct.unpack('<i', sample_bytes)[0]
            # Shift to get sign-extended 24-bit value
            sample = sample >> 8
            samples.append(sample)
    else:
        samples = list(struct.unpack(f'<{num_samples}{old_fmt}', data))
    
    # Scale samples to new width
    old_max = (1 << (old_width * 8 - 1)) - 1 if old_width < 4 else (1 << 23) - 1
    new_max = (1 << (new_width * 8 - 1)) - 1 if new_width < 4 else (1 << 23) - 1
    new_min = -(1 << (new_width * 8 - 1)) if new_width < 4 else -(1 << 23)
    
    if old_width != new_width:
        samples = [max(new_min, min(new_max, int(sample * new_max / old_max))) for sample in samples]
    
    # Pack new samples
    if new_width == 3:
        # 24-bit samples need special handling
        result = bytearray()
        for sample in samples:
            # Clamp to 24-bit range
            sample = max(-8388608, min(8388607, sample))
            # Convert to bytes (little-endian)
            sample_bytes = struct.pack('<i', sample << 8)[:3]
            result.extend(sample_bytes)
        return bytes(result)
    else:
        return struct.pack(f'<{num_samples}{new_fmt}', *samples)


class WaveformWorker(QObject):
    """Worker for generating waveform data in a background thread."""
    
    progress = pyqtSignal(int, int)  # current, total
    finished = pyqtSignal(str, list, int, int, int)  # path, peaks, duration_ms, size, mtime
    error = pyqtSignal(str, str)  # path, error_message
    
    def __init__(self, path: str, columns: int = WAVEFORM_COLUMNS):
        super().__init__()
        self._path = path
        self._columns = columns
        self._cancelled = False
    
    def cancel(self):
        """Cancel the waveform generation."""
        self._cancelled = True
    
    def run(self):
        """Generate waveform data for the audio file."""
        try:
            p = Path(self._path)
            if not p.exists():
                self.error.emit(self._path, "File not found")
                return
            
            # Decode audio samples
            samples, sample_rate, duration_ms = self._decode_audio_samples(p)
            
            if self._cancelled:
                return
            
            # Generate peaks progressively
            peaks = []
            chunk_size = 100
            total_chunks = (self._columns + chunk_size - 1) // chunk_size
            
            for chunk_idx, chunk_peaks in enumerate(self._compute_peaks_progressive(samples, self._columns, chunk_size)):
                if self._cancelled:
                    return
                
                start_idx, peak_data = chunk_peaks
                for min_val, max_val in peak_data:
                    peaks.append([float(min_val), float(max_val)])
                
                self.progress.emit(chunk_idx + 1, total_chunks)
            
            # Get file signature for caching
            stat = p.stat()
            size = stat.st_size
            mtime = int(stat.st_mtime)
            
            self.finished.emit(self._path, peaks, duration_ms, size, mtime)
            
        except Exception as e:
            self.error.emit(self._path, str(e))
    
    def _decode_audio_samples(self, path: Path) -> Tuple[List[float], int, int]:
        """
        Decode audio samples from file.
        
        Returns:
            Tuple of (samples, sample_rate, duration_ms)
        """
        suffix = path.suffix.lower()
        
        # Try WAV first (native support)
        if suffix in (".wav", ".wave"):
            try:
                with wave.open(str(path), "rb") as wf:
                    nch = wf.getnchannels()
                    sw = wf.getsampwidth()
                    sr = wf.getframerate()
                    nframes = wf.getnframes()
                    raw = wf.readframes(nframes)
                
                # Convert to 16-bit if needed
                if sw != 2:
                    try:
                        raw = convert_audio_samples(raw, sw, 2)
                        sw = 2
                    except Exception:
                        pass
                
                # Convert to array
                data = array("h")
                data.frombytes(raw[: (len(raw)//2)*2])
                
                # Convert to mono if stereo
                if nch > 1:
                    total = len(data) // nch
                    mono = array("h", [0]) * total
                    for i in range(total):
                        s = 0
                        base = i * nch
                        for c in range(nch):
                            s += data[base + c]
                        mono[i] = int(s / nch)
                    data = mono
                
                # Normalize to -1.0 to 1.0
                if HAVE_NUMPY:
                    arr = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                    samples = arr.tolist()
                else:
                    samples = [s / 32768.0 for s in data]
                
                dur_ms = int((len(samples) / sr) * 1000)
                return samples, sr, dur_ms
                
            except Exception as e:
                raise RuntimeError(f"Failed to decode WAV file: {e}")
        
        # Try MP3 using pydub
        if HAVE_PYDUB:
            try:
                seg = AudioSegment.from_file(str(path))
                sr = seg.frame_rate
                dur_ms = len(seg)
                ch = seg.channels
                raw = seg.get_array_of_samples()
                
                if HAVE_NUMPY:
                    arr = np.array(raw, dtype=np.int16).astype(np.float32)
                    if ch > 1:
                        arr = arr.reshape((-1, ch)).mean(axis=1)
                    samples = (arr / 32768.0).tolist()
                else:
                    ints = list(raw)
                    if ch > 1:
                        mono = []
                        for i in range(0, len(ints), ch):
                            s = 0
                            for c in range(ch):
                                s += ints[i + c]
                            mono.append(s / ch)
                        samples = [v / 32768.0 for v in mono]
                    else:
                        samples = [v / 32768.0 for v in ints]
                
                return samples, sr, dur_ms
                
            except Exception as e:
                # Check if this is an FFmpeg-related error
                error_msg = str(e).lower()
                if "ffmpeg" in error_msg or "decoder" in error_msg or "not found" in error_msg:
                    raise RuntimeError("No MP3 decoder found (install FFmpeg for pydub).")
                else:
                    raise RuntimeError(f"Failed to decode audio file: {e}")
        
        raise RuntimeError("Audio format not supported (WAV files work without pydub; MP3/other formats require pydub and FFmpeg).")
    
    def _compute_peaks_progressive(self, samples: List[float], columns: int, chunk: int):
        """
        Compute peaks progressively for mono audio.
        
        Yields:
            (start_index, peaks_data) where peaks_data = [[min, max], ...]
        """
        n = len(samples)
        if n == 0 or columns <= 0:
            yield 0, [[0.0, 0.0] for _ in range(max(1, columns))]
            return
        
        if HAVE_NUMPY:
            arr = np.asarray(samples, dtype=np.float32)
            idx = np.linspace(0, n, num=columns+1, dtype=np.int64)
            
            for start in range(0, columns, chunk):
                end = min(columns, start + chunk)
                out = []
                for i in range(start, end):
                    a, b = idx[i], idx[i+1]
                    if b > a:
                        seg = arr[a:b]
                        out.append([float(seg.min()), float(seg.max())])
                    else:
                        val = float(arr[min(a, n-1)])
                        out.append([val, val])
                yield start, out
        else:
            # Non-numpy implementation
            for start in range(0, columns, chunk):
                end = min(columns, start + chunk)
                out = []
                for i in range(start, end):
                    a = int((i * n) / columns)
                    b = int(((i+1) * n) / columns)
                    if b > a:
                        seg = samples[a:b]
                        out.append([min(seg), max(seg)])
                    else:
                        val = samples[min(a, n-1)]
                        out.append([val, val])
                yield start, out


class WaveformEngine(QObject):
    """
    Waveform generation engine for the AudioBrowser application.
    
    Provides waveform data generation, caching, and management with signals
    for QML integration.
    """
    
    # Signals for state changes
    waveformReady = pyqtSignal(str)  # file_path
    waveformProgress = pyqtSignal(str, int, int)  # file_path, current, total
    waveformError = pyqtSignal(str, str)  # file_path, error_message
    
    def __init__(self, parent=None):
        """Initialize the waveform engine."""
        super().__init__(parent)
        
        # Waveform cache: {file_path: {peaks, duration_ms, size, mtime}}
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_dir: Optional[Path] = None
        
        # Worker management
        self._workers: Dict[str, WaveformWorker] = {}
        self._threads: Dict[str, QThread] = {}
    
    @pyqtSlot(str)
    def setCacheDirectory(self, directory: str) -> None:
        """
        Set the cache directory for waveform data.
        
        Args:
            directory: Directory path where cache file will be stored
        """
        self._cache_dir = Path(directory) if directory else None
        if self._cache_dir:
            self._load_cache()
    
    @pyqtSlot(str)
    def generateWaveform(self, file_path: str) -> None:
        """
        Generate waveform data for an audio file.
        
        Args:
            file_path: Path to the audio file
        """
        # Check cache first
        if self._is_cached(file_path):
            self.waveformReady.emit(file_path)
            return
        
        # Cancel existing generation for this file
        if file_path in self._workers:
            self.cancelWaveform(file_path)
        
        # Create worker and thread
        worker = WaveformWorker(file_path)
        thread = QThread()
        
        # Connect signals
        worker.progress.connect(lambda cur, tot: self.waveformProgress.emit(file_path, cur, tot))
        worker.finished.connect(lambda path, peaks, dur, size, mtime: self._on_waveform_finished(path, peaks, dur, size, mtime))
        worker.error.connect(lambda path, err: self._on_waveform_error(path, err))
        worker.finished.connect(thread.quit)
        worker.error.connect(thread.quit)
        thread.finished.connect(thread.deleteLater)
        
        # Move worker to thread and start
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        
        self._workers[file_path] = worker
        self._threads[file_path] = thread
        
        thread.start()
    
    @pyqtSlot(str)
    def cancelWaveform(self, file_path: str) -> None:
        """
        Cancel waveform generation for a file.
        
        Args:
            file_path: Path to the audio file
        """
        if file_path in self._workers:
            worker = self._workers[file_path]
            worker.cancel()
            
            # Clean up
            if file_path in self._threads:
                thread = self._threads[file_path]
                thread.quit()
                thread.wait(1000)  # Wait up to 1 second
                
            del self._workers[file_path]
            if file_path in self._threads:
                del self._threads[file_path]
    
    @pyqtSlot(str, result=bool)
    def isWaveformReady(self, file_path: str) -> bool:
        """
        Check if waveform data is ready for a file.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            True if waveform data is available
        """
        return self._is_cached(file_path)
    
    @pyqtSlot(str, result=list)
    def getWaveformData(self, file_path: str) -> List[List[float]]:
        """
        Get waveform peak data for a file.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            List of [min, max] peak pairs, or empty list if not available
        """
        if file_path in self._cache:
            return self._cache[file_path].get("peaks", [])
        return []
    
    @pyqtSlot(str, result=int)
    def getWaveformDuration(self, file_path: str) -> int:
        """
        Get the duration of the waveform in milliseconds.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Duration in milliseconds, or 0 if not available
        """
        if file_path in self._cache:
            return self._cache[file_path].get("duration_ms", 0)
        return 0
    
    @pyqtSlot()
    def clearCache(self) -> None:
        """Clear the waveform cache."""
        self._cache.clear()
        self._save_cache()
    
    # ========== Private methods ==========
    
    def _is_cached(self, file_path: str) -> bool:
        """Check if waveform is cached and still valid."""
        if file_path not in self._cache:
            return False
        
        # Validate cache entry
        try:
            p = Path(file_path)
            if not p.exists():
                return False
            
            stat = p.stat()
            cached = self._cache[file_path]
            
            # Check if file has been modified
            if cached.get("size") != stat.st_size or cached.get("mtime") != int(stat.st_mtime):
                del self._cache[file_path]
                return False
            
            return True
        except Exception:
            return False
    
    def _on_waveform_finished(self, file_path: str, peaks: List[List[float]], 
                             duration_ms: int, size: int, mtime: int) -> None:
        """Handle waveform generation completion."""
        # Store in cache
        self._cache[file_path] = {
            "peaks": peaks,
            "duration_ms": duration_ms,
            "size": size,
            "mtime": mtime
        }
        
        # Save cache
        self._save_cache()
        
        # Clean up worker
        if file_path in self._workers:
            del self._workers[file_path]
        if file_path in self._threads:
            del self._threads[file_path]
        
        # Emit ready signal
        self.waveformReady.emit(file_path)
    
    def _on_waveform_error(self, file_path: str, error_message: str) -> None:
        """Handle waveform generation error."""
        # Clean up worker
        if file_path in self._workers:
            del self._workers[file_path]
        if file_path in self._threads:
            del self._threads[file_path]
        
        # Emit error signal
        self.waveformError.emit(file_path, error_message)
    
    def _load_cache(self) -> None:
        """Load waveform cache from disk."""
        if not self._cache_dir:
            return
        
        cache_file = self._cache_dir / WAVEFORM_CACHE_FILE
        if not cache_file.exists():
            return
        
        try:
            with open(cache_file, "r") as f:
                self._cache = json.load(f)
        except Exception:
            self._cache = {}
    
    def _save_cache(self) -> None:
        """Save waveform cache to disk."""
        if not self._cache_dir:
            return
        
        cache_file = self._cache_dir / WAVEFORM_CACHE_FILE
        try:
            with open(cache_file, "w") as f:
                json.dump(self._cache, f, indent=2)
        except Exception:
            pass  # Ignore cache save errors
