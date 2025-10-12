# Building Android APKs with GitHub Actions (Windows Users Guide)

This guide explains how Windows users can build Android APKs without setting up WSL2, Docker, or a Linux VM, using GitHub Actions instead.

## Overview

GitHub Actions is a free CI/CD service that runs builds in the cloud on Linux servers. This is perfect for Windows users who want to build Android APKs without installing Linux locally.

## Advantages

✓ **No local setup required** - Build in the cloud
✓ **Free for public repositories** - GitHub provides free build minutes
✓ **Automated builds** - APKs built automatically on every commit
✓ **Consistent environment** - Same build environment every time
✓ **Easy distribution** - Download APKs from GitHub Releases

## Prerequisites

- A GitHub account
- Fork of the BandTools repository

## Step-by-Step Guide

### Step 1: Fork the Repository

1. Go to https://github.com/TheMikaus/BandTools
2. Click the "Fork" button in the top right
3. This creates your own copy of the repository

### Step 2: Create a GitHub Actions Workflow

Create a new file in your fork at `.github/workflows/build-android-apk.yml`:

```yaml
name: Build Android APK

on:
  push:
    branches: [ main ]
    paths:
      - 'PolyRhythmMetronome/android/**'
  pull_request:
    branches: [ main ]
    paths:
      - 'PolyRhythmMetronome/android/**'
  workflow_dispatch:  # Allow manual trigger

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install system dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y openjdk-11-jdk git zip unzip autoconf libtool pkg-config
        sudo apt-get install -y zlib1g-dev libncurses-dev cmake libffi-dev libssl-dev
    
    - name: Install Python dependencies
      run: |
        pip install buildozer cython
    
    - name: Build APK with Buildozer
      working-directory: PolyRhythmMetronome/android
      run: |
        buildozer -v android debug
    
    - name: Upload APK artifact
      uses: actions/upload-artifact@v3
      with:
        name: polyrhythm-metronome-apk
        path: PolyRhythmMetronome/android/bin/*.apk
        retention-days: 30
```

### Step 3: Enable GitHub Actions

1. Go to your forked repository on GitHub
2. Click "Actions" tab
3. If prompted, click "I understand my workflows, go ahead and enable them"

### Step 4: Trigger a Build

**Option A: Push a Commit**
- Any commit to the `main` branch that modifies files in `PolyRhythmMetronome/android/` will trigger a build

**Option B: Manual Trigger**
1. Go to "Actions" tab
2. Select "Build Android APK" workflow
3. Click "Run workflow"
4. Select branch and click "Run workflow"

### Step 5: Download Your APK

1. Go to "Actions" tab in your repository
2. Click on the latest workflow run
3. Scroll down to "Artifacts"
4. Download "polyrhythm-metronome-apk"
5. Extract the ZIP file to get your APK

## Creating Releases

For easier distribution, you can create releases with attached APKs:

### Automated Release on Tag

Add this to your workflow file to automatically create releases:

```yaml
    - name: Create Release
      if: startsWith(github.ref, 'refs/tags/v')
      uses: softprops/action-gh-release@v1
      with:
        files: PolyRhythmMetronome/android/bin/*.apk
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

Then create a tag and push it:
```bash
git tag v1.0.0
git push origin v1.0.0
```

The APK will be attached to the GitHub Release automatically.

## Troubleshooting

### Build Fails - First Build

The first build can take 30-60 minutes because Buildozer downloads:
- Android SDK (~2GB)
- Android NDK (~1GB)
- Python-for-Android toolchain

**Solution**: GitHub Actions has a 6-hour timeout, so this should complete. Just be patient.

### Build Fails - Out of Disk Space

Buildozer builds require significant disk space (~5GB).

**Solution**: Add a cleanup step before building:
```yaml
    - name: Free disk space
      run: |
        sudo rm -rf /usr/share/dotnet
        sudo rm -rf /opt/ghc
        sudo rm -rf "/usr/local/share/boost"
        sudo rm -rf "$AGENT_TOOLSDIRECTORY"
```

### Build Fails - Timeout

If builds consistently timeout, you may need to cache dependencies.

**Solution**: Add caching to your workflow:
```yaml
    - name: Cache Buildozer
      uses: actions/cache@v3
      with:
        path: ~/.buildozer
        key: ${{ runner.os }}-buildozer-${{ hashFiles('**/buildozer.spec') }}
```

### APK Not Found

If the APK upload step fails, check the build logs to see where the APK was created.

**Solution**: Update the path in the upload step:
```yaml
        path: PolyRhythmMetronome/android/bin/*.apk
```

### Build Fails - "chown: invalid user: 'user'"

This error occurs when using older versions of the `ArtemSBulgakov/buildozer-action` that have a bug with file ownership.

**Solution**: Use manual buildozer installation instead of the action (already implemented in the repository):
```yaml
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install system dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y openjdk-11-jdk git zip unzip autoconf libtool pkg-config
        sudo apt-get install -y zlib1g-dev libncurses-dev cmake libffi-dev libssl-dev
    
    - name: Install Python dependencies
      run: |
        pip install buildozer cython
    
    - name: Build with Buildozer
      working-directory: PolyRhythmMetronome/android
      run: |
        buildozer -v android debug
```

## Alternative: Use GitHub Codespaces

If you want an interactive development environment:

1. Go to your forked repository
2. Click "Code" → "Codespaces" → "Create codespace on main"
3. Wait for the environment to load (Linux with VS Code in browser)
4. Open a terminal and run:
   ```bash
   cd PolyRhythmMetronome/android
   sudo python3 setup_android_dev.py
   buildozer -v android debug
   ```

This gives you a full Linux environment in your browser, no local setup needed!

## Cost Considerations

- **Public repositories**: Free unlimited minutes on GitHub Actions
- **Private repositories**: 2,000 free minutes per month, then $0.008 per minute
- **GitHub Codespaces**: 60 hours free per month for personal accounts

For most users building occasionally, the free tier is more than sufficient.

## Comparison with Local Builds

| Aspect | Local Build (WSL2/Docker) | GitHub Actions |
|--------|---------------------------|----------------|
| Setup time | 30-60 minutes | 5 minutes |
| Disk space | 5-10 GB on your PC | 0 GB (cloud-based) |
| Build time | 30-60 min (first), 5-10 min (subsequent) | 30-60 min every time* |
| Cost | Free | Free for public repos |
| Convenience | Build anytime offline | Need internet connection |
| Distribution | Manual transfer | Automatic via GitHub |

*Can be reduced with caching to 10-15 minutes

## Conclusion

For Windows users who just want to build APKs occasionally, GitHub Actions is the easiest option. You get:
- No local Linux setup required
- Automated builds on every commit
- Easy APK distribution via GitHub Releases
- Free for public repositories

For frequent development and testing, WSL2 or Docker may be more convenient as subsequent builds are much faster.

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Buildozer Documentation](https://buildozer.readthedocs.io/)
- [GitHub Codespaces](https://github.com/features/codespaces)

## Support

If you encounter issues, check:
1. The GitHub Actions logs for error messages
2. The [Troubleshooting](#troubleshooting) section above
3. The main BandTools repository issues
