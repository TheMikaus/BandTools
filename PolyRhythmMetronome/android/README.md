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

### Option 1: Pre-built APK (Recommended)
If an APK file is available, simply:
1. Transfer the APK to your Android device
2. Enable "Install from Unknown Sources" in Settings
3. Tap the APK file to install

### Option 2: Build from Source

#### For Windows Users

**Quick Start: Desktop Testing (No Build Needed)**

For rapid development and testing, run the app directly on Windows:

```bash
pip install kivy numpy
python main.py
```

This gives instant feedback without building APKs. Perfect for 90% of development!

See [Local Development on Windows](docs/user_guides/LOCAL_DEVELOPMENT_WINDOWS.md) for complete guide.

**Building APKs**

When you need to create APKs, you have several options:

**Option A: GitHub Actions (Recommended - No Local Setup)**
- Fork the repository and set up GitHub Actions to build APKs
- Download built APKs from GitHub Releases or Actions artifacts
- No local Linux environment needed!

**Option B: WSL2 (Fast Local Builds)**
```powershell
# Install WSL2
wsl --install

# Install Ubuntu from Microsoft Store, then run:
sudo python3 setup_android_dev.py
```
Subsequent builds take only 5-10 minutes.

**Option C: Docker or VM**
- Use Docker Desktop with a Linux container
- Use VirtualBox/VMware with Ubuntu

#### Setup Build Environment (Linux/macOS)

**Automated Setup (Recommended):**
```bash
# Run the automated setup script
sudo python3 setup_android_dev.py
```

This script will:
- Check Python version (3.8+)
- Install buildozer and cython
- Install system dependencies (OpenJDK, build tools)
- Verify all requirements are met

**Manual Setup:**

1. **Install Buildozer**:
```bash
pip install buildozer
```

2. **Install Dependencies** (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install -y git zip unzip openjdk-11-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses-dev libncursesw5-dev cmake libffi-dev libssl-dev
```

3. **Install Cython**:
```bash
pip install cython
```

#### Build the APK

1. Navigate to the android directory:
```bash
cd PolyRhythmMetronome/android
```

2. Initialize Buildozer (first time only):
```bash
buildozer init
```
Note: We already have a buildozer.spec file, so this step is optional.

3. Build the APK:
```bash
buildozer -v android debug
```

This will:
- Download and set up Android SDK/NDK
- Install required Python packages
- Compile the app
- Create an APK in `bin/` directory

The first build can take 30-60 minutes as it downloads and compiles dependencies.

4. The APK will be created at:
```
bin/polyrhythmmetronome-1.0-arm64-v8a-debug.apk
```

#### Install on Device

1. **Via USB**:
```bash
buildozer android deploy run
```

2. **Manual Transfer**:
- Copy the APK from `bin/` to your device
- Install using a file manager app

## Usage

### Basic Operation

1. **Set Tempo**: 
   - Use the BPM slider for precise control
   - Tap preset buttons for common tempos

2. **Configure Layers**:
   - **LEFT section** (blue background): Controls left ear
   - **RIGHT section** (red background): Controls right ear
   - Adjust subdivision (notes per beat)
   - Set frequency (pitch in Hz)
   - Adjust volume
   - Use MUTE button to toggle each ear

3. **Start Playing**:
   - Tap the green PLAY button
   - Visual indicators (●) will flash with each beat
   - Button changes to red STOP

4. **Save Your Pattern**:
   - Tap SAVE
   - Enter a filename
   - Pattern is saved to app storage

5. **Load a Pattern**:
   - Tap LOAD
   - Enter the filename
   - Pattern settings are restored

### Tips for Kindle Fire HD 10

- **Portrait Mode**: The app is optimized for portrait orientation
- **Screen Size**: Designed for 10.1" display (1920x1200)
- **Storage**: Patterns are saved to app-private storage
- **Performance**: Fire HD 10 has sufficient CPU/RAM for smooth operation

## Differences from Desktop Version

| Feature | Desktop | Android |
|---------|---------|---------|
| Layers per ear | Multiple | Multiple (full support) |
| Sound modes | Tone, WAV, Drum | Tone, Drum (WAV not supported) |
| UI framework | Tkinter | Kivy |
| File operations | Full file system | App storage |
| Controls | Mouse/keyboard | Touch-optimized |
| Orientation | Any | Portrait and Landscape |
| WAV export | Yes | No |

## Technical Details

### Architecture

- **Framework**: Kivy (Python mobile framework)
- **Audio**: Simple tone generation using NumPy
- **Threading**: Background thread for metronome timing
- **Storage**: JSON files in app-private storage

### File Format

Rhythm patterns are saved as JSON:
```json
{
  "bpm": 120.0,
  "beats_per_measure": 4,
  "accent_factor": 1.6,
  "left": {
    "subdiv": 4,
    "freq": 880.0,
    "vol": 1.0,
    "mute": false,
    "color": "#3B82F6"
  },
  "right": {
    "subdiv": 4,
    "freq": 440.0,
    "vol": 1.0,
    "mute": false,
    "color": "#EF4444"
  }
}
```

### Permissions

The app requests:
- `WRITE_EXTERNAL_STORAGE`: For saving rhythm patterns
- `READ_EXTERNAL_STORAGE`: For loading rhythm patterns
- `INTERNET`: For potential future features (not currently used)

## Development

### Testing on Desktop

While building for Android, you can test the app on desktop:

```bash
python main.py
```

This requires:
```bash
pip install kivy numpy
```

### Modifying the App

Key files:
- `main.py`: Main application code
- `buildozer.spec`: Build configuration
- `docs/`: Documentation

### Debugging

Enable USB debugging on your Android device and use:
```bash
buildozer android deploy run logcat
```

This will show Python errors and print statements in real-time.

## Troubleshooting

### Build Issues

**Problem**: Buildozer fails to download SDK/NDK
**Solution**: Check your internet connection and try again. The first build downloads ~2GB.

**Problem**: "No module named 'Cython'"
**Solution**: `pip install cython`

**Problem**: Java errors
**Solution**: Ensure you have OpenJDK 11 installed: `sudo apt install openjdk-11-jdk`

### Runtime Issues

**Problem**: App crashes on start
**Solution**: Check logcat for Python errors. Ensure device has Android 5.0+

**Problem**: No sound
**Solution**: Check device volume, ensure neither ear is muted

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
