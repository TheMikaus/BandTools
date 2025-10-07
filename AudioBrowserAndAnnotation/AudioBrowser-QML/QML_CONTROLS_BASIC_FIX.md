# QML Controls.Basic Fix - Technical Summary

## Problem

The AudioBrowser QML application failed to load with the following error:

```
QQmlApplicationEngine failed to load component
file:///c:/Work/ToolDev/BandTools/AudioBrowserAndAnnotation/AudioBrowser-QML/qml/components/FileContextMenu.qml:25:1: Type Menu unavailable
qrc:/qt-project.org/imports/QtQuick/Controls/Windows/Menu.qml:32:15: Type MenuItem unavailable
qrc:/qt-project.org/imports/QtQuick/Controls/Windows/MenuItem.qml:7:1: Cannot load library ... qtquickcontrols2windowsstyleimplplugin.dll: The specified module could not be found.
```

## Root Cause

When importing `QtQuick.Controls` without explicitly specifying a style, Qt attempts to load platform-specific implementations:
- On Windows: Windows style (requires `qtquickcontrols2windowsstyleimplplugin.dll`)
- On macOS: macOS style
- On Linux: May attempt various native styles

The Windows style plugin has dependencies on Windows-specific DLLs that may not be available in all environments (e.g., minimal installations, CI environments, or when using PyQt6 from pip).

## Solution

Replace all instances of `import QtQuick.Controls` with `import QtQuick.Controls.Basic` to explicitly use the Basic style, which:
- Is a pure QML implementation without native dependencies
- Works consistently across all platforms
- Does not require platform-specific plugins or DLLs
- Provides all standard controls (Button, Menu, MenuItem, TextField, etc.)

## Changes Made

### QML Files Updated (17 files)
All QML files that imported `QtQuick.Controls` were updated to use `QtQuick.Controls.Basic`:

1. **Main Application**
   - `qml/main.qml`

2. **Components** (9 files)
   - `qml/components/AnnotationMarker.qml`
   - `qml/components/ClipMarker.qml`
   - `qml/components/FileContextMenu.qml` *(Primary failure point)*
   - `qml/components/PlaybackControls.qml`
   - `qml/components/StyledButton.qml`
   - `qml/components/StyledLabel.qml`
   - `qml/components/StyledSlider.qml`
   - `qml/components/StyledTextField.qml`
   - `qml/components/WaveformDisplay.qml`

3. **Tabs** (4 files)
   - `qml/tabs/AnnotationsTab.qml`
   - `qml/tabs/ClipsTab.qml`
   - `qml/tabs/FolderNotesTab.qml`
   - `qml/tabs/LibraryTab.qml`

4. **Dialogs** (3 files)
   - `qml/dialogs/AnnotationDialog.qml`
   - `qml/dialogs/ClipDialog.qml`
   - `qml/dialogs/FolderDialog.qml`

### Documentation Updated
- `DEVELOPER_GUIDE.md` - Updated code templates to use `QtQuick.Controls.Basic`
- `CHANGELOG.md` - Added entry documenting the fix

## Benefits

1. **Cross-platform compatibility** - Works on Windows, macOS, and Linux without platform-specific requirements
2. **Reduced dependencies** - No need for native style plugins or their dependencies
3. **Predictable behavior** - Same appearance and behavior across all platforms
4. **Easier deployment** - Fewer DLL/shared library requirements for packaging

## Trade-offs

The Basic style does not provide native look-and-feel for each platform. However:
- The application already uses custom styling via the Theme singleton
- Most controls are custom-styled components that override default appearance
- Consistent cross-platform appearance is often preferable for branded applications

## Testing

The fix was validated by:
1. Running `test_structure.py` - Verified all QML files exist and are valid
2. Checking import consistency - All 17 files now use `QtQuick.Controls.Basic`
3. Documentation review - Developer guide updated with correct patterns

## Future Considerations

If platform-native styling is desired in the future, consider:
1. Bundling the Windows style plugin DLLs with the application
2. Using `QT_QUICK_CONTROLS_STYLE` environment variable to set style at runtime
3. Providing fallback logic to try native styles first, then fall back to Basic

For now, the Basic style provides the most reliable and maintainable solution.

## References

- [Qt Quick Controls Styles Documentation](https://doc.qt.io/qt-6/qtquickcontrols-styles.html)
- [Qt Quick Controls Basic Style](https://doc.qt.io/qt-6/qtquickcontrols-basic.html)
- [PyQt6 QML Controls](https://www.riverbankcomputing.com/static/Docs/PyQt6/qml.html)
