# AudioBrowser QML Implementation

This directory contains the QML-based implementation of the AudioBrowser application. This is a phased migration from the PyQt6 Widgets-based `audio_browser.py` to a modern Qt Quick/QML architecture.

## 🚀 Quick Start

**Getting QML errors?** Run this one command:
```bash
python3 verify_qml_installation.py
```
See [QUICK_VERIFICATION.md](QUICK_VERIFICATION.md) for instant help.

## Project Structure

```
AudioBrowser-QML/
├── main.py                      # Application entry point
├── backend/                     # Python backend modules
│   └── __init__.py             # Backend package initialization
├── qml/                         # QML UI definitions
│   ├── main.qml                # Main application window
│   ├── components/             # Reusable UI components
│   ├── tabs/                   # Main tab views
│   ├── dialogs/                # Dialog windows
│   └── styles/                 # Theme and styling
└── resources/                   # Assets
    ├── icons/
    └── images/
```

## Migration Phases

### ✅ Phase 0: Preparation (Complete)

**Objectives**: Set up infrastructure and plan migration

**Completed Tasks**:
- ✅ Created project directory structure
- ✅ Set up main.py entry point with dependency auto-installation
- ✅ Configured PyQt6.QtQuick dependencies
- ✅ Created basic QML "Hello World" application
- ✅ Established Python-QML communication via context properties
- ✅ Verified QML application launches successfully

**Deliverables**:
- Working QML skeleton application
- Project structure in place
- Backend module structure ready for Phase 1

### ✅ Phase 1: Core Infrastructure (Complete)

**Objectives**: Implement backend modules and basic UI shell

**Completed Tasks**:
- ✅ Created SettingsManager backend module (238 lines)
- ✅ Created ColorManager backend module (261 lines)
- ✅ Created AudioEngine backend module (289 lines)
- ✅ Created FileManager backend module (368 lines)
- ✅ Created data models (FileListModel, AnnotationsModel) (339 lines)
- ✅ Exposed backend managers to QML via context properties
- ✅ Established theme synchronization between SettingsManager and ColorManager
- ✅ Integrated backend modules into main.py
- ✅ Implemented QML tab structure (Library, Annotations, Clips)
- ✅ Created LibraryTab with file list view and playback
- ✅ Created reusable styled components (StyledButton, StyledLabel, StyledTextField, StyledSlider)
- ✅ Updated main.qml with toolbar and status bar
- ✅ Added PlaybackControls component with seek slider and volume control
- ✅ Implemented directory picker dialog
- ✅ Added keyboard shortcuts for common operations
- ✅ Created comprehensive UI components

### ✅ Phase 2: Waveform Display (Complete)

**Objectives**: Implement waveform visualization with playback integration

**Completed Tasks**:
- ✅ Created WaveformEngine backend module (~450 lines)
  - Waveform data generation from audio files
  - Progressive loading with progress signals
  - Caching system for performance
  - Support for WAV and MP3 formats
- ✅ Created WaveformView QQuickPaintedItem (~200 lines)
  - Custom painting for waveform visualization
  - Click-to-seek functionality
  - Playback position tracking
  - Theme-aware colors
- ✅ Created WaveformDisplay QML component (~300 lines)
  - Loading indicators
  - Error handling
  - Auto-generation on file load
  - Integration with AudioEngine
  - Zoom controls (1x-10x)
- ✅ Updated AnnotationsTab with waveform display
- ✅ Registered WaveformView as QML type
- ✅ Integrated with main.py and backend systems

### ✅ Phase 3: Annotation System (Complete)

**Objectives**: Implement comprehensive annotation management

**Completed Tasks**:
- ✅ Created AnnotationManager backend module (~490 lines)
  - Full CRUD operations for annotations
  - JSON file-based persistence
  - Multi-user support with username tracking
  - Category-based organization
  - Filtering and search functionality
- ✅ Created AnnotationMarker QML component (~180 lines)
  - Visual markers on waveform at timestamps
  - Color-coded by category
  - Interactive tooltips on hover
  - Click-to-seek, double-click to edit
- ✅ Created AnnotationDialog QML component (~380 lines)
  - Create and edit annotations
  - Timestamp, text, category, color, importance
  - "Use Current Time" button
  - Validation and error handling
- ✅ Updated AnnotationsTab with full UI (~350 lines added)
  - TableView for annotation list
  - Add/Edit/Delete/Clear controls
  - Filter by category and importance
  - Empty state handling
- ✅ Integrated with WaveformDisplay for marker rendering
- ✅ Connected to main.py and models
- ✅ Comprehensive documentation (PHASE_3_COMPLETE.md)

**Features**:
- Create annotations at any timestamp
- Edit existing annotations
- Delete individual or all annotations
- Filter by category (timing, energy, harmony, dynamics, notes)
- Filter by importance
- Visual markers on waveform
- Color selection (7 colors)
- Automatic persistence
- Multi-user attribution

### 🚧 Phase 7: Additional Features (In Progress)

**Objectives**: Add features from original audio_browser.py for feature parity

**Completed Tasks**:
- ✅ Created FolderNotesManager backend module (250 lines)
- ✅ Created FolderNotesTab with auto-save (235 lines)
- ✅ Created FileContextMenu component (240 lines)
- ✅ Extended FileManager with system integration
- ✅ Added right-click context menus to Library tab
- ✅ Added file properties dialog
- ✅ Added Ctrl+4 keyboard shortcut for Folder Notes
- ✅ Created BatchOperations backend module (~700 lines)
- ✅ Created BatchRenameDialog QML component (~280 lines)
- ✅ Created BatchConvertDialog QML component (~450 lines)
- ✅ Created ProgressDialog QML component (~220 lines)
- ✅ Added batch operations toolbar buttons
- ✅ Integrated batch operations with main application
- ✅ Comprehensive test suite for batch operations

**Features**:
- Folder-level notes with auto-save
- Right-click context menus on files
- System file manager integration
- File properties display
- Copy file path to clipboard
- **Batch rename files** with sequential numbering (##_pattern format)
- **Convert WAV to MP3** with bitrate selection
- **Convert stereo to mono** with channel selection
- **Volume boost export** with adjustable dB boost
- Progress tracking for all batch operations
- Preview before execution for batch rename
- Error handling and status reporting

### ✅ Phase 5: Clips System (Complete)

**Objectives**: Implement audio clip management and export

**Completed Tasks**:
- ✅ Created ClipManager backend module (~440 lines)
  - Full CRUD operations for clips
  - JSON file-based persistence
  - Export functionality to extract audio segments
  - Timestamp validation and error handling
- ✅ Created ClipMarker QML component (~230 lines)
  - Visual clip boundaries on waveform
  - Start/end markers with labels
  - Highlighted region between markers
  - Interactive tooltips on hover
  - Click-to-select, double-click to edit
- ✅ Created ClipDialog QML component (~320 lines)
  - Create and edit clips
  - Start/end time input with validation
  - "Use Current" buttons for playback position
  - Name and notes fields
- ✅ Updated ClipsTab with full UI (~420 lines)
  - TableView for clip list
  - Add/Edit/Delete/Export/Clear controls
  - Empty state handling
  - Confirmation dialogs
- ✅ Integrated with WaveformDisplay for marker rendering
- ✅ Connected to main.py and clip manager
- ✅ Comprehensive documentation (PHASE_5_CLIPS_SUMMARY.md)

**Features**:
- Create clips with start/end timestamps
- Edit existing clips (all properties)
- Delete individual or all clips
- Export clips as separate audio files
- Visual clip markers on waveform
- Click on clip to seek to start
- Duration calculation and display
- Automatic persistence
- Support for WAV, MP3, OGG, FLAC formats

## Running the Application

### Prerequisites

- Python 3.8+
- PyQt6 and Qt6 QML modules

### Installation

#### Option 1: System Packages (Recommended for Linux)

On Ubuntu/Debian systems, install the required Qt6 packages:

```bash
sudo apt-get update
sudo apt-get install -y \
    python3-pyqt6 \
    python3-pyqt6.qtquick \
    python3-pyqt6.qtmultimedia \
    qml6-module-qtquick \
    qml6-module-qtquick-controls \
    qml6-module-qtquick-layouts \
    qml6-module-qtquick-dialogs \
    qml6-module-qtquick-templates \
    qml6-module-qtquick-window \
    qml6-module-qtqml-models \
    qml6-module-qtqml-workerscript
```

#### Option 2: pip (Alternative)

If system packages are not available, PyQt6 can be installed via pip (this will be attempted automatically on first run):

```bash
pip install PyQt6 pydub
```

Note: The QML modules may not be available via pip on all platforms. System packages are recommended.

#### FFmpeg Requirement (For MP3 Support)

**Important**: While Qt Multimedia includes built-in FFmpeg for audio playback, **waveform generation requires a separate FFmpeg installation** that pydub can access.

Install FFmpeg:
- **Windows**: `winget install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`
- **macOS**: `brew install ffmpeg`

Without FFmpeg:
- ✅ WAV files will work (native Python support)
- ✅ MP3/OGG/FLAC playback will work (Qt's built-in FFmpeg)
- ❌ MP3/OGG/FLAC waveform generation will not work

To verify FFmpeg is detected, run:
```bash
python3 test_ffmpeg_detection.py
```

### Launch

```bash
cd AudioBrowser-QML
python3 main.py
```

Or use the provided launch script:

```bash
cd AudioBrowser-QML
./run.sh
```

The application will attempt to install PyQt6 dependencies automatically if they are not present.

### Features Available

**Phase 1 Features** (Core Infrastructure):
- Audio file browsing and playback
- Directory selection with file picker dialog
- Play/pause/stop controls
- Seek slider with time display
- Volume control with slider
- Theme switching (light/dark)
- Keyboard shortcuts (see KEYBOARD_SHORTCUTS.md)
- File filtering by name
- Responsive UI with custom styled components

**Phase 7 Features** (Additional Features - In Progress):
- Folder notes with auto-save
- File context menus (right-click)
- Audio duration display in file list
- Sortable columns (name, duration, size)
- Show in system file manager
- Copy file path to clipboard
- File properties dialog
- **Batch rename files** with sequential numbering
- **Batch convert WAV to MP3** with customizable bitrate
- **Convert stereo to mono** with channel selection
- **Volume boost export** with adjustable dB level
- Progress dialogs for long-running operations
- Preview before batch rename execution
- Automatic file refresh after operations

**Phase 2 Features** (Waveform Display):
- Waveform visualization for audio files
- Click-to-seek on waveform
- Zoom controls (1x to 10x)
- Horizontal scrolling when zoomed
- Loading indicators with progress
- Cached waveform data for performance
- Playback position tracking on waveform

**Phase 3 Features** (Annotations):
- Create annotations at any timestamp
- Edit existing annotations
- Delete annotations (individual or all)
- Visual markers on waveform
- Color-coded annotations (7 colors)
- Category organization (timing, energy, harmony, dynamics, notes)
- Importance flagging
- Filter by category
- Filter by importance
- Interactive tooltips on markers
- Click marker to seek
- Double-click marker to edit
- Automatic persistence to JSON
- Multi-user support

**Phase 5 Features** (Clips):
- Create clips with start/end timestamps
- Edit existing clips
- Delete clips (individual or all)
- Export clips as separate audio files
- Play clip region for focused practice
- Visual clip markers on waveform with region highlighting
- Start "[" and end "]" boundary markers
- Click to select, double-click to edit
- Interactive tooltips showing duration
- Time format validation (MM:SS.mmm)
- "Use Current" buttons to capture playback position
- Name and notes for each clip
- Automatic persistence to JSON
- Support for WAV, MP3, OGG, FLAC export formats

**Phase 6 Features** (Polish & Enhancements):
- Extended keyboard shortcuts (Left/Right arrows for navigation)
- Clip playback with automatic boundary handling and loop support
- Annotation keyboard shortcuts (Ctrl+A for quick annotation creation)
- Clip marker keyboard shortcuts ([ and ] to set clip boundaries)
- Context-aware keyboard handling (shortcuts disabled during text input)
- Comprehensive tooltips throughout the interface
- Improved version tracking and display
- Enhanced user experience refinements

**Phase 7 Features** (Additional Features - In Progress):
- Folder Notes tab for per-folder note-taking
- Auto-save notes as you type
- Character and word count display
- File context menus (right-click on files)
- System file manager integration (Show in Explorer)
- File properties display
- Copy file path to clipboard
- Quick actions: Play, Annotate, Create Clip

## Development Notes

- This QML implementation runs independently from the original `audio_browser.py`
- Both applications can coexist during the migration period
- The migration follows the strategy outlined in `docs/technical/QML_MIGRATION_STRATEGY.md`
- Backend modules will be gradually extracted from `audio_browser.py` in Phase 1

## Architecture Patterns

### Model-View-ViewModel (MVVM)

- **Models (Python)**: QAbstractListModel/QAbstractTableModel for data exposure
- **Views (QML)**: Declarative UI definitions
- **ViewModels (Python)**: Business logic and coordination via QObject

### Communication

- **Python → QML**: Signals and Q_PROPERTY bindings
- **QML → Python**: Q_INVOKABLE methods and pyqtSlot decorators
- **Context Properties**: Backend objects exposed to QML via QQmlContext

## User Guides

- [Quick Start Guide](docs/user_guides/QUICK_START.md)
- [Annotation Guide](docs/user_guides/ANNOTATION_GUIDE.md)
- [Waveform Guide](docs/user_guides/WAVEFORM_GUIDE.md)
- [Keyboard Shortcuts](docs/user_guides/KEYBOARD_SHORTCUTS.md)
- [Batch Operations Guide](docs/user_guides/BATCH_OPERATIONS_GUIDE.md)
- [QML Error Troubleshooting](docs/user_guides/QML_ERROR_TROUBLESHOOTING.md) - Fix QML loading errors

## Troubleshooting

If you encounter QML compilation errors like "Duplicate signal name" or "Cannot assign to non-existent property", see the [QML Error Troubleshooting Guide](docs/user_guides/QML_ERROR_TROUBLESHOOTING.md) for detailed solutions.

## References

- [QML Migration Strategy](../docs/technical/QML_MIGRATION_STRATEGY.md)
- [Current Architecture Inventory](../docs/technical/CURRENT_ARCHITECTURE_INVENTORY.md)
- [Phase 1 Implementation Summary](../docs/technical/PHASE_1_IMPLEMENTATION_SUMMARY.md)
