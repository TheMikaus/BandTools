# How to Create a Release

## Overview

As of the latest update, AudioBrowser releases are created **manually** via GitHub Actions workflow dispatch. This gives maintainers full control over when releases are published.

## Automatic Builds (Every Commit)

The GitHub Actions workflow automatically runs on every commit to `main` or `develop` branches that affect the `AudioBrowserAndAnnotation/` directory. These builds:

- ✅ Create build artifacts (30-day retention)
- ✅ Verify the build process works
- ❌ Do NOT create releases

**Build artifacts** are available in the GitHub Actions tab → Workflow run → Artifacts section for 30 days.

## Creating a Release (Manual)

To create a release, follow these steps:

### Step 1: Navigate to Actions

1. Go to the repository on GitHub
2. Click the **Actions** tab
3. Select the **Build AudioBrowser** workflow from the left sidebar

### Step 2: Trigger Workflow Dispatch

1. Click the **Run workflow** dropdown button (top right)
2. Select the branch (typically `main`)
3. **Check the box** for "Create a release after build"
4. Click the green **Run workflow** button

### Step 3: Wait for Build

The workflow will:
1. Build executables for both AudioBrowser Original and QML versions
2. Create archives with documentation
3. Upload build artifacts
4. Create GitHub releases with downloadable files

This typically takes 5-10 minutes.

### Step 4: Verify Release

Once complete:
1. Go to the repository **Releases** section
2. Verify the new release is published
3. Check that the download files are present:
   - `AudioAnnotationBrowser-Orig-{version}-windows.zip`
   - `AudioBrowser-QML-{version}-windows.zip`

## Release Tags

The workflow creates two separate releases:
- **Original version**: Tag `audiobrowser-v{version}`
- **QML version**: Tag `audiobrowser-qml-v{version}`

## Version Numbers

Version numbers are automatically generated from the git commit count:
- Format: `MAJOR.MINOR`
- MAJOR: Manually set in `version.py` (currently 1)
- MINOR: Automatically incremented with each commit

## Troubleshooting

### Build Fails
- Check the Actions tab for error logs
- Ensure all required files are present in the repository
- Verify Python dependencies can be installed

### Release Not Created
- Ensure you checked "Create a release after build" when triggering
- Check that the build completed successfully
- Verify you have write permissions to the repository

### Wrong Version Number
- Version is based on git commit count
- To change the major version, edit `AudioBrowserAndAnnotation/AudioBrowserOrig/version.py`

## Benefits of Manual Releases

- **Control**: Release only when ready, not on every commit
- **Quality**: Test builds via artifacts before publishing
- **Flexibility**: Create releases at your own pace
- **Clean**: Avoid cluttering releases with development builds
