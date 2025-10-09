# WaveformView Property Type Fix

## Issue

The application was failing to load with the following error:

```
Loading QML file: c:\Work\ToolDev\BandTools\AudioBrowserAndAnnotation\AudioBrowser-QML\qml\main.qml
TypeError: unable to convert a Python 'NoneType' object to a C++ 'PyQt_PyObject' instance
```

## Root Cause

The `peaks` property in the `WaveformView` class (backend/waveform_view.py) was defined using Python's `list` type directly:

```python
peaks = pyqtProperty(list, _get_peaks, _set_peaks)
```

In PyQt6, when exposing Python properties to QML, complex types like lists need to be specified as string type annotations rather than Python type objects. The Python `list` type doesn't directly map to C++/QML types, causing type conversion errors when QML tries to access or modify the property.

## Solution

Changed the property definition to use `'QVariant'` as a string type annotation:

```python
peaks = pyqtProperty('QVariant', _get_peaks, _set_peaks)
```

### Why QVariant?

- `QVariant` is Qt's type-safe union that can hold various types including lists
- Using string type annotations (`'QVariant'`) tells PyQt6 to handle type conversion automatically
- This is the recommended approach for PyQt6 and is used consistently elsewhere in the codebase

### Examples of Similar Patterns in the Codebase

Other backend modules use string type annotations for complex types:

- `backend/annotation_manager.py`: Uses `'QVariantMap'` for dictionary return types
  ```python
  @pyqtSlot(int, result='QVariantMap')
  def getAnnotation(self, index: int) -> Dict[str, Any]:
  ```

- `backend/settings_manager.py`: Uses `'QVariant'` for generic value types
  ```python
  @pyqtSlot(str, "QVariant", result="QVariant")
  def getValue(self, key: str, default_value=None):
  ```

## Changes Made

### File: `backend/waveform_view.py`

**Before:**
```python
def _set_peaks(self, peaks: List[List[float]]) -> None:
    if peaks != self._peaks:
        self._peaks = peaks if peaks else []
        self.update()

peaks = pyqtProperty(list, _get_peaks, _set_peaks)
```

**After:**
```python
def _set_peaks(self, peaks: List[List[float]]) -> None:
    if peaks != self._peaks:
        self._peaks = peaks if peaks else []
        self.update()

peaks = pyqtProperty('QVariant', _get_peaks, _set_peaks)
```

Only line 89 was changed.

## How the Property is Used in QML

The `peaks` property is accessed from QML components like `WaveformDisplay.qml`:

```qml
// Setting peaks to empty list when clearing waveform
waveform.peaks = []

// Setting peaks from waveform engine data
var peaks = waveformEngine.getWaveformData(filePath)
waveform.peaks = peaks
```

With the fix, these assignments now work correctly without type conversion errors.

## Testing

A test file was created (`test_waveform_property.py`) to verify the fix:

```python
# Test setting peaks to None (should not crash)
view.peaks = None
assert view.peaks == [] or view.peaks is None

# Test setting peaks to empty list
view.peaks = []
assert view.peaks == []

# Test setting peaks to actual data
test_peaks = [[0.5, -0.3], [0.7, -0.5]]
view.peaks = test_peaks
assert view.peaks == test_peaks
```

## Verification

To verify the fix:

1. Run the application: `python3 main.py`
2. The QML file should load successfully without the TypeError
3. Waveform display should work correctly when loading audio files
4. No type conversion errors should appear in the console

## Related Documentation

- See `BINDING_LOOP_FIXES.md` for a similar TypeError issue that was fixed in MiniWaveformWidget
- PyQt6 documentation on property types: https://www.riverbankcomputing.com/static/Docs/PyQt6/
- Qt QVariant documentation: https://doc.qt.io/qt-6/qvariant.html

## Best Practices for PyQt6 Properties

When defining `pyqtProperty` for QML exposure:

1. **Simple types**: Use Python types directly
   - `int`, `float`, `bool`, `str` are OK
   - Example: `pyqtProperty(int, getter, setter)`

2. **Qt types**: Use Qt type classes directly
   - `QColor`, `QUrl`, etc.
   - Example: `pyqtProperty(QColor, getter, setter)`

3. **Complex/container types**: Use string type annotations
   - Lists, dictionaries, custom objects
   - Use `'QVariant'`, `'QVariantList'`, or `'QVariantMap'`
   - Example: `pyqtProperty('QVariant', getter, setter)`

4. **Return types in slots**: Also use string annotations for complex types
   - Example: `@pyqtSlot(int, result='QVariantMap')`
