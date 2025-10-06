# AudioBrowser QML Implementation

This directory contains the QML-based implementation of the AudioBrowser application. This is a phased migration from the PyQt6 Widgets-based `audio_browser.py` to a modern Qt Quick/QML architecture.

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
- PyQt6 (automatically installed on first run)

### Launch

```bash
cd AudioBrowser-QML
python3 main.py
```

The application will automatically install PyQt6 dependencies if they are not present.

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
- Clip playback with automatic boundary handling
- Improved version tracking and display
- Enhanced user experience refinements

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

## References

- [QML Migration Strategy](../docs/technical/QML_MIGRATION_STRATEGY.md)
- [Current Architecture Inventory](../docs/technical/CURRENT_ARCHITECTURE_INVENTORY.md)
- [Phase 1 Implementation Summary](../docs/technical/PHASE_1_IMPLEMENTATION_SUMMARY.md)
