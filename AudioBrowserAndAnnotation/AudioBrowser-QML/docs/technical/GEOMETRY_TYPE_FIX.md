# Geometry Type Fix Summary

## Issue

The application crashed on startup with the following error:

```
TypeError: unable to convert a Python 'NoneType' object to a C++ 'PyQt_PyObject' instance
```

## Root Cause

The `getGeometry()` and `getSplitterState()` methods in `SettingsManager` had incorrect type annotations in their `@pyqtSlot` decorators:

1. **Type Mismatch**: Methods were annotated with `result=bytes` but QML expected strings
2. **None Return**: Methods could return `None` when no value was saved
3. **QML Usage**: The QML code was calling `JSON.parse()` on the returned value, expecting a string

### Previous Implementation

```python
@pyqtSlot(result=bytes)
def getGeometry(self) -> Optional[bytes]:
    """Get saved window geometry."""
    return self.settings.value(SETTINGS_KEY_WINDOW_GEOMETRY)

@pyqtSlot(bytes)
def setGeometry(self, geometry: bytes):
    """Save window geometry."""
    self.settings.setValue(SETTINGS_KEY_WINDOW_GEOMETRY, geometry)
```

### QML Usage

```qml
function saveWindowGeometry() {
    settingsManager.setGeometry(JSON.stringify({
        x: mainWindow.x,
        y: mainWindow.y,
        width: mainWindow.width,
        height: mainWindow.height
    }))
}

function restoreWindowGeometry() {
    var geometryStr = settingsManager.getGeometry()
    if (geometryStr) {
        var geometry = JSON.parse(geometryStr)
        // ... use geometry
    }
}
```

## Solution

Fixed the type annotations to match actual usage:

1. Changed `@pyqtSlot(result=bytes)` to `@pyqtSlot(result=str)`
2. Changed parameter types from `bytes` to `str`
3. Changed return values to always return `str` (empty string instead of `None`)
4. Updated type hints to reflect actual types

### Fixed Implementation

```python
@pyqtSlot(result=str)
def getGeometry(self) -> str:
    """Get saved window geometry."""
    result = self.settings.value(SETTINGS_KEY_WINDOW_GEOMETRY)
    return result if result is not None else ""

@pyqtSlot(str)
def setGeometry(self, geometry: str):
    """Save window geometry."""
    self.settings.setValue(SETTINGS_KEY_WINDOW_GEOMETRY, geometry)
```

## Files Changed

1. **backend/settings_manager.py**
   - Fixed `getGeometry()` return type and null handling
   - Fixed `setGeometry()` parameter type
   - Fixed `getSplitterState()` return type and null handling
   - Fixed `setSplitterState()` parameter type

## Testing

Created `test_geometry_types.py` to verify:
- ✓ `getGeometry()` returns empty string when no value saved
- ✓ `getGeometry()` returns saved string value correctly
- ✓ `setGeometry()` accepts string values
- ✓ `getSplitterState()` returns empty string when no value saved
- ✓ `getSplitterState()` returns saved string value correctly
- ✓ `setSplitterState()` accepts string values

All tests pass successfully.

## Impact

- **No Breaking Changes**: QML code already treated these as strings
- **Backward Compatible**: Existing saved settings continue to work
- **Type Safety**: Proper type annotations prevent future type errors
- **Null Safety**: Methods never return `None`, preventing null reference errors in QML

## Related Issues

This fix resolves the TypeError that prevented the application from loading. The same pattern should be applied to any other PyQt slot methods that interface with QML and handle optional values.
