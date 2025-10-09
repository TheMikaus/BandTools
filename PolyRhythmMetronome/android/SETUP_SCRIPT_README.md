# Android Development Setup Script

This directory contains `setup_android_dev.py`, an automated script to check and install all dependencies needed for building the PolyRhythmMetronome Android app.

## Quick Start

```bash
cd PolyRhythmMetronome/android
sudo python3 setup_android_dev.py
```

## What It Does

The script automatically:

1. ✓ Checks Python version (requires 3.8+)
2. ✓ Verifies pip is available
3. ✓ Installs buildozer (Android build tool)
4. ✓ Installs Cython (Python to C compiler)
5. ✓ Checks/installs OpenJDK 11+ (Java runtime)
6. ✓ Installs system build dependencies:
   - git, zip, unzip
   - autoconf, libtool, pkg-config
   - zlib, ncurses, libffi, openssl development libraries
   - cmake

## Supported Platforms

- **Ubuntu/Debian**: Full automatic installation with sudo
- **macOS**: Manual instructions provided
- **Fedora/RHEL**: Manual instructions provided
- **Windows**: Not recommended (use WSL2 instead)

## Usage Examples

### First Time Setup (Ubuntu)
```bash
# With sudo for system packages
sudo python3 setup_android_dev.py
```

### Check Status Without Installing
```bash
# Run without sudo to see what's missing
python3 setup_android_dev.py
```

### After Setup
```bash
# Add buildozer to PATH (if needed)
export PATH="$HOME/.local/bin:$PATH"

# Verify buildozer is available
buildozer --version

# Build the APK
buildozer -v android debug
```

## What Gets Installed

### Python Packages (via pip)
- `buildozer` - Android APK build tool
- `cython` - Python to C compiler

### System Packages (Ubuntu/Debian)
- `openjdk-11-jdk` - Java Development Kit
- `git` - Version control
- `zip`, `unzip` - Archive tools
- `autoconf`, `libtool`, `pkg-config` - Build tools
- `zlib1g-dev` - Compression library
- `libncurses-dev`, `libncursesw5-dev` - Terminal UI library
- `cmake` - Build system
- `libffi-dev` - Foreign Function Interface library
- `libssl-dev` - SSL/TLS library

### Downloaded by Buildozer (First Build)
- Android SDK (~2GB)
- Android NDK (~1GB)
- Python-for-Android toolchain
- Kivy, NumPy, and other Python dependencies

## Troubleshooting

### "buildozer command not found"
Add `~/.local/bin` to your PATH:
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### "Root/sudo access required"
Some system packages require sudo:
```bash
sudo python3 setup_android_dev.py
```

### Manual Installation Needed
If the script can't auto-install, it will provide specific commands to run manually.

### Permission Errors
If you get permission errors with pip:
```bash
# Install packages for your user only
pip install --user buildozer cython
```

## First Build Notes

After running the setup script, your first build will:
- Download ~2GB of Android SDK/NDK
- Take 30-60 minutes to complete
- Create build files in `.buildozer` directory

Subsequent builds are much faster (5-10 minutes).

## Verification

After setup completes successfully, you should see:
```
✓ All dependencies are installed!

Next steps:
  1. Navigate to the android directory:
     cd PolyRhythmMetronome/android

  2. Build the APK:
     buildozer -v android debug
```

## Script Output

The script uses colored output:
- ✓ Green checkmarks: Success
- ⚠ Yellow warnings: Action needed
- ✗ Red X: Error/failure
- ℹ Blue info: Information

## For Other Operating Systems

### macOS
```bash
brew install python3 openjdk@11
pip3 install buildozer cython
```

### Fedora/RHEL
```bash
sudo dnf install python3 python3-pip java-11-openjdk-devel
sudo dnf install git zip unzip autoconf libtool pkgconfig cmake
sudo dnf install zlib-devel ncurses-devel libffi-devel openssl-devel
pip3 install --user buildozer cython
```

### Windows (via WSL2)
1. Install WSL2 with Ubuntu
2. Run the setup script in WSL2:
```bash
sudo python3 setup_android_dev.py
```

## Related Documentation

- [README.md](README.md) - Main Android app documentation
- [buildozer.spec](buildozer.spec) - Build configuration
- [../PORTING_SUMMARY.md](../PORTING_SUMMARY.md) - Porting details

## Support

If you encounter issues not covered here, please check:
1. The error messages from the script
2. The [Troubleshooting](#troubleshooting) section above
3. The main BandTools repository issues

## License

Part of the BandTools project.
