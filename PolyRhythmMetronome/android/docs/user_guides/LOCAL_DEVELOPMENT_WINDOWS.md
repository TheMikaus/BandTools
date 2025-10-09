# Local Development on Windows - Build, Test, and Iterate

This guide explains how to develop and test the PolyRhythmMetronome Android app locally on Windows without relying on cloud builds or complex Linux environments.

## Quick Start: Desktop Testing (Recommended)

The **fastest way** to develop and test on Windows is to run the app directly on your desktop:

### Setup (One-time)

```bash
# Install Python 3.8+ from python.org
# Then install dependencies:
pip install kivy numpy
```

### Run the App

```bash
cd PolyRhythmMetronome/android
python main.py
```

The app will open in a desktop window with full functionality except Android-specific permissions.

### Advantages

✅ **Instant feedback** - No build time, just run  
✅ **Fast iteration** - Edit code and rerun immediately  
✅ **Full debugging** - Use Python debuggers, print statements  
✅ **Works on Windows** - No Linux environment needed  
✅ **Same codebase** - What you test is what runs on Android  

### Limitations

⚠ **No Android permissions** - Storage permissions not tested  
⚠ **Different UI scaling** - Desktop window vs. mobile screen  
⚠ **No touch events** - Mouse clicks instead of touch  

**Best Practice**: Use desktop testing for 90% of development, then test on actual device or emulator for final validation.

---

## Option 2: Local APK Builds with WSL2

For building APKs locally on Windows, WSL2 provides a native Linux environment:

### Initial Setup

1. **Install WSL2** (PowerShell as Administrator):
```powershell
wsl --install
```

2. **Install Ubuntu** from Microsoft Store

3. **Open Ubuntu terminal** and setup:
```bash
# Update packages
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip openjdk-11-jdk git zip unzip
sudo apt install -y autoconf libtool pkg-config zlib1g-dev libncurses-dev
sudo apt install -y cmake libffi-dev libssl-dev

# Install Python packages
pip3 install --user buildozer cython

# Add buildozer to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Building APKs

```bash
# Navigate to project (WSL can access Windows files at /mnt/c/)
cd /mnt/c/Users/YourUsername/path/to/BandTools/PolyRhythmMetronome/android

# First build (downloads SDK/NDK, takes 30-60 minutes)
buildozer -v android debug

# Subsequent builds (5-10 minutes)
buildozer -v android debug
```

### Advantages

✅ **Local builds** - No internet needed after initial setup  
✅ **Fast iteration** - Subsequent builds are quick  
✅ **Full control** - Customize build process  
✅ **Native Windows integration** - Access Windows files  

### Workflow Recommendation

1. **Develop and test on desktop** - Use `python main.py` for rapid iteration
2. **Build APK when ready** - Use WSL2 to create APK
3. **Test on device** - Install APK on Android device/emulator

---

## Option 3: Docker Desktop

If you prefer Docker over WSL2:

### Setup

1. Install Docker Desktop for Windows from docker.com
2. Create a Dockerfile in the project root:

```dockerfile
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip openjdk-11-jdk git zip unzip \
    autoconf libtool pkg-config zlib1g-dev libncurses-dev \
    cmake libffi-dev libssl-dev

# Install Python packages
RUN pip3 install buildozer cython

WORKDIR /app
```

3. Build and run:

```bash
# Build Docker image
docker build -t android-builder .

# Run build in container
docker run -v "%cd%":/app android-builder buildozer -v android debug
```

---

## Option 4: Android Studio with Chaquopy

For a **native Android development** experience using the Android SDK directly:

### Overview

Chaquopy is a plugin that embeds Python in native Android apps. This approach:
- Uses Android Studio (full IDE support on Windows)
- Builds with Gradle (standard Android toolchain)
- No Buildozer or p4a needed

### Setup

1. **Install Android Studio** from developer.android.com
2. **Create new Android project** (Kotlin or Java)
3. **Add Chaquopy plugin** in `build.gradle`:

```gradle
buildscript {
    repositories {
        google()
        mavenCentral()
        maven { url "https://chaquo.com/maven" }
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:8.1.0'
        classpath 'com.chaquo.python:gradle:14.0.2'
    }
}
```

4. **Configure Python** in app's `build.gradle`:

```gradle
plugins {
    id 'com.android.application'
    id 'com.chaquo.python'
}

android {
    defaultConfig {
        python {
            pip {
                install "kivy"
                install "numpy"
            }
        }
    }
}
```

5. **Copy Python code** to `app/src/main/python/`

### Advantages

✅ **Native Android IDE** - Full Android Studio features  
✅ **Standard toolchain** - Uses Gradle, Android SDK  
✅ **Windows native** - No WSL/Docker needed  
✅ **Better debugging** - Android Studio debugger  

### Disadvantages

⚠ **More complex** - Requires Android development knowledge  
⚠ **Different structure** - Not drop-in replacement  
⚠ **Larger APKs** - Includes both Java and Python runtimes  

---

## Option 5: Kivy Launcher (Quick Device Testing)

Test on real Android devices without building APKs:

### Setup

1. **Install Kivy Launcher** from Google Play Store on your Android device
2. **Enable USB debugging** on your device
3. **Connect device** to Windows PC via USB

### Usage

```bash
# Copy app to device
adb push main.py /sdcard/kivy/polyrhythm/main.py

# App automatically appears in Kivy Launcher
# Launch from the Kivy Launcher app
```

Or use network transfer:
1. Put `main.py` in `/sdcard/kivy/yourapp/` on device
2. Launch from Kivy Launcher

### Advantages

✅ **No APK build** - Direct Python execution  
✅ **Fast testing** - Just copy files  
✅ **Real device** - Test on actual hardware  

### Limitations

⚠ **Requires Kivy Launcher** - Must install from Play Store  
⚠ **Limited features** - Can't test custom permissions  
⚠ **Development only** - Not for distribution  

---

## Recommended Workflow for Windows Development

### Phase 1: Development (90% of time)
```
Edit code → python main.py → Test → Repeat
```
Use desktop testing for rapid iteration.

### Phase 2: Device Testing (10% of time)
```
Build APK → Install on device → Test → Fix issues
```
Use WSL2/Docker for local builds, or GitHub Actions for cloud builds.

### Phase 3: Distribution
```
Final build → Sign APK → Distribute
```
Use GitHub Actions for consistent release builds.

---

## Comparison of Methods

| Method | Setup Time | Iteration Speed | Windows Native | Real Android Testing |
|--------|------------|-----------------|----------------|---------------------|
| **Desktop Testing** | 5 min | Instant | ✅ Yes | ❌ No |
| **WSL2 + Buildozer** | 30 min | Fast (5-10 min) | ✅ Yes | ✅ Yes |
| **Docker** | 20 min | Fast (5-10 min) | ✅ Yes | ✅ Yes |
| **Android Studio + Chaquopy** | 60 min | Medium (2-5 min) | ✅ Yes | ✅ Yes |
| **Kivy Launcher** | 5 min | Fast (copy files) | ✅ Yes | ✅ Yes |
| **GitHub Actions** | 10 min | Slow (30-60 min) | ✅ Yes | ⚠️ Manual |

---

## Detailed Example: Desktop Testing Workflow

### 1. Edit the Code

Open `main.py` in your favorite editor (VS Code, PyCharm, etc.):

```python
# Example: Change BPM range
BPM_MIN = 40
BPM_MAX = 240
```

### 2. Run on Desktop

```bash
python main.py
```

The app window opens. Test your changes immediately.

### 3. Debug Issues

Add debug prints:

```python
def on_bpm_change(self, value):
    print(f"DEBUG: BPM changed to {value}")  # Appears in terminal
    self.bpm = value
```

Re-run to see debug output.

### 4. Test on Device (When Ready)

Once feature is working on desktop:

```bash
# In WSL2 terminal
cd /mnt/c/Users/YourName/BandTools/PolyRhythmMetronome/android
buildozer android debug
adb install -r bin/*.apk
```

---

## Troubleshooting

### Desktop Testing Issues

**Problem**: `ModuleNotFoundError: No module named 'kivy'`  
**Solution**: 
```bash
pip install kivy numpy
```

**Problem**: Window is too small/large  
**Solution**: Add to `main.py`:
```python
from kivy.core.window import Window
Window.size = (400, 600)  # Adjust as needed
```

**Problem**: Android-specific code crashes  
**Solution**: Add platform checks:
```python
from kivy.utils import platform

if platform == 'android':
    # Android-specific code
    from android.permissions import request_permissions
else:
    # Desktop fallback
    print("Running on desktop - skipping Android permissions")
```

### WSL2 Issues

**Problem**: Can't access Windows files  
**Solution**: Use `/mnt/c/` path:
```bash
cd /mnt/c/Users/YourName/Documents/BandTools
```

**Problem**: buildozer command not found  
**Solution**: Add to PATH:
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**Problem**: Builds are slow  
**Solution**: 
- First build downloads 2-3 GB (SDK/NDK), subsequent builds are faster
- Use `.buildozer` cache - don't delete this folder

### Android Studio Issues

**Problem**: Gradle sync fails  
**Solution**: Check internet connection, Gradle needs to download dependencies

**Problem**: Python not found  
**Solution**: Ensure Chaquopy plugin is properly configured in `build.gradle`

---

## Performance Comparison

### Build Times (Local Development)

| Method | First Build | Subsequent Builds | Code Change to Running |
|--------|-------------|-------------------|------------------------|
| Desktop Testing | N/A | N/A | **1-2 seconds** |
| WSL2 + Buildozer | 30-60 min | 5-10 min | 5-10 min |
| Docker | 30-60 min | 5-10 min | 5-10 min |
| Android Studio | 10-15 min | 2-5 min | 2-5 min |
| Kivy Launcher | N/A | 10-30 sec | 10-30 sec |

**Recommendation**: Use desktop testing for fastest iteration (1-2 seconds), build APKs only when needed.

---

## Additional Resources

### Official Documentation
- [Kivy Installation](https://kivy.org/doc/stable/gettingstarted/installation.html)
- [Buildozer](https://buildozer.readthedocs.io/)
- [Python-for-Android](https://python-for-android.readthedocs.io/)
- [Chaquopy](https://chaquo.com/chaquopy/)

### Community Resources
- [Kivy Discord](https://chat.kivy.org/)
- [Python-for-Android GitHub](https://github.com/kivy/python-for-android)

### Related Guides in This Project
- [GitHub Actions Build Guide](GITHUB_ACTIONS_BUILD_GUIDE.md) - Cloud builds
- [Quick Start Guide](QUICK_START.md) - Basic usage
- [FAQ](FAQ.md) - Common questions

---

## Summary

**For local Windows development**, the recommended approach is:

1. **Primary development**: Use desktop testing (`python main.py`)
   - Instant feedback, no build required
   - 90% of development can be done this way

2. **APK builds**: Use WSL2 + Buildozer when you need to test on device
   - Fast subsequent builds (5-10 minutes)
   - Full Android environment

3. **Cloud builds**: Use GitHub Actions for releases
   - Consistent build environment
   - No local setup maintenance

This gives you the best of all worlds: fast iteration during development, local control when needed, and automated releases.
