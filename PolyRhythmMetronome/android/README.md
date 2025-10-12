# PolyRhythmMetronome - Android Version

A touch-optimized metronome application for Android devices, specifically optimized for Kindle Fire HD 10.

## Features

This is a full-featured version of PolyRhythmMetronome, optimized for mobile use:

### Touch-Optimized for Mobile
- **Multiple Layers Per Ear**: Full support for unlimited layers like the desktop version
- **Large Touch Targets**: All buttons and controls are sized for easy touch interaction
- **BPM Presets**: Quick-access buttons for common tempos (60, 80, 100, 120, 140, 160, 180, 200 BPM)
- **Sound Generation**: Tone and Drum synthesis modes (kick, snare, hihat, crash, tom, ride)
- **Orientation Support**: Works in both portrait and landscape orientations

### Core Features
- **Multiple Stereo Layers**: Multiple independent rhythm layers for left and right ears (like desktop)
- **BPM Control**: Adjustable from 40 to 240 BPM via slider or preset buttons
- **Subdivision Settings**: Choose from 1, 2, 4, 8, or 16 notes per beat per layer
- **Sound Modes**: Tone (adjustable frequency in Hz) or Drum synthesis
- **Drum Sounds**: Six drum types (kick, snare, hihat, crash, tom, ride)
- **Volume Control**: Independent volume per layer
- **Mute Controls**: Toggle any layer on/off
- **Layer Management**: Add/remove layers dynamically with + and X buttons
- **Save/Load**: Save and load rhythm patterns as JSON files (compatible with desktop)
- **Auto-save**: Automatically saves your current settings
- **Orientation Support**: Full support for portrait and landscape modes

## Requirements

### For Running on Device
- Android device with API level 21+ (Android 5.0 Lollipop or newer)
- Kindle Fire HD 10 runs Fire OS (based on Android 9), which is fully compatible

### For Building
- Linux or macOS (recommended for building Android apps)
- Python 3.8+
- Buildozer (for creating Android APK)
- Android SDK and NDK

## Installation

#### For Windows Users
Follow the instructions for installation of buildozer here - https://buildozer.readthedocs.io/en/latest/installation.html#android-on-windows-10-or-11
Then build in the android folder with buildozer -v android debug

### Runtime Issues

**Problem**: App crashes on start
**Solution**: Check logcat for Python errors. Ensure device has Android 5.0+

**Problem**: No sound
**Solution**: 
- Check device volume and ensure neither ear is muted
- Verify the app shows one of: "[audio] Using Android AudioTrack", "[audio] Using simpleaudio", or "[audio] Using Kivy SoundLoader" in logs
- The app automatically selects the best available audio backend (Android AudioTrack → simpleaudio → Kivy SoundLoader)
- On Android, ensure pyjnius is included in the build (check buildozer.spec requirements)

**Problem**: Can't save/load files
**Solution**: Grant storage permissions in Android Settings > Apps > PolyRhythm Metronome

## Future Enhancements

Potential features for future versions:
- Multi-layer support (similar to desktop)
- Drum sound synthesis
- WAV file support
- Visual metronome with animations
- Haptic feedback (device vibration)
- Dark/light themes
- Tempo tap feature
- Custom color picker
- Export to audio file

## Support

For issues, feature requests, or contributions, please visit the main BandTools repository.

## License

Part of the BandTools project. See main repository for license information.
