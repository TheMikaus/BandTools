#!/usr/bin/env python3
# audio_browser.py

"""
Audio Folder Player with Annotations + Async Waveform (Live Progress + Cache)

New in this build (based on your requests):
1) Annotations are always kept in time order (auto-sorted after any change).
2) Each annotation can be flagged as Important (checkbox column).
3) Folder Notes tab shows a live list of all Important annotations (File – Time – Note).
4) Double-clicking an Important annotation (Folder Notes tab) jumps to that song/time.
5) Selecting an annotation highlights the whole row.
6) Selecting an annotation shows a GREEN marker on the waveform at its time.
7) You can adjust an annotation’s time:
   - Edit the time cell directly (supports mm:ss or h:mm:ss), OR
   - Click-and-drag the GREEN marker on the waveform.
8) Single-click enables editing in the Annotations table; double-click jumps to that time.
9) Drag the GREEN marker to change the annotation time (re-sorted on release).
10) When typing a new note, we remember the time you STARTED typing; if you clear the box, we clear that “captured time” until you type again.

All earlier features remain:
- First-run folder picker; remembers & changeable.
- Left tree only shows folders + .wav/.wave/.mp3. Double-click folder/file behavior as before.
- Single-click WAV/MP3 starts playback; slider and waveform support click-to-seek; clicking currently-playing file does not restart.
- Async waveform generation with live percentage + caching by size/mtime/columns.
- Per-song general paragraph; folder-level notes; export to CRLF text; batch rename ##_<ProvidedName>.
- Tabs default order (Folder Notes, Library, Annotations); user-reorder persisted.
- Auto-switch-to-Annotations toggle and Auto-progress toggle, both persisted.

Note: For MP3 waveform decoding, install FFmpeg for pydub.
"""

from __future__ import annotations

# ---------- Bootstrap: auto-install missing packages ----------
import sys, subprocess, importlib, os
def _ensure_import(mod_name: str, pip_name: str | None = None) -> bool:
    try:
        importlib.import_module(mod_name); return True
    except ImportError:
        if getattr(sys, "frozen", False): return False
        pkg = pip_name or mod_name
        print(f"[bootstrap] Installing '{pkg}'...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
        except subprocess.CalledProcessError:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", pkg])
            except subprocess.CalledProcessError:
                return False
        importlib.invalidate_caches()
        try:
            importlib.import_module(mod_name); return True
        except ImportError:
            return False

if not _ensure_import("PyQt6", "PyQt6"):
    raise RuntimeError("PyQt6 is required.")
HAVE_NUMPY = _ensure_import("numpy", "numpy")
HAVE_PYDUB = _ensure_import("pydub", "pydub")

# ---------- App imports ----------
import json, re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from PyQt6.QtCore import (
    QItemSelection, QModelIndex, QSettings, QTimer, Qt, QUrl, QPoint, QSize,
    pyqtSignal, QRect, QObject, QThread, QDir
)
from PyQt6.QtGui import (
    QAction, QKeySequence, QIcon, QPixmap, QPainter, QColor, QPen
)
# QFileSystemModel can live in QtGui in some builds; fallback to QtWidgets.
try:
    from PyQt6.QtGui import QFileSystemModel
except Exception:
    from PyQt6.QtWidgets import QFileSystemModel

from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from PyQt6.QtWidgets import (
    QApplication, QHBoxLayout, QHeaderView, QMainWindow, QMessageBox,
    QPushButton, QSlider, QSplitter, QTableWidget, QTableWidgetItem,
    QTreeView, QVBoxLayout, QWidget, QFileDialog, QAbstractItemView, QStatusBar,
    QToolBar, QStyle, QLabel, QTabWidget, QLineEdit, QPlainTextEdit, QCheckBox, QWidgetAction
)
from PyQt6.QtWidgets import QStyleFactory

# WAV decoding
import wave, audioop
from array import array
if HAVE_NUMPY:
    import numpy as np
if HAVE_PYDUB:
    try:
        from pydub import AudioSegment
    except Exception:
        HAVE_PYDUB = False

APP_ORG = "YourCompany"
APP_NAME = "Audio Folder Player"
SETTINGS_KEY_ROOT = "root_dir"
SETTINGS_KEY_TABS_ORDER = "tabs_order"            # pipe-separated tab names
SETTINGS_KEY_AUTOPROGRESS = "auto_progress"       # bool
SETTINGS_KEY_AUTOSWITCH = "auto_switch_ann"       # bool
NAMES_JSON = ".provided_names.json"
NOTES_JSON = ".audio_notes.json"        # versioned format, backward compatible
WAVEFORM_JSON = ".waveform_cache.json"
AUDIO_EXTS = {".wav", ".wave", ".mp3"}

# Waveform cache resolution (number of precomputed columns)
WAVEFORM_COLUMNS = 2000

# ---------- Helpers ----------
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
    if len(parts) == 1:
        sec = int(parts[0]); return max(0, sec * 1000)
    if len(parts) == 2:
        mm, ss = map(int, parts); return max(0, (mm * 60 + ss) * 1000)
    if len(parts) == 3:
        hh, mm, ss = map(int, parts); return max(0, (hh * 3600 + mm * 60 + ss) * 1000)
    return None

def sanitize(name: str) -> str:
    name = re.sub(r'[\\/:*?"<>|]+', "_", name.strip())
    return re.sub(r"\s+", " ", name).strip() or "Track"

def resource_path(name: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / name

def file_signature(p: Path) -> Tuple[int, int]:
    try:
        st = p.stat(); return int(st.st_size), int(st.st_mtime)
    except Exception:
        return (0, 0)

def load_waveform_cache(dirpath: Path) -> Dict:
    try:
        fp = dirpath / WAVEFORM_JSON
        if fp.exists():
            with open(fp, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "files" in data:
                    return data
    except Exception:
        pass
    return {"version": 1, "files": {}}

def save_waveform_cache(dirpath: Path, cache: Dict) -> None:
    try:
        fp = dirpath / WAVEFORM_JSON
        with open(fp, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def _open_path_default(path: Path):
    """Open a file or folder in the OS default application/explorer."""
    try:
        if sys.platform.startswith("win"):
            os.startfile(str(path))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.call(["open", str(path)])
        else:
            subprocess.call(["xdg-open", str(path)])
    except Exception as e:
        QMessageBox.warning(None, "Open Failed", f"Couldn't open:\n{e}")

# ---------- Click-to-seek slider ----------
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

# ---------- Waveform decoding utilities ----------
def decode_audio_samples(path: Path) -> Tuple[List[float], int, int]:
    """Return (mono_samples_float_list, sample_rate, duration_ms)."""
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
    """
    Yield (start_col, peaks_chunk) progressively.
    peaks_chunk is List[[min,max], ...] (lists for signal marshalling).
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
                    v = float(arr[min(a, n-1)]); out.append([v, v])
            yield start, out
    else:
        for start in range(0, columns, chunk):
            end = min(columns, start + chunk)
            out = []
            for i in range(start, end):
                a = int(i * n / columns)
                b = int((i+1) * n / columns)
                if b <= a:
                    v = samples[min(a, n-1)]; out.append([v, v])
                else:
                    seg = samples[a:b]; out.append([float(min(seg)), float(max(seg))])
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

# ---------- Waveform worker (threaded with progress + generation id) ----------
class WaveformWorker(QObject):
    progress = pyqtSignal(int, str, list, int, int)  # gen_id, path_str, peaks_chunk, done_cols, total_cols
    finished = pyqtSignal(int, str, list, int, int, int, int)  # gen_id, path_str, peaks, duration_ms, columns, size, mtime
    error = pyqtSignal(int, str, str)  # gen_id, path_str, message

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
            CHUNK = 100  # columns per emission
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

# ---------- Waveform view (async + cached + live progress + draggable marker) ----------
class WaveformView(QWidget):
    markerMoved = pyqtSignal(int)    # ms while dragging
    markerReleased = pyqtSignal(int) # ms on release

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(140)
        self._peaks: Optional[List[Tuple[float, float]]] = None
        self._peaks_loading: List[Tuple[float, float]] = []
        self._duration_ms: int = 0
        self._pixmap: Optional[QPixmap] = None
        self._pixmap_w: int = 0
        self._bg = QColor("#101114"); self._axis = QColor("#2a2c31")
        self._wave = QColor("#58a6ff"); self._playhead = QColor("#ff5555")
        self._message_color = QColor("#8a8f98")
        self._marker_color = QColor("#00cc66")
        self._player: Optional[QMediaPlayer] = None

        self._state: str = "empty"   # empty|loading|ready|error
        self._msg: str = ""
        self._path: Optional[Path] = None
        self._total_cols: int = 0
        self._done_cols: int = 0

        # Annotation marker state
        self._marker_ms: Optional[int] = None
        self._dragging_marker: bool = False
        self._drag_tolerance_px: int = 8

        # Generation IDs & bookkeeping
        self._gen_id_counter: int = 0
        self._active_gen_id: int = -1
        self._threads: List[QThread] = []              # keep refs to threads
        self._workers: Dict[int, WaveformWorker] = {}  # keep refs to workers (prevents GC)

    def bind_player(self, player: QMediaPlayer):
        self._player = player
        player.positionChanged.connect(lambda _: self.update())

    def clear(self):
        self._peaks = None
        self._peaks_loading = []
        self._duration_ms = 0
        self._pixmap = None
        self._state = "empty"
        self._msg = ""
        self._path = None
        self._total_cols = 0
        self._done_cols = 0
        self._marker_ms = None
        self.update()

    # ----- marker helpers -----
    def set_marker_ms(self, ms: Optional[int]):
        self._marker_ms = ms if (ms is None or ms >= 0) else 0
        self.update()

    def _ms_to_x(self, ms: int) -> int:
        if self._duration_ms <= 0: return 0
        return int((ms / self._duration_ms) * max(1, self.width()))

    def _x_to_ms(self, x: int) -> int:
        W = max(1, self.width())
        x = max(0, min(W, x))
        return int((x / W) * max(1, self._duration_ms))

    # ----- main API -----
    def set_audio_file(self, path: Optional[Path]):
        """Set file; if cache miss/stale, start a fresh background build every time."""
        if path is None:
            self.clear(); return

        # Reset view state for the new file
        self._path = path
        self._pixmap = None; self._pixmap_w = 0
        self._peaks = None; self._peaks_loading = []
        self._total_cols = WAVEFORM_COLUMNS; self._done_cols = 0
        self._marker_ms = None

        # Try cache first
        cache = load_waveform_cache(path.parent)
        entry = cache["files"].get(path.name)
        size, mtime = file_signature(path)
        if entry and entry.get("columns") == WAVEFORM_COLUMNS and \
           int(entry.get("size", 0)) == size and int(entry.get("mtime", 0)) == mtime and \
           isinstance(entry.get("peaks"), list) and isinstance(entry.get("duration_ms"), int):
            self._peaks = [(float(mn), float(mx)) for mn, mx in entry["peaks"]]
            self._duration_ms = int(entry["duration_ms"])
            self._state = "ready"; self._msg = ""
            self.update()
            return

        # No cache or stale -> start a brand-new worker
        self._state = "loading"; self._msg = "Analyzing waveform…"
        self.update()

        self._active_gen_id = self._gen_id_counter = (self._gen_id_counter + 1) % (1 << 31)
        self._start_worker(self._active_gen_id, path)

    def _start_worker(self, gen_id: int, path: Path):
        thread = QThread(self)
        worker = WaveformWorker(gen_id, str(path), WAVEFORM_COLUMNS)
        worker.moveToThread(thread)
        worker.setObjectName(f"WaveformWorker-{gen_id}")

        # Keep strong refs so the worker isn't GC'd mid-run
        self._threads.append(thread)
        self._workers[gen_id] = worker

        thread.started.connect(worker.run)
        worker.progress.connect(self._on_worker_progress)
        worker.finished.connect(self._on_worker_finished)
        worker.error.connect(self._on_worker_error)

        # Cleanup: when thread finishes, drop refs
        def _cleanup():
            worker.deleteLater()
            if thread in self._threads: self._threads.remove(thread)
            self._workers.pop(gen_id, None)
        worker.finished.connect(_cleanup)
        thread.finished.connect(_cleanup)
        thread.finished.connect(thread.deleteLater)

        thread.start()

    # Signal handlers — ignore anything that doesn't match the active gen_id
    def _on_worker_progress(self, gen_id: int, path_str: str, new_chunk: list, done_cols: int, total_cols: int):
        if gen_id != self._active_gen_id or not self._path or str(self._path) != path_str:
            return
        for pair in new_chunk:
            try:
                a, b = pair
            except Exception:
                continue
            self._peaks_loading.append((float(a), float(b)))

        self._total_cols = max(1, int(total_cols))
        self._done_cols = max(0, min(int(done_cols), self._total_cols))
        if self._done_cols > 0:
            pct = int(round(100.0 * self._done_cols / self._total_cols))
            self._msg = f"Analyzing waveform… {min(pct, 99)}%"
        else:
            self._msg = "Analyzing waveform…"
        self._pixmap = None
        self.update()

    def _on_worker_finished(self, gen_id: int, path_str: str, peaks: list, duration_ms: int, columns: int, size: int, mtime: int):
        if gen_id != self._active_gen_id or not self._path or str(self._path) != path_str:
            return
        self._peaks = [(float(mn), float(mx)) for mn, mx in peaks]
        self._duration_ms = int(duration_ms)
        self._state = "ready"; self._msg = ""
        # Cache
        dirpath = self._path.parent
        cache = load_waveform_cache(dirpath)
        cache["files"][self._path.name] = {
            "columns": int(columns),
            "size": int(size),
            "mtime": int(mtime),
            "duration_ms": int(duration_ms),
            "peaks": self._peaks,
        }
        save_waveform_cache(dirpath, cache)
        self._pixmap = None
        self.update()

    def _on_worker_error(self, gen_id: int, path_str: str, message: str):
        if gen_id != self._active_gen_id or not self._path or str(self._path) != path_str:
            return
        self._peaks = None
        self._duration_ms = 0
        self._state = "error"
        self._msg = "No waveform (MP3 needs FFmpeg installed)" if "No MP3 decoder" in message else "Waveform unavailable"
        self._pixmap = None
        self.update()

    # ---- painting & interaction ----
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.width() != self._pixmap_w: self._pixmap = None

    def _ensure_pixmap(self):
        if self._pixmap is not None and self._pixmap_w == self.width(): return
        W = max(1, self.width()); H = max(1, self.height())
        pm = QPixmap(W, H); pm.fill(self._bg)
        p = QPainter(pm)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        mid = H // 2
        pen_axis = QPen(self._axis); pen_axis.setWidth(1)
        p.setPen(pen_axis); p.drawLine(0, mid, W, mid)

        if self._state == "ready" and self._peaks:
            pen_wave = QPen(self._wave); pen_wave.setWidth(1)
            p.setPen(pen_wave)
            draw_peaks = resample_peaks(self._peaks, W)
            for x, (mn, mx) in enumerate(draw_peaks):
                y1 = int(mid - mn * (H/2-2)); y2 = int(mid - mx * (H/2-2))
                if y1 > y2: y1, y2 = y2, y1
                p.drawLine(x, y1, x, y2)
        elif self._state == "loading":
            if self._peaks_loading:
                pen_wave = QPen(self._wave); pen_wave.setWidth(1)
                p.setPen(pen_wave)
                partial = resample_peaks(self._peaks_loading, min(W, max(1, self._done_cols)))
                draw_peaks = resample_peaks(partial, W)
                for x, (mn, mx) in enumerate(draw_peaks):
                    y1 = int(mid - mn * (H/2-2)); y2 = int(mid - mx * (H/2-2))
                    if y1 > y2: y1, y2 = y2, y1
                    p.drawLine(x, y1, x, y2)
            p.setPen(self._message_color)
            p.drawText(QRect(0, 0, W, H), Qt.AlignmentFlag.AlignCenter, self._msg or "Analyzing waveform…")
        else:
            p.setPen(self._message_color)
            p.drawText(QRect(0, 0, W, H), Qt.AlignmentFlag.AlignCenter, self._msg or "No waveform")

        p.end()
        self._pixmap = pm; self._pixmap_w = W

    def paintEvent(self, event):
        self._ensure_pixmap()
        painter = QPainter(self)
        if self._pixmap: painter.drawPixmap(0, 0, self._pixmap)
        # playhead (red)
        if self._player and self._duration_ms > 0:
            pos = self._player.position()
            x = int((pos / self._duration_ms) * max(1, self.width()))
            pen = QPen(self._playhead); pen.setWidth(2)
            painter.setPen(pen); painter.drawLine(x, 0, x, self.height())
        # selected annotation marker (green)
        if self._marker_ms is not None and self._duration_ms > 0:
            x = self._ms_to_x(self._marker_ms)
            pen = QPen(self._marker_color); pen.setWidth(3)
            painter.setPen(pen); painter.drawLine(x, 0, x, self.height())
        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._duration_ms > 0:
            x = int(event.position().x())
            # If clicking near the marker, begin dragging
            if self._marker_ms is not None:
                mx = self._ms_to_x(self._marker_ms)
                if abs(x - mx) <= self._drag_tolerance_px:
                    self._dragging_marker = True
                    event.accept(); return
            # Otherwise, it’s a seek
            if self._player:
                ms = self._x_to_ms(x); self._player.setPosition(ms)
                self.update(); event.accept(); return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging_marker and self._duration_ms > 0:
            x = int(event.position().x())
            new_ms = self._x_to_ms(x)
            self._marker_ms = new_ms
            self.markerMoved.emit(new_ms)
            self.update()
            event.accept(); return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._dragging_marker and self._duration_ms > 0:
            self._dragging_marker = False
            self.markerReleased.emit(self._marker_ms or 0)
            event.accept(); return
        super().mouseReleaseEvent(event)

# ---------- Main window ----------
APP_ICON_NAME = "app_icon.png"

class AudioBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self._apply_app_icon()

        self.settings = QSettings(APP_ORG, APP_NAME)
        self.root_path: Path = self._load_or_ask_root()
        self.current_audio_file: Optional[Path] = None
        self.pending_note_start_ms: Optional[int] = None
        self._programmatic_selection = False  # suppress auto-switch when we change selection via code
        self._uid_counter: int = 1           # for stable note IDs across sessions

        # Media
        self.audio_output = QAudioOutput()
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)
        self.player.errorOccurred.connect(self._on_media_error)
        self.player.mediaStatusChanged.connect(self._on_media_status)

        # Stores
        self.provided_names: Dict[str, str] = {}
        # notes_by_file: fname -> list of {uid:int, ms:int, text:str, important:bool}
        self.notes_by_file: Dict[str, List[Dict]] = {}
        self.file_general: Dict[str, str] = {}
        self.folder_notes: str = ""

        # UI
        self._init_ui()

        # Load metadata
        self._load_names()
        self._load_notes()
        self._ensure_uids()

        # Populate
        self._refresh_right_table()
        self._load_annotations_for_current()
        self._update_folder_notes_ui()
        self._refresh_important_table()

        # Selection & timers
        self.tree.selectionModel().selectionChanged.connect(self._on_tree_selection_changed)
        self.slider_sync = QTimer(self); self.slider_sync.setInterval(200)
        self.slider_sync.timeout.connect(self._sync_slider)
        self.player.positionChanged.connect(lambda _: self._sync_slider())
        self.player.durationChanged.connect(self._on_duration_changed)

        # Waveform marker signals
        self.waveform.markerMoved.connect(self._on_marker_moved)
        self.waveform.markerReleased.connect(self._on_marker_released)

        # Restore toggles
        self._restore_toggles()

        self.statusBar().showMessage(f"Root: {self.root_path}")

    # ----- Icon handling -----
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

    # ---------- Settings & metadata ----------
    def _load_or_ask_root(self) -> Path:
        stored = self.settings.value(SETTINGS_KEY_ROOT, "", type=str)
        if stored and Path(stored).exists(): return Path(stored)
        dlg = QFileDialog(self, "Select your audio folder")
        dlg.setFileMode(QFileDialog.FileMode.Directory)
        dlg.setOption(QFileDialog.Option.ShowDirsOnly, True)
        if dlg.exec():
            p = Path(dlg.selectedFiles()[0]); self.settings.setValue(SETTINGS_KEY_ROOT, str(p)); return p
        home = Path.home(); self.settings.setValue(SETTINGS_KEY_ROOT, str(home)); return home

    def _save_root(self, p: Path):
        self.root_path = p; self.settings.setValue(SETTINGS_KEY_ROOT, str(p))
        self.statusBar().showMessage(f"Root: {self.root_path}")
        self.model.setRootPath(str(self.root_path))
        self._programmatic_selection = True
        try:
            self.tree.setRootIndex(self.model.index(str(self.root_path)))
        finally:
            QTimer.singleShot(0, lambda: setattr(self, "_programmatic_selection", False))
        self._load_names(); self._load_notes(); self._ensure_uids()
        self._refresh_right_table(); self.current_audio_file = None
        self._load_annotations_for_current()
        self._update_folder_notes_ui()
        self._refresh_important_table()
        self.waveform.clear()

    def _names_json_path(self) -> Path: return self.root_path / NAMES_JSON
    def _notes_json_path(self) -> Path: return self.root_path / NOTES_JSON

    def _load_names(self):
        self.provided_names = {}
        nj = self._names_json_path()
        try:
            if nj.exists():
                with open(nj, "r", encoding="utf-8") as f:
                    self.provided_names = {k: str(v) for k, v in json.load(f).items()}
        except Exception:
            self.provided_names = {}

    def _save_names(self):
        try:
            with open(self._names_json_path(), "w", encoding="utf-8") as f:
                json.dump(self.provided_names, f, indent=2, ensure_ascii=False)
        except Exception as e:
            QMessageBox.warning(self, "Save Names Failed", f"Couldn't save provided names:\n{e}")

    def _load_notes(self):
        """Load folder notes, per-file general, and per-file timestamped notes (v1/v2 compatible)."""
        self.notes_by_file = {}
        self.file_general = {}
        self.folder_notes = ""
        pj = self._notes_json_path()
        try:
            if pj.exists():
                with open(pj, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # v2 format
                if isinstance(data, dict) and "files" in data:
                    self.folder_notes = str(data.get("folder_notes", "") or "")
                    files = data.get("files", {}) or {}
                    for fname, meta in files.items():
                        if not isinstance(meta, dict): continue
                        self.file_general[fname] = str(meta.get("general", "") or "")
                        nlist = meta.get("notes", []) or []
                        clean = []
                        for n in nlist:
                            if not isinstance(n, dict): continue
                            clean.append({
                                "uid": int(n.get("uid", 0) or 0),
                                "ms": int(n.get("ms", 0)),
                                "text": str(n.get("text", "")),
                                "important": bool(n.get("important", False))
                            })
                        self.notes_by_file[fname] = clean
                # v1 format
                elif isinstance(data, dict) and "notes" in data:
                    m = data.get("notes", {}) or {}
                    for fname, nlist in m.items():
                        clean = []
                        for n in (nlist or []):
                            if not isinstance(n, dict): continue
                            clean.append({
                                "uid": 0,
                                "ms": int(n.get("ms", 0)),
                                "text": str(n.get("text", "")),
                                "important": False
                            })
                        self.notes_by_file[fname] = clean
        except Exception:
            self.notes_by_file = {}
            self.file_general = {}
            self.folder_notes = ""

    def _ensure_uids(self):
        # assign unique IDs to any note lacking one, and bump counter above max
        mx = self._uid_counter
        for lst in self.notes_by_file.values():
            for n in lst:
                if int(n.get("uid", 0)) <= 0:
                    n["uid"] = mx; mx += 1
                else:
                    if n["uid"] >= mx: mx = n["uid"] + 1
        self._uid_counter = mx

    def _save_notes(self):
        """Save in v2 format; backward compatible loader handles older files."""
        try:
            all_files = set(self.notes_by_file.keys()) | set(self.file_general.keys())
            files_payload = {}
            for fname in sorted(all_files):
                files_payload[fname] = {
                    "general": self.file_general.get(fname, ""),
                    "notes": self.notes_by_file.get(fname, []),
                }
            payload = {
                "version": 2,
                "updated": datetime.now().isoformat(timespec="seconds"),
                "folder_notes": self.folder_notes,
                "files": files_payload,
            }
            with open(self._notes_json_path(), "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
        except Exception as e:
            QMessageBox.warning(self, "Save Notes Failed", f"Couldn't save annotation notes:\n{e}")

    # ---------- UI ----------
    def _init_ui(self):
        self.resize(1320, 860); self.setStatusBar(QStatusBar(self))
        tb = QToolBar("Main"); self.addToolBar(tb)

        act_change_root = QAction("Change Folder…", self); act_change_root.triggered.connect(self._change_root_clicked); tb.addAction(act_change_root)
        act_up = QAction("Up", self); act_up.setShortcut(QKeySequence("Alt+Up")); act_up.triggered.connect(self._go_up); tb.addAction(act_up)
        tb.addSeparator()
        self.rename_action = QAction("Batch Rename (##_ProvidedName)", self); self.rename_action.triggered.connect(self._batch_rename); tb.addAction(self.rename_action)
        self.export_action = QAction("Export Annotations…", self); self.export_action.triggered.connect(self._export_annotations); tb.addAction(self.export_action)
        tb.addSeparator()

        # Auto-switch to Annotations toggle (toolbar checkbox)
        self.auto_switch_cb = QCheckBox("Auto-switch to Annotations")
        wa = QWidgetAction(self); wa.setDefaultWidget(self.auto_switch_cb); tb.addAction(wa)

        splitter = QSplitter(self); self.setCentralWidget(splitter)

        # Tree (left) - filtered to folders + WAV/MP3 only
        self.model = QFileSystemModel(self)
        self.model.setResolveSymlinks(True); self.model.setReadOnly(True)
        self.model.setFilter(QDir.Filter.AllDirs | QDir.Filter.NoDotAndDotDot | QDir.Filter.Drives | QDir.Filter.Files)
        self.model.setNameFilters(["*.wav", "*.wave", "*.mp3"])
        self.model.setNameFilterDisables(False)  # hide non-matching files
        self.model.setRootPath(str(self.root_path))

        self.tree = QTreeView(); self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(str(self.root_path)))
        self.tree.setColumnWidth(0, 360); self.tree.setAlternatingRowColors(True)
        self.tree.setSortingEnabled(True); self.tree.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.tree.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tree.doubleClicked.connect(self._on_tree_double_clicked)
        self.tree.activated.connect(self._on_tree_activated)
        splitter.addWidget(self.tree)

        # Right panel (player + tabs)
        right = QWidget(); splitter.addWidget(right)
        splitter.setStretchFactor(0, 2); splitter.setStretchFactor(1, 3)
        right_layout = QVBoxLayout(right)

        # Player controls
        player_bar = QHBoxLayout()
        self.play_pause_btn = QPushButton(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay), ""); self.play_pause_btn.setEnabled(False)
        self.play_pause_btn.clicked.connect(self._toggle_play_pause); player_bar.addWidget(self.play_pause_btn)

        self.position_slider = SeekSlider(Qt.Orientation.Horizontal)  # click-to-seek
        self.position_slider.setEnabled(False)
        self.position_slider.sliderPressed.connect(lambda: self._user_scrubbing(True))
        self.position_slider.sliderReleased.connect(lambda: self._user_scrubbing(False))
        self.position_slider.sliderMoved.connect(self._on_slider_moved)
        self.position_slider.clickedValue.connect(self._on_slider_clicked_value)
        player_bar.addWidget(self.position_slider, 1)

        self.time_label = QLabel("0:00 / 0:00"); player_bar.addWidget(self.time_label)

        # Auto-progress checkbox
        self.auto_progress_cb = QCheckBox("Auto-progress")
        self.auto_progress_cb.setToolTip("When enabled, automatically play the next file when the current one ends.")
        player_bar.addWidget(self.auto_progress_cb)

        right_layout.addLayout(player_bar)

        self.now_playing = QLabel("No selection"); self.now_playing.setStyleSheet("color: #666;"); right_layout.addWidget(self.now_playing)

        # Tabs
        self.tabs = QTabWidget(); right_layout.addWidget(self.tabs, 1)
        self.tabs.setDocumentMode(True)
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabs.setMovable(True)
        self.tabs.tabBar().tabMoved.connect(self._on_tab_moved)

        # ---- Build tabs (default order: Folder Notes, Library, Annotations) ----
        # Folder Notes tab
        self.folder_tab = QWidget(); folder_layout = QVBoxLayout(self.folder_tab)
        self.folder_label = QLabel("Notes for current folder:")
        self.folder_notes_edit = QPlainTextEdit()
        self.folder_notes_edit.setPlaceholderText("Write notes about this folder/collection. Saved automatically.")
        self.folder_notes_edit.textChanged.connect(self._on_folder_notes_changed)
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(self.folder_notes_edit, 1)

        # Important annotations table
        self.imp_label = QLabel("Important annotations in this folder:")
        folder_layout.addWidget(self.imp_label)
        self.imp_table = QTableWidget(0, 3)
        self.imp_table.setHorizontalHeaderLabels(["File", "Time", "Note"])
        ih = self.imp_table.horizontalHeader()
        ih.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        ih.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        ih.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.imp_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.imp_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.imp_table.itemDoubleClicked.connect(self._on_important_double_clicked)
        folder_layout.addWidget(self.imp_table, 1)

        # Library tab
        self.lib_tab = QWidget(); lib_layout = QVBoxLayout(self.lib_tab)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["File", "Created", "Provided Name (editable)"])
        hh = self.table.horizontalHeader(); hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents); hh.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.SelectedClicked)
        self.table.itemChanged.connect(self._on_table_item_changed); lib_layout.addWidget(self.table, 1)
        self.table.itemSelectionChanged.connect(self._stop_if_no_file_selected)

        # Annotations tab
        self.ann_tab = QWidget(); ann_layout = QVBoxLayout(self.ann_tab)

        # Waveform (async + cached + live progress + draggable marker)
        self.waveform = WaveformView()
        self.waveform.bind_player(self.player)
        ann_layout.addWidget(self.waveform)

        # New note input
        top_controls = QHBoxLayout()
        self.note_input = QLineEdit()
        self.note_input.setPlaceholderText("Type to create a note at captured time; press Enter to add")
        self.note_input.textEdited.connect(self._on_note_text_edited)
        self.note_input.textChanged.connect(self._on_note_text_changed_clear_capture)
        self.note_input.returnPressed.connect(self._on_note_return_pressed)
        top_controls.addWidget(QLabel("New note:"))
        top_controls.addWidget(self.note_input, 1)
        ann_layout.addLayout(top_controls)

        # General (per-song) paragraph editor
        self.general_label = QLabel("Song overview:")
        self.general_edit = QPlainTextEdit()
        self.general_edit.setPlaceholderText("Write a general description/notes for this song (saved automatically).")
        self.general_edit.textChanged.connect(self._on_general_changed)
        ann_layout.addWidget(self.general_label)
        ann_layout.addWidget(self.general_edit, 1)

        # Annotation table (Time, Note, Important)
        self.annotation_table = QTableWidget(0, 3)
        self.annotation_table.setHorizontalHeaderLabels(["Time", "Note", "Important"])
        ah = self.annotation_table.horizontalHeader()
        ah.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        ah.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        ah.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.annotation_table.verticalHeader().setVisible(False)
        # Single-click edits; double-click jumps
        self.annotation_table.setEditTriggers(QAbstractItemView.EditTrigger.SelectedClicked | QAbstractItemView.EditTrigger.EditKeyPressed)
        self.annotation_table.itemDoubleClicked.connect(self._on_annotation_double_clicked)
        self.annotation_table.itemChanged.connect(self._on_annotation_item_changed)
        self.annotation_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.annotation_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.annotation_table.selectionModel().selectionChanged.connect(self._on_annotation_selection_changed)
        ann_layout.addWidget(self.annotation_table, 2)

        # Bottom: Delete selected
        bottom_controls = QHBoxLayout()
        self.delete_note_btn = QPushButton("Delete Selected"); self.delete_note_btn.clicked.connect(self._delete_selected_annotations)
        bottom_controls.addStretch(1); bottom_controls.addWidget(self.delete_note_btn)
        ann_layout.addLayout(bottom_controls)

        # Add tabs in default order
        self.tabs.addTab(self.folder_tab, "Folder Notes")
        self.tabs.addTab(self.lib_tab, "Library")
        self.tabs.addTab(self.ann_tab, "Annotations")

        # Restore saved tab order
        self._restore_tab_order()

        if "Fusion" in QStyleFactory.keys(): QApplication.instance().setStyle("Fusion")

        # Debounce timers for autosave text areas
        self._general_save_timer = QTimer(self); self._general_save_timer.setSingleShot(True); self._general_save_timer.timeout.connect(self._save_notes)
        self._folder_save_timer = QTimer(self); self._folder_save_timer.setSingleShot(True); self._folder_save_timer.timeout.connect(self._save_notes)

    # ----- Tab order persistence -----
    def _tab_index_by_name(self, name: str) -> int:
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == name:
                return i
        return -1

    def _on_tab_moved(self, from_idx: int, to_idx: int):
        order = [self.tabs.tabText(i) for i in range(self.tabs.count())]
        self.settings.setValue(SETTINGS_KEY_TABS_ORDER, "|".join(order))

    def _restore_tab_order(self):
        saved = self.settings.value(SETTINGS_KEY_TABS_ORDER, "", type=str) or ""
        if not saved:
            return
        desired = [s for s in saved.split("|") if s in {"Folder Notes", "Library", "Annotations"}]
        if not desired:
            return
        for target, name in enumerate(desired):
            idx = self._tab_index_by_name(name)
            if idx == -1: continue
            if idx != target:
                self.tabs.tabBar().moveTab(idx, target)

    # ----- Toggle persistence -----
    def _restore_toggles(self):
        ap = self.settings.value(SETTINGS_KEY_AUTOPROGRESS, None)
        if ap is not None:
            try: self.auto_progress_cb.setChecked(bool(int(ap)) if isinstance(ap, str) else bool(ap))
            except Exception: pass
        else:
            self.auto_progress_cb.setChecked(False)

        asw = self.settings.value(SETTINGS_KEY_AUTOSWITCH, None)
        if asw is not None:
            try: self.auto_switch_cb.setChecked(bool(int(asw)) if isinstance(asw, str) else bool(asw))
            except Exception: pass
        else:
            self.auto_switch_cb.setChecked(True)  # default enabled

        # save on change
        self.auto_progress_cb.stateChanged.connect(lambda _:
            self.settings.setValue(SETTINGS_KEY_AUTOPROGRESS, int(self.auto_progress_cb.isChecked())))
        self.auto_switch_cb.stateChanged.connect(lambda _:
            self.settings.setValue(SETTINGS_KEY_AUTOSWITCH, int(self.auto_switch_cb.isChecked())))

    # ---------- Tree interactions ----------
    def _on_tree_double_clicked(self, idx: QModelIndex):
        """Double-click:
           - Folder: open it as root.
           - Audio file: if parent != root, switch to parent and select it (no forced restart),
             then show Annotations tab.
        """
        fi = self.model.fileInfo(idx)
        if fi.isDir():
            self._save_root(Path(fi.absoluteFilePath())); return

        if f".{fi.suffix().lower()}" in AUDIO_EXTS:
            path = Path(fi.absoluteFilePath()); parent = path.parent
            try: parent_res = parent.resolve()
            except Exception: parent_res = parent
            try: root_res = self.root_path.resolve()
            except Exception: root_res = self.root_path

            if parent_res != root_res:
                self._save_root(parent)
                idx_new = self.model.index(str(path))
                if idx_new.isValid():
                    self._programmatic_selection = True
                    try:
                        self.tree.setCurrentIndex(idx_new)
                    finally:
                        QTimer.singleShot(0, lambda: setattr(self, "_programmatic_selection", False))
                if not (self.current_audio_file and self.current_audio_file.resolve() == path.resolve()):
                    self._play_file(path)
            # Switch to annotations tab (double-click implies user wants it)
            self.tabs.setCurrentIndex(self._tab_index_by_name("Annotations"))

    def _on_tree_activated(self, idx: QModelIndex):
        fi = self.model.fileInfo(idx)
        if fi.isDir(): self._save_root(Path(fi.absoluteFilePath()))

    def _go_up(self):
        parent = self.root_path.parent
        if parent.exists() and parent != self.root_path: self._save_root(parent)

    def _change_root_clicked(self):
        d = QFileDialog.getExistingDirectory(self, "Choose Audio Folder", str(self.root_path))
        if d: self._save_root(Path(d))

    # ---------- Selection / Playback ----------
    def _on_tree_selection_changed(self, _sel: QItemSelection, _desel: QItemSelection):
        indexes = self.tree.selectionModel().selectedIndexes()
        idx = next((i for i in indexes if i.column() == 0), None)
        if not idx:
            self._stop_playback(); self.now_playing.setText("No selection"); self.current_audio_file = None
            self._load_annotations_for_current(); return
        fi = self.model.fileInfo(idx)
        if fi.isDir():
            self._stop_playback(); self.now_playing.setText(f"Folder selected: {fi.fileName()}"); self.current_audio_file = None
            self._load_annotations_for_current(); return
        if f".{fi.suffix().lower()}" in AUDIO_EXTS:
            path = Path(fi.absoluteFilePath())
            # Auto-switch to Annotations on user click (not when we programmatically change selection)
            if not self._programmatic_selection and self.auto_switch_cb.isChecked():
                self.tabs.setCurrentIndex(self._tab_index_by_name("Annotations"))
            # Only play if different from current
            if self.current_audio_file and self.current_audio_file.resolve() == path.resolve():
                return
            self._play_file(path)
        else:
            self._stop_playback(); self.now_playing.setText(fi.fileName()); self.current_audio_file = None
            self._load_annotations_for_current()

    def _play_file(self, path: Path):
        if self.current_audio_file and self.current_audio_file.resolve() == path.resolve():
            return
        self.player.stop(); self.player.setSource(QUrl.fromLocalFile(str(path)))
        self.audio_output.setVolume(0.9); self.player.play()
        self.play_pause_btn.setEnabled(True); self.position_slider.setEnabled(True); self.slider_sync.start()
        self.now_playing.setText(f"Playing: {path.name}")
        self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        self.current_audio_file = path; self.pending_note_start_ms = None
        self._load_annotations_for_current()
        try:
            self.waveform.set_audio_file(path)  # async & cached
        except Exception:
            self.waveform.clear()
        # Reflect selection in tree (useful for autoprogress) but mark as programmatic
        try:
            idx = self.model.index(str(path))
            if idx.isValid():
                self._programmatic_selection = True
                try:
                    self.tree.setCurrentIndex(idx)
                finally:
                    QTimer.singleShot(0, lambda: setattr(self, "_programmatic_selection", False))
        except Exception:
            pass

    def _stop_playback(self):
        if self.player.playbackState() != QMediaPlayer.PlaybackState.StoppedState: self.player.stop()
        self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_pause_btn.setEnabled(False); self.position_slider.setEnabled(False); self.slider_sync.stop()
        self.position_slider.setValue(0); self.time_label.setText("0:00 / 0:00"); self.pending_note_start_ms = None
        self.waveform.set_marker_ms(None)

    def _toggle_play_pause(self):
        st = self.player.playbackState()
        if st == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause(); self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        else:
            self.player.play(); self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))

    def _play_next_file(self):
        """Play next audio file in the current folder (by name ascending)."""
        if not self.current_audio_file: return
        files = [p for p in self._list_audio_in_root()]
        if not files: return
        try:
            files.sort(key=lambda p: p.name.lower())
            cur = self.current_audio_file.resolve()
            for i, p in enumerate(files):
                if p.resolve() == cur:
                    if i + 1 < len(files):
                        self._play_file(files[i+1])
                    break
        except Exception:
            pass

    # ---------- Slider / time ----------
    _user_is_scrubbing = False
    def _on_duration_changed(self, dur: int): self.position_slider.setRange(0, max(0, dur)); self._sync_slider()
    def _sync_slider(self):
        if self._user_is_scrubbing: return
        pos = self.player.position(); dur = max(1, self.player.duration())
        self.position_slider.blockSignals(True); self.position_slider.setValue(pos); self.position_slider.blockSignals(False)
        self.time_label.setText(f"{human_time_ms(pos)} / {human_time_ms(dur)}")
    def _user_scrubbing(self, on: bool): self._user_is_scrubbing = on
    def _on_slider_moved(self, value: int): self.player.setPosition(value)
    def _on_slider_clicked_value(self, value: int):
        if not self.position_slider.isEnabled(): return
        was = self._user_is_scrubbing; self._user_is_scrubbing = True
        try:
            self.player.setPosition(value); self.position_slider.setValue(value); self._sync_slider()
        finally:
            self._user_is_scrubbing = was

    # ---------- Library table ----------
    def _list_audio_in_root(self) -> List[Path]:
        if not self.root_path.exists(): return []
        return [p for p in sorted(self.root_path.iterdir()) if p.is_file() and p.suffix.lower() in AUDIO_EXTS]

    def _refresh_right_table(self):
        files = self._list_audio_in_root()
        self.table.blockSignals(True); self.table.setRowCount(len(files))
        for row, p in enumerate(files):
            try: ctime = os.path.getctime(p)
            except Exception: ctime = p.stat().st_mtime
            item_file = QTableWidgetItem(p.name); item_file.setFlags(item_file.flags() ^ Qt.ItemFlag.ItemIsEditable)
            item_created = QTableWidgetItem(datetime.fromtimestamp(ctime).strftime("%Y-%m-%d %H:%M:%S"))
            item_created.setData(Qt.ItemDataRole.UserRole, int(ctime)); item_created.setFlags(item_created.flags() ^ Qt.ItemFlag.ItemIsEditable)
            item_name = QTableWidgetItem(self.provided_names.get(p.name, "")); item_name.setToolTip("Double-click to edit your Provided Name")
            self.table.setItem(row, 0, item_file); self.table.setItem(row, 1, item_created); self.table.setItem(row, 2, item_name)
        self.table.blockSignals(False)

    def _on_table_item_changed(self, item: QTableWidgetItem):
        if item.column() != 2: return
        row = item.row(); file_item = self.table.item(row, 0)
        if not file_item: return
        self.provided_names[file_item.text()] = sanitize(item.text()); self._save_names()

    def _stop_if_no_file_selected(self):
        indexes = self.tree.selectionModel().selectedIndexes()
        idx = next((i for i in indexes if i.column() == 0), None)
        if not idx: self._stop_playback(); return
        fi = self.model.fileInfo(idx)
        if fi.isDir() or f".{fi.suffix().lower()}" not in AUDIO_EXTS: self._stop_playback()

    # ---------- Annotations (file) ----------
    def _load_annotations_for_current(self):
        self.general_edit.blockSignals(True); self.general_edit.clear()
        self.annotation_table.blockSignals(True); self.annotation_table.setRowCount(0)
        self.waveform.set_marker_ms(None)

        if not self.current_audio_file:
            self.annotation_table.blockSignals(False)
            self.general_edit.blockSignals(False)
            self._refresh_important_table()
            return

        fname = self.current_audio_file.name
        self.general_edit.setPlainText(self.file_general.get(fname, ""))

        # rows sorted by ms
        rows = sorted(self.notes_by_file.get(fname, []), key=lambda r: int(r.get("ms", 0)))
        for entry in rows:
            self._append_annotation_row(entry)

        self.annotation_table.blockSignals(False)
        self.general_edit.blockSignals(False)
        self._refresh_important_table()

    def _append_annotation_row(self, entry: Dict):
        ms = int(entry.get("ms", 0))
        text = str(entry.get("text", ""))
        important = bool(entry.get("important", False))
        uid = int(entry.get("uid", 0))

        r = self.annotation_table.rowCount(); self.annotation_table.insertRow(r)

        t = QTableWidgetItem(human_time_ms(ms))
        # Time IS editable now (so you can adjust)
        t.setData(Qt.ItemDataRole.UserRole, int(ms))
        t.setData(Qt.ItemDataRole.UserRole + 1, int(uid))  # store uid
        self.annotation_table.setItem(r, 0, t)

        n = QTableWidgetItem(text)
        n.setData(Qt.ItemDataRole.UserRole + 1, int(uid))
        self.annotation_table.setItem(r, 1, n)

        imp = QTableWidgetItem()
        imp.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsUserCheckable)
        imp.setCheckState(Qt.CheckState.Checked if important else Qt.CheckState.Unchecked)
        imp.setData(Qt.ItemDataRole.UserRole + 1, int(uid))
        self.annotation_table.setItem(r, 2, imp)

    def _current_file_list(self) -> List[Dict]:
        if not self.current_audio_file: return []
        return self.notes_by_file.setdefault(self.current_audio_file.name, [])

    def _find_entry_by_uid(self, uid: int) -> Optional[Dict]:
        for e in self._current_file_list():
            if int(e.get("uid", -1)) == uid:
                return e
        return None

    def _resort_and_rebuild_table_preserving_selection(self, keep_uid: Optional[int] = None):
        if not self.current_audio_file: return
        fname = self.current_audio_file.name
        # sort in-place
        lst = self.notes_by_file.setdefault(fname, [])
        lst.sort(key=lambda e: int(e.get("ms", 0)))
        # rebuild
        self._load_annotations_for_current()
        if keep_uid is not None:
            # reselect row with same uid
            for row in range(self.annotation_table.rowCount()):
                uid_row = int(self.annotation_table.item(row, 0).data(Qt.ItemDataRole.UserRole + 1))
                if uid_row == keep_uid:
                    self.annotation_table.selectRow(row)
                    # ensure visible
                    self.annotation_table.scrollToItem(self.annotation_table.item(row, 0))
                    break

    def _on_note_text_edited(self, _txt: str):
        # Capture the time at FIRST character typed
        if self.pending_note_start_ms is None:
            self.pending_note_start_ms = int(self.player.position())

    def _on_note_text_changed_clear_capture(self, txt: str):
        if not txt:
            # cleared -> forget captured time until typing resumes
            self.pending_note_start_ms = None

    def _on_note_return_pressed(self):
        txt = self.note_input.text().strip()
        if not txt or not self.current_audio_file:
            self.pending_note_start_ms = None; self.note_input.clear(); return
        ms = self.pending_note_start_ms if self.pending_note_start_ms is not None else int(self.player.position())
        self.pending_note_start_ms = None
        fname = self.current_audio_file.name
        # add new entry with uid
        uid = self._uid_counter; self._uid_counter += 1
        entry = {"uid": uid, "ms": int(ms), "text": txt, "important": False}
        self.notes_by_file.setdefault(fname, []).append(entry)
        # rebuild sorted
        self._resort_and_rebuild_table_preserving_selection(keep_uid=uid)
        # clear input
        self.note_input.clear()
        self._schedule_save_notes()

    def _on_annotation_double_clicked(self, item: QTableWidgetItem):
        # Double-click anywhere on row jumps to that time
        row = item.row()
        titem = self.annotation_table.item(row, 0)
        if not titem: return
        ms = parse_time_to_ms(titem.text())
        if ms is None:
            ms = int(titem.data(Qt.ItemDataRole.UserRole) or 0)
        self.player.setPosition(int(ms))
        # ensure marker shows
        self.waveform.set_marker_ms(int(ms))

    def _on_annotation_item_changed(self, item: QTableWidgetItem):
        # Handle edits: time text (col 0), note text (col 1), important checkbox (col 2)
        if not self.current_audio_file: return
        uid = int(item.data(Qt.ItemDataRole.UserRole + 1) or -1)
        entry = self._find_entry_by_uid(uid)
        if not entry: return

        if item.column() == 0:
            # time edited -> parse
            new_ms = parse_time_to_ms(item.text())
            if new_ms is None:
                # revert display
                item.setText(human_time_ms(int(entry.get("ms", 0))))
                return
            entry["ms"] = int(new_ms)
            item.setData(Qt.ItemDataRole.UserRole, int(new_ms))
            # if currently selected, move marker too
            if self._selected_uid() == uid:
                self.waveform.set_marker_ms(int(new_ms))
            # keep sorted order
            self._resort_and_rebuild_table_preserving_selection(keep_uid=uid)
            self._schedule_save_notes()
            self._refresh_important_table()
            return

        if item.column() == 1:
            entry["text"] = item.text()
            self._schedule_save_notes()
            self._refresh_important_table()
            return

        if item.column() == 2:
            entry["important"] = (item.checkState() == Qt.CheckState.Checked)
            self._schedule_save_notes()
            self._refresh_important_table()
            return

    def _delete_selected_annotations(self):
        if not self.current_audio_file: return
        fname = self.current_audio_file.name
        rows_model = self.notes_by_file.setdefault(fname, [])
        sel_rows = sorted({idx.row() for idx in self.annotation_table.selectionModel().selectedIndexes()}, reverse=True)
        if not sel_rows: return
        sel_uids = []
        for r in sel_rows:
            titem = self.annotation_table.item(r, 0)
            if not titem: continue
            uid = int(titem.data(Qt.ItemDataRole.UserRole + 1) or -1)
            if uid >= 0: sel_uids.append(uid)
        # remove by uid
        rows_model[:] = [e for e in rows_model if int(e.get("uid", -1)) not in set(sel_uids)]
        # rebuild
        self._load_annotations_for_current()
        self._schedule_save_notes()
        self._refresh_important_table()
        self.waveform.set_marker_ms(None)

    # Selection -> marker
    def _selected_uid(self) -> Optional[int]:
        sel = self.annotation_table.selectionModel().selectedRows()
        if not sel: return None
        row = sel[0].row()
        titem = self.annotation_table.item(row, 0)
        return int(titem.data(Qt.ItemDataRole.UserRole + 1)) if titem else None

    def _on_annotation_selection_changed(self, *_):
        uid = self._selected_uid()
        if uid is None:
            self.waveform.set_marker_ms(None); return
        entry = self._find_entry_by_uid(uid)
        if not entry:
            self.waveform.set_marker_ms(None); return
        self.waveform.set_marker_ms(int(entry.get("ms", 0)))

    # Autosave handlers (debounced)
    def _on_general_changed(self):
        if not self.current_audio_file: return
        fname = self.current_audio_file.name
        self.file_general[fname] = self.general_edit.toPlainText()
        self._schedule_save_notes()

    def _on_folder_notes_changed(self):
        self.folder_notes = self.folder_notes_edit.toPlainText()
        self._schedule_save_notes()

    def _schedule_save_notes(self):
        self._general_save_timer.start(600)
        self._folder_save_timer.start(600)

    def _update_folder_notes_ui(self):
        self.folder_label.setText(f"Notes for current folder: {self.root_path.name}")
        self.folder_notes_edit.blockSignals(True)
        self.folder_notes_edit.setPlainText(self.folder_notes or "")
        self.folder_notes_edit.blockSignals(False)

    # ---------- Important annotations summary (Folder tab) ----------
    def _refresh_important_table(self):
        # Build rows from current folder's files only
        rows = []
        parent_name = self.root_path.name
        for fname, notes in self.notes_by_file.items():
            for n in notes:
                if bool(n.get("important", False)):
                    rows.append((fname, int(n.get("ms", 0)), str(n.get("text", "")), int(n.get("uid", 0))))
        rows.sort(key=lambda r: (r[0].lower(), r[1]))  # by file then time

        self.imp_table.setRowCount(0)
        for fname, ms, text, uid in rows:
            r = self.imp_table.rowCount(); self.imp_table.insertRow(r)
            f_item = QTableWidgetItem(f"{parent_name}\\{fname}")
            f_item.setData(Qt.ItemDataRole.UserRole, fname)
            f_item.setData(Qt.ItemDataRole.UserRole + 1, uid)
            t_item = QTableWidgetItem(human_time_ms(ms))
            t_item.setData(Qt.ItemDataRole.UserRole, int(ms))
            n_item = QTableWidgetItem(text)
            self.imp_table.setItem(r, 0, f_item)
            self.imp_table.setItem(r, 1, t_item)
            self.imp_table.setItem(r, 2, n_item)

    def _on_important_double_clicked(self, item: QTableWidgetItem):
        row = item.row()
        f_item = self.imp_table.item(row, 0)
        t_item = self.imp_table.item(row, 1)
        if not f_item or not t_item: return
        fname = str(f_item.data(Qt.ItemDataRole.UserRole))
        ms = int(t_item.data(Qt.ItemDataRole.UserRole) or 0)
        # Jump: select file in tree and play (without restarting if same)
        target = self.root_path / fname
        if target.exists():
            self._play_file(target)
            # Switch to Annotations
            self.tabs.setCurrentIndex(self._tab_index_by_name("Annotations"))
            # Select the note with closest ms (exact uid if available)
            uid = int(f_item.data(Qt.ItemDataRole.UserRole + 1) or -1)
            self._select_annotation_by_uid_or_time(uid, ms)
            self.player.setPosition(int(ms))
            self.waveform.set_marker_ms(int(ms))

    def _select_annotation_by_uid_or_time(self, uid: int, ms: int):
        # Try UID first
        for r in range(self.annotation_table.rowCount()):
            titem = self.annotation_table.item(r, 0)
            if not titem: continue
            row_uid = int(titem.data(Qt.ItemDataRole.UserRole + 1) or -1)
            if uid >= 0 and row_uid == uid:
                self.annotation_table.selectRow(r)
                self.annotation_table.scrollToItem(titem)
                return
        # Fallback by ms (closest)
        closest_row, closest_diff = -1, 999999999
        for r in range(self.annotation_table.rowCount()):
            titem = self.annotation_table.item(r, 0)
            if not titem: continue
            rms = int(titem.data(Qt.ItemDataRole.UserRole) or 0)
            d = abs(rms - ms)
            if d < closest_diff:
                closest_diff = d; closest_row = r
        if closest_row >= 0:
            self.annotation_table.selectRow(closest_row)
            self.annotation_table.scrollToItem(self.annotation_table.item(closest_row, 0))

    # ---------- Waveform marker drag integration ----------
    def _on_marker_moved(self, new_ms: int):
        # Update selected annotation time LIVE (UI only), no resort yet
        uid = self._selected_uid()
        if uid is None: return
        entry = self._find_entry_by_uid(uid)
        if not entry: return
        # Update the visible cell
        row = self._row_for_uid(uid)
        if row is None: return
        titem = self.annotation_table.item(row, 0)
        if titem:
            titem.setText(human_time_ms(new_ms))
            # Store temp ms in the item (so double-click jumps to this)
            titem.setData(Qt.ItemDataRole.UserRole, int(new_ms))

    def _on_marker_released(self, new_ms: int):
        # Commit move -> update model, sort, rebuild, reselect note
        uid = self._selected_uid()
        if uid is None: return
        entry = self._find_entry_by_uid(uid)
        if not entry: return
        entry["ms"] = int(new_ms)
        self._resort_and_rebuild_table_preserving_selection(keep_uid=uid)
        self._schedule_save_notes()
        self._refresh_important_table()

    def _row_for_uid(self, uid: int) -> Optional[int]:
        for r in range(self.annotation_table.rowCount()):
            titem = self.annotation_table.item(r, 0)
            if not titem: continue
            row_uid = int(titem.data(Qt.ItemDataRole.UserRole + 1) or -1)
            if row_uid == uid:
                return r
        return None

    # ---------- Export annotations ----------
    def _export_annotations(self):
        default_path = str((self.root_path / "annotations_export.txt").resolve())
        save_path, _ = QFileDialog.getSaveFileName(self, "Export Annotations", default_path, "Text Files (*.txt);;All Files (*)")
        if not save_path: return
        lines: List[str] = []

        # Folder notes (if any)
        if (self.folder_notes or "").strip():
            lines.append(f"[Folder] {self.root_path}")
            for ln in (self.folder_notes.replace("\r\n", "\n").split("\n")):
                lines.append(ln.rstrip())
            lines.append("")

        # Files grouped; title then overview, then time-stamped notes
        parent_name = self.root_path.name
        for fname in sorted(set(list(self.notes_by_file.keys()) + list(self.file_general.keys()))):
            notes = sorted(self.notes_by_file.get(fname, []), key=lambda n: int(n.get("ms", 0)))
            overview = (self.file_general.get(fname, "") or "").strip()
            if not notes and not overview:
                continue

            # Title only "<ParentFolder>\<FileName>"
            title = f"{parent_name}\\{fname}"
            lines.append(title)

            if overview:
                for ln in overview.replace("\r\n", "\n").split("\n"):
                    lines.append(f"Overview: {ln.rstrip()}")
            for n in notes:
                ts = human_time_ms(int(n.get("ms", 0)))
                txt = str(n.get("text", "")).replace("\n", " ").strip()
                lines.append(f"{ts} {txt}")
            lines.append("")

        try:
            # Force DOS CRLF endings
            out = "\r\n".join(lines).rstrip("\r\n") + "\r\n"
            with open(save_path, "w", encoding="utf-8", newline="") as f:
                f.write(out)

            # Ask to open the exported file
            reply = QMessageBox.question(
                self,
                "Export Complete",
                f"Annotations exported to:\r\n{save_path}\r\n\r\nOpen the file now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes,
            )
            if reply == QMessageBox.StandardButton.Yes:
                _open_path_default(Path(save_path))

        except Exception as e:
            QMessageBox.warning(self, "Export Failed", f"Couldn't write file:\n{e}")

    # ---------- Batch rename (also remap notes & general) ----------
    def _batch_rename(self):
        files = self._list_audio_in_root()
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
            target = p.withname(f"{new_base}{p.suffix.lower()}")
            n = 1
            while Path(target).exists() and Path(target).resolve() != p.resolve():
                target = p.withname(f"{new_base} ({n}){p.suffix.lower()}"); n += 1
            plan.append((p, Path(target)))

        preview = "\n".join(f"{src.name}  →  {dst.name}" for src, dst in plan[:25])
        more = "" if len(plan) <= 25 else f"\n… and {len(plan) - 25} more"
        if QMessageBox.question(self, "Confirm Batch Rename", f"Rename {len(plan)} file(s) as follows?\n\n{preview}{more}",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return

        did = 0
        remapped_notes: Dict[str, List[Dict]] = dict(self.notes_by_file)
        remapped_general: Dict[str, str] = dict(self.file_general)
        for src, dst in plan:
            try:
                src.rename(dst)
                if src.name in self.provided_names: self.provided_names[dst.name] = self.provided_names.pop(src.name)
                if src.name in remapped_notes: remapped_notes[dst.name] = remapped_notes.pop(src.name)
                if src.name in remapped_general: remapped_general[dst.name] = remapped_general.pop(src.name)
                did += 1
            except Exception as e:
                errors.append(f"{src.name}: {e}")

        self.notes_by_file = remapped_notes
        self.file_general = remapped_general
        self._save_names(); self._save_notes()
        self._refresh_right_table()
        self.model.setRootPath(""); self.model.setRootPath(str(self.root_path))
        self.tree.setRootIndex(self.model.index(str(self.root_path)))
        if self.current_audio_file:
            cur = self.current_audio_file.name
            for s, d in plan:
                if s.name == cur: self.current_audio_file = d; break
        self._load_annotations_for_current()

        # Outcome dialog
        if errors:
            QMessageBox.warning(self, "Finished with Errors", f"Renamed {did}/{len(plan)} files. Some failed:\n\n" +
                                "\n".join(errors[:20]) + ("…" if len(errors) > 20 else ""))
        else:
            QMessageBox.information(self, "Batch Rename Complete", f"Renamed {did} file(s).")

        # Ask whether to open the folder in file explorer
        reply = QMessageBox.question(
            self,
            "Open Folder",
            "Open this folder in your file explorer now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if reply == QMessageBox.StandardButton.Yes:
            _open_path_default(self.root_path)

    # ---------- Media events / close ----------
    def _on_media_error(self, _err, msg):
        if msg: QMessageBox.warning(self, "Playback Error", msg)

    def _on_media_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            if self.auto_progress_cb.isChecked():
                self._play_next_file()

    def closeEvent(self, ev):
        self._save_names(); self._save_notes(); super().closeEvent(ev)

def main():
    app = QApplication(sys.argv)
    app.setOrganizationName(APP_ORG); app.setApplicationName(APP_NAME)
    if "Fusion" in QStyleFactory.keys(): app.setStyle("Fusion")
    w = AudioBrowser(); w.show(); sys.exit(app.exec())

if __name__ == "__main__": main()
