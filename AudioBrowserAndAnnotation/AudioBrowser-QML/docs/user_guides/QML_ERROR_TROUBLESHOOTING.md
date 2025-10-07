# QML Loading Error Troubleshooting Guide

## Common QML Compilation Errors

This guide helps you troubleshoot and resolve QML compilation errors in AudioBrowser-QML.

### Error Symptoms

If you see errors like:
```
qt.qml.invalidOverride: file:///path/to/ProgressDialog.qml:38:12: Duplicate signal name
QQmlApplicationEngine failed to load component
Type LibraryTab unavailable
Cannot assign to non-existent property "info"
```

## Quick Fix Verification

### Step 1: Run the Validation Script

```bash
cd AudioBrowser-QML
python3 validate_qml_fixes.py
```

**Expected Output:**
```
✓ All validation checks passed!

The QML errors should now be fixed:
  ✓ Removed duplicate 'signal closed()' from ProgressDialog
  ✓ Added 'info' property to StyledButton
  ✓ StyledButton properly styled with Theme.accentInfo
  ✓ LibraryTab can now use 'info: true'
```

### Step 2: Clear QML Cache

If validation passes but you still see errors, clear any cached QML files:

**On Windows:**
```cmd
# Clear local cache
del /s /q %TEMP%\*.qmlc
del /s /q %LOCALAPPDATA%\BandTools\*.qmlc

# Clear project cache
cd AudioBrowser-QML
del /s /q .qmlcache
```

**On Linux/macOS:**
```bash
# Clear local cache
rm -rf ~/.cache/BandTools/*.qmlc
rm -rf /tmp/*.qmlc

# Clear project cache
cd AudioBrowser-QML
rm -rf .qmlcache
```

### Step 3: Verify File Contents

**Check ProgressDialog.qml:**
```bash
grep -n "signal closed" qml/dialogs/ProgressDialog.qml
```

**Expected:** No output (signal should not exist)

**Check StyledButton.qml:**
```bash
grep -n "property bool info" qml/components/StyledButton.qml
```

**Expected:** Should show line 35 with `property bool info: false`

## Common Issues and Solutions

### Issue 1: Old Version of Files

**Problem:** You're running an older version of the code.

**Solution:**
1. Pull the latest changes from the repository:
   ```bash
   git pull origin main
   ```

2. Verify you're on the correct branch/tag:
   ```bash
   git status
   git log --oneline -3
   ```

### Issue 2: Local Modifications

**Problem:** You have local changes that reintroduced the bugs.

**Solution:**
1. Check for modifications:
   ```bash
   git status
   git diff
   ```

2. If you see unexpected changes in QML files, revert them:
   ```bash
   git checkout qml/dialogs/ProgressDialog.qml
   git checkout qml/components/StyledButton.qml
   ```

### Issue 3: PyQt6/Qt Version Issues

**Problem:** Your Qt/PyQt6 version has different behavior.

**Solution:**
1. Check your PyQt6 version:
   ```bash
   python3 -c "from PyQt6.QtCore import QT_VERSION_STR; print(QT_VERSION_STR)"
   ```

2. Upgrade to the latest PyQt6:
   ```bash
   pip install --upgrade PyQt6
   ```

### Issue 4: Wrong Working Directory

**Problem:** Running from a different location than expected.

**Solution:**
Make sure you're in the correct directory:
```bash
cd AudioBrowserAndAnnotation/AudioBrowser-QML
python3 main.py
```

## Manual Verification

If automatic validation isn't working, manually verify the fixes:

### ProgressDialog.qml Line 35-40

**Should look like:**
```qml
// ========== Signals ==========

signal cancelRequested()

// ========== Dialog Configuration ==========
```

**Should NOT have:**
```qml
signal closed()  // ❌ This should NOT be here
```

### StyledButton.qml Line 31-36

**Should look like:**
```qml
// Custom properties
property bool primary: false
property bool danger: false
property bool success: false
property bool info: false  // ✅ This MUST be here
```

## Testing After Fix

1. **Start the application:**
   ```bash
   python3 main.py
   ```

2. **Verify startup messages:**
   ```
   Installing pydub...
   Requirement already satisfied: pydub...
   qt.multimedia.ffmpeg: Using Qt multimedia with FFmpeg...
   Loading QML file: .../qml/main.qml
   AudioBrowser QML Phase 7 - Application started successfully
   ```

3. **Check the Library tab:**
   - Navigate to the "Library" tab
   - Verify buttons are visible and styled correctly
   - "Batch Rename" button should be light blue (info style)

## Still Having Issues?

If you've tried all the above steps and still encounter errors:

### Collect Debug Information

1. **Run with verbose output:**
   ```bash
   QT_LOGGING_RULES="*.debug=true" python3 main.py 2>&1 | tee debug.log
   ```

2. **Check Python path and imports:**
   ```bash
   python3 -c "import sys; print('\\n'.join(sys.path))"
   python3 -c "from PyQt6 import QtCore; print(QtCore.PYQT_VERSION_STR)"
   ```

3. **Run QML syntax test (requires GUI environment):**
   ```bash
   python3 test_qml_syntax.py
   ```

### Report the Issue

Include the following in your bug report:
- Output from `validate_qml_fixes.py`
- Python version: `python3 --version`
- PyQt6 version: `pip show PyQt6`
- Operating system and version
- Full error message from console
- Contents of debug.log
- Git commit hash: `git rev-parse HEAD`

## Related Documentation

- [QML_COMPILATION_FIX.md](../QML_COMPILATION_FIX.md) - Technical details of the fixes
- [STYLED_BUTTON_VARIANTS.md](../STYLED_BUTTON_VARIANTS.md) - Button styling reference
- [DEVELOPER_GUIDE.md](../technical/DEVELOPER_GUIDE.md) - Developer documentation
- [TESTING_GUIDE.md](../technical/TESTING_GUIDE.md) - Testing procedures

## Prevention Tips

To avoid similar issues in the future:

1. **Don't override built-in signals** - Check Qt documentation before adding signals
2. **Define properties before use** - Always declare properties before using them in child components
3. **Use the validation script** - Run `validate_qml_fixes.py` before committing changes
4. **Test QML changes** - Use `test_qml_syntax.py` to catch errors early
5. **Keep PyQt6 updated** - Newer versions may provide better error messages

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python3 validate_qml_fixes.py` | Verify fixes are in place |
| `python3 test_qml_syntax.py` | Test QML syntax (GUI required) |
| `python3 main.py` | Start the application |
| `git status` | Check for local modifications |
| `git diff qml/` | See QML file changes |
| `pip show PyQt6` | Check PyQt6 version |

## Success Indicators

You'll know everything is working when:
- ✅ Validation script shows all checks passing
- ✅ Application starts without QML errors
- ✅ Library tab displays correctly
- ✅ Info-styled buttons are visible and functional
- ✅ No error messages in console about signals or properties
