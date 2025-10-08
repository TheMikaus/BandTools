# PolyRhythmMetronome Android - Changelog

This file tracks changes made to the Android version of PolyRhythmMetronome.

## [1.0.0] - Initial Release

### Added
- **Android Application**: Complete Kivy-based metronome app for Android
- **Touch-Optimized UI**: Large buttons and controls designed for touch interaction
- **Single Layer Per Ear**: Simplified from desktop's multi-layer approach
- **Stereo Audio**: Independent rhythm control for left and right ears
- **BPM Control**: 
  - Slider from 40-240 BPM
  - Quick preset buttons (60, 80, 100, 120, 140, 160, 180, 200)
- **Subdivision Control**: 1, 2, 4, 8, or 16 notes per beat
- **Frequency Control**: Adjustable tone pitch (Hz) for each ear
- **Volume Control**: Independent volume sliders for left and right
- **Mute Buttons**: Toggle each ear on/off
- **Visual Feedback**: On-screen beat indicators with flashing
- **Save/Load**: 
  - Save rhythm patterns to JSON files
  - Load previously saved patterns
  - Auto-save feature for current state
- **Portrait Orientation**: Optimized for 10" tablets held vertically
- **Buildozer Support**: Complete build configuration for Android APK generation
- **Documentation**:
  - Complete README with installation and usage instructions
  - Quick Start Guide for new users
  - Technical porting analysis
  - Architecture documentation

### Optimized For
- **Target Device**: Kindle Fire HD 10
- **Screen Size**: 10.1" (1920x1200)
- **OS**: Fire OS / Android 5.0+
- **Touch Interface**: Large touch targets (48dp minimum)

### Differences from Desktop Version
- Single layer per ear (vs. unlimited layers)
- Tone-only sound mode (no WAV files or drum synthesis)
- No WAV export functionality
- Portrait orientation only
- App-private storage (vs. full file system access)
- Touch-optimized controls (vs. mouse/keyboard)

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
