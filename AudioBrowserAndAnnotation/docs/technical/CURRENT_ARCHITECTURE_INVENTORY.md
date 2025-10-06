# AudioBrowser Current Architecture Inventory

## Overview

This document provides a comprehensive inventory of the current AudioBrowser architecture, cataloging all components, classes, features, and data structures. This serves as a baseline for understanding the application and planning future refactoring or migration efforts.

**Application**: AudioBrowser (Audio Annotation and Practice Management Tool)  
**File**: `audio_browser.py`  
**Lines of Code**: 15,360  
**Architecture**: Monolithic PyQt6 Widgets application  
**Language**: Python 3.x

---

## Table of Contents

1. [Class Inventory](#class-inventory)
2. [Feature Catalog](#feature-catalog)
3. [UI Components](#ui-components)
4. [Data Structures](#data-structures)
5. [Threading Model](#threading-model)
6. [Integration Points](#integration-points)
7. [Code Metrics](#code-metrics)
8. [Simplification Opportunities](#simplification-opportunities)

---

## Class Inventory

### UI Widget Classes (9 classes)

#### 1. BestTakeIndicatorWidget (67 lines)
- **Purpose**: Visual indicator showing "Best Take" status
- **Location**: Lines 327-393
- **Dependencies**: QWidget, QPainter, ColorManager
- **Features**:
  - Gold star icon with gradient
  - Tooltip: "Best Take"
  - Fixed size: 24×24 pixels
- **Reusability**: High - standalone widget

#### 2. PartialTakeIndicatorWidget (227 lines)
- **Purpose**: Visual indicator showing "Partial Take" status
- **Location**: Lines 393-620
- **Dependencies**: QWidget, QPainter, ColorManager
- **Features**:
  - Half-filled star icon
  - Tooltip: "Partial Take"
  - Fixed size: 24×24 pixels
- **Reusability**: High - standalone widget

#### 3. SeekSlider (1,426 lines)
- **Purpose**: Custom slider with click-to-seek, marker display
- **Location**: Lines 776-2202
- **Dependencies**: QSlider, QPainter, ColorManager
- **Features**:
  - Click anywhere to seek
  - Displays annotation markers
  - Loop markers (orange triangles)
  - Tempo markers (vertical lines)
  - Hover tooltips showing markers
  - Mouse press/release events
- **Complexity**: High - 1,400+ lines
- **Refactoring Opportunity**: Could split into multiple classes

#### 4. WaveformView (844 lines)
- **Purpose**: Main waveform display and interaction
- **Location**: Lines 2915-3759
- **Dependencies**: QWidget, QPainter, QPixmap, ColorManager
- **Features**:
  - Waveform rendering (stereo or mono)
  - Zoom controls (1×, 2×, 4×, 8×, 16×)
  - Annotation markers (draggable)
  - Loop markers (draggable)
  - Tempo markers (measure numbers)
  - Spectrogram overlay
  - Click-to-seek
  - Mouse hover tooltips
  - Marker selection
  - Context menu
- **Complexity**: Very High - 844 lines
- **Refactoring Opportunity**: Could split into renderer, interaction handler, marker manager

#### 5. MiniWaveformWidget (105 lines)
- **Purpose**: Compact waveform for Now Playing panel
- **Location**: Lines 3759-3864
- **Dependencies**: QWidget, QPainter
- **Features**:
  - Simplified waveform rendering
  - Fits in compact space
  - No interaction (display only)
- **Reusability**: High - standalone widget

#### 6. NowPlayingPanel (196 lines)
- **Purpose**: Persistent playback controls accessible from any tab
- **Location**: Lines 3864-4060
- **Dependencies**: QWidget, QLabel, QPushButton, QSlider
- **Features**:
  - Current file display
  - Play/Pause/Stop buttons
  - Seek slider
  - Time display (current/total)
  - Volume control
  - Quick annotation entry
  - Collapsible with toggle button
  - State persists across sessions
- **Reusability**: High - self-contained panel

#### 7. ClickableLabel (30 lines)
- **Purpose**: QLabel that emits clicked signal
- **Location**: Lines 4060-4090
- **Dependencies**: QLabel
- **Features**:
  - Emits clicked() signal on mouse press
  - Used for clickable status bar elements
- **Reusability**: High - generic utility widget

#### 8. BackupSelectionDialog (100 lines)
- **Purpose**: Dialog for selecting backup to restore
- **Location**: Lines 4268-4368
- **Dependencies**: QMessageBox, QListWidget
- **Features**:
  - Lists available backups
  - Shows backup dates
  - Allows selection of target folder
  - Confirms before restoring
- **Reusability**: Medium - specific to backup system

#### 9. AudioBrowser (11,000+ lines)
- **Purpose**: Main application window
- **Location**: Lines 4584-15360
- **Dependencies**: QMainWindow, all other classes, PyQt6.QtMultimedia
- **Features**: See "Feature Catalog" section below
- **Complexity**: Extreme - 11,000+ lines
- **Refactoring Opportunity**: **Primary candidate for refactoring**

### Dialog Classes (2 classes)

#### 10. AutoGenerationSettingsDialog (128 lines)
- **Purpose**: Configure automatic waveform/fingerprint generation
- **Location**: Lines 4368-4496
- **Dependencies**: QDialog, QCheckBox
- **Features**:
  - Enable/disable auto waveform generation
  - Enable/disable auto fingerprint generation
  - Save preferences to QSettings
- **Reusability**: Medium - specific to this app

#### 11. PreferencesDialog (88 lines)
- **Purpose**: Application preferences configuration
- **Location**: Lines 4496-4584
- **Dependencies**: QDialog, QSpinBox, QComboBox, QCheckBox
- **Features**:
  - Undo limit setting (10-1000)
  - Theme selection (Light/Dark)
  - Pagination enable/disable
  - Chunk size (50-1000)
  - Parallel workers (0-16)
  - Save to QSettings
- **Reusability**: Medium - could be generalized

### Backend Worker Classes (8 classes)

#### 12. WaveformWorker (51 lines)
- **Purpose**: Generate waveform for single file
- **Location**: Lines 2206-2257
- **Dependencies**: QObject, wave module
- **Threading**: Runs in QThread
- **Signals**: `progress(int, int, str)`, `finished(str, list)`

#### 13. ConvertWorker (40 lines)
- **Purpose**: Convert WAV to MP3 using ffmpeg
- **Location**: Lines 2257-2297
- **Dependencies**: QObject, subprocess (ffmpeg)
- **Threading**: Runs in QThread
- **Signals**: `progress(int, int, str)`, `finished()`

#### 14. MonoConvertWorker (82 lines)
- **Purpose**: Convert stereo to mono
- **Location**: Lines 2297-2379
- **Dependencies**: QObject, wave, audioop
- **Threading**: Runs in QThread
- **Signals**: `progress(int, int, str)`, `finished()`

#### 15. VolumeBoostWorker (62 lines)
- **Purpose**: Export audio with volume boost
- **Location**: Lines 2379-2441
- **Dependencies**: QObject, wave, audioop, subprocess (ffmpeg)
- **Threading**: Runs in QThread
- **Signals**: `progress(int, int, str)`, `finished()`

#### 16. ChannelMutingWorker (48 lines)
- **Purpose**: Export audio with channels muted
- **Location**: Lines 2441-2489
- **Dependencies**: QObject, wave, audioop
- **Threading**: Runs in QThread
- **Signals**: `progress(int, int, str)`, `finished()`

#### 17. FingerprintWorker (80 lines)
- **Purpose**: Generate audio fingerprint
- **Location**: Lines 2489-2569
- **Dependencies**: QObject, wave, numpy, hashlib
- **Threading**: Runs in QThread
- **Signals**: `progress(int, int, str)`, `finished(str, str, int)`

#### 18. AutoWaveformWorker (172 lines)
- **Purpose**: Coordinate automatic waveform generation for multiple files
- **Location**: Lines 2654-2831
- **Dependencies**: QObject, QThreadPool
- **Threading**: Coordinator (main thread), spawns WaveformGenerationTask
- **Signals**: `progress(int, int, str)`, `finished()`

#### 19. AutoFingerprintWorker (84 lines)
- **Purpose**: Coordinate automatic fingerprint generation
- **Location**: Lines 2831-2915
- **Dependencies**: QObject
- **Threading**: Spawns FingerprintWorker threads
- **Signals**: `progress(int, int, str)`, `finished()`

### Support Classes (3 classes)

#### 20. ColorManager (156 lines)
- **Purpose**: Centralized color and theme management
- **Location**: Lines 620-776
- **Dependencies**: None (pure Python)
- **Features**:
  - Light and dark theme palettes
  - UI colors (background, text, borders)
  - Waveform colors (waveform, markers, grid)
  - User assignment colors
  - Theme switching
  - Color caching
- **Reusability**: High - could be used in other Qt apps

#### 21. FileInfoProxyModel (178 lines)
- **Purpose**: Filter and sort file tree
- **Location**: Lines 4090-4268
- **Dependencies**: QSortFilterProxyModel, QFileSystemModel
- **Features**:
  - Filter by file name (fuzzy matching)
  - Show only audio files (.wav, .mp3)
  - Custom sorting
- **Reusability**: High - generic file filtering

#### 22. WaveformGenerationTask (85 lines)
- **Purpose**: Single waveform generation task (for thread pool)
- **Location**: Lines 2569-2654
- **Dependencies**: QRunnable, wave
- **Threading**: Runs in QThreadPool
- **Signals**: Via callback function

---

## Feature Catalog

### Core Features

#### Audio Playback
- Play, pause, stop, seek
- Volume control
- Looping (A-B repeat)
- Keyboard shortcuts (Space, arrows)
- QMediaPlayer integration

#### File Management
- Browse folder hierarchy
- Filter by name (fuzzy search)
- Show only audio files (.wav, .mp3)
- Display file info (size, duration, date)
- Recent folders menu (up to 10)

#### Library Tab
- File list with metadata
- Editable "Provided Name" column
- Duration column (cached)
- Best Take indicator
- Partial Take indicator
- BPM/Tempo column
- Right-click context menu
- Sorting by columns
- Pagination (500+ files)

#### Annotations
- Create annotations at timestamp
- Edit annotation text
- Mark as "Important"
- Categorize (Timing, Energy, Harmony, Dynamics)
- Delete annotations
- Multi-user support (separate files per user)
- Merged view (all users' annotations)
- Export to text file
- Folder notes (overall comments)

#### Waveform Display
- Stereo or mono visualization
- Zoom levels (1×, 2×, 4×, 8×, 16×)
- Annotation markers (draggable)
- Loop markers (A/B points)
- Tempo markers (measure lines)
- Click-to-seek
- Spectrogram overlay (60-8000 Hz)
- Auto-generate in background
- Cache waveforms for performance

#### Clips
- Define clip start/end
- Export clip as separate file
- Clip metadata and notes

#### Audio Fingerprinting
- Generate audio fingerprints
- Match songs across folders
- Detect duplicates
- Auto-generate in background

#### Batch Operations
- Batch rename (##_ProvidedName format)
- Convert WAV→MP3 (delete originals)
- Convert stereo→mono
- Export with volume boost
- Mute channels during export

#### Backup System
- Automatic backups before modifications
- Timestamped backup folders (.backup/YYYY-MM-DD-###/)
- Restore from backup dialog
- Preview before restoring

#### Google Drive Sync
- Manual sync trigger
- Upload/download audio files
- Upload/download metadata
- Version tracking
- Conflict resolution
- Sync history viewer
- Sync rules configuration
- Multi-user annotation sync

#### Practice Features
- Practice statistics (song frequency, session counts)
- Practice goals (time, sessions, per-song)
- Setlist builder (create, edit, export, practice mode)
- Tempo/BPM tracking
- Best Take tracking

#### UI Enhancements
- Dark mode theme
- Recent folders
- Preferences dialog
- Workspace layouts (save/restore window size and splitter positions)
- Status bar progress indicators
- Now Playing panel (collapsible, persistent)
- Keyboard shortcuts (30+)
- Context menus
- Toolbar
- Documentation browser (in-app)

#### Settings and Persistence
- QSettings for preferences
- JSON files for metadata
- Backup system
- Recent folders history
- Workspace layout

---

## UI Components

### Main Window Structure

```
AudioBrowser (QMainWindow)
├── Menu Bar
│   ├── File Menu
│   │   ├── Change Band Practice Folder
│   │   ├── Recent Folders (submenu)
│   │   ├── Batch Rename
│   │   ├── Export Annotations
│   │   ├── Convert WAV→MP3
│   │   ├── Convert to Mono
│   │   ├── Export with Volume Boost
│   │   ├── Auto-Generation Settings
│   │   ├── Preferences
│   │   ├── Restore from Backup
│   │   ├── Sync with Google Drive
│   │   └── Delete Remote Folder from Google Drive
│   ├── Edit Menu
│   │   ├── Undo (Ctrl+Z)
│   │   └── Redo (Ctrl+Y)
│   ├── View Menu
│   │   ├── Save Workspace Layout (Ctrl+Shift+L)
│   │   ├── Restore Workspace Layout (Ctrl+Shift+R)
│   │   └── Reset Workspace Layout
│   ├── Tools Menu
│   │   └── Setlist Builder (Ctrl+Shift+T)
│   └── Help Menu
│       ├── Keyboard Shortcuts (Ctrl+H)
│       ├── Documentation Browser (Ctrl+Shift+H)
│       ├── Practice Statistics (Ctrl+Shift+S)
│       ├── Practice Goals (Ctrl+Shift+G)
│       ├── Changelog
│       └── About
├── Toolbar
│   ├── Undo Button
│   ├── Redo Button
│   ├── Up Button (parent folder)
│   ├── Auto-switch Checkbox
│   └── Sync Button
├── Status Bar
│   ├── Clickable status labels
│   ├── Progress bar (when operations running)
│   └── Progress label (operation details)
├── Main Splitter (horizontal)
│   ├── Left Panel: File Tree
│   │   ├── Filter Box (search)
│   │   └── QTreeView (file hierarchy)
│   └── Right Panel: Tab Widget
│       ├── Tab 1: Library
│       │   ├── Toolbar (Show Best/Partial Take filters)
│       │   ├── QTableWidget (file list with metadata)
│       │   └── Pagination controls (Previous/Next)
│       ├── Tab 2: Annotations
│       │   ├── Controls
│       │   │   ├── User selector (QComboBox)
│       │   │   ├── Merged view toggle
│       │   │   ├── Waveform controls (zoom, spectrogram)
│       │   │   └── Playback controls
│       │   ├── WaveformView (custom widget)
│       │   ├── SeekSlider (custom widget)
│       │   ├── Annotations Table (QTableWidget)
│       │   │   └── Columns: Time, Text, Important, Category, User
│       │   └── Folder Notes (QTextEdit)
│       ├── Tab 3: Clips
│       │   ├── Clip controls
│       │   ├── WaveformView (custom widget)
│       │   ├── SeekSlider (custom widget)
│       │   └── Clips Table (QTableWidget)
│       └── Tab 4: Fingerprints
│           ├── Generate button
│           ├── Match across folders button
│           └── Results table (QTableWidget)
└── Now Playing Panel (optional, collapsible)
    ├── File label
    ├── Play/Pause/Stop buttons
    ├── Seek slider
    ├── Time display
    ├── Volume slider
    └── Quick annotation entry
```

### Dialogs

1. **PreferencesDialog**: Undo limit, theme, pagination, performance
2. **AutoGenerationSettingsDialog**: Auto waveform/fingerprint settings
3. **BackupSelectionDialog**: Select backup to restore
4. **Setlist Builder Dialog**: 3 tabs (Manage, Practice, Export)
5. **Practice Goals Dialog**: Set and track practice goals
6. **Practice Statistics Dialog**: View practice analytics
7. **Sync Dialog**: Google Drive sync interface
8. **Conflict Resolution Dialog**: Resolve sync conflicts
9. **Sync History Dialog**: View sync operation history
10. **Sync Rules Dialog**: Configure sync rules
11. **Documentation Browser**: Browse in-app documentation
12. **Export Best Takes Dialog**: Export best takes package
13. **Batch Rename Confirmation**: Confirm batch rename
14. **Export Annotations Dialog**: Choose export format
15. **Fingerprint Progress Dialog**: Fingerprinting progress

---

## Data Structures

### JSON Files (per practice folder)

#### 1. `.audio_notes_<username>.json`
```json
{
  "filename.wav": {
    "song_name": "Song Title",
    "notes": [
      {
        "time": 45.5,
        "text": "Off tempo here",
        "important": true,
        "category": "timing",
        "user": "username"
      }
    ],
    "clips": [
      {
        "start_time": 30.0,
        "end_time": 60.0,
        "name": "Bridge section",
        "notes": "Good harmonies"
      }
    ]
  },
  "folder_notes": "Overall practice notes"
}
```

#### 2. `.provided_names.json`
```json
{
  "filename.wav": "Song Title"
}
```

#### 3. `.duration_cache.json`
```json
{
  "filename.wav": 185.5
}
```

#### 4. `.audio_fingerprints.json`
```json
{
  "filename.wav": {
    "fingerprint": "abcd1234efgh5678...",
    "duration": 185
  }
}
```

#### 5. `.user_colors.json`
```json
{
  "username1": "#FF5733",
  "username2": "#33C1FF"
}
```

#### 6. `.tempo.json`
```json
{
  "filename.wav": {
    "bpm": 120,
    "time_signature": "4/4"
  }
}
```

#### 7. `.practice_goals.json`
```json
{
  "goals": [
    {
      "id": "uuid-1234",
      "type": "time",
      "target": 600,
      "current": 320,
      "deadline": "2025-12-31",
      "description": "Practice 10 hours this month"
    }
  ]
}
```

#### 8. `.setlists.json`
```json
{
  "setlists": [
    {
      "name": "January Gig",
      "songs": [
        {"folder": "2025-01-05", "file": "song1.wav"},
        {"folder": "2025-01-12", "file": "song2.wav"}
      ],
      "notes": "Key changes: Song 1 to D, Song 2 to A"
    }
  ]
}
```

#### 9. `.sync_history.json`
```json
{
  "operations": [
    {
      "timestamp": "2025-01-15T14:30:00",
      "operation": "upload",
      "files": 5,
      "user": "username"
    }
  ]
}
```

#### 10. `.sync_rules.json`
```json
{
  "max_file_size_mb": 100,
  "annotations_only": false,
  "sync_audio": true,
  "auto_download": false
}
```

### QSettings Keys

- `geometry` - Window geometry
- `windowState` - Window state (maximized, etc.)
- `splitterState` - Main splitter state
- `recentFolders` - List of recent folders
- `undoLimit` - Undo operation limit
- `theme` - UI theme (light/dark)
- `paginationEnabled` - Pagination on/off
- `chunkSize` - Files per page
- `parallelWorkers` - Worker thread count
- `autoWaveforms` - Auto-generate waveforms
- `autoFingerprints` - Auto-generate fingerprints
- `nowPlayingCollapsed` - Now Playing panel state

---

## Threading Model

### Main Thread
- UI updates
- User interaction
- Playback control
- File system operations (quick)

### Background Threads

1. **WaveformWorker** (QThread)
   - Generate waveform for single file
   - Emits progress and finished signals

2. **AutoWaveformWorker** (QObject + QThreadPool)
   - Coordinates multiple waveform generations
   - Spawns WaveformGenerationTask (QRunnable) in thread pool
   - Uses CPU core count for parallelism

3. **FingerprintWorker** (QThread)
   - Generate fingerprint for single file
   - Emits progress and finished signals

4. **AutoFingerprintWorker** (QObject)
   - Coordinates multiple fingerprint generations
   - Spawns FingerprintWorker threads

5. **ConvertWorker** (QThread)
   - WAV→MP3 conversion using ffmpeg
   - One file at a time

6. **MonoConvertWorker** (QThread)
   - Stereo→Mono conversion
   - Processes audio data

7. **VolumeBoostWorker** (QThread)
   - Export with volume boost
   - Processes audio data and calls ffmpeg

8. **ChannelMutingWorker** (QThread)
   - Mute audio channels
   - Processes audio data

### Thread Safety
- All workers emit signals to main thread
- No direct UI updates from worker threads
- Data passed via signals (immutable or copied)
- File operations use locks where needed

---

## Integration Points

### External Dependencies

1. **PyQt6** - GUI framework
2. **ffmpeg** - Audio conversion (WAV↔MP3)
3. **Google Drive API** - Cloud synchronization (optional)
4. **Python Standard Library**:
   - `wave` - Audio file reading
   - `audioop` - Audio processing
   - `json` - Data persistence
   - `pathlib` - File system operations
   - `hashlib` - Fingerprinting
   - `subprocess` - ffmpeg integration

### External Files
- `credentials.json` - Google Drive OAuth credentials (optional)
- `.token.json` - Google Drive auth token (auto-generated, optional)

### External Services
- **Google Drive API** - Synchronization (optional)

---

## Code Metrics

### File Statistics
- **Total Lines**: 15,360
- **Classes**: 22
- **Main Class (AudioBrowser)**: ~11,000 lines
- **Other Classes**: ~4,000 lines
- **Module-level Code**: ~360 lines

### Class Size Distribution

| Size Category | Line Count | Classes |
|---------------|------------|---------|
| Small (< 100 lines) | 30-100 | 8 classes |
| Medium (100-500 lines) | 100-500 | 8 classes |
| Large (500-1000 lines) | 500-1000 | 4 classes |
| Very Large (1000+ lines) | 1,400+ | 1 class (SeekSlider) |
| Extreme (10000+ lines) | 11,000+ | 1 class (AudioBrowser) |

### Complexity Indicators

**High Complexity Areas**:
1. **AudioBrowser._init_ui()** - ~500 lines
2. **AudioBrowser.playback and file management** - ~2,000 lines
3. **AudioBrowser.annotation management** - ~1,500 lines
4. **SeekSlider** - 1,400+ lines
5. **WaveformView** - 844 lines

**Moderate Complexity Areas**:
1. **Worker classes** - 40-172 lines each
2. **ColorManager** - 156 lines
3. **NowPlayingPanel** - 196 lines

**Low Complexity Areas**:
1. **Indicator widgets** - 30-67 lines
2. **Dialog classes** - 88-128 lines

---

## Simplification Opportunities

### 1. AudioBrowser Class Decomposition

**Current**: 11,000+ line monolithic class  
**Opportunity**: Split into specialized classes

**Proposed Decomposition**:

```
AudioBrowser (Main Window)
├── AudioEngine (Playback)
├── FileManager (File operations)
├── AnnotationManager (Annotations CRUD)
├── WaveformManager (Waveform operations)
├── FingerprintManager (Fingerprinting)
├── SyncManager (Google Drive sync)
├── BackupManager (Backup/restore)
├── PracticeManager (Stats, goals, setlists)
└── UIManager (UI state, preferences)
```

**Benefits**:
- Easier to understand and maintain
- Better testability
- Clear separation of concerns
- Easier to modify individual components

**Effort**: High (requires significant refactoring)

### 2. SeekSlider Simplification

**Current**: 1,400+ lines with marker display, interaction, and painting  
**Opportunity**: Split responsibilities

**Proposed Split**:
- `SeekSlider` - Basic slider with click-to-seek (200 lines)
- `MarkerRenderer` - Draw markers on slider (300 lines)
- `MarkerInteraction` - Handle marker dragging (200 lines)
- `MarkerTooltip` - Hover tooltips (100 lines)

**Benefits**:
- Each class has single responsibility
- Easier to test and debug
- More reusable components

**Effort**: Medium

### 3. WaveformView Simplification

**Current**: 844 lines with rendering, interaction, and state  
**Opportunity**: Split into renderer and controller

**Proposed Split**:
- `WaveformRenderer` - Pure rendering logic (400 lines)
- `WaveformController` - User interaction and state (300 lines)
- `MarkerManager` - Marker positioning and dragging (144 lines)

**Benefits**:
- Clearer separation
- Easier to test rendering independently
- Could reuse renderer in other contexts

**Effort**: Medium

### 4. Duplicate Code Consolidation

**Identified Duplications**:

1. **Worker Pattern**: 8 worker classes with similar structure
   - **Opportunity**: Create base `Worker` class with common functionality
   - **Savings**: ~200 lines of duplicate code

2. **Progress Dialog**: Similar patterns across multiple operations
   - **Opportunity**: Create reusable `ProgressDialog` class
   - **Savings**: ~100 lines

3. **JSON Loading/Saving**: Repeated patterns
   - **Opportunity**: Create `JSONPersistence` utility class
   - **Savings**: ~150 lines

4. **Table Population**: Similar code for populating tables
   - **Opportunity**: Create `TablePopulator` utility class
   - **Savings**: ~200 lines

**Total Savings**: ~650 lines

### 5. Method Extraction

**Long Methods in AudioBrowser**:
- `_init_ui()` - 500+ lines → Extract tab creation methods
- `_populate_library_table()` - 300+ lines → Extract row creation
- `_create_setlist_builder_dialog()` - 500+ lines → Extract tab creation

**Opportunity**: Break long methods into smaller, focused methods  
**Benefits**: Easier to read, test, and maintain  
**Effort**: Low (relatively safe refactoring)

### 6. Configuration Management

**Current**: Scattered QSettings calls and JSON files  
**Opportunity**: Centralized `ConfigManager` class

**Proposed**:
```python
class ConfigManager:
    def __init__(self):
        self.settings = QSettings(...)
    
    def get_theme(self): ...
    def set_theme(self, theme): ...
    def get_undo_limit(self): ...
    # etc.
```

**Benefits**:
- Single source of truth
- Easier to add/modify settings
- Better testability

**Effort**: Low-Medium

### 7. Signal/Slot Consolidation

**Current**: Many similar signal connections scattered throughout  
**Opportunity**: Group related connections, use naming conventions

**Benefits**:
- Easier to trace signal flow
- Reduced cognitive load

**Effort**: Low

### 8. UI Component Reuse

**Current**: Some UI patterns repeated (buttons, labels, layouts)  
**Opportunity**: Create reusable UI component factory methods

**Example**:
```python
def create_action_button(text, icon, callback):
    button = QPushButton(text)
    button.setIcon(icon)
    button.clicked.connect(callback)
    return button
```

**Benefits**:
- Consistent UI appearance
- Less boilerplate code

**Effort**: Low

### 9. Data Model Abstraction

**Current**: Direct JSON manipulation throughout code  
**Opportunity**: Create data model classes

**Proposed**:
```python
class Annotation:
    def __init__(self, time, text, important=False, category=None):
        self.time = time
        self.text = text
        self.important = important
        self.category = category
    
    def to_dict(self): ...
    @classmethod
    def from_dict(cls, data): ...
```

**Benefits**:
- Type safety
- Easier to validate data
- Better IDE support

**Effort**: Medium

### 10. Testing Infrastructure

**Current**: No automated tests  
**Opportunity**: Add unit tests for backend logic

**Priority Areas**:
1. ColorManager - Pure functions, easy to test
2. Worker classes - Test core logic without UI
3. Data persistence - Test JSON loading/saving
4. Annotation CRUD - Test business logic

**Benefits**:
- Catch regressions early
- Document expected behavior
- Enable confident refactoring

**Effort**: High (but valuable)

---

## Prioritized Simplification Plan

### Phase 1: Low-Hanging Fruit (1 week)
- [ ] Extract long methods into smaller methods
- [ ] Create configuration manager
- [ ] Consolidate duplicate worker code into base class
- [ ] Create reusable UI component factory methods

**Impact**: Medium  
**Effort**: Low  
**Risk**: Low

### Phase 2: Component Extraction (2 weeks)
- [ ] Split SeekSlider into multiple classes
- [ ] Split WaveformView into renderer and controller
- [ ] Create data model classes (Annotation, Clip, etc.)
- [ ] Create JSON persistence utility class

**Impact**: High  
**Effort**: Medium  
**Risk**: Medium

### Phase 3: Architecture Refactoring (4 weeks)
- [ ] Decompose AudioBrowser into specialized manager classes
- [ ] Create proper service layer
- [ ] Implement dependency injection
- [ ] Add comprehensive tests

**Impact**: Very High  
**Effort**: High  
**Risk**: High

### Phase 4: QML Migration (8-12 weeks)
- [ ] See QML_MIGRATION_STRATEGY.md

**Impact**: Very High  
**Effort**: Very High  
**Risk**: High

---

## Conclusion

The AudioBrowser application is a feature-rich, monolithic PyQt6 Widgets application with significant complexity concentrated in a few classes (especially `AudioBrowser` and `SeekSlider`). 

**Key Findings**:
1. **22 classes**, mostly well-structured except main class
2. **11,000-line main class** is primary refactoring target
3. **Multiple simplification opportunities** with varying effort/impact
4. **Strong foundation** for QML migration after refactoring

**Recommendations**:
1. **Short-term**: Apply Phase 1 simplifications (quick wins)
2. **Medium-term**: Extract components (Phase 2)
3. **Long-term**: Full architectural refactoring (Phase 3) or QML migration (Phase 4)

---

## Document Metadata

**Created**: 2025-10-06  
**Author**: Copilot SWE Agent  
**Version**: 1.0  
**Related Documents**:
- [QML_MIGRATION_STRATEGY.md](QML_MIGRATION_STRATEGY.md)
- [INTERFACE_IMPROVEMENT_IDEAS.md](INTERFACE_IMPROVEMENT_IDEAS.md)
- [BUILD.md](BUILD.md)
