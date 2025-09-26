# AudioBrowser CI/CD Setup

This document describes the GitHub Actions setup for automatically building and releasing the AudioBrowser application.

## Workflow Overview

The build system is configured in `.github/workflows/build-audiobrowser.yml` and provides:

1. **Automated Building**: Builds AudioBrowser executable on every commit to main/develop branches
2. **Multi-Platform Support**: Creates executables for Windows, Linux, and macOS
3. **Artifact Storage**: Stores built executables as GitHub artifacts
4. **Automatic Releases**: Creates releases with downloadable packages
5. **Version Management**: Uses the existing git-based version system

## Triggering Builds

### Automatic Triggers
- **Push to main/develop**: Builds executables and creates release
- **Pull Request**: Builds executables for testing (no release)
- **Changes to AudioBrowserAndAnnotation**: Only builds if relevant files change

### Manual Triggers
- **Workflow Dispatch**: Manual trigger from GitHub Actions tab
- **Create Release Option**: Check "Create a release after build" for immediate release

## Build Process

### 1. Multi-Platform Matrix
```yaml
strategy:
  matrix:
    include:
      - os: ubuntu-latest (Linux)
      - os: windows-latest (Windows) 
      - os: macos-latest (macOS)
```

### 2. Build Steps
1. **Checkout**: Downloads repository with full git history
2. **Python Setup**: Installs Python 3.11
3. **System Dependencies**: Installs Qt libraries (Linux only)
4. **Version Detection**: Reads version from `version.py` 
5. **Dependencies**: Installs PyInstaller and PyQt6
6. **Icon Generation**: Creates app icons using `make_icon.py`
7. **Clean Build**: Removes previous build artifacts
8. **PyInstaller Build**: Builds executable using `audio_browser.spec`
9. **Verification**: Checks executable was created correctly
10. **Artifact Upload**: Stores executable as GitHub artifact

### 3. Release Creation
- **Archives**: Creates platform-specific archives (.zip for Windows, .tar.gz for Linux/macOS)
- **Release Notes**: Auto-generated with version info and download links
- **Assets**: Uploads all platform executables to the release

## Version System Integration

The CI/CD system integrates with the existing version system:

- **Version Format**: `MAJOR.MINOR` (e.g., 1.5)
- **Auto-increment**: Minor version increments with each commit
- **Git Integration**: Uses `git rev-list --count HEAD` for version calculation
- **Release Tags**: Creates tags like `audiobrowser-v1.5`

## File Structure

```
.github/
├── workflows/
│   └── build-audiobrowser.yml    # Main build workflow
└── CI_CD_SETUP.md                # This documentation

AudioBrowserAndAnnotation/
├── audio_browser.py               # Main application
├── audio_browser.spec             # PyInstaller configuration
├── build_exe.sh/.bat             # Local build scripts (still functional)
├── make_icon.py                   # Icon generation
├── version.py                     # Version management
└── ...
```

## Artifacts and Releases

### Build Artifacts (per build)
- **Retention**: 30 days
- **Names**: `AudioFolderPlayer-{version}-{platform}`
- **Content**: Raw executables

### Release Archives (on main branch)
- **Retention**: 90 days for artifacts, permanent for releases  
- **Formats**:
  - Windows: `AudioFolderPlayer-{version}-windows.zip`
  - Linux: `AudioFolderPlayer-{version}-linux.tar.gz`
  - macOS: `AudioFolderPlayer-{version}-macos.tar.gz`

### Release Creation
- **Automatic**: Every push to main branch
- **Manual**: Via workflow dispatch with "Create release" option
- **Tag Format**: `audiobrowser-v{version}`
- **Assets**: All platform archives attached

## System Requirements

### GitHub Repository
- **Actions Enabled**: Repository must have GitHub Actions enabled
- **Token Permissions**: Default `GITHUB_TOKEN` has sufficient permissions
- **Branch Protection**: Works with protected branches

### Build Environment
- **Python 3.11**: Consistent across all platforms
- **PyInstaller**: Latest version installed during build
- **PyQt6**: GUI framework dependency
- **Git**: Full history access for version calculation
- **System Libraries (Linux)**: Updated for Ubuntu 24.04 compatibility
  - EGL and Mesa libraries for Qt rendering
  - XCB libraries for X11 integration
  - PulseAudio and PC/SC Lite libraries for multimedia and NFC support

## Usage Instructions

### For Developers
1. **Regular Development**: Just push to main/develop - builds happen automatically
2. **Testing**: Create PR - builds without release to verify changes
3. **Manual Release**: Use "Actions" tab → "Build AudioBrowser" → "Run workflow"

### For Users
1. **Download**: Go to repository "Releases" section  
2. **Choose Platform**: Download appropriate archive for your OS
3. **Extract**: Unzip/untar the archive
4. **Run**: Execute the `AudioFolderPlayer` executable

## Troubleshooting

### Common Issues

**Build Failures**:
- Check Python/dependency installation logs
- Verify PyInstaller spec file compatibility
- Check system dependencies (especially Linux Qt libraries for Ubuntu 24.04+)
- Ensure all required XCB and Mesa packages are available

**Version Issues**:
- Ensure git history is available (`fetch-depth: 0`)
- Check `version.py` import/execution
- Verify git commands work in build environment

**Release Creation Failures**:
- Check artifact download patterns
- Verify release asset paths
- Check GitHub token permissions
- Ensure archive creation works on all platforms

**Archive Creation Issues**:
- Windows builds use Python's zipfile module (no external dependencies)
- Linux/macOS builds use standard tar command
- Verify executable permissions are preserved in archives

### Local Testing
The existing `build_exe.sh` and `build_exe.bat` scripts still work for local testing:

```bash
cd AudioBrowserAndAnnotation
./build_exe.sh        # Linux/macOS
# or
build_exe.bat         # Windows
```

## Maintenance

### Updating the Workflow
1. **Python Version**: Update `python-version` in setup-python steps
2. **Dependencies**: Modify system package lists as needed for OS updates
3. **PyInstaller**: Version specified in pip install commands
4. **Actions**: Update action versions (checkout@v4, setup-python@v5, etc.)
5. **Release Management**: Uses modern `softprops/action-gh-release@v1` for reliability

### Monitoring
- **Actions Tab**: View build status and logs
- **Releases Page**: Monitor release creation and downloads
- **Artifacts**: Check artifact sizes and retention

## Security Considerations

- **Token Usage**: Uses repository's `GITHUB_TOKEN` (automatic, secure)
- **Dependencies**: Only installs from PyPI (pip)
- **Artifacts**: Stored securely in GitHub infrastructure  
- **Releases**: Public releases match repository visibility

## Future Enhancements

### Potential Improvements
- **Code Signing**: Sign executables for Windows/macOS
- **Notarization**: macOS notarization for better security
- **Testing**: Add automated testing before build
- **Caching**: Cache dependencies for faster builds
- **Notifications**: Slack/Discord notifications for releases
- **Documentation**: Auto-update documentation with builds

### Advanced Features
- **Feature Branches**: Different build configurations per branch
- **Beta Releases**: Separate beta/stable release channels  
- **Update Mechanism**: In-app update notifications
- **Telemetry**: Build success/failure metrics