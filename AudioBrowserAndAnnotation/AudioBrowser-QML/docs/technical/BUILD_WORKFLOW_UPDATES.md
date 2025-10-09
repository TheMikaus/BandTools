# Build Workflow Updates - December 2024

## Overview

Updated the GitHub Actions build workflow to reflect the recent repository reorganization where the original AudioBrowser application was moved to the `AudioBrowserOrig` subdirectory, and added support for building the new QML version.

## Changes Made

### 1. Updated AudioBrowser Original Build Job

**Job renamed**: `build-windows` → `build-audiobrowser-orig-windows`

**Path updates**: All commands now use `AudioBrowserAndAnnotation/AudioBrowserOrig` instead of `AudioBrowserAndAnnotation`

**Archive improvements**:
- Archive now includes:
  - Executable: `AudioAnnotationBrowser.exe`
  - Documentation: `README_ORIG.md` (renamed to `README.md` in archive)
  - Full docs directory with user guides, technical docs, and test plans
- Archive name changed to: `AudioAnnotationBrowser-Orig-{version}-windows.zip`

**Steps affected**:
- Get version information
- Generate application icon
- Verify build prerequisites
- Clean previous builds
- Build executable with PyInstaller
- Verify build
- Create Windows archive
- Upload build artifact
- Create Release

### 2. Added AudioBrowser QML Build Job

**New job**: `build-audiobrowser-qml-windows`

**Created new file**: `AudioBrowserAndAnnotation/AudioBrowser-QML/audiobrowser_qml.spec`
- PyInstaller specification for QML version
- Includes QML files, backend modules, documentation, and README
- Generates executable: `AudioBrowser-QML.exe`

**Build process**:
1. Checkout repository with full history
2. Set up Python 3.11
3. Get version information (from AudioBrowserOrig/version.py)
4. Install PyInstaller and PyQt6 dependencies
5. Verify build prerequisites (main.py, spec file, backend/, qml/, docs/)
6. Clean previous builds
7. Build executable with PyInstaller
8. Verify build
9. Create archive with executable, README.md, and docs
10. Upload artifact
11. Create release (on main branch or manual trigger)

**Archive contents**:
- Executable: `AudioBrowser-QML.exe`
- Documentation: `README.md`
- Full docs directory
- Archive name: `AudioBrowser-QML-{version}-windows.zip`

### 3. Release Management

Both jobs create separate releases:
- **Original version**: Tag `audiobrowser-v{version}`, includes Original build
- **QML version**: Tag `audiobrowser-qml-v{version}`, includes QML build

Each release includes:
- Executable packaged with README and documentation
- Version information
- Build number and commit hash
- Installation instructions

## Files Modified

1. `.github/workflows/build-audiobrowser.yml`
   - Updated all paths for original version
   - Added new QML build job
   - Improved archive creation to include documentation

2. `AudioBrowserAndAnnotation/AudioBrowser-QML/audiobrowser_qml.spec` (NEW)
   - PyInstaller specification for QML version
   - Includes all necessary files for standalone executable

## Testing

The workflow will be automatically triggered on:
- Push to `main` or `develop` branches that affect `AudioBrowserAndAnnotation/**`
- Pull requests to `main` or `develop` branches
- Manual workflow dispatch

Artifacts are uploaded to GitHub Actions with 30-day retention.
Releases are created automatically on main branch builds.

## Version Management

Both builds use the same version number from `AudioBrowserOrig/version.py`, which uses the automatic versioning system based on git commit count.

## Documentation Inclusion

Both packages now include complete documentation:
- README files (README_ORIG.md for Original, README.md for QML)
- User guides
- Technical documentation
- Test plans

This ensures users have access to all help documentation directly in the downloaded archive.

---

**Date**: December 2024  
**Status**: ✅ Complete  
**Related Files**: 
- `.github/workflows/build-audiobrowser.yml`
- `AudioBrowserAndAnnotation/AudioBrowser-QML/audiobrowser_qml.spec`
