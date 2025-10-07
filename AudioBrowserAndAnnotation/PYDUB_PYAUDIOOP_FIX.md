# Pydub pyaudioop Import Error Fix

## Problem

When running AudioBrowser applications on Python 3.13+, the following error occurred:

```
WARNING: Failed to import pydub: No module named 'pyaudioop'
ERROR: Successfully installed pydub but still cannot import pydub: No module named 'pyaudioop'
```

### Root Cause

1. **Python 3.13+ removed the `audioop` module** - This module was deprecated in Python 3.11 and removed in Python 3.13.

2. **pydub depends on audioop** - The pydub library uses the `audioop` module for audio sample format conversion. In its `utils.py` file, it attempts to import:
   ```python
   try:
       import audioop
   except ImportError:
       import pyaudioop as audioop
   ```

3. **`pyaudioop` doesn't exist as a standalone package** - When `audioop` is not available, pydub tries to import `pyaudioop`, which is not a real PyPI package, causing the import to fail.

## Solution

Modified the `_ensure_import()` function in all affected files to detect when pydub fails to import due to the missing `audioop`/`pyaudioop` module on Python 3.13+, and automatically install the `audioop-lts` package.

The `audioop-lts` package is a maintained long-term support version of the deprecated `audioop` module, specifically designed for Python 3.13+.

### Implementation

Added special handling in the `_ensure_import()` function:

```python
except ImportError as e:
    # Special handling for pydub: if it fails with pyaudioop error on Python 3.13+,
    # install audioop-lts which provides the missing audioop module
    if mod_name == "pydub" and "pyaudioop" in str(e) and sys.version_info >= (3, 13):
        print(f"WARNING: pydub requires audioop module (removed in Python 3.13+). Installing audioop-lts...", file=sys.stderr)
        try:
            # Try to install audioop-lts
            for args in ([sys.executable, "-m", "pip", "install", "audioop-lts"],
                         [sys.executable, "-m", "pip", "install", "--user", "audioop-lts"]):
                try:
                    subprocess.check_call(args)
                    break
                except subprocess.CalledProcessError:
                    continue
            
            # Try importing pydub again
            importlib.import_module(mod_name)  # or __import__(mod_name)
            print(f"SUCCESS: {mod_name} now works with audioop-lts", file=sys.stderr)
            return True, ""
        except Exception as audioop_error:
            error_msg = f"Successfully installed {pkg} but still cannot import {mod_name}: {e}. Also tried installing audioop-lts: {audioop_error}"
            print(f"ERROR: {error_msg}", file=sys.stderr)
            return False, error_msg
```

### Files Modified

1. **AudioBrowserAndAnnotation/AudioBrowserOrig/audio_browser.py**
   - Modified `_ensure_import()` function (lines ~79-110)
   - Added automatic `audioop-lts` installation on Python 3.13+

2. **AudioBrowserAndAnnotation/AudioBrowser-QML/backend/batch_operations.py**
   - Modified `_ensure_import()` function (lines ~57-85)
   - Added automatic `audioop-lts` installation on Python 3.13+

3. **AudioBrowserAndAnnotation/AudioBrowser-QML/main.py**
   - Modified `_ensure_import()` function (lines ~33-61)
   - Added automatic `audioop-lts` installation on Python 3.13+

4. **AudioBrowserAndAnnotation/AudioBrowser-QML/test_qml_syntax.py**
   - Modified `_ensure_import()` function (lines ~30-58)
   - Added automatic `audioop-lts` installation on Python 3.13+

## Behavior

### Python 3.12 and Earlier
- Uses the built-in `audioop` module
- pydub imports successfully without additional packages
- No changes to existing behavior

### Python 3.13 and Later
When pydub is installed but fails to import due to missing audioop:
1. Detects the `pyaudioop` error message
2. Automatically installs `audioop-lts` package
3. Retries the pydub import
4. pydub now works with the `audioop-lts` replacement

## Testing

### Verification
All modified files:
- ✅ Compile successfully without syntax errors
- ✅ Include the fix for automatic audioop-lts installation
- ✅ Maintain backward compatibility with Python 3.12 and earlier
- ✅ Preserve existing return value behavior

### Manual Testing on Python 3.13+
To test on Python 3.13+:
```bash
# Ensure pydub is not installed
python3.13 -m pip uninstall pydub audioop-lts -y

# Run any of the modified applications
python3.13 AudioBrowserOrig/audio_browser.py

# Expected output:
# - pydub installs successfully
# - Initial import fails with pyaudioop error
# - audioop-lts installs automatically
# - pydub imports successfully
```

## Related Issues

This fix complements the existing Python 3.13 compatibility work:
- **PYTHON_313_COMPATIBILITY.md** - Documents the pure Python replacement for `audioop.lin2lin()` used in waveform generation
- **ERROR_LOGGING_IMPROVEMENT.md** - Documents the enhanced error logging in `_ensure_import()`

Both issues stem from Python 3.13's removal of the `audioop` module, but address different use cases:
1. **PYTHON_313_COMPATIBILITY.md** - Application's direct use of audioop
2. **This fix** - pydub's dependency on audioop

## Benefits

1. **Automatic Resolution** - Users don't need to manually install `audioop-lts`
2. **Transparent** - Works seamlessly on both old and new Python versions
3. **Clear Diagnostics** - Informative error messages help users understand what's happening
4. **Future-Proof** - Applications will work on Python 3.13+ without manual intervention

## References

- **audioop-lts package**: https://pypi.org/project/audioop-lts/
- **Python 3.13 Release Notes**: https://docs.python.org/3.13/whatsnew/3.13.html
- **pydub documentation**: https://github.com/jiaaro/pydub

---

**Date**: January 2025  
**Python Version Tested**: 3.12 (code verified, 3.13+ testing required)  
**Status**: ✅ Implemented, awaiting 3.13+ testing
