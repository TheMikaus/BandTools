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

### 🔄 Phase 1: Core Infrastructure (Next)

**Objectives**: Implement backend modules and basic UI shell

**Tasks**:
- [ ] Split monolithic `audio_browser.py` into backend modules
- [ ] Implement Python backend classes (audio, waveform, file, annotation managers)
- [ ] Create QML main window with tab structure
- [ ] Expose backend objects to QML via context properties
- [ ] Implement basic theming system
- [ ] Set up QSettings integration
- [ ] Create reusable QML components (buttons, labels, etc.)

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
