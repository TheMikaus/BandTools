# AudioBrowser QML - Quick Start Guide

## What is AudioBrowser QML?

AudioBrowser QML is a modern Qt Quick/QML-based audio file browser and annotation tool for musicians and band practice sessions. It's a complete rewrite of the original PyQt6 Widgets-based audio browser, using QML for a more modern and flexible UI.

## Current Status

- **Phase**: 7 (Additional Features)
- **Progress**: 55% complete
- **Status**: ✅ Fully functional and tested
- **Version**: 0.7.0

## Quick Installation (Ubuntu/Debian)

```bash
# Install Qt6 dependencies
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

# Navigate to the application directory
cd AudioBrowserAndAnnotation/AudioBrowser-QML

# Run the application
./run.sh
# or
python3 main.py
```

## What Can It Do?

### ✅ Working Features

1. **Audio Playback**
   - Play/pause/stop controls
   - Seek slider with time display
   - Volume control
   - Support for WAV and MP3 files

2. **File Management**
   - Browse audio files in directories
   - Display file duration, size, and metadata
   - Sort by name, duration, or size
   - Right-click context menus for quick actions
   - Open file location in system file manager
   - Copy file paths to clipboard

3. **Waveform Visualization**
   - Visual waveform display
   - Click-to-seek on waveform
   - Zoom controls (1x to 10x)
   - Playback position tracking

4. **Annotations**
   - Create annotations at any timestamp
   - Color-coded categories (timing, energy, harmony, dynamics, notes)
   - Importance flagging
   - Filter by category and importance
   - Visual markers on waveform
   - Multi-user support

5. **Clips System**
   - Create clips with start/end timestamps
   - Export clips as separate audio files
   - Visual clip markers on waveform
   - Loop playback within clip boundaries

6. **Folder Notes**
   - Per-folder note-taking
   - Auto-save as you type
   - Character and word count
   - Organize session notes and song arrangements

7. **User Interface**
   - Dark and light themes
   - Comprehensive keyboard shortcuts
   - Responsive layout
   - Context-aware controls

## Keyboard Shortcuts

### Navigation
- **Ctrl+1**: Library tab
- **Ctrl+2**: Annotations tab
- **Ctrl+3**: Clips tab
- **Ctrl+4**: Folder Notes tab

### Playback
- **Space**: Play/Pause
- **Ctrl+S**: Stop
- **Left/Right Arrow**: Seek backward/forward
- **Up/Down Arrow**: Volume up/down

### Quick Actions
- **Ctrl+A**: Add annotation at current time
- **[**: Set clip start time
- **]**: Set clip end time
- **Ctrl+L**: Open file location in file manager

See KEYBOARD_SHORTCUTS.md for the complete list.

## Testing

Run the test suites to verify everything is working:

```bash
# Structure validation
python3 test_structure.py

# Backend module tests
python3 test_backend.py

# Application startup test
python3 test_integration.py

# Enhanced file list tests
python3 test_enhanced_file_list.py

# Clips system tests
python3 test_clips.py
```

All tests should pass with ✅ status.

## Troubleshooting

### Application Won't Start

**Error**: "module 'QtQuick' is not installed"

**Solution**: Install the missing QML module. See the full list in README.md under Installation.

### No Audio Playback

**Issue**: This is expected in headless/CI environments.

**Solution**: Run on a system with audio output devices.

### Binding Loop Warnings

**Issue**: Warnings about binding loops in the console.

**Impact**: None - these are false positives and don't affect functionality.

**Status**: Known Qt behavior with property passing pattern.

## Documentation

- **README.md** - Complete project documentation
- **VERIFICATION_SUMMARY.md** - Detailed test results and verification
- **PHASE_7_SUMMARY.md** - Phase 7 implementation details
- **KEYBOARD_SHORTCUTS.md** - Complete keyboard shortcut reference
- **DEVELOPER_GUIDE.md** - Guide for developers
- **PROJECT_STRUCTURE.md** - Architecture and code organization

## Getting Help

- Check the documentation files for detailed information
- Review test results in VERIFICATION_SUMMARY.md
- Open an issue on GitHub for bugs or feature requests

## What's Next?

Phase 7 development continues with:
- Batch operations (rename/convert multiple files)
- Additional polish and testing
- Performance optimizations
- More keyboard shortcuts

Current progress: 55% complete (3 of 6 major features done)

---

**Last Updated**: December 2024  
**Version**: 0.7.0  
**Status**: ✅ Production Ready
