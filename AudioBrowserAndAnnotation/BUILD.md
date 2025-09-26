# Building AudioBrowser Executable

This directory contains batch files to build a standalone executable for the AudioBrowser annotation software.

## Automated Builds (Recommended)

**Pre-built executables are automatically created** for every commit and available in the [Releases section](https://github.com/TheMikaus/BandTools/releases). This is the easiest way to get a working executable without setting up a build environment.

The automated CI/CD system builds for:
- Windows (`AudioFolderPlayer-{version}-windows.zip`)  
- Linux (`AudioFolderPlayer-{version}-linux.tar.gz`)
- macOS (`AudioFolderPlayer-{version}-macos.tar.gz`)

## Manual Build (Development)

For development or customization, you can build manually using the scripts below:

## Quick Start

### Windows
1. Open Command Prompt or PowerShell
2. Navigate to the AudioBrowserAndAnnotation directory
3. Run: `build_exe.bat`

### Linux/macOS/Unix
1. Open Terminal
2. Navigate to the AudioBrowserAndAnnotation directory  
3. Make executable: `chmod +x build_exe.sh`
4. Run: `./build_exe.sh`

## Requirements

- Python 3.7 or higher installed and in PATH
- Internet connection (for automatic dependency installation)

## What the build scripts do

1. **Check Dependencies**: Verify Python is installed and install PyInstaller and PyQt6 if needed
2. **Generate Icons**: Create app_icon.png and app_icon.ico files using make_icon.py
3. **Clean Build**: Remove any previous build artifacts  
4. **Build Executable**: Use PyInstaller with the audio_browser.spec configuration to create a standalone executable
5. **Report Results**: Show the location and size of the built executable

## Output

The executable will be created at:
- Windows: `dist\AudioFolderPlayer.exe` 
- Linux/macOS: `dist/AudioFolderPlayer`

The executable is self-contained and can be distributed without requiring Python or other dependencies on the target system.

## Troubleshooting

- **Python not found**: Install Python 3.7+ and ensure it's in your system PATH
- **Build fails**: Check that you have write permissions in the directory and sufficient disk space
- **Icon generation fails**: The build will continue without icons if make_icon.py fails
- **Missing libraries**: On Linux, you may need to install additional system packages for Qt graphics support

## File Structure After Build

```
AudioBrowserAndAnnotation/
├── audio_browser.py          # Main application
├── audio_browser.spec        # PyInstaller specification  
├── make_icon.py             # Icon generation script
├── build_exe.bat            # Windows build script
├── build_exe.sh             # Cross-platform build script
├── app_icon.png             # Generated app icon (PNG)
├── app_icon.ico             # Generated app icon (ICO)  
├── build/                   # Build artifacts (can be deleted)
└── dist/                    # Final executable location
    └── AudioFolderPlayer    # The built executable
```

## Notes

- The executable size is typically 100MB+ due to bundling Python and Qt libraries
- First build may take several minutes to download and install dependencies
- Subsequent builds are faster as dependencies are cached
- The build scripts work on Windows, Linux, and macOS

## Automated CI/CD System

This repository includes a GitHub Actions workflow that automatically builds executables on every commit to main/develop branches. The workflow:

- **Builds for multiple platforms**: Windows, Linux, and macOS simultaneously
- **Creates releases**: Automatically publishes releases with downloadable archives  
- **Version management**: Uses git commit count for automatic version numbering
- **Artifact storage**: Keeps build artifacts for 30 days, release archives permanently

See [../.github/CI_CD_SETUP.md](../.github/CI_CD_SETUP.md) for detailed information about the automated build system.

**For end users**: Download pre-built executables from the [Releases page](https://github.com/TheMikaus/BandTools/releases) instead of building manually.