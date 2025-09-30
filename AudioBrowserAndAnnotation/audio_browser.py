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

import sys, subprocess, importlib, os, json, re, uuid, hashlib, wave, time, getpass, logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from array import array

# Windows subprocess flag to hide console windows
if sys.platform == "win32":
    CREATE_NO_WINDOW = 0x08000000  # Windows CREATE_NO_WINDOW flag
else:
    CREATE_NO_WINDOW = 0  # No-op on non-Windows platforms

# Import version information
try:
    from .version import VERSION_STRING, VERSION_INFO
except ImportError:
    try:
        from version import VERSION_STRING, VERSION_INFO
    except ImportError:
        # Fallback if version module is not available
        VERSION_STRING = "1.0"
        VERSION_INFO = "Version 1.0"

# ========== Bootstrap: auto-install PyQt6 (if not frozen) ==========
def _ensure_import(mod_name: str, pip_name: str | None = None) -> tuple[bool, str]:
    """Try to import a module, auto-installing if needed.
    
    Returns:
        tuple[bool, str]: (success, error_message)
    """
    try:
        importlib.import_module(mod_name)
        return True, ""
    except ImportError:
        if getattr(sys, "frozen", False):
            return False, f"{mod_name} is not available in this frozen build"
        
        pkg = pip_name or mod_name
        
        # Prepare subprocess arguments to hide console windows
        subprocess_kwargs = {}
        if sys.platform == "win32":
            subprocess_kwargs["creationflags"] = CREATE_NO_WINDOW
        
        install_errors = []
        for args in ([sys.executable, "-m", "pip", "install", pkg],
                     [sys.executable, "-m", "pip", "install", "--user", pkg]):
            try:
                subprocess.check_call(args, **subprocess_kwargs)
                break
            except subprocess.CalledProcessError as e:
                install_errors.append(f"'{' '.join(args)}' failed with exit code {e.returncode}")
                continue
        else:
            error_msg = f"Failed to install {pkg}. Attempted installations:\n" + "\n".join(f"  - {err}" for err in install_errors)
            return False, error_msg
        
        importlib.invalidate_caches()
        try:
            importlib.import_module(mod_name)
            return True, ""
        except ImportError as e:
            return False, f"Successfully installed {pkg} but still cannot import {mod_name}: {e}"

try:
    import PyQt6
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False

if not PYQT6_AVAILABLE:
    if getattr(sys, "frozen", False):
        # In frozen builds, PyQt6 should already be bundled
        raise RuntimeError("PyQt6 is missing from this build. Please reinstall the application.")
    else:
        success, error_msg = _ensure_import("PyQt6", "PyQt6")
        if not success:
            error_details = f"""PyQt6 is required but could not be installed automatically.

Error details:
{error_msg}

To fix this issue, try one of the following:

1. Install PyQt6 manually:
   pip install PyQt6

2. If you're behind a corporate firewall or proxy:
   - Configure pip to use your proxy settings
   - Or ask your IT administrator for help

3. If you're in a restricted environment:
   - Use a Python virtual environment with pip access
   - Or install PyQt6 using your system package manager

4. Alternative manual installation:
   python -m pip install --user PyQt6

For more help, see: https://pypi.org/project/PyQt6/"""
            raise RuntimeError(error_details)
    
    # Try importing again after installation
    try:
        import PyQt6
        PYQT6_AVAILABLE = True
    except ImportError:
        raise RuntimeError("PyQt6 installation succeeded but import still fails. Please restart the application.")

HAVE_NUMPY, _ = _ensure_import("numpy", "numpy")
HAVE_PYDUB, _ = _ensure_import("pydub", "pydub")
HAVE_AUDIOOP, _ = _ensure_import("audioop", "audioop")
if HAVE_PYDUB:
    try:
        from pydub import AudioSegment
        from pydub.utils import which as pydub_which
    except Exception:
        HAVE_PYDUB = False

# ========== Qt imports ==========
from PyQt6.QtCore import (
    QItemSelection, QModelIndex, QSettings, QTimer, Qt, QUrl, QPoint, QSize,
    pyqtSignal, QRect, QObject, QThread, QDir, QIdentityProxyModel, QSortFilterProxyModel
)
from PyQt6.QtGui import (
    QAction, QKeySequence, QIcon, QPixmap, QPainter, QColor, QPen, QCursor, QPalette
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
    QProgressDialog, QColorDialog, QInputDialog, QComboBox, QMenu, QDialog, QTextEdit, QMenuBar
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
SETTINGS_KEY_FINGERPRINT_ALGORITHM = "fingerprint_algorithm"
SETTINGS_KEY_AUTO_GEN_WAVEFORMS = "auto_generate_waveforms"
SETTINGS_KEY_AUTO_GEN_FINGERPRINTS = "auto_generate_fingerprints"
SETTINGS_KEY_AUTO_GEN_TIMING = "auto_generation_timing"  # "boot" or "folder_selection"
NAMES_JSON = ".provided_names.json"
NOTES_JSON = ".audio_notes.json"
WAVEFORM_JSON = ".waveform_cache.json"
DURATIONS_JSON = ".duration_cache.json"
FINGERPRINTS_JSON = ".audio_fingerprints.json"
USER_COLORS_JSON = ".user_colors.json"
RESERVED_JSON = {NAMES_JSON, NOTES_JSON, WAVEFORM_JSON, DURATIONS_JSON, FINGERPRINTS_JSON, USER_COLORS_JSON}
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

# ========== Logging Setup ==========
def setup_logging():
    """
    Set up logging to redirect all console output to a log file.
    The log file is recreated each time the application starts.
    """
    # Get the application directory
    app_dir = Path(__file__).parent
    log_file = app_dir / "audiobrowser.log"
    
    # Remove existing log file if it exists (recreate on each startup)
    if log_file.exists():
        try:
            log_file.unlink()
        except Exception:
            pass  # Ignore errors removing old log file
    
    # Clear any existing handlers to avoid conflicts
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Configure logging with explicit encoding and error handling
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, mode='w', encoding='utf-8', errors='replace'),
        ],
        force=True
    )
    
    # Get the root logger
    logger = logging.getLogger()
    
    # Log startup message with safe string formatting
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.info("AudioBrowser application starting up - %s", timestamp)
    logger.info("Log file location: %s", str(log_file.absolute()))
    
    return logger

# Global logger instance
_logger = None

def get_logger():
    """Get the global logger instance."""
    global _logger
    if _logger is None:
        _logger = setup_logging()
    return _logger

def log_print(*args, **kwargs):
    """
    Replacement for print() that logs to file instead of console.
    Maintains similar interface to print() for easy replacement.
    Ensures all content is safely encoded and readable.
    """
    try:
        # Convert args to string like print() does, with safe string conversion
        def safe_str(obj):
            """Safely convert any object to string, handling encoding issues"""
            try:
                if isinstance(obj, bytes):
                    return obj.decode('utf-8', errors='replace')
                else:
                    return str(obj)
            except Exception:
                return repr(obj)
        
        message_parts = [safe_str(arg) for arg in args]
        
        # Handle common print() keyword arguments
        sep = kwargs.get('sep', ' ')
        end = kwargs.get('end', '\n')
        
        # Join the message parts
        message = sep.join(message_parts)
        
        # Remove the trailing newline since logging adds its own
        if end == '\n' and message.endswith('\n'):
            message = message[:-1]
        
        # Escape control characters to keep log files readable
        # This prevents multiline breaks and non-printable characters from 
        # corrupting the log file structure
        message = message.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
        
        # Escape other common control characters that could cause issues
        for i in range(32):
            if i not in (9, 10, 13):  # Skip tab, newline, carriage return (already handled)
                char = chr(i)
                if char in message:
                    message = message.replace(char, f'\\x{i:02x}')
        
        # Use parameterized logging to avoid format string issues
        get_logger().info("%s", message)
        
    except Exception as e:
        # Fallback logging in case of any encoding issues
        try:
            get_logger().error("log_print failed: %s", str(e))
            get_logger().error("Original args: %s", repr(args))
        except:
            # Ultimate fallback - write to stderr
            print(f"Critical logging error: {e}", file=sys.stderr)

# ========== Custom Widgets ==========
class BestTakeIndicatorWidget(QWidget):
    """Custom widget that shows colored squares for each annotation set that marked a file as best take."""
    
    def __init__(self, best_take_sets: List[Dict[str, Any]], current_set_id: str = "", parent=None):
        super().__init__(parent)
        self.best_take_sets = best_take_sets
        self.current_set_id = current_set_id
        self.setMinimumHeight(20)
        self.setMaximumHeight(20)
        # Make it checkable-like behavior for the current set
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background
        painter.fillRect(self.rect(), QColor(255, 255, 255))
        
        if not self.best_take_sets:
            return
            
        # Calculate square size and spacing
        square_size = min(16, self.height() - 4)
        spacing = 2
        total_width = len(self.best_take_sets) * square_size + (len(self.best_take_sets) - 1) * spacing
        start_x = max(2, (self.width() - total_width) // 2)
        start_y = (self.height() - square_size) // 2
        
        # Draw colored squares for each annotation set
        for i, best_take_set in enumerate(self.best_take_sets):
            x = start_x + i * (square_size + spacing)
            color = QColor(best_take_set["color"])
            
            # Draw the square
            painter.fillRect(x, start_y, square_size, square_size, color)
            
            # Draw border (thicker for current set)
            pen_width = 3 if best_take_set["id"] == self.current_set_id else 1
            painter.setPen(QPen(QColor(0, 0, 0), pen_width))
            painter.drawRect(x, start_y, square_size, square_size)
    
    def update_best_takes(self, best_take_sets: List[Dict[str, Any]], current_set_id: str = ""):
        self.best_take_sets = best_take_sets
        self.current_set_id = current_set_id
        self.update()

    def mousePressEvent(self, event):
        """Handle clicks to toggle best take for current set."""
        # Calculate which square was clicked (if any)
        if not self.best_take_sets:
            return
            
        square_size = min(16, self.height() - 4)
        spacing = 2
        total_width = len(self.best_take_sets) * square_size + (len(self.best_take_sets) - 1) * spacing
        start_x = max(2, (self.width() - total_width) // 2)
        
        click_x = event.pos().x()
        
        # Check if click is within the squares area
        if click_x >= start_x and click_x <= start_x + total_width:
            # Emit a custom signal or call parent method
            self.parent().on_best_take_clicked()


class PartialTakeIndicatorWidget(QWidget):
    """Custom widget that shows colored circles for each annotation set that marked a file as partial take."""
    
    def __init__(self, partial_take_sets: List[Dict[str, Any]], current_set_id: str = "", parent=None):
        super().__init__(parent)
        self.partial_take_sets = partial_take_sets
        self.current_set_id = current_set_id
        self.setMinimumHeight(20)
        self.setMaximumHeight(20)
        # Make it checkable-like behavior for the current set
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background
        painter.fillRect(self.rect(), QColor(255, 255, 255))
        
        if not self.partial_take_sets:
            return
            
        # Calculate circle size and spacing
        circle_size = min(16, self.height() - 4)
        spacing = 2
        total_width = len(self.partial_take_sets) * circle_size + (len(self.partial_take_sets) - 1) * spacing
        start_x = max(2, (self.width() - total_width) // 2)
        start_y = (self.height() - circle_size) // 2
        
        # Draw colored circles for each annotation set
        for i, partial_take_set in enumerate(self.partial_take_sets):
            x = start_x + i * (circle_size + spacing)
            color = QColor(partial_take_set["color"])
            
            # Draw the circle
            painter.setBrush(color)
            painter.drawEllipse(x, start_y, circle_size, circle_size)
            
            # Draw border (thicker for current set)
            pen_width = 3 if partial_take_set["id"] == self.current_set_id else 1
            painter.setPen(QPen(QColor(0, 0, 0), pen_width))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(x, start_y, circle_size, circle_size)
    
    def update_partial_takes(self, partial_take_sets: List[Dict[str, Any]], current_set_id: str = ""):
        self.partial_take_sets = partial_take_sets
        self.current_set_id = current_set_id
        self.update()

    def mousePressEvent(self, event):
        """Handle clicks to toggle partial take for current set."""
        # Calculate which circle was clicked (if any)
        if not self.partial_take_sets:
            return
            
        circle_size = min(16, self.height() - 4)
        spacing = 2
        total_width = len(self.partial_take_sets) * circle_size + (len(self.partial_take_sets) - 1) * spacing
        start_x = max(2, (self.width() - total_width) // 2)
        
        click_x = event.pos().x()
        
        # Check if click is within the circles area
        if click_x >= start_x and click_x <= start_x + total_width:
            # Emit a custom signal or call parent method
            self.parent().on_partial_take_clicked()

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

# ========== Color Standardization System ==========
class ColorManager:
    """Manages consistent colors across different machines and display environments."""
    
    def __init__(self):
        self._color_cache = {}
        
    def get_standardized_color(self, base_color: str, purpose: str = "general") -> QColor:
        """
        Get a standardized color that appears consistent across different machines.
        
        Args:
            base_color: Base hex color (e.g., "#58a6ff")
            purpose: Purpose of the color (e.g., "selection", "waveform", "text")
            
        Returns:
            QColor object with standardized properties for consistent appearance
        """
        cache_key = f"{base_color}_{purpose}"
        if cache_key in self._color_cache:
            return self._color_cache[cache_key]
            
        base_qcolor = QColor(base_color)
        if not base_qcolor.isValid():
            base_qcolor = QColor("#808080")  # Fallback gray
            
        # Apply standardization based on purpose
        standardized = self._apply_color_standardization(base_qcolor, purpose)
        self._color_cache[cache_key] = standardized
        return standardized
    
    def _apply_color_standardization(self, color: QColor, purpose: str) -> QColor:
        """Apply standardization rules to ensure consistent appearance across machines."""
        # Convert to HSV for consistent manipulation
        h, s, v, a = color.getHsvF()
        
        # Standardize based on purpose
        if purpose == "selection":
            # Ensure selection colors are vivid and high-contrast
            s = max(0.8, s)  # Ensure high saturation for visibility
            v = max(0.6, min(0.9, v))  # Ensure adequate brightness without being blinding
        elif purpose == "waveform":
            # Waveform colors should be clear but not too bright
            s = max(0.7, min(0.95, s))  # Good saturation for clarity
            v = max(0.5, min(0.8, v))  # Medium brightness for long viewing comfort
        elif purpose == "text":
            # Text colors need good contrast
            if v > 0.5:  # Light colors
                v = max(0.2, v)  # Ensure dark enough for readability
            else:  # Dark colors  
                v = min(0.8, max(0.4, v))  # Ensure light enough for readability
        elif purpose == "ui_accent":
            # UI accent colors (buttons, highlights)
            s = max(0.6, min(0.9, s))  # Strong but not overwhelming
            v = max(0.4, min(0.7, v))  # Medium brightness
        
        # Apply gamma correction for consistent appearance across displays
        # Most displays have gamma around 2.2, so we normalize to that
        v = pow(v, 1.0 / 2.2) if v > 0 else 0
        v = pow(v, 2.2)
        
        return QColor.fromHsvF(h, s, v, a)
    
    def get_selection_colors(self) -> dict:
        """Get standardized selection colors for UI consistency."""
        return {
            'primary': self.get_standardized_color("#2563eb", "selection"),
            'active': self.get_standardized_color("#1d4ed8", "selection"), 
            'inactive': self.get_standardized_color("#1e3a8a", "selection")
        }
    
    def get_waveform_colors(self) -> dict:
        """Get standardized waveform colors."""
        return {
            'background': self.get_standardized_color("#101114", "ui_accent"),
            'axis': self.get_standardized_color("#2a2c31", "ui_accent"),
            'left_channel': self.get_standardized_color("#58a6ff", "waveform"),
            'right_channel': self.get_standardized_color("#ff6b58", "waveform"),
            'playhead': self.get_standardized_color("#ff5555", "waveform"),
            'selected': self.get_standardized_color("#ffa500", "selection"),
            'message': self.get_standardized_color("#8a8f98", "text")
        }
    
    def get_ui_colors(self) -> dict:
        """Get standardized UI element colors."""
        return {
            'success': self.get_standardized_color("#4CAF50", "ui_accent"),
            'danger': self.get_standardized_color("#f44336", "ui_accent"),
            'info': self.get_standardized_color("#2196F3", "ui_accent"),
            'warning': self.get_standardized_color("#ff9800", "ui_accent"),
            'text_secondary': self.get_standardized_color("#666666", "text"),
            'text_muted': self.get_standardized_color("#999999", "text"),
            'background_light': self.get_standardized_color("#f8f8f8", "ui_accent"),
            'background_medium': self.get_standardized_color("#f0f0f0", "ui_accent"),
            'border': self.get_standardized_color("#cccccc", "ui_accent")
        }

# Global color manager instance
_color_manager = ColorManager()

def get_consistent_stylesheet_colors():
    """Get color values for consistent stylesheets across machines."""
    ui_colors = _color_manager.get_ui_colors()
    selection_colors = _color_manager.get_selection_colors()
    
    return {
        'selection_primary': selection_colors['primary'].name(),
        'selection_active': selection_colors['active'].name(), 
        'selection_inactive': selection_colors['inactive'].name(),
        'success': ui_colors['success'].name(),
        'danger': ui_colors['danger'].name(),
        'info': ui_colors['info'].name(),
        'warning': ui_colors['warning'].name(),
        'text_secondary': ui_colors['text_secondary'].name(),
        'text_muted': ui_colors['text_muted'].name(),
        'bg_light': ui_colors['background_light'].name(),
        'bg_medium': ui_colors['background_medium'].name(),
        'border': ui_colors['border'].name()
    }

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

def decode_audio_samples(path: Path, stereo: bool = False) -> Tuple[List[float], int, int, Optional[List[float]]]:
    """
    Decode audio samples from file.
    
    Args:
        path: Audio file path
        stereo: If True, return both mono and stereo channel data
        
    Returns:
        Tuple of (mono_samples, sample_rate, duration_ms, stereo_samples)
        where stereo_samples is None if stereo=False or file is mono,
        otherwise it's [left_ch, right_ch, left_ch, right_ch, ...]
    """
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
        
        stereo_samples = None
        if nch > 1:
            total = len(data) // nch
            mono = array("h", [0]) * total
            for i in range(total):
                s = 0; base = i * nch
                for c in range(nch): s += data[base + c]
                mono[i] = int(s / nch)
            
            # Store stereo data if requested and it's stereo
            if stereo and nch >= 2:
                if HAVE_NUMPY:
                    stereo_arr = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                    stereo_samples = stereo_arr.tolist()
                else:
                    stereo_samples = [s / 32768.0 for s in data]
            
            data = mono
        
        if HAVE_NUMPY:
            arr = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
            samples = arr.tolist()
        else:
            samples = [s / 32768.0 for s in data]
        dur_ms = int((len(samples) / sr) * 1000)
        return samples, sr, dur_ms, stereo_samples
        
    if HAVE_PYDUB:
        seg = AudioSegment.from_file(str(path))
        sr = seg.frame_rate
        dur_ms = len(seg)
        ch = seg.channels
        raw = seg.get_array_of_samples()
        
        stereo_samples = None
        if HAVE_NUMPY:
            arr = np.array(raw, dtype=np.int16).astype(np.float32)
            
            # Store stereo data if requested and it's stereo
            if stereo and ch >= 2:
                stereo_samples = (arr / 32768.0).tolist()
            
            if ch > 1: arr = arr.reshape((-1, ch)).mean(axis=1)
            samples = (arr / 32768.0).tolist()
        else:
            ints = list(raw)
            if ch > 1:
                # Store stereo data if requested
                if stereo and ch >= 2:
                    stereo_samples = [v / 32768.0 for v in ints]
                
                mono = []
                for i in range(0, len(ints), ch):
                    s = 0
                    for c in range(ch): s += ints[i + c]
                    mono.append(s / ch)
                samples = [v / 32768.0 for v in mono]
            else:
                samples = [v / 32768.0 for v in ints]
        return samples, sr, dur_ms, stereo_samples
        
    raise RuntimeError("No MP3 decoder found (install FFmpeg for pydub).")


def get_audio_channel_count(path: Path) -> int:
    """Return the number of channels in an audio file (1 for mono, 2+ for stereo/multichannel)."""
    suf = path.suffix.lower()
    if suf in (".wav", ".wave"):
        try:
            with wave.open(str(path), "rb") as wf:
                return wf.getnchannels()
        except Exception:
            pass
    if HAVE_PYDUB:
        try:
            seg = AudioSegment.from_file(str(path))
            return seg.channels
        except Exception:
            pass
    return 1  # Default to mono if we can't determine

def compute_peaks_progressive(samples: List[float], columns: int, chunk: int, stereo_samples: Optional[List[float]] = None):
    """
    Compute peaks progressively for mono or stereo audio.
    
    Args:
        samples: Mono audio samples
        columns: Number of columns to generate
        chunk: Chunk size for progressive generation
        stereo_samples: Optional stereo samples [L, R, L, R, ...] for stereo mode
        
    Yields:
        (start_index, peaks_data)
        For mono: peaks_data = [[min, max], [min, max], ...]
        For stereo: peaks_data = [[[L_min, L_max], [R_min, R_max]], ...]
    """
    n = len(samples)
    if n == 0 or columns <= 0:
        if stereo_samples:
            yield 0, [[[0.0, 0.0], [0.0, 0.0]] for _ in range(max(1, columns))]
        else:
            yield 0, [[0.0, 0.0] for _ in range(max(1, columns))]
        return
    
    if stereo_samples and len(stereo_samples) >= 2:
        # Stereo mode - process left and right channels separately
        n_stereo = len(stereo_samples)
        n_samples = n_stereo // 2  # Number of sample pairs
        
        if HAVE_NUMPY:
            arr = np.asarray(stereo_samples, dtype=np.float32)
            left_ch = arr[::2]  # Every even index
            right_ch = arr[1::2]  # Every odd index
            idx = np.linspace(0, n_samples, num=columns+1, dtype=np.int64)
            
            for start in range(0, columns, chunk):
                end = min(columns, start + chunk)
                out = []
                for i in range(start, end):
                    a, b = idx[i], idx[i+1]
                    if b > a:
                        left_seg = left_ch[a:b]
                        right_seg = right_ch[a:b]
                        out.append([
                            [float(left_seg.min()), float(left_seg.max())],
                            [float(right_seg.min()), float(right_seg.max())]
                        ])
                    else:
                        left_val = float(left_ch[min(a, len(left_ch)-1)])
                        right_val = float(right_ch[min(a, len(right_ch)-1)])
                        out.append([[left_val, left_val], [right_val, right_val]])
                yield start, out
        else:
            # Non-numpy stereo processing
            for start in range(0, columns, chunk):
                end = min(columns, start + chunk)
                out = []
                for i in range(start, end):
                    a = int(i * n_samples / columns) * 2  # Convert to stereo index
                    b = int((i+1) * n_samples / columns) * 2
                    if b <= a: b = a + 2
                    
                    left_min, left_max = 1.0, -1.0
                    right_min, right_max = 1.0, -1.0
                    
                    for j in range(a, min(b, n_stereo-1), 2):
                        left_val = stereo_samples[j]
                        right_val = stereo_samples[j+1] if j+1 < n_stereo else left_val
                        
                        if left_val < left_min: left_min = left_val
                        if left_val > left_max: left_max = left_val
                        if right_val < right_min: right_min = right_val
                        if right_val > right_max: right_max = right_val
                    
                    out.append([
                        [float(left_min), float(left_max)],
                        [float(right_min), float(right_max)]
                    ])
                yield start, out
    else:
        # Mono mode - existing implementation
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

def resample_peaks(peaks: List, width: int) -> List:
    """
    Resample peaks to target width.
    
    Args:
        peaks: For mono: List[Tuple[float, float]]
               For stereo: List[List[List[float]]] where each item is [[L_min, L_max], [R_min, R_max]]
        width: Target width
        
    Returns:
        Resampled peaks in same format as input
    """
    n = len(peaks)
    if n == 0 or width <= 0: 
        # Detect format by checking first element if available
        if n > 0 and isinstance(peaks[0], list) and len(peaks[0]) == 2 and isinstance(peaks[0][0], list):
            # Stereo format
            return [[[0.0, 0.0], [0.0, 0.0]] for _ in range(max(1, width))]
        else:
            # Mono format
            return [(0.0, 0.0)] * max(1, width)
    
    if width == n: return peaks
    
    # Check if this is stereo data
    is_stereo = isinstance(peaks[0], list) and len(peaks[0]) == 2 and isinstance(peaks[0][0], list)
    
    out = []
    for i in range(width):
        a = int(i * n / width); b = int((i+1) * n / width)
        if b <= a: b = a + 1
        
        if is_stereo:
            # Stereo resampling
            left_min, left_max = 1.0, -1.0
            right_min, right_max = 1.0, -1.0
            
            for j in range(a, min(b, n)):
                left_peak = peaks[j][0]  # [L_min, L_max]
                right_peak = peaks[j][1]  # [R_min, R_max]
                
                if left_peak[0] < left_min: left_min = left_peak[0]
                if left_peak[1] > left_max: left_max = left_peak[1]
                if right_peak[0] < right_min: right_min = right_peak[0]
                if right_peak[1] > right_max: right_max = right_peak[1]
            
            out.append([[left_min, left_max], [right_min, right_max]])
        else:
            # Mono resampling (existing logic)
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
    
    Note: This function assumes both fingerprints were generated using the same algorithm.
    The calling code is responsible for ensuring algorithm consistency.
    """
    if not fp1 or not fp2:
        return 0.0
    
    # Safety check: warn if fingerprints have very different lengths, which might indicate different algorithms
    len1, len2 = len(fp1), len(fp2)
    if abs(len1 - len2) > max(len1, len2) * 0.5:  # More than 50% size difference
        log_print(f"Warning: Comparing fingerprints of very different lengths ({len1} vs {len2}). "
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
    Based on the algorithm suggestion in the issue:
    - Downsample to ~11 kHz, take up to the middle 60s
    - STFT - group magnitudes into ~32 log-spaced frequency bands (60–6000 Hz)
    - Log/normalize → average over time
    - Return 32-D vector per file for cosine similarity comparison
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
    
    band_energies = []
    
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
    Based on the actual ChromaPrint methodology:
    - Extracts chroma features (12 semitone classes) 
    - Uses overlapping frames with FFT analysis
    - Maps frequencies to chroma bins using proper pitch class mapping
    - Applies temporal smoothing and quantization
    - Generates compact binary-like hash representation
    """
    if not HAVE_NUMPY:
        # Simple fallback without numpy
        return [float(i % 12) / 12.0 for i in range(144)]  # 12 chroma * 12 frames
        
    arr = np.asarray(samples, dtype=np.float32)
    
    # ChromaPrint-style parameters
    frame_size = 4096  # Frame size for FFT
    hop_length = frame_size // 4  # 75% overlap
    
    # Chroma parameters
    n_chroma = 12  # 12 semitones (C, C#, D, D#, E, F, F#, G, G#, A, A#, B)
    min_frequency = 80.0  # Minimum frequency to consider (Hz)
    max_frequency = min(sr // 2, 5000.0)  # Maximum frequency
    
    # Create frequency to chroma mapping
    def freq_to_chroma(freq):
        """Convert frequency to chroma class (0-11)"""
        if freq <= 0:
            return 0
        # A4 (440 Hz) = note 69 in MIDI, which is chroma class 9 (A)
        # Formula: chroma = (12 * log2(freq/440)) % 12, adjusted for A=9
        note_number = 12 * np.log2(freq / 440.0) + 69
        chroma_class = int(note_number) % 12
        return chroma_class
    
    chroma_frames = []
    window = np.hanning(frame_size)
    
    for i in range(0, len(arr) - frame_size + 1, hop_length):
        frame = arr[i:i + frame_size] * window
        
        # Compute FFT
        fft_result = np.fft.rfft(frame)
        magnitude = np.abs(fft_result)
        
        # Create frequency bins
        freqs = np.fft.rfftfreq(frame_size, 1.0 / sr)
        
        # Initialize chroma vector
        chroma_vector = np.zeros(n_chroma)
        
        # Map frequency bins to chroma classes
        for j, freq in enumerate(freqs):
            if min_frequency <= freq <= max_frequency:
                chroma_class = freq_to_chroma(freq)
                chroma_vector[chroma_class] += magnitude[j]
        
        # Normalize the chroma vector
        total_energy = np.sum(chroma_vector)
        if total_energy > 0:
            chroma_vector = chroma_vector / total_energy
            
        chroma_frames.append(chroma_vector)
    
    if not chroma_frames:
        return [0.0] * (n_chroma * 12)  # Fallback
    
    # Convert to numpy array for easier manipulation
    chroma_matrix = np.array(chroma_frames)
    
    # Apply temporal smoothing (simple moving average)
    smoothed_chroma = []
    window_size = 3
    for i in range(len(chroma_matrix)):
        start_idx = max(0, i - window_size // 2)
        end_idx = min(len(chroma_matrix), i + window_size // 2 + 1)
        smoothed_frame = np.mean(chroma_matrix[start_idx:end_idx], axis=0)
        smoothed_chroma.append(smoothed_frame)
    
    # Quantize and create hash-like features
    # ChromaPrint-style: compare adjacent frames to create binary features
    hash_features = []
    for i in range(len(smoothed_chroma) - 1):
        current_frame = smoothed_chroma[i]
        next_frame = smoothed_chroma[i + 1]
        
        # Create binary-like features by comparing chroma values
        frame_hash = []
        for c in range(n_chroma):
            # Compare current vs next frame for each chroma class
            diff = next_frame[c] - current_frame[c]
            # Convert to quantized feature (0.0 or 1.0)
            feature = 1.0 if diff > 0 else 0.0
            frame_hash.append(feature)
        
        hash_features.extend(frame_hash)
    
    # Limit to consistent size (12 chroma classes * 12 time frames = 144 features)
    target_size = 144
    if len(hash_features) > target_size:
        # Downsample by taking every nth element
        step = len(hash_features) / target_size
        downsampled = [hash_features[int(i * step)] for i in range(target_size)]
        return downsampled
    elif len(hash_features) < target_size:
        # Pad with zeros
        return hash_features + [0.0] * (target_size - len(hash_features))
    else:
        return hash_features

def compute_audfprint_fingerprint(samples: List[float], sr: int) -> List[float]:
    """
    AudFprint-inspired constellation fingerprint algorithm.
    Based on the actual audfprint methodology:
    - Creates spectrogram and finds prominent spectral peaks
    - Uses constellation mapping with landmark/anchor points
    - Generates hash pairs from peak combinations in time-frequency space
    - Creates robust fingerprint resistant to noise and time shifting
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
                # This simulates audfprint's hash generation
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

DEFAULT_ALGORITHM = "spectral"

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
                log_print(f"Error computing {alg_name} fingerprint: {e}")
                # Fallback to basic pattern
                fingerprints[alg_name] = [0.1] * 50
    
    return fingerprints

def validate_fingerprint_algorithm_coverage(cache: Dict, required_algorithm: str) -> Dict[str, bool]:
    """
    Check which files in a cache have fingerprints for the specified algorithm.
    
    Args:
        cache: Fingerprint cache dictionary
        required_algorithm: Algorithm name to check for
        
    Returns:
        Dictionary mapping filename -> boolean (True if algorithm present, False otherwise)
    """
    coverage = {}
    files_data = cache.get("files", {})
    
    for filename, file_data in files_data.items():
        fingerprint = get_fingerprint_for_algorithm(file_data, required_algorithm)
        coverage[filename] = fingerprint is not None
    
    return coverage

def get_fingerprint_for_algorithm(file_data: Dict, algorithm: str) -> Optional[List[float]]:
    """
    Safely retrieve a fingerprint for a specific algorithm from file data.
    
    Args:
        file_data: File data from fingerprint cache
        algorithm: Algorithm name to retrieve fingerprint for
        
    Returns:
        Fingerprint list if available for the algorithm, None otherwise
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
    Old format: cache["files"][filename]["fingerprint"] = [...]
    New format: cache["files"][filename]["fingerprints"] = {"algorithm": [...], ...}
    """
    if "files" not in cache:
        return cache
    
    migrated = False
    for filename, file_data in cache["files"].items():
        if isinstance(file_data, dict) and "fingerprint" in file_data and "fingerprints" not in file_data:
            # Migrate from old format
            old_fingerprint = file_data["fingerprint"]
            # Assume old fingerprint was from the spectral algorithm (default)
            file_data["fingerprints"] = {DEFAULT_ALGORITHM: old_fingerprint}
            # Remove old key
            del file_data["fingerprint"]
            migrated = True
    
    if migrated:
        log_print("Migrated fingerprint cache to new multi-algorithm format")
    
    return cache

def load_fingerprint_cache(dirpath: Path) -> Dict:
    """Load fingerprint cache from directory."""
    data = load_json(dirpath / FINGERPRINTS_JSON, None)
    cache = data if isinstance(data, dict) and "files" in data else {"version": 1, "files": {}, "excluded_files": []}
    
    # Ensure excluded_files field exists
    if "excluded_files" not in cache:
        cache["excluded_files"] = []
    
    # Migrate old format if needed
    cache = migrate_fingerprint_cache(cache)
    
    return cache

def save_fingerprint_cache(dirpath: Path, cache: Dict) -> None:
    """Save fingerprint cache to directory."""
    save_json(dirpath / FINGERPRINTS_JSON, cache)

def is_file_excluded_from_fingerprinting(dirpath: Path, filename: str) -> bool:
    """Check if a file is excluded from fingerprinting in a directory."""
    cache = load_fingerprint_cache(dirpath)
    excluded_files = cache.get("excluded_files", [])
    return filename in excluded_files

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
    
    # Check immediate subdirectories
    try:
        for item in root_path.iterdir():
            if item.is_dir() and (item / FINGERPRINTS_JSON).exists():
                practice_folders.append(item)
    except (OSError, PermissionError):
        pass  # Skip directories we can't read
    
    return practice_folders

def discover_directories_with_audio_files(root_path: Path) -> List[Path]:
    """
    Recursively discover all directories that contain audio files.
    Returns list of directories that have .wav, .wave, or .mp3 files.
    """
    directories_with_audio = []
    if not root_path.exists() or not root_path.is_dir():
        return directories_with_audio
    
    def scan_directory(directory: Path):
        """Recursively scan directory for audio files."""
        try:
            has_audio_files = False
            subdirectories = []
            
            for item in directory.iterdir():
                if item.is_file() and item.suffix.lower() in AUDIO_EXTS:
                    has_audio_files = True
                elif item.is_dir():
                    # Skip hidden directories and common non-audio directories
                    if not item.name.startswith('.') and item.name.lower() not in {'__pycache__', 'node_modules', '.git'}:
                        subdirectories.append(item)
            
            # Add this directory if it contains audio files
            if has_audio_files:
                directories_with_audio.append(directory)
            
            # Recursively scan subdirectories
            for subdir in subdirectories:
                scan_directory(subdir)
                
        except (OSError, PermissionError):
            # Skip directories we can't read
            pass
    
    scan_directory(root_path)
    return directories_with_audio

def collect_fingerprints_from_folders(folder_paths: List[Path], algorithm: str, exclude_dir: Optional[Path] = None) -> Dict[str, List[Dict]]:
    """
    Collect fingerprints from multiple folders and organize by filename.
    
    ALGORITHM CONSISTENCY: This function only collects fingerprints that were generated
    using the specified algorithm, ensuring that all returned fingerprints are comparable.
    
    Args:
        folder_paths: List of directories to scan for fingerprints
        algorithm: Which fingerprint algorithm to use (e.g., 'spectral', 'lightweight')
                  Only fingerprints generated with this algorithm will be collected
        exclude_dir: Optional directory to exclude from collection
    
    Returns:
        Dictionary mapping filename -> list of {fingerprint, folder_path, file_data, provided_name}
        All fingerprints in the result were generated using the same algorithm.
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
        excluded_files = cache.get("excluded_files", [])
        
        # Load provided names from this folder
        names_json_path = folder_path / NAMES_JSON
        provided_names = load_json(names_json_path, {}) or {}
        
        for filename, file_data in files_data.items():
            # Skip files that are marked as excluded
            if filename in excluded_files:
                continue
                
            # Get fingerprint for the selected algorithm using safer method
            fingerprint = get_fingerprint_for_algorithm(file_data, algorithm)
            if fingerprint:  # Only include files with fingerprint for this algorithm
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

# ========== Backup System ==========
def create_backup_folder_name(practice_folder: Path) -> Path:
    """
    Create a unique backup folder name with format .backup/YYYY-MM-DD-###
    
    Backups are created in each practice folder under .backup/ directory.
    The format ensures chronological ordering and prevents conflicts when
    multiple backups are created on the same day.
    
    Args:
        practice_folder: Practice folder where the backup will be created
        
    Returns:
        Path to the backup folder (not yet created)
    """
    today = datetime.now()
    date_str = today.strftime("%Y-%m-%d")
    backups_dir = practice_folder / ".backup"
    
    # Find the next available number for today
    counter = 1
    while True:
        backup_folder = backups_dir / f"{date_str}-{counter:03d}"
        if not backup_folder.exists():
            return backup_folder
        counter += 1

def get_metadata_files_to_backup(practice_folder: Path) -> List[Path]:
    """
    Get list of metadata files that exist in the practice folder and might change.
    
    This includes:
    - .provided_names.json (file naming data)
    - .duration_cache.json (playback duration cache)
    - .waveform_cache.json (waveform visualization cache)
    - .audio_fingerprints.json (audio fingerprint data)
    - .audio_notes_<username>.json (user-specific annotation data)
    
    Excludes any files in .backup or .backups directories.
    
    Args:
        practice_folder: Directory to scan for metadata files
        
    Returns:
        List of Path objects for existing metadata files
    """
    # Skip backup directories entirely
    if practice_folder.name in ['.backup', '.backups']:
        return []
    
    metadata_files = []
    
    # List of all possible metadata files
    possible_files = [
        practice_folder / NAMES_JSON,
        practice_folder / DURATIONS_JSON,
        practice_folder / WAVEFORM_JSON,
        practice_folder / FINGERPRINTS_JSON,
    ]
    
    # Add user-specific annotation files
    username = getpass.getuser()
    user_notes_file = practice_folder / f".audio_notes_{username}.json"
    possible_files.append(user_notes_file)
    
    # Also check for any other user-specific annotation files
    for json_file in practice_folder.glob(".audio_notes_*.json"):
        if json_file not in possible_files:
            possible_files.append(json_file)
    
    # Only include files that actually exist and are not in backup directories
    for file_path in possible_files:
        if file_path.exists() and file_path.is_file():
            # Make sure the file is not in a backup directory
            if not any(part in ['.backup', '.backups'] for part in file_path.parts):
                metadata_files.append(file_path)
    
    return metadata_files

def backup_metadata_files(practice_folder: Path, backup_base_folder: Path) -> int:
    """
    Backup metadata files from practice_folder to backup_base_folder.
    Returns the number of files backed up.
    """
    metadata_files = get_metadata_files_to_backup(practice_folder)
    
    if not metadata_files:
        return 0  # No files to backup
    
    # Create the backup directory
    backup_base_folder.mkdir(parents=True, exist_ok=True)
    
    backed_up_count = 0
    for metadata_file in metadata_files:
        try:
            backup_file_path = backup_base_folder / metadata_file.name
            # Copy the file
            backup_file_path.write_bytes(metadata_file.read_bytes())
            backed_up_count += 1
        except Exception as e:
            log_print(f"Warning: Failed to backup {metadata_file}: {e}")
    
    return backed_up_count

def should_create_backup(practice_folder: Path) -> bool:
    """
    Determine if a backup should be created for this practice folder.
    Only create backup if there are metadata files that could change.
    """
    return len(get_metadata_files_to_backup(practice_folder)) > 0

def create_metadata_backup_if_needed(practice_folder: Path) -> Optional[Path]:
    """
    Create a backup of metadata files if needed.
    
    This function implements the main backup logic:
    1. Check if there are metadata files that could change
    2. If yes, create a timestamped backup folder in the practice folder
    3. Copy all existing metadata files to the backup location
    
    Args:
        practice_folder: Current practice session folder where backup will be created
        
    Returns:
        Path to created backup folder if backup was created, None otherwise
    """
    if not should_create_backup(practice_folder):
        return None
    
    backup_folder = create_backup_folder_name(practice_folder)
    backed_up_count = backup_metadata_files(practice_folder, backup_folder)
    
    if backed_up_count > 0:
        return backup_folder
    else:
        # Clean up empty backup folder
        try:
            backup_folder.rmdir()
            # Also try to remove parent .backup directory if it's empty
            backup_folder.parent.rmdir()
        except Exception:
            pass
        return None

def discover_available_backups(root_path: Path) -> List[Tuple[Path, str]]:
    """
    Discover all available backup folders in all practice folders.
    
    Searches for .backup directories within the root practice directory tree.
    
    Args:
        root_path: Root band practice directory to search for .backup folders
        
    Returns:
        List of tuples (backup_folder_path, formatted_display_name) sorted by date descending
    """
    backups = []
    
    # Search for .backup directories recursively
    for backup_dir in root_path.rglob(".backup"):
        if backup_dir.is_dir():
            # Look for dated backup folders within each .backup directory
            for backup_folder in backup_dir.iterdir():
                if backup_folder.is_dir():
                    # Parse folder name format: YYYY-MM-DD-###
                    try:
                        # Extract timestamp info for display
                        folder_name = backup_folder.name
                        date_part = folder_name.rsplit('-', 1)[0]  # Remove counter
                        date_obj = datetime.strptime(date_part, "%Y-%m-%d")
                        
                        # Get relative path from root for display
                        practice_folder = backup_dir.parent
                        rel_practice = practice_folder.relative_to(root_path)
                        practice_name = str(rel_practice) if str(rel_practice) != "." else "Root"
                        
                        # Create display name with date and practice folder
                        display_name = f"{date_obj.strftime('%A, %B %d, %Y')} ({folder_name}) - {practice_name}"
                        backups.append((backup_folder, display_name))
                        
                    except (ValueError, IndexError):
                        # If folder doesn't match expected format, include it anyway
                        practice_folder = backup_dir.parent
                        rel_practice = practice_folder.relative_to(root_path)
                        practice_name = str(rel_practice) if str(rel_practice) != "." else "Root"
                        display_name = f"{backup_folder.name} - {practice_name}"
                        backups.append((backup_folder, display_name))
    
    # Sort by folder name (which includes timestamp) in descending order
    backups.sort(key=lambda x: x[0].name, reverse=True)
    return backups

def get_backup_contents(backup_folder: Path, root_path: Path) -> Dict[Path, List[Path]]:
    """
    Get the contents of a backup folder organized by practice folder.
    
    Args:
        backup_folder: Path to specific backup folder
        root_path: Root band practice directory for relative path resolution
        
    Returns:
        Dictionary mapping practice folder paths to lists of backup files
    """
    contents = {}
    
    if not backup_folder.exists():
        return contents
    
    # The backup folder is in a practice folder's .backup directory
    # So the practice folder is backup_folder.parent.parent
    practice_folder = backup_folder.parent.parent
    
    # Walk through backup folder to find all backed up files
    for backup_file in backup_folder.glob("*.json"):
        if backup_file.is_file():
            if practice_folder not in contents:
                contents[practice_folder] = []
            contents[practice_folder].append(backup_file)
    
    return contents

def restore_metadata_from_backup(backup_folder: Path, target_practice_folder: Path, root_path: Path) -> int:
    """
    Restore metadata files from a backup folder to the target practice folder.
    
    Args:
        backup_folder: Path to the backup folder containing the files
        target_practice_folder: Practice folder where files should be restored
        root_path: Root band practice directory for path resolution
        
    Returns:
        Number of files successfully restored
    """
    if not backup_folder.exists():
        return 0
    
    restored_count = 0
    # Copy all JSON files from backup to target folder
    for backup_file in backup_folder.glob("*.json"):
        try:
            target_file = target_practice_folder / backup_file.name
            target_file.write_bytes(backup_file.read_bytes())
            restored_count += 1
            log_print(f"Restored: {backup_file.name}")
        except Exception as e:
            log_print(f"Warning: Failed to restore {backup_file.name}: {e}")
    
    return restored_count

# ========== Waveform worker ==========
class WaveformWorker(QObject):
    progress = pyqtSignal(int, str, list, int, int, bool)  # Added bool for stereo mode
    finished = pyqtSignal(int, str, list, int, int, int, int, bool, bool)  # Added bool for has_stereo_data
    error = pyqtSignal(int, str, str)

    def __init__(self, gen_id: int, path_str: str, columns: int, stereo: bool = False):
        super().__init__()
        self._gen_id = int(gen_id)
        self._path_str = path_str
        self._columns = int(columns)
        self._stereo = stereo

    def run(self):
        try:
            p = Path(self._path_str)
            
            # First, quickly determine stereo availability without full decode
            channel_count = get_audio_channel_count(p)
            has_stereo_data = channel_count >= 2
            
            # Only decode stereo if we're actually generating stereo peaks
            need_stereo_decode = self._stereo and has_stereo_data
            samples, _sr, dur_ms, stereo_samples = decode_audio_samples(p, stereo=need_stereo_decode)
            
            if self._stereo and stereo_samples:
                # Stereo mode - generate stereo peaks
                peaks_all: List[List[List[float]]] = []
                CHUNK = 100
                for start, chunk_peaks in compute_peaks_progressive(samples, self._columns, CHUNK, stereo_samples):
                    for peak_data in chunk_peaks:
                        # Convert to serializable format: [[L_min, L_max], [R_min, R_max]]
                        peaks_all.append([[float(peak_data[0][0]), float(peak_data[0][1])], 
                                        [float(peak_data[1][0]), float(peak_data[1][1])]])
                    done = start + len(chunk_peaks)
                    self.progress.emit(self._gen_id, self._path_str, chunk_peaks, int(done), int(self._columns), True)
            else:
                # Mono mode - generate mono peaks
                peaks_all: List[List[float]] = []
                CHUNK = 100
                for start, chunk_peaks in compute_peaks_progressive(samples, self._columns, CHUNK):
                    for a, b in chunk_peaks:
                        peaks_all.append([float(a), float(b)])
                    done = start + len(chunk_peaks)
                    self.progress.emit(self._gen_id, self._path_str, chunk_peaks, int(done), int(self._columns), False)
            
            size, mtime = file_signature(p)
            self.finished.emit(self._gen_id, self._path_str, peaks_all, int(dur_ms), int(self._columns), int(size), int(mtime), self._stereo, has_stereo_data)
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

# ========== Mono convert worker ==========
class MonoConvertWorker(QObject):
    progress = pyqtSignal(int, int, str)  # done, total, filename
    file_done = pyqtSignal(str, bool, str)  # filename, success, error_msg
    finished = pyqtSignal(bool)  # canceled?

    def __init__(self, audio_path: str):
        super().__init__()
        self._path = str(audio_path)
        self._cancel = False

    def cancel(self): 
        self._cancel = True

    def run(self):
        if self._cancel: 
            self.finished.emit(True)
            return
            
        src = Path(self._path)
        self.progress.emit(0, 1, src.name)
        
        try:
            # Load the audio file
            audio = AudioSegment.from_file(str(src))
            
            # Check if already mono
            if audio.channels == 1:
                self.file_done.emit(src.name, False, "File is already mono")
                self.finished.emit(False)
                return
            
            # Convert to mono
            mono_audio = audio.set_channels(1)
            
            # Create backup filename
            base = src.stem
            backup_name = f"{base}_stereo{src.suffix}"
            backup_path = src.with_name(backup_name)
            
            # Make sure backup doesn't already exist
            n = 1
            while backup_path.exists():
                backup_name = f"{base}_stereo({n}){src.suffix}"
                backup_path = src.with_name(backup_name)
                n += 1
            
            # Rename original to backup
            src.rename(backup_path)
            
            # Export mono version with original filename
            if src.suffix.lower() in ('.mp3',):
                mono_audio.export(str(src), format="mp3", bitrate="128k")
            else:
                mono_audio.export(str(src), format="wav")
            
            self.file_done.emit(src.name, True, f"Converted to mono (stereo backup: {backup_name})")
            
        except Exception as e:
            self.file_done.emit(src.name, False, str(e))
        
        self.progress.emit(1, 1, src.name)
        self.finished.emit(False)

# ========== Fingerprint worker ==========
class FingerprintWorker(QObject):
    progress = pyqtSignal(int, int, str)  # current_index, total_files, filename
    file_done = pyqtSignal(str, bool, str)  # filename, success, error_msg
    finished = pyqtSignal(int, bool)  # generated_count, canceled

    def __init__(self, audio_files: List[str], current_dir: str, force_regenerate: bool):
        super().__init__()
        self._audio_files = [str(p) for p in audio_files]
        self._current_dir = Path(current_dir)
        self._force_regenerate = bool(force_regenerate)
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def run(self):
        cache = load_fingerprint_cache(self._current_dir)
        generated = 0
        total_files = len(self._audio_files)
        
        for i, audio_file_str in enumerate(self._audio_files):
            if self._cancel:
                self.finished.emit(generated, True)
                return
                
            audio_file = Path(audio_file_str)
            self.progress.emit(i, total_files, audio_file.name)
            
            try:
                # Check if fingerprint already exists and is up to date (unless force regenerating)
                size, mtime = file_signature(audio_file)
                existing = cache["files"].get(audio_file.name)
                if not self._force_regenerate and existing and existing.get("size") == size and existing.get("mtime") == mtime:
                    self.file_done.emit(audio_file.name, True, "Skipped (already cached)")
                    continue  # Skip if already cached and file unchanged
                
                # Generate fingerprints for multiple algorithms
                samples, sr, dur_ms, _ = decode_audio_samples(audio_file)  # Only need mono for fingerprinting
                
                # Get existing fingerprints for this file (if any)
                existing_entry = cache["files"].get(audio_file.name, {})
                existing_fingerprints = existing_entry.get("fingerprints", {})
                
                # Generate all algorithms if force regenerate, otherwise only missing ones
                if self._force_regenerate:
                    algorithms_to_generate = list(FINGERPRINT_ALGORITHMS.keys())
                else:
                    algorithms_to_generate = [alg for alg in FINGERPRINT_ALGORITHMS.keys() 
                                              if alg not in existing_fingerprints]
                
                if algorithms_to_generate:
                    new_fingerprints = compute_multiple_fingerprints(samples, sr, algorithms_to_generate)
                    
                    # Merge with existing fingerprints
                    all_fingerprints = existing_fingerprints.copy()
                    all_fingerprints.update(new_fingerprints)
                    
                    # Store in cache
                    cache["files"][audio_file.name] = {
                        "fingerprints": all_fingerprints,
                        "size": size,
                        "mtime": mtime,
                        "duration_ms": dur_ms
                    }
                    generated += 1
                    self.file_done.emit(audio_file.name, True, f"Generated {len(algorithms_to_generate)} algorithm(s)")
                else:
                    self.file_done.emit(audio_file.name, True, "Skipped (all algorithms already cached)")
                
            except Exception as e:
                error_msg = f"Error generating fingerprint: {e}"
                log_print(f"Error generating fingerprint for {audio_file.name}: {e}")
                self.file_done.emit(audio_file.name, False, error_msg)
        
        # Save the cache after processing all files
        save_fingerprint_cache(self._current_dir, cache)
        self.finished.emit(generated, False)

# ========== Auto-generation workers ==========
class AutoWaveformWorker(QObject):
    """Worker to automatically generate waveforms for all audio files in a folder"""
    progress = pyqtSignal(int, int, str)  # current_index, total_files, filename
    file_done = pyqtSignal(str, bool, str)  # filename, success, error_msg
    finished = pyqtSignal(int, bool)  # generated_count, canceled

    def __init__(self, audio_files: List[str], folder_path: str):
        super().__init__()
        self._audio_files = audio_files[:]
        self._folder_path = folder_path
        self._canceled = False

    def cancel(self):
        self._canceled = True

    def run(self):
        generated_count = 0
        
        for i, audio_file in enumerate(self._audio_files):
            if self._canceled:
                self.finished.emit(generated_count, True)
                return
                
            filename = Path(audio_file).name
            self.progress.emit(i, len(self._audio_files), filename)
            
            try:
                # Check if waveform cache files already exist
                audio_path = Path(audio_file)
                mono_cache_file = audio_path.parent / f".waveform_cache_{audio_path.stem}.json"
                stereo_cache_file = audio_path.parent / f".waveform_cache_{audio_path.stem}_stereo.json"
                
                # Skip if both caches exist (don't regenerate existing waveforms)
                if mono_cache_file.exists() and stereo_cache_file.exists():
                    self.file_done.emit(filename, True, "Already cached")
                    continue
                
                # Generate actual waveform data using existing logic
                channel_count = get_audio_channel_count(audio_path)
                has_stereo_data = channel_count >= 2
                
                # Generate mono waveform if not exists
                if not mono_cache_file.exists():
                    try:
                        samples, _sr, dur_ms, _ = decode_audio_samples(audio_path, stereo=False)
                        
                        # Generate mono peaks
                        all_peaks = []
                        for start, chunk_peaks in compute_peaks_progressive(samples, WAVEFORM_COLUMNS, 100):
                            all_peaks.extend(chunk_peaks)
                        
                        mono_data = {
                            "peaks": all_peaks,
                            "duration_ms": dur_ms,
                            "columns": WAVEFORM_COLUMNS,
                            "stereo": False
                        }
                        
                        with open(mono_cache_file, 'w') as f:
                            json.dump(mono_data, f)
                            
                    except Exception as e:
                        self.file_done.emit(filename, False, f"Error generating mono waveform: {e}")
                        continue
                        
                # Generate stereo waveform if not exists and file has stereo data
                if not stereo_cache_file.exists() and has_stereo_data:
                    try:
                        samples, _sr, dur_ms, stereo_samples = decode_audio_samples(audio_path, stereo=True)
                        
                        # Generate stereo peaks
                        all_peaks = []
                        for start, chunk_peaks in compute_peaks_progressive(samples, WAVEFORM_COLUMNS, 100, stereo_samples):
                            all_peaks.extend(chunk_peaks)
                        
                        stereo_data = {
                            "peaks": all_peaks,
                            "duration_ms": dur_ms,
                            "columns": WAVEFORM_COLUMNS,
                            "stereo": True
                        }
                        
                        with open(stereo_cache_file, 'w') as f:
                            json.dump(stereo_data, f)
                            
                    except Exception as e:
                        self.file_done.emit(filename, False, f"Error generating stereo waveform: {e}")
                        continue
                elif not has_stereo_data:
                    # Create placeholder stereo file indicating no stereo data
                    stereo_data = {"peaks": [], "duration_ms": 0, "stereo": False, "no_stereo_data": True}
                    try:
                        with open(stereo_cache_file, 'w') as f:
                            json.dump(stereo_data, f)
                    except Exception as e:
                        pass  # Not critical if placeholder creation fails
                
                generated_count += 1
                self.file_done.emit(filename, True, "Generated")
                
            except Exception as e:
                self.file_done.emit(filename, False, str(e))
        
        self.finished.emit(generated_count, False)

class AutoFingerprintWorker(QObject):
    """Worker to automatically generate fingerprints for all audio files in a folder"""
    progress = pyqtSignal(int, int, str)  # current_index, total_files, filename
    file_done = pyqtSignal(str, bool, str)  # filename, success, error_msg
    finished = pyqtSignal(int, bool)  # generated_count, canceled

    def __init__(self, audio_files: List[str], folder_path: str):
        super().__init__()
        self._audio_files = audio_files[:]
        self._folder_path = folder_path
        self._canceled = False

    def cancel(self):
        self._canceled = True

    def run(self):
        generated_count = 0
        
        # Load existing fingerprint cache
        cache_path = Path(self._folder_path) / FINGERPRINTS_JSON
        cache = load_fingerprint_cache(self._folder_path)
        
        for i, audio_file in enumerate(self._audio_files):
            if self._canceled:
                self.finished.emit(generated_count, True)
                return
                
            filename = Path(audio_file).name
            self.progress.emit(i, len(self._audio_files), filename)
            
            try:
                # Check if fingerprint already exists in cache
                if filename in cache:
                    self.file_done.emit(filename, True, "Already cached")
                    continue
                
                # Generate fingerprint (reuses existing logic)
                try:
                    # Load existing cache properly
                    if "files" not in cache:
                        cache["files"] = {}
                        
                    # Check if fingerprint already exists in cache  
                    if filename in cache["files"]:
                        self.file_done.emit(filename, True, "Already cached")
                        continue
                    
                    # Decode audio and generate fingerprints
                    samples, sr, dur_ms, _ = decode_audio_samples(audio_file)
                    
                    # Generate all algorithms
                    new_fingerprints = compute_multiple_fingerprints(samples, sr, list(FINGERPRINT_ALGORITHMS.keys()))
                    
                    if new_fingerprints:
                        # Get file signature
                        size, mtime = file_signature(Path(audio_file))
                        
                        cache["files"][filename] = {
                            "fingerprints": new_fingerprints,
                            "size": size,
                            "mtime": mtime,
                            "duration_ms": dur_ms
                        }
                        generated_count += 1
                        self.file_done.emit(filename, True, "Generated")
                    else:
                        self.file_done.emit(filename, False, "No fingerprints generated")
                        
                except Exception as e:
                    self.file_done.emit(filename, False, str(e))
                    
            except Exception as e:
                self.file_done.emit(filename, False, str(e))
        
        # Save updated cache
        try:
            save_fingerprint_cache(self._folder_path, cache)
        except Exception as e:
            # Don't fail completely if cache save fails
            pass
            
        self.finished.emit(generated_count, False)

# ========== Waveform view ==========
class WaveformView(QWidget):
    markerMoved = pyqtSignal(str, int, int)     # set_id, uid, ms
    markerReleased = pyqtSignal(str, int, int)  # set_id, uid, ms
    annotationClicked = pyqtSignal(str, int)    # set_id, uid
    seekRequested = pyqtSignal(int)             # ms
    waveformReady = pyqtSignal()                # Emitted when waveform data is loaded

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(140)
        # Enable focus so the widget can receive keyboard events
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._peaks: Optional[List] = None  # Can be mono or stereo format
        self._peaks_loading: List = []
        self._duration_ms: int = 0
        self._pixmap: Optional[QPixmap] = None
        self._pixmap_w: int = 0
        
        # Stereo mode support
        self._stereo_mode: bool = False
        self._has_stereo_data: bool = False

        # Use standardized colors for consistency across machines
        waveform_colors = _color_manager.get_waveform_colors()
        self._bg = waveform_colors['background']
        self._axis = waveform_colors['axis'] 
        self._wave = waveform_colors['left_channel']  # Default wave color
        self._playhead = waveform_colors['playhead']
        self._msg_color = waveform_colors['message']
        self._selected_color = waveform_colors['selected']
        
        # Stereo channel colors
        self._left_color = waveform_colors['left_channel']
        self._right_color = waveform_colors['right_channel']

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
        self._has_stereo_data = False
        self.update()

    def set_stereo_mode(self, enabled: bool):
        """Toggle between mono and stereo waveform display."""
        if self._stereo_mode == enabled:
            return
        
        self._stereo_mode = enabled
        
        # If we have a file loaded, try to use cached data for the new mode
        if self._path and self._path.exists():
            # Check if we can switch modes without regenerating waveform data
            cache = load_waveform_cache(self._path.parent)
            entry = cache["files"].get(self._path.name)
            size, mtime = file_signature(self._path)
            
            # Check if cached data exists for the new mode
            new_cache_key = "stereo_peaks" if enabled else "peaks"
            if (entry and entry.get("columns") == WAVEFORM_COLUMNS and 
                int(entry.get("size", 0)) == size and int(entry.get("mtime", 0)) == mtime and 
                isinstance(entry.get(new_cache_key), list)):
                
                # We have cached data for the new mode, use it directly
                self._peaks = entry[new_cache_key]
                self._duration_ms = int(entry.get("duration_ms", 0))
                
                # Update stereo availability info
                if "has_stereo_data" in entry:
                    self._has_stereo_data = bool(entry.get("has_stereo_data", False))
                else:
                    # Detect quickly without full decode
                    try:
                        channel_count = get_audio_channel_count(self._path)
                        self._has_stereo_data = channel_count >= 2
                    except Exception:
                        self._has_stereo_data = False
                
                self._state = "ready"
                self._pixmap = None  # Force pixmap regeneration for new mode
                self.update()
                return
            
            # No cached data for new mode, need to regenerate
            self.set_audio_file(self._path)
        else:
            # Just update display with current data
            self._pixmap = None
            self.update()

    def get_stereo_mode(self) -> bool:
        """Return current stereo mode status."""
        return self._stereo_mode

    def has_stereo_data(self) -> bool:
        """Return whether current file has stereo data available."""
        return self._has_stereo_data

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
        
        # Check if we have cached data for the current mode
        cache_key = "stereo_peaks" if self._stereo_mode else "peaks"
        
        if entry and entry.get("columns") == WAVEFORM_COLUMNS and \
           int(entry.get("size", 0)) == size and int(entry.get("mtime", 0)) == mtime and \
           isinstance(entry.get(cache_key), list) and isinstance(entry.get("duration_ms"), int):
            
            self._peaks = entry[cache_key]
            self._duration_ms = int(entry["duration_ms"])
            
            # Check stereo availability - use cached value if available, otherwise detect quickly
            if "has_stereo_data" in entry:
                self._has_stereo_data = bool(entry.get("has_stereo_data", False))
            else:
                # For backward compatibility, detect stereo availability without full decode
                try:
                    channel_count = get_audio_channel_count(path)
                    self._has_stereo_data = channel_count >= 2
                    # Update cache with stereo availability for future use
                    entry["has_stereo_data"] = self._has_stereo_data
                    cache["files"][path.name] = entry
                    save_waveform_cache(path.parent, cache)
                except Exception:
                    self._has_stereo_data = False
            
            self._state = "ready"; self._msg = ""
            self.update()
            
            # Notify that waveform data is ready (from cache)
            self.waveformReady.emit()
            return

        self._duration_ms = 0
        self._state = "loading"; self._msg = "Analyzing waveform…"
        self.update()

        self._active_gen_id = self._gen_id_counter = (self._gen_id_counter + 1) % (1 << 31)
        self._start_worker(self._active_gen_id, path)

    def _start_worker(self, gen_id: int, path: Path):
        thread = QThread(self)
        worker = WaveformWorker(gen_id, str(path), WAVEFORM_COLUMNS, stereo=self._stereo_mode)
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

    def _on_worker_progress(self, gen_id: int, path_str: str, new_chunk: list, done_cols: int, total_cols: int, is_stereo: bool = False):
        if gen_id != self._active_gen_id or not self._path or str(self._path) != path_str:
            return
        
        if is_stereo:
            # Stereo format: each item is [[L_min, L_max], [R_min, R_max]]
            for item in new_chunk:
                try: 
                    self._peaks_loading.append(item)
                except Exception: continue
        else:
            # Mono format: each item is [min, max]
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

    def _on_worker_finished(self, gen_id: int, path_str: str, peaks: list, duration_ms: int, columns: int, size: int, mtime: int, is_stereo: bool = False, has_stereo_data: bool = False):
        if gen_id != self._active_gen_id or not self._path or str(self._path) != path_str:
            return
        
        self._peaks = peaks
        self._duration_ms = int(duration_ms)
        self._state = "ready"; self._msg = ""
        
        # Use the stereo data availability passed from the worker
        self._has_stereo_data = has_stereo_data
        
        # Update cache with both mono and stereo data
        cache = load_waveform_cache(self._path.parent)
        file_entry = cache["files"].get(self._path.name, {})
        
        file_entry.update({
            "columns": int(columns),
            "size": int(size),
            "mtime": int(mtime),
            "duration_ms": int(duration_ms),
            "has_stereo_data": self._has_stereo_data
        })
        
        if is_stereo:
            file_entry["stereo_peaks"] = peaks
        else:
            file_entry["peaks"] = peaks
        
        cache["files"][self._path.name] = file_entry
        save_waveform_cache(self._path.parent, cache)
        self._pixmap = None; self.update()
        
        # Notify that waveform data is ready (including stereo availability)
        self.waveformReady.emit()

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
        
        if self._state == "ready" and self._peaks:
            self._draw_waveform(p, W, H, self._peaks)
        elif self._state == "loading":
            if self._peaks_loading:
                self._draw_waveform(p, W, H, self._peaks_loading, loading=True)
            p.setPen(self._msg_color)
            p.drawText(QRect(0, 0, W, H), Qt.AlignmentFlag.AlignCenter, self._msg or "Analyzing waveform…")
        else:
            # Draw axis line for empty state
            mid = H // 2
            pen_axis = QPen(self._axis); pen_axis.setWidth(1)
            p.setPen(pen_axis); p.drawLine(0, mid, W, mid)
            p.setPen(self._msg_color)
            p.drawText(QRect(0, 0, W, H), Qt.AlignmentFlag.AlignCenter, self._msg or "No waveform")

        p.end()
        self._pixmap = pm; self._pixmap_w = W

    def _draw_waveform(self, painter: QPainter, W: int, H: int, peaks_data: List, loading: bool = False):
        """Draw waveform based on current mode (mono/stereo)."""
        if not peaks_data:
            return
        
        # Check if this is stereo data
        is_stereo = len(peaks_data) > 0 and isinstance(peaks_data[0], list) and len(peaks_data[0]) == 2 and isinstance(peaks_data[0][0], list)
        
        if self._stereo_mode and is_stereo:
            # Stereo mode - draw left and right channels separately
            self._draw_stereo_waveform(painter, W, H, peaks_data, loading)
        else:
            # Mono mode - draw single waveform
            self._draw_mono_waveform(painter, W, H, peaks_data, loading)

    def _draw_mono_waveform(self, painter: QPainter, W: int, H: int, peaks_data: List, loading: bool = False):
        """Draw mono waveform."""
        mid = H // 2
        pen_axis = QPen(self._axis); pen_axis.setWidth(1)
        painter.setPen(pen_axis); painter.drawLine(0, mid, W, mid)
        
        pen_wave = QPen(self._wave); pen_wave.setWidth(WAVEFORM_STROKE_WIDTH); painter.setPen(pen_wave)
        
        if loading:
            partial = resample_peaks(peaks_data, min(W, max(1, self._done_cols)))
            draw_peaks = resample_peaks(partial, W)
        else:
            draw_peaks = resample_peaks(peaks_data, W)
        
        for x, peak_data in enumerate(draw_peaks):
            if isinstance(peak_data, (tuple, list)) and len(peak_data) >= 2:
                mn, mx = peak_data[0], peak_data[1]
            else:
                continue
            y1 = int(mid - mn * (H/2-2)); y2 = int(mid - mx * (H/2-2))
            if y1 > y2: y1, y2 = y2, y1
            painter.drawLine(x, y1, x, y2)

    def _draw_stereo_waveform(self, painter: QPainter, W: int, H: int, peaks_data: List, loading: bool = False):
        """Draw stereo waveform with separate left and right channels."""
        # Split height for left and right channels
        quarter = H // 4
        left_mid = quarter
        right_mid = 3 * quarter
        
        # Draw axis lines for both channels
        pen_axis = QPen(self._axis); pen_axis.setWidth(1)
        painter.setPen(pen_axis)
        painter.drawLine(0, left_mid, W, left_mid)    # Left channel axis
        painter.drawLine(0, right_mid, W, right_mid)  # Right channel axis
        painter.drawLine(0, H//2, W, H//2)            # Center divider
        
        if loading:
            partial = resample_peaks(peaks_data, min(W, max(1, self._done_cols)))
            draw_peaks = resample_peaks(partial, W)
        else:
            draw_peaks = resample_peaks(peaks_data, W)
        
        for x, peak_data in enumerate(draw_peaks):
            if not isinstance(peak_data, list) or len(peak_data) != 2:
                continue
            
            left_peak, right_peak = peak_data
            if not (isinstance(left_peak, list) and isinstance(right_peak, list)):
                continue
                
            if len(left_peak) >= 2 and len(right_peak) >= 2:
                # Draw left channel (top half)
                pen_left = QPen(self._left_color); pen_left.setWidth(WAVEFORM_STROKE_WIDTH)
                painter.setPen(pen_left)
                left_mn, left_mx = left_peak[0], left_peak[1]
                y1 = int(left_mid - left_mn * (quarter-2))
                y2 = int(left_mid - left_mx * (quarter-2))
                if y1 > y2: y1, y2 = y2, y1
                painter.drawLine(x, y1, x, y2)
                
                # Draw right channel (bottom half)
                pen_right = QPen(self._right_color); pen_right.setWidth(WAVEFORM_STROKE_WIDTH)
                painter.setPen(pen_right)
                right_mn, right_mx = right_peak[0], right_peak[1]
                y1 = int(right_mid - right_mn * (quarter-2))
                y2 = int(right_mid - right_mx * (quarter-2))
                if y1 > y2: y1, y2 = y2, y1
                painter.drawLine(x, y1, x, y2)

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
class FileInfoProxyModel(QSortFilterProxyModel):
    def __init__(self, parent_model: QFileSystemModel, duration_cache: Dict[str, int], audio_browser, parent=None):
        super().__init__(parent)
        self.setSourceModel(parent_model)
        self.duration_cache = duration_cache
        self.audio_browser = audio_browser  # Reference to get current practice folder
        
        # Cache for fingerprint exclusion data to avoid repeated disk I/O
        self._exclusion_cache: Dict[str, Tuple[set, float]] = {}  # dirpath -> (excluded_files_set, mtime)

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        """Filter out .backup and .backups folders from the file tree."""
        model = self.sourceModel()
        index = model.index(source_row, 0, source_parent)
        file_info = model.fileInfo(index)
        
        # Hide directories that start with .backup
        if file_info.isDir():
            folder_name = file_info.fileName()
            if folder_name.startswith('.backup'):
                return False
        
        return True

    def _is_file_excluded_cached(self, dirpath: Path, filename: str) -> bool:
        """Fast cached check for file exclusion from fingerprinting."""
        dirpath_str = str(dirpath)
        fingerprints_file = dirpath / FINGERPRINTS_JSON
        
        # Get current modification time of the fingerprints file
        try:
            current_mtime = fingerprints_file.stat().st_mtime if fingerprints_file.exists() else 0
        except OSError:
            current_mtime = 0
        
        # Check if we have valid cached data
        if dirpath_str in self._exclusion_cache:
            excluded_files, cached_mtime = self._exclusion_cache[dirpath_str]
            if cached_mtime == current_mtime:
                return filename in excluded_files
        
        # Cache is stale or missing, reload from disk
        try:
            cache = load_fingerprint_cache(dirpath)
            excluded_files = set(cache.get("excluded_files", []))
            self._exclusion_cache[dirpath_str] = (excluded_files, current_mtime)
            return filename in excluded_files
        except Exception:
            # On error, assume not excluded and cache empty set
            self._exclusion_cache[dirpath_str] = (set(), current_mtime)
            return False

    def invalidate_exclusion_cache(self, dirpath: Optional[Path] = None):
        """Invalidate exclusion cache for a specific directory or all directories."""
        if dirpath:
            self._exclusion_cache.pop(str(dirpath), None)
        else:
            self._exclusion_cache.clear()
    
    def _is_file_best_take(self, filename: str) -> bool:
        """Check if a file is marked as best take in any visible annotation set."""
        try:
            if not hasattr(self.audio_browser, 'annotation_sets'):
                return False
            for aset in self.audio_browser.annotation_sets:
                if not aset.get("visible", True):
                    continue  # Skip invisible sets
                file_meta = aset.get("files", {}).get(filename, {})
                if file_meta.get("best_take", False):
                    return True
            return False
        except Exception:
            return False
    
    def _is_file_partial_take(self, filename: str) -> bool:
        """Check if a file is marked as partial take in any visible annotation set."""
        try:
            if not hasattr(self.audio_browser, 'annotation_sets'):
                return False
            for aset in self.audio_browser.annotation_sets:
                if not aset.get("visible", True):
                    continue  # Skip invisible sets
                file_meta = aset.get("files", {}).get(filename, {})
                if file_meta.get("partial_take", False):
                    return True
            return False
        except Exception:
            return False

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            if section == 1: return "Size / Time"
            if section == 3: return "Date / Time Modified"
        return super().headerData(section, orientation, role)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return super().data(index, role)
            
        # Handle text color for excluded files
        if role == Qt.ItemDataRole.ForegroundRole and index.column() == 0:
            src = self.mapToSource(index)
            fi = self.sourceModel().fileInfo(src)  # type: ignore
            if fi.isFile() and f".{fi.suffix().lower()}" in AUDIO_EXTS:
                filename = fi.fileName()
                dirpath = Path(fi.absoluteFilePath()).parent
                if self._is_file_excluded_cached(dirpath, filename):
                    return QColor(128, 128, 128)  # Gray out excluded files
        
        # Handle bold font for best take files
        if role == Qt.ItemDataRole.FontRole and index.column() == 0:
            src = self.mapToSource(index)
            fi = self.sourceModel().fileInfo(src)  # type: ignore
            if fi.isFile() and f".{fi.suffix().lower()}" in AUDIO_EXTS:
                filename = fi.fileName()
                # Check if this file is marked as best take in any visible annotation set
                if self._is_file_best_take(filename):
                    from PyQt6.QtGui import QFont
                    font = QFont()
                    font.setBold(True)
                    return font
        
        # Handle tooltip for excluded files
        if role == Qt.ItemDataRole.ToolTipRole and index.column() == 0:
            src = self.mapToSource(index)
            fi = self.sourceModel().fileInfo(src)  # type: ignore
            if fi.isFile() and f".{fi.suffix().lower()}" in AUDIO_EXTS:
                filename = fi.fileName()
                dirpath = Path(fi.absoluteFilePath()).parent
                if self._is_file_excluded_cached(dirpath, filename):
                    return f"{filename}\n(Excluded from fingerprinting)"
        
        # Handle display text - add asterisk for partial takes
        if role == Qt.ItemDataRole.DisplayRole and index.column() == 0:
            src = self.mapToSource(index)
            fi = self.sourceModel().fileInfo(src)  # type: ignore
            if fi.isFile() and f".{fi.suffix().lower()}" in AUDIO_EXTS:
                filename = fi.fileName()
                # Check if this file is marked as partial take in any visible annotation set
                if self._is_file_partial_take(filename):
                    return f"{filename} *"
        
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

# ========== Backup Selection Dialog ==========
class BackupSelectionDialog(QMessageBox):
    """Dialog for selecting which backup to restore and where to restore it."""
    
    def __init__(self, available_backups: List[Tuple[Path, str]], current_folder: Path, root_path: Path, parent=None):
        super().__init__(parent)
        self.available_backups = available_backups
        self.current_folder = current_folder
        self.root_path = root_path
        self.selected_backup = None
        self.selected_folder = None
        
        self.setWindowTitle("Restore from Backup")
        self.setText("Select a backup to restore:")
        self.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        
        # Create custom widget for backup selection
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Backup selection
        layout.addWidget(QLabel("Available backups:"))
        self.backup_combo = QComboBox()
        for backup_path, display_name in available_backups:
            self.backup_combo.addItem(display_name, backup_path)
        layout.addWidget(self.backup_combo)
        
        # Folder selection
        layout.addWidget(QLabel("Restore to folder:"))
        self.folder_combo = QComboBox()
        
        # Populate folder options
        self.folder_combo.addItem(f"Current folder: {current_folder.relative_to(root_path) if current_folder != root_path else current_folder.name}", current_folder)
        
        # Add other practice folders that have backups
        try:
            selected_backup_path = available_backups[0][0] if available_backups else None
            if selected_backup_path:
                backup_contents = get_backup_contents(selected_backup_path, root_path)
                for folder_path in sorted(backup_contents.keys()):
                    if folder_path != current_folder:
                        folder_display = folder_path.relative_to(root_path) if folder_path != root_path else folder_path.name
                        self.folder_combo.addItem(f"Other folder: {folder_display}", folder_path)
        except Exception:
            pass  # If error getting backup contents, just show current folder
        
        layout.addWidget(self.folder_combo)
        
        # Add info label
        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)
        
        # Connect backup selection change to update folder options
        self.backup_combo.currentIndexChanged.connect(self._update_folder_options)
        self._update_folder_options()  # Initial update
        
        # Add the widget to the dialog
        self.layout().addWidget(widget, 1, 1)
    
    def _update_folder_options(self):
        """Update available folder options based on selected backup."""
        try:
            selected_backup = self.backup_combo.currentData()
            if not selected_backup:
                return
                
            # Clear current folder options except current folder (keep first item)
            while self.folder_combo.count() > 1:
                self.folder_combo.removeItem(1)
            
            # Get backup contents and add folders
            backup_contents = get_backup_contents(selected_backup, self.root_path)
            for folder_path in sorted(backup_contents.keys()):
                if folder_path != self.current_folder:
                    folder_display = folder_path.relative_to(self.root_path) if folder_path != self.root_path else folder_path.name
                    file_count = len(backup_contents[folder_path])
                    self.folder_combo.addItem(f"Other folder: {folder_display} ({file_count} files)", folder_path)
            
            # Update info label
            current_backup_contents = backup_contents.get(self.current_folder, [])
            if current_backup_contents:
                file_list = [f.name for f in current_backup_contents]
                self.info_label.setText(f"Files in backup for current folder:\n" + "\n".join(file_list))
            else:
                self.info_label.setText("No files found in backup for current folder.")
                
        except Exception as e:
            self.info_label.setText(f"Error reading backup contents: {str(e)}")
    
    def get_selection(self):
        """Return the selected backup path and target folder path."""
        return self.selected_backup, self.selected_folder
    
    def accept(self):
        """Handle OK button click."""
        self.selected_backup = self.backup_combo.currentData()
        self.selected_folder = self.folder_combo.currentData()
        super().accept()

# ========== Auto-Generation Settings Dialog ==========
class AutoGenerationSettingsDialog(QDialog):
    """Dialog for configuring auto-generation settings for the whole band practice folder."""
    
    def __init__(self, current_settings: dict, parent=None):
        super().__init__(parent)
        self.current_settings = current_settings
        self.result_settings = current_settings.copy()
        
        self.setWindowTitle("Auto-Generation Settings")
        self.setModal(True)
        self.resize(500, 300)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Description
        description = QLabel("Configure automatic generation settings for the entire band practice folder.")
        description.setWordWrap(True)
        main_layout.addWidget(description)
        
        main_layout.addWidget(QLabel(""))  # Spacer
        
        # Settings group
        colors = get_consistent_stylesheet_colors()
        settings_group = QWidget()
        settings_group.setStyleSheet(f"QWidget {{ background-color: {colors['bg_light']}; border: 1px solid {colors['border']}; border-radius: 5px; }}")
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.setContentsMargins(15, 15, 15, 15)
        
        # Auto-generation checkboxes
        options_row = QHBoxLayout()
        self.auto_gen_waveforms_cb = QCheckBox("Auto-generate waveform images")
        self.auto_gen_waveforms_cb.setChecked(current_settings.get('auto_gen_waveforms', False))
        options_row.addWidget(self.auto_gen_waveforms_cb)
        
        self.auto_gen_fingerprints_cb = QCheckBox("Auto-generate fingerprints")
        self.auto_gen_fingerprints_cb.setChecked(current_settings.get('auto_gen_fingerprints', False))
        options_row.addWidget(self.auto_gen_fingerprints_cb)
        settings_layout.addLayout(options_row)
        
        # Timing selection
        timing_row = QHBoxLayout()
        timing_row.addWidget(QLabel("Auto-generate:"))
        self.auto_gen_timing_combo = QComboBox()
        self.auto_gen_timing_combo.addItem("On application startup", "boot")
        self.auto_gen_timing_combo.addItem("When clicking into folder", "folder_selection")
        current_timing_idx = self.auto_gen_timing_combo.findData(current_settings.get('auto_gen_timing', 'folder_selection'))
        if current_timing_idx >= 0:
            self.auto_gen_timing_combo.setCurrentIndex(current_timing_idx)
        timing_row.addWidget(self.auto_gen_timing_combo)
        timing_row.addStretch(1)
        settings_layout.addLayout(timing_row)
        
        main_layout.addWidget(settings_group)
        main_layout.addStretch(1)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setDefault(True)
        button_layout.addWidget(ok_btn)
        
        main_layout.addLayout(button_layout)
    
    def accept(self):
        """Handle OK button click - save settings to result."""
        self.result_settings['auto_gen_waveforms'] = self.auto_gen_waveforms_cb.isChecked()
        self.result_settings['auto_gen_fingerprints'] = self.auto_gen_fingerprints_cb.isChecked()
        self.result_settings['auto_gen_timing'] = self.auto_gen_timing_combo.currentData()
        super().accept()
    
    def get_settings(self):
        """Return the configured settings."""
        return self.result_settings

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
            log_print("Issue#2: release-media error:", _e)
    
    # ---- Issue #3: default annotation-set name from current user ----
    def _resolve_user_display_name(self) -> str:
        try:
            # local imports to avoid new global includes
            import subprocess, os, getpass
            # Prefer Git global user.name
            try:
                # Prepare subprocess arguments to hide console windows
                subprocess_kwargs = {"stderr": subprocess.DEVNULL, "text": True}
                if sys.platform == "win32":
                    subprocess_kwargs["creationflags"] = CREATE_NO_WINDOW
                    
                name = subprocess.check_output(
                    ["git", "config", "--global", "user.name"],
                    **subprocess_kwargs
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
                # Update color to be consistent for this user
                annotation_set["color"] = self._get_color_for_set_name(user_name)
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

    def _user_colors_json_path(self) -> Path:
        """Return path to the user colors mapping file."""
        return self.root_path / USER_COLORS_JSON

    def _load_user_colors(self) -> Dict[str, str]:
        """Load the user-to-color mapping from disk."""
        return load_json(self._user_colors_json_path(), {}) or {}

    def _save_user_colors(self, user_colors: Dict[str, str]) -> None:
        """Save the user-to-color mapping to disk."""
        save_json(self._user_colors_json_path(), user_colors)

    def _get_default_colors(self) -> List[str]:
        """Return a list of default colors to assign to users."""
        return [
            "#00cc66",  # Green (original default)
            "#ff6b58",  # Red 
            "#58a6ff",  # Blue
            "#ffa500",  # Orange
            "#9966cc",  # Purple
            "#ff69b4",  # Hot Pink
            "#00ced1",  # Dark Turquoise
            "#ffd700",  # Gold
            "#32cd32",  # Lime Green
            "#ff4500",  # Orange Red
            "#4169e1",  # Royal Blue
            "#dc143c",  # Crimson
        ]

    def _assign_user_color(self, user_name: str) -> str:
        """Get or assign a consistent color for a user."""
        user_colors = self._load_user_colors()
        
        # If user already has a color, return it
        if user_name in user_colors:
            return user_colors[user_name]
        
        # Assign a new color for this user
        default_colors = self._get_default_colors()
        used_colors = set(user_colors.values())
        
        # Find the first available color from defaults
        for color in default_colors:
            if color not in used_colors:
                user_colors[user_name] = color
                self._save_user_colors(user_colors)
                return color
        
        # If all default colors are used, generate a new one based on user name hash
        import hashlib
        hash_obj = hashlib.sha256(user_name.encode())
        hash_hex = hash_obj.hexdigest()
        # Convert first 6 characters to a color
        color = f"#{hash_hex[:6]}"
        user_colors[user_name] = color
        self._save_user_colors(user_colors)
        return color

    def _get_color_for_set_name(self, set_name: str) -> str:
        """Get appropriate color for an annotation set name."""
        current_user = self._default_annotation_set_name()
        
        # If this is a user set (matches current user name or has [username] prefix)
        if set_name == current_user:
            return self._assign_user_color(current_user)
        elif set_name.startswith("[") and "]" in set_name:
            # Extract username from [username] prefix
            end_bracket = set_name.find("]")
            if end_bracket > 1:
                user_part = set_name[1:end_bracket]
                return self._assign_user_color(user_part)
        
        # For non-user sets, use default color (can be customized later)
        return "#00cc66"

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
                    sid = str(data.get("id") or ("ext_" + hashlib.sha256(str(jp).encode()).hexdigest()[:8]))
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
                        # Use consistent color for this user
                        color = self._get_color_for_set_name(name)
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
                        unique_sid = f"user_{hashlib.sha256(str(jp).encode()).hexdigest()[:8]}_{sid}"
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
        self.setWindowTitle(f"{APP_NAME} - {VERSION_STRING}"); self._apply_app_icon()

        self.settings = QSettings(APP_ORG, APP_NAME)
        self.root_path: Path = self._load_root_silently()
        self.current_practice_folder: Path = self.root_path  # Initially same as root
        self._needs_root_selection: bool = not self._has_stored_root()
        self.current_audio_file: Optional[Path] = None
        self.pending_note_start_ms: Optional[int] = None
        self.clip_sel_start_ms: Optional[int] = None
        self.clip_sel_end_ms: Optional[int] = None
        self._clip_play_end_ms: Optional[int] = None
        self._clip_play_start_ms: Optional[int] = None  # For looping clips
        self._clip_playing: bool = False
        # Sub-section playback state
        self._subsection_start_ms: Optional[int] = None
        self._subsection_end_ms: Optional[int] = None
        self._subsection_loops: bool = False
        self._subsection_playing: bool = False
        self.annotation_filter: str = 'all'
        self._programmatic_selection = False
        self._uid_counter: int = 1
        self._suspend_ann_change = False

        # Backup tracking - only create backup on first modification
        self._backup_created_this_session: bool = False
        self._initialization_complete: bool = False

        # Channel count cache for performance optimization
        self._channel_count_cache: Dict[Tuple[str, int, int], int] = {}

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
        
        # Listen for audio device changes
        self.media_instance = QMediaDevices()
        self.media_instance.audioOutputsChanged.connect(self._refresh_output_devices)

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
        self.file_partial_takes: Dict[str, bool] = {}  # Track partial takes per file in current set
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
        self.fingerprint_algorithm: str = self.settings.value(SETTINGS_KEY_FINGERPRINT_ALGORITHM, DEFAULT_ALGORITHM)
        # Validate the algorithm exists
        if self.fingerprint_algorithm not in FINGERPRINT_ALGORITHMS:
            self.fingerprint_algorithm = DEFAULT_ALGORITHM
        self.fingerprint_cache: Dict[str, Dict] = {}  # loaded per directory
        
        # Auto-labeling state management
        self.auto_label_in_progress: bool = False
        self.auto_label_backup_names: Dict[str, str] = {}

        # Auto-generation preferences
        self.auto_gen_waveforms: bool = bool(int(self.settings.value(SETTINGS_KEY_AUTO_GEN_WAVEFORMS, 0)))
        self.auto_gen_fingerprints: bool = bool(int(self.settings.value(SETTINGS_KEY_AUTO_GEN_FINGERPRINTS, 0)))
        self.auto_gen_timing: str = self.settings.value(SETTINGS_KEY_AUTO_GEN_TIMING, "folder_selection")
        
        # Print loaded settings for debugging
        log_print("Auto-generation settings loaded:")
        log_print(f"  Waveforms: {self.auto_gen_waveforms}")
        log_print(f"  Fingerprints: {self.auto_gen_fingerprints}") 
        log_print(f"  Timing: {self.auto_gen_timing}")

        # Auto-generation workers and progress tracking
        self._auto_gen_waveform_worker: Optional['AutoWaveformWorker'] = None
        self._auto_gen_waveform_thread: Optional[QThread] = None
        self._auto_gen_fingerprint_worker: Optional['AutoFingerprintWorker'] = None
        self._auto_gen_fingerprint_thread: Optional[QThread] = None
        self._auto_gen_in_progress: bool = False
        
        # Recursive auto-generation state
        self._directories_to_process: List[Path] = []
        self._current_directory_index: int = 0
        self._follow_with_fingerprints: bool = False

        # UI
        self._init_ui()

        # Load metadata
        self._load_names()
        self._load_notes()
        self._ensure_uids()

        # Populate UI
        self._refresh_set_combo()
        self._refresh_right_table()
        self._refresh_annotation_legend()
        self._load_annotations_for_current()
        
        # Refresh tree display to show any best take/partial take formatting
        self._refresh_tree_display()
        self._update_folder_notes_ui()
        self._refresh_important_table()
        self._update_fingerprint_ui()

        # Tree selection & timers
        self.tree.selectionModel().selectionChanged.connect(self._on_tree_selection_changed)
        self.slider_sync = QTimer(self); self.slider_sync.setInterval(200)
        self.slider_sync.timeout.connect(self._sync_slider)
        # Note: _sync_slider is only called by the timer (200ms interval), not on every position change
        # This prevents excessive UI updates during playback that can cause stuttering

        # Mark initialization as complete
        self._initialization_complete = True

        # Start auto-generation on boot if enabled
        if self.auto_gen_timing == "boot" and (self.auto_gen_waveforms or self.auto_gen_fingerprints):
            log_print(f"Boot auto-generation enabled - will start in 1 second")
            log_print(f"  Settings: timing=boot, waveforms={self.auto_gen_waveforms}, fingerprints={self.auto_gen_fingerprints}")
            log_print(f"  Target folder: {self.current_practice_folder}")
            self.statusBar().showMessage("Auto-generation will start shortly...", 4000)
            try:
                QTimer.singleShot(1000, lambda: self._start_auto_generation_for_folder(self.current_practice_folder))
                log_print("  Auto-generation timer scheduled successfully")
            except Exception as e:
                log_print(f"  ERROR: Failed to schedule auto-generation timer: {e}")
                self.statusBar().showMessage(f"Auto-generation failed to schedule: {str(e)}", 3000)
        else:
            # Show why boot auto-generation was not triggered
            if self.auto_gen_timing != "boot":
                log_print(f"Boot auto-generation not enabled (timing set to '{self.auto_gen_timing}')")
            elif not (self.auto_gen_waveforms or self.auto_gen_fingerprints):
                log_print("Boot auto-generation not enabled (both waveforms and fingerprints disabled)")
            else:
                log_print("Boot auto-generation not enabled (unknown reason)")
            
            if self.auto_gen_timing == "folder_selection" and (self.auto_gen_waveforms or self.auto_gen_fingerprints):
                log_print("Auto-generation will trigger when selecting folders")
            
            self.statusBar().showMessage("Auto-generation ready", 2000)

        # Waveform hooks
        self.waveform.markerMoved.connect(self._on_marker_moved_multi)
        self.waveform.markerReleased.connect(self._on_marker_released_multi)
        self.waveform.seekRequested.connect(self._on_waveform_seek_requested)
        self.waveform.annotationClicked.connect(self._on_waveform_annotation_clicked_multi)
        self.waveform.waveformReady.connect(self._update_stereo_button_state)
        self.waveform.waveformReady.connect(self._update_channel_muting_state)

        # Toggles
        self._restore_toggles()
        self._update_undo_actions_enabled()
        self._update_mono_button_state()  # Initialize mono button state
        self._update_channel_muting_state()  # Initialize channel muting state
        self._cleanup_temp_channel_files()  # Clean up old temporary files
        
        # Mark initialization as complete
        self._initialization_complete = True
        
        # Schedule root folder selection dialog if needed (after UI is shown)
        if self._needs_root_selection:
            QTimer.singleShot(100, self._show_root_selection_if_needed)

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

    # ----- Backup -----
    def _create_backup_if_needed(self):
        """
        Create backup of metadata files before first modification in this session.
        
        This method ensures that a backup is created only once per session, before
        the first time any metadata files are modified. It creates a timestamped 
        backup of existing metadata files in the current practice folder.
        
        Backup behavior:
        - Only creates backup if metadata files exist in the current folder
        - Only creates backup once per session (tracked via _backup_created_this_session)
        - Only creates backup after initialization is complete (not during app startup)
        - Creates .backup/YYYY-MM-DD-###/ folder in the current practice directory
        - Increments backup number for multiple backups on same day
        - Shows backup location in console if backup is created
        """
        # Don't create backup during initialization
        if not self._initialization_complete:
            return
            
        if self._backup_created_this_session:
            return  # Already created backup for this session
            
        try:
            backup_folder = create_metadata_backup_if_needed(self.current_practice_folder)
            if backup_folder:
                relative_backup = backup_folder.relative_to(self.current_practice_folder)
                log_print(f"Backup created before modification: {relative_backup}")
                # Could also show a brief status message in the UI if desired
                # self.statusBar().showMessage(f"Backup created: {relative_backup}", 3000)
            
            # Mark that we've attempted backup for this session (even if no files existed)
            self._backup_created_this_session = True
            
        except Exception as e:
            log_print(f"Warning: Failed to create backup: {e}")
            # Mark as attempted even if failed to avoid repeated attempts
            self._backup_created_this_session = True

    # ----- Settings & metadata -----
    def _has_stored_root(self) -> bool:
        """Check if a root directory is stored in settings and exists."""
        stored = self.settings.value(SETTINGS_KEY_ROOT, "", type=str)
        return bool(stored and Path(stored).exists())
    
    def _has_valid_root(self) -> bool:
        """Check if current root_path is valid and exists."""
        return self.root_path and self.root_path.exists()
    
    def _load_root_silently(self) -> Path:
        """Load root path from settings without showing any dialogs."""
        stored = self.settings.value(SETTINGS_KEY_ROOT, "", type=str)
        if stored and Path(stored).exists():
            return Path(stored)
        # Return home directory as fallback - don't show dialog yet
        return Path.home()
    
    def _show_root_selection_if_needed(self):
        """Show root selection dialog if no valid root is configured."""
        if not self._needs_root_selection:
            return
        
        dlg = QFileDialog(self, "Select your root band practice folder")
        dlg.setFileMode(QFileDialog.FileMode.Directory)
        dlg.setOption(QFileDialog.Option.ShowDirsOnly, True)
        if dlg.exec():
            p = Path(dlg.selectedFiles()[0])
            self.settings.setValue(SETTINGS_KEY_ROOT, str(p))
            self._save_root(p)  # This will update UI and reload data
            self._needs_root_selection = False  # Mark as resolved
        else:
            # User canceled - keep using home directory but mark as still needing selection
            home = Path.home()
            if self.root_path != home:
                self._save_root(home)
            # Don't set _needs_root_selection to False so dialog shows again if needed

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
            # Restore folder selection after changing root
            QTimer.singleShot(100, self._restore_folder_selection)
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
        self._refresh_annotation_legend()
        self._update_fingerprint_ui()
        self.waveform.clear()

    def _names_json_path(self) -> Path: 
        # Always use current_practice_folder for provided names to ensure consistency
        # whether a folder or audio file is selected
        return self.current_practice_folder / NAMES_JSON
    def _notes_json_path(self) -> Path: 
        # Always use current_practice_folder for annotations to ensure consistency
        # whether a folder or audio file is selected
        user_notes_filename = self._user_notes_filename()
        return self.current_practice_folder / user_notes_filename
    def _dur_json_path(self) -> Path: 
        # Always use current_practice_folder for duration cache to ensure consistency
        # whether a folder or audio file is selected
        return self.current_practice_folder / DURATIONS_JSON
    
    def _get_audio_file_dir(self) -> Path:
        """Return the current practice folder for consistency."""
        return self.current_practice_folder
    
    def _set_current_practice_folder(self, folder: Path):
        """Update the current practice folder (distinct from root band practice folder)."""
        if folder.exists() and folder.is_dir():
            # Reset backup flag when changing to a different folder
            if self.current_practice_folder != folder:
                self._backup_created_this_session = False
                # Clear channel count cache when changing directories to avoid stale entries
                self._channel_count_cache.clear()
            self.current_practice_folder = folder
            
            # Trigger auto-generation if enabled for folder selection and initialization is complete
            if (self._initialization_complete and 
                self.auto_gen_timing == "folder_selection" and 
                (self.auto_gen_waveforms or self.auto_gen_fingerprints)):
                # Use a timer to avoid blocking the UI thread
                try:
                    QTimer.singleShot(100, lambda: self._start_auto_generation_for_folder(folder))
                    log_print(f"Folder selection auto-generation scheduled for: {folder}")
                except Exception as e:
                    log_print(f"ERROR: Failed to schedule folder selection auto-generation: {e}")
    
    def _get_notes_json_path_for_audio_file(self) -> Path:
        """Return the notes JSON path for the current audio file's directory."""
        return self._get_audio_file_dir() / NOTES_JSON

    def _load_names(self):
        self.provided_names = load_json(self._names_json_path(), {}) or {}

    def _save_names(self):
        self._create_backup_if_needed()  # Create backup before first modification
        save_json(self._names_json_path(), self.provided_names)

    # ----- Annotation sets load/save -----
    def _create_default_set(self, carry_notes: Optional[Dict[str, List[Dict]]] = None, carry_general: Optional[Dict[str, str]] = None, carry_folder_notes: str = ""):
        sid = uuid.uuid4().hex[:8]
        set_name = self._default_annotation_set_name()
        color = self._get_color_for_set_name(set_name)
        aset = {"id": sid, "name": set_name, "color": color, "visible": True, "folder_notes": carry_folder_notes, "files": {}}
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
        self.notes_by_file = {}; self.file_general = {}; self.file_best_takes = {}; self.file_partial_takes = {}; self.folder_notes = ""

        
        # Check for migration from legacy file
        user_notes_path = self._notes_json_path()
        legacy_notes_path = (self.current_audio_file.parent if self.current_audio_file else self.current_practice_folder) / NOTES_JSON
        
        # If user-specific file doesn't exist but legacy file does, migrate it
        if not user_notes_path.exists() and legacy_notes_path.exists():
            try:
                legacy_data = load_json(legacy_notes_path, {})
                if legacy_data:  # Only migrate if there's actual data
                    save_json(user_notes_path, legacy_data)
                    log_print(f"Migrated annotations from {legacy_notes_path.name} to {user_notes_path.name}")
            except Exception as e:
                log_print(f"Warning: Could not migrate legacy annotations: {e}")
        
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
                            "partial_take": bool(meta.get("partial_take", False)),
                            "notes": [{
                                "uid": int(n.get("uid", 0) or 0),
                                "ms": int(n.get("ms", 0)),
                                "text": str(n.get("text", "")),
                                "important": bool(n.get("important", False)),
                                **({"end_ms": int(n["end_ms"])} if n.get("end_ms") is not None else {}),
                                **({"subsection": bool(n["subsection"])} if n.get("subsection") else {}),
                                **({"subsection_note": str(n["subsection_note"])} if n.get("subsection_note") else {})
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
        self._create_backup_if_needed()  # Create backup before first modification
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
        self.notes_by_file = {}; self.file_general = {}; self.file_best_takes = {}; self.file_partial_takes = {}
        if aset:
            for fname, meta in aset.get("files", {}).items():
                self.file_general[fname] = str(meta.get("general", "") or "")
                self.file_best_takes[fname] = bool(meta.get("best_take", False))
                self.file_partial_takes[fname] = bool(meta.get("partial_take", False))
                self.notes_by_file[fname] = [dict(n) for n in (meta.get("notes", []) or [])]
        else:
            self.notes_by_file = {}; self.file_general = {}; self.file_best_takes = {}; self.file_partial_takes = {}
        self._update_general_label()

    def _sync_fields_into_current_set(self):
        aset = self._get_current_set()
        if not aset: return
        files = {}
        all_files = set(self.notes_by_file.keys()) | set(self.file_general.keys()) | set(self.file_best_takes.keys()) | set(self.file_partial_takes.keys())
        for fname in all_files:
            files[fname] = {
                "general": self.file_general.get(fname, ""),
                "best_take": self.file_best_takes.get(fname, False),
                "partial_take": self.file_partial_takes.get(fname, False),
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
        self._create_backup_if_needed()  # Create backup before first modification
        save_json(self._dur_json_path(), self.played_durations)

    # ----- UI -----
    def _init_ui(self):
        self.resize(1360, 900); self.setStatusBar(QStatusBar(self))
        
        # Create menu bar
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        act_change_root = QAction("Change Band Practice &Folder…", self)
        act_change_root.triggered.connect(self._change_root_clicked)
        file_menu.addAction(act_change_root)
        
        file_menu.addSeparator()
        
        self.rename_action = QAction("&Batch Rename (##_ProvidedName)", self)
        self.rename_action.triggered.connect(self._batch_rename)
        file_menu.addAction(self.rename_action)
        
        self.export_action = QAction("&Export Annotations…", self)
        self.export_action.triggered.connect(self._export_annotations)
        file_menu.addAction(self.export_action)
        
        file_menu.addSeparator()
        
        self.convert_action = QAction("&Convert WAV→MP3 (delete WAVs)", self)
        self.convert_action.triggered.connect(self._convert_wav_to_mp3_threaded)
        file_menu.addAction(self.convert_action)
        
        self.mono_action = QAction("Convert to &Mono", self)
        self.mono_action.triggered.connect(self._convert_to_mono)
        file_menu.addAction(self.mono_action)
        
        file_menu.addSeparator()
        
        self.auto_gen_settings_action = QAction("Auto-Generation &Settings…", self)
        self.auto_gen_settings_action.triggered.connect(self._show_auto_generation_settings)
        file_menu.addAction(self.auto_gen_settings_action)
        
        self.restore_backup_action = QAction("&Restore from Backup…", self)
        self.restore_backup_action.triggered.connect(self._restore_from_backup)
        file_menu.addAction(self.restore_backup_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        help_about_action = QAction("&About", self)
        help_about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(help_about_action)
        
        help_changelog_action = QAction("&Changelog", self)
        help_changelog_action.triggered.connect(self._show_changelog_dialog)
        help_menu.addAction(help_changelog_action)
        
        # Simplified toolbar - Undo/Redo, Up navigation, Undo limit, and Auto-switch
        tb = QToolBar("Main"); self.addToolBar(tb)

        # Undo/Redo
        self.act_undo = QAction("Undo", self); self.act_undo.setShortcut(QKeySequence.StandardKey.Undo)
        self.act_redo = QAction("Redo", self); self.act_redo.setShortcut(QKeySequence.StandardKey.Redo)
        self.act_undo.triggered.connect(self._undo); self.act_redo.triggered.connect(self._redo)
        tb.addAction(self.act_undo); tb.addAction(self.act_redo)

        tb.addSeparator()
        
        # Up navigation button
        act_up = QAction("Up", self)
        act_up.setShortcut(QKeySequence("Alt+Up"))
        act_up.triggered.connect(self._go_up)
        tb.addAction(act_up)

        tb.addSeparator()
        tb.addWidget(QLabel("Undo limit:"))
        self.undo_spin = QSpinBox(); self.undo_spin.setRange(10, 1000); self.undo_spin.setValue(int(self.settings.value(SETTINGS_KEY_UNDO_CAP, 100)))
        self.undo_spin.valueChanged.connect(self._on_undo_capacity_changed)
        tb.addWidget(self.undo_spin)
        tb.addSeparator()

        self.auto_switch_cb = QCheckBox("Auto-switch to Annotations")
        wa = QWidgetAction(self); wa.setDefaultWidget(self.auto_switch_cb); tb.addAction(wa)

        # Create main widget to hold path label and splitter
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for cleaner look
        
        # Add path label at the top with consistent colors
        self.path_label = QLabel()
        colors = get_consistent_stylesheet_colors()
        self.path_label.setStyleSheet(f"QLabel {{ background-color: {colors['bg_medium']}; padding: 8px; border-bottom: 1px solid {colors['border']}; font-weight: bold; }}")
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

        self.file_proxy = FileInfoProxyModel(self.fs_model, self.played_durations, self, parent=None)

        self.tree = QTreeView()
        self.tree.setModel(self.file_proxy)
        self.tree.setRootIndex(self.file_proxy.mapFromSource(self.fs_model.index(str(self.root_path))))
        self.tree.setColumnHidden(1, True)  # hide Size/Time column
        self.tree.setColumnHidden(2, True)  # hide Type column  
        self.tree.setColumnHidden(3, True)  # hide Date Modified column
        self.tree.setColumnWidth(0, 360)
        self.tree.setAlternatingRowColors(True)
        # Enhanced selection styling with consistent colors for cross-machine compatibility
        colors = get_consistent_stylesheet_colors()
        self.tree.setStyleSheet(f"""
            QTreeView::item:selected {{
                background-color: {colors['selection_inactive']};
                color: white;
            }}
            QTreeView::item:selected:active {{
                background-color: {colors['selection_active']};
                color: white;
            }}
            QTreeView::item:selected:!active {{
                background-color: {colors['selection_primary']};
                color: white;
            }}
        """)
        self.tree.setSortingEnabled(True); self.tree.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.tree.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tree.doubleClicked.connect(self._on_tree_double_clicked)
        self.tree.activated.connect(self._on_tree_activated)
        # Add context menu for fingerprint exclusion
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._on_tree_context_menu)
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
        self.loop_cb = QCheckBox("Loop"); player_bar.addWidget(self.loop_cb)

        right_layout.addLayout(player_bar)

        # Initialize output devices
        self._refresh_output_devices()

        colors = get_consistent_stylesheet_colors()
        self.now_playing = QLabel("No selection"); self.now_playing.setStyleSheet(f"color: {colors['text_secondary']};")
        right_layout.addWidget(self.now_playing)

        # Tabs
        self.tabs = QTabWidget(); right_layout.addWidget(self.tabs, 1)
        self.tabs.setDocumentMode(True); self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabs.setMovable(True)
        self.tabs.tabBar().tabMoved.connect(self._on_tab_moved)
        self.tabs.currentChanged.connect(self._on_tab_changed)  # Handle tab changes for deferred loading

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
        colors = get_consistent_stylesheet_colors()
        fp_group.setStyleSheet(f"QWidget {{ background-color: {colors['bg_light']}; border: 1px solid {colors['border']}; border-radius: 5px; }}")
        
        fp_title = QLabel("Audio Fingerprinting")
        fp_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #333;")
        fp_layout.addWidget(fp_title)
        
        # Reference folder selection
        ref_row = QHBoxLayout()
        ref_folder_lbl = QLabel("Reference folder:")
        ref_folder_lbl.setStyleSheet("color: #333; font-weight: bold;")
        ref_row.addWidget(ref_folder_lbl)
        self.fingerprint_ref_label = QLabel("(None selected)")
        colors = get_consistent_stylesheet_colors()
        self.fingerprint_ref_label.setStyleSheet(f"color: {colors['text_muted']}; font-style: italic;")
        ref_row.addWidget(self.fingerprint_ref_label, 1)
        self.select_ref_btn = QPushButton("Choose...")
        self.select_ref_btn.setStyleSheet(f"QPushButton {{ background-color: {colors['bg_medium']}; border: 1px solid {colors['border']}; padding: 4px 12px; border-radius: 3px; }} QPushButton:hover {{ background-color: {colors['info']}; color: white; }}")
        self.select_ref_btn.clicked.connect(self._select_fingerprint_reference_folder)
        ref_row.addWidget(self.select_ref_btn)
        fp_layout.addLayout(ref_row)
        
        # Algorithm selection
        algorithm_row = QHBoxLayout()
        alg_lbl = QLabel("Fingerprint algorithm:")
        alg_lbl.setStyleSheet("color: #333; font-weight: bold;")
        algorithm_row.addWidget(alg_lbl)
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.setStyleSheet(f"QComboBox {{ background-color: white; border: 2px solid {colors['border']}; padding: 4px; border-radius: 3px; }} QComboBox:hover {{ border-color: {colors['info']}; }}")
        for alg_key, alg_info in FINGERPRINT_ALGORITHMS.items():
            self.algorithm_combo.addItem(alg_info["name"], alg_key)
        # Set current selection
        current_idx = self.algorithm_combo.findData(self.fingerprint_algorithm)
        if current_idx >= 0:
            self.algorithm_combo.setCurrentIndex(current_idx)
        self.algorithm_combo.currentTextChanged.connect(self._on_fingerprint_algorithm_changed)
        algorithm_row.addWidget(self.algorithm_combo)
        algorithm_row.addStretch(1)
        fp_layout.addLayout(algorithm_row)
        
        # Threshold and actions
        threshold_row = QHBoxLayout()
        threshold_lbl = QLabel("Match threshold:")
        threshold_lbl.setStyleSheet("color: #333; font-weight: bold;")
        threshold_row.addWidget(threshold_lbl)
        self.threshold_spin = QSpinBox()
        self.threshold_spin.setStyleSheet(f"QSpinBox {{ background-color: white; border: 2px solid {colors['border']}; padding: 4px; border-radius: 3px; }} QSpinBox:hover {{ border-color: {colors['info']}; }}")
        self.threshold_spin.setRange(50, 95)
        self.threshold_spin.setValue(int(self.fingerprint_threshold * 100))
        self.threshold_spin.setSuffix("%")
        self.threshold_spin.valueChanged.connect(self._on_fingerprint_threshold_changed)
        threshold_row.addWidget(self.threshold_spin)
        threshold_row.addStretch(1)
        
        self.generate_fingerprints_btn = QPushButton("Generate Fingerprints for Current Folder")
        self.generate_fingerprints_btn.setStyleSheet(f"QPushButton {{ background-color: {colors['info']}; color: white; border: 2px solid {colors['info']}; padding: 6px 12px; border-radius: 4px; font-weight: bold; }} QPushButton:hover {{ background-color: #1976D2; border-color: #1565C0; }}")
        self.generate_fingerprints_btn.clicked.connect(self._generate_fingerprints_for_folder)
        threshold_row.addWidget(self.generate_fingerprints_btn)
        
        self.auto_label_btn = QPushButton("Auto-Label Files")
        self.auto_label_btn.setStyleSheet(f"QPushButton {{ background-color: {colors['success']}; color: white; border: 2px solid {colors['success']}; padding: 6px 12px; border-radius: 4px; font-weight: bold; }} QPushButton:hover {{ background-color: #388E3C; border-color: #2E7D32; }} QPushButton:disabled {{ background-color: {colors['bg_medium']}; color: {colors['text_muted']}; border-color: {colors['border']}; }}")
        self.auto_label_btn.clicked.connect(self._auto_label_with_fingerprints)
        self.auto_label_btn.setEnabled(False)  # Enabled when reference folder is set
        threshold_row.addWidget(self.auto_label_btn)
        
        self.show_practice_folders_btn = QPushButton("Show Practice Folders")
        self.show_practice_folders_btn.setStyleSheet(f"QPushButton {{ background-color: {colors['bg_medium']}; color: #333; border: 2px solid {colors['border']}; padding: 6px 12px; border-radius: 4px; font-weight: bold; }} QPushButton:hover {{ background-color: {colors['warning']}; color: white; border-color: {colors['warning']}; }}")
        self.show_practice_folders_btn.clicked.connect(self._show_practice_folders_info)
        threshold_row.addWidget(self.show_practice_folders_btn)
        
        fp_layout.addLayout(threshold_row)
        
        # Clear names section
        clear_row = QHBoxLayout()
        clear_row.addStretch(1)  # Push button to the right
        self.clear_all_names_btn = QPushButton("Clear All Provided Names")
        self.clear_all_names_btn.clicked.connect(self._on_clear_all_provided_names)
        colors = get_consistent_stylesheet_colors()
        self.clear_all_names_btn.setStyleSheet(f"QPushButton {{ background-color: {colors['danger']}; color: white; font-weight: bold; }}")
        clear_row.addWidget(self.clear_all_names_btn)
        fp_layout.addLayout(clear_row)
        
        # Status label
        self.fingerprint_status = QLabel("")
        self.fingerprint_status.setStyleSheet(f"color: {colors['text_secondary']}; font-size: 11px;")
        fp_layout.addWidget(self.fingerprint_status)
        
        # Apply/Cancel buttons for auto-labeling (initially hidden)
        self.auto_label_buttons_row = QHBoxLayout()
        self.auto_label_buttons_row.addStretch(1)  # Push buttons to the right
        self.auto_label_apply_btn = QPushButton("Apply")
        self.auto_label_apply_btn.clicked.connect(self._on_auto_label_apply)
        colors = get_consistent_stylesheet_colors()
        self.auto_label_apply_btn.setStyleSheet(f"QPushButton {{ background-color: {colors['success']}; color: white; font-weight: bold; }}")
        self.auto_label_buttons_row.addWidget(self.auto_label_apply_btn)
        
        self.auto_label_cancel_btn = QPushButton("Cancel")
        self.auto_label_cancel_btn.clicked.connect(self._on_auto_label_cancel)
        self.auto_label_cancel_btn.setStyleSheet(f"QPushButton {{ background-color: {colors['danger']}; color: white; font-weight: bold; }}")
        self.auto_label_buttons_row.addWidget(self.auto_label_cancel_btn)
        
        self.auto_label_buttons_widget = QWidget()
        self.auto_label_buttons_widget.setLayout(self.auto_label_buttons_row)
        self.auto_label_buttons_widget.setVisible(False)  # Initially hidden
        fp_layout.addWidget(self.auto_label_buttons_widget)
        
        lib_layout.addWidget(fp_group)
        
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["File", "Best Take", "Partial Take", "Provided Name (editable)"])
        hh = self.table.horizontalHeader(); hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.SelectedClicked)
        self.table.itemChanged.connect(self._on_table_item_changed)
        lib_layout.addWidget(self.table, 1)
        self.table.itemSelectionChanged.connect(self._stop_if_no_file_selected)

        self.table.cellClicked.connect(self._on_library_cell_clicked)
        self.table.cellDoubleClicked.connect(self._on_library_cell_double_clicked)
        
        # Add legend for annotation set colors
        self.legend_widget = self._create_annotation_legend()
        lib_layout.addWidget(self.legend_widget)
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
        
        # Partial Take checkbox in annotation tab
        self.partial_take_cb = QCheckBox("Partial Take")
        self.partial_take_cb.setToolTip("Mark this song as a partial take")
        self.partial_take_cb.setEnabled(False)
        self.partial_take_cb.stateChanged.connect(self._on_partial_take_changed)
        pn_row.addWidget(self.partial_take_cb)
        
        ann_layout.addLayout(pn_row)

        # --- Waveform controls ---
        waveform_controls = QHBoxLayout()
        waveform_controls.addWidget(QLabel("Waveform:"))
        self.stereo_mono_toggle = QPushButton("Mono")
        self.stereo_mono_toggle.setCheckable(True)
        self.stereo_mono_toggle.setToolTip("Toggle between mono and stereo waveform view")
        self.stereo_mono_toggle.clicked.connect(self._on_stereo_toggle_clicked)
        self.stereo_mono_toggle.setMaximumWidth(80)
        waveform_controls.addWidget(self.stereo_mono_toggle)
        
        # --- Channel muting controls ---
        waveform_controls.addWidget(QLabel("Channels:"))
        self.left_channel_cb = QCheckBox("Left")
        self.left_channel_cb.setChecked(True)  # Default: both channels enabled
        self.left_channel_cb.setToolTip("Enable/disable left audio channel")
        self.left_channel_cb.stateChanged.connect(self._on_channel_muting_changed)
        waveform_controls.addWidget(self.left_channel_cb)
        
        self.right_channel_cb = QCheckBox("Right")
        self.right_channel_cb.setChecked(True)  # Default: both channels enabled
        self.right_channel_cb.setToolTip("Enable/disable right audio channel")
        self.right_channel_cb.stateChanged.connect(self._on_channel_muting_changed)
        waveform_controls.addWidget(self.right_channel_cb)
        
        waveform_controls.addStretch(1)  # Push to the left
        ann_layout.addLayout(waveform_controls)

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

        # --- Sub-section controls ---
        subsec_row = QHBoxLayout()
        subsec_row.addWidget(QLabel("Sub-section Name:"))
        self.subsec_name_edit = QLineEdit(); self.subsec_name_edit.setPlaceholderText("e.g. Chorus, Verse 1, Solo")
        self.subsec_name_edit.setMaximumWidth(150)
        subsec_row.addWidget(self.subsec_name_edit)
        subsec_row.addWidget(QLabel("Note:"))
        self.subsec_note_edit = QLineEdit(); self.subsec_note_edit.setPlaceholderText("Optional note for this subsection")
        self.subsec_note_edit.setMaximumWidth(200)
        subsec_row.addWidget(self.subsec_note_edit)
        self.subsec_label_btn = QPushButton("Label Subsection")
        self.subsec_clear_all_btn = QPushButton("Clear All")
        self.subsec_relabel_all_btn = QPushButton("Re-label All")
        subsec_row.addWidget(self.subsec_label_btn)
        subsec_row.addWidget(self.subsec_clear_all_btn)
        subsec_row.addWidget(self.subsec_relabel_all_btn)
        subsec_row.addStretch(1)
        ann_layout.addLayout(subsec_row)

        # Filter combo for annotations
        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Show:"))
        self.ann_filter_combo = QComboBox()
        self.ann_filter_combo.addItems(["All", "Points", "Clips", "Sub-sections"])
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
        # Sub-section connections
        self.subsec_label_btn.clicked.connect(self._on_subsection_label_clicked)
        self.subsec_clear_all_btn.clicked.connect(self._on_subsection_clear_all_clicked)
        self.subsec_relabel_all_btn.clicked.connect(self._on_subsection_relabel_all_clicked)
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

    def _create_annotation_legend(self) -> QWidget:
        """Create a legend widget showing annotation set colors and names."""
        legend_widget = QWidget()
        legend_layout = QHBoxLayout(legend_widget)
        legend_layout.setContentsMargins(5, 5, 5, 5)
        
        legend_label = QLabel("Best Take Legend:")
        legend_label.setStyleSheet("font-weight: bold;")
        legend_layout.addWidget(legend_label)
        
        # Create colored squares with labels for each visible annotation set
        for aset in self.annotation_sets:
            if not aset.get("visible", True):
                continue
                
            # Create a container for this legend item
            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(5)
            
            # Color square
            color_square = QLabel()
            color_square.setFixedSize(16, 16)
            color_square.setStyleSheet(f"background-color: {aset.get('color', '#00cc66')}; border: 1px solid black;")
            item_layout.addWidget(color_square)
            
            # Set name
            name_label = QLabel(aset.get("name", "Unknown"))
            name_label.setStyleSheet("font-size: 12px;")
            item_layout.addWidget(name_label)
            
            legend_layout.addWidget(item_widget)
        
        legend_layout.addStretch()  # Push everything to the left
        return legend_widget
    
    def _refresh_annotation_legend(self):
        """Refresh the annotation legend when sets change."""
        # Remove old legend and create new one
        lib_layout = self.lib_tab.layout()
        if hasattr(self, 'legend_widget') and self.legend_widget:
            lib_layout.removeWidget(self.legend_widget)
            self.legend_widget.deleteLater()
        
        self.legend_widget = self._create_annotation_legend()
        lib_layout.addWidget(self.legend_widget)

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
        self._refresh_right_table()  # Refresh table to show current set's best takes with border
        
        # Refresh tree display to show best take/partial take formatting for the new set
        self._refresh_tree_display()

    def _on_set_visible_toggled(self, _state):
        aset = self._get_current_set()
        if not aset: return
        aset["visible"] = bool(self.set_visible_cb.isChecked())
        self._save_notes()
        self._update_waveform_annotations()
        self._refresh_important_table()
        self._refresh_annotation_legend()
        self._refresh_right_table()
        self._load_annotations_for_current()
        
        # Refresh tree display when visibility is toggled
        self._refresh_tree_display()

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
        
        # Get consistent color for user sets, or allow custom color for non-user sets
        current_user = self._default_annotation_set_name()
        if name == current_user:
            # Use consistent user color
            color = self._get_color_for_set_name(name)
        else:
            # Allow custom color selection for non-user sets
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
        self._refresh_annotation_legend()
        self._refresh_right_table()

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
        self._refresh_annotation_legend()
        self._refresh_right_table()

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

    def _on_tab_changed(self, index: int):
        """Handle tab changes to trigger deferred loading when switching to Annotations tab."""
        if index >= 0 and self.tabs.tabText(index) == "Annotations" and self.current_audio_file:
            # Check if waveform is empty/not loaded yet (indicates deferred loading)
            if not hasattr(self.waveform, '_path') or self.waveform._path != self.current_audio_file:
                # Trigger immediate loading now that user is viewing Annotations tab
                self._deferred_annotation_load()

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
            # Always play on double-click for consistency with single-click behavior
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
            self._update_waveform_annotations(); self._load_annotations_for_current(); self._refresh_provided_name_field(); self._refresh_best_take_field(); self._refresh_partial_take_field()
            # Note: _refresh_right_table() removed - not needed for selection changes within same directory
            self._update_mono_button_state()
            return
        fi = self._fi(idx)
        if fi.isDir():
            # Update current practice folder when folder is selected
            folder_path = Path(fi.absoluteFilePath())
            self._set_current_practice_folder(folder_path)
            self._stop_playback(); self.now_playing.setText(f"Folder selected: {fi.fileName()}"); self.current_audio_file = None
            self._update_waveform_annotations(); self._load_annotations_for_current(); self._refresh_provided_name_field(); self._refresh_best_take_field(); self._refresh_partial_take_field(); self._refresh_right_table()
            # Note: Keep _refresh_right_table() here since folder selection means directory change
            self._update_mono_button_state()
            return
        if f".{fi.suffix().lower()}" in AUDIO_EXTS:
            path = Path(fi.absoluteFilePath())
            # Update current practice folder when audio file is selected (to its parent directory)
            self._set_current_practice_folder(path.parent)
            
            # Check if this is actually a different file before expensive operations
            is_different_file = self.current_audio_file != path
            
            if not self._programmatic_selection and self.auto_switch_cb.isChecked():
                self.tabs.setCurrentIndex(self._tab_index_by_name("Annotations"))
            # Always play the selected file, even if it's already the current file
            # This allows restarting the same song from the beginning when clicked
            self._play_file(path)
            
            # Only update UI states if the file actually changed (performance optimization)
            if is_different_file:
                self._update_mono_button_state()
                self._update_channel_muting_state()
        else:
            self._stop_playback(); self.now_playing.setText(fi.fileName()); self.current_audio_file = None
            self._update_waveform_annotations(); self._load_annotations_for_current(); self._refresh_provided_name_field(); self._refresh_best_take_field(); self._refresh_partial_take_field()
            # Note: _refresh_right_table() removed - not needed for selection changes within same directory
            self._update_mono_button_state()
            self._update_channel_muting_state()

    def _on_tree_context_menu(self, position: QPoint):
        """Handle right-click context menu on file tree."""
        idx = self.tree.indexAt(position)
        if not idx.isValid():
            return
            
        fi = self._fi(idx)
        # Only show context menu for audio files
        if not fi.isFile() or f".{fi.suffix().lower()}" not in AUDIO_EXTS:
            return
            
        file_path = Path(fi.absoluteFilePath())
        filename = file_path.name
        dirpath = file_path.parent
        
        # Check if file is currently excluded from fingerprinting
        is_excluded = self.file_proxy._is_file_excluded_cached(dirpath, filename)
        
        # Create context menu
        menu = QMenu(self)
        
        if is_excluded:
            action = menu.addAction("Include in fingerprinting")
            action.setToolTip("Include this file when matching fingerprints")
        else:
            action = menu.addAction("Exclude from fingerprinting")
            action.setToolTip("Exclude this file when matching fingerprints")
        
        # Show menu and handle selection
        result = menu.exec(self.tree.mapToGlobal(position))
        if result == action:
            # Toggle exclusion status
            new_status = toggle_file_fingerprint_exclusion(dirpath, filename)
            
            # Invalidate the cache for this directory to force reload
            self.file_proxy.invalidate_exclusion_cache(dirpath)
            
            # Update UI to reflect the change
            self._update_fingerprint_ui()
            self._refresh_tree_display()
            
            # Show confirmation message
            status_text = "excluded from" if new_status else "included in"
            QMessageBox.information(self, "Fingerprint Exclusion", 
                                  f"File '{filename}' is now {status_text} fingerprinting.")

    def _refresh_tree_display(self):
        """Force refresh of the tree display to update visual indicators."""
        # Invalidate the exclusion cache and emit dataChanged signals to refresh display
        self.file_proxy.invalidate_exclusion_cache()
        
        # Emit dataChanged signals for all visible items to refresh their display
        root_index = self.tree.rootIndex()
        if root_index.isValid():
            # Get the range of visible rows to minimize refresh overhead
            top_left = self.file_proxy.index(0, 0, root_index)
            row_count = self.file_proxy.rowCount(root_index)
            if row_count > 0:
                bottom_right = self.file_proxy.index(row_count - 1, 0, root_index)
                # Include FontRole and DisplayRole for best take and partial take indicators
                self.file_proxy.dataChanged.emit(top_left, bottom_right, [
                    Qt.ItemDataRole.ForegroundRole, 
                    Qt.ItemDataRole.ToolTipRole,
                    Qt.ItemDataRole.FontRole,
                    Qt.ItemDataRole.DisplayRole
                ])

    def _go_up(self):
        parent = self.root_path.parent
        if parent.exists() and parent != self.root_path: self._save_root(parent)

    def _change_root_clicked(self):
        d = QFileDialog.getExistingDirectory(self, "Choose Root Band Practice Folder", str(self.root_path))
        if d: self._save_root(Path(d))

    def _restore_from_backup(self):
        """Show backup selection dialog and restore selected backup."""
        try:
            # Discover available backups
            available_backups = discover_available_backups(self.root_path)
            
            if not available_backups:
                QMessageBox.information(
                    self, "No Backups Found", 
                    "No backup folders were found in the .backups directory.\n\n"
                    "Backups are automatically created when you make changes to metadata files."
                )
                return
            
            # Create backup selection dialog
            dialog = BackupSelectionDialog(available_backups, self.current_practice_folder, self.root_path, self)
            if dialog.exec():
                selected_backup, selected_folder = dialog.get_selection()
                if selected_backup and selected_folder:
                    # Confirm restoration
                    reply = QMessageBox.question(
                        self, "Confirm Restore",
                        f"Are you sure you want to restore metadata files from:\n\n"
                        f"Backup: {selected_backup.name}\n"
                        f"To folder: {selected_folder.relative_to(self.root_path) if selected_folder != self.root_path else selected_folder.name}\n\n"
                        f"This will overwrite existing metadata files!",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                    )
                    
                    if reply == QMessageBox.StandardButton.Yes:
                        # Perform restoration
                        restored_count = restore_metadata_from_backup(selected_backup, selected_folder, self.root_path)
                        
                        if restored_count > 0:
                            # Refresh UI to reflect restored data
                            self._load_annotations_for_current()
                            self._refresh_set_combo()
                            self._refresh_right_table()
                            self._update_folder_notes_ui()
                            self._refresh_important_table()
                            self._refresh_tree_display()
                            
                            QMessageBox.information(
                                self, "Restore Complete",
                                f"Successfully restored {restored_count} metadata file(s) from backup."
                            )
                        else:
                            QMessageBox.warning(
                                self, "No Files Restored",
                                "No compatible metadata files were found in the selected backup."
                            )
                    
        except Exception as e:
            QMessageBox.critical(
                self, "Restore Error",
                f"An error occurred while restoring from backup:\n\n{str(e)}"
            )

    # ----- Channel-specific audio processing -----
    def _get_cached_channel_count(self, path: Path) -> int:
        """
        Get the channel count for an audio file using a cache for performance.
        
        Args:
            path: Path to the audio file
            
        Returns:
            Number of channels (1 for mono, 2+ for stereo/multichannel)
        """
        try:
            # Create cache key using path, size, and modification time
            stat_info = path.stat()
            cache_key = (str(path), int(stat_info.st_size), int(stat_info.st_mtime))
            
            # Check cache first
            if cache_key in self._channel_count_cache:
                return self._channel_count_cache[cache_key]
            
            # Not in cache, detect channel count
            channel_count = get_audio_channel_count(path)
            
            # Cache the result (limit cache size to avoid memory issues)
            if len(self._channel_count_cache) > 1000:
                # Clear oldest entries when cache gets too large
                keys_to_remove = list(self._channel_count_cache.keys())[:500]
                for key in keys_to_remove:
                    del self._channel_count_cache[key]
            
            self._channel_count_cache[cache_key] = channel_count
            return channel_count
            
        except Exception:
            # Fallback to direct detection on error
            return get_audio_channel_count(path)

    def _get_channel_muted_file(self, path: Path, left_enabled: bool, right_enabled: bool) -> Path:
        """
        Get a path to an audio file with the specified channel muting configuration.
        
        Args:
            path: Original audio file path
            left_enabled: Whether left channel should be audible
            right_enabled: Whether right channel should be audible
            
        Returns:
            Path to the audio file to play (original or temporary channel-muted file)
        """
        if left_enabled and right_enabled:  # Both channels enabled
            return path
            
        if not HAVE_PYDUB:
            # Fall back to original file if pydub is not available
            return path
            
        # Check if file is actually stereo using cached channel count
        channel_count = self._get_cached_channel_count(path)
        if channel_count < 2:
            return path  # File is not stereo, return original
            
        # Create temporary directory for channel-muted files
        temp_dir = Path.home() / ".audiobrowser_temp"
        temp_dir.mkdir(exist_ok=True)
        
        # Generate filename for channel-muted version
        if not left_enabled and right_enabled:
            suffix = "_left_muted"
        elif left_enabled and not right_enabled:
            suffix = "_right_muted"
        elif not left_enabled and not right_enabled:
            suffix = "_both_muted"
        else:
            suffix = ""
            
        temp_filename = f"{path.stem}{suffix}{path.suffix}"
        temp_path = temp_dir / temp_filename
        
        # Check if temporary file already exists and is newer than original
        if temp_path.exists():
            try:
                original_mtime = path.stat().st_mtime
                temp_mtime = temp_path.stat().st_mtime
                if temp_mtime >= original_mtime:
                    return temp_path  # Use existing temp file
            except Exception:
                pass
        
        try:
            # Create channel-muted audio file
            audio = AudioSegment.from_file(str(path))
            
            if audio.channels >= 2:
                # Split into individual channels
                channels = audio.split_to_mono()
                left_channel = channels[0] if left_enabled else AudioSegment.silent(duration=len(channels[0]))
                right_channel = channels[1] if right_enabled and len(channels) > 1 else AudioSegment.silent(duration=len(channels[0]))
                
                # Create stereo audio with muted channels
                muted_audio = AudioSegment.from_mono_audiosegments(left_channel, right_channel)
            else:
                # For mono files, just return original or silence
                muted_audio = audio if (left_enabled or right_enabled) else AudioSegment.silent(duration=len(audio))
                
            # Export temporary file
            muted_audio.export(str(temp_path), format=path.suffix[1:].lower())
            return temp_path
            
        except Exception as e:
            log_print(f"Error creating channel-muted file: {e}")
            return path  # Fall back to original file
    
    def _cleanup_temp_channel_files(self):
        """Clean up temporary channel-muted audio files."""
        try:
            temp_dir = Path.home() / ".audiobrowser_temp"
            if temp_dir.exists():
                # Remove old temp files (older than 1 hour)
                import time
                current_time = time.time()
                for temp_file in temp_dir.glob("*"):
                    try:
                        if temp_file.is_file() and (current_time - temp_file.stat().st_mtime) > 3600:
                            temp_file.unlink()
                    except Exception:
                        pass
        except Exception:
            pass  # Don't let cleanup errors affect the application

    # ----- Playback -----
    def _play_file(self, path: Path, seek_to_ms: Optional[int] = None):
        # Always play the file, even if it's the same as current - this allows restarting
        # Check if we need to reload annotations from a different directory
        prev_audio_dir = self.current_audio_file.parent if self.current_audio_file else None
        new_audio_dir = path.parent
        need_reload_annotations = (prev_audio_dir != new_audio_dir)
        
        # Performance optimization: check channel muting state efficiently
        # Skip all channel processing overhead when both channels enabled (common case)
        try:
            left_enabled = self.left_channel_cb.isChecked()
            right_enabled = self.right_channel_cb.isChecked()
            both_channels_enabled = left_enabled and right_enabled
        except AttributeError:
            # Fallback during initialization - assume both channels enabled
            both_channels_enabled = True
        
        if both_channels_enabled:
            playback_file = path
        else:
            playback_file = self._get_channel_muted_file(path, left_enabled, right_enabled)
        
        # Optimize media player state changes for faster song switching
        self.player.stop()
        self.player.setSource(QUrl.fromLocalFile(str(playback_file)))
        self.player.play()
        
        # Handle seeking if requested (this may add delay but only when seeking)
        if seek_to_ms is not None:
            # Use a small delay to ensure media is loaded before seeking
            QTimer.singleShot(100, lambda: self.player.setPosition(seek_to_ms))
        
        self.play_pause_btn.setEnabled(True)
        self.position_slider.setEnabled(True)
        self.slider_sync.start()
        
        # Update UI text to show channel muting info (fast operation)
        channel_info = ""
        if both_channels_enabled:
            channel_info = ""
        elif not left_enabled and not right_enabled:
            channel_info = " (Both Muted)"
        elif not left_enabled:
            channel_info = " (Left Muted)"
        elif not right_enabled:
            channel_info = " (Right Muted)"
        
        self.now_playing.setText(f"Playing: {path.name}{channel_info}")
        
        self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        self.current_audio_file = path
        self.pending_note_start_ms = None  # Store original path, not temp file
        self._update_captured_time_label()
        
        # Defer expensive operations to not block audio playback startup
        # Use a short timer to let audio start playing before doing heavy UI work
        QTimer.singleShot(10, lambda: self._finish_song_loading(path, need_reload_annotations))
    
    def _finish_song_loading(self, path: Path, need_reload_annotations: bool):
        """Complete the song loading process with expensive UI operations deferred to not block audio playback."""
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
            self._refresh_annotation_legend()
        
        # Check if we should defer expensive annotation operations until the Annotations tab is viewed
        annotations_tab_active = self.tabs.currentIndex() == self._tab_index_by_name("Annotations")
        will_auto_switch = not self._programmatic_selection and self.auto_switch_cb.isChecked()
        
        if annotations_tab_active or will_auto_switch:
            # Load annotations immediately if we're on the annotations tab or will switch to it
            self._load_annotations_for_current()
            self._refresh_provided_name_field()
            self._refresh_best_take_field()
            self._refresh_partial_take_field()
            try: 
                self.waveform.set_audio_file(path)
                self._update_stereo_button_state()  # Update stereo button after waveform is loaded
                self._update_channel_muting_state()  # Update channel muting state
            except Exception: 
                self.waveform.clear()
                self._update_stereo_button_state()  # Update button state even on error
                self._update_channel_muting_state()  # Update channel muting state even on error
            self._update_waveform_annotations()
        else:
            # Defer expensive operations when not on annotations tab and not auto-switching
            # Use QTimer.singleShot to defer waveform and annotation loading
            QTimer.singleShot(0, self._deferred_annotation_load)
        
        # Ensure the file is highlighted in the tree view (important for auto-progression)
        self._highlight_file_in_tree(path)
    
    def _deferred_annotation_load(self):
        """Load annotations and waveform data after a brief delay to improve perceived responsiveness."""
        if self.current_audio_file:  # Make sure file is still current
            self._load_annotations_for_current()
            self._refresh_provided_name_field()
            self._refresh_best_take_field()
            self._refresh_partial_take_field()
            try: 
                self.waveform.set_audio_file(self.current_audio_file)
                self._update_stereo_button_state()  # Update stereo button after waveform is loaded
                self._update_channel_muting_state()  # Update channel muting state
            except Exception: 
                self.waveform.clear()
                self._update_stereo_button_state()  # Update button state even on error
                self._update_channel_muting_state()  # Update channel muting state even on error
            self._update_waveform_annotations()

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
                log_print(f"Warning: Could not find {path} in filesystem model")
                return
                
            # Map from source model to proxy model
            proxy_idx = self.file_proxy.mapFromSource(src_idx)
            if not proxy_idx.isValid():
                log_print(f"Warning: Could not map {path} to proxy model")
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
            log_print(f"Warning: Failed to highlight {path} in tree view: {e}")

    def _restore_folder_selection(self):
        """Restore the folder selection in the tree view to match current_practice_folder.
        
        This is called after tree refresh operations to maintain visual consistency
        when the user has selected a folder but the tree model has been reset.
        """
        try:
            if not hasattr(self, 'current_practice_folder') or self.current_practice_folder == self.root_path:
                return
            
            # Get the source index for the folder from the filesystem model
            src_idx = self.fs_model.index(str(self.current_practice_folder))
            if not src_idx.isValid():
                return
                
            # Map from source model to proxy model
            proxy_idx = self.file_proxy.mapFromSource(src_idx)
            if not proxy_idx.isValid():
                return
            
            # Set the programmatic selection flag to prevent triggering selection change events
            self._programmatic_selection = True
            
            try:
                # Select and highlight the folder in the tree view
                self.tree.setCurrentIndex(proxy_idx)
                
                # Ensure the selected item is visible (scroll to it if necessary)
                self.tree.scrollTo(proxy_idx, QAbstractItemView.ScrollHint.EnsureVisible)
                
            finally:
                # Reset the programmatic selection flag after a short delay
                QTimer.singleShot(0, lambda: setattr(self, "_programmatic_selection", False))
                
        except Exception as e:
            # Log the error but don't crash - folder selection restoration is not critical
            log_print(f"Warning: Failed to restore folder selection for {self.current_practice_folder}: {e}")

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
        self._refresh_partial_take_field()

    def _update_mono_button_state(self):
        """Update the mono conversion button enabled/disabled state based on current selection."""
        if not hasattr(self, 'mono_action'):
            return  # Button not created yet
            
        # Disable if no file is selected
        if not self.current_audio_file or not self.current_audio_file.exists():
            self.mono_action.setEnabled(False)
            self.mono_action.setText("Convert to Mono")
            return
        
        # Check if pydub is available
        if not HAVE_PYDUB:
            self.mono_action.setEnabled(False)
            self.mono_action.setText("Convert to Mono (pydub required)")
            return
        
        # Check channel count
        try:
            channels = self._get_cached_channel_count(self.current_audio_file)
            if channels == 1:
                self.mono_action.setEnabled(False)
                self.mono_action.setText("Convert to Mono (already mono)")
            else:
                self.mono_action.setEnabled(True)
                self.mono_action.setText("Convert to Mono")
        except Exception:
            # If we can't determine channel count, disable the button
            self.mono_action.setEnabled(False)
            self.mono_action.setText("Convert to Mono (unable to read file)")

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
                        log_print(f"Auto-progressing from '{cur.name}' to '{next_file.name}'")
                        self._play_file(next_file)
                    else:
                        log_print(f"Auto-progression: reached end of playlist (last file: '{cur.name}')")
                    break
        except Exception as e:
            log_print(f"Error during auto-progression: {e}")
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

    def _on_stereo_toggle_clicked(self, checked: bool):
        """Handle stereo/mono toggle button click."""
        # Update the waveform mode
        self.waveform.set_stereo_mode(checked)
        
        # Update button text and tooltip
        if checked:
            self.stereo_mono_toggle.setText("Stereo")
            self.stereo_mono_toggle.setToolTip("Currently showing stereo view. Click for mono view.")
        else:
            self.stereo_mono_toggle.setText("Mono")
            self.stereo_mono_toggle.setToolTip("Currently showing mono view. Click for stereo view.")
        
        # Enable/disable button based on whether current file has stereo data
        if self.current_audio_file:
            self.stereo_mono_toggle.setEnabled(self.waveform.has_stereo_data())

    def _update_stereo_button_state(self):
        """Update stereo button state based on current file."""
        if not self.current_audio_file:
            self.stereo_mono_toggle.setEnabled(False)
            return
            
        has_stereo = self.waveform.has_stereo_data()
        self.stereo_mono_toggle.setEnabled(has_stereo)
        
        if not has_stereo and self.waveform.get_stereo_mode():
            # File doesn't have stereo data but we're in stereo mode, switch to mono
            self.stereo_mono_toggle.setChecked(False)
            self._on_stereo_toggle_clicked(False)

    def _on_channel_muting_changed(self, _state):
        """Handle channel muting checkbox changes."""
        if not self.current_audio_file:
            return
            
        # Update channel checkbox state based on file
        self._update_channel_muting_state()
        
        # If we're currently playing, restart playback with new channel settings
        was_playing = self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState
        current_position = self.player.position() if was_playing else 0
        
        # Reload the current file with new channel settings
        if self.current_audio_file:
            self._play_file(self.current_audio_file, seek_to_ms=current_position if was_playing else None)
            if was_playing:
                self.player.play()

    def _update_channel_muting_state(self):
        """Update channel muting checkbox state based on current file."""
        if not self.current_audio_file:
            self.left_channel_cb.setEnabled(False)
            self.right_channel_cb.setEnabled(False)
            return
            
        # Enable channel controls only for stereo files
        channel_count = self._get_cached_channel_count(self.current_audio_file) if self.current_audio_file else 1
        
        # Enable only if file has more than 1 channel
        is_stereo = channel_count > 1
        self.left_channel_cb.setEnabled(is_stereo)
        self.right_channel_cb.setEnabled(is_stereo)
        
        # If file is mono, ensure both checkboxes are checked
        if not is_stereo:
            self.left_channel_cb.setChecked(True)
            self.right_channel_cb.setChecked(True)

    # ----- Library table helpers -----
    def _list_audio_in_root(self) -> List[Path]:
        if not self.root_path.exists(): return []
        return [p for p in sorted(self.root_path.iterdir()) if p.is_file() and p.suffix.lower() in AUDIO_EXTS]

    def _list_wav_in_root(self) -> List[Path]:
        if not self.root_path.exists(): return []
        return [p for p in sorted(self.root_path.iterdir()) if p.is_file() and p.suffix.lower() in {".wav",".wave"}]

    def _list_audio_in_current_dir(self) -> List[Path]:
        """List audio files in the directory containing the currently selected song, or current practice folder if no song selected."""
        target_dir = self.current_practice_folder
        if not target_dir.exists(): return []
        return [p for p in sorted(target_dir.iterdir()) if p.is_file() and p.suffix.lower() in AUDIO_EXTS]

    def _get_all_best_takes_for_file(self, filename: str) -> List[Dict[str, Any]]:
        """Get all annotation sets that have marked this file as a best take, along with their colors."""
        best_take_sets = []
        for aset in self.annotation_sets:
            if not aset.get("visible", True):
                continue  # Skip invisible sets
            file_meta = aset.get("files", {}).get(filename, {})
            if file_meta.get("best_take", False):
                best_take_sets.append({
                    "id": aset.get("id"),
                    "name": aset.get("name", "Unknown"),
                    "color": aset.get("color", "#00cc66")
                })
        return best_take_sets

    def _get_all_partial_takes_for_file(self, filename: str) -> List[Dict[str, Any]]:
        """Get all annotation sets that have marked this file as a partial take, along with their colors."""
        partial_take_sets = []
        for aset in self.annotation_sets:
            if not aset.get("visible", True):
                continue  # Skip invisible sets
            file_meta = aset.get("files", {}).get(filename, {})
            if file_meta.get("partial_take", False):
                partial_take_sets.append({
                    "id": aset.get("id"),
                    "name": aset.get("name", "Unknown"),
                    "color": aset.get("color", "#00cc66")
                })
        return partial_take_sets

    def _refresh_right_table(self):
        files = self._list_audio_in_current_dir()
        self.table.blockSignals(True); self.table.setRowCount(len(files))
        for row, p in enumerate(files):
            item_file = QTableWidgetItem(p.name); item_file.setFlags(item_file.flags() ^ Qt.ItemFlag.ItemIsEditable)
            
            # Get all best takes for this file from all visible annotation sets
            best_take_sets = self._get_all_best_takes_for_file(p.name)
            
            # Get all partial takes for this file from all visible annotation sets
            partial_take_sets = self._get_all_partial_takes_for_file(p.name)
            
            # Create best take indicator widget
            best_take_widget = BestTakeIndicatorWidget(best_take_sets, self.current_set_id, self.table)
            best_take_widget.on_best_take_clicked = lambda row=row: self._on_best_take_widget_clicked(row)
            
            # Create partial take indicator widget
            partial_take_widget = PartialTakeIndicatorWidget(partial_take_sets, self.current_set_id, self.table)
            partial_take_widget.on_partial_take_clicked = lambda row=row: self._on_partial_take_widget_clicked(row)
            
            item_name = QTableWidgetItem(self.provided_names.get(p.name, "")); item_name.setToolTip("Double-click to edit your Provided Name")
            
            # Set light background for files with any best takes or partial takes
            if best_take_sets or partial_take_sets:
                if best_take_sets:
                    light_color = QColor(245, 255, 245)  # Very light green for best takes
                else:
                    light_color = QColor(255, 248, 220)  # Very light yellow for partial takes
                item_file.setBackground(light_color)
                item_name.setBackground(light_color)
            
            self.table.setItem(row, 0, item_file)
            self.table.setCellWidget(row, 1, best_take_widget)  # Use setCellWidget for custom widget
            self.table.setCellWidget(row, 2, partial_take_widget)  # Use setCellWidget for custom widget  
            self.table.setItem(row, 3, item_name)
        self.table.blockSignals(False)

    def _on_best_take_widget_clicked(self, row: int):
        """Handle clicks on the best take indicator widget to toggle best take for current set."""
        file_item = self.table.item(row, 0)
        if not file_item:
            return
        filename = file_item.text()
        
        # Toggle best take for current set
        is_currently_best = self.file_best_takes.get(filename, False)
        self.file_best_takes[filename] = not is_currently_best
        self._save_notes()
        
        # Refresh the entire table to update the display
        self._refresh_right_table()
        
        # Refresh the tree display to show best take formatting
        self._refresh_tree_display()

    def _on_partial_take_widget_clicked(self, row: int):
        """Handle clicks on the partial take indicator widget to toggle partial take for current set."""
        file_item = self.table.item(row, 0)
        if not file_item:
            return
        filename = file_item.text()
        
        # Toggle partial take for current set
        is_currently_partial = self.file_partial_takes.get(filename, False)
        self.file_partial_takes[filename] = not is_currently_partial
        self._save_notes()
        
        # Refresh the entire table to update the display
        self._refresh_right_table()
        
        # Refresh the tree display to show partial take formatting
        self._refresh_tree_display()

    def _on_table_item_changed(self, item: QTableWidgetItem):
        row = item.row(); file_item = self.table.item(row, 0)
        if not file_item: return
        filename = file_item.text()
        
        if item.column() == 3:  # Provided Name (editable) - now column 3
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
            log_print("Issue#1 handler error:", _e)

    def _on_library_cell_double_clicked(self, row: int, column: int):
        """Handle double-clicks on the library table cells."""
        # Handle double-clicks on the Best Take column (column 1) or Partial Take column (column 2)
        if column not in [1, 2]:
            return
            
        # Toggle best take or partial take for the current user/set on the clicked file
        file_item = self.table.item(row, 0)
        if not file_item:
            return
            
        filename = file_item.text().strip()
        if not filename:
            return
            
        if column == 1:  # Best Take column
            # Toggle best take for current set (same logic as _on_best_take_widget_clicked)
            is_currently_best = self.file_best_takes.get(filename, False)
            self.file_best_takes[filename] = not is_currently_best
        elif column == 2:  # Partial Take column
            # Toggle partial take for current set (same logic as _on_partial_take_widget_clicked)
            is_currently_partial = self.file_partial_takes.get(filename, False)
            self.file_partial_takes[filename] = not is_currently_partial
            
        self._save_notes()
        
        # Refresh the entire table to update the display
        self._refresh_right_table()
        
        # Refresh the tree display to show best/partial take formatting
        self._refresh_tree_display()

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
            if self.annotation_filter == 'sub-sections' and not entry.get('subsection'): continue
            self._append_annotation_row(entry, set_id=set_id, set_name=set_name, editable=editable)

        self.annotation_table.blockSignals(False); self.general_edit.blockSignals(False)
        self._refresh_important_table()
        self._update_waveform_annotations()
        self._refresh_provided_name_field()
        self._refresh_best_take_field()
        self._refresh_partial_take_field()

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
        # Also handle sub-sections with special formatting
        try:
            end_ms = entry.get("end_ms")
            is_subsection = entry.get("subsection", False)
            if end_ms is not None:
                # time item is at self._c_time
                titem = self.annotation_table.item(r, self._c_time)
                if titem:
                    time_text = f"{human_time_ms(int(ms))} - {human_time_ms(int(end_ms))}"
                    if is_subsection:
                        time_text += " [SUB]"
                    titem.setText(time_text)
                    titem.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                    
                # Also update note text for sub-sections to show it's a sub-section
                if is_subsection:
                    note_item = self.annotation_table.item(r, self._c_note)
                    if note_item:
                        original_text = note_item.text()
                        subsection_note = entry.get("subsection_note", "")
                        if subsection_note:
                            note_item.setText(f"[SUBSECTION] {original_text} | {subsection_note}")
                        else:
                            note_item.setText(f"[SUBSECTION] {original_text}")
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
                    
        # Find the annotation entry to check if it's a sub-section
        entry = self._find_annotation_entry(set_id, uid)
        if entry and entry.get("subsection") and entry.get("end_ms"):
            # Handle sub-section playback
            self._play_subsection(entry)
        else:
            # Regular annotation playback
            self.player.setPosition(int(ms))
            self.waveform.set_selected_uid(set_id, uid)
            self.player.play()
            self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))

    def _find_annotation_entry(self, set_id: str, uid: int) -> Optional[Dict]:
        """Find an annotation entry by set_id and uid."""
        if not self.current_audio_file:
            return None
            
        fname = self.current_audio_file.name
        
        # Find the annotation set
        annotation_set = None
        for s in self.annotation_sets:
            if s.get("id") == set_id:
                annotation_set = s
                break
                
        if not annotation_set:
            return None
            
        # Find the entry
        files = annotation_set.get("files", {})
        file_data = files.get(fname, {})
        notes = file_data.get("notes", [])
        
        for entry in notes:
            if entry.get("uid") == uid:
                return entry
                
        return None

    def _play_subsection(self, entry: Dict):
        """Play a sub-section with optional looping."""
        start_ms = int(entry.get("ms", 0))
        end_ms = int(entry.get("end_ms", 0))
        
        if end_ms <= start_ms:
            return
            
        # Set up sub-section playback
        self._subsection_start_ms = start_ms
        self._subsection_end_ms = end_ms
        self._subsection_loops = self.loop_cb.isChecked()  # Use global loop state
        self._subsection_playing = True
        
        # Start playback
        self.player.setPosition(start_ms)
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
        
        # Refresh the tree display to show best take formatting
        self._refresh_tree_display()

    # Partial take checkbox on Annotations tab
    def _on_partial_take_changed(self, state):
        if not self.current_audio_file:
            return
        fname = self.current_audio_file.name
        is_checked = state == Qt.CheckState.Checked.value
        self.file_partial_takes[fname] = is_checked
        self._save_notes()  # Save the annotation data including partial_take
        self._refresh_right_table()  # Update the library table to show the highlighting
        
        # Refresh the tree display to show partial take formatting
        self._refresh_tree_display()

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

    def _refresh_partial_take_field(self):
        if not self.current_audio_file:
            self.partial_take_cb.setChecked(False)
            self.partial_take_cb.setEnabled(False)
            return
        fname = self.current_audio_file.name
        self.partial_take_cb.setEnabled(True)
        self.partial_take_cb.blockSignals(True)  # Prevent triggering the change handler
        self.partial_take_cb.setChecked(self.file_partial_takes.get(fname, False))
        self.partial_take_cb.blockSignals(False)

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
            colors = get_consistent_stylesheet_colors()
            self.folder_notes_edit.setStyleSheet(f"QPlainTextEdit {{ background-color: {colors['bg_light']}; }}")
            
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
        # Store clip start for looping
        self._clip_play_start_ms = int(self.clip_sel_start_ms)
        self.player.setPosition(int(self.clip_sel_start_ms)); self.player.play()
        self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))

    def _on_player_pos_for_clip(self, pos_ms: int):
        # Handle clip playback ending
        if self._clip_playing and self._clip_play_end_ms is not None:
            if int(pos_ms) >= int(self._clip_play_end_ms):
                if self.loop_cb.isChecked() and self._clip_play_start_ms is not None:
                    # Loop back to clip start
                    self.player.setPosition(int(self._clip_play_start_ms))
                else:
                    # Stop playing
                    self.player.pause()
                    self._clip_playing = False
                    self._clip_play_end_ms = None
                    self._clip_play_start_ms = None
                    self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
                
        # Handle sub-section playback and looping
        if self._subsection_playing and self._subsection_end_ms is not None:
            if int(pos_ms) >= int(self._subsection_end_ms):
                if self.loop_cb.isChecked() and self._subsection_start_ms is not None:
                    # Loop back to start
                    self.player.setPosition(int(self._subsection_start_ms))
                else:
                    # Stop playing
                    self.player.pause()
                    self._subsection_playing = False
                    self._subsection_start_ms = None
                    self._subsection_end_ms = None
                    self._subsection_loops = False
                    self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

    def _on_clip_cancel_clicked(self):
        self.clip_sel_start_ms = None; self.clip_sel_end_ms = None
        self._clip_play_end_ms = None; self._clip_play_start_ms = None; self._clip_playing = False
        # Also reset sub-section playback
        self._subsection_playing = False
        self._subsection_start_ms = None
        self._subsection_end_ms = None
        self._subsection_loops = False
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
        elif "sub-section" in txt: self.annotation_filter = "sub-sections"
        else: self.annotation_filter = "all"
        self._load_annotations_for_current()

    def _on_subsection_label_clicked(self):
        """Label a sub-section using clip start/end and name."""
        if not self.current_audio_file: return
        if self.clip_sel_start_ms is None or self.clip_sel_end_ms is None: 
            QMessageBox.information(self, "Select Range", "Please select a clip start and end time first.")
            return
        if int(self.clip_sel_start_ms) >= int(self.clip_sel_end_ms): return
        
        name = self.subsec_name_edit.text().strip()
        if not name:
            QMessageBox.information(self, "Add Name", "Please enter a sub-section name (e.g., 'Chorus', 'Verse 1').")
            return
            
        note = self.subsec_note_edit.text().strip()  # Get the note text
        fname = self.current_audio_file.name
        uid = self._uid_counter; self._uid_counter += 1
        
        entry = {
            "uid": int(uid), 
            "ms": int(self.clip_sel_start_ms), 
            "end_ms": int(self.clip_sel_end_ms), 
            "text": name, 
            "important": False,
            "subsection": True
        }
        
        # Add the note field if a note was provided
        if note:
            entry["subsection_note"] = note
        
        self.notes_by_file.setdefault(fname, []).append(entry)
        self._push_undo({"type":"add","set":self.current_set_id,"file":fname,"entry":entry})
        self._resort_and_rebuild_table_preserving_selection(keep_pair=(self.current_set_id, uid))
        self.subsec_name_edit.clear()
        self.subsec_note_edit.clear()
        self._on_clip_cancel_clicked()
        self._schedule_save_notes()

    def _on_subsection_clear_all_clicked(self):
        """Clear all sub-sections for the current file."""
        if not self.current_audio_file: return
        
        reply = QMessageBox.question(self, "Clear All Sub-sections", 
                                   "Remove all sub-sections for this song?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
            
        fname = self.current_audio_file.name
        notes = self.notes_by_file.get(fname, [])
        
        # Collect subsections for undo
        removed_subsections = [entry for entry in notes if entry.get("subsection")]
        if not removed_subsections:
            QMessageBox.information(self, "No Sub-sections", "No sub-sections found to clear.")
            return
            
        # Remove subsections
        self.notes_by_file[fname] = [entry for entry in notes if not entry.get("subsection")]
        
        # Push undo for each removed subsection
        for entry in removed_subsections:
            self._push_undo({"type":"remove","set":self.current_set_id,"file":fname,"entry":entry})
            
        self._resort_and_rebuild_table_preserving_selection()
        self._schedule_save_notes()
        QMessageBox.information(self, "Cleared", f"Removed {len(removed_subsections)} sub-sections.")

    def _on_clear_all_provided_names(self):
        """Clear all provided names from the current practice session files."""
        # Get the current directory where provided names are stored
        current_dir = self._get_audio_file_dir()
        
        # Check if there are any provided names to clear
        if not self.provided_names:
            QMessageBox.information(self, "No Provided Names", "No provided names found to clear.")
            return
        
        # Confirmation dialog
        reply = QMessageBox.question(self, "Clear All Provided Names",
                                   f"Remove all provided names from files in this practice session?\n\n"
                                   f"Directory: {current_dir}\n"
                                   f"This will clear {len(self.provided_names)} provided name(s).",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Count how many names we're clearing
        cleared_count = len(self.provided_names)
        
        # Clear all provided names
        self.provided_names.clear()
        
        # Save the empty provided names to the JSON file
        self._save_names()
        
        # Refresh the library table to show the cleared names
        self._refresh_right_table()
        
        # Clear the provided name field if there's a current file
        self._refresh_provided_name_field()
        
        # Show confirmation message
        QMessageBox.information(self, "Cleared", f"Removed {cleared_count} provided name(s).")

    def _on_subsection_relabel_all_clicked(self):
        """Re-run fingerprinting to label all sub-sections in current folder."""
        if not self.current_audio_file:
            QMessageBox.information(self, "No File", "Please select an audio file first.")
            return
        
        reply = QMessageBox.question(self, "Re-label Sub-sections", 
                                   "This will attempt to find and copy sub-sections from other practice folders based on fingerprinting matches. Continue?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
            
        # Run the subsection fingerprinting logic
        self._auto_label_subsections_with_fingerprints()

    def _auto_label_subsections_with_fingerprints(self):
        """Auto-label sub-sections in current folder based on fingerprint matches from all available folders."""
        self._create_backup_if_needed()  # Create backup before first modification
        current_dir = self._get_audio_file_dir()
        
        # Discover practice folders with fingerprints
        practice_folders = discover_practice_folders_with_fingerprints(self.root_path)
        
        # Collect ALL available folders with fingerprints (practice folders + reference folder)
        all_fingerprint_folders = list(practice_folders)  # Start with practice folders
        
        # Add reference folder if it exists and has fingerprints (and isn't already included)
        if self.fingerprint_reference_dir and (self.fingerprint_reference_dir / FINGERPRINTS_JSON).exists():
            if self.fingerprint_reference_dir not in all_fingerprint_folders:
                all_fingerprint_folders.append(self.fingerprint_reference_dir)
        
        if not all_fingerprint_folders:
            QMessageBox.warning(self, "No Folders with Fingerprints", 
                              "No folders with fingerprints found.")
            return
        
        # If current folder is the only one with fingerprints, nothing to match against
        if len(all_fingerprint_folders) == 1 and all_fingerprint_folders[0].resolve() == current_dir.resolve():
            QMessageBox.information(self, "No Other Folders", 
                                  "Current folder is the only one with fingerprints. Need other folders to match against.")
            return
            
        # Collect fingerprints from all available folders (excluding current)
        fingerprint_map = collect_fingerprints_from_folders(all_fingerprint_folders, self.fingerprint_algorithm, exclude_dir=current_dir)
        
        if not fingerprint_map:
            QMessageBox.warning(self, "No Reference Fingerprints", 
                              "No fingerprints found in other available folders.")
            return
            
        # Process each audio file in current folder
        current_cache = load_fingerprint_cache(current_dir)
        matches_found = 0
        subsections_added = 0
        
        progress = QProgressDialog("Finding sub-section matches...", "Cancel", 0, 100, self)
        progress.setWindowTitle("Sub-section Fingerprinting")
        progress.show()
        
        audio_files = [f for f in current_dir.iterdir() if f.is_file() and f.suffix.lower() in AUDIO_EXTS]
        
        for i, audio_file in enumerate(audio_files):
            if progress.wasCanceled():
                break
                
            progress.setLabelText(f"Matching {audio_file.name}...")
            progress.setValue(int((i / len(audio_files)) * 100))
            QApplication.processEvents()
            
            # Get or generate fingerprint for current file using selected algorithm
            current_file_data = current_cache.get("files", {}).get(audio_file.name, {})
            current_fp = get_fingerprint_for_algorithm(current_file_data, self.fingerprint_algorithm)
            
            if not current_fp:
                try:
                    samples, sr, dur_ms, _ = decode_audio_samples(audio_file)
                    # Generate fingerprint for current algorithm
                    new_fingerprints = compute_multiple_fingerprints(samples, sr, [self.fingerprint_algorithm])
                    current_fp = new_fingerprints.get(self.fingerprint_algorithm)
                    
                    # Update cache with new fingerprint
                    size, mtime = file_signature(audio_file)
                    existing_fingerprints = current_file_data.get("fingerprints", {})
                    # Handle legacy format migration inline for existing data
                    if not existing_fingerprints and "fingerprint" in current_file_data:
                        existing_fingerprints = {DEFAULT_ALGORITHM: current_file_data["fingerprint"]}
                    
                    existing_fingerprints.update(new_fingerprints)
                    current_cache.setdefault("files", {})[audio_file.name] = {
                        "fingerprints": existing_fingerprints,
                        "size": size,
                        "mtime": mtime,
                        "duration_ms": dur_ms
                    }
                except Exception as e:
                    log_print(f"Error processing {audio_file.name}: {e}")
                    continue
            
            # Find best match across all practice folders
            match_result = find_best_cross_folder_match(current_fp, fingerprint_map, self.fingerprint_threshold)
            
            if match_result:
                matched_filename, score, source_folder, provided_name = match_result
                matches_found += 1
                
                # Load sub-sections from the matched file
                subsections_copied = self._copy_subsections_from_matched_file(audio_file.name, source_folder, matched_filename)
                subsections_added += subsections_copied
                
        progress.setValue(100)
        save_fingerprint_cache(current_dir, current_cache)
        
        if matches_found > 0:
            QMessageBox.information(self, "Sub-section Matching Complete", 
                                  f"Found {matches_found} matches.\nCopied {subsections_added} sub-sections.")
            self._load_annotations_for_current()
        else:
            QMessageBox.information(self, "No Matches", "No matching songs found for sub-section copying.")

    def _copy_subsections_from_matched_file(self, target_filename: str, source_folder: Path, source_filename: str) -> int:
        """Copy sub-sections from a matched file in another folder to the current file."""
        # Load notes from the source folder
        user = getpass.getuser()
        source_notes_path = source_folder / f".audio_notes_{user}.json"
        if not source_notes_path.exists():
            source_notes_path = source_folder / NOTES_JSON  # Fallback to legacy
        
        source_data = load_json(source_notes_path, {})
        if not isinstance(source_data, dict) or "sets" not in source_data:
            return 0
            
        # Find sub-sections in any visible set from the source file
        subsections_to_copy = []
        for annotation_set in source_data.get("sets", []):
            if not annotation_set.get("visible", True):
                continue
            files = annotation_set.get("files", {})
            source_file_data = files.get(source_filename, {})
            notes = source_file_data.get("notes", [])
            
            for note in notes:
                if note.get("subsection"):
                    subsections_to_copy.append(note)
        
        if not subsections_to_copy:
            return 0
            
        # Clear existing sub-sections for the target file
        fname = target_filename
        existing_notes = self.notes_by_file.get(fname, [])
        self.notes_by_file[fname] = [entry for entry in existing_notes if not entry.get("subsection")]
        
        # Add copied sub-sections with new UIDs
        copied_count = 0
        for subsection in subsections_to_copy:
            uid = self._uid_counter; self._uid_counter += 1
            entry = {
                "uid": int(uid),
                "ms": int(subsection.get("ms", 0)),
                "end_ms": int(subsection.get("end_ms", 0)),
                "text": str(subsection.get("text", "")),
                "important": False,
                "subsection": True
            }
            self.notes_by_file[fname].append(entry)
            copied_count += 1
            
        if copied_count > 0:
            self._schedule_save_notes()
            
        return copied_count
        
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
        # Clear any selected file to avoid rename conflicts when file is in use
        self.tree.selectionModel().clearSelection()
        
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
        # Restore folder selection after tree refresh
        QTimer.singleShot(100, self._restore_folder_selection)
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

    # ----- Mono conversion -----
    def _convert_to_mono(self):
        if not HAVE_PYDUB:
            QMessageBox.warning(self, "Missing dependency",
                                "This feature requires the 'pydub' package and FFmpeg installed on your system.")
            return
        if not pydub_which("ffmpeg"):
            QMessageBox.warning(self, "FFmpeg not found",
                                "FFmpeg isn't available on your PATH. Please install FFmpeg and try again.")
            return
        
        # Check if we have a currently selected audio file
        if not self.current_audio_file or not self.current_audio_file.exists():
            QMessageBox.information(self, "No File Selected", "Please select an audio file to convert to mono.")
            return
        
        # Check if the file is already mono
        channels = self._get_cached_channel_count(self.current_audio_file)
        if channels == 1:
            QMessageBox.information(self, "Already Mono", "The selected file is already mono.")
            return
        
        # Confirm conversion
        msg = (f"Convert '{self.current_audio_file.name}' to mono?\n\n"
               "• The original stereo file will be renamed with '_stereo' suffix\n"
               "• A new mono version will replace the original filename")
        if QMessageBox.question(self, "Convert to Mono", msg,
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return

        self._stop_playback()

        # Create progress dialog
        dlg = QProgressDialog("Converting to mono…", "Cancel", 0, 1, self)
        dlg.setWindowTitle("Mono Conversion")
        dlg.setWindowModality(Qt.WindowModality.WindowModal)
        dlg.setAutoClose(False)
        dlg.setAutoReset(False)
        dlg.setMinimumDuration(0)
        dlg.setValue(0)

        # Create worker thread
        self._mono_thread = QThread(self)
        self._mono_worker = MonoConvertWorker(str(self.current_audio_file))
        self._mono_worker.moveToThread(self._mono_thread)

        def on_progress(done: int, total: int, name: str):
            dlg.setLabelText(f"Converting {name}")
            dlg.setRange(0, total)
            dlg.setValue(done)

        def on_file_done(filename: str, success: bool, msg: str):
            if success:
                # Refresh the file system model and reload annotations
                self.fs_model.setRootPath("")
                self.fs_model.setRootPath(str(self.root_path))
                self.tree.setRootIndex(self.file_proxy.mapFromSource(self.fs_model.index(str(self.root_path))))
                # Restore folder selection after tree refresh
                QTimer.singleShot(100, self._restore_folder_selection)
                self._load_annotations_for_current()

        def on_finished(canceled: bool):
            dlg.close()
            if not canceled:
                QMessageBox.information(self, "Conversion Complete", 
                                        f"Successfully converted '{self.current_audio_file.name}' to mono.")
                # Reload the current file to update waveform display
                if self.current_audio_file and self.current_audio_file.exists():
                    self._play_file(self.current_audio_file)
            
            # Clean up
            self._mono_worker.deleteLater()
            self._mono_thread.quit()
            self._mono_thread.wait()
            self._mono_thread.deleteLater()
            self._mono_worker = None
            self._mono_thread = None

        # Connect signals
        self._mono_thread.started.connect(self._mono_worker.run)
        self._mono_worker.progress.connect(on_progress)
        self._mono_worker.file_done.connect(on_file_done)
        self._mono_worker.finished.connect(on_finished)
        dlg.canceled.connect(self._mono_worker.cancel)

        # Start the conversion
        self._mono_thread.start()
        dlg.exec()

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
            # Restore folder selection after tree refresh
            QTimer.singleShot(100, self._restore_folder_selection)
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
        
        # Collect ALL available folders with fingerprints (practice folders + reference folder)
        all_fingerprint_folders = list(practice_folders)  # Start with practice folders
        
        # Add reference folder if it exists and has fingerprints (and isn't already included)
        if self.fingerprint_reference_dir and (self.fingerprint_reference_dir / FINGERPRINTS_JSON).exists():
            if self.fingerprint_reference_dir not in all_fingerprint_folders:
                all_fingerprint_folders.append(self.fingerprint_reference_dir)
        
        # Count total fingerprints available for matching (excluding current folder)
        fingerprint_map = collect_fingerprints_from_folders(all_fingerprint_folders, self.fingerprint_algorithm, exclude_dir=current_dir)
        total_available_songs = len(fingerprint_map)
        unique_songs = sum(1 for song_entries in fingerprint_map.values() if len(song_entries) == 1)
        
        # Enable auto-label if we have any folders with fingerprints (excluding current folder)
        other_folders = [f for f in all_fingerprint_folders if f.resolve() != current_dir.resolve()]
        can_auto_label = not self.auto_label_in_progress and bool(other_folders)
        
        # Show information about all available folders for fingerprinting
        colors = get_consistent_stylesheet_colors()
        if not all_fingerprint_folders:
            self.fingerprint_ref_label.setText("(No fingerprints found)")
            self.fingerprint_ref_label.setStyleSheet(f"color: {colors['text_muted']}; font-style: italic;")
        elif len(all_fingerprint_folders) == 1 and all_fingerprint_folders[0].resolve() == current_dir.resolve():
            folder_text = f"Current folder only ({all_fingerprint_folders[0].name})"
            self.fingerprint_ref_label.setText(folder_text)
            self.fingerprint_ref_label.setStyleSheet(f"color: {colors['text_secondary']};")
        else:
            # Count different types of folders
            num_practice = len(practice_folders)
            has_reference = self.fingerprint_reference_dir and (self.fingerprint_reference_dir / FINGERPRINTS_JSON).exists()
            other_folders_count = len([f for f in all_fingerprint_folders if f.resolve() != current_dir.resolve()])
            
            # Build description
            parts = []
            if num_practice > 0:
                parts.append(f"{num_practice} practice")
            if has_reference:
                parts.append("1 reference")
            
            if parts:
                folder_text = f"{other_folders_count} available: " + " + ".join(parts) + " folders"
            else:
                folder_text = f"{other_folders_count} available folders"
            
            self.fingerprint_ref_label.setText(folder_text)
            self.fingerprint_ref_label.setStyleSheet(f"color: {colors['text_secondary']};")
        
        self.auto_label_btn.setEnabled(can_auto_label)
        
        # Update status with current folder and available songs info
        current_cache = load_fingerprint_cache(current_dir)
        num_current_fingerprints = len(current_cache.get("files", {}))
        
        # Add algorithm info to status
        algorithm_name = FINGERPRINT_ALGORITHMS[self.fingerprint_algorithm]["name"]
        status_parts = [f"Algorithm: {algorithm_name}"]
        status_parts.append(f"Current: {num_current_fingerprints} fingerprints")
        if total_available_songs > 0:
            status_parts.append(f"Available: {total_available_songs} songs")
            if unique_songs > 0:
                status_parts.append(f"({unique_songs} unique)")
        
        self.fingerprint_status.setText(" | ".join(status_parts))

    def _show_practice_folders_info(self):
        """Show information about all available folders with fingerprints."""
        practice_folders = discover_practice_folders_with_fingerprints(self.root_path)
        current_dir = self._get_audio_file_dir()
        
        # Collect ALL available folders with fingerprints (practice folders + reference folder)
        all_fingerprint_folders = list(practice_folders)  # Start with practice folders
        
        # Add reference folder if it exists and has fingerprints (and isn't already included)
        if self.fingerprint_reference_dir and (self.fingerprint_reference_dir / FINGERPRINTS_JSON).exists():
            if self.fingerprint_reference_dir not in all_fingerprint_folders:
                all_fingerprint_folders.append(self.fingerprint_reference_dir)
        
        if not all_fingerprint_folders:
            QMessageBox.information(self, "No Folders with Fingerprints Found", 
                                  "No folders with fingerprints were found.\n\n"
                                  "To use cross-folder matching:\n"
                                  "1. Navigate to practice session folders and generate fingerprints\n"
                                  "2. Or select a reference folder and generate fingerprints\n"
                                  "3. The system will automatically find and use them for matching")
            return
        
        # Collect detailed information
        info_lines = [f"Found {len(all_fingerprint_folders)} folder(s) with fingerprints:\n"]
        
        total_songs = 0
        unique_songs = 0
        fingerprint_map = collect_fingerprints_from_folders(all_fingerprint_folders, self.fingerprint_algorithm, exclude_dir=current_dir)
        
        for folder in all_fingerprint_folders:
            cache = load_fingerprint_cache(folder)
            num_files = len(cache.get("files", {}))
            total_songs += num_files
            
            is_current = folder.resolve() == current_dir.resolve()
            current_marker = " (current)" if is_current else ""
            
            # Determine folder type
            is_reference = self.fingerprint_reference_dir and folder.resolve() == self.fingerprint_reference_dir.resolve()
            folder_type = " [reference]" if is_reference else ""
            
            info_lines.append(f"• {folder.name}: {num_files} fingerprints{current_marker}{folder_type}")
        
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

    def _on_fingerprint_algorithm_changed(self):
        """Handle algorithm change."""
        selected_data = self.algorithm_combo.currentData()
        if selected_data and selected_data in FINGERPRINT_ALGORITHMS:
            self.fingerprint_algorithm = selected_data
            self.settings.setValue(SETTINGS_KEY_FINGERPRINT_ALGORITHM, self.fingerprint_algorithm)
            self._update_fingerprint_ui()

    # ----- Auto-generation callbacks -----
    def _generate_fingerprints_for_folder(self):
        """Generate fingerprints for all audio files in the current folder."""
        # Check if a fingerprinting operation is already in progress
        if hasattr(self, '_fingerprint_thread') and self._fingerprint_thread is not None and self._fingerprint_thread.isRunning():
            QMessageBox.warning(self, "Fingerprinting In Progress", 
                              "Fingerprinting is already in progress. Please wait for it to complete.")
            return
            
        current_dir = self._get_audio_file_dir()
        audio_files = self._list_audio_in_current_dir()
        
        if not audio_files:
            QMessageBox.information(self, "No Audio Files", "No audio files found in current folder.")
            return
        
        cache = load_fingerprint_cache(current_dir)
        
        # Check if fingerprints already exist in the current folder
        existing_fingerprints = len(cache.get("files", {}))
        force_regenerate = False
        
        if existing_fingerprints > 0:
            # Prompt user to confirm regeneration
            reply = QMessageBox.question(
                self, 
                "Regenerate Fingerprints", 
                f"This folder already contains {existing_fingerprints} fingerprint(s).\n\n"
                f"Do you want to regenerate all fingerprints for the {len(audio_files)} audio files in this folder?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                force_regenerate = True
            else:
                return
        
        # Create progress dialog
        self._fingerprint_progress = QProgressDialog("Preparing fingerprint generation...", "Cancel", 0, len(audio_files), self)
        self._fingerprint_progress.setWindowTitle("Generating Fingerprints")
        self._fingerprint_progress.setWindowModality(Qt.WindowModality.WindowModal)
        self._fingerprint_progress.setAutoClose(False)
        self._fingerprint_progress.setAutoReset(False)
        self._fingerprint_progress.setMinimumDuration(0)
        self._fingerprint_progress.setValue(0)

        # Disable fingerprinting button to prevent concurrent operations  
        self.generate_fingerprints_btn.setEnabled(False)

        # Create and setup the worker thread
        self._fingerprint_thread = QThread(self)
        self._fingerprint_worker = FingerprintWorker([str(f) for f in audio_files], str(current_dir), force_regenerate)
        self._fingerprint_worker.moveToThread(self._fingerprint_thread)

        # Variables to track results
        self._fingerprint_generated_count = 0
        self._fingerprint_force_regenerate = force_regenerate

        # Connect signals
        def on_progress(current_index: int, total_files: int, filename: str):
            self._fingerprint_progress.setLabelText(f"Processing {filename}...")
            self._fingerprint_progress.setValue(current_index)

        def on_file_done(filename: str, success: bool, message: str):
            if success and "Generated" in message:
                self._fingerprint_generated_count += 1

        def on_finished(generated_count: int, canceled: bool):
            self._fingerprint_progress.hide()
            
            if canceled:
                QMessageBox.information(self, "Fingerprinting Canceled", "Fingerprint generation was canceled.")
            else:
                # Reload cache to get final count
                final_cache = load_fingerprint_cache(current_dir)
                total_fingerprints = len(final_cache.get("files", {}))
                
                if self._fingerprint_force_regenerate:
                    QMessageBox.information(self, "Fingerprints Regenerated", 
                                            f"Regenerated fingerprints for {generated_count} files.\n"
                                            f"Total fingerprints in folder: {total_fingerprints}")
                else:
                    QMessageBox.information(self, "Fingerprints Generated", 
                                            f"Generated fingerprints for {generated_count} files.\n"
                                            f"Total fingerprints in folder: {total_fingerprints}")
            
            # Invalidate the exclusion cache since fingerprint files may have been modified
            self.file_proxy.invalidate_exclusion_cache(current_dir)
            
            # Update UI and cleanup
            self.generate_fingerprints_btn.setEnabled(True)
            self._update_fingerprint_ui()
            self._cleanup_fingerprint_thread()

        def on_error():
            self._fingerprint_progress.hide()
            self.generate_fingerprints_btn.setEnabled(True)
            QMessageBox.critical(self, "Fingerprinting Error", "An error occurred during fingerprint generation.")
            self._cleanup_fingerprint_thread()

        # Connect all signals
        self._fingerprint_thread.started.connect(self._fingerprint_worker.run)
        self._fingerprint_worker.progress.connect(on_progress)
        self._fingerprint_worker.file_done.connect(on_file_done)
        self._fingerprint_worker.finished.connect(on_finished)
        self._fingerprint_progress.canceled.connect(self._fingerprint_worker.cancel)

        # Start the thread
        self._fingerprint_thread.start()
        self._fingerprint_progress.show()  # Show non-blocking, unlike exec()

    def _cleanup_fingerprint_thread(self):
        """Clean up fingerprint worker thread and related objects."""
        if hasattr(self, '_fingerprint_worker') and self._fingerprint_worker:
            self._fingerprint_worker.deleteLater()
            self._fingerprint_worker = None
        
        if hasattr(self, '_fingerprint_thread') and self._fingerprint_thread:
            self._fingerprint_thread.quit()
            self._fingerprint_thread.wait()
            self._fingerprint_thread.deleteLater()
            self._fingerprint_thread = None

    def _auto_label_with_fingerprints(self):
        """Auto-label files in current folder based on fingerprint matches from practice folders."""
        self._create_backup_if_needed()  # Create backup before first modification
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
        
        # Collect ALL available folders with fingerprints (practice folders + reference folder)
        all_fingerprint_folders = list(practice_folders)  # Start with practice folders
        
        # Add reference folder if it exists and has fingerprints (and isn't already included)
        if self.fingerprint_reference_dir and (self.fingerprint_reference_dir / FINGERPRINTS_JSON).exists():
            if self.fingerprint_reference_dir not in all_fingerprint_folders:
                all_fingerprint_folders.append(self.fingerprint_reference_dir)
        
        # Check if we have any folders with fingerprints
        if not all_fingerprint_folders:
            QMessageBox.warning(self, "No Fingerprints Available", 
                              "No folders with fingerprints found.\n"
                              "Please select a reference folder or generate fingerprints for practice folders first.")
            return
        
        # If current folder is the only one with fingerprints, nothing to match against
        if len(all_fingerprint_folders) == 1 and all_fingerprint_folders[0].resolve() == current_dir.resolve():
            QMessageBox.information(self, "No Other Folders", 
                                  "Current folder is the only one with fingerprints. Need other folders to match against.")
            return
        
        # Collect fingerprints from all available folders (excluding current)
        fingerprint_map = collect_fingerprints_from_folders(all_fingerprint_folders, self.fingerprint_algorithm, exclude_dir=current_dir)
        
        if not fingerprint_map:
            QMessageBox.warning(self, "No Reference Fingerprints", 
                              "No fingerprints found in other available folders.")
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
            
            # Get or generate fingerprint for current file using selected algorithm
            current_file_data = current_fingerprints.get(audio_file.name, {})
            current_fp = get_fingerprint_for_algorithm(current_file_data, self.fingerprint_algorithm)
            
            if not current_fp:
                try:
                    samples, sr, dur_ms, _ = decode_audio_samples(audio_file)
                    # Generate fingerprint for current algorithm
                    new_fingerprints = compute_multiple_fingerprints(samples, sr, [self.fingerprint_algorithm])
                    current_fp = new_fingerprints.get(self.fingerprint_algorithm)
                    
                    # Update cache with new fingerprint
                    size, mtime = file_signature(audio_file)
                    existing_fingerprints = current_file_data.get("fingerprints", {})
                    # Handle legacy format migration inline for existing data
                    if not existing_fingerprints and "fingerprint" in current_file_data:
                        existing_fingerprints = {DEFAULT_ALGORITHM: current_file_data["fingerprint"]}
                    
                    existing_fingerprints.update(new_fingerprints)
                    current_cache["files"][audio_file.name] = {
                        "fingerprints": existing_fingerprints,
                        "size": size,
                        "mtime": mtime,
                        "duration_ms": dur_ms
                    }
                except Exception as e:
                    log_print(f"Error processing {audio_file.name}: {e}")
                    continue
            
            # Find best match across all practice folders
            match_result = find_best_cross_folder_match(current_fp, fingerprint_map, self.fingerprint_threshold)
            
            if match_result:
                matched_filename, score, source_folder, provided_name = match_result
                
                # Use the provided name from the matched fingerprint's folder
                self.provided_names[audio_file.name] = provided_name
                matches_found += 1
                
                # Also copy sub-sections from the matched file
                subsections_copied = self._copy_subsections_from_matched_file(audio_file.name, source_folder, matched_filename)
                if subsections_copied > 0:
                    log_print(f"Copied {subsections_copied} sub-sections for {audio_file.name}")
                
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
            result_message += f"Scanned {len(all_fingerprint_folders)} folders with fingerprints\n\n"
            
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
            result_message += f"Scanned {len(all_fingerprint_folders)} folders with fingerprints"
            
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
            
            # Check if fingerprints already exist and are up to date
            size, mtime = file_signature(audio_file)
            existing = cache["files"].get(audio_file.name)
            
            # Check if we need to generate any new fingerprints
            existing_fingerprints = existing.get("fingerprints", {}) if existing else {}
            # Handle legacy format
            if not existing_fingerprints and existing and "fingerprint" in existing:
                existing_fingerprints = {DEFAULT_ALGORITHM: existing["fingerprint"]}
            
            needs_update = (not existing or 
                          existing.get("size") != size or 
                          existing.get("mtime") != mtime or 
                          len(existing_fingerprints) < len(FINGERPRINT_ALGORITHMS))
            
            if not needs_update:
                continue
            
            try:
                samples, sr, dur_ms, _ = decode_audio_samples(audio_file)
                
                # Determine which algorithms to generate
                if not existing or existing.get("size") != size or existing.get("mtime") != mtime:
                    # File changed, regenerate all algorithms
                    algorithms_to_generate = list(FINGERPRINT_ALGORITHMS.keys())
                else:
                    # File unchanged, only generate missing algorithms
                    algorithms_to_generate = [alg for alg in FINGERPRINT_ALGORITHMS.keys() 
                                              if alg not in existing_fingerprints]
                
                if algorithms_to_generate:
                    new_fingerprints = compute_multiple_fingerprints(samples, sr, algorithms_to_generate)
                    
                    # Merge with existing fingerprints
                    all_fingerprints = existing_fingerprints.copy()
                    all_fingerprints.update(new_fingerprints)
                    
                    cache["files"][audio_file.name] = {
                        "fingerprints": all_fingerprints,
                        "size": size,
                        "mtime": mtime,
                        "duration_ms": dur_ms
                    }
                generated += 1
                
            except Exception as e:
                log_print(f"Error generating fingerprint for {audio_file.name}: {e}")
        
        progress.setValue(len(ref_audio_files))
        save_fingerprint_cache(self.fingerprint_reference_dir, cache)
        
        QMessageBox.information(self, "Reference Fingerprints Generated",
                                f"Generated {generated} new fingerprints in reference folder.")

    def _show_auto_generation_settings(self):
        """Show auto-generation settings dialog."""
        # Gather current settings
        current_settings = {
            'auto_gen_waveforms': self.auto_gen_waveforms,
            'auto_gen_fingerprints': self.auto_gen_fingerprints,
            'auto_gen_timing': self.auto_gen_timing
        }
        
        # Show dialog
        dialog = AutoGenerationSettingsDialog(current_settings, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Apply new settings
            new_settings = dialog.get_settings()
            
            self.auto_gen_waveforms = new_settings['auto_gen_waveforms']
            self.auto_gen_fingerprints = new_settings['auto_gen_fingerprints'] 
            self.auto_gen_timing = new_settings['auto_gen_timing']
            
            # Print updated settings for debugging
            log_print("Auto-generation settings updated:")
            log_print(f"  Waveforms: {self.auto_gen_waveforms}")
            log_print(f"  Fingerprints: {self.auto_gen_fingerprints}")
            log_print(f"  Timing: {self.auto_gen_timing}")
            
            # Save to persistent settings
            self.settings.setValue(SETTINGS_KEY_AUTO_GEN_WAVEFORMS, int(self.auto_gen_waveforms))
            self.settings.setValue(SETTINGS_KEY_AUTO_GEN_FINGERPRINTS, int(self.auto_gen_fingerprints))
            self.settings.setValue(SETTINGS_KEY_AUTO_GEN_TIMING, self.auto_gen_timing)

    def _show_about_dialog(self):
        """Show About dialog with version information."""
        about_text = f"""<h2>{APP_NAME}</h2>
<p><strong>{VERSION_INFO}</strong></p>

<p>Audio file browser and annotation tool for band practice workflow management.</p>

<h3>Key Features:</h3>
<ul>
<li>Audio file browser with waveform visualization</li>
<li>Multi-user annotation system with timestamped notes</li>
<li>Best take and partial take marking system</li>
<li>Batch renaming and audio conversion tools</li>
<li>Audio fingerprinting for automatic song identification</li>
<li>Backup and restore system for metadata</li>
</ul>

<p><em>Built with PyQt6 and developed with heavy use of AI assistance (ChatGPT/Copilot).</em></p>"""
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(f"About {APP_NAME}")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(about_text)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def _show_changelog_dialog(self):
        """Show changelog dialog with version history."""
        try:
            # Try to read the changelog file
            changelog_path = Path(__file__).parent / "CHANGELOG.md"
            if changelog_path.exists():
                changelog_content = changelog_path.read_text(encoding='utf-8')
            else:
                changelog_content = f"# {APP_NAME} Changelog\n\nChangelog file not found.\n\nCurrent version: {VERSION_INFO}"
        except Exception as e:
            changelog_content = f"# {APP_NAME} Changelog\n\nError reading changelog: {e}\n\nCurrent version: {VERSION_INFO}"
        
        # Create a custom dialog for better changelog viewing
        dialog = QDialog(self)
        dialog.setWindowTitle(f"{APP_NAME} - Changelog")
        dialog.resize(800, 600)
        
        layout = QVBoxLayout(dialog)
        
        # Add text display area
        text_edit = QTextEdit()
        text_edit.setPlainText(changelog_content)
        text_edit.setReadOnly(True)
        text_edit.setFont(self.font())  # Use application font
        layout.addWidget(text_edit)
        
        # Add close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        dialog.exec()

    # ----- Auto-generation methods -----
    def _start_auto_generation_for_folder(self, folder_path: Path):
        """Start auto-generation for the given folder and its subdirectories if enabled and not already running."""
        log_print(f"Auto-generation check for folder: {folder_path}")
        
        # Validate folder_path
        if not folder_path:
            log_print("  ERROR: folder_path is None or empty")
            self.statusBar().showMessage("Auto-generation failed: invalid folder path", 3000)
            return
        
        if not isinstance(folder_path, Path):
            log_print(f"  ERROR: folder_path is not a Path object (type: {type(folder_path)})")
            self.statusBar().showMessage("Auto-generation failed: invalid folder path", 3000)
            return
        
        if not folder_path.exists():
            log_print(f"  ERROR: Folder does not exist: {folder_path}")
            self.statusBar().showMessage("Auto-generation failed: folder not found", 3000)
            return
        
        if not folder_path.is_dir():
            log_print(f"  ERROR: Path is not a directory: {folder_path}")
            self.statusBar().showMessage("Auto-generation failed: not a directory", 3000)
            return
        
        if self._auto_gen_in_progress:
            log_print("  Skipped: auto-generation already in progress")
            self.statusBar().showMessage("Auto-generation already running", 2000)
            return  # Already running
        
        # Check what needs to be generated first
        needs_waveforms = self.auto_gen_waveforms
        needs_fingerprints = self.auto_gen_fingerprints
        
        log_print(f"  Settings: waveforms={needs_waveforms}, fingerprints={needs_fingerprints}")
        
        if not needs_waveforms and not needs_fingerprints:
            log_print("  Skipped: auto-generation disabled in settings")
            self.statusBar().showMessage("Auto-generation skipped: disabled in settings", 3000)
            return  # Nothing to generate
            
        # Discover all directories with audio files recursively
        log_print("  Discovering directories with audio files...")
        directories_with_audio = discover_directories_with_audio_files(folder_path)
        
        if not directories_with_audio:
            log_print("  Skipped: no directories with audio files found")
            self.statusBar().showMessage("Auto-generation skipped: no audio files found", 3000)
            return  # No directories with audio files to process
        
        log_print(f"  Found {len(directories_with_audio)} directories with audio files:")
        for i, directory in enumerate(directories_with_audio):
            log_print(f"    {i+1}. {directory}")
            
        # Collect all audio files from all discovered directories
        all_audio_files = []
        directories_to_process = []
        
        try:
            for directory in directories_with_audio:
                directory_audio_files = []
                for ext in AUDIO_EXTS:
                    found_files = list(directory.glob(f"*{ext}"))
                    directory_audio_files.extend(found_files)
                
                if directory_audio_files:
                    log_print(f"    {directory}: {len(directory_audio_files)} audio files")
                    all_audio_files.extend(directory_audio_files)
                    directories_to_process.append(directory)
                    
        except Exception as e:
            log_print(f"  ERROR: Failed to scan directories for audio files: {e}")
            self.statusBar().showMessage(f"Auto-generation failed: {str(e)}", 3000)
            return
            
        if not all_audio_files:
            log_print("  Skipped: no audio files found in any directories")
            self.statusBar().showMessage("Auto-generation skipped: no audio files found", 3000)
            return  # No audio files to process
            
        log_print(f"  Starting recursive auto-generation for {len(all_audio_files)} audio files across {len(directories_to_process)} directories")
        self._auto_gen_in_progress = True
        
        # Start with waveforms if needed, then fingerprints
        try:
            if needs_waveforms:
                self._start_auto_waveform_generation_recursive(directories_to_process, needs_fingerprints)
            elif needs_fingerprints:
                self._start_auto_fingerprint_generation_recursive(directories_to_process)
        except Exception as e:
            log_print(f"  ERROR: Failed to start auto-generation: {e}")
            self.statusBar().showMessage(f"Auto-generation failed: {str(e)}", 3000)
            self._auto_gen_in_progress = False  # Reset flag on error
            return
            
    def _start_auto_waveform_generation_recursive(self, directories: List[Path], follow_with_fingerprints: bool = False):
        """Start recursive auto waveform generation for multiple directories."""
        if not directories:
            self._finish_auto_generation()
            return
            
        log_print(f"Starting recursive waveform generation for {len(directories)} directories...")
        self.statusBar().showMessage(f"Generating waveforms in {len(directories)} directories...")
        
        # Store state for recursive processing
        self._directories_to_process = directories[:]
        self._current_directory_index = 0
        self._follow_with_fingerprints = follow_with_fingerprints
        
        # Start with the first directory
        self._process_next_directory_waveforms()
    
    def _process_next_directory_waveforms(self):
        """Process waveforms for the next directory in the queue."""
        if self._current_directory_index >= len(self._directories_to_process):
            # All directories processed for waveforms
            log_print("All waveform generation completed")
            
            if self._follow_with_fingerprints and self.auto_gen_fingerprints:
                self._start_auto_fingerprint_generation_recursive(self._directories_to_process)
            else:
                self._finish_auto_generation()
            return
            
        current_directory = self._directories_to_process[self._current_directory_index]
        log_print(f"Processing waveforms for directory {self._current_directory_index + 1}/{len(self._directories_to_process)}: {current_directory}")
        
        # Get audio files for this directory
        audio_files = []
        try:
            for ext in AUDIO_EXTS:
                found_files = list(current_directory.glob(f"*{ext}"))
                audio_files.extend(found_files)
        except Exception as e:
            log_print(f"  ERROR: Failed to scan directory {current_directory}: {e}")
            # Move to next directory
            self._current_directory_index += 1
            self._process_next_directory_waveforms()
            return
            
        if not audio_files:
            log_print(f"  Skipped: no audio files found in {current_directory}")
            # Move to next directory
            self._current_directory_index += 1
            self._process_next_directory_waveforms()
            return
        
        # Process this directory using the existing function
        self._current_directory_index += 1  # Increment before starting
        self._start_auto_waveform_generation(current_directory, audio_files, False)  # Don't follow with fingerprints here
    
    def _start_auto_fingerprint_generation_recursive(self, directories: List[Path]):
        """Start recursive auto fingerprint generation for multiple directories."""
        if not directories:
            self._finish_auto_generation()
            return
            
        log_print(f"Starting recursive fingerprint generation for {len(directories)} directories...")
        self.statusBar().showMessage(f"Generating fingerprints in {len(directories)} directories...")
        
        # Store state for recursive processing
        self._directories_to_process = directories[:]
        self._current_directory_index = 0
        
        # Start with the first directory
        self._process_next_directory_fingerprints()
    
    def _process_next_directory_fingerprints(self):
        """Process fingerprints for the next directory in the queue."""
        if self._current_directory_index >= len(self._directories_to_process):
            # All directories processed
            log_print("All fingerprint generation completed")
            self._finish_auto_generation()
            return
            
        current_directory = self._directories_to_process[self._current_directory_index]
        log_print(f"Processing fingerprints for directory {self._current_directory_index + 1}/{len(self._directories_to_process)}: {current_directory}")
        
        # Get audio files for this directory
        audio_files = []
        try:
            for ext in AUDIO_EXTS:
                found_files = list(current_directory.glob(f"*{ext}"))
                audio_files.extend(found_files)
        except Exception as e:
            log_print(f"  ERROR: Failed to scan directory {current_directory}: {e}")
            # Move to next directory
            self._current_directory_index += 1
            self._process_next_directory_fingerprints()
            return
            
        if not audio_files:
            log_print(f"  Skipped: no audio files found in {current_directory}")
            # Move to next directory
            self._current_directory_index += 1
            self._process_next_directory_fingerprints()
            return
        
        # Process this directory using the existing function
        self._current_directory_index += 1  # Increment before starting
        self._start_auto_fingerprint_generation(current_directory, audio_files)

    def _start_auto_waveform_generation(self, folder_path: Path, audio_files: List[Path], follow_with_fingerprints: bool = False):
        """Start auto waveform generation."""
        log_print(f"Starting waveform generation for {len(audio_files)} files...")
        self.statusBar().showMessage("Generating waveforms...")
        
        try:
            # Create worker and thread
            self._auto_gen_waveform_thread = QThread(self)
            self._auto_gen_waveform_worker = AutoWaveformWorker([str(f) for f in audio_files], str(folder_path))
            self._auto_gen_waveform_worker.moveToThread(self._auto_gen_waveform_thread)
        except Exception as e:
            log_print(f"  ERROR: Failed to create waveform worker: {e}")
            self.statusBar().showMessage(f"Waveform generation failed: {str(e)}", 3000)
            self._auto_gen_in_progress = False
            return
        
        def on_waveform_progress(current, total, filename):
            progress_msg = f"Generating waveforms... {current + 1}/{total}: {filename}"
            log_print(f"  {progress_msg}")
            self.statusBar().showMessage(progress_msg)
            
        def on_waveform_finished(generated_count, canceled):
            self._cleanup_auto_waveform_thread()
            
            if canceled:
                log_print("Waveform generation was canceled")
                self._finish_auto_generation()
                return
                
            log_print(f"Waveform generation completed: {generated_count} files processed")
            
            # Check if we're in recursive mode
            if self._directories_to_process and self._current_directory_index < len(self._directories_to_process):
                # Continue with next directory for waveforms
                self._process_next_directory_waveforms()
            elif follow_with_fingerprints and self.auto_gen_fingerprints:
                # Start fingerprints if requested
                self._start_auto_fingerprint_generation(folder_path, audio_files)
            else:
                # Finish auto-generation
                self._finish_auto_generation()
                
        # Connect signals and start thread
        try:
            self._auto_gen_waveform_thread.started.connect(self._auto_gen_waveform_worker.run)
            self._auto_gen_waveform_worker.progress.connect(on_waveform_progress)
            self._auto_gen_waveform_worker.finished.connect(on_waveform_finished)
            
            # Start thread
            self._auto_gen_waveform_thread.start()
            log_print("  Waveform generation thread started successfully")
        except Exception as e:
            log_print(f"  ERROR: Failed to start waveform generation thread: {e}")
            self.statusBar().showMessage(f"Waveform generation failed to start: {str(e)}", 3000)
            self._cleanup_auto_waveform_thread()
            self._auto_gen_in_progress = False
            return
        
    def _start_auto_fingerprint_generation(self, folder_path: Path, audio_files: List[Path]):
        """Start auto fingerprint generation."""
        log_print(f"Starting fingerprint generation for {len(audio_files)} files...")
        self.statusBar().showMessage("Generating fingerprints...")
        
        try:
            # Create worker and thread
            self._auto_gen_fingerprint_thread = QThread(self)
            self._auto_gen_fingerprint_worker = AutoFingerprintWorker([str(f) for f in audio_files], str(folder_path))
            self._auto_gen_fingerprint_worker.moveToThread(self._auto_gen_fingerprint_thread)
        except Exception as e:
            log_print(f"  ERROR: Failed to create fingerprint worker: {e}")
            self.statusBar().showMessage(f"Fingerprint generation failed: {str(e)}", 3000)
            self._auto_gen_in_progress = False
            return
        
        def on_fingerprint_progress(current, total, filename):
            progress_msg = f"Generating fingerprints... {current + 1}/{total}: {filename}"
            log_print(f"  {progress_msg}")
            self.statusBar().showMessage(progress_msg)
        
        def on_fingerprint_finished(generated_count, canceled):
            self._cleanup_auto_fingerprint_thread()
            if canceled:
                log_print("Fingerprint generation was canceled")
                self._finish_auto_generation()
                return
            else:
                log_print(f"Fingerprint generation completed: {generated_count} files processed")
            
            # Check if we're in recursive mode
            if self._directories_to_process and self._current_directory_index < len(self._directories_to_process):
                # Continue with next directory for fingerprints
                self._process_next_directory_fingerprints()
            else:
                # Finish auto-generation
                self._finish_auto_generation()
            
        # Connect signals and start thread
        try:
            self._auto_gen_fingerprint_thread.started.connect(self._auto_gen_fingerprint_worker.run)
            self._auto_gen_fingerprint_worker.progress.connect(on_fingerprint_progress)
            self._auto_gen_fingerprint_worker.finished.connect(on_fingerprint_finished)
            
            # Start thread
            self._auto_gen_fingerprint_thread.start()
            log_print("  Fingerprint generation thread started successfully")
        except Exception as e:
            log_print(f"  ERROR: Failed to start fingerprint generation thread: {e}")
            self.statusBar().showMessage(f"Fingerprint generation failed to start: {str(e)}", 3000)
            self._cleanup_auto_fingerprint_thread()
            self._auto_gen_in_progress = False
            return
        
    def _cancel_auto_generation(self):
        """Cancel the currently running auto-generation."""
        log_print("Canceling auto-generation...")
        if self._auto_gen_waveform_worker:
            self._auto_gen_waveform_worker.cancel()
        if self._auto_gen_fingerprint_worker:
            self._auto_gen_fingerprint_worker.cancel()
            
    def _finish_auto_generation(self):
        """Clean up after auto-generation is complete."""
        self._auto_gen_in_progress = False
        log_print("Auto-generation completed successfully")
        self.statusBar().showMessage("Auto-generation complete", 3000)  # Show for 3 seconds
        
    def _cleanup_auto_waveform_thread(self):
        """Clean up auto waveform worker and thread."""
        if self._auto_gen_waveform_worker:
            self._auto_gen_waveform_worker.deleteLater()
            self._auto_gen_waveform_worker = None
        if self._auto_gen_waveform_thread:
            self._auto_gen_waveform_thread.quit()
            self._auto_gen_waveform_thread.wait()
            self._auto_gen_waveform_thread.deleteLater()
            self._auto_gen_waveform_thread = None
            
    def _cleanup_auto_fingerprint_thread(self):
        """Clean up auto fingerprint worker and thread."""
        if self._auto_gen_fingerprint_worker:
            self._auto_gen_fingerprint_worker.deleteLater()
            self._auto_gen_fingerprint_worker = None
        if self._auto_gen_fingerprint_thread:
            self._auto_gen_fingerprint_thread.quit()
            self._auto_gen_fingerprint_thread.wait()
            self._auto_gen_fingerprint_thread.deleteLater()
            self._auto_gen_fingerprint_thread = None

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
        
        # Cancel any running auto-generation
        if self._auto_gen_in_progress:
            self._cancel_auto_generation()
            
        # Clean up auto-generation threads
        self._cleanup_auto_waveform_thread()
        self._cleanup_auto_fingerprint_thread()

        self._save_names(); self._save_notes(); self._save_duration_cache(); 
        self._cleanup_temp_channel_files();
        super().closeEvent(ev)

# ========== Entrypoint ==========
def main():
    # Set up logging first, before any other output
    setup_logging()
    
    app = QApplication(sys.argv)
    app.setOrganizationName(APP_ORG); app.setApplicationName(APP_NAME)
    
    # Set a consistent style for cross-machine compatibility
    # Fusion provides the most consistent appearance across platforms
    available_styles = QStyleFactory.keys()
    preferred_styles = ["Fusion", "Windows", "WindowsVista", "Breeze", "Qt6CT-Style"]
    
    selected_style = None
    for style in preferred_styles:
        if style in available_styles:
            selected_style = style
            break
    
    if selected_style:
        app.setStyle(selected_style)
        log_print(f"Using Qt style: {selected_style}")
    else:
        log_print(f"Using default Qt style (available: {', '.join(available_styles)})")
    
    # Apply consistent application-wide color scheme
    # This ensures consistent appearance regardless of system theme
    app_palette = app.palette()
    colors = _color_manager.get_ui_colors()
    
    # Set standard colors for consistent appearance
    app_palette.setColor(app_palette.ColorRole.Highlight, colors['info'])
    app_palette.setColor(app_palette.ColorRole.HighlightedText, QColor("white"))
    app.setPalette(app_palette)
    
    w = AudioBrowser(); w.show(); sys.exit(app.exec())

if __name__ == "__main__":
    main()
