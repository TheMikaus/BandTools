# AudioBrowser Code Simplification Examples

## Overview

This document provides concrete examples of how the AudioBrowser codebase can be simplified and refactored. These examples demonstrate patterns that could be applied throughout the application to reduce duplication, improve maintainability, and prepare for potential QML migration.

---

## Table of Contents

1. [Worker Base Class Pattern](#worker-base-class-pattern)
2. [Configuration Manager Pattern](#configuration-manager-pattern)
3. [Method Extraction Examples](#method-extraction-examples)
4. [UI Component Factory Pattern](#ui-component-factory-pattern)
5. [Data Model Classes](#data-model-classes)
6. [JSON Persistence Utility](#json-persistence-utility)
7. [Progress Dialog Consolidation](#progress-dialog-consolidation)
8. [Before/After Comparison](#beforeafter-comparison)

---

## 1. Worker Base Class Pattern

### Problem
Eight worker classes (`WaveformWorker`, `ConvertWorker`, `MonoConvertWorker`, `VolumeBoostWorker`, `ChannelMutingWorker`, `FingerprintWorker`, `AutoWaveformWorker`, `AutoFingerprintWorker`) share similar structure:
- Emit `progress(int, int, str)` signal
- Emit `finished()` signal (with varying parameters)
- Run in QThread or QThreadPool
- Similar error handling patterns

This leads to ~200 lines of duplicate code.

### Solution: Base Worker Class

```python
class BaseWorker(QObject):
    """Base class for background workers with common signal patterns."""
    progress = pyqtSignal(int, int, str)  # current, total, filename
    finished = pyqtSignal(object)  # result (varies by subclass)
    error = pyqtSignal(str)  # error message
    
    def __init__(self):
        super().__init__()
        self._should_stop = False
    
    def stop(self):
        """Request worker to stop gracefully."""
        self._should_stop = True
    
    def emit_progress(self, current: int, total: int, filename: str = ""):
        """Safely emit progress signal."""
        if not self._should_stop:
            self.progress.emit(current, total, filename)
    
    def emit_finished(self, result=None):
        """Safely emit finished signal."""
        self.finished.emit(result)
    
    def emit_error(self, error_msg: str):
        """Safely emit error signal."""
        self.error.emit(error_msg)
    
    def run(self):
        """Override in subclass to implement worker logic."""
        raise NotImplementedError("Subclass must implement run()")
```

### Example Usage: Simplified WaveformWorker

**Before** (51 lines):
```python
class WaveformWorker(QObject):
    progress = pyqtSignal(int, int, str)
    finished = pyqtSignal(str, list)
    
    def __init__(self, wav_path):
        super().__init__()
        self.wav_path = wav_path
    
    def run(self):
        try:
            with wave.open(str(self.wav_path), 'rb') as wav_file:
                # ... waveform generation logic ...
                self.progress.emit(current, total, filename)
            self.finished.emit(str(self.wav_path), waveform_data)
        except Exception as e:
            logging.error(f"Waveform generation failed: {e}")
            self.finished.emit(str(self.wav_path), [])
```

**After** (30 lines - ~40% reduction):
```python
class WaveformWorker(BaseWorker):
    """Generate waveform data for an audio file."""
    
    def __init__(self, wav_path):
        super().__init__()
        self.wav_path = wav_path
    
    def run(self):
        try:
            waveform_data = self._generate_waveform()
            self.emit_finished((str(self.wav_path), waveform_data))
        except Exception as e:
            self.emit_error(f"Waveform generation failed: {e}")
            self.emit_finished((str(self.wav_path), []))
    
    def _generate_waveform(self):
        """Core waveform generation logic."""
        with wave.open(str(self.wav_path), 'rb') as wav_file:
            # ... waveform generation logic ...
            self.emit_progress(current, total, self.wav_path.name)
        return waveform_data
```

**Benefits**:
- Eliminates duplicate signal definitions
- Standardized error handling
- Easier to add features (e.g., cancellation)
- More consistent API across workers
- Reduced code duplication (~200 lines saved across all workers)

---

## 2. Configuration Manager Pattern

### Problem
QSettings calls scattered throughout code, inconsistent naming, no central documentation of settings keys.

### Solution: Centralized ConfigManager

```python
class ConfigManager:
    """Centralized configuration management using QSettings."""
    
    # Settings keys (documented in one place)
    KEY_GEOMETRY = "geometry"
    KEY_WINDOW_STATE = "windowState"
    KEY_SPLITTER_STATE = "splitterState"
    KEY_RECENT_FOLDERS = "recentFolders"
    KEY_UNDO_LIMIT = "undoLimit"
    KEY_THEME = "theme"
    KEY_PAGINATION_ENABLED = "paginationEnabled"
    KEY_CHUNK_SIZE = "chunkSize"
    KEY_PARALLEL_WORKERS = "parallelWorkers"
    KEY_AUTO_WAVEFORMS = "autoGenerateWaveforms"
    KEY_AUTO_FINGERPRINTS = "autoGenerateFingerprints"
    KEY_NOW_PLAYING_COLLAPSED = "nowPlayingCollapsed"
    
    # Default values
    DEFAULT_UNDO_LIMIT = 100
    DEFAULT_THEME = "light"
    DEFAULT_CHUNK_SIZE = 200
    DEFAULT_PARALLEL_WORKERS = 0  # 0 = auto-detect
    
    def __init__(self, org_name: str = "BandTools", app_name: str = "AudioBrowser"):
        self.settings = QSettings(org_name, app_name)
    
    # Geometry and layout
    def get_geometry(self) -> Optional[bytes]:
        return self.settings.value(self.KEY_GEOMETRY)
    
    def set_geometry(self, geometry: bytes):
        self.settings.setValue(self.KEY_GEOMETRY, geometry)
    
    def get_window_state(self) -> Optional[bytes]:
        return self.settings.value(self.KEY_WINDOW_STATE)
    
    def set_window_state(self, state: bytes):
        self.settings.setValue(self.KEY_WINDOW_STATE, state)
    
    def get_splitter_state(self) -> Optional[bytes]:
        return self.settings.value(self.KEY_SPLITTER_STATE)
    
    def set_splitter_state(self, state: bytes):
        self.settings.setValue(self.KEY_SPLITTER_STATE, state)
    
    # Recent folders
    def get_recent_folders(self) -> List[str]:
        folders = self.settings.value(self.KEY_RECENT_FOLDERS, [])
        return folders if isinstance(folders, list) else []
    
    def add_recent_folder(self, folder_path: str, max_recent: int = 10):
        recent = self.get_recent_folders()
        if folder_path in recent:
            recent.remove(folder_path)
        recent.insert(0, folder_path)
        recent = recent[:max_recent]  # Keep only max_recent items
        self.settings.setValue(self.KEY_RECENT_FOLDERS, recent)
    
    def clear_recent_folders(self):
        self.settings.setValue(self.KEY_RECENT_FOLDERS, [])
    
    # Preferences
    def get_undo_limit(self) -> int:
        return self.settings.value(self.KEY_UNDO_LIMIT, self.DEFAULT_UNDO_LIMIT, type=int)
    
    def set_undo_limit(self, limit: int):
        self.settings.setValue(self.KEY_UNDO_LIMIT, limit)
    
    def get_theme(self) -> str:
        return self.settings.value(self.KEY_THEME, self.DEFAULT_THEME, type=str)
    
    def set_theme(self, theme: str):
        self.settings.setValue(self.KEY_THEME, theme)
    
    def get_pagination_enabled(self) -> bool:
        return self.settings.value(self.KEY_PAGINATION_ENABLED, True, type=bool)
    
    def set_pagination_enabled(self, enabled: bool):
        self.settings.setValue(self.KEY_PAGINATION_ENABLED, enabled)
    
    def get_chunk_size(self) -> int:
        return self.settings.value(self.KEY_CHUNK_SIZE, self.DEFAULT_CHUNK_SIZE, type=int)
    
    def set_chunk_size(self, size: int):
        self.settings.setValue(self.KEY_CHUNK_SIZE, size)
    
    def get_parallel_workers(self) -> int:
        return self.settings.value(self.KEY_PARALLEL_WORKERS, self.DEFAULT_PARALLEL_WORKERS, type=int)
    
    def set_parallel_workers(self, count: int):
        self.settings.setValue(self.KEY_PARALLEL_WORKERS, count)
    
    # Auto-generation settings
    def get_auto_waveforms(self) -> bool:
        return self.settings.value(self.KEY_AUTO_WAVEFORMS, True, type=bool)
    
    def set_auto_waveforms(self, enabled: bool):
        self.settings.setValue(self.KEY_AUTO_WAVEFORMS, enabled)
    
    def get_auto_fingerprints(self) -> bool:
        return self.settings.value(self.KEY_AUTO_FINGERPRINTS, False, type=bool)
    
    def set_auto_fingerprints(self, enabled: bool):
        self.settings.setValue(self.KEY_AUTO_FINGERPRINTS, enabled)
    
    # UI state
    def get_now_playing_collapsed(self) -> bool:
        return self.settings.value(self.KEY_NOW_PLAYING_COLLAPSED, False, type=bool)
    
    def set_now_playing_collapsed(self, collapsed: bool):
        self.settings.setValue(self.KEY_NOW_PLAYING_COLLAPSED, collapsed)
    
    def reset_to_defaults(self):
        """Reset all settings to default values."""
        self.settings.clear()
```

**Usage in AudioBrowser**:

**Before**:
```python
# Scattered throughout the codebase
settings = QSettings("BandTools", "AudioBrowser")
undo_limit = settings.value("undoLimit", 100, type=int)
# ...later...
settings = QSettings("BandTools", "AudioBrowser")
settings.setValue("undoLimit", new_limit)
```

**After**:
```python
# In __init__
self.config = ConfigManager()

# Anywhere in the code
undo_limit = self.config.get_undo_limit()
# ...later...
self.config.set_undo_limit(new_limit)
```

**Benefits**:
- Single source of truth for settings keys
- Type-safe access (no more string key typos)
- Default values documented in one place
- Easier to add new settings
- Better IDE autocomplete support
- Self-documenting code

---

## 3. Method Extraction Examples

### Problem
`AudioBrowser._init_ui()` is ~500 lines, difficult to understand and modify.

### Solution: Extract logical sections into separate methods

**Before** (500+ lines in one method):
```python
def _init_ui(self):
    # 50 lines of file tree setup
    file_tree = QTreeView()
    file_tree.setModel(...)
    # ...
    
    # 100 lines of Library tab setup
    library_tab = QWidget()
    library_layout = QVBoxLayout()
    # ...
    
    # 150 lines of Annotations tab setup
    annotations_tab = QWidget()
    # ...
    
    # 100 lines of Clips tab setup
    clips_tab = QWidget()
    # ...
    
    # 50 lines of Fingerprints tab setup
    fingerprints_tab = QWidget()
    # ...
    
    # 50 lines of menu bar setup
    menu_bar = self.menuBar()
    # ...
```

**After** (50 lines with clear structure):
```python
def _init_ui(self):
    """Initialize the user interface."""
    self._create_menu_bar()
    self._create_toolbar()
    self._create_status_bar()
    self._create_main_layout()
    self._restore_window_state()
    self._setup_keyboard_shortcuts()
    self._connect_signals()

def _create_main_layout(self):
    """Create the main window layout with file tree and tabs."""
    # Main splitter
    self.main_splitter = QSplitter(Qt.Horizontal)
    
    # Left panel: file tree
    left_panel = self._create_file_tree_panel()
    self.main_splitter.addWidget(left_panel)
    
    # Right panel: tabs
    right_panel = self._create_tab_widget()
    self.main_splitter.addWidget(right_panel)
    
    # Set central widget
    self.setCentralWidget(self.main_splitter)

def _create_file_tree_panel(self) -> QWidget:
    """Create the file tree panel with search box."""
    panel = QWidget()
    layout = QVBoxLayout(panel)
    
    # Search box
    self.file_filter = QLineEdit()
    self.file_filter.setPlaceholderText("Filter files...")
    self.file_filter.textChanged.connect(self._on_filter_changed)
    layout.addWidget(self.file_filter)
    
    # Tree view
    self.file_tree = QTreeView()
    self.file_tree.setModel(self.file_model)
    self.file_tree.clicked.connect(self._on_file_clicked)
    layout.addWidget(self.file_tree)
    
    return panel

def _create_tab_widget(self) -> QTabWidget:
    """Create the main tab widget with all tabs."""
    tabs = QTabWidget()
    tabs.addTab(self._create_library_tab(), "Library")
    tabs.addTab(self._create_annotations_tab(), "Annotations")
    tabs.addTab(self._create_clips_tab(), "Clips")
    tabs.addTab(self._create_fingerprints_tab(), "Fingerprints")
    tabs.currentChanged.connect(self._on_tab_changed)
    return tabs

def _create_library_tab(self) -> QWidget:
    """Create the Library tab with file list and controls."""
    # ~50 lines instead of inline in _init_ui
    pass

def _create_annotations_tab(self) -> QWidget:
    """Create the Annotations tab with waveform and table."""
    # ~100 lines instead of inline in _init_ui
    pass

# ... etc for other tabs
```

**Benefits**:
- Each method has single, clear purpose
- Easier to find and modify specific UI sections
- Better testability (can test tab creation independently)
- Improved readability
- Easier to document

---

## 4. UI Component Factory Pattern

### Problem
Repetitive code for creating similar UI elements (buttons, labels, layouts).

### Solution: Factory methods for common patterns

```python
class UIFactory:
    """Factory methods for creating common UI components."""
    
    @staticmethod
    def create_push_button(text: str, icon: Optional[QIcon] = None, 
                          tooltip: Optional[str] = None,
                          callback: Optional[callable] = None) -> QPushButton:
        """Create a configured push button."""
        button = QPushButton(text)
        if icon:
            button.setIcon(icon)
        if tooltip:
            button.setToolTip(tooltip)
        if callback:
            button.clicked.connect(callback)
        return button
    
    @staticmethod
    def create_label(text: str, bold: bool = False, 
                    color: Optional[str] = None) -> QLabel:
        """Create a configured label."""
        label = QLabel(text)
        if bold:
            font = label.font()
            font.setBold(True)
            label.setFont(font)
        if color:
            label.setStyleSheet(f"color: {color};")
        return label
    
    @staticmethod
    def create_hbox_layout(*widgets, spacing: int = 5, 
                          margins: Tuple[int, int, int, int] = (0, 0, 0, 0)) -> QHBoxLayout:
        """Create a horizontal box layout with widgets."""
        layout = QHBoxLayout()
        layout.setSpacing(spacing)
        layout.setContentsMargins(*margins)
        for widget in widgets:
            if widget is None:
                layout.addStretch()
            else:
                layout.addWidget(widget)
        return layout
    
    @staticmethod
    def create_vbox_layout(*widgets, spacing: int = 5,
                          margins: Tuple[int, int, int, int] = (0, 0, 0, 0)) -> QVBoxLayout:
        """Create a vertical box layout with widgets."""
        layout = QVBoxLayout()
        layout.setSpacing(spacing)
        layout.setContentsMargins(*margins)
        for widget in widgets:
            if widget is None:
                layout.addStretch()
            else:
                layout.addWidget(widget)
        return layout
    
    @staticmethod
    def create_form_row(label_text: str, widget: QWidget) -> QHBoxLayout:
        """Create a form row with label and widget."""
        label = QLabel(label_text)
        layout = QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(widget)
        layout.addStretch()
        return layout
    
    @staticmethod
    def create_group_box(title: str, *widgets) -> QGroupBox:
        """Create a group box with vertical layout."""
        group = QGroupBox(title)
        layout = QVBoxLayout()
        for widget in widgets:
            layout.addWidget(widget)
        group.setLayout(layout)
        return group
    
    @staticmethod
    def create_toolbar_separator() -> QWidget:
        """Create a vertical separator for toolbars."""
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        return separator
```

**Usage Example**:

**Before**:
```python
# Repetitive button creation
play_button = QPushButton("Play")
play_button.setIcon(QIcon("play.png"))
play_button.setToolTip("Play audio (Space)")
play_button.clicked.connect(self.play_audio)

pause_button = QPushButton("Pause")
pause_button.setIcon(QIcon("pause.png"))
pause_button.setToolTip("Pause audio (Space)")
pause_button.clicked.connect(self.pause_audio)

stop_button = QPushButton("Stop")
stop_button.setIcon(QIcon("stop.png"))
stop_button.setToolTip("Stop audio")
stop_button.clicked.connect(self.stop_audio)

# Repetitive layout creation
controls_layout = QHBoxLayout()
controls_layout.addWidget(play_button)
controls_layout.addWidget(pause_button)
controls_layout.addWidget(stop_button)
controls_layout.addStretch()
```

**After**:
```python
# Concise button creation
play_button = UIFactory.create_push_button(
    "Play", QIcon("play.png"), "Play audio (Space)", self.play_audio
)
pause_button = UIFactory.create_push_button(
    "Pause", QIcon("pause.png"), "Pause audio (Space)", self.pause_audio
)
stop_button = UIFactory.create_push_button(
    "Stop", QIcon("stop.png"), "Stop audio", self.stop_audio
)

# Concise layout creation
controls_layout = UIFactory.create_hbox_layout(
    play_button, pause_button, stop_button, None  # None adds stretch
)
```

**Benefits**:
- Less boilerplate code
- Consistent UI element styling
- Easier to change styling globally
- More readable code
- Fewer lines

---

## 5. Data Model Classes

### Problem
Direct dictionary manipulation for annotations, clips, etc. No type safety or validation.

### Solution: Typed data classes

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Annotation:
    """Represents a single annotation on an audio file."""
    time: float  # Position in seconds
    text: str  # Annotation text
    important: bool = False
    category: Optional[str] = None  # "timing", "energy", "harmony", "dynamics"
    user: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "time": self.time,
            "text": self.text,
            "important": self.important,
            "category": self.category,
            "user": self.user,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Annotation':
        """Create from dictionary (JSON deserialization)."""
        return cls(
            time=data["time"],
            text=data["text"],
            important=data.get("important", False),
            category=data.get("category"),
            user=data.get("user", ""),
            created_at=data.get("created_at", datetime.now().isoformat())
        )
    
    def __str__(self) -> str:
        important_marker = "⭐ " if self.important else ""
        category_marker = f"[{self.category}] " if self.category else ""
        return f"{important_marker}{category_marker}{self.text} @ {self.time:.2f}s"

@dataclass
class Clip:
    """Represents a clip (time range) in an audio file."""
    start_time: float
    end_time: float
    name: str = ""
    notes: str = ""
    
    @property
    def duration(self) -> float:
        """Calculate clip duration."""
        return self.end_time - self.start_time
    
    def to_dict(self) -> dict:
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "name": self.name,
            "notes": self.notes
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Clip':
        return cls(
            start_time=data["start_time"],
            end_time=data["end_time"],
            name=data.get("name", ""),
            notes=data.get("notes", "")
        )

@dataclass
class AudioFileMetadata:
    """Metadata for a single audio file."""
    filename: str
    song_name: str = ""
    best_take: bool = False
    partial_take: bool = False
    bpm: Optional[int] = None
    duration: Optional[float] = None
    annotations: list[Annotation] = field(default_factory=list)
    clips: list[Clip] = field(default_factory=list)
    
    def add_annotation(self, annotation: Annotation):
        """Add an annotation to this file."""
        self.annotations.append(annotation)
    
    def remove_annotation(self, annotation: Annotation):
        """Remove an annotation from this file."""
        self.annotations.remove(annotation)
    
    def get_important_annotations(self) -> list[Annotation]:
        """Get all important annotations."""
        return [a for a in self.annotations if a.important]
    
    def get_annotations_by_category(self, category: str) -> list[Annotation]:
        """Get annotations filtered by category."""
        return [a for a in self.annotations if a.category == category]
```

**Usage**:

**Before**:
```python
# Direct dictionary manipulation
annotation = {
    "time": 45.5,
    "text": "Off tempo here",
    "important": True,
    "category": "timing",
    "user": "mike"
}

# Access with risk of KeyError
time = annotation["time"]
important = annotation.get("important", False)  # Need to remember default
```

**After**:
```python
# Type-safe object
annotation = Annotation(
    time=45.5,
    text="Off tempo here",
    important=True,
    category="timing",
    user="mike"
)

# IDE autocomplete and type checking
time = annotation.time  # Type is float
important = annotation.important  # Type is bool
```

**Benefits**:
- Type safety (IDE catches errors)
- Autocomplete support
- Validation at creation time
- Self-documenting code
- Easier to add methods (business logic)
- Better error messages

---

## 6. JSON Persistence Utility

### Problem
Repeated JSON loading/saving patterns throughout code.

### Solution: Reusable persistence utility

```python
import json
from pathlib import Path
from typing import Optional, Any, Callable
import logging

class JSONPersistence:
    """Utility for loading and saving JSON files with error handling."""
    
    @staticmethod
    def load_json(file_path: Path, default: Any = None) -> Any:
        """Load JSON file with error handling."""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in {file_path}: {e}")
        except Exception as e:
            logging.error(f"Failed to load {file_path}: {e}")
        return default
    
    @staticmethod
    def save_json(file_path: Path, data: Any, indent: int = 2, 
                  create_backup: bool = False) -> bool:
        """Save data to JSON file with error handling."""
        try:
            # Create backup if requested
            if create_backup and file_path.exists():
                backup_path = file_path.with_suffix(file_path.suffix + '.bak')
                import shutil
                shutil.copy2(file_path, backup_path)
            
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write JSON
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            return True
        except Exception as e:
            logging.error(f"Failed to save {file_path}: {e}")
            return False
    
    @staticmethod
    def load_with_migration(file_path: Path, default: Any,
                           migrator: Optional[Callable] = None) -> Any:
        """Load JSON with optional data migration."""
        data = JSONPersistence.load_json(file_path, default)
        if migrator and data != default:
            try:
                data = migrator(data)
            except Exception as e:
                logging.error(f"Failed to migrate {file_path}: {e}")
                return default
        return data
```

**Usage**:

**Before**:
```python
# Repeated throughout codebase
def _load_provided_names(self):
    json_path = self.current_folder / ".provided_names.json"
    try:
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                self.provided_names = json.load(f)
        else:
            self.provided_names = {}
    except Exception as e:
        logging.error(f"Failed to load provided names: {e}")
        self.provided_names = {}

def _save_provided_names(self):
    json_path = self.current_folder / ".provided_names.json"
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.provided_names, f, indent=2)
    except Exception as e:
        logging.error(f"Failed to save provided names: {e}")
```

**After**:
```python
def _load_provided_names(self):
    json_path = self.current_folder / ".provided_names.json"
    self.provided_names = JSONPersistence.load_json(json_path, default={})

def _save_provided_names(self):
    json_path = self.current_folder / ".provided_names.json"
    JSONPersistence.save_json(json_path, self.provided_names, create_backup=True)
```

**Benefits**:
- Consistent error handling
- Less boilerplate code
- Automatic backup support
- Easier to add features (compression, encryption)
- ~150 lines saved across all JSON operations

---

## 7. Progress Dialog Consolidation

### Problem
Similar progress dialog patterns for multiple operations (convert, mono, boost, etc.).

### Solution: Reusable progress dialog

```python
class ProgressDialog(QDialog):
    """Reusable progress dialog for long-running operations."""
    
    cancelled = pyqtSignal()
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(400)
        
        # UI setup
        layout = QVBoxLayout(self)
        
        # Operation label
        self.operation_label = QLabel("")
        layout.addWidget(self.operation_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)
        
        # File label
        self.file_label = QLabel("")
        self.file_label.setWordWrap(True)
        layout.addWidget(self.file_label)
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.on_cancel)
        layout.addWidget(self.cancel_button)
    
    def update_progress(self, current: int, total: int, filename: str = ""):
        """Update progress display."""
        percentage = int((current / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(percentage)
        self.operation_label.setText(f"Processing {current} of {total} files...")
        if filename:
            self.file_label.setText(f"Current file: {filename}")
        QApplication.processEvents()  # Keep UI responsive
    
    def set_operation(self, operation: str):
        """Set the operation description."""
        self.operation_label.setText(operation)
    
    def on_cancel(self):
        """Handle cancel button click."""
        self.cancel_button.setEnabled(False)
        self.cancel_button.setText("Cancelling...")
        self.cancelled.emit()
    
    def finish(self):
        """Close dialog when operation completes."""
        self.accept()
```

**Usage**:

**Before**:
```python
# Custom dialog for each operation
progress_dialog = QProgressDialog("Converting WAV to MP3...", "Cancel", 0, len(wav_files), self)
progress_dialog.setWindowModality(Qt.WindowModal)
for i, file in enumerate(wav_files):
    if progress_dialog.wasCanceled():
        break
    progress_dialog.setValue(i)
    progress_dialog.setLabelText(f"Converting {file.name}...")
    # ... conversion logic ...
progress_dialog.setValue(len(wav_files))
```

**After**:
```python
# Reusable dialog
progress = ProgressDialog("WAV to MP3 Conversion", self)
progress.cancelled.connect(worker.stop)  # Connect to worker's stop method
progress.show()

# Worker emits progress signal
worker.progress.connect(progress.update_progress)
worker.finished.connect(progress.finish)
```

**Benefits**:
- Consistent progress dialog appearance
- Less duplicate code (~100 lines saved)
- Easier to add features (time remaining, speed, etc.)
- Better cancellation handling

---

## 8. Before/After Comparison

### Summary of Code Reduction

| Area | Before (lines) | After (lines) | Savings | Notes |
|------|---------------|---------------|---------|-------|
| Worker Classes | ~400 | ~250 | 150 | Base class consolidation |
| QSettings Calls | ~200 | ~50 | 150 | ConfigManager centralization |
| _init_ui() Method | ~500 | ~100 | 400 | Method extraction |
| UI Component Creation | ~300 | ~150 | 150 | Factory pattern |
| JSON Operations | ~200 | ~50 | 150 | JSONPersistence utility |
| Progress Dialogs | ~150 | ~50 | 100 | Reusable ProgressDialog |
| **Total** | **~1,750** | **~650** | **~1,100** | **63% reduction** |

### Maintainability Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Longest method | 500 lines | 100 lines | 80% smaller |
| Duplicate code patterns | 8 similar workers | 1 base + 8 subclasses | Eliminated |
| Settings access | Scattered, inconsistent | Centralized, typed | ✓ |
| Type safety | Dictionary access | Typed classes | ✓ |
| Testability | Difficult (UI coupled) | Easy (logic extracted) | ✓ |

---

## Conclusion

These simplification patterns demonstrate practical ways to improve the AudioBrowser codebase:

1. **Worker Base Class**: Eliminates duplicate worker code (~150 lines saved)
2. **Config Manager**: Centralizes settings management (~150 lines saved)
3. **Method Extraction**: Makes long methods manageable (~400 lines saved)
4. **UI Factory**: Reduces UI boilerplate (~150 lines saved)
5. **Data Models**: Adds type safety and validation
6. **JSON Utility**: Consolidates persistence (~150 lines saved)
7. **Progress Dialog**: Reuses progress UI (~100 lines saved)

**Total Potential Savings**: ~1,100 lines (7% of total codebase)

**Additional Benefits**:
- Better code organization
- Improved testability
- Enhanced maintainability
- Reduced cognitive load
- Easier onboarding for new developers
- Preparation for QML migration

These patterns can be applied incrementally without disrupting existing functionality, making them ideal candidates for immediate implementation.

---

## Document Metadata

**Created**: 2025-10-06  
**Author**: Copilot SWE Agent  
**Version**: 1.0  
**Related Documents**:
- [CURRENT_ARCHITECTURE_INVENTORY.md](CURRENT_ARCHITECTURE_INVENTORY.md)
- [QML_MIGRATION_STRATEGY.md](QML_MIGRATION_STRATEGY.md)
- [INTERFACE_IMPROVEMENT_IDEAS.md](INTERFACE_IMPROVEMENT_IDEAS.md)
