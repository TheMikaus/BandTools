# Error Logging Improvement for _ensure_import

## Overview

This document describes the error logging improvement made to the `_ensure_import` function used throughout the AudioBrowser applications.

## Problem

The `_ensure_import` function is used to automatically install missing Python dependencies. However, when imports failed, error information was only returned as a string and not logged. Many callers ignored the error return value:

```python
HAVE_PYDUB, pydub_error = _ensure_import("pydub", "pydub")
# Error stored but never logged or displayed
```

Or in some cases:
```python
_ensure_import("PyQt6.QtCore", "PyQt6")
# Exceptions raised but no diagnostic context
```

This made debugging difficult because:

1. No diagnostic information was visible in console output
2. Developers couldn't see what actually failed during import
3. Error messages like "ModuleNotFoundError: No module named 'pyaudioop'" gave no context

## Solution

Added logging to stderr at all error paths in the `_ensure_import` function:

### Logging Added

1. **Initial Import Error** - Log when module cannot be imported initially
   ```python
   print(f"WARNING: Failed to import {mod_name}: {e}", file=sys.stderr)
   ```

2. **Frozen Build Error** - Log when module unavailable in frozen build
   ```python
   print(f"ERROR: {error_msg}", file=sys.stderr)
   ```

3. **Installation Failure** - Log when pip installation fails
   ```python
   print(f"ERROR: {error_msg}", file=sys.stderr)
   ```

4. **Post-Install Import Error** - Log when import still fails after successful installation
   ```python
   print(f"ERROR: {error_msg}", file=sys.stderr)
   ```

### Key Design Decisions

- **Use stderr** - All error messages go to `sys.stderr` for proper error stream handling
- **Preserve behavior** - Return values and function signatures unchanged
- **Minimal changes** - Only added logging, no functional changes
- **Clear prefixes** - Use "WARNING:" and "ERROR:" prefixes for easy identification
- **Exception context** - Include the actual Python exception message for detailed diagnostics

## Files Modified (QML Version)

1. `backend/batch_operations.py` - Updated `_ensure_import` with logging
2. `main.py` - Updated `_ensure_import` with logging
3. `test_qml_syntax.py` - Updated `_ensure_import` with logging

## Example Output

### Before Fix
```
(No output - error swallowed silently)
```

### After Fix
```
WARNING: Failed to import pyaudioop: No module named 'pyaudioop'
ERROR: Module pyaudioop not found
```

Or for installation failures:
```
WARNING: Failed to import somepackage: No module named 'somepackage'
Installing somepackage...
ERROR: Failed to install somepackage. Attempted installations:
  - '/usr/bin/python3 -m pip install somepackage' failed with exit code 1
  - '/usr/bin/python3 -m pip install --user somepackage' failed with exit code 1
```

## Benefits

1. **Better Diagnostics** - Errors are now visible even when return value is ignored
2. **Faster Debugging** - Developers immediately see what module failed and why
3. **Context Preservation** - Full error messages including Python exceptions
4. **Non-Breaking** - Existing code continues to work exactly as before
5. **Consistent Pattern** - Same logging approach across all AudioBrowser versions

## Testing

All modified files:
- ✅ Compile successfully without syntax errors
- ✅ Log errors to stderr as expected
- ✅ Maintain backward compatibility
- ✅ Preserve existing return value behavior
- ✅ Work correctly with QML application startup

---

**Date**: December 2024  
**Status**: ✅ Complete  
**Related Issue**: AudioBrowserOrig's ensure_import swallows errors
