# PolyRhythmMetronome Android - Changelog

This file tracks changes made to the Android version of PolyRhythmMetronome.

## [Unreleased]

### Added
- **Random Dark Colors**: New layers now automatically get assigned random dark colors for better visual distinction
- **Auto Flash Colors**: Flash colors are automatically generated as brighter versions of layer inactive colors

### Fixed
- **AudioTrack Initialization**: Fixed "play called on uninitialized AudioTrack" error by:
  - Switching from MODE_STATIC to MODE_STREAM for better compatibility
  - Adding initialization state check before playback
  - Scheduling proper cleanup after playback completes

## [1.5.0] - Audio Playback Bug Fix and Major Enhancements

### Fixed
- **Tone Audio Playback on Android**: Fixed critical buffer size calculation bug in AudioTrack implementation. Now uses `getMinBufferSize()` to ensure buffer meets Android system requirements, preventing "Invalid audio buffer size" errors. The fix ensures compatibility across all Android devices.

### Added
- **Separate Active/Inactive Colors**: Each layer now has two color pickers - one for the inactive background color and one for the active/flash color. This allows full customization of layer appearance during beats without breaking the flash functionality.
- **Accent Beat System**: Implemented automatic accent on first beat of each measure with adjustable accent volume multiplier (1.0-3.0x, default 1.6x). Each layer has independent accent control via slider in UI.
- **Improved Drum Synthesis**: Completely redesigned drum sounds with richer, more realistic synthesis:
  - **Kick**: Two-stage frequency sweep with punch and depth, enhanced beater click
  - **Snare**: High-passed noise with multi-frequency body and crisp attack transient
  - **Hi-hat**: Metallic shimmer with band-limited noise and high-frequency oscillations
  - **Crash**: Complex shimmer with slow modulated decay and multiple frequency components
  - **Tom**: Frequency-swept resonance with harmonics for fuller tone
  - **Ride**: Bell-like ping with multiple harmonics and sustained wash

### Changed
- **Layer Widget Height**: Increased from 80dp to 100dp to accommodate accent volume control
- **UI Layout**: Added third row with accent volume slider for fine-tuning first-beat emphasis

## [1.4.0] - UI Improvements and Enhanced Usability

### Changed
- **Subdivision Options**: Expanded from [1,2,4,8,16] to [2,3,4,5,6,7,8,16,32,64] for more rhythmic flexibility
- **Layer Widget Layout**: Completely redesigned for compactness (140dp → 80dp height)
  - Row 1: [Mode][Value] / [Subdivision] [Mute] [X]
  - Row 2: [Color Picker] [Volume Slider]
- **Color Input**: Replaced text input with visual color picker button for easier color selection
- **Play/Stop Button**: Increased height and font size for better visibility and touch interaction
- **Control Button Layout**: Reorganized to [NEW][LOAD][SAVE] spacer [LOGS] for clearer grouping

### Added
- **Visual Color Picker**: Interactive color picker popup with OK/Cancel buttons for layer colors

## [1.3.0] - Audio Backend Overhaul

### Fixed
- **Audio Installation Permission Issue**: Removed runtime auto-installation of simpleaudio which failed on Android due to permission issues
- **No Audio Playback on Android**: Implemented proper Android audio support using native AudioTrack API

### Added
- **Android AudioTrack Support**: Primary audio backend using pyjnius to access native Android audio APIs for lowest latency
- **Kivy SoundLoader Implementation**: Complete fallback implementation with WAV file caching for platforms without AudioTrack or simpleaudio
- **Three-Tier Audio System**: Automatic fallback chain: Android AudioTrack → simpleaudio → Kivy SoundLoader

### Changed
- **buildozer.spec**: Added pyjnius to requirements for Android AudioTrack support
- **Audio Library Detection**: Now properly detects platform and chooses appropriate backend
- **Audio Initialization**: Removed ensure_pkg() call for simpleaudio (should be pre-installed, not auto-installed at runtime)

## [1.2.0] - UI Improvements and Bug Fixes

### Fixed
- **Audio Playback**: Improved simpleaudio auto-installation to ensure Play button properly plays audio
- **Per-Layer Visual Flashing**: Fixed flashing to highlight specific layer rows instead of full-screen overlay, matching desktop behavior

### Added
- **Log Viewer**: New "VIEW LOGS" button displays application logs from the current session with Refresh and Copy functionality for debugging

### Changed
- **BPM Button Layout**: Changed BPM preset buttons from 4 columns (2 rows) to 8 columns (1 row) - buttons are now taller but thinner for better space usage
- **UI Spacing**: Reduced gap between BPM buttons and layer list boxes for more compact layout (spacing reduced from 10dp to 2dp)
- **Header Height**: Increased from 120dp to 140dp to accommodate taller BPM buttons
- **Controls Height**: Increased from 80dp to 120dp to accommodate logs button

## [1.1.0] - Bug Fixes and Enhancements

### Fixed
- **Audio Playback**: Fixed critical bug where Play button did not play audio - engine now properly plays sounds using simpleaudio library
- **Layer Deletion**: Removed forced minimum layer requirement - users can now remove all layers from left and/or right channels

### Added
- **Color Picker**: Each layer now has a color input field to specify custom flash colors (hex format: #RRGGBB or #RGB)
- **Visual Flashing**: Screen now flashes with the layer's color on each beat, synchronized to the specific beat division (quarter notes, eighth notes, etc.)
- **Drum Sound Support**: Full drum sound synthesis now working with audio playback (kick, snare, hihat, crash, tom, ride)

### Changed
- **BPM Button Size**: Increased BPM preset button font size from 14sp to 20sp for better touch interaction
- **Layer Widget Height**: Increased from 120dp to 140dp to accommodate color picker

## [1.0.0] - Initial Release

### Added
- **Android Application**: Complete Kivy-based metronome app for Android
- **Touch-Optimized UI**: Large buttons and controls designed for touch interaction
- **Multiple Layers Per Ear**: Full support for unlimited layers like desktop version
- **Stereo Audio**: Independent rhythm control for left and right ears
- **Layer Management**: Add/remove layers with + and X buttons
- **Scrollable Layer Lists**: Easy management of many layers
- **BPM Control**: 
  - Slider from 40-240 BPM
  - Quick preset buttons (60, 80, 100, 120, 140, 160, 180, 200)
- **Subdivision Control**: 1, 2, 4, 8, or 16 notes per beat per layer
- **Sound Mode Selection**: Choose between Tone and Drum for each layer
- **Drum Synthesis**: Six drum sounds (kick, snare, hihat, crash, tom, ride)
- **Frequency Control**: Adjustable tone pitch (Hz) for each layer in tone mode
- **Volume Control**: Independent volume sliders for each layer
- **Mute Buttons**: Toggle any layer on/off
- **Save/Load**: 
  - Save rhythm patterns to JSON files
  - Load previously saved patterns
  - Auto-save feature for current state
  - Compatible with desktop JSON format
- **Orientation Support**: Works in both portrait and landscape modes
- **NEW Button**: Quick reset to default single layer per ear
- **Buildozer Support**: Complete build configuration for Android APK generation
- **Documentation**:
  - Complete README with installation and usage instructions
  - Quick Start Guide for new users
  - Technical porting analysis
  - Architecture documentation

### Optimized For
- **Target Device**: Kindle Fire HD 10
- **Screen Size**: 10.1" (1920x1200) and other sizes
- **OS**: Fire OS / Android 5.0+
- **Touch Interface**: Large touch targets, scrollable lists
- **Orientation**: Portrait and landscape modes

### Differences from Desktop Version
- No WAV file support (desktop supports WAV playback)
- No WAV export functionality
- App-private storage (vs. full file system access)
- Touch-optimized controls with scrolling (vs. mouse/keyboard)
- Mobile-optimized layout for portrait and landscape

## Technical Details

### Dependencies
- Python 3.8+
- Kivy framework
- NumPy for audio generation

### Build System
- Buildozer for APK generation
- Android API level 31 (target)
- Android API level 21+ (minimum)
- ARM architectures: arm64-v8a, armeabi-v7a

### APK Size
- Estimated: ~20-25MB

## Future Enhancements

### Planned for Version 1.1
- [ ] Drum synthesis sound mode
- [ ] Dark/light theme support
- [ ] Haptic feedback (device vibration)
- [ ] Tempo tap feature
- [ ] Custom color picker for visual indicators

### Planned for Version 2.0
- [ ] Multiple layers per ear support
- [ ] WAV file sound mode
- [ ] Advanced save/load with file picker
- [ ] Rhythm pattern library
- [ ] Export to audio file
- [ ] Widget for home screen

## Known Limitations

### Current Version
- Sound mode limited to tone generation only
- File picker uses text input (not graphical browser)
- Portrait orientation only
- Single layer per ear

### Platform-Specific
- Requires storage permissions for save/load
- Audio latency varies by device
- Fire OS restrictions on some features

## Migration from Desktop

Users of the desktop version should note:
- JSON rhythm files are compatible with some limitations
- Multi-layer patterns will load only the first layer per ear
- WAV/Drum mode settings will be converted to tone mode
- Frequencies and subdivisions transfer directly

## Credits

Ported from the desktop PolyRhythmMetronome application.
Part of the BandTools project.

## License

See main BandTools repository for license information.
