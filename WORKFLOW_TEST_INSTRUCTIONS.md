# Testing the APK Build Workflow

## What Was Fixed

The GitHub Actions workflow for building the PolyRhythmMetronome APK had a permission error caused by an incorrect `sudo chown -R 1000:1000 .` command. This has been fixed by:

1. **Removed the problematic chown command** - The buildozer-action container handles permissions internally
2. **Removed sudo usage** - Not needed for directory creation and chmod
3. **Simplified permission handling** - Using `chmod 777` on necessary directories for container access

## How to Test the Fixed Workflow

### Option 1: Manual Trigger via GitHub UI (Recommended)

1. **Go to the Actions tab** in your GitHub repository:
   ```
   https://github.com/TheMikaus/BandTools/actions
   ```

2. **Select the workflow**:
   - Click on "Build PolyRhythmMetronome APK" in the left sidebar

3. **Run the workflow**:
   - Click the "Run workflow" dropdown button (top right)
   - Select branch: `copilot/fix-chown-invalid-user-error`
   - Leave default settings:
     - Target: `android debug`
     - Spec path: `./PolyRhythmMetronome/android/buildozer.spec`
     - Clean: `false`
     - Create release: `false`
   - Click "Run workflow" button

4. **Monitor the build**:
   - Click on the workflow run that appears
   - Watch the build progress (first build takes 30-60 minutes)
   - Check for any errors

5. **Download the APK** (if successful):
   - Scroll to the "Artifacts" section at the bottom
   - Download "android-build"
   - Extract and test the APK

### Option 2: Push a Commit (Automatic Trigger)

The workflow is configured to run on `workflow_dispatch` only, so it won't trigger automatically on push. If you want automatic builds, you'd need to add:

```yaml
on:
  push:
    branches: [ main, copilot/* ]
    paths:
      - 'PolyRhythmMetronome/android/**'
  workflow_dispatch:
    ...
```

### Option 3: Using GitHub CLI (Command Line)

If you have `gh` CLI installed and authenticated:

```bash
gh workflow run "Build PolyRhythmMetronome APK" \
  --ref copilot/fix-chown-invalid-user-error \
  -f target="android debug" \
  -f spec_path="./PolyRhythmMetronome/android/buildozer.spec" \
  -f clean="false" \
  -f create_release="false"
```

Then watch the run:
```bash
gh run watch
```

## Expected Results

### Successful Build

The workflow should:
1. ✅ Checkout the code
2. ✅ Prep cache directories (without permission errors)
3. ✅ Restore cached buildozer files (if available)
4. ✅ Build APK using buildozer-action
5. ✅ Upload APK as artifact
6. ✅ Complete in 30-60 minutes (first build) or 10-20 minutes (cached builds)

### Common Issues (Now Fixed)

- ❌ ~~`chown: invalid user: 'user'`~~ - **FIXED**: Removed chown command
- ❌ ~~Permission denied errors~~ - **FIXED**: Using chmod 777 for container access
- ❌ ~~`buildozer android clean` fails~~ - **FIXED**: Removed from clean step

## Changes Made to Workflow

**File**: `.github/workflows/build-polyrhythm-apk.yml`

### Before (Problematic)
```yaml
- name: Fix permissions for buildozer user
  run: |
    sudo chown -R 1000:1000 .

- name: Prep cache dirs (permissive perms)
  run: |
    sudo mkdir -p "${HOME}/.buildozer" ".buildozer" "PolyRhythmMetronome/android/bin"
    sudo chmod -R a+rwx "${HOME}/.buildozer" ".buildozer" "PolyRhythmMetronome/android/bin"
```

### After (Fixed)
```yaml
- name: Prep cache dirs
  run: |
    mkdir -p "${HOME}/.buildozer" ".buildozer" "PolyRhythmMetronome/android/bin"
    chmod -R 777 "${HOME}/.buildozer" ".buildozer" "PolyRhythmMetronome/android/bin"
```

Also removed `buildozer android clean` from the optional clean step since buildozer can only run inside the container.

## Verification Checklist

After running the workflow, verify:

- [ ] Workflow starts without errors
- [ ] No permission errors appear in logs
- [ ] Buildozer action completes successfully
- [ ] APK artifact is created and uploadable
- [ ] APK can be downloaded from artifacts
- [ ] APK is installable on Android device (optional)

## Next Steps

Once verified working:
1. Merge this branch to main
2. Update documentation if needed
3. Consider adding automatic builds on push (optional)
4. Set up release builds for tagged versions (optional)
