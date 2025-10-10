# Fix for TypeError: unable to convert Python NoneType to C++ PyQt_PyObject

## Summary

Fixed a critical TypeError that prevented the AudioBrowser QML application from starting. The issue was caused by incorrect type annotations in the `SettingsManager` geometry methods.

## The Problem

When the application tried to load, it crashed with:
```
TypeError: unable to convert a Python 'NoneType' object to a C++ 'PyQt_PyObject' instance
```

### Root Cause Analysis

1. **Type Mismatch**: Methods `getGeometry()` and `getSplitterState()` were annotated with `@pyqtSlot(result=bytes)` but QML expected strings
2. **Null Return**: These methods could return `None` when no saved value existed
3. **QML Usage**: The QML code used `JSON.stringify()` to save and `JSON.parse()` to restore geometry as strings
4. **Bridge Failure**: PyQt6's Python-to-QML bridge couldn't convert `None` with a `bytes` type annotation

## The Solution

Changed type annotations from `bytes` to `str` and ensured methods never return `None`:

### Before (Incorrect)
```python
@pyqtSlot(result=bytes)
def getGeometry(self) -> Optional[bytes]:
    return self.settings.value(SETTINGS_KEY_WINDOW_GEOMETRY)

@pyqtSlot(bytes)
def setGeometry(self, geometry: bytes):
    self.settings.setValue(SETTINGS_KEY_WINDOW_GEOMETRY, geometry)
```

### After (Fixed)
```python
@pyqtSlot(result=str)
def getGeometry(self) -> str:
    result = self.settings.value(SETTINGS_KEY_WINDOW_GEOMETRY)
    return result if result is not None else ""

@pyqtSlot(str)
def setGeometry(self, geometry: str):
    self.settings.setValue(SETTINGS_KEY_WINDOW_GEOMETRY, geometry)
```

## Changes Made

### Modified Files
- `backend/settings_manager.py`: Fixed 4 methods
  - `getGeometry()` - Changed return type from `bytes` to `str`, added null check
  - `setGeometry()` - Changed parameter type from `bytes` to `str`
  - `getSplitterState()` - Changed return type from `bytes` to `str`, added null check
  - `setSplitterState()` - Changed parameter type from `bytes` to `str`

### New Files
- `test_geometry_types.py` - Comprehensive test suite for type safety
- `docs/technical/GEOMETRY_TYPE_FIX.md` - Detailed technical documentation

## Testing

Created and ran comprehensive tests:

```bash
$ python3 test_geometry_types.py
============================================================
Geometry Methods Type Safety Test
============================================================
Testing geometry methods...
  ✓ getGeometry() returns empty string when no value saved
  ✓ getGeometry() returns saved string value correctly
  ✓ getSplitterState() returns empty string when no value saved
  ✓ getSplitterState() returns saved string value correctly

✅ All tests passed!
```

Also verified:
- ✅ Python syntax validation
- ✅ Workspace layouts test
- ✅ Backend module tests
- ✅ No breaking changes to existing code

## Why This Works

1. **Type Alignment**: `str` type matches what QML expects and what the code actually uses
2. **Null Safety**: Returning empty string `""` instead of `None` prevents type conversion errors
3. **Backward Compatible**: Existing saved settings (if any) continue to work
4. **Minimal Changes**: Only 4 methods were modified, no changes to QML or other Python code

## Related Information

- The QML code in `qml/main.qml` already uses `JSON.stringify()` and `JSON.parse()`, confirming strings are the correct type
- No other methods in the codebase have this issue
- This fix follows the same pattern used by other string-based settings in the class

## Verification Steps

To verify the fix works:

1. **Syntax Check**:
   ```bash
   python3 -m py_compile backend/settings_manager.py
   ```

2. **Type Safety Test**:
   ```bash
   python3 test_geometry_types.py
   ```

3. **Integration Test**:
   ```bash
   python3 test_workspace_layouts.py
   ```

All tests pass successfully ✅

## Impact

- **Fixes**: Application no longer crashes on startup
- **No Breaking Changes**: All existing functionality preserved
- **Type Safety**: Proper type annotations prevent future errors
- **Maintainability**: Clear types make code easier to understand
