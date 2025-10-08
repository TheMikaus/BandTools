# PolyRhythmMetronome

A stereo subdivision metronome with multi-layer support, visual flashing, and advanced rhythm features.

## Platform Versions

This application is available in two versions optimized for different platforms:

### Desktop Version
- **Location**: [`Desktop/`](Desktop/)
- **Technology**: Tkinter (Python GUI)
- **Platform**: Windows, macOS, Linux
- **Features**: Full-featured desktop application with mouse/keyboard controls
- **Documentation**: See [Desktop/README.md](Desktop/README.md)

### Android Version
- **Location**: [`android/`](android/)
- **Technology**: Kivy (Python mobile framework)
- **Platform**: Android devices (optimized for Kindle Fire HD 10)
- **Features**: Touch-optimized mobile interface with simplified controls
- **Documentation**: See [android/README.md](android/README.md)

## Quick Start

### Desktop
```bash
cd Desktop
python3 Poly_Rhythm_Metronome.py
```

### Android
See [android/README.md](android/README.md) for build and installation instructions.

## Features

Both versions include:
- **Stereo Layers**: Independent rhythm layers for left and right ears
- **Multiple Sound Sources**: Tone generation, WAV file playback, drum synthesis
- **Per-Layer Controls**: Mute/unmute, volume, color coding, subdivision settings
- **Global Settings**: BPM control, time signature, accent factor
- **Save/Load**: Save and load rhythm patterns as JSON files

The Android version includes touch-optimized simplifications for ease of use on mobile devices.

## Development

See individual platform folders for specific development information.
