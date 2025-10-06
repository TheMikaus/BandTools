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

### ✅ Phase 1: Core Infrastructure (95% Complete)

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

**Remaining Tasks**:
- [ ] Test UI functionality with real audio files
- [ ] Implement waveform display for AnnotationsTab (Phase 2)
- [ ] Implement annotation persistence (Phase 2)
- [ ] Performance optimization

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

**Phase 1 Features**:
- Audio file browsing and playback
- Directory selection with file picker dialog
- Play/pause/stop controls
- Seek slider with time display
- Volume control with slider
- Theme switching (light/dark)
- Keyboard shortcuts (see KEYBOARD_SHORTCUTS.md)
- File filtering by name
- Responsive UI with custom styled components

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
