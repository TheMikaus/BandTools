# BandTools

A collection of music-related desktop applications built for band practice workflow management. All applications are developed with heavy use of AI assistance (ChatGPT/Copilot) and prioritize functionality and ease of development.

## Applications

### 1. AudioBrowserAndAnnotation

PyQt6-based audio file browser and annotation tool for musicians.

**Key Features:**
- Audio file browser with waveform visualization
- Multi-user annotation system
- Batch renaming and audio conversion
- Audio fingerprinting for automatic song identification
- Best take marking system
- Practice goals and statistics tracking
- Setlist builder for performances

**Versions:**
- **AudioBrowserOrig** - Original mature version with full feature set
- **AudioBrowser-QML** - Modern QML-based rewrite (in development)

📖 [Documentation](AudioBrowserAndAnnotation/AudioBrowserOrig/docs/INDEX.md)

### 2. PolyRhythmMetronome

Tkinter-based advanced metronome with polyrhythm support.

**Key Features:**
- Multi-layer rhythm patterns
- Stereo subdivision metronome
- Custom drum sounds and tone generation
- Real-time rhythm editing
- Save/load rhythm patterns
- Export to WAV

📖 [Documentation](PolyRhythmMetronome/docs/INDEX.md) | 📖 [README](PolyRhythmMetronome/README.md)

### 3. JamStikRecord

Tkinter-based MIDI recording and tablature generation tool for JamStik devices.

**Key Features:**
- Real-time MIDI capture from JamStik devices
- Tablature generation and display
- MusicXML export (Guitar Pro compatible)
- Configurable string tuning

📖 [Documentation](JamStikRecord/docs/INDEX.md)

## Technology Stack

### AudioBrowserAndAnnotation
- **GUI**: PyQt6
- **Audio**: Native Python (wave, audioop), pydub (optional)
- **Storage**: JSON for annotations and settings
- **Threading**: Background waveform generation and audio processing

### PolyRhythmMetronome
- **GUI**: Tkinter
- **Audio**: sounddevice (primary), simpleaudio (fallback)
- **Synthesis**: Custom drum synthesis with numpy
- **Storage**: JSON for rhythm patterns

### JamStikRecord
- **GUI**: Tkinter
- **MIDI**: mido for MIDI handling
- **Music**: music21 for MusicXML generation
- **Audio**: pygame (optional) for audio feedback

## Quick Start

All applications automatically install their dependencies on first run. Simply:

1. Clone the repository:
   ```bash
   git clone https://github.com/TheMikaus/BandTools.git
   cd BandTools
   ```

2. Run the application you want:
   ```bash
   # AudioBrowser (Original)
   cd AudioBrowserAndAnnotation/AudioBrowserOrig
   python3 audio_browser.py
   
   # AudioBrowser (QML)
   cd AudioBrowserAndAnnotation/AudioBrowser-QML
   python3 main.py
   
   # PolyRhythmMetronome
   cd PolyRhythmMetronome
   python3 Poly_Rhythm_Metronome.py
   ```

3. Dependencies will be installed automatically on first run

## Development

### Repository Standards

This repository follows strict standards for code quality, documentation, and dependency management. See [REPOSITORY_STANDARDS.md](REPOSITORY_STANDARDS.md) for detailed information.

**Key Standards:**
- ✓ All code must compile and run
- ✓ Structured documentation in `docs/` folders (user_guides, technical, test_plans)
- ✓ Automatic dependency installation
- ✓ Applications must run without crashing

### Verification

Verify repository standards compliance:
```bash
python3 verify_repository_standards.py
```

### Documentation Structure

Each application maintains documentation in a standard structure:
```
Application/
├── docs/
│   ├── INDEX.md           # Documentation index
│   ├── user_guides/       # End-user documentation
│   ├── technical/         # Developer documentation
│   └── test_plans/        # QA and testing documentation
```

### AI Development

This repository is designed for AI-assisted development:
- See [.github/copilot-instructions.md](.github/copilot-instructions.md) for Copilot guidelines
- Applications use monolithic single-file architecture for easier AI generation
- Automatic dependency installation simplifies development workflow

## Building Executables

### AudioBrowserAndAnnotation

Build standalone executables using PyInstaller:

**Windows:**
```bash
cd AudioBrowserAndAnnotation/AudioBrowserOrig
build_exe.bat
```

**Linux/macOS:**
```bash
cd AudioBrowserAndAnnotation/AudioBrowserOrig
chmod +x build_exe.sh
./build_exe.sh
```

See [AudioBrowserAndAnnotation/AudioBrowserOrig/docs/technical/BUILD.md](AudioBrowserAndAnnotation/AudioBrowserOrig/docs/technical/BUILD.md) for details.

## Architecture Patterns

### Auto-Installation
All applications implement automatic dependency installation:
```python
def _ensure_import(mod_name: str, pip_name: str | None = None) -> bool:
    # Auto-install pattern used across applications
```

### Data Storage
- JSON files for settings and persistent data
- QSettings for Qt applications
- Human-readable configuration files

### Threading
- Background processing for audio operations
- UI responsiveness maintained during heavy operations
- Proper cleanup for audio resources

## Version Management

- MAJOR.MINOR version format
- MINOR version auto-increments per commit
- CHANGELOG.md tracks all changes
- Version displayed in application UI

## Contributing

1. Follow [REPOSITORY_STANDARDS.md](REPOSITORY_STANDARDS.md)
2. Update documentation when adding features
3. Test thoroughly before committing
4. Run verification script to ensure compliance
5. Update CHANGELOG.md with changes

### Adding Features

When adding new features:
1. Create user guide in `docs/user_guides/`
2. Create implementation summary in `docs/technical/`
3. Create test plan in `docs/test_plans/`
4. Update docs/INDEX.md
5. Update application README.md and CHANGELOG.md

## Testing

### Automated Tests
```bash
# AudioBrowser-QML backend tests
cd AudioBrowserAndAnnotation/AudioBrowser-QML
python3 test_backend.py

# Repository standards verification
python3 verify_repository_standards.py
```

### Manual Testing
- GUI applications require manual testing
- Audio functionality tested with sample files
- Cross-platform testing recommended

## Requirements

- Python 3.7 or higher
- Internet connection for first-run dependency installation
- System audio support
- For AudioBrowser: Qt graphics support on Linux

## License

See individual applications for license information.

## Support

- 📖 [Repository Standards](REPOSITORY_STANDARDS.md)
- 📖 [Copilot Instructions](.github/copilot-instructions.md)
- 🐛 [Report Issues](https://github.com/TheMikaus/BandTools/issues)

---

**Note**: This repository represents practical desktop tools for musicians, prioritizing functionality and ease of development over architectural complexity.
