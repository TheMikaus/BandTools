#!/usr/bin/env python3
"""
Waveform View Backend Module

QQuickPaintedItem implementation for waveform rendering in QML.
Provides custom painting for waveform visualization with position tracking.
Includes spectrogram overlay support for frequency analysis.
"""

from typing import Optional, List
from pathlib import Path
import wave
import struct
from array import array
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, pyqtProperty, QPointF, Qt
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtQuick import QQuickPaintedItem

# Try to import numpy for FFT analysis
try:
    import numpy as np
    HAVE_NUMPY = True
except ImportError:
    HAVE_NUMPY = False
    np = None

# Try to import pydub for MP3 support
try:
    from pydub import AudioSegment
    HAVE_PYDUB = True
except ImportError:
    HAVE_PYDUB = False
    AudioSegment = None


class WaveformView(QQuickPaintedItem):
    """
    Custom QML item for rendering audio waveforms.
    
    Provides waveform visualization with playback position tracking,
    click-to-seek functionality, and theme-aware colors.
    """
    
    # Signals
    seekRequested = pyqtSignal(int)  # Position in milliseconds
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Waveform data
        self._peaks: List[List[float]] = []
        self._duration_ms: int = 0
        
        # Playback state
        self._position_ms: int = 0
        
        # Tempo/BPM for markers
        self._bpm: float = 0.0
        
        # Spectrogram data
        self._show_spectrogram: bool = False
        self._spectrogram_data: Optional[List] = None
        self._current_audio_file: str = ""
        
        # Colors (default dark theme)
        self._background_color = QColor("#1e1e1e")
        self._waveform_color = QColor("#4a9eff")
        self._playhead_color = QColor("#ff4444")
        self._axis_color = QColor("#3e3e3e")
        self._tempo_marker_color = QColor("#666666")
        
        # Enable mouse tracking for click-to-seek
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
        
        # Request repaint when size changes
        self.widthChanged.connect(self.update)
        self.heightChanged.connect(self.update)
    
    # ========== Properties for QML ==========
    
    def _get_peaks(self) -> List[List[float]]:
        return self._peaks
    
    def _set_peaks(self, peaks: List[List[float]]) -> None:
        if peaks != self._peaks:
            self._peaks = peaks if peaks else []
            self.update()
    
    peaks = pyqtProperty(list, _get_peaks, _set_peaks)
    
    def _get_duration_ms(self) -> int:
        return self._duration_ms
    
    def _set_duration_ms(self, duration: int) -> None:
        if duration != self._duration_ms:
            self._duration_ms = int(duration)
            self.update()
    
    durationMs = pyqtProperty(int, _get_duration_ms, _set_duration_ms)
    
    def _get_position_ms(self) -> int:
        return self._position_ms
    
    def _set_position_ms(self, position: int) -> None:
        if position != self._position_ms:
            self._position_ms = int(position)
            self.update()
    
    positionMs = pyqtProperty(int, _get_position_ms, _set_position_ms)
    
    def _get_background_color(self) -> QColor:
        return self._background_color
    
    def _set_background_color(self, color: QColor) -> None:
        self._background_color = color
        self.update()
    
    backgroundColor = pyqtProperty(QColor, _get_background_color, _set_background_color)
    
    def _get_waveform_color(self) -> QColor:
        return self._waveform_color
    
    def _set_waveform_color(self, color: QColor) -> None:
        self._waveform_color = color
        self.update()
    
    waveformColor = pyqtProperty(QColor, _get_waveform_color, _set_waveform_color)
    
    def _get_playhead_color(self) -> QColor:
        return self._playhead_color
    
    def _set_playhead_color(self, color: QColor) -> None:
        self._playhead_color = color
        self.update()
    
    playheadColor = pyqtProperty(QColor, _get_playhead_color, _set_playhead_color)
    
    def _get_axis_color(self) -> QColor:
        return self._axis_color
    
    def _set_axis_color(self, color: QColor) -> None:
        self._axis_color = color
        self.update()
    
    axisColor = pyqtProperty(QColor, _get_axis_color, _set_axis_color)
    
    def _get_bpm(self) -> float:
        return self._bpm
    
    def _set_bpm(self, bpm: float) -> None:
        if bpm != self._bpm:
            self._bpm = float(bpm) if bpm > 0 else 0.0
            self.update()
    
    bpm = pyqtProperty(float, _get_bpm, _set_bpm)
    
    def _get_tempo_marker_color(self) -> QColor:
        return self._tempo_marker_color
    
    def _set_tempo_marker_color(self, color: QColor) -> None:
        self._tempo_marker_color = color
        self.update()
    
    tempoMarkerColor = pyqtProperty(QColor, _get_tempo_marker_color, _set_tempo_marker_color)
    
    # ========== Painting ==========
    
    def paint(self, painter: QPainter) -> None:
        """Paint the waveform or spectrogram."""
        width = int(self.width())
        height = int(self.height())
        
        if width <= 0 or height <= 0:
            return
        
        # Fill background
        painter.fillRect(0, 0, width, height, self._background_color)
        
        # Draw spectrogram or waveform
        if self._show_spectrogram:
            # Compute spectrogram if not cached
            if self._spectrogram_data is None and self._current_audio_file:
                self._compute_spectrogram()
            
            # Draw spectrogram
            if self._spectrogram_data:
                self._draw_spectrogram(painter, width, height)
            else:
                # Fallback to waveform if spectrogram unavailable
                mid_y = height / 2
                painter.setPen(QPen(self._axis_color, 1))
                painter.drawLine(0, int(mid_y), width, int(mid_y))
                
                if self._peaks and len(self._peaks) > 0:
                    self._paint_waveform(painter, width, height, mid_y)
        else:
            # Draw center axis
            mid_y = height / 2
            painter.setPen(QPen(self._axis_color, 1))
            painter.drawLine(0, int(mid_y), width, int(mid_y))
            
            # Draw waveform if data available
            if self._peaks and len(self._peaks) > 0:
                self._paint_waveform(painter, width, height, mid_y)
        
        # Draw tempo markers if BPM is set (always on top)
        if self._bpm > 0 and self._duration_ms > 0:
            self._paint_tempo_markers(painter, width, height)
        
        # Draw playhead if position is set (always on top)
        if self._duration_ms > 0 and self._position_ms >= 0:
            self._paint_playhead(painter, width, height)
    
    def _paint_waveform(self, painter: QPainter, width: int, height: int, mid_y: float) -> None:
        """Paint the waveform peaks."""
        num_peaks = len(self._peaks)
        if num_peaks == 0:
            return
        
        # Calculate scale
        x_scale = width / num_peaks
        y_scale = (height / 2) * 0.9  # 90% of half-height for some padding
        
        # Draw waveform
        painter.setPen(QPen(self._waveform_color, 1))
        
        for i, peak in enumerate(self._peaks):
            if len(peak) < 2:
                continue
            
            min_val, max_val = peak[0], peak[1]
            
            x = int(i * x_scale)
            y_min = int(mid_y - (max_val * y_scale))
            y_max = int(mid_y - (min_val * y_scale))
            
            # Draw vertical line for this peak
            if y_max > y_min:
                painter.drawLine(x, y_min, x, y_max)
            else:
                # Single point
                painter.drawPoint(x, y_min)
    
    def _paint_playhead(self, painter: QPainter, width: int, height: int) -> None:
        """Paint the playback position indicator."""
        if self._duration_ms <= 0:
            return
        
        # Calculate playhead position
        progress = self._position_ms / self._duration_ms
        x = int(progress * width)
        
        # Draw playhead line
        painter.setPen(QPen(self._playhead_color, 2))
        painter.drawLine(x, 0, x, height)
    
    def _paint_tempo_markers(self, painter: QPainter, width: int, height: int) -> None:
        """Paint tempo/measure markers based on BPM."""
        if self._bpm <= 0 or self._duration_ms <= 0:
            return
        
        # Calculate measure duration in milliseconds (assuming 4/4 time signature)
        # 1 beat = 60,000ms / BPM
        # 1 measure (4 beats) = 4 * (60,000 / BPM) = 240,000 / BPM
        measure_duration_ms = 240000.0 / self._bpm
        
        # Calculate number of measures
        num_measures = int(self._duration_ms / measure_duration_ms)
        
        # Limit to 1000 measures for performance
        if num_measures > 1000:
            return
        
        # Draw measure markers
        pen = QPen(self._tempo_marker_color, 1, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        
        for i in range(1, num_measures + 1):
            measure_time_ms = i * measure_duration_ms
            if measure_time_ms > self._duration_ms:
                break
            
            # Calculate x position
            progress = measure_time_ms / self._duration_ms
            x = int(progress * width)
            
            # Draw vertical dashed line
            painter.drawLine(x, 0, x, height)
            
            # Draw measure number every 4 measures
            if i % 4 == 0:
                painter.setPen(QPen(self._tempo_marker_color, 1))
                painter.drawText(x + 2, 12, f"M{i}")
                pen = QPen(self._tempo_marker_color, 1, Qt.PenStyle.DashLine)
                painter.setPen(pen)
    
    # ========== Spectrogram Properties ==========
    
    def _get_show_spectrogram(self) -> bool:
        return self._show_spectrogram
    
    def _set_show_spectrogram(self, enabled: bool) -> None:
        if enabled != self._show_spectrogram:
            self._show_spectrogram = enabled
            self.update()
    
    showSpectrogram = pyqtProperty(bool, _get_show_spectrogram, _set_show_spectrogram)
    
    @pyqtSlot(str)
    def setAudioFile(self, file_path: str) -> None:
        """
        Set the current audio file for spectrogram computation.
        Clears cached spectrogram if file changes.
        """
        if file_path != self._current_audio_file:
            self._current_audio_file = file_path
            self._spectrogram_data = None
            if self._show_spectrogram:
                self.update()
    
    # ========== Mouse interaction ==========
    
    def mousePressEvent(self, event) -> None:
        """Handle mouse press for click-to-seek."""
        if self._duration_ms > 0:
            # Calculate position from click
            progress = event.pos().x() / self.width()
            position_ms = int(progress * self._duration_ms)
            
            # Clamp to valid range
            position_ms = max(0, min(position_ms, self._duration_ms))
            
            # Emit seek request
            self.seekRequested.emit(position_ms)
        
        super().mousePressEvent(event)
    
    # ========== Spectrogram Computation ==========
    
    def _compute_spectrogram(self) -> None:
        """
        Compute spectrogram using Short-Time Fourier Transform (STFT).
        
        Uses FFT analysis to convert time-domain audio to frequency domain.
        Stores result as 2D array (time x frequency) for visualization.
        """
        if not HAVE_NUMPY:
            print("NumPy not available - spectrogram disabled")
            return
        
        if not self._current_audio_file or not Path(self._current_audio_file).exists():
            print(f"Audio file not available: {self._current_audio_file}")
            return
        
        try:
            # Load audio samples
            samples, sample_rate = self._load_audio_samples(Path(self._current_audio_file))
            if not samples or len(samples) == 0:
                return
            
            # STFT parameters
            fft_size = 2048
            hop_length = 512
            freq_bins = 128
            
            # Frequency range: 60-8000 Hz (musical range)
            min_freq = 60
            max_freq = 8000
            
            # Calculate log-spaced frequency bins
            freq_range = np.logspace(np.log10(min_freq), np.log10(max_freq), freq_bins)
            
            # Convert to NumPy array
            audio_array = np.array(samples, dtype=np.float32)
            
            # Number of time frames
            num_frames = (len(audio_array) - fft_size) // hop_length + 1
            
            # Initialize spectrogram array
            spectrogram = np.zeros((num_frames, freq_bins), dtype=np.float32)
            
            # Hanning window for FFT
            window = np.hanning(fft_size)
            
            # Compute STFT
            for frame_idx in range(num_frames):
                start_idx = frame_idx * hop_length
                end_idx = start_idx + fft_size
                
                if end_idx > len(audio_array):
                    break
                
                # Extract windowed frame
                frame = audio_array[start_idx:end_idx] * window
                
                # Compute FFT
                fft = np.fft.rfft(frame)
                magnitude = np.abs(fft)
                
                # Convert frequency bins to indices
                freq_idx = (freq_range * fft_size / sample_rate).astype(np.int32)
                freq_idx = np.clip(freq_idx, 0, len(magnitude) - 1)
                
                # Map to log-spaced frequency bins
                for bin_idx, f_idx in enumerate(freq_idx):
                    if f_idx < len(magnitude):
                        spectrogram[frame_idx, bin_idx] = magnitude[f_idx]
            
            # Log compression for better visualization
            spectrogram = np.log1p(spectrogram * 100)
            
            # Normalize to 0-1 range
            max_val = spectrogram.max()
            if max_val > 0:
                spectrogram = spectrogram / max_val
            
            # Store as list for QML access
            self._spectrogram_data = spectrogram.tolist()
            
        except Exception as e:
            print(f"Failed to compute spectrogram: {e}")
            self._spectrogram_data = None
    
    def _load_audio_samples(self, path: Path) -> tuple:
        """
        Load audio samples from file for spectrogram computation.
        
        Returns:
            Tuple of (samples, sample_rate)
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
                
                # Convert to 16-bit
                data = array("h")
                if sw == 2:
                    data.frombytes(raw[: (len(raw)//2)*2])
                else:
                    # Simple conversion for other bit depths
                    num_samples = len(raw) // sw
                    for i in range(num_samples):
                        offset = i * sw
                        if sw == 1:
                            val = struct.unpack('B', raw[offset:offset+1])[0] - 128
                            data.append(val * 256)
                        elif sw == 3:
                            val = struct.unpack('<i', raw[offset:offset+3] + b'\x00')[0] >> 8
                            data.append(val // 256)
                        elif sw == 4:
                            val = struct.unpack('<i', raw[offset:offset+4])[0]
                            data.append(val // 65536)
                
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
                samples = [s / 32768.0 for s in data]
                return samples, sr
                
            except Exception as e:
                print(f"Failed to decode WAV file: {e}")
                return [], 44100
        
        # Try MP3 using pydub
        if HAVE_PYDUB:
            try:
                seg = AudioSegment.from_file(str(path))
                sr = seg.frame_rate
                ch = seg.channels
                raw = seg.get_array_of_samples()
                
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
                
                return samples, sr
                
            except Exception as e:
                print(f"Failed to decode audio file with pydub: {e}")
                return [], 44100
        
        return [], 44100
    
    def _draw_spectrogram(self, painter: QPainter, width: int, height: int) -> None:
        """
        Render spectrogram visualization with color gradient.
        
        Color mapping: Blue (low) -> Green -> Yellow -> Red (high)
        """
        if not self._spectrogram_data or len(self._spectrogram_data) == 0:
            return
        
        num_time_frames = len(self._spectrogram_data)
        num_freq_bins = len(self._spectrogram_data[0]) if num_time_frames > 0 else 0
        
        if num_time_frames == 0 or num_freq_bins == 0:
            return
        
        # Scale factors
        x_scale = width / num_time_frames
        y_scale = height / num_freq_bins
        
        # Draw spectrogram column by column
        for t_idx in range(num_time_frames):
            x = int(t_idx * x_scale)
            x_next = int((t_idx + 1) * x_scale)
            rect_width = max(1, x_next - x)
            
            for f_idx in range(num_freq_bins):
                # Get magnitude (0-1 range)
                magnitude = self._spectrogram_data[t_idx][f_idx]
                
                # Map magnitude to color (Blue -> Green -> Yellow -> Red)
                if magnitude < 0.33:
                    # Blue to Green
                    r = 0
                    g = int(magnitude * 3 * 255)
                    b = int((0.33 - magnitude) * 3 * 255)
                elif magnitude < 0.66:
                    # Green to Yellow
                    r = int((magnitude - 0.33) * 3 * 255)
                    g = 255
                    b = 0
                else:
                    # Yellow to Red
                    r = 255
                    g = int((1.0 - magnitude) * 3 * 255)
                    b = 0
                
                color = QColor(r, g, b)
                
                # Draw frequency bin (inverted y-axis: low freq at bottom)
                y_top = int(height - (f_idx + 1) * y_scale)
                y_bottom = int(height - f_idx * y_scale)
                rect_height = max(1, y_bottom - y_top)
                
                painter.fillRect(x, y_top, rect_width, rect_height, color)
