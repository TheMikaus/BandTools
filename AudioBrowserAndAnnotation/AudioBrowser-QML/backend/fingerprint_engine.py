"""
Audio Fingerprinting Engine for AudioBrowser QML

This module provides audio fingerprinting functionality including:
- Multiple fingerprinting algorithms (spectral, lightweight, chromaprint, audfprint)
- Cross-folder matching
- Fingerprint cache management
- Background fingerprint generation
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QThread

# Ensure numpy is available
def _ensure_import(mod_name: str, pip_name: str | None = None) -> bool:
    """Try to import a module, installing it if necessary."""
    if pip_name is None:
        pip_name = mod_name
    
    try:
        __import__(mod_name)
        return True
    except ImportError:
        print(f"Installing {pip_name}...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
        __import__(mod_name)
        return True

HAVE_NUMPY = _ensure_import("numpy", "numpy")

if HAVE_NUMPY:
    import numpy as np

# Constants
FINGERPRINTS_JSON = ".audio_fingerprints.json"
DEFAULT_ALGORITHM = "spectral"


# ========== Audio fingerprinting functions ==========

def compute_audio_fingerprint(samples: List[float], sr: int) -> List[float]:
    """
    Compute a simple audio fingerprint using spectral features.
    Returns a list of float values representing the audio's spectral signature.
    """
    if HAVE_NUMPY:
        arr = np.asarray(samples, dtype=np.float32)
        
        # Use shorter segments for better temporal resolution
        segment_length = min(sr // 2, len(arr) // 8)  # 0.5 second or 1/8 of file
        if segment_length < 1024:
            segment_length = min(1024, len(arr))
        
        fingerprint = []
        
        # Process overlapping segments
        hop_length = segment_length // 4
        for i in range(0, len(arr) - segment_length + 1, hop_length):
            segment = arr[i:i + segment_length]
            
            # Apply window to reduce spectral leakage
            window = np.hanning(len(segment))
            windowed = segment * window
            
            # Compute FFT
            fft = np.fft.rfft(windowed)
            magnitude = np.abs(fft)
            
            # Divide into frequency bands (like simplified MFCCs)
            n_bands = 12
            band_size = len(magnitude) // n_bands
            band_energies = []
            
            for b in range(n_bands):
                start = b * band_size
                end = (b + 1) * band_size if b < n_bands - 1 else len(magnitude)
                if end > start:
                    energy = float(np.mean(magnitude[start:end]))
                else:
                    energy = 0.0
                band_energies.append(energy)
            
            # Normalize by total energy to make it volume-independent
            total_energy = sum(band_energies)
            if total_energy > 0:
                band_energies = [e / total_energy for e in band_energies]
            
            fingerprint.extend(band_energies)
        
        # Limit fingerprint length to avoid huge files
        max_len = 144  # 12 bands * 12 segments max
        if len(fingerprint) > max_len:
            # Downsample by averaging consecutive groups
            group_size = len(fingerprint) // max_len
            downsampled = []
            for i in range(0, len(fingerprint), group_size):
                group = fingerprint[i:i + group_size]
                downsampled.append(sum(group) / len(group) if group else 0.0)
            fingerprint = downsampled[:max_len]
        
        return fingerprint
    else:
        # Fallback without numpy - very basic
        n_bands = 12
        segment_length = min(sr, len(samples) // 4)
        if segment_length < 512:
            segment_length = min(512, len(samples))
        
        fingerprint = []
        for i in range(0, len(samples) - segment_length + 1, segment_length // 2):
            segment = samples[i:i + segment_length]
            
            # Simple frequency analysis without FFT
            band_energies = [0.0] * n_bands
            for j, sample in enumerate(segment):
                # Rough frequency mapping based on position
                band = min(n_bands - 1, j * n_bands // len(segment))
                band_energies[band] += abs(sample)
            
            # Normalize
            total = sum(band_energies)
            if total > 0:
                band_energies = [e / total for e in band_energies]
            
            fingerprint.extend(band_energies)
        
        return fingerprint[:144]  # Limit length


def compare_fingerprints(fp1: List[float], fp2: List[float]) -> float:
    """
    Compare two fingerprints and return similarity score (0.0 to 1.0).
    Higher values indicate more similarity.
    
    Note: This function assumes both fingerprints were generated using the same algorithm.
    The calling code is responsible for ensuring algorithm consistency.
    """
    if not fp1 or not fp2:
        return 0.0
    
    # Safety check: warn if fingerprints have very different lengths
    len1, len2 = len(fp1), len(fp2)
    if abs(len1 - len2) > max(len1, len2) * 0.5:  # More than 50% size difference
        print(f"Warning: Comparing fingerprints of very different lengths ({len1} vs {len2}). "
              f"This might indicate different algorithms were used.")
    
    # Align lengths by truncating to shorter
    min_len = min(len1, len2)
    fp1_trunc = fp1[:min_len]
    fp2_trunc = fp2[:min_len]
    
    if HAVE_NUMPY:
        arr1 = np.asarray(fp1_trunc)
        arr2 = np.asarray(fp2_trunc)
        
        # Compute cosine similarity
        dot_product = np.dot(arr1, arr2)
        norm1 = np.linalg.norm(arr1)
        norm2 = np.linalg.norm(arr2)
        
        if norm1 > 0 and norm2 > 0:
            return float(dot_product / (norm1 * norm2))
        else:
            return 0.0
    else:
        # Manual cosine similarity
        dot_product = sum(a * b for a, b in zip(fp1_trunc, fp2_trunc))
        norm1 = sum(a * a for a in fp1_trunc) ** 0.5
        norm2 = sum(b * b for b in fp2_trunc) ** 0.5
        
        if norm1 > 0 and norm2 > 0:
            return dot_product / (norm1 * norm2)
        else:
            return 0.0


# ========== Multiple fingerprinting algorithms ==========

def compute_spectral_fingerprint(samples: List[float], sr: int) -> List[float]:
    """
    Original spectral analysis fingerprinting algorithm (renamed for clarity).
    This is the same as the original compute_audio_fingerprint function.
    """
    return compute_audio_fingerprint(samples, sr)


def compute_lightweight_fingerprint(samples: List[float], sr: int) -> List[float]:
    """
    Lightweight fingerprint using downsampled STFT with log-spaced frequency bands.
    """
    if not HAVE_NUMPY:
        # Simple fallback - just return fixed-size vector
        return [0.1] * 32
        
    arr = np.asarray(samples, dtype=np.float32)
    
    # Target sample rate ~11kHz
    target_sr = 11025
    if sr > target_sr:
        # Simple decimation by taking every nth sample
        decim_factor = sr // target_sr
        arr = arr[::decim_factor]
        effective_sr = sr // decim_factor
    else:
        effective_sr = sr
    
    # Take middle 60 seconds max (more stable than intros/outros)
    max_samples = 60 * effective_sr  # 60 seconds worth
    if len(arr) > max_samples:
        start_idx = (len(arr) - max_samples) // 2
        arr = arr[start_idx:start_idx + max_samples]
    
    # STFT parameters
    n_fft = 2048
    hop_length = n_fft // 4
    
    # Frequency range: 60-6000 Hz
    min_freq = 60
    max_freq = min(6000, effective_sr // 2)  # Don't exceed Nyquist
    
    # Create 32 log-spaced frequency bands
    n_bands = 32
    freq_bins = np.logspace(np.log10(min_freq), np.log10(max_freq), n_bands + 1)
    
    # Convert frequencies to FFT bin indices
    bin_indices = (freq_bins * n_fft / effective_sr).astype(int)
    bin_indices = np.clip(bin_indices, 0, n_fft // 2)
    
    # Process overlapping windows for STFT
    window = np.hanning(n_fft)
    frame_energies = []
    
    for i in range(0, len(arr) - n_fft + 1, hop_length):
        frame = arr[i:i + n_fft] * window
        fft = np.fft.rfft(frame)
        magnitude = np.abs(fft)
        
        # Group into log-spaced frequency bands
        frame_bands = []
        for b in range(n_bands):
            start_bin = bin_indices[b]
            end_bin = bin_indices[b + 1]
            if end_bin > start_bin:
                # Average magnitude in this frequency band
                band_energy = float(np.mean(magnitude[start_bin:end_bin]))
            else:
                band_energy = 0.0
            frame_bands.append(band_energy)
        
        frame_energies.append(frame_bands)
    
    if not frame_energies:
        return [0.0] * n_bands
    
    # Average over time (all frames)
    frame_energies = np.array(frame_energies)
    avg_bands = np.mean(frame_energies, axis=0)
    
    # Apply log compression and normalization
    avg_bands = np.log1p(avg_bands)  # log(1 + x) to handle zeros
    
    # Normalize to unit vector for cosine similarity
    norm = np.linalg.norm(avg_bands)
    if norm > 0:
        avg_bands = avg_bands / norm
    
    return avg_bands.tolist()


def compute_chromaprint_fingerprint(samples: List[float], sr: int) -> List[float]:
    """
    ChromaPrint-inspired fingerprint algorithm.
    """
    if not HAVE_NUMPY:
        # Simple fallback without numpy
        return [float(i % 12) / 12.0 for i in range(144)]  # 12 chroma * 12 frames
        
    arr = np.asarray(samples, dtype=np.float32)
    
    # ChromaPrint-style parameters
    frame_size = 4096  # Frame size for FFT
    hop_length = frame_size // 4  # 75% overlap
    
    # Chroma parameters
    n_chroma = 12  # 12 semitones
    min_frequency = 80.0  # Minimum frequency to consider (Hz)
    max_frequency = min(sr // 2, 5000.0)  # Maximum frequency
    
    # Create frequency to chroma mapping
    def freq_to_chroma(freq):
        """Convert frequency to chroma class (0-11)"""
        if freq <= 0:
            return 0
        # A4 (440 Hz) = note 69 in MIDI, which is chroma class 9 (A)
        note_number = 12 * np.log2(freq / 440.0) + 69
        chroma_class = int(note_number) % 12
        return chroma_class
    
    chroma_frames = []
    window = np.hanning(frame_size)
    
    for i in range(0, len(arr) - frame_size + 1, hop_length):
        frame = arr[i:i + frame_size] * window
        fft = np.fft.rfft(frame)
        magnitude = np.abs(fft)
        
        # Initialize chroma bins
        chroma_bins = np.zeros(n_chroma)
        
        # Map FFT bins to chroma classes
        for bin_idx in range(len(magnitude)):
            freq = bin_idx * sr / frame_size
            if min_frequency <= freq <= max_frequency:
                chroma_class = freq_to_chroma(freq)
                chroma_bins[chroma_class] += magnitude[bin_idx]
        
        # Normalize chroma vector
        norm = np.linalg.norm(chroma_bins)
        if norm > 0:
            chroma_bins = chroma_bins / norm
        
        chroma_frames.append(chroma_bins.tolist())
        
        # Limit to 12 frames for consistent size
        if len(chroma_frames) >= 12:
            break
    
    # Flatten to single vector
    fingerprint = []
    for frame in chroma_frames:
        fingerprint.extend(frame)
    
    # Pad if needed
    target_size = 144  # 12 chroma * 12 frames
    while len(fingerprint) < target_size:
        fingerprint.append(0.0)
    
    return fingerprint[:target_size]


def compute_audfprint_fingerprint(samples: List[float], sr: int) -> List[float]:
    """
    AudFprint-inspired constellation fingerprint algorithm.
    """
    if not HAVE_NUMPY:
        # Simple fallback without numpy
        return [float((i * 7 + 13) % 256) / 256.0 for i in range(256)]
        
    arr = np.asarray(samples, dtype=np.float32)
    
    # AudFprint-style parameters
    frame_size = 2048  # Frame size for STFT
    hop_length = frame_size // 4  # 75% overlap
    n_peaks_per_frame = 5  # Number of peaks to extract per frame
    
    # Frequency range for peak detection
    min_freq_bin = int(300 * frame_size / sr)  # ~300 Hz minimum
    max_freq_bin = int(2000 * frame_size / sr)  # ~2000 Hz maximum
    max_freq_bin = min(max_freq_bin, frame_size // 2)
    
    # Peak detection parameters
    peak_threshold_ratio = 0.3  # Minimum relative magnitude for peaks
    
    constellation_points = []  # List of (time_frame, freq_bin, magnitude) tuples
    window = np.hanning(frame_size)
    
    # Step 1: Create spectrogram and extract peaks
    time_frame = 0
    for i in range(0, len(arr) - frame_size + 1, hop_length):
        frame = arr[i:i + frame_size] * window
        
        # Compute FFT
        fft_result = np.fft.rfft(frame)
        magnitude = np.abs(fft_result)
        
        # Find local maxima (peaks) in the specified frequency range
        peaks = []
        for j in range(min_freq_bin + 2, min(max_freq_bin, len(magnitude) - 2)):
            # Check if this bin is a local maximum
            if (magnitude[j] > magnitude[j-1] and 
                magnitude[j] > magnitude[j+1] and
                magnitude[j] > magnitude[j-2] and 
                magnitude[j] > magnitude[j+2]):
                
                # Check if magnitude is above threshold
                frame_max = np.max(magnitude[min_freq_bin:max_freq_bin])
                if magnitude[j] > peak_threshold_ratio * frame_max:
                    peaks.append((j, magnitude[j]))
        
        # Sort peaks by magnitude and take the strongest ones
        peaks.sort(key=lambda x: x[1], reverse=True)
        top_peaks = peaks[:n_peaks_per_frame]
        
        # Add peaks to constellation
        for freq_bin, mag in top_peaks:
            constellation_points.append((time_frame, freq_bin, mag))
        
        time_frame += 1
    
    if len(constellation_points) < 2:
        return [0.0] * 256  # Fallback if no peaks found
    
    # Step 2: Create hash pairs from constellation points
    hash_features = []
    max_time_delta = 10  # Maximum time difference for hash pairs
    
    for i, (t1, f1, m1) in enumerate(constellation_points):
        # Create hash pairs with nearby points
        anchor_hashes = []
        
        for j, (t2, f2, m2) in enumerate(constellation_points[i+1:], i+1):
            time_delta = t2 - t1
            
            # Only consider points within reasonable time distance
            if time_delta > max_time_delta:
                break
            
            if time_delta > 0:  # Ensure we're looking forward in time
                # Create hash from frequency pair and time delta
                freq_hash = (f1 * 1000 + f2) % 65536  # Frequency pair hash
                time_hash = time_delta * 4096  # Time delta component
                combined_hash = (freq_hash + time_hash) % 65536
                
                # Normalize to 0-1 range
                normalized_hash = combined_hash / 65536.0
                anchor_hashes.append(normalized_hash)
        
        # Limit number of hashes per anchor point
        anchor_hashes = anchor_hashes[:8]  # Max 8 hashes per anchor
        hash_features.extend(anchor_hashes)
        
        # Stop if we have enough hash features
        if len(hash_features) >= 256:
            break
    
    # Step 3: Create consistent-sized fingerprint
    target_size = 256  # Audfprint-style size
    
    if len(hash_features) > target_size:
        # Use statistical sampling to maintain diversity
        step = len(hash_features) / target_size
        sampled = [hash_features[int(i * step)] for i in range(target_size)]
        return sampled
    elif len(hash_features) < target_size:
        # Pad with derived values to maintain some structure
        padding = []
        for i in range(target_size - len(hash_features)):
            # Create synthetic hash values based on existing ones
            if hash_features:
                base_idx = i % len(hash_features)
                synthetic_hash = (hash_features[base_idx] + i * 0.001) % 1.0
                padding.append(synthetic_hash)
            else:
                padding.append(float(i) / target_size)
        
        return hash_features + padding
    else:
        return hash_features


# Dictionary of available algorithms
FINGERPRINT_ALGORITHMS = {
    "spectral": {
        "name": "Spectral Analysis",
        "description": "Original spectral band analysis (default)",
        "compute_func": compute_spectral_fingerprint
    },
    "lightweight": {
        "name": "Lightweight STFT", 
        "description": "Downsampled STFT with log-spaced bands",
        "compute_func": compute_lightweight_fingerprint
    },
    "chromaprint": {
        "name": "ChromaPrint-style",
        "description": "Chroma-based fingerprinting with pitch class mapping",
        "compute_func": compute_chromaprint_fingerprint
    },
    "audfprint": {
        "name": "AudFprint-style",
        "description": "Constellation approach with spectral peak hashing", 
        "compute_func": compute_audfprint_fingerprint
    }
}


def compute_multiple_fingerprints(samples: List[float], sr: int, algorithms: List[str] = None) -> Dict[str, List[float]]:
    """
    Compute fingerprints using multiple algorithms.
    
    Args:
        samples: Audio sample data
        sr: Sample rate
        algorithms: List of algorithm names to compute. If None, computes all.
    
    Returns:
        Dictionary mapping algorithm names to fingerprint lists
    """
    if algorithms is None:
        algorithms = list(FINGERPRINT_ALGORITHMS.keys())
    
    fingerprints = {}
    for alg_name in algorithms:
        if alg_name in FINGERPRINT_ALGORITHMS:
            compute_func = FINGERPRINT_ALGORITHMS[alg_name]["compute_func"]
            try:
                fingerprints[alg_name] = compute_func(samples, sr)
            except Exception as e:
                print(f"Error computing {alg_name} fingerprint: {e}")
                # Fallback to basic pattern
                fingerprints[alg_name] = [0.1] * 50
    
    return fingerprints


def get_fingerprint_for_algorithm(file_data: Dict, algorithm: str) -> Optional[List[float]]:
    """
    Safely retrieve a fingerprint for a specific algorithm from file data.
    """
    if not file_data or not isinstance(file_data, dict):
        return None
    
    fingerprints = file_data.get("fingerprints", {})
    
    # Handle legacy format migration inline
    if not fingerprints and "fingerprint" in file_data:
        fingerprints = {DEFAULT_ALGORITHM: file_data["fingerprint"]}
    
    return fingerprints.get(algorithm)


def migrate_fingerprint_cache(cache: Dict) -> Dict:
    """
    Migrate old single-fingerprint cache format to new multiple-algorithms format.
    """
    if "files" not in cache:
        return cache
    
    migrated = False
    for filename, file_data in cache["files"].items():
        if isinstance(file_data, dict) and "fingerprint" in file_data and "fingerprints" not in file_data:
            # Migrate from old format
            old_fingerprint = file_data["fingerprint"]
            file_data["fingerprints"] = {DEFAULT_ALGORITHM: old_fingerprint}
            del file_data["fingerprint"]
            migrated = True
    
    if migrated:
        print("Migrated fingerprint cache to new multi-algorithm format")
    
    return cache


def load_fingerprint_cache(dirpath: Path) -> Dict:
    """Load fingerprint cache from directory."""
    cache_path = dirpath / FINGERPRINTS_JSON
    try:
        if cache_path.exists():
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            cache = data if isinstance(data, dict) and "files" in data else {"version": 1, "files": {}, "excluded_files": []}
        else:
            cache = {"version": 1, "files": {}, "excluded_files": []}
    except Exception:
        cache = {"version": 1, "files": {}, "excluded_files": []}
    
    # Ensure excluded_files field exists
    if "excluded_files" not in cache:
        cache["excluded_files"] = []
    
    # Migrate old format if needed
    cache = migrate_fingerprint_cache(cache)
    
    return cache


def save_fingerprint_cache(dirpath: Path, cache: Dict) -> None:
    """Save fingerprint cache to directory."""
    cache_path = dirpath / FINGERPRINTS_JSON
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving fingerprint cache: {e}")


def is_file_excluded_from_fingerprinting(dirpath: Path, filename: str) -> bool:
    """Check if a file is excluded from fingerprinting in a directory."""
    cache = load_fingerprint_cache(dirpath)
    excluded_files = cache.get("excluded_files", [])
    return filename in excluded_files


def is_folder_reference(dirpath: Path) -> bool:
    """Check if a folder is marked as a reference folder (higher matching weight)."""
    cache = load_fingerprint_cache(dirpath)
    return cache.get("is_reference_folder", False)


def toggle_folder_reference(dirpath: Path) -> bool:
    """Toggle reference folder status. Returns new reference status."""
    cache = load_fingerprint_cache(dirpath)
    current_status = cache.get("is_reference_folder", False)
    cache["is_reference_folder"] = not current_status
    save_fingerprint_cache(dirpath, cache)
    return cache["is_reference_folder"]


def is_folder_ignored(dirpath: Path) -> bool:
    """Check if a folder is marked to be ignored for fingerprint matching."""
    cache = load_fingerprint_cache(dirpath)
    return cache.get("ignore_fingerprints", False)


def toggle_folder_ignore(dirpath: Path) -> bool:
    """Toggle folder ignore status. Returns new ignore status."""
    cache = load_fingerprint_cache(dirpath)
    current_status = cache.get("ignore_fingerprints", False)
    cache["ignore_fingerprints"] = not current_status
    save_fingerprint_cache(dirpath, cache)
    return cache["ignore_fingerprints"]


def toggle_file_fingerprint_exclusion(dirpath: Path, filename: str) -> bool:
    """Toggle fingerprint exclusion status for a file. Returns new exclusion status."""
    cache = load_fingerprint_cache(dirpath)
    excluded_files = cache.get("excluded_files", [])
    
    if filename in excluded_files:
        # Remove from exclusion list
        excluded_files.remove(filename)
        is_excluded = False
    else:
        # Add to exclusion list
        excluded_files.append(filename)
        is_excluded = True
    
    cache["excluded_files"] = excluded_files
    save_fingerprint_cache(dirpath, cache)
    return is_excluded


def discover_practice_folders_with_fingerprints(root_path: Path) -> List[Path]:
    """
    Discover all subdirectories that contain fingerprint cache files.
    Returns list of directories that have .audio_fingerprints.json files.
    """
    practice_folders = []
    if not root_path.exists() or not root_path.is_dir():
        return practice_folders
    
    # Check root directory itself
    if (root_path / FINGERPRINTS_JSON).exists():
        practice_folders.append(root_path)
    
    # Search all subdirectories
    try:
        for item in root_path.rglob(FINGERPRINTS_JSON):
            if item.is_file():
                folder = item.parent
                if folder not in practice_folders:
                    practice_folders.append(folder)
    except Exception as e:
        print(f"Error discovering practice folders: {e}")
    
    return practice_folders


# ========== FingerprintEngine QObject ==========

class FingerprintWorker(QThread):
    """Worker thread for generating fingerprints."""
    
    progressUpdate = pyqtSignal(int, int, str)  # current, total, filename
    finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, directory: Path, files: List[str], algorithm: str, audio_loader):
        super().__init__()
        self.directory = directory
        self.files = files
        self.algorithm = algorithm
        self.audio_loader = audio_loader
        self._should_stop = False
    
    def stop(self):
        """Request the worker to stop."""
        self._should_stop = True
    
    def run(self):
        """Generate fingerprints for files."""
        try:
            cache = load_fingerprint_cache(self.directory)
            excluded_files = cache.get("excluded_files", [])
            
            total = len(self.files)
            generated_count = 0
            
            for idx, filepath in enumerate(self.files):
                if self._should_stop:
                    self.finished.emit(False, "Operation cancelled")
                    return
                
                filename = Path(filepath).name
                
                # Skip excluded files
                if filename in excluded_files:
                    self.progressUpdate.emit(idx + 1, total, f"Skipped (excluded): {filename}")
                    continue
                
                self.progressUpdate.emit(idx + 1, total, f"Processing: {filename}")
                
                # Check if fingerprint already exists
                file_data = cache["files"].get(filename, {})
                fingerprints = file_data.get("fingerprints", {})
                
                if self.algorithm in fingerprints:
                    continue  # Already have this fingerprint
                
                # Load audio and generate fingerprint
                try:
                    samples, sr = self.audio_loader(filepath)
                    if samples and sr:
                        fingerprint = compute_multiple_fingerprints(samples, sr, [self.algorithm])
                        
                        # Update cache
                        if filename not in cache["files"]:
                            cache["files"][filename] = {"fingerprints": {}}
                        if "fingerprints" not in cache["files"][filename]:
                            cache["files"][filename]["fingerprints"] = {}
                        
                        cache["files"][filename]["fingerprints"][self.algorithm] = fingerprint[self.algorithm]
                        generated_count += 1
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
            
            # Save cache
            save_fingerprint_cache(self.directory, cache)
            
            self.finished.emit(True, f"Generated {generated_count} fingerprints")
            
        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}")


class FingerprintEngine(QObject):
    """
    Audio fingerprinting engine for QML application.
    Manages fingerprint generation, caching, and matching.
    """
    
    # Signals
    fingerprintGenerationStarted = pyqtSignal()
    fingerprintGenerationProgress = pyqtSignal(int, int, str)  # current, total, status
    fingerprintGenerationFinished = pyqtSignal(bool, str)  # success, message
    matchingFinished = pyqtSignal(str)  # results as JSON string
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_directory = None
        self._current_algorithm = DEFAULT_ALGORITHM
        self._threshold = 0.7
        self._worker = None
        self._audio_loader = None  # Will be set by caller
    
    def setAudioLoader(self, loader):
        """Set the audio loading function."""
        self._audio_loader = loader
    
    @pyqtSlot(str)
    def setCurrentDirectory(self, directory: str):
        """Set the current directory for fingerprinting operations."""
        self._current_directory = Path(directory) if directory else None
    
    @pyqtSlot(str)
    def setAlgorithm(self, algorithm: str):
        """Set the current fingerprinting algorithm."""
        if algorithm in FINGERPRINT_ALGORITHMS:
            self._current_algorithm = algorithm
    
    @pyqtSlot(float)
    def setThreshold(self, threshold: float):
        """Set the matching threshold (0.0 to 1.0)."""
        self._threshold = max(0.0, min(1.0, threshold))
    
    @pyqtSlot(result=str)
    def getAlgorithm(self) -> str:
        """Get the current algorithm."""
        return self._current_algorithm
    
    @pyqtSlot(result=float)
    def getThreshold(self) -> float:
        """Get the current threshold."""
        return self._threshold
    
    @pyqtSlot(result=str)
    def getAlgorithmsList(self) -> str:
        """Get list of available algorithms as JSON."""
        algorithms = []
        for key, info in FINGERPRINT_ALGORITHMS.items():
            algorithms.append({
                "id": key,
                "name": info["name"],
                "description": info["description"]
            })
        return json.dumps(algorithms)
    
    @pyqtSlot(list)
    def generateFingerprints(self, files: list):
        """Generate fingerprints for given files in background."""
        if not self._current_directory or not self._audio_loader:
            self.fingerprintGenerationFinished.emit(False, "No directory or audio loader set")
            return
        
        if self._worker and self._worker.isRunning():
            self.fingerprintGenerationFinished.emit(False, "Generation already in progress")
            return
        
        # Create and start worker thread
        self._worker = FingerprintWorker(
            self._current_directory,
            files,
            self._current_algorithm,
            self._audio_loader
        )
        
        self._worker.progressUpdate.connect(self.fingerprintGenerationProgress)
        self._worker.finished.connect(self._on_generation_finished)
        
        self.fingerprintGenerationStarted.emit()
        self._worker.start()
    
    def _on_generation_finished(self, success: bool, message: str):
        """Handle generation completion."""
        self.fingerprintGenerationFinished.emit(success, message)
        if self._worker:
            self._worker.deleteLater()
            self._worker = None
    
    @pyqtSlot()
    def cancelGeneration(self):
        """Cancel ongoing fingerprint generation."""
        if self._worker and self._worker.isRunning():
            self._worker.stop()
            self._worker.wait()
    
    @pyqtSlot(str, result=str)
    def getFingerprintInfo(self, directory: str) -> str:
        """Get fingerprint information for a directory."""
        dir_path = Path(directory) if directory else None
        if not dir_path or not dir_path.exists():
            return json.dumps({"error": "Invalid directory"})
        
        cache = load_fingerprint_cache(dir_path)
        files_data = cache.get("files", {})
        
        info = {
            "total_files": len(files_data),
            "algorithm_coverage": {},
            "excluded_files": cache.get("excluded_files", [])
        }
        
        # Count coverage for each algorithm
        for alg in FINGERPRINT_ALGORITHMS.keys():
            count = 0
            for file_data in files_data.values():
                if get_fingerprint_for_algorithm(file_data, alg):
                    count += 1
            info["algorithm_coverage"][alg] = count
        
        return json.dumps(info)
    
    @pyqtSlot(str, result=str)
    def discoverPracticeFolders(self, root_path: str) -> str:
        """Discover all practice folders with fingerprints."""
        folders = discover_practice_folders_with_fingerprints(Path(root_path))
        folder_list = [str(f) for f in folders]
        return json.dumps(folder_list)
    
    @pyqtSlot(str, str, result=bool)
    def toggleFileExclusion(self, directory: str, filename: str) -> bool:
        """Toggle file exclusion status."""
        return toggle_file_fingerprint_exclusion(Path(directory), filename)
    
    @pyqtSlot(str, str, result=bool)
    def isFileExcluded(self, directory: str, filename: str) -> bool:
        """Check if file is excluded."""
        return is_file_excluded_from_fingerprinting(Path(directory), filename)
    
    @pyqtSlot(str, result=bool)
    def isFolderReference(self, directory: str) -> bool:
        """Check if folder is marked as reference folder."""
        return is_folder_reference(Path(directory))
    
    @pyqtSlot(str, result=bool)
    def toggleFolderReference(self, directory: str) -> bool:
        """Toggle folder reference status."""
        return toggle_folder_reference(Path(directory))
    
    @pyqtSlot(str, result=bool)
    def isFolderIgnored(self, directory: str) -> bool:
        """Check if folder is ignored for fingerprint matching."""
        return is_folder_ignored(Path(directory))
    
    @pyqtSlot(str, result=bool)
    def toggleFolderIgnore(self, directory: str) -> bool:
        """Toggle folder ignore status."""
        return toggle_folder_ignore(Path(directory))
