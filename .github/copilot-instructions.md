# BandTools - Copilot Instructions

## Project Overview

BandTools is a collection of music-related desktop applications built primarily for band practice workflow management. The repository consists of three main applications, all developed with heavy use of AI assistance (ChatGPT/Copilot).

### Applications

1. **AudioBrowserAndAnnotation** - PyQt6-based audio file browser and annotation tool
2. **JamStikRecord** - Tkinter-based MIDI recording and tablature generation tool
3. **PolyRhythmMetronome** - Tkinter-based advanced metronome with polyrhythm support

## Architecture Patterns

### Code Organization
- Each application is primarily contained in a single main file (intentionally monolithic for AI generation ease)
- Auto-installation of dependencies is implemented in each application
- JSON is used for persistent storage of settings and data
- Threading is used for audio processing and UI responsiveness

### Dependencies Management
All applications implement automatic dependency installation using pip:
```python
def _ensure_import(mod_name: str, pip_name: str | None = None) -> bool:
    # Auto-install pattern used across applications
```

## Application-Specific Guidelines

### AudioBrowserAndAnnotation (`audio_browser.py`)

**Technology Stack:**
- PyQt6 for GUI
- Native Python audio libraries (wave, audioop)
- JSON for data persistence
- Threading for background operations

**Key Features:**
- Audio file browser with waveform visualization  
- Multi-user annotation system
- Batch renaming and audio conversion
- Audio fingerprinting for automatic song identification
- Best take marking system

**Code Patterns:**
- Class-based architecture with `AudioBrowser(QMainWindow)`
- Extensive use of Qt signals and slots
- File-based JSON storage for annotations and metadata
- Threaded waveform generation and audio processing

**Development Notes:**
- Waveforms are cached and generated progressively
- Supports both WAV and MP3 formats
- Multi-user support through separate annotation files
- Cross-folder fingerprint matching for song identification
- **Version Management**: Uses automatic versioning system with MAJOR.MINOR format where minor version increments per commit

### JamStikRecord (`jsrec.py`)

**Technology Stack:**
- Tkinter for GUI
- mido for MIDI handling
- music21 for MusicXML generation
- pygame (optional) for audio feedback

**Key Features:**
- Real-time MIDI capture from JamStik devices
- Tablature generation and display
- MusicXML export (Guitar Pro compatible)
- Configurable string tuning

**Code Patterns:**
- Single main class `JSRecApp`
- Real-time MIDI processing with threading
- Tab notation using ASCII art formatting
- Time-based note quantization

### PolyRhythmMetronome (`Poly_Rhythm_Metronome.py`)

**Technology Stack:**
- Tkinter for GUI
- sounddevice for audio output (simpleaudio fallback)
- Custom drum synthesis
- Multi-threading for audio generation

**Key Features:**
- Multi-layer rhythm patterns
- Stereo subdivision metronome
- Custom drum sounds and tone generation
- Real-time rhythm editing
- Save/load rhythm patterns

**Code Patterns:**
- Event-driven audio synthesis
- Real-time parameter updates
- JSON-based rhythm storage
- Threaded audio streaming

## Coding Conventions

### Python Style
- Use type hints where practical: `def function(param: str) -> bool:`
- Prefer pathlib.Path over os.path
- Use f-strings for string formatting
- Follow PEP 8 naming conventions

### Error Handling
- Graceful degradation when optional dependencies are missing
- Try/except blocks around file operations and audio processing
- User-friendly error messages in GUI applications

### File Organization
```
ApplicationName/
├── main_application.py      # Primary application file
├── README.md               # Feature documentation  
├── CHANGELOG.md            # Version history
├── BUILD.md               # Build instructions (where applicable)
├── build_exe.bat/.sh      # Build scripts
├── docs/                  # Documentation folder (REQUIRED)
│   ├── INDEX.md           # Documentation index
│   ├── user_guides/       # End-user documentation
│   ├── technical/         # Developer/technical docs
│   └── test_plans/        # QA and testing docs
└── additional_files       # Icons, specs, etc.
```

**Documentation Organization Standards:**
- All applications MUST have a `docs/` folder with subfolders for `user_guides/`, `technical/`, and `test_plans/`
- Each `docs/` folder should contain an `INDEX.md` that lists all documentation
- Documentation should follow the same structure across all applications in the repository
- Use `.gitkeep` files to preserve empty documentation folders

### JSON Storage Patterns
- Use `.json` files for configuration and data
- Implement load/save helper functions
- Handle file corruption gracefully with defaults

## Build and Deployment

### AudioBrowserAndAnnotation
- Uses PyInstaller with custom `.spec` file
- Includes build scripts for Windows/Unix
- Auto-generates application icons
- Creates standalone executable (~100MB+)

### Dependencies
- All applications auto-install Python dependencies
- Some applications require system libraries (Qt, audio drivers)
- No external package managers required (requirements.txt, etc.)

## Development Workflow

### Testing Strategy
- Currently no automated test suites (noted as future enhancement)
- Manual testing through GUI interaction
- Audio functionality tested with sample files

### AI Development Notes
- Applications are intentionally designed as single-file monoliths for easier AI generation
- Heavy use of ChatGPT/Copilot for feature development
- Refactoring into multiple files planned for future

## Best Practices for Copilot

### When Working on Any Task
**ALWAYS ensure the following before completing any task:**
1. **Code compiles and runs** - Verify syntax and test execution
2. **Documentation is organized** - Keep documents in their respective folders:
   - `docs/user_guides/` - End-user documentation and how-to guides
   - `docs/technical/` - Developer documentation and implementation details
   - `docs/test_plans/` - Testing documentation and QA procedures
3. **All imports are auto-installed** - Ensure dependencies use auto-install patterns
4. **Application runs without crashing** - Test basic functionality before completing

### When Adding Features
1. Maintain the single-file architecture unless refactoring is explicitly requested
2. Follow existing auto-installation patterns for new dependencies  
3. Use JSON for any persistent data storage
4. Implement proper threading for audio/UI operations
5. Add comprehensive docstrings for complex functions
6. **Update version system: Update CHANGELOG.md with feature additions and changes**
7. **Create documentation**: Add user guide, technical doc, and test plan as appropriate

### When Fixing Issues
1. Preserve existing functionality while making minimal changes
2. Test audio operations thoroughly
3. Handle edge cases in file operations gracefully
4. Maintain backwards compatibility with existing data files
5. **Update version system: Document bug fixes in CHANGELOG.md**

### Version Management Guidelines
- The application uses automatic version numbering (MAJOR.MINOR format)
- MAJOR version (1.x) represents significant releases or architectural changes
- MINOR version (x.N) automatically increments with each commit via `git rev-list --count HEAD`
- **Always update CHANGELOG.md** when making changes:
  - Add new features under "### Added"
  - Document changes under "### Changed"  
  - List bug fixes under "### Fixed"
  - Note any breaking changes under "### Breaking Changes"
- Version information is imported from `version.py` module
- Version appears in window title and Help > About dialog

### Code Generation Tips
- Focus on functional code over elegant architecture
- Prioritize user experience and workflow efficiency
- Use Qt Designer patterns for PyQt6 interfaces where applicable
- Implement proper cleanup for audio resources

## Common Patterns

### Audio Processing
```python
# Waveform generation pattern
def generate_waveform_data(audio_path: Path) -> List[float]:
    # Process audio file and return normalized samples
```

### Settings Management
```python
# QSettings pattern for PyQt6 apps
settings = QSettings("BandTools", "AudioBrowser")
setting_value = settings.value("key", default_value)
```

### Threading Pattern
```python
# Background processing pattern
class WorkerThread(QThread):
    finished = pyqtSignal(object)
    
    def run(self):
        # Background work here
        self.finished.emit(result)
```

This repository represents practical desktop tools for musicians, prioritizing functionality and ease of development over architectural complexity.