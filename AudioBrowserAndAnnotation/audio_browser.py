#!/usr/bin/env python3
# audio_browser.py

"""
Audio Folder Player with Annotations + Async Waveform (Live Progress + Cache)

Updates in this build:
- Waveform progress text actually increments: “Analyzing waveform… NN%”.
  If progress can’t stream for some reason, it shows “Analyzing waveform…” (no stuck 0%).
- Waveform moved ABOVE the “New note” input in the Annotations tab.
- (Retained) Per-file async waveform generation with cache (size+mtime+columns),
  continues even if playback ends; clicking the same file doesn’t restart playback.
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
        print(f"[bootstrap] '{mod_name}' not found. Installing '{pkg}' via pip ...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
        except subprocess.CalledProcessError:
            print("[bootstrap] Global install failed. Retrying with --user ...")
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
    QItemSelection, QModelIndex, QSettings, QTimer, Qt, QUrl, QPoint, QEvent,
    pyqtSignal, QRect, QObject, QThread
)
from PyQt6.QtGui import (
    QAction, QKeySequence, QIcon, QPixmap, QPainter, QColor, QPen
)
# QFileSystemModel can live in QtGui in some PyQt6 builds; fallback to QtWidgets.
try:
    from PyQt6.QtGui import QFileSystemModel
except Exception:
    from PyQt6.QtWidgets import QFileSystemModel

from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from PyQt6.QtWidgets import (
    QApplication, QHBoxLayout, QHeaderView, QMainWindow, QMessageBox,
    QPushButton, QSlider, QSplitter, QTableWidget, QTableWidgetItem,
    QTreeView, QVBoxLayout, QWidget, QFileDialog, QAbstractItemView, QStatusBar,
    QToolBar, QStyle, QLabel, QTabWidget, QLineEdit
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
NAMES_JSON = ".provided_names.json"
NOTES_JSON = ".audio_notes.json"
WAVEFORM_JSON = ".waveform_cache.json"
AUDIO_EXTS = {".wav", ".wave", ".mp3"}

# Waveform cache resolution (number of precomputed columns)
WAVEFORM_COLUMNS = 2000

# ---------- Helpers ----------
def human_time_ms(ms: int) -> str:
    if ms < 0: return "0:00"
    s = ms // 1000
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"

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

            done = 0
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

# ---------- Waveform view (async + cached + live progress + robust multi-file) ----------
class WaveformView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(120)
        self._peaks: Optional[List[Tuple[float, float]]] = None
        self._peaks_loading: List[Tuple[float, float]] = []
        self._duration_ms: int = 0
        self._pixmap: Optional[QPixmap] = None
        self._pixmap_w: int = 0
        self._bg = QColor("#101114"); self._axis = QColor("#2a2c31")
        self._wave = QColor("#58a6ff"); self._playhead = QColor("#ff5555")
        self._message_color = QColor("#8a8f98")
        self._player: Optional[QMediaPlayer] = None

        self._state: str = "empty"   # empty|loading|ready|error
        self._msg: str = ""
        self._path: Optional[Path] = None
        self._total_cols: int = 0
        self._done_cols: int = 0

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
        self.update()

    def set_audio_file(self, path: Optional[Path]):
        """Set file; if cache miss/stale, start a fresh background build every time."""
        if path is None:
            self.clear(); return

        # Reset view state for the new file
        self._path = path
        self._pixmap = None; self._pixmap_w = 0
        self._peaks = None; self._peaks_loading = []
        self._total_cols = WAVEFORM_COLUMNS; self._done_cols = 0

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
        self._state = "loading"; self._msg = "Analyzing waveform…"  # start without `%`
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
        # Normalize incoming chunk to list[(float,float)]
        for pair in new_chunk:
            try:
                a, b = pair
            except Exception:
                continue
            self._peaks_loading.append((float(a), float(b)))

        # Bound done/total to sane values and update message with % if we have progress
        self._total_cols = max(1, int(total_cols))
        self._done_cols = max(0, min(int(done_cols), self._total_cols))
        if self._done_cols > 0:
            pct = int(round(100.0 * self._done_cols / self._total_cols))
            if pct < 100:  # only show percent while building
                self._msg = f"Analyzing waveform… {pct}%"
            else:
                self._msg = "Analyzing waveform…"
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
                # Stretch partial to full width for nicer UX
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
        if self._player and self._duration_ms > 0:
            pos = self._player.position()
            x = int((pos / self._duration_ms) * max(1, self.width()))
            pen = QPen(self._playhead); pen.setWidth(2)
            painter.setPen(pen); painter.drawLine(x, 0, x, self.height())
        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._player and self._duration_ms > 0:
            x = max(0, min(self.width(), int(event.position().x())))
            ms = int((x / max(1, self.width())) * self._duration_ms)
            self._player.setPosition(ms); self.update(); event.accept()
        else:
            super().mousePressEvent(event)

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

        # Media
        self.audio_output = QAudioOutput()
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)
        self.player.errorOccurred.connect(self._on_media_error)
        self.player.mediaStatusChanged.connect(self._on_media_status)

        # Stores
        self.provided_names: Dict[str, str] = {}
        self.notes_by_file: Dict[str, List[Dict]] = {}

        # UI
        self._init_ui()

        # Load metadata
        self._load_names()
        self._load_notes()

        # Populate
        self._refresh_right_table()
        self._load_annotations_for_current()

        # Selection & timers
        self.tree.selectionModel().selectionChanged.connect(self._on_tree_selection_changed)
        self.slider_sync = QTimer(self); self.slider_sync.setInterval(200)
        self.slider_sync.timeout.connect(self._sync_slider)
        self.player.positionChanged.connect(lambda _: self._sync_slider())
        self.player.durationChanged.connect(self._on_duration_changed)

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
        self.tree.setRootIndex(self.model.index(str(self.root_path)))
        self._load_names(); self._load_notes()
        self._refresh_right_table(); self.current_audio_file = None
        self._load_annotations_for_current()
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
        self.notes_by_file = {}
        pj = self._notes_json_path()
        try:
            if pj.exists():
                with open(pj, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "notes" in data and isinstance(data["notes"], dict):
                        self.notes_by_file = {
                            fname: [
                                {"ms": int(n.get("ms", 0)), "text": str(n.get("text", ""))}
                                for n in (notes or []) if isinstance(n, dict)
                            ]
                            for fname, notes in data["notes"].items()
                        }
        except Exception:
            self.notes_by_file = {}

    def _save_notes(self):
        try:
            payload = {"version": 1, "updated": datetime.now().isoformat(timespec="seconds"), "notes": self.notes_by_file}
            with open(self._notes_json_path(), "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
        except Exception as e:
            QMessageBox.warning(self, "Save Notes Failed", f"Couldn't save annotation notes:\n{e}")

    # ---------- UI ----------
    def _init_ui(self):
        self.resize(1250, 780); self.setStatusBar(QStatusBar(self))
        tb = QToolBar("Main"); self.addToolBar(tb)

        act_change_root = QAction("Change Folder…", self); act_change_root.triggered.connect(self._change_root_clicked); tb.addAction(act_change_root)
        act_up = QAction("Up", self); act_up.setShortcut(QKeySequence("Alt+Up")); act_up.triggered.connect(self._go_up); tb.addAction(act_up)
        tb.addSeparator()
        self.rename_button = QAction("Batch Rename (##_ProvidedName)", self); self.rename_button.triggered.connect(self._batch_rename); tb.addAction(self.rename_button)
        self.export_button = QAction("Export Annotations…", self); self.export_button.triggered.connect(self._export_annotations); tb.addAction(self.export_button)

        splitter = QSplitter(self); self.setCentralWidget(splitter)

        # Tree (left)
        self.model = QFileSystemModel(self); self.model.setRootPath(str(self.root_path))
        self.model.setResolveSymlinks(True); self.model.setReadOnly(True)
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
        right_layout.addLayout(player_bar)

        self.now_playing = QLabel("No selection"); self.now_playing.setStyleSheet("color: #666;"); right_layout.addWidget(self.now_playing)

        self.tabs = QTabWidget(); right_layout.addWidget(self.tabs, 1)

        # ---- Annotations tab (Waveform ABOVE "New note") ----
        ann_tab = QWidget(); ann_layout = QVBoxLayout(ann_tab)

        # Waveform (async + cached + live progress)
        self.waveform = WaveformView()
        self.waveform.bind_player(self.player)
        ann_layout.addWidget(self.waveform)

        # New note input (below waveform)
        top_controls = QHBoxLayout()
        self.note_input = QLineEdit(); self.note_input.setPlaceholderText("Type to create a note at current time; press Enter to add")
        self.note_input.textEdited.connect(self._on_note_text_edited); self.note_input.returnPressed.connect(self._on_note_return_pressed)
        top_controls.addWidget(QLabel("New note:"))
        top_controls.addWidget(self.note_input, 1)
        ann_layout.addLayout(top_controls)

        # Annotation table
        self.annotation_table = QTableWidget(0, 2)
        self.annotation_table.setHorizontalHeaderLabels(["Time", "Note"])
        ah = self.annotation_table.horizontalHeader(); ah.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents); ah.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.annotation_table.verticalHeader().setVisible(False)
        self.annotation_table.setEditTriggers(QAbstractItemView.EditTrigger.SelectedClicked | QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.EditKeyPressed)
        self.annotation_table.itemDoubleClicked.connect(self._on_annotation_double_clicked)
        self.annotation_table.itemChanged.connect(self._on_annotation_item_changed)
        self.annotation_table.installEventFilter(self)  # capture Delete key
        ann_layout.addWidget(self.annotation_table, 1)

        # Bottom: Delete selected
        bottom_controls = QHBoxLayout()
        self.delete_note_btn = QPushButton("Delete Selected"); self.delete_note_btn.clicked.connect(self._delete_selected_annotations)
        bottom_controls.addStretch(1); bottom_controls.addWidget(self.delete_note_btn)
        ann_layout.addLayout(bottom_controls)

        self.tabs.addTab(ann_tab, "Annotations")

        # ---- Library tab (unchanged) ----
        lib_tab = QWidget(); lib_layout = QVBoxLayout(lib_tab)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["File", "Created", "Provided Name (editable)"])
        hh = self.table.horizontalHeader(); hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents); hh.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.SelectedClicked)
        self.table.itemChanged.connect(self._on_table_item_changed); lib_layout.addWidget(self.table, 1)
        self.table.itemSelectionChanged.connect(self._stop_if_no_file_selected)
        self.tabs.addTab(lib_tab, "Library")

        if "Fusion" in QStyleFactory.keys(): QApplication.instance().setStyle("Fusion")

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
                if idx_new.isValid(): self.tree.setCurrentIndex(idx_new)
                if not (self.current_audio_file and self.current_audio_file.resolve() == path.resolve()):
                    self._play_file(path)
            self.tabs.setCurrentIndex(1)

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
            self._stop_playback(); self.now_playing.setText("No selection"); self.current_audio_file = None; self._load_annotations_for_current(); return
        fi = self.model.fileInfo(idx)
        if fi.isDir():
            self._stop_playback(); self.now_playing.setText(f"Folder selected: {fi.fileName()}"); self.current_audio_file = None; self._load_annotations_for_current(); return
        if f".{fi.suffix().lower()}" in AUDIO_EXTS:
            path = Path(fi.absoluteFilePath())
            if self.current_audio_file and self.current_audio_file.resolve() == path.resolve():
                return
            self._play_file(path)
        else:
            self._stop_playback(); self.now_playing.setText(fi.fileName()); self.current_audio_file = None; self._load_annotations_for_current()

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

    def _stop_playback(self):
        if self.player.playbackState() != QMediaPlayer.PlaybackState.StoppedState: self.player.stop()
        self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_pause_btn.setEnabled(False); self.position_slider.setEnabled(False); self.slider_sync.stop()
        self.position_slider.setValue(0); self.time_label.setText("0:00 / 0:00"); self.pending_note_start_ms = None
        # Waveform generation continues regardless

    def _toggle_play_pause(self):
        st = self.player.playbackState()
        if st == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause(); self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        else:
            self.player.play(); self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))

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

    # ---------- Annotations ----------
    def _load_annotations_for_current(self):
        self.annotation_table.blockSignals(True); self.annotation_table.setRowCount(0)
        if not self.current_audio_file: self.annotation_table.blockSignals(False); return
        fname = self.current_audio_file.name
        rows = sorted(self.notes_by_file.get(fname, []), key=lambda r: r.get("ms", 0))
        for entry in rows: self._append_annotation_row(int(entry.get("ms", 0)), str(entry.get("text", "")))
        self.annotation_table.blockSignals(False)

    def _append_annotation_row(self, ms: int, text: str):
        r = self.annotation_table.rowCount(); self.annotation_table.insertRow(r)
        t = QTableWidgetItem(human_time_ms(ms)); t.setFlags(t.flags() ^ Qt.ItemFlag.ItemIsEditable); t.setData(Qt.ItemDataRole.UserRole, int(ms))
        n = QTableWidgetItem(text)
        self.annotation_table.setItem(r, 0, t); self.annotation_table.setItem(r, 1, n)

    def _on_note_text_edited(self, _txt: str):
        if self.pending_note_start_ms is None: self.pending_note_start_ms = int(self.player.position())

    def _on_note_return_pressed(self):
        txt = self.note_input.text().strip()
        if not txt or not self.current_audio_file:
            self.pending_note_start_ms = None; self.note_input.clear(); return
        ms = self.pending_note_start_ms if self.pending_note_start_ms is not None else int(self.player.position())
        self.pending_note_start_ms = None
        fname = self.current_audio_file.name
        self.notes_by_file.setdefault(fname, []).append({"ms": int(ms), "text": txt})
        self._append_annotation_row(ms, txt); self._save_notes(); self.note_input.clear()

    def _on_annotation_double_clicked(self, item: QTableWidgetItem):
        row = item.row(); titem = self.annotation_table.item(row, 0)
        if not titem: return
        ms = int(titem.data(Qt.ItemDataRole.UserRole) or 0); self.player.setPosition(ms)

    def _on_annotation_item_changed(self, item: QTableWidgetItem):
        if item.column() != 1 or not self.current_audio_file: return
        row = item.row(); titem = self.annotation_table.item(row, 0)
        if not titem: return
        ms = int(titem.data(Qt.ItemDataRole.UserRole) or 0); fname = self.current_audio_file.name
        rows = self.notes_by_file.setdefault(fname, [])
        for entry in rows:
            if int(entry.get("ms", -1)) == ms:
                entry["text"] = item.text(); break
        self._save_notes()

    def _delete_selected_annotations(self):
        if not self.current_audio_file: return
        fname = self.current_audio_file.name
        rows_model = self.notes_by_file.setdefault(fname, [])
        sel_rows = sorted({idx.row() for idx in self.annotation_table.selectionModel().selectedIndexes()}, reverse=True)
        if not sel_rows: return
        to_remove = []
        for r in sel_rows:
            titem = self.annotation_table.item(r, 0)
            nitem = self.annotation_table.item(r, 1)
            if not titem or not nitem: continue
            ms = int(titem.data(Qt.ItemDataRole.UserRole) or 0)
            tx = nitem.text()
            to_remove.append((ms, tx))
        for ms, tx in to_remove:
            for i, entry in enumerate(rows_model):
                if int(entry.get("ms", -1)) == ms and str(entry.get("text","")) == tx:
                    rows_model.pop(i); break
        for r in sel_rows: self.annotation_table.removeRow(r)
        self._save_notes()

    # Capture Delete key on the annotations table
    def eventFilter(self, obj, event):
        if obj is self.annotation_table and event.type() == QEvent.Type.KeyPress:
            if event.key() in (Qt.Key.Key_Delete,):
                self._delete_selected_annotations(); return True
        return super().eventFilter(obj, event)

    # ---------- Export annotations ----------
    def _export_annotations(self):
        default_path = str((self.root_path / "annotations_export.txt").resolve())
        save_path, _ = QFileDialog.getSaveFileName(self, "Export Annotations", default_path, "Text Files (*.txt);;All Files (*)")
        if not save_path: return
        lines: List[str] = []
        for fname in sorted(self.notes_by_file.keys()):
            notes = sorted(self.notes_by_file.get(fname, []), key=lambda n: int(n.get("ms", 0)))
            if not notes: continue
            provided = (self.provided_names.get(fname, "") or "").replace("\n", " ").strip()
            stem = Path(fname).stem
            title = f"{fname} — {provided}" if provided and provided != stem else fname
            lines.append(title)
            for n in notes:
                ts = human_time_ms(int(n.get("ms", 0))); txt = str(n.get("text", "")).replace("\n", " ").strip()
                lines.append(f"{ts} {txt}")
            lines.append("")
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines).rstrip() + "\n")
            QMessageBox.information(self, "Export Complete", f"Annotations exported to:\n{save_path}")
        except Exception as e:
            QMessageBox.warning(self, "Export Failed", f"Couldn't write file:\n{e}")

    # ---------- Batch rename (also remap notes) ----------
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

        did = 0; remapped_notes: Dict[str, List[Dict]] = dict(self.notes_by_file)
        for src, dst in plan:
            try:
                src.rename(dst)
                if src.name in self.provided_names: self.provided_names[dst.name] = self.provided_names.pop(src.name)
                if src.name in remapped_notes: remapped_notes[dst.name] = remapped_notes.pop(src.name)
                did += 1
            except Exception as e:
                errors.append(f"{src.name}: {e}")

        self.notes_by_file = remapped_notes
        self._save_names(); self._save_notes()
        self._refresh_right_table()
        self.model.setRootPath(""); self.model.setRootPath(str(self.root_path))
        self.tree.setRootIndex(self.model.index(str(self.root_path)))
        if self.current_audio_file:
            cur = self.current_audio_file.name
            for s, d in plan:
                if s.name == cur: self.current_audio_file = d; break
        self._load_annotations_for_current()

        if errors:
            QMessageBox.warning(self, "Finished with Errors", f"Renamed {did}/{len(plan)} files. Some failed:\n\n" +
                                "\n".join(errors[:20]) + ("…" if len(errors) > 20 else ""))
        else:
            QMessageBox.information(self, "Batch Rename Complete", f"Renamed {did} file(s).")

    # ---------- Media events / close ----------
    def _on_media_error(self, _err, msg):
        if msg: QMessageBox.warning(self, "Playback Error", msg)
    def _on_media_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
    def closeEvent(self, ev):
        self._save_names(); self._save_notes(); super().closeEvent(ev)

def main():
    app = QApplication(sys.argv)
    app.setOrganizationName(APP_ORG); app.setApplicationName(APP_NAME)
    if "Fusion" in QStyleFactory.keys(): app.setStyle("Fusion")
    w = AudioBrowser(); w.show(); sys.exit(app.exec())

if __name__ == "__main__": main()
