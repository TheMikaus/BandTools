# Building AudioBrowser Executable

This directory contains batch files to build a standalone executable for the AudioBrowser annotation software.

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