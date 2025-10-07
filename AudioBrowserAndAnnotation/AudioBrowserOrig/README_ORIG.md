# AudioBrowser (Original PyQt6 Version)

This folder contains the original single-file PyQt6 implementation of AudioBrowser.

## About This Version

This is the **original, stable, production-ready** version of AudioBrowser that has been in use and continuously improved since the project's inception. It's a monolithic application built with PyQt6 widgets.

## Files in This Folder

- **audio_browser.py** - Main application (single file, ~7000+ lines)
- **version.py** - Version information module
- **build_exe.sh / build_exe.bat** - Build scripts for creating executables
- **audio_browser.spec** - PyInstaller specification file
- **make_icon.py** - Icon generation script
- **app_icon.png / app_icon.ico** - Application icons
- **gdrive_sync.py** - Google Drive synchronization module
- **sync_dialog.py** - Google Drive sync dialog
- **credentials.json.example** - Example Google Drive credentials file
- **docs/** - Complete documentation for this version

## Documentation

Full documentation for this version is in the `docs/` subdirectory:

- [docs/INDEX.md](docs/INDEX.md) - Documentation index
- [docs/user_guides/](docs/user_guides/) - User guides and how-tos
- [docs/technical/](docs/technical/) - Technical documentation
- [docs/test_plans/](docs/test_plans/) - Test plans and QA documentation

## QML Version

A new QML-based version is under development in the `AudioBrowser-QML/` folder at the parent level. The QML version aims to provide a more modern UI while maintaining feature parity with this original version.

## Building

To build an executable:

**Linux/Mac:**
```bash
./build_exe.sh
```

**Windows:**
```bat
build_exe.bat
```

The executable will be created in the `dist/` directory.

## Features

This version includes all AudioBrowser features:
- Audio file browser with waveform visualization
- Multi-user annotation system
- Audio playback and seeking
- Practice goals and statistics tracking
- Setlist builder
- Tempo/metronome features
- Batch operations (rename, convert)
- Audio fingerprinting
- Google Drive synchronization (optional)
- And much more...

See the [main documentation](docs/INDEX.md) for complete feature details.

## Python Version Support

**Important**: As of December 2024, this version has been updated to work with Python 3.13+, which removed the deprecated `audioop` module. The audio sample conversion functionality previously provided by `audioop` has been replaced with a pure Python implementation.

## Why Keep This Version?

The original version is kept because:
1. It's the stable, battle-tested implementation
2. It has all features working and well-documented
3. Some users may prefer the widget-based UI
4. It serves as a reference for the QML migration
5. It can be used if the QML version has issues

---

**Note**: For new features and development, consider using or contributing to the QML version. This original version is primarily in maintenance mode.
