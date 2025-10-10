# Android Development Setup Script

This directory contains `setup_android_dev.py`, an automated script to check and install all dependencies needed for building the PolyRhythmMetronome Android app.

> **📢 Windows Users**: 
> - **For development/testing**: Run the app on desktop with `python main.py` (no build needed!)
> - **For building APKs**: Use [GitHub Actions](docs/user_guides/GITHUB_ACTIONS_BUILD_GUIDE.md) (cloud builds) or WSL2 (local builds)
> - See [Local Development on Windows](docs/user_guides/LOCAL_DEVELOPMENT_WINDOWS.md) for complete guide

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
7. ✓ **On Windows**: Checks for WSL and Ubuntu, provides guided installation instructions

## Supported Platforms

- **Ubuntu/Debian**: Full automatic installation with sudo
- **WSL (Windows Subsystem for Linux)**: Full support with Ubuntu
- **macOS**: Manual instructions provided
- **Fedora/RHEL**: Manual instructions provided
- **Windows**: Automatic WSL and Ubuntu installation checks (with guided instructions)

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

### Windows

**Automatic WSL/Ubuntu Check (New!)**

The setup script now automatically checks for and guides you through WSL and Ubuntu installation:

```powershell
# Run the script on Windows - it will check for WSL and Ubuntu
python3 setup_android_dev.py
```

The script will:
1. ✓ Detect if WSL is installed
2. ✓ Check if Ubuntu is available in WSL
3. ✓ Provide step-by-step instructions to install missing components
4. ✓ Guide you to complete setup in Ubuntu terminal

**Option 1: WSL2 (Recommended for Local Builds)**

After running the setup script and following its instructions:
1. Install WSL2: `wsl --install` (if not already installed)
2. Install Ubuntu from Microsoft Store (if not already installed)
3. Open Ubuntu and run: `sudo python3 setup_android_dev.py`

**Option 2: GitHub Actions (For Cloud Builds)**

For Windows users who prefer not to set up WSL:
1. Fork the BandTools repository on GitHub
2. Create a GitHub Actions workflow to build the APK automatically
3. Download built APKs from GitHub Releases or Actions artifacts
4. No local setup required!

**Option 3: Docker or Linux VM**

Use Docker Desktop or a virtual machine (VirtualBox, VMware) with Ubuntu, then run the setup script inside.

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
