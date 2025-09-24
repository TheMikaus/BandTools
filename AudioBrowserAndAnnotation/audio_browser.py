#!/usr/bin/env python3
# audio_browser.py — Audio folder browser + player + multi-annotation sets
# - PyQt6 auto-install (when not frozen)
# - File tree with Name, Size/Time, Date Modified (only folders/mp3/wav)
# - Play on single-click; double-click opens folder or focuses Annotations
# - Click-to-seek slider; volume control
# - Waveform generation (threaded, cached per file, progressive draw)
# - Notes per song (timestamped), folder-level notes, and multi annotation sets
# - Markers on waveform for all visible sets; drag to adjust
# - Export annotations (CRLF), batch rename (##_<ProvidedName>), WAV→MP3 with progress
# - Merged view toggle that shows annotations from all visible sets in a single table
#   and allows editing across sets (time/text/important/delete).
from __future__ import annotations

import sys, subprocess, importlib, os, json, re, uuid, hashlib, wave, audioop, time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from array import array

# ========== Bootstrap: auto-install PyQt6 (if not frozen) ==========
def _ensure_import(mod_name: str, pip_name: str | None = None) -> bool:
    try:
        importlib.import_module(mod_name); return True
    except ImportError:
        if getattr(sys, "frozen", False): return False
        pkg = pip_name or mod_name
        for args in ([sys.executable, "-m", "pip", "install", pkg],
                     [sys.executable, "-m", "pip", "install", "--user", pkg]):
            try:
                subprocess.check_call(args); break
            except subprocess.CalledProcessError:
                continue
        else:
            return False
        importlib.invalidate_caches()
        try:
            importlib.import_module(mod_name); return True
        except ImportError:
            return False

try:
    import PyQt6
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False

if not PYQT6_AVAILABLE:
    if not _ensure_import("PyQt6", "PyQt6"):
        raise RuntimeError("PyQt6 is required.")

HAVE_NUMPY = _ensure_import("numpy", "numpy")
HAVE_PYDUB = _ensure_import("pydub", "pydub")
if HAVE_PYDUB:
    try:
        from pydub import AudioSegment
        from pydub.utils import which as pydub_which
    except Exception:
        HAVE_PYDUB = False

# ========== Qt imports ==========
from PyQt6.QtCore import (
    QItemSelection, QModelIndex, QSettings, QTimer, Qt, QUrl, QPoint, QSize,
    pyqtSignal, QRect, QObject, QThread, QDir, QIdentityProxyModel
)
from PyQt6.QtGui import (
    QAction, QKeySequence, QIcon, QPixmap, QPainter, QColor, QPen, QCursor
)
# QFileSystemModel may import from QtWidgets or QtGui depending on build
try:
    from PyQt6.QtWidgets import QFileSystemModel
except Exception:
    from PyQt6.QtGui import QFileSystemModel  # type: ignore
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer, QMediaDevices
from PyQt6.QtWidgets import (
    QApplication, QHBoxLayout, QHeaderView, QMainWindow, QMessageBox,
    QPushButton, QSlider, QSplitter, QTableWidget, QTableWidgetItem,
    QTreeView, QVBoxLayout, QWidget, QFileDialog, QAbstractItemView, QStatusBar,
    QToolBar, QStyle, QLabel, QTabWidget, QLineEdit, QPlainTextEdit, QCheckBox, QWidgetAction, QSpinBox,
    QProgressDialog, QColorDialog, QInputDialog, QComboBox, QMenu
)
from PyQt6.QtWidgets import QStyleFactory

# ========== Constants ==========
APP_ORG = "YourCompany"
APP_NAME = "Audio Folder Player"
SETTINGS_KEY_ROOT = "root_dir"
SETTINGS_KEY_TABS_ORDER = "tabs_order"
SETTINGS_KEY_AUTOPROGRESS = "auto_progress"
SETTINGS_KEY_AUTOSWITCH = "auto_switch_ann"
SETTINGS_KEY_VOLUME = "volume_0_100"
SETTINGS_KEY_UNDO_CAP = "undo_capacity"
SETTINGS_KEY_CUR_SET = "current_set_id"
SETTINGS_KEY_SHOW_ALL = "show_all_sets"
SETTINGS_KEY_SHOW_ALL_FOLDER_NOTES = "show_all_folder_notes"
SETTINGS_KEY_FINGERPRINT_DIR = "fingerprint_reference_dir"
SETTINGS_KEY_FINGERPRINT_THRESHOLD = "fingerprint_match_threshold"
NAMES_JSON = ".provided_names.json"
NOTES_JSON = ".audio_notes.json"
WAVEFORM_JSON = ".waveform_cache.json"
DURATIONS_JSON = ".duration_cache.json"
FINGERPRINTS_JSON = ".audio_fingerprints.json"
RESERVED_JSON = {NAMES_JSON, NOTES_JSON, WAVEFORM_JSON, DURATIONS_JSON, FINGERPRINTS_JSON}
AUDIO_EXTS = {".wav", ".wave", ".mp3"}
WAVEFORM_COLUMNS = 2000
APP_ICON_NAME = "app_icon.png"

# Visual widths
MARKER_WIDTH = 2                # thin marker width
MARKER_SELECTED_WIDTH = 6       # selected marker width
PLAYHEAD_WIDTH = 4              # playhead width
WAVEFORM_STROKE_WIDTH = 1
MARKER_HIT_TOLERANCE_PX = 8

# Conversion
DEFAULT_MP3_BITRATE = "192k"

# ========== Helpers ==========
def human_time_ms(ms: int) -> str:
    if ms < 0: return "0:00"
    s = int(ms) // 1000
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"

def parse_time_to_ms(text: str) -> Optional[int]:
    s = text.strip()
    if not s: return None
    parts = s.split(":")
    if not all(p.isdigit() for p in parts): return None
    if len(parts) == 1: return max(0, int(parts[0]) * 1000)
    if len(parts) == 2:
        mm, ss = map(int, parts); return max(0, (mm*60 + ss) * 1000)
    if len(parts) == 3:
        hh, mm, ss = map(int, parts); return max(0, (hh*3600 + mm*60 + ss) * 1000)
    return None

def sanitize(name: str) -> str:
    name = re.sub(r'[\\/:*?"<>|]+', "_", name.strip())
    return re.sub(r"\s+", " ", name).strip()

def resource_path(name: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / name

def file_signature(p: Path) -> Tuple[int, int]:
    try:
        st = p.stat(); return int(st.st_size), int(st.st_mtime)
    except Exception:
        return (0, 0)

def load_json(path: Path, default):
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default

def save_json(path: Path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def load_waveform_cache(dirpath: Path) -> Dict:
    data = load_json(dirpath / WAVEFORM_JSON, None)
    return data if isinstance(data, dict) and "files" in data else {"version": 1, "files": {}}

def save_waveform_cache(dirpath: Path, cache: Dict) -> None:
    save_json(dirpath / WAVEFORM_JSON, cache)

def bytes_to_human(n: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    i = 0; f = float(n)
    while f >= 1024 and i < len(units) - 1:
        f /= 1024.0; i += 1
    return f"{int(f)} {units[i]}" if units[i] == "B" else f"{f:.1f} {units[i]}"

def _open_path_default(path: Path):
    try:
        if sys.platform.startswith("win"):
            os.startfile(str(path))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.call(["open", str(path)])
        else:
            subprocess.call(["xdg-open", str(path)])
    except Exception as e:
        QMessageBox.warning(None, "Open Failed", f"Couldn't open:\n{e}")

def color_to_hex(c: QColor) -> str:
    return c.name(QColor.NameFormat.HexRgb)

def hex_to_color(s: str) -> QColor:
    try:
        return QColor(s) if s else QColor("#00cc66")
    except Exception:
        return QColor("#00cc66")

# ========== SeekSlider (click-to-seek) ==========
from PyQt6.QtWidgets import QSlider
class SeekSlider(QSlider):
    clickedValue = pyqtSignal(int)
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.maximum() > self.minimum():
                x = event.position().x()
                rng = self.maximum() - self.minimum()
                value = self.minimum() + int(round(rng * x / max(1, self.width())))
                self.setSliderPosition(value)
                self.clickedValue.emit(value)
            event.accept()
        else:
            super().mousePressEvent(event)

# ========== Audio decode & peak computation ==========
if HAVE_NUMPY:
    import numpy as np

def decode_audio_samples(path: Path) -> Tuple[List[float], int, int]:
    suf = path.suffix.lower()
    if suf in (".wav", ".wave"):
        with wave.open(str(path), "rb") as wf:
            nch = wf.getnchannels()
            sw = wf.getsampwidth()
            sr = wf.getframerate()
            nframes = wf.getnframes()
            raw = wf.readframes(nframes)
        if sw != 2:
            try:
                raw = audioop.lin2lin(raw, sw, 2); sw = 2
            except Exception:
                pass
        data = array("h"); data.frombytes(raw[: (len(raw)//2)*2 ])
        if nch > 1:
            total = len(data) // nch
            mono = array("h", [0]) * total
            for i in range(total):
                s = 0; base = i * nch
                for c in range(nch): s += data[base + c]
                mono[i] = int(s / nch)
            data = mono
        if HAVE_NUMPY:
            arr = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
            samples = arr.tolist()
        else:
            samples = [s / 32768.0 for s in data]
        dur_ms = int((len(samples) / sr) * 1000)
        return samples, sr, dur_ms
    if HAVE_PYDUB:
        seg = AudioSegment.from_file(str(path))
        sr = seg.frame_rate
        dur_ms = len(seg)
        ch = seg.channels
        raw = seg.get_array_of_samples()
        if HAVE_NUMPY:
            arr = np.array(raw, dtype=np.int16).astype(np.float32)
            if ch > 1: arr = arr.reshape((-1, ch)).mean(axis=1)
            samples = (arr / 32768.0).tolist()
        else:
            ints = list(raw)
            if ch > 1:
                mono = []
                for i in range(0, len(ints), ch):
                    s = 0
                    for c in range(ch): s += ints[i + c]
                    mono.append(s / ch)
                samples = [v / 32768.0 for v in mono]
            else:
                samples = [v / 32768.0 for v in ints]
        return samples, sr, dur_ms
    raise RuntimeError("No MP3 decoder found (install FFmpeg for pydub).")

def compute_peaks_progressive(samples: List[float], columns: int, chunk: int):
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
                    v = float(arr[min(a, n-1)]); out.append([v, v])
            yield start, out
    else:
        for start in range(0, columns, chunk):
            end = min(columns, start + chunk)
            out = []
            for i in range(start, end):
                a = int(i * n / columns)
                b = int((i+1) * n / columns)
                if b <= a: b = a + 1
                mn, mx = 1.0, -1.0
                for j in range(a, min(b, n)):
                    v = samples[j]
                    if v < mn: mn = v
                    if v > mx: mx = v
                out.append([float(mn), float(mx)])
            yield start, out

def resample_peaks(peaks: List[Tuple[float, float]], width: int) -> List[Tuple[float, float]]:
    n = len(peaks)
    if n == 0 or width <= 0: return [(0.0, 0.0)] * max(1, width)
    if width == n: return peaks
    out = []
    for i in range(width):
        a = int(i * n / width); b = int((i+1) * n / width)
        if b <= a: b = a + 1
        mn, mx = 1.0, -1.0
        for j in range(a, min(b, n)):
            pmn, pmx = peaks[j]
            if pmn < mn: mn = pmn
            if pmx > mx: mx = pmx
        out.append((mn, mx))
    return out

# ========== Audio fingerprinting ==========
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
    """
    if not fp1 or not fp2:
        return 0.0
    
    # Align lengths by truncating to shorter
    min_len = min(len(fp1), len(fp2))
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

def load_fingerprint_cache(dirpath: Path) -> Dict:
    """Load fingerprint cache from directory."""
    data = load_json(dirpath / FINGERPRINTS_JSON, None)
    return data if isinstance(data, dict) and "files" in data else {"version": 1, "files": {}}

def save_fingerprint_cache(dirpath: Path, cache: Dict) -> None:
    """Save fingerprint cache to directory."""
    save_json(dirpath / FINGERPRINTS_JSON, cache)

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
    
    # Check immediate subdirectories
    try:
        for item in root_path.iterdir():
            if item.is_dir() and (item / FINGERPRINTS_JSON).exists():
                practice_folders.append(item)
    except (OSError, PermissionError):
        pass  # Skip directories we can't read
    
    return practice_folders

def collect_fingerprints_from_folders(folder_paths: List[Path], exclude_dir: Optional[Path] = None) -> Dict[str, Dict]:
    """
    Collect fingerprints from multiple folders and organize by filename.
    
    Args:
        folder_paths: List of directories to scan for fingerprints
        exclude_dir: Optional directory to exclude from collection
    
    Returns:
        Dictionary mapping filename -> list of {fingerprint, folder_path, file_data, provided_name}
        Format: {
            "song1.mp3": [
                {"fingerprint": [...], "folder": Path("/path/to/folder1"), "data": {...}, "provided_name": "Song Name"},
                {"fingerprint": [...], "folder": Path("/path/to/folder2"), "data": {...}, "provided_name": "Song Name"}
            ]
        }
    """
    fingerprint_map = {}
    
    for folder_path in folder_paths:
        if exclude_dir and folder_path.resolve() == exclude_dir.resolve():
            continue
            
        cache = load_fingerprint_cache(folder_path)
        files_data = cache.get("files", {})
        
        # Load provided names from this folder
        names_json_path = folder_path / NAMES_JSON
        provided_names = load_json(names_json_path, {}) or {}
        
        for filename, file_data in files_data.items():
            fingerprint = file_data.get("fingerprint")
            if fingerprint:  # Only include files with valid fingerprints
                if filename not in fingerprint_map:
                    fingerprint_map[filename] = []
                
                # Get the provided name for this file, fallback to filename stem
                provided_name = provided_names.get(filename, "").strip()
                if not provided_name:
                    provided_name = Path(filename).stem
                
                fingerprint_map[filename].append({
                    "fingerprint": fingerprint,
                    "folder": folder_path,
                    "data": file_data,
                    "provided_name": provided_name
                })
    
    return fingerprint_map

def find_best_cross_folder_match(target_fingerprint: List[float], fingerprint_map: Dict[str, List[Dict]], threshold: float) -> Optional[Tuple[str, float, Path, str]]:
    """
    Find the best match for a target fingerprint across multiple folders.
    Prioritizes matches that appear in only one folder (unique identification).
    
    Args:
        target_fingerprint: The fingerprint to match against
        fingerprint_map: Dictionary from collect_fingerprints_from_folders
        threshold: Minimum similarity threshold (0.0 to 1.0)
    
    Returns:
        Tuple of (filename, similarity_score, source_folder, provided_name) or None if no match above threshold
    """
    best_matches = []  # List of (filename, score, folder, folder_count, provided_name)
    
    for filename, fingerprint_entries in fingerprint_map.items():
        folder_count = len(fingerprint_entries)
        
        # Find best score for this filename across all its instances
        best_score_for_file = 0.0
        best_folder_for_file = None
        best_provided_name = None
        
        for entry in fingerprint_entries:
            score = compare_fingerprints(target_fingerprint, entry["fingerprint"])
            if score > best_score_for_file:
                best_score_for_file = score
                best_folder_for_file = entry["folder"]
                best_provided_name = entry["provided_name"]
        
        if best_score_for_file >= threshold:
            best_matches.append((filename, best_score_for_file, best_folder_for_file, folder_count, best_provided_name))
    
    if not best_matches:
        return None
    
    # Sort by priority: 
    # 1. Files appearing in only one folder (folder_count=1) get priority
    # 2. Then by similarity score (descending)
    # 3. Then by filename for consistency
    best_matches.sort(key=lambda x: (-1 if x[3] == 1 else 0, x[1], x[0]), reverse=True)
    
    best_match = best_matches[0]
    return (best_match[0], best_match[1], best_match[2], best_match[4])

# ========== Waveform worker ==========
class WaveformWorker(QObject):
    progress = pyqtSignal(int, str, list, int, int)
    finished = pyqtSignal(int, str, list, int, int, int, int)
    error = pyqtSignal(int, str, str)

    def __init__(self, gen_id: int, path_str: str, columns: int):
        super().__init__()
        self._gen_id = int(gen_id)
        self._path_str = path_str
        self._columns = int(columns)

    def run(self):
        try:
            p = Path(self._path_str)
            samples, _sr, dur_ms = decode_audio_samples(p)
            peaks_all: List[Tuple[float, float]] = []
            CHUNK = 100
            for start, chunk_peaks in compute_peaks_progressive(samples, self._columns, CHUNK):
                for a, b in chunk_peaks:
                    peaks_all.append((float(a), float(b)))
                done = start + len(chunk_peaks)
                self.progress.emit(self._gen_id, self._path_str, chunk_peaks, int(done), int(self._columns))
            size, mtime = file_signature(p)
            peaks_payload = [[float(a), float(b)] for (a, b) in peaks_all]
            self.finished.emit(self._gen_id, self._path_str, peaks_payload, int(dur_ms), int(self._columns), int(size), int(mtime))
        except Exception as e:
            self.error.emit(self._gen_id, self._path_str, str(e))

# ========== Convert worker (WAV→MP3) ==========
class ConvertWorker(QObject):
    progress = pyqtSignal(int, int, str)  # done, total, filename
    file_done = pyqtSignal(str, str, bool, str)  # src_name, dst_name, deleted_ok, error_msg
    finished = pyqtSignal(bool)  # canceled?

    def __init__(self, wav_paths: List[str], bitrate: str):
        super().__init__()
        self._paths = [str(p) for p in wav_paths]
        self._bitrate = str(bitrate)
        self._cancel = False

    def cancel(self): self._cancel = True

    def run(self):
        total = len(self._paths); done = 0
        for srcs in self._paths:
            if self._cancel: self.finished.emit(True); return
            src = Path(srcs)
            self.progress.emit(done, total, src.name)
            try:
                base = src.stem; target = src.with_suffix(".mp3"); n = 1
                while target.exists():
                    target = src.with_name(f"{base} ({n}).mp3"); n += 1
                audio = AudioSegment.from_file(str(src))
                audio.export(str(target), format="mp3", bitrate=self._bitrate)
                deleted_ok = True
                try:
                    src.unlink()
                except Exception as de:
                    deleted_ok = False
                    self.file_done.emit(src.name, target.name, False, f"Converted but couldn't delete: {de}")
                else:
                    self.file_done.emit(src.name, target.name, True, "")
            except Exception as e:
                self.file_done.emit(src.name, "", False, str(e))
            done += 1
            self.progress.emit(done, total, src.name)
        self.finished.emit(False)

# ========== Waveform view ==========
class WaveformView(QWidget):
    markerMoved = pyqtSignal(str, int, int)     # set_id, uid, ms
    markerReleased = pyqtSignal(str, int, int)  # set_id, uid, ms
    annotationClicked = pyqtSignal(str, int)    # set_id, uid
    seekRequested = pyqtSignal(int)             # ms

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(140)
        # Enable focus so the widget can receive keyboard events
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._peaks: Optional[List[Tuple[float, float]]] = None
        self._peaks_loading: List[Tuple[float, float]] = []
        self._duration_ms: int = 0
        self._pixmap: Optional[QPixmap] = None
        self._pixmap_w: int = 0

        self._bg = QColor("#101114"); self._axis = QColor("#2a2c31")
        self._wave = QColor("#58a6ff"); self._playhead = QColor("#ff5555")
        self._msg_color = QColor("#8a8f98")
        self._selected_color = QColor("#ffa500")

        self._state: str = "empty"   # empty|loading|ready|error
        self._msg: str = ""
        self._path: Optional[Path] = None
        self._total_cols: int = 0
        self._done_cols: int = 0

        # Multi annotations: { set_id: {"color": QColor, "visible": bool, "pairs":[(uid,ms)]} }
        self._multi: Dict[str, Dict[str, Any]] = {}
        self._selected: Optional[Tuple[str,int]] = None   # (set_id, uid)
        self._hover: Optional[Tuple[str,int]] = None

        self._dragging_marker: bool = False
        self._drag_tolerance_px: int = MARKER_HIT_TOLERANCE_PX

        self._player: Optional[QMediaPlayer] = None

        self._gen_id_counter = 0
        self._active_gen_id = -1
        self._threads: List[QThread] = []
        self._workers: Dict[int, WaveformWorker] = {}
        
        # Clip selection region
        self._clip_start_ms: Optional[int] = None
        self._clip_end_ms: Optional[int] = None

    def bind_player(self, player: QMediaPlayer):
        self._player = player
        player.positionChanged.connect(lambda _: self.update())

    def set_annotations_multi(self, payload: Dict[str, Dict[str, Any]]):
        self._multi = {}
        for sid, v in payload.items():
            color = v.get("color")
            qc = color if isinstance(color, QColor) else QColor(str(color))
            self._multi[str(sid)] = {
                "color": qc if qc.isValid() else QColor("#00cc66"),
                "visible": bool(v.get("visible", True)),
                "pairs": [(int(uid), int(ms)) for (uid, ms) in (v.get("pairs") or [])],
            }
        self.update()

    def set_selected_uid(self, set_id: Optional[str], uid: Optional[int]):
        if set_id is None or uid is None: self._selected = None
        else: self._selected = (str(set_id), int(uid))
        self.update()

    def set_clip_selection(self, start_ms: Optional[int], end_ms: Optional[int]):
        """Set the clip selection region to be highlighted on the waveform."""
        self._clip_start_ms = start_ms
        self._clip_end_ms = end_ms
        self.update()

    def clear(self):
        self._peaks = None; self._peaks_loading = []; self._duration_ms = 0
        self._pixmap = None; self._state = "empty"; self._msg = ""
        self._path = None; self._total_cols = 0; self._done_cols = 0
        self._multi = {}; self._selected = None; self._hover = None
        self._dragging_marker = False
        self._clip_start_ms = None; self._clip_end_ms = None
        self.update()

    def _effective_duration(self) -> int:
        if self._duration_ms > 0: return self._duration_ms
        if self._player is not None and self._player.duration() > 0:
            return int(self._player.duration())
        return 0

    def _ms_to_x(self, ms: int) -> int:
        dur = self._effective_duration()
        if dur <= 0: return 0
        return int((ms / dur) * max(1, self.width()))

    def _x_to_ms(self, x: int) -> int:
        W = max(1, self.width())
        x = max(0, min(W, x))
        dur = self._effective_duration()
        if dur <= 0: return 0
        return int((x / W) * dur)

    def set_audio_file(self, path: Optional[Path]):
        if path is None:
            self.clear(); return
        self._path = path
        self._pixmap = None; self._pixmap_w = 0
        self._peaks = None; self._peaks_loading = []
        self._total_cols = WAVEFORM_COLUMNS; self._done_cols = 0

        cache = load_waveform_cache(path.parent)
        entry = cache["files"].get(path.name)
        size, mtime = file_signature(path)
        if entry and entry.get("columns") == WAVEFORM_COLUMNS and \
           int(entry.get("size", 0)) == size and int(entry.get("mtime", 0)) == mtime and \
           isinstance(entry.get("peaks"), list) and isinstance(entry.get("duration_ms"), int):
            self._peaks = [(float(mn), float(mx)) for mn, mx in entry["peaks"]]
            self._duration_ms = int(entry["duration_ms"])
            self._state = "ready"; self._msg = ""
            self.update(); return

        self._duration_ms = 0
        self._state = "loading"; self._msg = "Analyzing waveform…"
        self.update()

        self._active_gen_id = self._gen_id_counter = (self._gen_id_counter + 1) % (1 << 31)
        self._start_worker(self._active_gen_id, path)

    def _start_worker(self, gen_id: int, path: Path):
        thread = QThread(self)
        worker = WaveformWorker(gen_id, str(path), WAVEFORM_COLUMNS)
        worker.moveToThread(thread); worker.setObjectName(f"WaveformWorker-{gen_id}")
        self._threads.append(thread); self._workers[gen_id] = worker

        thread.started.connect(worker.run)
        worker.progress.connect(self._on_worker_progress)
        worker.finished.connect(self._on_worker_finished)
        worker.error.connect(self._on_worker_error)

        def _cleanup():
            worker.deleteLater()
            if thread in self._threads: self._threads.remove(thread)
            self._workers.pop(gen_id, None)
        worker.finished.connect(_cleanup)
        thread.finished.connect(_cleanup); thread.finished.connect(thread.deleteLater)
        thread.start()

    def _on_worker_progress(self, gen_id: int, path_str: str, new_chunk: list, done_cols: int, total_cols: int):
        if gen_id != self._active_gen_id or not self._path or str(self._path) != path_str:
            return
        for pair in new_chunk:
            try: a, b = pair
            except Exception: continue
            self._peaks_loading.append((float(a), float(b)))
        self._total_cols = max(1, int(total_cols))
        self._done_cols = max(0, min(int(done_cols), self._total_cols))
        if self._done_cols > 0:
            pct = int(round(100.0 * self._done_cols / self._total_cols))
            self._msg = f"Analyzing waveform… {min(pct, 99)}%"
        else:
            self._msg = "Analyzing waveform…"
        self._pixmap = None; self.update()

    def _on_worker_finished(self, gen_id: int, path_str: str, peaks: list, duration_ms: int, columns: int, size: int, mtime: int):
        if gen_id != self._active_gen_id or not self._path or str(self._path) != path_str:
            return
        self._peaks = [(float(mn), float(mx)) for mn, mx in peaks]
        self._duration_ms = int(duration_ms)
        self._state = "ready"; self._msg = ""
        cache = load_waveform_cache(self._path.parent)
        cache["files"][self._path.name] = {
            "columns": int(columns),
            "size": int(size),
            "mtime": int(mtime),
            "duration_ms": int(duration_ms),
            "peaks": self._peaks,
        }
        save_waveform_cache(self._path.parent, cache)
        self._pixmap = None; self.update()

    def _on_worker_error(self, gen_id: int, path_str: str, message: str):
        if gen_id != self._active_gen_id or not self._path or str(self._path) != path_str:
            return
        self._peaks = None; self._duration_ms = 0
        self._state = "error"
        self._msg = "No waveform (MP3 needs FFmpeg installed)" if "No MP3 decoder" in message else "Waveform unavailable"
        self._pixmap = None; self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.width() != self._pixmap_w: self._pixmap = None

    def _ensure_pixmap(self):
        if self._pixmap is not None and self._pixmap_w == self.width(): return
        W = max(1, self.width()); H = max(1, self.height())
        pm = QPixmap(W, H); pm.fill(self._bg)
        p = QPainter(pm); p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        mid = H // 2
        pen_axis = QPen(self._axis); pen_axis.setWidth(1)
        p.setPen(pen_axis); p.drawLine(0, mid, W, mid)

        if self._state == "ready" and self._peaks:
            pen_wave = QPen(self._wave); pen_wave.setWidth(WAVEFORM_STROKE_WIDTH); p.setPen(pen_wave)
            draw_peaks = resample_peaks(self._peaks, W)
            for x, (mn, mx) in enumerate(draw_peaks):
                y1 = int(mid - mn * (H/2-2)); y2 = int(mid - mx * (H/2-2))
                if y1 > y2: y1, y2 = y2, y1
                p.drawLine(x, y1, x, y2)
        elif self._state == "loading":
            if self._peaks_loading:
                pen_wave = QPen(self._wave); pen_wave.setWidth(WAVEFORM_STROKE_WIDTH); p.setPen(pen_wave)
                partial = resample_peaks(self._peaks_loading, min(W, max(1, self._done_cols)))
                draw_peaks = resample_peaks(partial, W)
                for x, (mn, mx) in enumerate(draw_peaks):
                    y1 = int(mid - mn * (H/2-2)); y2 = int(mid - mx * (H/2-2))
                    if y1 > y2: y1, y2 = y2, y1
                    p.drawLine(x, y1, x, y2)
            p.setPen(self._msg_color)
            p.drawText(QRect(0, 0, W, H), Qt.AlignmentFlag.AlignCenter, self._msg or "Analyzing waveform…")
        else:
            p.setPen(self._msg_color)
            p.drawText(QRect(0, 0, W, H), Qt.AlignmentFlag.AlignCenter, self._msg or "No waveform")

        p.end()
        self._pixmap = pm; self._pixmap_w = W

    def paintEvent(self, event):
        self._ensure_pixmap()
        painter = QPainter(self)
        if self._pixmap: painter.drawPixmap(0, 0, self._pixmap)

        # All markers for visible sets
        for sid, info in self._multi.items():
            if not info.get("visible", True): continue
            color: QColor = info.get("color", QColor("#00cc66"))
            pairs = info.get("pairs", [])
            for uid, ms in pairs:
                x = self._ms_to_x(int(ms))
                if x < 0 or x > self.width(): continue
                sel = (self._selected is not None and self._selected == (sid, uid))
                pen = QPen(self._selected_color if sel else color)
                pen.setWidth(MARKER_SELECTED_WIDTH if sel else MARKER_WIDTH)
                painter.setPen(pen); painter.drawLine(x, 0, x, self.height())

        # Clip selection region highlight
        if self._clip_start_ms is not None and self._clip_end_ms is not None:
            start_x = self._ms_to_x(self._clip_start_ms)
            end_x = self._ms_to_x(self._clip_end_ms)
            if start_x < self.width() and end_x > 0:  # Only draw if visible
                # Ensure proper order
                left_x = min(start_x, end_x)
                right_x = max(start_x, end_x)
                # Clamp to widget bounds
                left_x = max(0, left_x)
                right_x = min(self.width(), right_x)
                
                if right_x > left_x:  # Only draw if there's a visible region
                    # Draw semi-transparent highlight
                    highlight_color = QColor("#ffff00")  # Yellow
                    highlight_color.setAlpha(60)  # Semi-transparent
                    painter.fillRect(int(left_x), 0, int(right_x - left_x), self.height(), highlight_color)
                    
                    # Draw border lines for the selection
                    border_pen = QPen(QColor("#ffff00"))
                    border_pen.setWidth(2)
                    painter.setPen(border_pen)
                    painter.drawLine(int(left_x), 0, int(left_x), self.height())
                    painter.drawLine(int(right_x), 0, int(right_x), self.height())
        elif self._clip_start_ms is not None or self._clip_end_ms is not None:
            # Draw single yellow line when only start or end is specified
            border_pen = QPen(QColor("#ffff00"))
            border_pen.setWidth(2)
            painter.setPen(border_pen)
            
            if self._clip_start_ms is not None:
                start_x = self._ms_to_x(self._clip_start_ms)
                if 0 <= start_x <= self.width():  # Only draw if visible
                    painter.drawLine(int(start_x), 0, int(start_x), self.height())
            
            if self._clip_end_ms is not None:
                end_x = self._ms_to_x(self._clip_end_ms)
                if 0 <= end_x <= self.width():  # Only draw if visible
                    painter.drawLine(int(end_x), 0, int(end_x), self.height())

        # Playhead
        dur = self._effective_duration()
        if self._player and dur > 0:
            pos = self._player.position()
            x = int((pos / dur) * max(1, self.width()))
            pen = QPen(self._selected_color.darker(135)); pen.setWidth(PLAYHEAD_WIDTH)
            painter.setPen(pen); painter.drawLine(x, 0, x, self.height())

        painter.end()

    def _nearest_marker(self, x: int) -> Optional[Tuple[str,int,int]]:
        best = None; bestd = 10**9
        for sid, info in self._multi.items():
            if not info.get("visible", True): continue
            for uid, ms in info.get("pairs", []):
                mx = self._ms_to_x(int(ms))
                d = abs(x - mx)
                if d <= self._drag_tolerance_px and d < bestd:
                    bestd = d; best = (sid, int(uid), int(ms))
        return best

    def mouseMoveEvent(self, event):
        x = int(event.position().x())
        if self._dragging_marker and self._selected is not None:
            sid, uid = self._selected
            new_ms = self._x_to_ms(x)
            info = self._multi.get(sid)
            if info:
                pairs = info.get("pairs", [])
                for i, (u, _ms) in enumerate(pairs):
                    if int(u) == int(uid):
                        pairs[i] = (u, int(new_ms)); break
            self.markerMoved.emit(sid, uid, int(new_ms))
            self.update(); event.accept(); return
        hit = self._nearest_marker(x)
        if hit is None:
            self._hover = None
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        else:
            sid, uid, _ = hit
            self._hover = (sid, uid)
            self.setCursor(QCursor(Qt.CursorShape.SizeHorCursor if self._selected == (sid, uid) else Qt.CursorShape.PointingHandCursor))
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Set focus to this widget so it can receive keyboard events
            self.setFocus()
            x = int(event.position().x())
            hit = self._nearest_marker(x)
            if hit is not None:
                sid, uid, _ = hit
                self._selected = (sid, uid)
                self.annotationClicked.emit(sid, uid)
                self._dragging_marker = True
                event.accept(); return
            ms = self._x_to_ms(x)
            self.seekRequested.emit(ms)
            if self._player: self._player.setPosition(ms)
            self.update(); event.accept(); return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self._dragging_marker and self._selected is not None:
            sid, uid = self._selected
            info = self._multi.get(sid); ms = 0
            if info:
                for u, m in info.get("pairs", []):
                    if int(u) == int(uid): ms = int(m); break
            self._dragging_marker = False
            self.markerReleased.emit(sid, uid, int(ms))
            event.accept(); return
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        """Handle key press events for the waveform widget."""
        if event.key() == Qt.Key.Key_Space:
            # Find the parent AudioBrowser window and call its toggle play/pause method
            parent_widget = self.parent()
            while parent_widget:
                if hasattr(parent_widget, '_toggle_play_pause'):
                    parent_widget._toggle_play_pause()
                    event.accept()
                    return
                parent_widget = parent_widget.parent()
            event.ignore()
            return
        
        # Call parent implementation for other keys
        super().keyPressEvent(event)

# ========== FileInfo proxy to show Size/Time ==========
class FileInfoProxyModel(QIdentityProxyModel):
    def __init__(self, parent_model: QFileSystemModel, duration_cache: Dict[str, int], parent=None):
        super().__init__(parent)
        self.setSourceModel(parent_model)
        self.duration_cache = duration_cache

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            if section == 1: return "Size / Time"
            if section == 3: return "Date / Time Modified"
        return super().headerData(section, orientation, role)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return super().data(index, role)
        if role == Qt.ItemDataRole.DisplayRole and index.column() == 1:
            src = self.mapToSource(index)
            fi = self.sourceModel().fileInfo(src)  # type: ignore
            if fi.isDir(): return ""
            fname = fi.fileName()
            if fname in self.duration_cache and int(self.duration_cache.get(fname, 0)) > 0:
                return human_time_ms(int(self.duration_cache[fname]))
            size = int(fi.size())
            return bytes_to_human(size)
        return super().data(index, role)

# ========== Main window ==========
class AudioBrowser(QMainWindow):

    # ---- Issue #2 helpers: release media lock for file renames ----
    def _current_media_local_path(self):
        try:
            url = self.player.source()
            if hasattr(url, "isValid") and url.isValid():
                lf = url.toLocalFile()
                if lf:
                    from pathlib import Path as _P
                    return _P(lf)
        except Exception:
            pass
        return None

    def _release_media_for_path(self, path: Path) -> None:
        # If the player is using 'path', stop and clear the source, then wait briefly
        # for the OS to release the handle (Windows).
        try:
            cur = self._current_media_local_path()
            same = False
            try:
                if cur and os.path.exists(cur) and os.path.exists(path):
                    # os.path.samefile may raise on Windows if either path doesn't exist
                    same = os.path.samefile(str(cur), str(path))
                elif cur and str(cur) == str(path):
                    same = True
            except Exception:
                same = (str(cur) == str(path))

            if same:
                try:
                    # Stop and clear the source so Windows releases the handle
                    self.player.stop()
                    from PyQt6.QtCore import QUrl
                    self.player.setSource(QUrl())  # clear media source
                except Exception:
                    pass

                # Give the OS a moment to release locks
                for _ in range(20):  # up to ~1s
                    try:
                        # Try opening for append (write) as a probe
                        with open(path, "ab"):
                            pass
                        break
                    except Exception:
                        time.sleep(0.05)
        except Exception as _e:
            print("Issue#2: release-media error:", _e)
    
    # ---- Issue #3: default annotation-set name from current user ----
    def _resolve_user_display_name(self) -> str:
        try:
            # local imports to avoid new global includes
            import subprocess, os, getpass
            # Prefer Git global user.name
            try:
                name = subprocess.check_output(
                    ["git", "config", "--global", "user.name"],
                    stderr=subprocess.DEVNULL, text=True
                ).strip()
                if name:
                    return name
            except Exception:
                pass
            # Common environment fallbacks
            for k in ("FULLNAME", "GIT_AUTHOR_NAME", "GIT_COMMITTER_NAME"):
                v = os.environ.get(k)
                if v:
                    return v
            # OS username as a last resort
            try:
                u = getpass.getuser()
                if u:
                    return u
            except Exception:
                pass
            return os.environ.get("USERNAME") or os.environ.get("USER") or "User"
        except Exception:
            return "User"

    def _default_annotation_set_name(self) -> str:
        return self._resolve_user_display_name()
    
    def _user_notes_filename(self) -> str:
        """Return user-specific notes filename based on current user."""
        user_name = self._resolve_user_display_name()
        # Clean username for filename (remove problematic characters)
        clean_user = re.sub(r'[<>:"/\\|?*]', '_', user_name)
        return f".audio_notes_{clean_user}.json"

    def _convert_default_to_user_set(self, annotation_sets: List[dict]) -> List[dict]:
        """Convert 'Default' annotation set to user-based name if no user set exists."""
        if not annotation_sets:
            return annotation_sets
        
        user_name = self._default_annotation_set_name()
        
        # Check if there's already a set with the user's name
        has_user_set = any(s.get("name") == user_name for s in annotation_sets)
        if has_user_set:
            return annotation_sets
        
        # Look for a set named "Default" (case-insensitive) to convert
        for annotation_set in annotation_sets:
            set_name = annotation_set.get("name", "")
            # Handle None or non-string names safely
            if isinstance(set_name, str) and set_name.lower() == "default":
                annotation_set["name"] = user_name
                break
        
        return annotation_sets

    # ---- External single-set auto-detect ----
    def _is_user_annotation_file(self, filepath: Path) -> bool:
        """Check if a file is a user-specific annotation file (including legacy)."""
        filename = filepath.name
        # Check for legacy .audio_notes.json
        if filename == NOTES_JSON:
            return True
        # Check for user-specific pattern: .audio_notes_<username>.json
        if filename.startswith(".audio_notes_") and filename.endswith(".json"):
            return True
        return False

    def _extract_user_from_filename(self, filepath: Path) -> str:
        """Extract username from annotation filename, or return 'Legacy' for old format."""
        filename = filepath.name
        if filename == NOTES_JSON:
            return "Legacy"
        if filename.startswith(".audio_notes_") and filename.endswith(".json"):
            # Extract username between .audio_notes_ and .json
            user_part = filename[13:-5]  # Remove ".audio_notes_" and ".json"
            return user_part or "Unknown"
        return "Unknown"

    def _scan_external_annotation_sets(self) -> List[dict]:
        ext_sets = []
        try:
            for jp in sorted(self.root_path.glob("*.json")):
                # Skip non-annotation reserved files (but allow user annotation files)
                if jp.name in RESERVED_JSON and not self._is_user_annotation_file(jp):
                    continue
                
                # Check for user-specific annotation files
                is_user_annotation = self._is_user_annotation_file(jp)
                current_user_file = jp.name == self._user_notes_filename()
                
                data = load_json(jp, None)
                if not isinstance(data, dict): continue
                
                # Handle both single-set files and multi-set user annotation files
                if "files" in data and "sets" not in data and isinstance(data["files"], dict):
                    # Single-set external file
                    name = str(data.get("name") or jp.stem)
                    color = str(data.get("color", "#00cc66") or "#00cc66")
                    visible = bool(data.get("visible", True))
                    files = {}
                    for fname, meta in (data.get("files") or {}).items():
                        if not isinstance(meta, dict): continue
                        files[str(fname)] = {
                            "general": str(meta.get("general", "") or ""),
                            "best_take": bool(meta.get("best_take", False)),
                            "notes": [{
                                "uid": int(n.get("uid", 0) or 0),
                                "ms": int(n.get("ms", 0)),
                                "text": str(n.get("text", "")),
                                "important": bool(n.get("important", False)),
                            } for n in (meta.get("notes", []) or []) if isinstance(n, dict)]
                        }
                    sid = str(data.get("id") or ("ext_" + hashlib.md5(str(jp).encode()).hexdigest()[:8]))
                    ext_sets.append({"id": sid, "name": name, "color": color, "visible": visible, "files": files, "source_path": str(jp)})
                elif is_user_annotation and not current_user_file and "sets" in data:
                    # Multi-set user annotation file from another user
                    user_name = self._extract_user_from_filename(jp)
                    sets = data.get("sets") or []
                    for s in sets:
                        if not isinstance(s, dict): continue
                        sid = str(s.get("id") or uuid.uuid4().hex[:8])
                        # Prefix the name with the user to distinguish
                        name = f"[{user_name}] {str(s.get('name', '') or 'Set')}"
                        color = str(s.get("color", "#00cc66") or "#00cc66")
                        visible = bool(s.get("visible", True))
                        files = {}
                        for fname, meta in (s.get("files", {}) or {}).items():
                            if not isinstance(meta, dict): continue
                            files[str(fname)] = {
                                "general": str(meta.get("general", "") or ""),
                                "best_take": bool(meta.get("best_take", False)),
                                "notes": [{
                                    "uid": int(n.get("uid", 0) or 0),
                                    "ms": int(n.get("ms", 0)),
                                    "text": str(n.get("text", "")),
                                    "important": bool(n.get("important", False)),
                                } for n in (meta.get("notes", []) or []) if isinstance(n, dict)]
                            }
                        # Make ID unique by prefixing with file hash to avoid conflicts
                        unique_sid = f"user_{hashlib.md5(str(jp).encode()).hexdigest()[:8]}_{sid}"
                        ext_sets.append({"id": unique_sid, "name": name, "color": color, "visible": visible, "files": files, "source_path": str(jp)})
        except Exception:
            pass
        return ext_sets

    def _append_external_sets(self):
        externals = self._scan_external_annotation_sets()
        if not externals: return
        existing_sources = {s.get("source_path") for s in self.annotation_sets if s.get("source_path")}
        existing_ids = {s.get("id") for s in self.annotation_sets}
        for s in externals:
            if s.get("source_path") in existing_sources: continue
            sid = s.get("id")
            if sid in existing_ids:
                s["id"] = s["id"] + "_" + uuid.uuid4().hex[:4]
            self.annotation_sets.append(s)

    def _strip_set_for_payload(self, s: dict) -> dict:
        return {
            "id": s.get("id"),
            "name": s.get("name", "Set"),
            "color": s.get("color", "#00cc66"),
            "visible": bool(s.get("visible", True)),
            "folder_notes": s.get("folder_notes", ""),
            "files": s.get("files", {}),
        }

    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME); self._apply_app_icon()

        self.settings = QSettings(APP_ORG, APP_NAME)
        self.root_path: Path = self._load_or_ask_root()
        self.current_practice_folder: Path = self.root_path  # Initially same as root
        self.current_audio_file: Optional[Path] = None
        self.pending_note_start_ms: Optional[int] = None
        self.clip_sel_start_ms: Optional[int] = None
        self.clip_sel_end_ms: Optional[int] = None
        self._clip_play_end_ms: Optional[int] = None
        self._clip_playing: bool = False
        self.annotation_filter: str = 'all'
        self._programmatic_selection = False
        self._uid_counter: int = 1
        self._suspend_ann_change = False

        # Undo/Redo
        self._undo_stack: List[dict] = []
        self._undo_index: int = 0
        self._undo_capacity: int = int(self.settings.value(SETTINGS_KEY_UNDO_CAP, 100))

        # Media
        self.audio_output = QAudioOutput()
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)
        self.player.errorOccurred.connect(self._on_media_error)
        self.player.mediaStatusChanged.connect(self._on_media_status)
        self.player.durationChanged.connect(self._on_duration_changed)

        vol_raw = self.settings.value(SETTINGS_KEY_VOLUME, 90)
        vol = int(vol_raw) if isinstance(vol_raw, (int, str)) else 90
        self.audio_output.setVolume(max(0.0, min(1.0, vol / 100.0)))

        # Provided names & duration cache
        self.provided_names: Dict[str, str] = {}
        self.played_durations: Dict[str, int] = self._load_duration_cache()

        # Annotation sets
        self.annotation_sets: List[Dict[str, Any]] = []
        self.current_set_id: Optional[str] = None

        # For current set fields
        self.notes_by_file: Dict[str, List[Dict]] = {}
        self.file_general: Dict[str, str] = {}
        self.file_best_takes: Dict[str, bool] = {}  # Track best takes per file in current set
        self.folder_notes: str = ""

        # Show-all toggle
        show_all_raw = self.settings.value(SETTINGS_KEY_SHOW_ALL, 0)
        self.show_all_sets: bool = bool(int(show_all_raw)) if isinstance(show_all_raw, (int, str)) else False
        
        # Show-all folder notes toggle
        show_all_folder_notes_raw = self.settings.value(SETTINGS_KEY_SHOW_ALL_FOLDER_NOTES, 0)
        self.show_all_folder_notes: bool = bool(int(show_all_folder_notes_raw)) if isinstance(show_all_folder_notes_raw, (int, str)) else False

        # Fingerprinting
        self.fingerprint_reference_dir: Optional[Path] = None
        ref_dir_str = self.settings.value(SETTINGS_KEY_FINGERPRINT_DIR, "")
        if ref_dir_str and Path(ref_dir_str).exists():
            self.fingerprint_reference_dir = Path(ref_dir_str)
        
        self.fingerprint_threshold: float = float(self.settings.value(SETTINGS_KEY_FINGERPRINT_THRESHOLD, 0.7))
        self.fingerprint_cache: Dict[str, Dict] = {}  # loaded per directory
        
        # Auto-labeling state management
        self.auto_label_in_progress: bool = False
        self.auto_label_backup_names: Dict[str, str] = {}

        # UI
        self._init_ui()

        # Load metadata
        self._load_names()
        self._load_notes()
        self._ensure_uids()

        # Populate UI
        self._refresh_set_combo()
        self._refresh_right_table()
        self._load_annotations_for_current()
        self._update_folder_notes_ui()
        self._refresh_important_table()
        self._update_fingerprint_ui()

        # Tree selection & timers
        self.tree.selectionModel().selectionChanged.connect(self._on_tree_selection_changed)
        self.slider_sync = QTimer(self); self.slider_sync.setInterval(200)
        self.slider_sync.timeout.connect(self._sync_slider)
        self.player.positionChanged.connect(lambda _: self._sync_slider())

        # Waveform hooks
        self.waveform.markerMoved.connect(self._on_marker_moved_multi)
        self.waveform.markerReleased.connect(self._on_marker_released_multi)
        self.waveform.seekRequested.connect(self._on_waveform_seek_requested)
        self.waveform.annotationClicked.connect(self._on_waveform_annotation_clicked_multi)

        # Toggles
        self._restore_toggles()
        self._update_undo_actions_enabled()

    # ----- Icon -----
    def _apply_app_icon(self):
        icon_png = resource_path(APP_ICON_NAME)
        if icon_png.exists():
            self.setWindowIcon(QIcon(str(icon_png))); return
        pm = QPixmap(256, 256); pm.fill(Qt.GlobalColor.transparent)
        p = QPainter(pm); p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.setPen(Qt.PenStyle.NoPen); p.setBrush(QColor("#FFCB2B"))
        p.drawRoundedRect(28, 84, 200, 128, 20, 20)
        p.drawRoundedRect(56, 64, 90, 36, 10, 10)
        p.setBrush(QColor("#222")); p.setPen(QColor("#222"))
        p.drawRect(150, 80, 12, 90); p.drawEllipse(118, 150, 38, 28)
        p.setBrush(QColor("#2E7D32")); p.setPen(Qt.PenStyle.NoPen)
        pts = [ (70,120), (70,180), (120,150) ]
        p.drawPolygon(*[QPoint(x,y) for x,y in pts]); p.end()
        self.setWindowIcon(QIcon(pm))

    # ----- Settings & metadata -----
    def _load_or_ask_root(self) -> Path:
        stored = self.settings.value(SETTINGS_KEY_ROOT, "", type=str)
        if stored and Path(stored).exists(): return Path(stored)
        dlg = QFileDialog(self, "Select your root band practice folder")
        dlg.setFileMode(QFileDialog.FileMode.Directory)
        dlg.setOption(QFileDialog.Option.ShowDirsOnly, True)
        if dlg.exec():
            p = Path(dlg.selectedFiles()[0]); self.settings.setValue(SETTINGS_KEY_ROOT, str(p)); return p
        home = Path.home(); self.settings.setValue(SETTINGS_KEY_ROOT, str(home)); return home

    def _save_root(self, p: Path):
        self.root_path = p; self.settings.setValue(SETTINGS_KEY_ROOT, str(p))
        self.current_practice_folder = p  # Reset to root when changing root
        self.path_label.setText(f"Band Practice Directory: {self.root_path}")
        self.fs_model.setRootPath(str(self.root_path))
        self._programmatic_selection = True
        try:
            src = self.fs_model.index(str(self.root_path))
            self.tree.setRootIndex(self.file_proxy.mapFromSource(src))
        finally:
            QTimer.singleShot(0, lambda: setattr(self, "_programmatic_selection", False))
        # Reload per-folder state
        self.current_audio_file = None  # Clear current audio file before loading metadata
        self.played_durations = self._load_duration_cache()
        self.file_proxy.duration_cache = self.played_durations
        self._load_names(); self._load_notes(); self._ensure_uids()
        self._refresh_set_combo()
        self._refresh_right_table()
        self._load_annotations_for_current()
        self._update_folder_notes_ui()
        self._refresh_important_table()
        self._update_fingerprint_ui()
        self.waveform.clear()

    def _names_json_path(self) -> Path: 
        # When an audio file is selected, use its directory for provided names
        if self.current_audio_file:
            return self.current_audio_file.parent / NAMES_JSON
        return self.current_practice_folder / NAMES_JSON
    def _notes_json_path(self) -> Path: 
        # When an audio file is selected, use its directory for annotations
        user_notes_filename = self._user_notes_filename()
        if self.current_audio_file:
            return self.current_audio_file.parent / user_notes_filename
        return self.current_practice_folder / user_notes_filename
    def _dur_json_path(self) -> Path: 
        # When an audio file is selected, use its directory for duration cache
        if self.current_audio_file:
            return self.current_audio_file.parent / DURATIONS_JSON
        return self.current_practice_folder / DURATIONS_JSON
    
    def _get_audio_file_dir(self) -> Path:
        """Return the directory containing the current audio file, or current_practice_folder if no file selected."""
        if self.current_audio_file:
            return self.current_audio_file.parent
        return self.current_practice_folder
    
    def _set_current_practice_folder(self, folder: Path):
        """Update the current practice folder (distinct from root band practice folder)."""
        if folder.exists() and folder.is_dir():
            self.current_practice_folder = folder
    
    def _get_notes_json_path_for_audio_file(self) -> Path:
        """Return the notes JSON path for the current audio file's directory."""
        return self._get_audio_file_dir() / NOTES_JSON

    def _load_names(self):
        self.provided_names = load_json(self._names_json_path(), {}) or {}

    def _save_names(self):
        save_json(self._names_json_path(), self.provided_names)

    # ----- Annotation sets load/save -----
    def _create_default_set(self, carry_notes: Optional[Dict[str, List[Dict]]] = None, carry_general: Optional[Dict[str, str]] = None, carry_folder_notes: str = ""):
        sid = uuid.uuid4().hex[:8]
        aset = {"id": sid, "name": self._default_annotation_set_name(), "color": "#00cc66", "visible": True, "folder_notes": carry_folder_notes, "files": {}}
        if carry_notes or carry_general:
            all_files = set((carry_notes or {}).keys()) | set((carry_general or {}).keys())
            for fname in all_files:
                aset["files"][fname] = {
                    "general": (carry_general or {}).get(fname, ""),
                    "notes": list((carry_notes or {}).get(fname, []))
                }
        self.annotation_sets = [aset]; self.current_set_id = sid
        self.settings.setValue(SETTINGS_KEY_CUR_SET, sid)
        self._load_current_set_into_fields()

    def _load_notes(self):
        self.annotation_sets = []
        self.notes_by_file = {}; self.file_general = {}; self.file_best_takes = {}; self.folder_notes = ""

        
        # Check for migration from legacy file
        user_notes_path = self._notes_json_path()
        legacy_notes_path = (self.current_audio_file.parent if self.current_audio_file else self.current_practice_folder) / NOTES_JSON
        
        # If user-specific file doesn't exist but legacy file does, migrate it
        if not user_notes_path.exists() and legacy_notes_path.exists():
            try:
                legacy_data = load_json(legacy_notes_path, {})
                if legacy_data:  # Only migrate if there's actual data
                    save_json(user_notes_path, legacy_data)
                    print(f"Migrated annotations from {legacy_notes_path.name} to {user_notes_path.name}")
            except Exception as e:
                print(f"Warning: Could not migrate legacy annotations: {e}")
        
        data = load_json(user_notes_path, {})
        try:
            if isinstance(data, dict) and "sets" in data:
                # Handle migration from global folder_notes to per-set folder_notes
                global_folder_notes = str(data.get("folder_notes", "") or "")
                sets = data.get("sets") or []
                cleaned = []
                for s in sets:
                    if not isinstance(s, dict): continue
                    sid = str(s.get("id") or uuid.uuid4().hex[:8])
                    name = str(s.get("name", "") or "Set")
                    color = str(s.get("color", "#00cc66") or "#00cc66")
                    visible = bool(s.get("visible", True))
                    # Handle per-set folder notes, migrating from global if needed
                    folder_notes = str(s.get("folder_notes", "") or "")
                    if not folder_notes and global_folder_notes:
                        folder_notes = global_folder_notes  # Migrate global notes to each set
                    files = {}
                    for fname, meta in (s.get("files", {}) or {}).items():
                        if not isinstance(meta, dict): continue
                        files[str(fname)] = {
                            "general": str(meta.get("general", "") or ""),
                            "best_take": bool(meta.get("best_take", False)),
                            "notes": [{
                                "uid": int(n.get("uid", 0) or 0),
                                "ms": int(n.get("ms", 0)),
                                "text": str(n.get("text", "")),
                                "important": bool(n.get("important", False)),
                                **({"end_ms": int(n["end_ms"])} if n.get("end_ms") is not None else {})
                            } for n in (meta.get("notes", []) or []) if isinstance(n, dict)]
                        }
                    cleaned.append({"id": sid, "name": name, "color": color, "visible": visible, "folder_notes": folder_notes, "files": files})
                if not cleaned:
                    self._create_default_set()
                else:
                    # Convert "Default" set to user-based name if needed
                    cleaned = self._convert_default_to_user_set(cleaned)
                    self.annotation_sets = cleaned
                    cur = self.settings.value(SETTINGS_KEY_CUR_SET, "", type=str) or ""
                    if not any(s["id"] == cur for s in self.annotation_sets): cur = self.annotation_sets[0]["id"]
                    self.current_set_id = cur
                    self._load_current_set_into_fields()
            else:
                # Legacy single-set file
                legacy_folder_notes = str(data.get("folder_notes", "") or "")
                fgen, fnote = {}, {}
                if isinstance(data, dict) and "files" in data:
                    for fname, meta in (data.get("files", {}) or {}).items():
                        if not isinstance(meta, dict): continue
                        fgen[str(fname)] = str(meta.get("general", "") or "")
                        clean = []
                        for n in (meta.get("notes", []) or []):
                            if not isinstance(n, dict): continue
                            clean.append({
                                "uid": int(n.get("uid", 0) or 0),
                                "ms": int(n.get("ms", 0)),
                                "text": str(n.get("text", "")),
                                "important": bool(n.get("important", False))
                            })
                        fnote[str(fname)] = clean
                self._create_default_set(carry_notes=fnote, carry_general=fgen, carry_folder_notes=legacy_folder_notes)
        except Exception:
            self._create_default_set()

        # Discover external single-set annotation files in this folder
        self._append_external_sets()

    def _save_notes(self):
        self._sync_fields_into_current_set()
        try:
            internal_sets = [self._strip_set_for_payload(s) for s in self.annotation_sets if not s.get("source_path")]
            payload = {
                "version": 3,
                "updated": datetime.now().isoformat(timespec="seconds"),
                "sets": internal_sets,
            }
            save_json(self._notes_json_path(), payload)
            # Save external sets to their own files
            for s in self.annotation_sets:
                sp = s.get("source_path")
                if not sp: continue
                try:
                    save_json(Path(sp), self._strip_set_for_payload(s))
                except Exception:
                    pass
        except Exception as e:
            QMessageBox.warning(self, "Save Notes Failed", f"Couldn't save annotation notes:\n{e}")

    def _load_current_set_into_fields(self):
        aset = self._get_current_set()
        self.notes_by_file = {}; self.file_general = {}; self.file_best_takes = {}
        if aset:
            for fname, meta in aset.get("files", {}).items():
                self.file_general[fname] = str(meta.get("general", "") or "")
                self.file_best_takes[fname] = bool(meta.get("best_take", False))
                self.notes_by_file[fname] = [dict(n) for n in (meta.get("notes", []) or [])]
        else:
            self.notes_by_file = {}; self.file_general = {}; self.file_best_takes = {}
        self._update_general_label()

    def _sync_fields_into_current_set(self):
        aset = self._get_current_set()
        if not aset: return
        files = {}
        all_files = set(self.notes_by_file.keys()) | set(self.file_general.keys()) | set(self.file_best_takes.keys())
        for fname in all_files:
            files[fname] = {
                "general": self.file_general.get(fname, ""),
                "best_take": self.file_best_takes.get(fname, False),
                "notes": self.notes_by_file.get(fname, []),
            }
        aset["files"] = files

    def _get_current_set(self) -> Optional[Dict[str, Any]]:
        for s in self.annotation_sets:
            if s.get("id") == self.current_set_id: return s
        return self.annotation_sets[0] if self.annotation_sets else None

    def _update_general_label(self):
        """Update the general_label to show the current annotation set name."""
        aset = self._get_current_set()
        if aset:
            set_name = aset.get("name", "Set")
            self.general_label.setText(f"Song overview ({set_name}):")
        else:
            self.general_label.setText("Song overview (no set):")

    def _ensure_uids(self):
        mx = self._uid_counter
        for aset in self.annotation_sets:
            for lst in (f.get("notes", []) for f in aset.get("files", {}).values()):
                for n in lst:
                    if int(n.get("uid", 0)) <= 0:
                        n["uid"] = mx; mx += 1
                    else:
                        if n["uid"] >= mx: mx = n["uid"] + 1
        self._uid_counter = mx

    def _load_duration_cache(self) -> Dict[str,int]:
        d = load_json(self._dur_json_path(), {}) or {}
        out = {}
        for k,v in d.items():
            try: out[str(k)] = int(v)
            except Exception: pass
        return out

    def _save_duration_cache(self):
        save_json(self._dur_json_path(), self.played_durations)

    # ----- UI -----
    def _init_ui(self):
        self.resize(1360, 900); self.setStatusBar(QStatusBar(self))
        tb = QToolBar("Main"); self.addToolBar(tb)

        # Undo/Redo
        self.act_undo = QAction("Undo", self); self.act_undo.setShortcut(QKeySequence.StandardKey.Undo)
        self.act_redo = QAction("Redo", self); self.act_redo.setShortcut(QKeySequence.StandardKey.Redo)
        self.act_undo.triggered.connect(self._undo); self.act_redo.triggered.connect(self._redo)
        tb.addAction(self.act_undo); tb.addAction(self.act_redo)

        tb.addSeparator()
        tb.addWidget(QLabel("Undo limit:"))
        self.undo_spin = QSpinBox(); self.undo_spin.setRange(10, 1000); self.undo_spin.setValue(int(self.settings.value(SETTINGS_KEY_UNDO_CAP, 100)))
        self.undo_spin.valueChanged.connect(self._on_undo_capacity_changed)
        tb.addWidget(self.undo_spin)
        tb.addSeparator()

        act_change_root = QAction("Change Band Practice Folder…", self); act_change_root.triggered.connect(self._change_root_clicked); tb.addAction(act_change_root)
        act_up = QAction("Up", self); act_up.setShortcut(QKeySequence("Alt+Up")); act_up.triggered.connect(self._go_up); tb.addAction(act_up)
        tb.addSeparator()
        self.rename_action = QAction("Batch Rename (##_ProvidedName)", self); self.rename_action.triggered.connect(self._batch_rename); tb.addAction(self.rename_action)
        self.export_action = QAction("Export Annotations…", self); self.export_action.triggered.connect(self._export_annotations); tb.addAction(self.export_action)
        self.convert_action = QAction("Convert WAV→MP3 (delete WAVs)", self); self.convert_action.triggered.connect(self._convert_wav_to_mp3_threaded); tb.addAction(self.convert_action)
        tb.addSeparator()

        self.auto_switch_cb = QCheckBox("Auto-switch to Annotations")
        wa = QWidgetAction(self); wa.setDefaultWidget(self.auto_switch_cb); tb.addAction(wa)

        # Create main widget to hold path label and splitter
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for cleaner look
        
        # Add path label at the top
        self.path_label = QLabel()
        self.path_label.setStyleSheet("QLabel { background-color: #f0f0f0; padding: 8px; border-bottom: 1px solid #ccc; font-weight: bold; }")
        self.path_label.setText(f"Band Practice Directory: {self.root_path}")
        main_layout.addWidget(self.path_label)

        splitter = QSplitter(self); main_layout.addWidget(splitter)

        # Tree model
        self.fs_model = QFileSystemModel(self)
        self.fs_model.setResolveSymlinks(True); self.fs_model.setReadOnly(True)
        self.fs_model.setFilter(QDir.Filter.AllDirs | QDir.Filter.NoDotAndDotDot | QDir.Filter.Drives | QDir.Filter.Files)
        self.fs_model.setNameFilters(["*.wav", "*.wave", "*.mp3"])
        self.fs_model.setNameFilterDisables(False)
        self.fs_model.setRootPath(str(self.root_path))

        self.file_proxy = FileInfoProxyModel(self.fs_model, self.played_durations, self)

        self.tree = QTreeView()
        self.tree.setModel(self.file_proxy)
        self.tree.setRootIndex(self.file_proxy.mapFromSource(self.fs_model.index(str(self.root_path))))
        self.tree.setColumnHidden(1, True)  # hide Size/Time column
        self.tree.setColumnHidden(2, True)  # hide Type column  
        self.tree.setColumnHidden(3, True)  # hide Date Modified column
        self.tree.setColumnWidth(0, 360)
        self.tree.setAlternatingRowColors(True)
        # Enhanced selection styling for better visibility
        self.tree.setStyleSheet("""
            QTreeView::item:selected {
                background-color: #1e3a8a;
                color: white;
            }
            QTreeView::item:selected:active {
                background-color: #1d4ed8;
                color: white;
            }
            QTreeView::item:selected:!active {
                background-color: #2563eb;
                color: white;
            }
        """)
        self.tree.setSortingEnabled(True); self.tree.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.tree.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tree.doubleClicked.connect(self._on_tree_double_clicked)
        self.tree.activated.connect(self._on_tree_activated)
        splitter.addWidget(self.tree)

        # Right panel
        right = QWidget(); splitter.addWidget(right)
        splitter.setStretchFactor(0, 2); splitter.setStretchFactor(1, 3)
        right_layout = QVBoxLayout(right)

        # Player bar
        player_bar = QHBoxLayout()
        self.play_pause_btn = QPushButton(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay), ""); self.play_pause_btn.setEnabled(False)
        self.play_pause_btn.clicked.connect(self._toggle_play_pause); player_bar.addWidget(self.play_pause_btn)

        self.position_slider = SeekSlider(Qt.Orientation.Horizontal)
        self.position_slider.setEnabled(False)
        self.position_slider.sliderPressed.connect(lambda: self._user_scrubbing(True))
        self.position_slider.sliderReleased.connect(lambda: self._user_scrubbing(False))
        self.position_slider.sliderMoved.connect(self._on_slider_moved)
        self.position_slider.clickedValue.connect(self._on_slider_clicked_value)
        player_bar.addWidget(self.position_slider, 1)

        self.time_label = QLabel("0:00 / 0:00"); player_bar.addWidget(self.time_label)

        player_bar.addWidget(QLabel("Vol"))
        self.volume_slider = QSlider(Qt.Orientation.Horizontal); self.volume_slider.setFixedWidth(140)
        self.volume_slider.setRange(0, 100); self.volume_slider.setValue(int(self.audio_output.volume() * 100))
        self.volume_slider.valueChanged.connect(self._on_volume_changed)
        player_bar.addWidget(self.volume_slider)

        player_bar.addWidget(QLabel("Output"))
        self.output_device_combo = QComboBox(); self.output_device_combo.setFixedWidth(200)
        self.output_device_combo.currentIndexChanged.connect(self._on_output_device_changed)
        player_bar.addWidget(self.output_device_combo)

        self.auto_progress_cb = QCheckBox("Auto-progress"); player_bar.addWidget(self.auto_progress_cb)

        right_layout.addLayout(player_bar)

        # Initialize output devices
        self._refresh_output_devices()

        self.now_playing = QLabel("No selection"); self.now_playing.setStyleSheet("color: #666;")
        right_layout.addWidget(self.now_playing)

        # Tabs
        self.tabs = QTabWidget(); right_layout.addWidget(self.tabs, 1)
        self.tabs.setDocumentMode(True); self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabs.setMovable(True)
        self.tabs.tabBar().tabMoved.connect(self._on_tab_moved)

        # Folder Notes tab
        self.folder_tab = QWidget(); folder_layout = QVBoxLayout(self.folder_tab)
        self.folder_label = QLabel("Notes for current folder:")
        
        # Show all folder notes checkbox
        self.show_all_folder_notes_cb = QCheckBox("Show all folder notes from visible sets")
        self.show_all_folder_notes_cb.setChecked(self.show_all_folder_notes)
        self.show_all_folder_notes_cb.stateChanged.connect(self._on_show_all_folder_notes_toggled)
        
        self.folder_notes_edit = QPlainTextEdit(); self.folder_notes_edit.setPlaceholderText("Write notes about this folder/collection.")
        self.folder_notes_edit.textChanged.connect(self._on_folder_notes_changed)
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(self.show_all_folder_notes_cb)
        folder_layout.addWidget(self.folder_notes_edit, 1)

        self.imp_label = QLabel("Important annotations in this folder:")
        folder_layout.addWidget(self.imp_label)
        self.imp_table = QTableWidget(0, 4)
        self.imp_table.setHorizontalHeaderLabels(["Set", "File", "Time", "Note"])
        ih = self.imp_table.horizontalHeader()
        ih.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        ih.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        ih.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        ih.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.imp_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.imp_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.imp_table.itemDoubleClicked.connect(self._on_important_double_clicked)
        folder_layout.addWidget(self.imp_table, 1)

        # Library tab
        self.lib_tab = QWidget(); lib_layout = QVBoxLayout(self.lib_tab)
        
        # Fingerprinting section
        fp_group = QWidget()
        fp_layout = QVBoxLayout(fp_group)
        fp_layout.setContentsMargins(10, 10, 10, 10)
        fp_group.setStyleSheet("QWidget { background-color: #f8f8f8; border: 1px solid #ccc; border-radius: 5px; }")
        
        fp_title = QLabel("Audio Fingerprinting")
        fp_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #333;")
        fp_layout.addWidget(fp_title)
        
        # Reference folder selection
        ref_row = QHBoxLayout()
        ref_row.addWidget(QLabel("Reference folder:"))
        self.fingerprint_ref_label = QLabel("(None selected)")
        self.fingerprint_ref_label.setStyleSheet("color: #666; font-style: italic;")
        ref_row.addWidget(self.fingerprint_ref_label, 1)
        self.select_ref_btn = QPushButton("Choose...")
        self.select_ref_btn.clicked.connect(self._select_fingerprint_reference_folder)
        ref_row.addWidget(self.select_ref_btn)
        fp_layout.addLayout(ref_row)
        
        # Threshold and actions
        threshold_row = QHBoxLayout()
        threshold_row.addWidget(QLabel("Match threshold:"))
        self.threshold_spin = QSpinBox()
        self.threshold_spin.setRange(50, 95)
        self.threshold_spin.setValue(int(self.fingerprint_threshold * 100))
        self.threshold_spin.setSuffix("%")
        self.threshold_spin.valueChanged.connect(self._on_fingerprint_threshold_changed)
        threshold_row.addWidget(self.threshold_spin)
        threshold_row.addStretch(1)
        
        self.generate_fingerprints_btn = QPushButton("Generate Fingerprints for Current Folder")
        self.generate_fingerprints_btn.clicked.connect(self._generate_fingerprints_for_folder)
        threshold_row.addWidget(self.generate_fingerprints_btn)
        
        self.auto_label_btn = QPushButton("Auto-Label Files")
        self.auto_label_btn.clicked.connect(self._auto_label_with_fingerprints)
        self.auto_label_btn.setEnabled(False)  # Enabled when reference folder is set
        threshold_row.addWidget(self.auto_label_btn)
        
        self.show_practice_folders_btn = QPushButton("Show Practice Folders")
        self.show_practice_folders_btn.clicked.connect(self._show_practice_folders_info)
        threshold_row.addWidget(self.show_practice_folders_btn)
        
        fp_layout.addLayout(threshold_row)
        
        # Status label
        self.fingerprint_status = QLabel("")
        self.fingerprint_status.setStyleSheet("color: #666; font-size: 11px;")
        fp_layout.addWidget(self.fingerprint_status)
        
        # Apply/Cancel buttons for auto-labeling (initially hidden)
        self.auto_label_buttons_row = QHBoxLayout()
        self.auto_label_buttons_row.addStretch(1)  # Push buttons to the right
        self.auto_label_apply_btn = QPushButton("Apply")
        self.auto_label_apply_btn.clicked.connect(self._on_auto_label_apply)
        self.auto_label_apply_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        self.auto_label_buttons_row.addWidget(self.auto_label_apply_btn)
        
        self.auto_label_cancel_btn = QPushButton("Cancel")
        self.auto_label_cancel_btn.clicked.connect(self._on_auto_label_cancel)
        self.auto_label_cancel_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-weight: bold; }")
        self.auto_label_buttons_row.addWidget(self.auto_label_cancel_btn)
        
        self.auto_label_buttons_widget = QWidget()
        self.auto_label_buttons_widget.setLayout(self.auto_label_buttons_row)
        self.auto_label_buttons_widget.setVisible(False)  # Initially hidden
        fp_layout.addWidget(self.auto_label_buttons_widget)
        
        lib_layout.addWidget(fp_group)
        
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["File", "Best Take", "Provided Name (editable)"])
        hh = self.table.horizontalHeader(); hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.SelectedClicked)
        self.table.itemChanged.connect(self._on_table_item_changed)
        lib_layout.addWidget(self.table, 1)
        self.table.itemSelectionChanged.connect(self._stop_if_no_file_selected)

        self.table.cellClicked.connect(self._on_library_cell_clicked)
# Annotations tab
        self.ann_tab = QWidget(); ann_layout = QVBoxLayout(self.ann_tab)

        set_row = QHBoxLayout()
        set_row.addWidget(QLabel("Annotation set:"))
        self.set_combo = QComboBox()
        self.set_combo.currentIndexChanged.connect(self._on_set_combo_changed)
        set_row.addWidget(self.set_combo, 1)
        self.set_visible_cb = QCheckBox("Visible")
        self.set_visible_cb.stateChanged.connect(self._on_set_visible_toggled)
        set_row.addWidget(self.set_visible_cb)
        self.set_color_btn = QPushButton("Color…")
        self.set_color_btn.clicked.connect(self._on_set_pick_color)
        set_row.addWidget(self.set_color_btn)
        self.add_set_btn = QPushButton("Add Set")
        self.add_set_btn.clicked.connect(self._on_add_set)
        set_row.addWidget(self.add_set_btn)
        self.rename_set_btn = QPushButton("Rename")
        self.rename_set_btn.clicked.connect(self._on_rename_set)
        set_row.addWidget(self.rename_set_btn)
        self.del_set_btn = QPushButton("Delete")
        self.del_set_btn.clicked.connect(self._on_delete_set)
        set_row.addWidget(self.del_set_btn)
        self.show_all_cb = QCheckBox("Show all visible sets in table")
        self.show_all_cb.setChecked(self.show_all_sets)
        self.show_all_cb.stateChanged.connect(self._on_show_all_toggled)
        set_row.addWidget(self.show_all_cb)

        ann_layout.addLayout(set_row)

        # Provided name editor and best take checkbox
        pn_row = QHBoxLayout()
        pn_row.addWidget(QLabel("Provided Name:"))
        self.provided_name_edit = QLineEdit()
        self.provided_name_edit.setPlaceholderText("Optional display name used by batch rename")
        self.provided_name_edit.setEnabled(False)
        self.provided_name_edit.returnPressed.connect(self._on_provided_name_edited)
        self.provided_name_edit.editingFinished.connect(self._on_provided_name_edited)
        pn_row.addWidget(self.provided_name_edit, 1)
        
        # Best Take checkbox in annotation tab
        self.best_take_cb = QCheckBox("Best Take")
        self.best_take_cb.setToolTip("Mark this song as the best take")
        self.best_take_cb.setEnabled(False)
        self.best_take_cb.stateChanged.connect(self._on_best_take_changed)
        pn_row.addWidget(self.best_take_cb)
        
        ann_layout.addLayout(pn_row)

        self.waveform = WaveformView(); self.waveform.bind_player(self.player)
        self.waveform.installEventFilter(self)
        ann_layout.addWidget(self.waveform)
        # --- Clip selection controls (Issue #4) ---
        clip_row = QHBoxLayout()
        clip_row.addWidget(QLabel("Clip Start:"))
        self.clip_start_edit = QLineEdit(); self.clip_start_edit.setPlaceholderText("mm:ss")
        self.clip_start_edit.setMaximumWidth(100)
        clip_row.addWidget(self.clip_start_edit)
        clip_row.addWidget(QLabel("Clip End:"))
        self.clip_end_edit = QLineEdit(); self.clip_end_edit.setPlaceholderText("mm:ss")
        self.clip_end_edit.setMaximumWidth(100)
        clip_row.addWidget(self.clip_end_edit)
        self.clip_play_btn = QPushButton("Play Clip")
        self.clip_save_btn = QPushButton("Save Clip")
        self.clip_cancel_btn = QPushButton("Cancel")
        clip_row.addWidget(self.clip_play_btn)
        clip_row.addWidget(self.clip_save_btn)
        clip_row.addWidget(self.clip_cancel_btn)
        ann_layout.addLayout(clip_row)

        # Filter combo for annotations
        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Show:"))
        self.ann_filter_combo = QComboBox()
        self.ann_filter_combo.addItems(["All", "Points", "Clips"])
        filter_row.addWidget(self.ann_filter_combo); filter_row.addStretch(1)
        ann_layout.addLayout(filter_row)


        top_controls = QHBoxLayout()
        self.captured_time_label = QLabel(""); self.captured_time_label.setMinimumWidth(90)
        self.note_input = QLineEdit(); self.note_input.setPlaceholderText("Type to create a note; press Enter to add")
        self.note_input.textEdited.connect(self._on_note_text_edited)
        self.note_input.textChanged.connect(self._on_note_text_changed_clear_capture)
        self.note_input.returnPressed.connect(self._on_note_return_pressed)
        top_controls.addWidget(QLabel("New note time:")); top_controls.addWidget(self.captured_time_label)
        top_controls.addWidget(QLabel("Text:")); top_controls.addWidget(self.note_input, 1)
        ann_layout.addLayout(top_controls)

        self.general_label = QLabel("Song overview (current set):")
        self.general_edit = QPlainTextEdit(); self.general_edit.setPlaceholderText("Write a general description/notes for this song (current set).")
        self.general_edit.textChanged.connect(self._on_general_changed)
        ann_layout.addWidget(self.general_label); ann_layout.addWidget(self.general_edit, 1)

        self.annotation_table = QTableWidget(0, 3)
        ann_layout.addWidget(self.annotation_table, 2)
        self._configure_annotation_table()
        # Issue #4 connections
        self.clip_start_edit.editingFinished.connect(self._on_clip_time_edits_changed)
        self.clip_end_edit.editingFinished.connect(self._on_clip_time_edits_changed)
        self.clip_play_btn.clicked.connect(self._on_clip_play_clicked)
        self.clip_save_btn.clicked.connect(self._on_clip_save_clicked)
        self.clip_cancel_btn.clicked.connect(self._on_clip_cancel_clicked)
        self.ann_filter_combo.currentIndexChanged.connect(self._on_ann_filter_changed)
        # also stop clip at end
        self.player.positionChanged.connect(self._on_player_pos_for_clip)


        bottom_controls = QHBoxLayout()
        self.delete_note_btn = QPushButton("Delete Selected"); self.delete_note_btn.clicked.connect(self._delete_selected_annotations)
        bottom_controls.addStretch(1); bottom_controls.addWidget(self.delete_note_btn)
        ann_layout.addLayout(bottom_controls)
        self.export_clips_btn = QPushButton("Export Clips")
        bottom_controls.insertWidget(0, self.export_clips_btn)
        self.export_clips_btn.clicked.connect(self._on_export_clips_clicked)


        # Tabs default order
        self.tabs.addTab(self.folder_tab, "Folder Notes")
        self.tabs.addTab(self.lib_tab, "Library")
        self.tabs.addTab(self.ann_tab, "Annotations")
        self._restore_tab_order()

        if "Fusion" in QStyleFactory.keys(): QApplication.instance().setStyle("Fusion")

        self._general_save_timer = QTimer(self); self._general_save_timer.setSingleShot(True); self._general_save_timer.timeout.connect(self._save_notes)
        self._folder_save_timer = QTimer(self); self._folder_save_timer.setSingleShot(True); self._folder_save_timer.timeout.connect(self._save_notes)

    # ----- Set controls helpers -----
    def _refresh_set_combo(self):
        self.set_combo.blockSignals(True)
        self.set_combo.clear()
        for aset in self.annotation_sets:
            name = aset.get("name","Set")
            color = hex_to_color(aset.get("color","#00cc66"))
            pm = QPixmap(16,16); pm.fill(color)
            icon = QIcon(pm)
            self.set_combo.addItem(icon, name, userData=aset.get("id"))
        self.set_combo.blockSignals(False)
        cur = self.current_set_id or (self.annotation_sets[0]["id"] if self.annotation_sets else None)
        if cur:
            for i in range(self.set_combo.count()):
                if str(self.set_combo.itemData(i)) == str(cur):
                    self.set_combo.setCurrentIndex(i); break
        aset = self._get_current_set()
        if aset: self.set_visible_cb.setChecked(bool(aset.get("visible", True)))
        self._update_waveform_annotations()

    def _on_set_combo_changed(self, idx: int):
        if idx < 0: return
        new_id = str(self.set_combo.itemData(idx))
        if not new_id: return
        self._sync_fields_into_current_set()
        self.current_set_id = new_id
        self.settings.setValue(SETTINGS_KEY_CUR_SET, new_id)
        self._load_current_set_into_fields()
        self._load_annotations_for_current()
        aset = self._get_current_set()
        if aset: self.set_visible_cb.setChecked(bool(aset.get("visible", True)))
        self._update_waveform_annotations()
        self._refresh_important_table()
        self._update_folder_notes_ui()  # Update folder notes UI when set changes

    def _on_set_visible_toggled(self, _state):
        aset = self._get_current_set()
        if not aset: return
        aset["visible"] = bool(self.set_visible_cb.isChecked())
        self._save_notes()
        self._update_waveform_annotations()
        self._refresh_important_table()
        self._load_annotations_for_current()

    def _on_set_pick_color(self):
        aset = self._get_current_set()
        if not aset: return
        c0 = hex_to_color(aset.get("color","#00cc66"))
        c = QColorDialog.getColor(c0, self, "Pick marker color for this set")
        if c.isValid():
            aset["color"] = color_to_hex(c)
            self._save_notes()
            self._refresh_set_combo()
            self._update_waveform_annotations()
            self._load_annotations_for_current()

    def _on_add_set(self):
        name, ok = QInputDialog.getText(self, "Add Annotation Set", "Name:", text=self._default_annotation_set_name())
        if not ok:
            return
        name = name.strip() or self._default_annotation_set_name()
        c = QColorDialog.getColor(hex_to_color("#00cc66"), self, "Pick marker color")
        color = color_to_hex(c) if c.isValid() else "#00cc66"
        sid = uuid.uuid4().hex[:8]
        self.annotation_sets.append({"id": sid, "name": name.strip(), "color": color, "visible": True, "files": {}})
        self.current_set_id = sid
        self.settings.setValue(SETTINGS_KEY_CUR_SET, sid)
        self._load_current_set_into_fields()
        self._refresh_set_combo()
        self._load_annotations_for_current()
        self._save_notes()

    def _on_rename_set(self):
        aset = self._get_current_set()
        if not aset: return
        name, ok = QInputDialog.getText(self, "Rename Annotation Set", "New name:", text=str(aset.get("name","Set")))
        if not ok:
            return
        name = name.strip() or self._default_annotation_set_name()
        aset["name"] = name.strip()
        self._update_general_label()
        self._refresh_set_combo(); self._save_notes(); self._refresh_important_table(); self._load_annotations_for_current()

    def _on_delete_set(self):
        if len(self.annotation_sets) <= 1:
            QMessageBox.information(self, "Can't delete", "At least one annotation set is required."); return
        aset = self._get_current_set()
        if not aset: return
        if QMessageBox.question(self, "Delete Annotation Set",
                                f"Delete set '{aset.get('name','Set')}'? This removes its notes permanently.",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return
        sid = aset.get("id"); src_path = aset.get("source_path")
        self.annotation_sets = [s for s in self.annotation_sets if s.get("id") != sid]
        if src_path and Path(src_path).exists():
            if QMessageBox.question(self, "Delete Set File?", f"Also delete the external set file?\n{src_path}", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
                try: Path(src_path).unlink()
                except Exception: pass
        self.current_set_id = self.annotation_sets[0]["id"]
        self.settings.setValue(SETTINGS_KEY_CUR_SET, self.current_set_id)
        self._load_current_set_into_fields()
        self._refresh_set_combo()
        self._load_annotations_for_current()
        self._save_notes()
        self._refresh_important_table()

    # ----- Show-all toggle -----
    def _on_show_all_toggled(self, _state):
        self.show_all_sets = bool(self.show_all_cb.isChecked())
        self.settings.setValue(SETTINGS_KEY_SHOW_ALL, int(self.show_all_sets))
        self._configure_annotation_table()
        self._load_annotations_for_current()

    def _on_show_all_folder_notes_toggled(self, _state):
        self.show_all_folder_notes = bool(self.show_all_folder_notes_cb.isChecked())
        self.settings.setValue(SETTINGS_KEY_SHOW_ALL_FOLDER_NOTES, int(self.show_all_folder_notes))
        self._update_folder_notes_ui()

    # ----- Tab order -----
    def _tab_index_by_name(self, name: str) -> int:
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == name: return i
        return -1

    def _on_tab_moved(self, *_):
        order = [self.tabs.tabText(i) for i in range(self.tabs.count())]
        self.settings.setValue(SETTINGS_KEY_TABS_ORDER, "|".join(order))

    def _restore_tab_order(self):
        saved = self.settings.value(SETTINGS_KEY_TABS_ORDER, "", type=str) or ""
        if not saved: return
        desired = [s for s in saved.split("|") if s in {"Folder Notes", "Library", "Annotations"}]
        if not desired: return
        for target, name in enumerate(desired):
            idx = self._tab_index_by_name(name)
            if idx != -1 and idx != target:
                self.tabs.tabBar().moveTab(idx, target)

    # ----- Toggles -----
    def _restore_toggles(self):
        ap = self.settings.value(SETTINGS_KEY_AUTOPROGRESS, None)
        self.auto_progress_cb.setChecked(bool(int(ap)) if isinstance(ap, str) and ap else bool(ap) if ap is not None else False)
        asw = self.settings.value(SETTINGS_KEY_AUTOSWITCH, None)
        self.auto_switch_cb.setChecked(bool(int(asw)) if isinstance(asw, str) and asw else bool(asw) if asw is not None else True)
        self.auto_progress_cb.stateChanged.connect(lambda _:
            self.settings.setValue(SETTINGS_KEY_AUTOPROGRESS, int(self.auto_progress_cb.isChecked())))
        self.auto_switch_cb.stateChanged.connect(lambda _:
            self.settings.setValue(SETTINGS_KEY_AUTOSWITCH, int(self.auto_switch_cb.isChecked())))

    # ----- Volume -----
    def _on_volume_changed(self, val: int):
        self.audio_output.setVolume(max(0.0, min(1.0, val / 100.0)))
        self.settings.setValue(SETTINGS_KEY_VOLUME, int(val))

    # ----- Audio Output Device -----
    def _refresh_output_devices(self):
        """Populate the output device combo box with available audio devices."""
        current_device = self.audio_output.device()
        current_description = current_device.description() if current_device else ""
        
        self.output_device_combo.clear()
        devices = QMediaDevices.audioOutputs()
        
        selected_index = 0
        for i, device in enumerate(devices):
            self.output_device_combo.addItem(device.description(), device)
            if device.description() == current_description:
                selected_index = i
        
        if not devices:
            self.output_device_combo.addItem("No devices available")
            self.output_device_combo.setEnabled(False)
        else:
            self.output_device_combo.setEnabled(True)
            self.output_device_combo.setCurrentIndex(selected_index)

    def _on_output_device_changed(self, index: int):
        """Handle output device selection change."""
        if index < 0 or not self.output_device_combo.isEnabled():
            return
            
        device = self.output_device_combo.itemData(index)
        if device is None:
            return
            
        # Store current playback state
        was_playing = self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState
        current_position = self.player.position()
        current_volume = self.audio_output.volume()
        
        # Create new audio output with selected device
        self.audio_output = QAudioOutput(device)
        self.audio_output.setVolume(current_volume)
        self.player.setAudioOutput(self.audio_output)
        
        # Resume playback if it was playing
        if was_playing and current_position > 0:
            self.player.setPosition(current_position)
            self.player.play()
            self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        elif was_playing:
            self.player.play()
            self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))

    # ----- Tree helpers -----
    def _fi(self, proxy_idx: QModelIndex):
        src = self.file_proxy.mapToSource(proxy_idx)
        return self.fs_model.fileInfo(src)  # QFileInfo

    # ----- Tree interactions -----
    def _on_tree_double_clicked(self, idx: QModelIndex):
        fi = self._fi(idx)
        if fi.isDir():
            self._save_root(Path(fi.absoluteFilePath())); return
        if f".{fi.suffix().lower()}" in AUDIO_EXTS:
            path = Path(fi.absoluteFilePath()); parent = path.parent
            if parent.resolve() != self.root_path.resolve():
                self._save_root(parent)
            if not (self.current_audio_file and self.current_audio_file.resolve() == path.resolve()):
                self._play_file(path)
            self.tabs.setCurrentIndex(self._tab_index_by_name("Annotations"))

    def _on_tree_activated(self, idx: QModelIndex):
        fi = self._fi(idx)
        if fi.isDir(): self._save_root(Path(fi.absoluteFilePath()))

    def _on_tree_selection_changed(self, *_):
        indexes = self.tree.selectionModel().selectedIndexes()
        idx = next((i for i in indexes if i.column() == 0), None)
        if not idx:
            self._stop_playback(); self.now_playing.setText("No selection"); self.current_audio_file = None
            self._update_waveform_annotations(); self._load_annotations_for_current(); self._refresh_provided_name_field(); self._refresh_best_take_field(); self._refresh_right_table(); return
        fi = self._fi(idx)
        if fi.isDir():
            # Update current practice folder when folder is selected
            folder_path = Path(fi.absoluteFilePath())
            self._set_current_practice_folder(folder_path)
            self._stop_playback(); self.now_playing.setText(f"Folder selected: {fi.fileName()}"); self.current_audio_file = None
            self._update_waveform_annotations(); self._load_annotations_for_current(); self._refresh_provided_name_field(); self._refresh_best_take_field(); self._refresh_right_table(); return
        if f".{fi.suffix().lower()}" in AUDIO_EXTS:
            path = Path(fi.absoluteFilePath())
            # Update current practice folder when audio file is selected (to its parent directory)
            self._set_current_practice_folder(path.parent)
            if not self._programmatic_selection and self.auto_switch_cb.isChecked():
                self.tabs.setCurrentIndex(self._tab_index_by_name("Annotations"))
            if self.current_audio_file and self.current_audio_file.resolve() == path.resolve():
                return
            self._play_file(path)
        else:
            self._stop_playback(); self.now_playing.setText(fi.fileName()); self.current_audio_file = None
            self._update_waveform_annotations(); self._load_annotations_for_current(); self._refresh_provided_name_field(); self._refresh_best_take_field(); self._refresh_right_table()

    def _go_up(self):
        parent = self.root_path.parent
        if parent.exists() and parent != self.root_path: self._save_root(parent)

    def _change_root_clicked(self):
        d = QFileDialog.getExistingDirectory(self, "Choose Root Band Practice Folder", str(self.root_path))
        if d: self._save_root(Path(d))

    # ----- Playback -----
    def _play_file(self, path: Path):
        if self.current_audio_file and self.current_audio_file.resolve() == path.resolve():
            return
        
        # Check if we need to reload annotations from a different directory
        prev_audio_dir = self.current_audio_file.parent if self.current_audio_file else None
        new_audio_dir = path.parent
        need_reload_annotations = (prev_audio_dir != new_audio_dir)
        
        self.player.stop(); self.player.setSource(QUrl.fromLocalFile(str(path)))
        self.player.play()
        self.play_pause_btn.setEnabled(True); self.position_slider.setEnabled(True); self.slider_sync.start()
        self.now_playing.setText(f"Playing: {path.name}")
        self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        self.current_audio_file = path; self.pending_note_start_ms = None
        self._update_captured_time_label()
        
        # Reload annotations from the audio file's directory if needed
        if need_reload_annotations:
            self._load_names()  # Reload provided names from the new directory
            self.played_durations = self._load_duration_cache()  # Reload duration cache from the new directory
            self.file_proxy.duration_cache = self.played_durations
            self._load_notes()
            self._ensure_uids()
            self._refresh_set_combo()
            self._refresh_right_table()  # Refresh library table to show files from the new directory
            self._update_folder_notes_ui()  # Update folder notes UI for the new directory
        
        self._load_annotations_for_current()
        self._refresh_provided_name_field()
        self._refresh_best_take_field()
        try: self.waveform.set_audio_file(path)
        except Exception: self.waveform.clear()
        self._update_waveform_annotations()
        
        # Ensure the file is highlighted in the tree view (important for auto-progression)
        self._highlight_file_in_tree(path)

    def _highlight_file_in_tree(self, path: Path):
        """Highlight the specified file in the tree view, ensuring it's visible and selected.
        
        This is particularly important for auto-progression so users can see which file
        is currently playing when songs advance automatically.
        """
        try:
            # Get the source index for the file from the filesystem model
            src_idx = self.fs_model.index(str(path))
            if not src_idx.isValid():
                # File not found in filesystem model, this could happen if model is not updated
                print(f"Warning: Could not find {path} in filesystem model")
                return
                
            # Map from source model to proxy model
            proxy_idx = self.file_proxy.mapFromSource(src_idx)
            if not proxy_idx.isValid():
                print(f"Warning: Could not map {path} to proxy model")
                return
            
            # Set the programmatic selection flag to prevent triggering selection change events
            self._programmatic_selection = True
            
            try:
                # Ensure the parent directory is expanded so the file is visible
                parent_idx = proxy_idx.parent()
                if parent_idx.isValid():
                    self.tree.setExpanded(parent_idx, True)
                
                # Select and highlight the file in the tree view
                self.tree.setCurrentIndex(proxy_idx)
                
                # Ensure the selected item is visible (scroll to it if necessary)
                self.tree.scrollTo(proxy_idx, QAbstractItemView.ScrollHint.EnsureVisible)
                
            finally:
                # Reset the programmatic selection flag after a short delay
                QTimer.singleShot(0, lambda: setattr(self, "_programmatic_selection", False))
                
        except Exception as e:
            # Log the error but don't crash - tree highlighting is not critical for playback
            print(f"Warning: Failed to highlight {path} in tree view: {e}")

    def _stop_playback(self):
        if self.player.playbackState() != QMediaPlayer.PlaybackState.StoppedState: self.player.stop()
        self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_pause_btn.setEnabled(False); self.position_slider.setEnabled(False); self.slider_sync.stop()
        self.position_slider.setValue(0); self.time_label.setText("0:00 / 0:00"); self.pending_note_start_ms = None
        self._update_captured_time_label()
        self.waveform.set_selected_uid(None, None)
        self._update_waveform_annotations()
        self._refresh_provided_name_field()
        self._refresh_best_take_field()

    def _toggle_play_pause(self):
        st = self.player.playbackState()
        if st == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause(); self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        else:
            self.player.play(); self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))

    def _play_next_file(self):
        """Auto-advance to the next audio file in the current directory.
        
        This method is called when auto-progression is enabled and a song finishes playing.
        It will find the next file alphabetically and play it, ensuring the file is highlighted
        in the tree view so users can see what is currently selected.
        """
        if not self.current_audio_file: 
            return
            
        files = [p for p in self._list_audio_in_current_dir()]
        if not files: 
            return
            
        try:
            # Sort files alphabetically for consistent ordering
            files.sort(key=lambda p: p.name.lower())
            cur = self.current_audio_file.resolve()
            
            # Find the current file and advance to the next one
            for i, p in enumerate(files):
                if p.resolve() == cur:
                    if i + 1 < len(files):
                        next_file = files[i + 1]
                        print(f"Auto-progressing from '{cur.name}' to '{next_file.name}'")
                        self._play_file(next_file)
                    else:
                        print(f"Auto-progression: reached end of playlist (last file: '{cur.name}')")
                    break
        except Exception as e:
            print(f"Error during auto-progression: {e}")
            # Don't let auto-progression errors crash the application

    # ----- Slider/time -----
    _user_is_scrubbing = False
    def _on_duration_changed(self, dur: int):
        self.position_slider.setRange(0, max(0, dur)); self._sync_slider()
        if self.current_audio_file and dur > 0:
            fname = self.current_audio_file.name
            if int(self.played_durations.get(fname, 0)) <= 0:
                self.played_durations[fname] = int(dur); self._save_duration_cache()
                src_idx = self.fs_model.index(str(self.current_audio_file))
                if src_idx.isValid():
                    pi = self.file_proxy.mapFromSource(src_idx); col = 1
                    top = self.file_proxy.index(pi.row(), col, pi.parent())
                    self.file_proxy.dataChanged.emit(top, top)

    def _sync_slider(self):
        if self._user_is_scrubbing: return
        pos = self.player.position(); dur = max(1, self.player.duration())
        self.position_slider.blockSignals(True); self.position_slider.setValue(pos); self.position_slider.blockSignals(False)
        self.time_label.setText(f"{human_time_ms(pos)} / {human_time_ms(dur)}")

    def _user_scrubbing(self, on: bool): self._user_is_scrubbing = on

    def _on_slider_moved(self, value: int):
        self.player.setPosition(value)
        if self.note_input.text().strip():
            self.pending_note_start_ms = int(value); self._update_captured_time_label()

    def _on_slider_clicked_value(self, value: int):
        if not self.position_slider.isEnabled(): return
        was = self._user_is_scrubbing; self._user_is_scrubbing = True
        try:
            self.player.setPosition(value); self.position_slider.setValue(value); self._sync_slider()
            if self.note_input.text().strip():
                self.pending_note_start_ms = int(value); self._update_captured_time_label()
        finally:
            self._user_is_scrubbing = was

    # ----- Library table helpers -----
    def _list_audio_in_root(self) -> List[Path]:
        if not self.root_path.exists(): return []
        return [p for p in sorted(self.root_path.iterdir()) if p.is_file() and p.suffix.lower() in AUDIO_EXTS]

    def _list_wav_in_root(self) -> List[Path]:
        if not self.root_path.exists(): return []
        return [p for p in sorted(self.root_path.iterdir()) if p.is_file() and p.suffix.lower() in {".wav",".wave"}]

    def _list_audio_in_current_dir(self) -> List[Path]:
        """List audio files in the directory containing the currently selected song, or current practice folder if no song selected."""
        target_dir = self.current_audio_file.parent if self.current_audio_file else self.current_practice_folder
        if not target_dir.exists(): return []
        return [p for p in sorted(target_dir.iterdir()) if p.is_file() and p.suffix.lower() in AUDIO_EXTS]

    def _refresh_right_table(self):
        files = self._list_audio_in_current_dir()
        self.table.blockSignals(True); self.table.setRowCount(len(files))
        for row, p in enumerate(files):
            item_file = QTableWidgetItem(p.name); item_file.setFlags(item_file.flags() ^ Qt.ItemFlag.ItemIsEditable)
            
            # Best Take checkbox
            item_best_take = QTableWidgetItem()
            item_best_take.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsUserCheckable)
            is_best_take = self.file_best_takes.get(p.name, False)
            item_best_take.setCheckState(Qt.CheckState.Checked if is_best_take else Qt.CheckState.Unchecked)
            
            item_name = QTableWidgetItem(self.provided_names.get(p.name, "")); item_name.setToolTip("Double-click to edit your Provided Name")
            
            # Set green background for best takes
            if is_best_take:
                green_color = QColor(200, 255, 200)  # Light green
                item_file.setBackground(green_color)
                item_best_take.setBackground(green_color)
                item_name.setBackground(green_color)
            
            self.table.setItem(row, 0, item_file)
            self.table.setItem(row, 1, item_best_take)
            self.table.setItem(row, 2, item_name)
        self.table.blockSignals(False)

    def _on_table_item_changed(self, item: QTableWidgetItem):
        row = item.row(); file_item = self.table.item(row, 0)
        if not file_item: return
        filename = file_item.text()
        
        if item.column() == 1:  # Best Take checkbox
            is_checked = item.checkState() == Qt.CheckState.Checked
            self.file_best_takes[filename] = is_checked
            self._save_notes()  # Save the annotation data including best_take
            
            # Update background colors for the entire row
            green_color = QColor(200, 255, 200) if is_checked else QColor(255, 255, 255)
            for col in range(self.table.columnCount()):
                cell_item = self.table.item(row, col)
                if cell_item:
                    cell_item.setBackground(green_color)
                    
        elif item.column() == 2:  # Provided Name (editable)
            self.provided_names[filename] = sanitize(item.text())
            self._save_names()

    def _stop_if_no_file_selected(self):
        indexes = self.tree.selectionModel().selectedIndexes()
        idx = next((i for i in indexes if i.column() == 0), None)
        if not idx: self._stop_playback()

    # ----- Annotation table config (dynamic) -----
    def _on_library_cell_clicked(self, row: int, column: int):
        # Play the clicked filename from the Library tab without switching tabs.
        try:
            # Only the File column (0)
            if column != 0:
                return
            item = self.table.item(row, 0)
            if not item:
                return
            fname = item.text().strip()
            if not fname:
                return
            from pathlib import Path as _P
            path = (self.current_practice_folder / fname) if hasattr(self, 'current_practice_folder') else _P(fname)
            if not path.exists():
                try:
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "File Missing", f"Couldn't find: {path}")
                except Exception:
                    pass
                return
            # Start playback; do not switch tabs
            if hasattr(self, '_play_file'):
                self._play_file(path)
        except Exception as _e:
            # Be defensive; do not break UI if something is slightly different locally
            print("Issue#1 handler error:", _e)

    def _configure_annotation_table(self):
        self.annotation_table.clear()
        if self.show_all_sets:
            self.annotation_table.setColumnCount(4)
            self.annotation_table.setHorizontalHeaderLabels(["Set", "!", "Time", "Note"])
            self._c_set, self._c_imp, self._c_time, self._c_note = 0, 1, 2, 3
            ah = self.annotation_table.horizontalHeader()
            ah.setSectionResizeMode(self._c_set, QHeaderView.ResizeMode.ResizeToContents)
            ah.setSectionResizeMode(self._c_imp, QHeaderView.ResizeMode.ResizeToContents)
            ah.setSectionResizeMode(self._c_time, QHeaderView.ResizeMode.ResizeToContents)
            ah.setSectionResizeMode(self._c_note, QHeaderView.ResizeMode.Stretch)
        else:
            self.annotation_table.setColumnCount(3)
            self.annotation_table.setHorizontalHeaderLabels(["!", "Time", "Note"])
            self._c_set, self._c_imp, self._c_time, self._c_note = -1, 0, 1, 2
            ah = self.annotation_table.horizontalHeader()
            ah.setSectionResizeMode(self._c_imp, QHeaderView.ResizeMode.ResizeToContents)
            ah.setSectionResizeMode(self._c_time, QHeaderView.ResizeMode.ResizeToContents)
            ah.setSectionResizeMode(self._c_note, QHeaderView.ResizeMode.Stretch)
        self.annotation_table.verticalHeader().setVisible(False)
        self.annotation_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.annotation_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.annotation_table.setEditTriggers(QAbstractItemView.EditTrigger.SelectedClicked | QAbstractItemView.EditTrigger.EditKeyPressed)
        try: self.annotation_table.itemDoubleClicked.disconnect()
        except Exception: pass
        self.annotation_table.itemDoubleClicked.connect(self._on_annotation_double_clicked)
        try: self.annotation_table.itemChanged.disconnect()
        except Exception: pass
        self.annotation_table.itemChanged.connect(self._on_annotation_item_changed)
        try: self.annotation_table.selectionModel().selectionChanged.disconnect()
        except Exception: pass
        self.annotation_table.selectionModel().selectionChanged.connect(self._on_annotation_selection_changed)
        
        # Enable context menu and key handling for annotation table
        self.annotation_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.annotation_table.customContextMenuRequested.connect(self._on_annotation_context_menu)
        self.annotation_table.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    # ----- Helpers for cross-set editing -----
    def _get_set_and_list(self, set_id: str, fname: str):
        if set_id == self.current_set_id:
            return self._get_current_set(), self.notes_by_file.setdefault(fname, [])
        for s in self.annotation_sets:
            if s.get("id") == set_id:
                meta = s.setdefault("files", {}).setdefault(fname, {"general":"","notes":[]})
                return s, meta["notes"]
        return None, None

    def _find_entry_in_list(self, lst: List[Dict], uid: int) -> Optional[Dict]:
        for e in lst:
            if int(e.get("uid",-1)) == int(uid): return e
        return None

    # ----- Annotations (current file; merged view optional) -----
    def _load_annotations_for_current(self):
        self.general_edit.blockSignals(True); self.general_edit.clear()
        self.annotation_table.blockSignals(True); self.annotation_table.setRowCount(0)

        if not self.current_audio_file:
            self.annotation_table.blockSignals(False); self.general_edit.blockSignals(False)
            self._refresh_important_table(); return

        fname = self.current_audio_file.name
        self.general_edit.setPlainText(self.file_general.get(fname, ""))

        rows: List[Tuple[str,str,Dict]] = []  # (set_id, set_name, entry)
        if self.show_all_sets:
            for s in self.annotation_sets:
                if not bool(s.get("visible", True)): continue
                set_id = s.get("id")
                set_name = s.get("name","Set")
                meta = s.get("files", {}).get(fname)
                if not meta: continue
                for e in (meta.get("notes") or []):
                    rows.append((set_id, set_name, dict(e)))
        else:
            aset = self._get_current_set()
            if aset:
                set_id = aset.get("id")
                set_name = aset.get("name","Set")
                for e in (aset.get("files", {}).get(fname, {}).get("notes") or []):
                    rows.append((set_id, set_name, dict(e)))

        rows.sort(key=lambda r: int(r[2].get("ms", 0)))
        for set_id, set_name, entry in rows:
            editable = True if self.show_all_sets else (set_id == self.current_set_id)
            # Issue #4 filter
            if self.annotation_filter == 'points' and entry.get('end_ms') is not None: continue
            if self.annotation_filter == 'clips' and entry.get('end_ms') is None: continue
            self._append_annotation_row(entry, set_id=set_id, set_name=set_name, editable=editable)

        self.annotation_table.blockSignals(False); self.general_edit.blockSignals(False)
        self._refresh_important_table()
        self._update_waveform_annotations()
        self._refresh_provided_name_field()
        self._refresh_best_take_field()

    def _append_annotation_row(self, entry: Dict, *, set_id: Optional[str]=None, set_name: Optional[str]=None, editable: bool=True):
        ms = int(entry.get("ms", 0))
        text = str(entry.get("text", ""))
        important = bool(entry.get("important", False))
        uid = int(entry.get("uid", 0))

        r = self.annotation_table.rowCount(); self.annotation_table.insertRow(r)

        if self.show_all_sets:
            s_item = QTableWidgetItem(set_name or "")
            s_item.setData(Qt.ItemDataRole.UserRole, str(set_id or ""))
            s_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.annotation_table.setItem(r, self._c_set, s_item)

        imp = QTableWidgetItem()
        flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsUserCheckable
        if not editable: flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        imp.setFlags(flags)
        imp.setCheckState(Qt.CheckState.Checked if important else Qt.CheckState.Unchecked)
        imp.setData(Qt.ItemDataRole.UserRole + 1, int(uid))
        imp.setData(Qt.ItemDataRole.UserRole + 2, str(set_id or self.current_set_id or ""))
        self.annotation_table.setItem(r, self._c_imp, imp)

        t = QTableWidgetItem(human_time_ms(ms))
        t.setData(Qt.ItemDataRole.UserRole, int(ms))
        t.setData(Qt.ItemDataRole.UserRole + 1, int(uid))
        t.setData(Qt.ItemDataRole.UserRole + 2, str(set_id or self.current_set_id or ""))
        t.setFlags((t.flags() | Qt.ItemFlag.ItemIsEditable) if editable else (Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled))
        self.annotation_table.setItem(r, self._c_time, t)

        n = QTableWidgetItem(text)
        n.setData(Qt.ItemDataRole.UserRole + 1, int(uid))
        n.setData(Qt.ItemDataRole.UserRole + 2, str(set_id or self.current_set_id or ""))
        n.setFlags((n.flags() | Qt.ItemFlag.ItemIsEditable) if editable else (Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled))
        self.annotation_table.setItem(r, self._c_note, n)

    
        # Issue #4: display clip ranges as start - end and lock time cell editing for clips
        try:
            end_ms = entry.get("end_ms")
            if end_ms is not None:
                # time item is at self._c_time
                titem = self.annotation_table.item(r, self._c_time)
                if titem:
                    titem.setText(f"{human_time_ms(int(ms))} - {human_time_ms(int(end_ms))}")
                    titem.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        except Exception:
            pass

    def _current_file_list(self) -> List[Dict]:
        if not self.current_audio_file: return []
        return self.notes_by_file.setdefault(self.current_audio_file.name, [])

    def _find_entry_by_uid(self, uid: int) -> Optional[Dict]:
        for e in self._current_file_list():
            if int(e.get("uid", -1)) == uid: return e
        return None

    def _row_for_uid(self, uid: int, set_id: Optional[str]=None) -> Optional[int]:
        for r in range(self.annotation_table.rowCount()):
            titem = self.annotation_table.item(r, self._c_time)
            if not titem: continue
            row_uid = int(titem.data(Qt.ItemDataRole.UserRole + 1) or -1)
            row_sid = str(titem.data(Qt.ItemDataRole.UserRole + 2) or "")
            if row_uid == uid and ((set_id is None) or (row_sid == str(set_id))):
                return r
        return None

    def _select_row_by_uid(self, uid: int, set_id: Optional[str]=None):
        r = self._row_for_uid(uid, set_id=set_id)
        if r is not None:
            self.annotation_table.selectRow(r)
            self.annotation_table.scrollToItem(self.annotation_table.item(r, self._c_time))

    def _resort_and_rebuild_table_preserving_selection(self, keep_pair: Optional[Tuple[str,int]] = None):
        if not self.current_audio_file: return
        fname = self.current_audio_file.name
        lst = self.notes_by_file.setdefault(fname, [])
        lst.sort(key=lambda e: int(e.get("ms", 0)))
        self._sync_fields_into_current_set()  # Sync notes_by_file to annotation set before reload
        self._load_annotations_for_current()
        if keep_pair is not None:
            set_id, uid = keep_pair
            self._select_row_by_uid(uid, set_id=set_id)
        self._update_waveform_annotations()
        if keep_pair is not None:
            set_id, uid = keep_pair
            self.waveform.set_selected_uid(set_id, uid)

    def _on_note_text_edited(self, _txt: str):
        if self.pending_note_start_ms is None:
            self.pending_note_start_ms = int(self.player.position()); self._update_captured_time_label()

    def _on_note_text_changed_clear_capture(self, txt: str):
        if not txt:
            self.pending_note_start_ms = None; self._update_captured_time_label()

    def _update_captured_time_label(self):
        self.captured_time_label.setText("" if self.pending_note_start_ms is None else human_time_ms(int(self.pending_note_start_ms)))

    def _on_note_return_pressed(self):
        txt = self.note_input.text().strip()
        if not txt or not self.current_audio_file:
            self.pending_note_start_ms = None; self.note_input.clear(); self._update_captured_time_label(); return
        ms = self.pending_note_start_ms if self.pending_note_start_ms is not None else int(self.player.position())
        self.pending_note_start_ms = None; self._update_captured_time_label()
        fname = self.current_audio_file.name
        uid = self._uid_counter; self._uid_counter += 1
        entry = ({'uid': uid, 'ms': int(ms), 'text': txt, 'important': False} if self.clip_sel_start_ms is None or self.clip_sel_end_ms is None else {'uid': uid, 'ms': int(self.clip_sel_start_ms), 'end_ms': int(self.clip_sel_end_ms), 'text': txt, 'important': False})
        self.notes_by_file.setdefault(fname, []).append(entry)
        self._push_undo({"type":"add","set":self.current_set_id,"file":fname,"entry":entry})
        self._resort_and_rebuild_table_preserving_selection(keep_pair=(self.current_set_id, uid))
        self.note_input.clear()
        self._on_clip_cancel_clicked()
        self._schedule_save_notes()

    def _on_annotation_double_clicked(self, item: QTableWidgetItem):
        row = item.row(); titem = self.annotation_table.item(row, self._c_time)
        if not titem: return
        ms = parse_time_to_ms(titem.text())
        if ms is None: ms = int(titem.data(Qt.ItemDataRole.UserRole) or 0)
        uid = int(titem.data(Qt.ItemDataRole.UserRole + 1) or -1)
        set_id = str(titem.data(Qt.ItemDataRole.UserRole + 2) or self.current_set_id or "")
        if set_id and set_id != self.current_set_id:
            for i in range(self.set_combo.count()):
                if str(self.set_combo.itemData(i)) == str(set_id):
                    if self.set_combo.currentIndex() != i: self.set_combo.setCurrentIndex(i)
                    break
        self.player.setPosition(int(ms))
        self.waveform.set_selected_uid(set_id, uid)
        self.player.play()
        self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))

    def _on_annotation_item_changed(self, item: QTableWidgetItem):
        if self._suspend_ann_change: return
        if not self.current_audio_file: return
        uid = int(item.data(Qt.ItemDataRole.UserRole + 1) or -1)
        set_id = str(item.data(Qt.ItemDataRole.UserRole + 2) or self.current_set_id or "")
        if uid < 0 or not set_id: return
        fname = self.current_audio_file.name
        aset, lst = self._get_set_and_list(set_id, fname)
        if not lst: return
        entry = self._find_entry_in_list(lst, uid)
        if not entry: return

        if item.column() == self._c_time:
            new_ms = parse_time_to_ms(item.text())
            if new_ms is None:
                self._suspend_ann_change = True
                try:
                    item.setText(human_time_ms(int(entry.get("ms", 0))))
                finally:
                    self._suspend_ann_change = False
                return
            old_ms = int(entry.get("ms", 0))
            if int(new_ms) != old_ms:
                self._push_undo({"type":"edit","set":set_id,"file":fname,"uid":uid,"field":"ms","before":old_ms,"after":int(new_ms)})
            entry["ms"] = int(new_ms)
            item.setData(Qt.ItemDataRole.UserRole, int(new_ms))
            lst.sort(key=lambda e: int(e.get("ms", 0)))
            # Sync if we modified current set's notes_by_file
            if set_id == self.current_set_id:
                self._sync_fields_into_current_set()
            self._load_annotations_for_current()
            self._select_row_by_uid(uid, set_id=set_id)
            self._schedule_save_notes(); self._refresh_important_table()
            return

        if item.column() == self._c_note:
            old_text = entry.get("text","")
            new_text = item.text()
            if new_text != old_text:
                self._push_undo({"type":"edit","set":set_id,"file":fname,"uid":uid,"field":"text","before":old_text,"after":new_text})
            entry["text"] = new_text
            self._schedule_save_notes(); self._refresh_important_table(); return

        if item.column() == self._c_imp:
            new_imp = (item.checkState() == Qt.CheckState.Checked)
            old_imp = bool(entry.get("important", False))
            if new_imp != old_imp:
                self._push_undo({"type":"edit","set":set_id,"file":fname,"uid":uid,"field":"important","before":old_imp,"after":new_imp})
            entry["important"] = new_imp
            self._schedule_save_notes(); self._refresh_important_table(); return

    def _delete_selected_annotations(self):
        if not self.current_audio_file: return
        fname = self.current_audio_file.name
        sel_rows = sorted({idx.row() for idx in self.annotation_table.selectionModel().selectedIndexes()}, reverse=True)
        if not sel_rows: return
        to_delete: List[Tuple[str,int]] = []  # (set_id, uid)
        for r in sel_rows:
            titem = self.annotation_table.item(r, self._c_time)
            if not titem: continue
            uid = int(titem.data(Qt.ItemDataRole.UserRole + 1) or -1)
            set_id = str(titem.data(Qt.ItemDataRole.UserRole + 2) or "")
            if uid >= 0 and set_id: to_delete.append((set_id, uid))
        if not to_delete: return

        for set_id, uid in to_delete:
            aset, lst = self._get_set_and_list(set_id, fname)
            if not lst: continue
            entry = self._find_entry_in_list(lst, uid)
            if not entry: continue
            self._push_undo({"type":"delete","set":set_id,"file":fname,"entries":[dict(entry)]})
            lst[:] = [e for e in lst if int(e.get("uid",-1)) != uid]

        # Sync current set changes before reload
        self._sync_fields_into_current_set()
        self._load_annotations_for_current()
        self._schedule_save_notes(); self._refresh_important_table()
        self.waveform.set_selected_uid(None, None)

    def _selected_row_identity(self) -> Optional[Tuple[str,int]]:
        sel = self.annotation_table.selectionModel().selectedRows()
        if not sel: return None
        row = sel[0].row()
        titem = self.annotation_table.item(row, self._c_time)
        if not titem: return None
        uid = int(titem.data(Qt.ItemDataRole.UserRole + 1) or -1)
        set_id = str(titem.data(Qt.ItemDataRole.UserRole + 2) or self.current_set_id or "")
        return (set_id, uid) if uid >= 0 and set_id else None

    def _on_annotation_selection_changed(self, *_):
        ident = self._selected_row_identity()
        if not ident:
            self.waveform.set_selected_uid(None, None)
            return
        set_id, uid = ident
        self.waveform.set_selected_uid(set_id, uid)
        
        # Issue #23: If selected annotation is a clip, highlight it in waveform and populate textboxes
        if self.current_audio_file:
            fname = self.current_audio_file.name
            aset, lst = self._get_set_and_list(set_id, fname)
            if lst:
                entry = self._find_entry_in_list(lst, uid)
                if entry and entry.get("end_ms") is not None:
                    # This is a clip annotation with start and end times
                    start_ms = entry.get("ms")
                    end_ms = entry.get("end_ms")
                    self.clip_sel_start_ms = start_ms
                    self.clip_sel_end_ms = end_ms
                    self._update_clip_edits_from_selection()
                else:
                    # This is a point annotation - clear any existing clip selection
                    if self.clip_sel_start_ms is not None or self.clip_sel_end_ms is not None:
                        self.clip_sel_start_ms = None
                        self.clip_sel_end_ms = None
                        self._update_clip_edits_from_selection()

    def _on_annotation_context_menu(self, position: QPoint):
        """Handle right-click context menu on annotation table."""
        if not self.annotation_table.itemAt(position):
            return
        
        # Check if there are selected rows
        selected_rows = self.annotation_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        menu = QMenu(self)
        delete_action = menu.addAction("Delete Selected")
        delete_action.triggered.connect(self._delete_selected_with_confirmation)
        
        # Show menu at the requested position
        menu.exec(self.annotation_table.mapToGlobal(position))
    
    def _delete_selected_with_confirmation(self):
        """Delete selected annotations after confirmation."""
        if not self.current_audio_file:
            return
        
        selected_rows = self.annotation_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        # Create confirmation message
        count = len(selected_rows)
        if count == 1:
            message = "Delete this annotation? This action cannot be undone."
        else:
            message = f"Delete {count} selected annotations? This action cannot be undone."
        
        reply = QMessageBox.question(
            self, "Delete Annotations",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No  # Default to No for safety
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._delete_selected_annotations()

    def keyPressEvent(self, event):
        """Handle key press events for the main window."""
        if event.key() == Qt.Key.Key_Delete:
            # Check if annotation table has focus and selected items
            if (self.annotation_table.hasFocus() and 
                self.annotation_table.selectionModel().selectedRows()):
                self._delete_selected_with_confirmation()
                event.accept()
                return
        
        # Call parent implementation for other keys
        super().keyPressEvent(event)

    # Waveform interactions
    def _on_waveform_seek_requested(self, ms: int):
        if self.note_input.text().strip():
            self.pending_note_start_ms = int(ms); self._update_captured_time_label()

    def _on_waveform_annotation_clicked_multi(self, set_id: str, uid: int):
        for i in range(self.set_combo.count()):
            if str(self.set_combo.itemData(i)) == str(set_id):
                if self.set_combo.currentIndex() != i: self.set_combo.setCurrentIndex(i)
                break
        self._select_row_by_uid(uid, set_id=set_id)
        self.waveform.set_selected_uid(set_id, uid)

    def _on_marker_moved_multi(self, set_id: str, uid: int, new_ms: int):
        fname = self.current_audio_file.name if self.current_audio_file else ""
        aset, lst = self._get_set_and_list(set_id, fname)
        if not lst: return
        entry = self._find_entry_in_list(lst, uid)
        if not entry: return
        entry["ms"] = int(new_ms)
        row = self._row_for_uid(uid, set_id=set_id)
        if row is not None:
            titem = self.annotation_table.item(row, self._c_time)
            if titem:
                self._suspend_ann_change = True
                try:
                    titem.setText(human_time_ms(new_ms))
                    titem.setData(Qt.ItemDataRole.UserRole, int(new_ms))
                finally:
                    self._suspend_ann_change = False

    def _on_marker_released_multi(self, set_id: str, uid: int, new_ms: int):
        fname = self.current_audio_file.name if self.current_audio_file else ""
        aset, lst = self._get_set_and_list(set_id, fname)
        if not lst: return
        entry = self._find_entry_in_list(lst, uid)
        if not entry: return
        old_ms = int(entry.get("ms", 0))
        if int(new_ms) != old_ms:
            self._push_undo({"type":"edit","set":set_id,"file":fname,"uid":uid,"field":"ms","before":old_ms,"after":int(new_ms)})
        entry["ms"] = int(new_ms)
        lst.sort(key=lambda e: int(e.get("ms",0)))
        self._load_annotations_for_current()
        self._select_row_by_uid(uid, set_id=set_id)
        self._schedule_save_notes(); self._refresh_important_table()
        self._update_waveform_annotations()

    # Provided name on Annotations tab
    def _on_provided_name_edited(self):
        if not self.current_audio_file:
            return
        new_name = sanitize(self.provided_name_edit.text())
        fname = self.current_audio_file.name
        if self.provided_names.get(fname, "") != new_name:
            self.provided_names[fname] = new_name
            self._save_names()
            self._update_library_provided_name_cell(fname, new_name)

    def _update_library_provided_name_cell(self, file_name: str, new_value: str):
        try:
            self.table.blockSignals(True)
            for row in range(self.table.rowCount()):
                it = self.table.item(row, 0)
                if it and it.text() == file_name:
                    tgt = self.table.item(row, 1)
                    if tgt is None:
                        tgt = QTableWidgetItem(new_value)
                        self.table.setItem(row, 1, tgt)
                    else:
                        tgt.setText(new_value)
                    break
        finally:
            self.table.blockSignals(False)

    # Best take checkbox on Annotations tab
    def _on_best_take_changed(self, state):
        if not self.current_audio_file:
            return
        fname = self.current_audio_file.name
        is_checked = state == Qt.CheckState.Checked.value
        self.file_best_takes[fname] = is_checked
        self._save_notes()  # Save the annotation data including best_take
        self._refresh_right_table()  # Update the library table to show the green highlighting

    def _refresh_provided_name_field(self):
        if not self.current_audio_file:
            self.provided_name_edit.setText("")
            self.provided_name_edit.setEnabled(False)
            return
        fname = self.current_audio_file.name
        self.provided_name_edit.setEnabled(True)
        self.provided_name_edit.setText(self.provided_names.get(fname, ""))

    def _refresh_best_take_field(self):
        if not self.current_audio_file:
            self.best_take_cb.setChecked(False)
            self.best_take_cb.setEnabled(False)
            return
        fname = self.current_audio_file.name
        self.best_take_cb.setEnabled(True)
        self.best_take_cb.blockSignals(True)  # Prevent triggering the change handler
        self.best_take_cb.setChecked(self.file_best_takes.get(fname, False))
        self.best_take_cb.blockSignals(False)

    # Autosave handlers
    def _on_general_changed(self):
        if not self.current_audio_file: return
        fname = self.current_audio_file.name
        self.file_general[fname] = self.general_edit.toPlainText()
        self._schedule_save_notes()

    def _on_folder_notes_changed(self):
        # Only save changes when not in show-all mode (when it's editable)
        if not self.show_all_folder_notes:
            aset = self._get_current_set()
            if aset:
                aset["folder_notes"] = self.folder_notes_edit.toPlainText()
            self._schedule_save_notes()

    def _schedule_save_notes(self):
        self._general_save_timer.start(600); self._folder_save_timer.start(600)

    def _update_folder_notes_ui(self):
        self.folder_notes_edit.blockSignals(True)
        aset = self._get_current_set()
        set_name = aset.get("name", "Unknown Set") if aset else "No Set"
        # Show the current audio file's directory name, or current practice folder if no file selected
        current_dir = self._get_audio_file_dir()
        self.folder_label.setText(f"Notes for current folder ({set_name}): {current_dir.name}")
        
        if self.show_all_folder_notes:
            # Show all folder notes from visible sets
            self.folder_label.setText(f"Notes for current folder: {current_dir.name} (All visible sets)")
            
            # Collect folder notes from all visible sets
            notes_by_set = []
            for s in self.annotation_sets:
                if not bool(s.get("visible", True)): 
                    continue
                folder_notes = (s.get("folder_notes", "") or "").strip()
                if folder_notes:
                    set_name = s.get("name", "Unknown Set")
                    notes_by_set.append((set_name, folder_notes))
            
            # Format the combined notes
            if notes_by_set:
                combined_text = ""
                for i, (set_name, notes) in enumerate(notes_by_set):
                    if i > 0:
                        combined_text += "\n\n"
                    combined_text += f"=== {set_name} ===\n{notes}"
                self.folder_notes_edit.setPlainText(combined_text)
            else:
                self.folder_notes_edit.setPlainText("(No folder notes in visible sets)")
            
            # Make read-only when showing all sets
            self.folder_notes_edit.setReadOnly(True)
            self.folder_notes_edit.setStyleSheet("QPlainTextEdit { background-color: #f8f8f8; }")
            
        else:
            # Show only current set folder notes (original behavior)
            aset = self._get_current_set()
            set_name = aset.get("name", "Unknown Set") if aset else "No Set"
            self.folder_label.setText(f"Notes for current folder ({set_name}): {current_dir.name}")
            folder_notes = aset.get("folder_notes", "") if aset else ""
            self.folder_notes_edit.setPlainText(folder_notes or "")
            
            # Make editable when showing single set
            self.folder_notes_edit.setReadOnly(False)
            self.folder_notes_edit.setStyleSheet("")
        
        self.folder_notes_edit.blockSignals(False)

    # ----- Waveform annotations payload -----
    def _update_waveform_annotations(self):
        payload = {}
        if not self.current_audio_file:
            self.waveform.set_annotations_multi(payload); return
        fname = self.current_audio_file.name
        for s in self.annotation_sets:
            pairs = []
            meta = s.get("files", {}).get(fname)
            if meta:
                pairs = [(int(n.get("uid",0)), int(n.get("ms",0))) for n in (meta.get("notes") or [])]
            payload[s["id"]] = {"color": s.get("color","#00cc66"), "visible": bool(s.get("visible",True)), "pairs": pairs}
        self.waveform.set_annotations_multi(payload)
    # ----- Issue #4: event filter for waveform Shift+click selection -----
    def eventFilter(self, obj, event):
        try:
            from PyQt6.QtCore import QEvent, Qt
            if obj is self.waveform:
                if event.type() == QEvent.Type.MouseButtonPress:
                    if getattr(event, "button", None) and event.button() == Qt.MouseButton.LeftButton:
                        mods = getattr(event, "modifiers", lambda: Qt.KeyboardModifier.NoModifier)()
                        if mods & Qt.KeyboardModifier.ShiftModifier:
                            x = int(getattr(event, "position", lambda: None)().x()) if hasattr(event, "position") else int(event.pos().x())
                            # map x to ms using player duration
                            W = max(1, self.waveform.width())
                            dur = int(self.player.duration())
                            ms = max(0, min(dur, int((x / W) * dur)))
                            if self.clip_sel_start_ms is None or (self.clip_sel_start_ms is not None and self.clip_sel_end_ms is not None):
                                self.clip_sel_start_ms = ms; self.clip_sel_end_ms = None
                            else:
                                self.clip_sel_end_ms = ms
                                if self.clip_sel_end_ms < self.clip_sel_start_ms:
                                    self.clip_sel_start_ms, self.clip_sel_end_ms = self.clip_sel_end_ms, self.clip_sel_start_ms
                            self._update_clip_edits_from_selection()
                            return True
            return super().eventFilter(obj, event)
        except Exception:
            return super().eventFilter(obj, event)

    def _update_clip_edits_from_selection(self):
        s = self.clip_sel_start_ms; e = self.clip_sel_end_ms
        self.clip_start_edit.blockSignals(True); self.clip_end_edit.blockSignals(True)
        self.clip_start_edit.setText(human_time_ms(int(s)) if s is not None else "")
        self.clip_end_edit.setText(human_time_ms(int(e)) if e is not None else "")
        self.clip_start_edit.blockSignals(False); self.clip_end_edit.blockSignals(False)
        # Update waveform visual selection
        self.waveform.set_clip_selection(s, e)

    def _on_clip_time_edits_changed(self):
        s = parse_time_to_ms(self.clip_start_edit.text() or "")
        e = parse_time_to_ms(self.clip_end_edit.text() or "")
        self.clip_sel_start_ms = s
        self.clip_sel_end_ms = e
        # Normalize order
        if (s is not None) and (e is not None) and e < s:
            self.clip_sel_start_ms, self.clip_sel_end_ms = e, s
        # Update waveform visual selection
        self.waveform.set_clip_selection(self.clip_sel_start_ms, self.clip_sel_end_ms)

    def _on_clip_play_clicked(self):
        if not self.current_audio_file: return
        if self.clip_sel_start_ms is None or self.clip_sel_end_ms is None: return
        if int(self.clip_sel_start_ms) >= int(self.clip_sel_end_ms): return
        self._clip_play_end_ms = int(self.clip_sel_end_ms)
        self._clip_playing = True
        self.player.setPosition(int(self.clip_sel_start_ms)); self.player.play()
        self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))

    def _on_player_pos_for_clip(self, pos_ms: int):
        if self._clip_playing and self._clip_play_end_ms is not None:
            if int(pos_ms) >= int(self._clip_play_end_ms):
                self.player.pause()
                self._clip_playing = False
                self._clip_play_end_ms = None
                self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

    def _on_clip_cancel_clicked(self):
        self.clip_sel_start_ms = None; self.clip_sel_end_ms = None
        self._clip_play_end_ms = None; self._clip_playing = False
        self._update_clip_edits_from_selection()

    def _on_clip_save_clicked(self):
        if not self.current_audio_file: return
        if self.clip_sel_start_ms is None or self.clip_sel_end_ms is None: return
        if int(self.clip_sel_start_ms) >= int(self.clip_sel_end_ms): return
        txt = self.note_input.text().strip()
        if not txt:
            QMessageBox.information(self, "Add Text", "Type an annotation in the Text box before saving the clip.")
            return
        fname = self.current_audio_file.name
        uid = self._uid_counter; self._uid_counter += 1
        entry = {"uid": int(uid), "ms": int(self.clip_sel_start_ms), "end_ms": int(self.clip_sel_end_ms), "text": txt, "important": False}
        self.notes_by_file.setdefault(fname, []).append(entry)
        self._push_undo({"type":"add","set":self.current_set_id,"file":fname,"entry":entry})
        self._resort_and_rebuild_table_preserving_selection(keep_pair=(self.current_set_id, uid))
        self.note_input.clear()
        self._on_clip_cancel_clicked()
        self._schedule_save_notes()

    def _on_ann_filter_changed(self, idx: int):
        txt = (self.ann_filter_combo.currentText() or "All").lower()
        if "point" in txt: self.annotation_filter = "points"
        elif "clip" in txt: self.annotation_filter = "clips"
        else: self.annotation_filter = "all"
        self._load_annotations_for_current()
    def _on_export_clips_clicked(self):
        # Collect all clips across current annotation set and folder
        aset = self._get_current_set()
        if not aset:
            QMessageBox.information(self, "No Set", "No current annotation set selected."); return
        clips: list[tuple[Path, dict]] = []
        base = self.current_practice_folder
        files = aset.get("files", {})
        for fname, meta in files.items():
            for e in (meta.get("notes") or []):
                if e.get("end_ms") is not None:
                    p = base / fname
                    if p.exists(): clips.append((p, e))
        if not clips:
            QMessageBox.information(self, "No Clips", "No region-based annotations found to export."); return

        # Prepare destination folder
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = self.current_practice_folder / f"Clips_{ts}"
        out_dir.mkdir(parents=True, exist_ok=True)

        # Check pydub/ffmpeg
        if not HAVE_PYDUB:
            QMessageBox.warning(self, "Missing dependency",
                "Export requires the 'pydub' package and FFmpeg installed on your system."); return
        try:
            from pydub import AudioSegment
            from pydub.utils import which as pydub_which
            if not pydub_which("ffmpeg"):
                QMessageBox.warning(self, "FFmpeg not found",
                    "FFmpeg isn't available on your PATH. Please install FFmpeg and try again."); return
        except Exception as e:
            QMessageBox.warning(self, "pydub error", f"pydub not available: {e}"); return

        # Export
        report_lines = []
        by_file = {}
        for p, e in clips:
            by_file.setdefault(p.name, []).append(e)
        for fname, entries in by_file.items():
            # group header
            report_lines.append(fname)
            # load once
            ext = p.suffix.lower()
            try:
                seg = AudioSegment.from_file(str((self.current_practice_folder / fname)))
            except Exception as ex:
                report_lines.append(f"Error loading {fname}: {ex}"); report_lines.append("\r\n"); continue
            # export entries
            entries.sort(key=lambda d: int(d.get('ms',0)))
            for i, e in enumerate(entries, 1):
                s = int(e.get('ms',0)); en = int(e.get('end_ms',0))
                if en <= s: continue
                clip = seg[s:en]
                base_name = Path(fname).stem
                out_name = f"{base_name}_clip{i:02d}_{human_time_ms(s).replace(':','-')}_to_{human_time_ms(en).replace(':','-')}{ext}"
                out_path = out_dir / out_name
                try:
                    clip.export(str(out_path), format=ext.lstrip('.'))
                except Exception as ex:
                    report_lines.append(f"{i:02d}: {human_time_ms(s)} - {human_time_ms(en)} :: {e.get('text','')} :: ERROR {ex}")
                    continue
                # log line
                report_lines.append(f"{human_time_ms(s)} - {human_time_ms(en)} :: {e.get('text','')}")
            report_lines.append("\r\n")  # blank line between files

        # Write report
        try:
            (out_dir / "clips_annotations.txt").write_text("\r\n".join(report_lines), encoding="utf-8")
        except Exception:
            pass
        QMessageBox.information(self, "Export Complete", f"Exported clips to: {out_dir}")



    # ----- Important annotations (Folder tab) -----
    def _refresh_important_table(self):
        rows = []
        parent_name = self.current_practice_folder.name
        for s in self.annotation_sets:
            if not bool(s.get("visible", True)): continue
            set_name = s.get("name","Set"); sid = s.get("id")
            for fname, meta in (s.get("files", {}) or {}).items():
                for n in (meta.get("notes") or []):
                    if bool(n.get("important", False)):
                        rows.append((sid, set_name, fname, int(n.get("ms", 0)), str(n.get("text", "")), int(n.get("uid", 0))))
        rows.sort(key=lambda r: (r[1].lower(), r[2].lower(), r[3]))
        self.imp_table.setRowCount(0)
        for sid, set_name, fname, ms, text, uid in rows:
            r = self.imp_table.rowCount(); self.imp_table.insertRow(r)
            s_item = QTableWidgetItem(set_name); s_item.setData(Qt.ItemDataRole.UserRole, sid)
            f_item = QTableWidgetItem(f"{parent_name}\\{fname}"); f_item.setData(Qt.ItemDataRole.UserRole, fname)
            t_item = QTableWidgetItem(human_time_ms(ms)); t_item.setData(Qt.ItemDataRole.UserRole, int(ms))
            n_item = QTableWidgetItem(text)
            self.imp_table.setItem(r, 0, s_item); self.imp_table.setItem(r, 1, f_item); self.imp_table.setItem(r, 2, t_item); self.imp_table.setItem(r, 3, n_item)

    def _on_important_double_clicked(self, item: QTableWidgetItem):
        row = item.row()
        s_item = self.imp_table.item(row, 0); f_item = self.imp_table.item(row, 1); t_item = self.imp_table.item(row, 2)
        if not s_item or not f_item or not t_item: return
        sid = str(s_item.data(Qt.ItemDataRole.UserRole) or "")
        fname = str(f_item.data(Qt.ItemDataRole.UserRole) or "")
        ms = int(t_item.data(Qt.ItemDataRole.UserRole) or 0)
        if not fname: return
        target = self.current_practice_folder / fname
        if not target.exists(): return
        for i in range(self.set_combo.count()):
            if str(self.set_combo.itemData(i)) == sid:
                if self.set_combo.currentIndex() != i: self.set_combo.setCurrentIndex(i)
                break
        self._play_file(target)
        self.tabs.setCurrentIndex(self._tab_index_by_name("Annotations"))
        aset = self._get_current_set()
        uid = -1
        if aset:
            notes = (aset.get("files", {}).get(fname, {}) or {}).get("notes", []) or []
            if notes: uid = min(notes, key=lambda e: abs(int(e.get("ms",0))-ms)).get("uid", -1)
        if uid >= 0:
            self._select_row_by_uid(int(uid), set_id=sid)
            self.waveform.set_selected_uid(sid, int(uid))
        self.player.setPosition(int(ms)); self.player.play()
        self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))

    # ----- Export annotations (CRLF) -----
    def _export_annotations(self):
        default_path = str((self.current_practice_folder / "annotations_export.txt").resolve())
        save_path, _ = QFileDialog.getSaveFileName(self, "Export Annotations", default_path, "Text Files (*.txt);;All Files (*)")
        if not save_path: return
        lines: List[str] = []
        
        # Export folder notes from all visible annotation sets
        for s in self.annotation_sets:
            if not bool(s.get("visible", True)): continue
            folder_notes = (s.get("folder_notes", "") or "").strip()
            if folder_notes:
                set_name = s.get("name", "Unknown Set")
                lines.append(f"[Folder - {set_name}] {self.current_practice_folder}")
                for ln in folder_notes.replace("\r\n", "\n").split("\n"):
                    lines.append(ln.rstrip())
                lines.append("")
        parent_name = self.current_practice_folder.name
        all_files = set()
        for s in self.annotation_sets:
            if not bool(s.get("visible", True)): continue
            all_files.update((s.get("files", {}) or {}).keys())
        for fname in sorted(all_files, key=str.lower):
            collected = []
            for s in self.annotation_sets:
                if not bool(s.get("visible", True)): continue
                meta = (s.get("files", {}) or {}).get(fname)
                if not meta: continue
                overview = (meta.get("general","") or "").strip()
                notes = sorted(meta.get("notes", []) or [], key=lambda n: int(n.get("ms",0)))
                collected.append((s.get("name","Set"), overview, notes))
            if not collected: continue
            title = f"{parent_name}\\{fname}"
            lines.append(title)
            for set_name, overview, notes in collected:
                lines.append(f"== Set: {set_name} ==")
                if overview:
                    for ln in overview.replace("\r\n","\n").split("\n"):
                        lines.append(f"Overview: {ln.rstrip()}")
                for n in notes:
                    ts = human_time_ms(int(n.get("ms", 0)))
                    txt = str(n.get("text", "")).replace("\n", " ").strip()
                    lines.append(f"{ts} {txt}")
            lines.append("")
        try:
            out = "\r\n".join(lines).rstrip("\r\n") + "\r\n"
            with open(save_path, "w", encoding="utf-8", newline="") as f:
                f.write(out)
            reply = QMessageBox.question(
                self, "Export Complete",
                f"Annotations exported to:\r\n{save_path}\r\n\r\nOpen the file now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes,
            )
            if reply == QMessageBox.StandardButton.Yes:
                _open_path_default(Path(save_path))
        except Exception as e:
            QMessageBox.warning(self, "Export Failed", f"Couldn't write file:\n{e}")

    # ----- Batch rename (##_<ProvidedName>) -----
    def _batch_rename(self):
        files = self._list_audio_in_current_dir()
        if not files:
            QMessageBox.information(self, "Nothing to Rename", "No WAV/MP3 files in this folder."); return
        def ctime(p: Path) -> float:
            try: return os.path.getctime(p)
            except Exception: return p.stat().st_mtime
        files.sort(key=ctime)
        width = max(2, len(str(len(files))))
        plan, errors = [], []
        for i, p in enumerate(files, start=1):
            base = sanitize(self.provided_names.get(p.name, "") or p.stem)
            new_base = f"{str(i).zfill(width)}_{base}"
            target = p.with_name(f"{new_base}{p.suffix.lower()}")
            n = 1
            while target.exists() and target.resolve() != p.resolve():
                target = p.with_name(f"{new_base} ({n}){p.suffix.lower()}"); n += 1
            plan.append((p, target))
        preview = "\n".join(f"{src.name}  →  {dst.name}" for src, dst in plan[:25])
        more = "" if len(plan) <= 25 else f"\n… and {len(plan) - 25} more"
        if QMessageBox.question(self, "Confirm Batch Rename", f"Rename {len(plan)} file(s) as follows?\n\n{preview}{more}",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return
        did = 0; errors = []
        for src, dst in plan:
            try:
                src.rename(dst)
                if src.name in self.provided_names: self.provided_names[dst.name] = self.provided_names.pop(src.name)
                if src.name in self.played_durations: self.played_durations[dst.name] = self.played_durations.pop(src.name)
                for s in self.annotation_sets:
                    files_map = s.setdefault("files", {})
                    if src.name in files_map and dst.name not in files_map:
                        files_map[dst.name] = files_map.pop(src.name)
                did += 1
            except Exception as e:
                errors.append(f"{src.name}: {e}")
        self._load_current_set_into_fields()
        self._save_names(); self._save_notes(); self._save_duration_cache()
        self._refresh_right_table()
        self.fs_model.setRootPath(""); self.fs_model.setRootPath(str(self.root_path))
        self.tree.setRootIndex(self.file_proxy.mapFromSource(self.fs_model.index(str(self.root_path))))
        if self.current_audio_file:
            cur = self.current_audio_file.name
            for s, d in plan:
                if s.name == cur: self.current_audio_file = d; break
        self._load_annotations_for_current()
        if errors:
            text = "\n".join(errors[:20])
            more = "" if len(errors) <= 20 else f"\n… and {len(errors) - 20} more"
            QMessageBox.warning(self, "Finished with Errors", f"Renamed {did}/{len(plan)} files. Some failed:\n\n" + text + more)
        else:
            QMessageBox.information(self, "Batch Rename Complete", f"Renamed {did} file(s).")
        reply = QMessageBox.question(
            self, "Open Folder", "Open this folder in your file explorer now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if reply == QMessageBox.StandardButton.Yes:
            _open_path_default(self.root_path)

    # ----- WAV→MP3 conversion (threaded with progress) -----
    def _convert_wav_to_mp3_threaded(self):
        if not HAVE_PYDUB:
            QMessageBox.warning(self, "Missing dependency",
                                "This feature requires the 'pydub' package and FFmpeg installed on your system.")
            return
        if not pydub_which("ffmpeg"):
            QMessageBox.warning(self, "FFmpeg not found",
                                "FFmpeg isn't available on your PATH. Please install FFmpeg and try again.")
            return
        wavs = self._list_wav_in_root()
        if not wavs:
            QMessageBox.information(self, "Nothing to Convert", "No WAV files in this folder."); return
        msg = ("Convert {n} WAV file(s) to MP3 in-place?\n\n"
               "• MP3s will be created next to the originals\n"
               "• Original WAV/WAVE files will be deleted AFTER each successful conversion").format(n=len(wavs))
        if QMessageBox.question(self, "Convert WAV→MP3", msg,
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return

        self._stop_playback()

        total = len(wavs)
        dlg = QProgressDialog("Preparing conversion…", "Cancel", 0, total, self)
        dlg.setWindowTitle("WAV → MP3 Conversion")
        dlg.setWindowModality(Qt.WindowModality.WindowModal)
        dlg.setAutoClose(False); dlg.setAutoReset(False)
        dlg.setMinimumDuration(0); dlg.setValue(0)

        self._conv_thread = QThread(self)
        self._conv_worker = ConvertWorker([str(p) for p in wavs], DEFAULT_MP3_BITRATE)
        self._conv_worker.moveToThread(self._conv_thread)

        remap_notes: Dict[str,str] = {}
        fails: List[Tuple[str,str]] = []
        successes = 0

        def on_progress(done:int, total:int, name:str):
            dlg.setLabelText(f"Converting {name}  ({min(done,total)}/{total})")
            dlg.setRange(0, total); dlg.setValue(done)

        def on_file_done(src_name:str, dst_name:str, deleted_ok:bool, err:str):
            nonlocal successes
            if dst_name:
                remap_notes[src_name] = dst_name
                if deleted_ok: successes += 1
            if err:
                fails.append((src_name, err))

        def on_finished(canceled: bool):
            dlg.close()
            if remap_notes:
                for s in self.annotation_sets:
                    files_map = s.setdefault("files", {})
                    for old, new in remap_notes.items():
                        if old in files_map and new not in files_map:
                            files_map[new] = files_map.pop(old)
                remapped_names = {}
                for old, new in remap_notes.items():
                    if old in self.provided_names and new not in self.provided_names:
                        remapped_names[new] = self.provided_names.pop(old)
                self.provided_names.update(remapped_names)
                for old, new in remap_notes.items():
                    if old in self.played_durations and new not in self.played_durations:
                        self.played_durations[new] = self.played_durations.pop(old)
                self._save_names(); self._save_notes(); self._save_duration_cache()

            self._load_current_set_into_fields()
            self._refresh_right_table()
            self.fs_model.setRootPath(""); self.fs_model.setRootPath(str(self.root_path))
            self.tree.setRootIndex(self.file_proxy.mapFromSource(self.fs_model.index(str(self.root_path))))
            self._load_annotations_for_current()
            self._refresh_important_table()

            if canceled:
                status_title = "Conversion Canceled"; body = f"Finished {successes} file(s) before cancel."
            else:
                status_title = "Conversion Complete" if not fails else "Conversion Finished (with issues)"
                body = f"Converted and deleted {successes} WAV file(s)."

            if fails:
                text = "\n".join([f"{n}: {err}" for n, err in fails[:20]])
                more = "" if len(fails) <= 20 else f"\n… and {len(fails)-20} more"
                QMessageBox.warning(self, status_title, f"{body}\n\nSome issues:\n\n{text}{more}")
            else:
                QMessageBox.information(self, status_title, body)

            reply = QMessageBox.question(
                self, "Open Folder", "Open this folder in your file explorer now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes,
            )
            if reply == QMessageBox.StandardButton.Yes:
                _open_path_default(self.root_path)

            self._conv_worker.deleteLater()
            self._conv_thread.quit(); self._conv_thread.wait(); self._conv_thread.deleteLater()
            self._conv_worker = None; self._conv_thread = None

        self._conv_thread.started.connect(self._conv_worker.run)
        self._conv_worker.progress.connect(on_progress)
        self._conv_worker.file_done.connect(on_file_done)
        self._conv_worker.finished.connect(on_finished)
        dlg.canceled.connect(self._conv_worker.cancel)

        self._conv_thread.start()
        dlg.exec()

    # ----- Undo/Redo -----
    def _on_undo_capacity_changed(self, v: int):
        self._undo_capacity = int(v)
        self.settings.setValue(SETTINGS_KEY_UNDO_CAP, int(v))
        overflow = len(self._undo_stack) - self._undo_capacity
        if overflow > 0:
            del self._undo_stack[0:overflow]
            self._undo_index = max(0, self._undo_index - overflow)
        self._update_undo_actions_enabled()

    def _push_undo(self, action: dict):
        if self._undo_index < len(self._undo_stack):
            del self._undo_stack[self._undo_index:]
        self._undo_stack.append(action)
        if len(self._undo_stack) > self._undo_capacity:
            drop = len(self._undo_stack) - self._undo_capacity
            del self._undo_stack[0:drop]
        self._undo_index = len(self._undo_stack)
        self._update_undo_actions_enabled()

    def _undo(self):
        if self._undo_index <= 0: return
        self._undo_index -= 1
        action = self._undo_stack[self._undo_index]
        self._apply_action(action, undo=True)
        self._update_undo_actions_enabled()

    def _redo(self):
        if self._undo_index >= len(self._undo_stack): return
        action = self._undo_stack[self._undo_index]
        self._undo_index += 1
        self._apply_action(action, undo=False)
        self._update_undo_actions_enabled()

    def _update_undo_actions_enabled(self):
        self.act_undo.setEnabled(self._undo_index > 0)
        self.act_redo.setEnabled(self._undo_index < len(self._undo_stack))

    def _apply_action(self, action: dict, undo: bool):
        typ = action.get("type")
        set_id = str(action.get("set",""))
        fname = str(action.get("file",""))
        if not fname: return
        if set_id == self.current_set_id:
            lst = self.notes_by_file.setdefault(fname, [])
        else:
            aset = None
            for s in self.annotation_sets:
                if s.get("id") == set_id: aset = s; break
            if not aset: return
            meta = aset.setdefault("files", {}).setdefault(fname, {"general":"","notes":[]})
            lst = meta["notes"]

        def _reload_if_current():
            if self.current_audio_file and self.current_audio_file.name == fname:
                # If we modified the current set's notes_by_file, sync to annotation set before reload
                if set_id == self.current_set_id:
                    self._sync_fields_into_current_set()
                self._load_annotations_for_current()
                self._update_waveform_annotations()
            self._save_notes(); self._refresh_important_table()

        if typ == "add":
            entry = dict(action.get("entry", {}))
            uid = int(entry.get("uid", -1))
            if undo:
                lst[:] = [e for e in lst if int(e.get("uid",-1)) != uid]
            else:
                lst.append(entry); lst.sort(key=lambda e: int(e.get("ms", 0)))
            _reload_if_current(); return

        if typ == "delete":
            entries = [dict(e) for e in (action.get("entries") or [])]
            if undo:
                lst.extend(entries); lst.sort(key=lambda e: int(e.get("ms",0)))
            else:
                uids = {int(e.get("uid",-1)) for e in entries}
                lst[:] = [e for e in lst if int(e.get("uid",-1)) not in uids]
            _reload_if_current(); return

        if typ == "edit":
            uid = int(action.get("uid",-1))
            field = str(action.get("field",""))
            before = action.get("before"); after = action.get("after")
            target = None
            for e in lst:
                if int(e.get("uid",-1)) == uid: target = e; break
            if not target: return
            value = before if undo else after
            if field == "ms":
                target["ms"] = int(value); lst.sort(key=lambda e: int(e.get("ms",0)))
            elif field == "text":
                target["text"] = str(value)
            elif field == "important":
                target["important"] = bool(value)
            _reload_if_current(); return

    # ----- Media events / close -----
    def _on_media_error(self, _err, msg):
        if msg: QMessageBox.warning(self, "Playback Error", msg)

    def _on_media_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            if self.auto_progress_cb.isChecked(): self._play_next_file()

    # ----- Fingerprinting methods -----
    def _update_fingerprint_ui(self):
        """Update fingerprint UI elements."""
        # Discover practice folders with fingerprints
        practice_folders = discover_practice_folders_with_fingerprints(self.root_path)
        current_dir = self._get_audio_file_dir()
        
        # Count total fingerprints available for matching (excluding current folder)
        fingerprint_map = collect_fingerprints_from_folders(practice_folders, exclude_dir=current_dir)
        total_available_songs = len(fingerprint_map)
        unique_songs = sum(1 for song_entries in fingerprint_map.values() if len(song_entries) == 1)
        
        # Enable auto-label if we have practice folders with fingerprints OR a reference folder
        can_auto_label = (not self.auto_label_in_progress and bool(practice_folders) and (len(practice_folders) > 1 or 
                         (len(practice_folders) == 1 and practice_folders[0].resolve() != current_dir.resolve()))) or \
                        bool(self.fingerprint_reference_dir)
        
        # Prioritize manually selected reference folder, then show practice folder info
        if self.fingerprint_reference_dir:
            self.fingerprint_ref_label.setText(f"Reference: {self.fingerprint_reference_dir.name}")
            self.fingerprint_ref_label.setStyleSheet("color: #333;")
        elif practice_folders:
            # Show practice folder information when no reference folder is selected
            if len(practice_folders) == 1:
                if practice_folders[0].resolve() == current_dir.resolve():
                    folder_text = f"Current folder only ({practice_folders[0].name})"
                else:
                    folder_text = f"1 practice folder: {practice_folders[0].name}"
            else:
                other_folders = [f for f in practice_folders if f.resolve() != current_dir.resolve()]
                if other_folders:
                    folder_text = f"{len(other_folders)} other practice folders"
                else:
                    folder_text = f"{len(practice_folders)} practice folders (all current)"
            
            self.fingerprint_ref_label.setText(folder_text)
            self.fingerprint_ref_label.setStyleSheet("color: #333;")
        else:
            self.fingerprint_ref_label.setText("(No fingerprints found)")
            self.fingerprint_ref_label.setStyleSheet("color: #666; font-style: italic;")
        
        self.auto_label_btn.setEnabled(can_auto_label)
        
        # Update status with current folder and available songs info
        current_cache = load_fingerprint_cache(current_dir)
        num_current_fingerprints = len(current_cache.get("files", {}))
        
        status_parts = [f"Current: {num_current_fingerprints} fingerprints"]
        if total_available_songs > 0:
            status_parts.append(f"Available: {total_available_songs} songs")
            if unique_songs > 0:
                status_parts.append(f"({unique_songs} unique)")
        
        self.fingerprint_status.setText(" | ".join(status_parts))

    def _show_practice_folders_info(self):
        """Show information about discovered practice folders and their fingerprints."""
        practice_folders = discover_practice_folders_with_fingerprints(self.root_path)
        current_dir = self._get_audio_file_dir()
        
        if not practice_folders:
            QMessageBox.information(self, "No Practice Folders Found", 
                                  "No practice folders with fingerprints were found.\n\n"
                                  "To use cross-folder matching:\n"
                                  "1. Navigate to practice session folders\n"
                                  "2. Generate fingerprints for each folder\n"
                                  "3. The system will automatically find and use them for matching")
            return
        
        # Collect detailed information
        info_lines = [f"Found {len(practice_folders)} practice folder(s) with fingerprints:\n"]
        
        total_songs = 0
        unique_songs = 0
        fingerprint_map = collect_fingerprints_from_folders(practice_folders, exclude_dir=current_dir)
        
        for folder in practice_folders:
            cache = load_fingerprint_cache(folder)
            num_files = len(cache.get("files", {}))
            total_songs += num_files
            
            is_current = folder.resolve() == current_dir.resolve()
            current_marker = " (current)" if is_current else ""
            info_lines.append(f"• {folder.name}: {num_files} fingerprints{current_marker}")
        
        # Count unique songs (appearing in only one folder)
        for song_entries in fingerprint_map.values():
            if len(song_entries) == 1:
                unique_songs += 1
        
        available_for_matching = len(fingerprint_map)
        info_lines.append(f"\nAvailable for matching: {available_for_matching} songs")
        info_lines.append(f"Unique songs (best for identification): {unique_songs}")
        info_lines.append(f"Multi-folder songs: {available_for_matching - unique_songs}")
        
        if available_for_matching > 0:
            info_lines.append(f"\nThe system prioritizes matches from songs that appear in only one folder,")
            info_lines.append(f"as these provide the most reliable identification.")
        
        QMessageBox.information(self, "Practice Folders Information", "\n".join(info_lines))

    def _select_fingerprint_reference_folder(self):
        """Let user select a folder containing reference audio files with fingerprints."""
        dlg = QFileDialog(self, "Select Reference Folder for Fingerprints")
        dlg.setFileMode(QFileDialog.FileMode.Directory)
        dlg.setOption(QFileDialog.Option.ShowDirsOnly, True)
        
        if dlg.exec():
            ref_path = Path(dlg.selectedFiles()[0])
            self.fingerprint_reference_dir = ref_path
            self.settings.setValue(SETTINGS_KEY_FINGERPRINT_DIR, str(ref_path))
            self._update_fingerprint_ui()

    def _on_fingerprint_threshold_changed(self, value):
        """Handle threshold change."""
        self.fingerprint_threshold = value / 100.0
        self.settings.setValue(SETTINGS_KEY_FINGERPRINT_THRESHOLD, self.fingerprint_threshold)

    def _generate_fingerprints_for_folder(self):
        """Generate fingerprints for all audio files in the current folder."""
        current_dir = self._get_audio_file_dir()
        audio_files = self._list_audio_in_current_dir()
        
        if not audio_files:
            QMessageBox.information(self, "No Audio Files", "No audio files found in current folder.")
            return
        
        cache = load_fingerprint_cache(current_dir)
        
        progress = QProgressDialog("Generating fingerprints...", "Cancel", 0, len(audio_files), self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()
        
        generated = 0
        for i, audio_file in enumerate(audio_files):
            if progress.wasCanceled():
                break
                
            progress.setLabelText(f"Processing {audio_file.name}...")
            progress.setValue(i)
            QApplication.processEvents()
            
            # Check if fingerprint already exists and is up to date
            size, mtime = file_signature(audio_file)
            existing = cache["files"].get(audio_file.name)
            if existing and existing.get("size") == size and existing.get("mtime") == mtime:
                continue  # Skip if already cached and file unchanged
            
            try:
                # Generate fingerprint
                samples, sr, dur_ms = decode_audio_samples(audio_file)
                fingerprint = compute_audio_fingerprint(samples, sr)
                
                # Store in cache
                cache["files"][audio_file.name] = {
                    "fingerprint": fingerprint,
                    "size": size,
                    "mtime": mtime,
                    "duration_ms": dur_ms
                }
                generated += 1
                
            except Exception as e:
                print(f"Error generating fingerprint for {audio_file.name}: {e}")
        
        progress.setValue(len(audio_files))
        save_fingerprint_cache(current_dir, cache)
        
        QMessageBox.information(self, "Fingerprints Generated", 
                                f"Generated {generated} new fingerprints.\n"
                                f"Total fingerprints in folder: {len(cache['files'])}")
        self._update_fingerprint_ui()

    def _auto_label_with_fingerprints(self):
        """Auto-label files in current folder based on fingerprint matches from practice folders."""
        # Check if auto-labeling is already in progress
        if self.auto_label_in_progress:
            QMessageBox.warning(self, "Auto-Labeling In Progress", 
                              "Auto-labeling is already in progress. Please apply or cancel the current operation first.")
            return
            
        current_dir = self._get_audio_file_dir()
        
        # Create backup of current provided names
        self.auto_label_backup_names = self.provided_names.copy()
        
        # Discover all practice folders with fingerprints
        practice_folders = discover_practice_folders_with_fingerprints(self.root_path)
        
        # If no practice folders found, fall back to reference folder approach
        if not practice_folders:
            if not self.fingerprint_reference_dir:
                QMessageBox.warning(self, "No Fingerprints Available", 
                                  "No fingerprints found in practice folders.\n"
                                  "Please select a reference folder or generate fingerprints for practice folders first.")
                return
            practice_folders = [self.fingerprint_reference_dir]
        
        # If current folder is the only one with fingerprints, nothing to match against
        if len(practice_folders) == 1 and practice_folders[0].resolve() == current_dir.resolve():
            QMessageBox.information(self, "No Other Practice Folders", 
                                  "Current folder is the only one with fingerprints. Need other practice folders to match against.")
            return
        
        # Collect fingerprints from all practice folders (excluding current)
        fingerprint_map = collect_fingerprints_from_folders(practice_folders, exclude_dir=current_dir)
        
        if not fingerprint_map:
            QMessageBox.warning(self, "No Reference Fingerprints", 
                              "No fingerprints found in other practice folders.")
            return
        
        # Load current folder fingerprints
        current_cache = load_fingerprint_cache(current_dir)
        current_fingerprints = current_cache.get("files", {})
        
        # Get files to process (unlabeled files)
        audio_files = self._list_audio_in_current_dir()
        unlabeled_files = [f for f in audio_files if not self.provided_names.get(f.name, "").strip()]
        
        if not unlabeled_files:
            QMessageBox.information(self, "No Unlabeled Files", "All files already have names.")
            return
        
        # Process each unlabeled file
        matches_found = 0
        unique_matches = 0  # Matches from songs appearing in only one folder
        progress = QProgressDialog("Matching fingerprints across practice folders...", "Cancel", 0, len(unlabeled_files), self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()
        
        match_details = []  # For detailed results message
        
        for i, audio_file in enumerate(unlabeled_files):
            if progress.wasCanceled():
                break
                
            progress.setLabelText(f"Matching {audio_file.name}...")
            progress.setValue(i)
            QApplication.processEvents()
            
            # Get or generate fingerprint for current file
            current_fp = current_fingerprints.get(audio_file.name, {}).get("fingerprint")
            if not current_fp:
                try:
                    samples, sr, dur_ms = decode_audio_samples(audio_file)
                    current_fp = compute_audio_fingerprint(samples, sr)
                    # Update cache
                    size, mtime = file_signature(audio_file)
                    current_cache["files"][audio_file.name] = {
                        "fingerprint": current_fp,
                        "size": size,
                        "mtime": mtime,
                        "duration_ms": dur_ms
                    }
                except Exception as e:
                    print(f"Error processing {audio_file.name}: {e}")
                    continue
            
            # Find best match across all practice folders
            match_result = find_best_cross_folder_match(current_fp, fingerprint_map, self.fingerprint_threshold)
            
            if match_result:
                matched_filename, score, source_folder, provided_name = match_result
                
                # Use the provided name from the matched fingerprint's folder
                self.provided_names[audio_file.name] = provided_name
                matches_found += 1
                
                # Check if this was a unique match (song appears in only one folder)
                folder_count = len(fingerprint_map[matched_filename])
                if folder_count == 1:
                    unique_matches += 1
                
                # Store details for result message
                match_details.append({
                    "file": audio_file.name,
                    "match": provided_name,
                    "score": score,
                    "folder": source_folder.name,
                    "unique": folder_count == 1
                })
        
        progress.setValue(len(unlabeled_files))
        
        # Don't save immediately - show apply/cancel buttons instead
        if matches_found > 0:
            # Update fingerprint cache but don't save names yet
            save_fingerprint_cache(current_dir, current_cache)
            self._refresh_right_table()
            
            # Set auto-labeling state and show apply/cancel buttons
            self.auto_label_in_progress = True
            self.auto_label_buttons_widget.setVisible(True)
            
            # Show summary of what would be applied
            result_message = f"Found {matches_found} matches out of {len(unlabeled_files)} unlabeled files.\n"
            result_message += f"Unique matches (song in only one folder): {unique_matches}\n"
            result_message += f"Threshold: {self.fingerprint_threshold:.0%}\n"
            result_message += f"Scanned {len(practice_folders)} practice folders\n\n"
            
            if match_details:
                result_message += "Match details:\n"
                for detail in match_details[:5]:  # Show first 5 matches
                    unique_indicator = " (unique)" if detail["unique"] else ""
                    result_message += f"• {detail['file']} → {detail['match']} ({detail['score']:.0%}, from {detail['folder']}){unique_indicator}\n"
                if len(match_details) > 5:
                    result_message += f"... and {len(match_details) - 5} more matches\n"
                    
            result_message += "\nUse Apply to save these changes or Cancel to discard them."
            
            QMessageBox.information(self, "Auto-Labeling Preview", result_message)
        else:
            # No matches found, no need for apply/cancel buttons
            result_message = f"No matches found for {len(unlabeled_files)} unlabeled files.\n"
            result_message += f"Threshold: {self.fingerprint_threshold:.0%}\n"
            result_message += f"Scanned {len(practice_folders)} practice folders"
            
            QMessageBox.information(self, "Auto-Labeling Complete", result_message)

    def _on_auto_label_apply(self):
        """Apply the auto-labeling changes and hide the apply/cancel buttons."""
        if not self.auto_label_in_progress:
            return
            
        # Save the changes
        self._save_names()
        
        # Reset state
        self.auto_label_in_progress = False
        self.auto_label_backup_names.clear()
        self.auto_label_buttons_widget.setVisible(False)
        
        # Update UI state
        self._update_fingerprint_ui()
        
        # Show confirmation
        QMessageBox.information(self, "Changes Applied", 
                              "Auto-labeling changes have been saved successfully.")

    def _on_auto_label_cancel(self):
        """Cancel the auto-labeling changes and restore the previous state."""
        if not self.auto_label_in_progress:
            return
            
        # Restore the backup
        self.provided_names = self.auto_label_backup_names.copy()
        self._refresh_right_table()
        
        # Reset state
        self.auto_label_in_progress = False
        self.auto_label_backup_names.clear()
        self.auto_label_buttons_widget.setVisible(False)
        
        # Update UI state
        self._update_fingerprint_ui()
        
        # Show confirmation
        QMessageBox.information(self, "Changes Cancelled", 
                              "Auto-labeling changes have been discarded.")

    def _generate_fingerprints_for_reference_folder(self):
        """Generate fingerprints for the reference folder."""
        if not self.fingerprint_reference_dir:
            return
        
        # Get audio files in reference folder
        ref_audio_files = []
        for ext in AUDIO_EXTS:
            ref_audio_files.extend(self.fingerprint_reference_dir.glob(f"*{ext}"))
        
        if not ref_audio_files:
            QMessageBox.information(self, "No Audio Files", 
                                    f"No audio files found in reference folder:\n{self.fingerprint_reference_dir}")
            return
        
        cache = load_fingerprint_cache(self.fingerprint_reference_dir)
        
        progress = QProgressDialog("Generating reference fingerprints...", "Cancel", 0, len(ref_audio_files), self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()
        
        generated = 0
        for i, audio_file in enumerate(ref_audio_files):
            if progress.wasCanceled():
                break
                
            progress.setLabelText(f"Processing {audio_file.name}...")
            progress.setValue(i)
            QApplication.processEvents()
            
            # Check if fingerprint already exists and is up to date
            size, mtime = file_signature(audio_file)
            existing = cache["files"].get(audio_file.name)
            if existing and existing.get("size") == size and existing.get("mtime") == mtime:
                continue
            
            try:
                samples, sr, dur_ms = decode_audio_samples(audio_file)
                fingerprint = compute_audio_fingerprint(samples, sr)
                
                cache["files"][audio_file.name] = {
                    "fingerprint": fingerprint,
                    "size": size,
                    "mtime": mtime,
                    "duration_ms": dur_ms
                }
                generated += 1
                
            except Exception as e:
                print(f"Error generating fingerprint for {audio_file.name}: {e}")
        
        progress.setValue(len(ref_audio_files))
        save_fingerprint_cache(self.fingerprint_reference_dir, cache)
        
        QMessageBox.information(self, "Reference Fingerprints Generated",
                                f"Generated {generated} new fingerprints in reference folder.")

    def closeEvent(self, ev):
        # Check if auto-labeling is in progress
        if self.auto_label_in_progress:
            reply = QMessageBox.question(self, "Auto-labeling in progress", 
                                       "Auto-labeling is in progress. Do you want to apply the changes before closing?",
                                       QMessageBox.StandardButton.Apply | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
            
            if reply == QMessageBox.StandardButton.Apply:
                # Apply changes before closing
                self._save_names()
                self.auto_label_in_progress = False
                self.auto_label_backup_names.clear()
            elif reply == QMessageBox.StandardButton.Discard:
                # Discard changes before closing  
                self.provided_names = self.auto_label_backup_names.copy()
                self.auto_label_in_progress = False
                self.auto_label_backup_names.clear()
            else:  # Cancel
                ev.ignore()
                return
        
        self._save_names(); self._save_notes(); self._save_duration_cache(); super().closeEvent(ev)

# ========== Entrypoint ==========
def main():
    app = QApplication(sys.argv)
    app.setOrganizationName(APP_ORG); app.setApplicationName(APP_NAME)
    if "Fusion" in QStyleFactory.keys(): app.setStyle("Fusion")
    w = AudioBrowser(); w.show(); sys.exit(app.exec())

if __name__ == "__main__":
    main()
