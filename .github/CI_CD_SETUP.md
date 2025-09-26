# AudioBrowser CI/CD Setup

This document describes the GitHub Actions setup for automatically building and releasing the AudioBrowser application.

## Workflow Overview

The build system is configured in `.github/workflows/build-audiobrowser.yml` and provides:

1. **Automated Building**: Builds AudioBrowser executable on every commit to main/develop branches
2. **Windows-Only Support**: Currently builds Windows executable only (as requested)
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

### 1. Windows Build
```yaml
jobs:
  build-windows:
    runs-on: windows-latest
```
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

## Where Built Executables Are Stored

**Important**: GitHub Actions builds do NOT commit executables back to the repository. The executables are stored in GitHub's artifact and release systems:

### 1. GitHub Artifacts (All Builds)
- **Location**: Repository → Actions tab → Select workflow run → Artifacts section
- **Retention**: 30 days
- **Format**: Raw executable files
- **Names**: `AudioFolderPlayer-{version}-{platform}`
- **Access**: Available for all builds (including pull requests)

### 2. GitHub Releases (Main Branch Only)
- **Location**: Repository → Releases section 
- **Retention**: Permanent
- **Format**: Compressed archives with executables
- **Names**: 
  - Windows: `AudioFolderPlayer-{version}-windows.zip`
  - Linux: `AudioFolderPlayer-{version}-linux.tar.gz`
  - macOS: `AudioFolderPlayer-{version}-macos.tar.gz`
- **Access**: Public downloads for end users

### 3. Build Process (Temporary)
During the build process, the executable is created at:
- `AudioBrowserAndAnnotation/dist/AudioFolderPlayer.exe` (Windows)
- `AudioBrowserAndAnnotation/dist/AudioFolderPlayer` (Linux/macOS)

However, the `dist/` directory is cleaned at the start of each build and never committed to the repository.

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

## Frequently Asked Questions

### Q: Where is the executable after GitHub Actions builds?

**A: The executable is NOT in the repository's `dist/` folder.** GitHub Actions builds are designed to produce downloadable artifacts and releases, not to modify the repository.

**To find your built executable:**

1. **For any build** (including pull requests):
   - Go to: Repository → Actions tab
   - Click on the workflow run you're interested in
   - Scroll down to "Artifacts" section
   - Download `AudioFolderPlayer-{version}-windows` (or other platform)

2. **For main branch builds** (permanent releases):
   - Go to: Repository → Releases section  
   - Download the latest release archive
   - Extract and run the executable

### Q: Why isn't the executable committed to the repository?

**A: By design.** Committing large binary executables (100MB+) to version control is not recommended because:
- It bloats the repository size significantly
- Binary files don't diff well in version control
- It's unnecessary when GitHub provides artifact and release storage
- Users typically only need the latest executable, not the entire history

### Q: Can I get the executable from the `dist/` folder?

**A: Only for local builds.** When you run `build_exe.bat` or `build_exe.sh` locally, the executable appears in your local `dist/` folder. However, GitHub Actions builds clean this directory and never commit it.

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