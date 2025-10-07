# Binding Loop Fixes and Startup Improvements

## Overview

This document describes the fixes applied to resolve binding loop errors, QML property issues, and improve the startup experience of the AudioBrowser QML application.

## Issues Resolved

### 1. Binding Loop Errors

**Problem**: Multiple binding loop errors were occurring when the application started:
```
QML ClipsTab: Binding loop detected for property "clipManager"
QML ClipsTab: Binding loop detected for property "audioEngine"
QML FolderNotesTab: Binding loop detected for property "folderNotesManager"
QML FileContextMenu: Binding loop detected for property "audioEngine"
QML FileContextMenu: Binding loop detected for property "annotationManager"
QML FileContextMenu: Binding loop detected for property "clipManager"
QML FileContextMenu: Binding loop detected for property "fileManager"
```

**Root Cause**: Components were defining properties with the same names as context properties, and then trying to assign the context property to the local property (e.g., `clipManager: clipManager`). This creates a binding loop because QML tries to bind the property to itself.

**Solution**: Removed redundant property assignments in `main.qml` and `LibraryTab.qml`:

- **main.qml**: Removed property assignments from ClipsTab and FolderNotesTab
  ```qml
  // Before:
  ClipsTab {
      id: clipsTab
      clipManager: clipManager  // Binding loop!
      audioEngine: audioEngine  // Binding loop!
  }
  
  // After:
  ClipsTab {
      id: clipsTab
  }
  ```

- **LibraryTab.qml**: Removed property assignments from FileContextMenu
  ```qml
  // Before:
  FileContextMenu {
      id: contextMenu
      audioEngine: audioEngine  // Binding loop!
      annotationManager: annotationManager  // Binding loop!
      clipManager: clipManager  // Binding loop!
      fileManager: fileManager  // Binding loop!
  }
  
  // After:
  FileContextMenu {
      id: contextMenu
  }
  ```

Since these objects are exposed as context properties in `main.py`, they are globally accessible to all QML components and don't need to be passed down.

### 2. QColor Assignment Errors

**Problem**: Multiple "Unable to assign [undefined] to QColor" errors:
```
Unable to assign [undefined] to QColor (at LibraryTab.qml:480)
Unable to assign [undefined] to QColor (at FolderNotesTab.qml:199)
Unable to assign [undefined] to QColor (at FolderNotesTab.qml:242)
```

**Root Cause**: Components were using `Theme.foregroundColor` which doesn't exist in the Theme singleton. The correct property name is `Theme.textColor`.

**Solution**: Replaced all instances of `Theme.foregroundColor` with `Theme.textColor`:

- `qml/tabs/LibraryTab.qml` (line 476)
- `qml/tabs/FolderNotesTab.qml` (lines 199, 242)

### 3. FileDialog FileMode Error

**Problem**: Error when loading FolderDialog:
```
Unable to assign [undefined] to QQuickFileDialog::FileMode
```

**Root Cause**: The code was using `FileDialog.OpenDirectory` which is not available in Qt Quick Dialogs for Qt6.

**Solution**: Updated `qml/dialogs/FolderDialog.qml` to use a workaround:
- Use `fileMode: FileDialog.OpenFile` (which is supported)
- Extract the parent directory from the selected file
- This allows users to navigate to a folder and select any file in it, then the folder path is derived

## New Features Added

### 4. Legacy Settings Migration

**Feature**: Automatic migration of settings from the legacy "Audio Folder Player" application.

**Implementation**: Added `_migrate_legacy_settings()` method to `SettingsManager` class:

```python
def _migrate_legacy_settings(self):
    """
    Migrate settings from legacy "Audio Folder Player" application.
    
    Checks for settings from the old PyQt5-based application and imports
    the root directory if available and not already set.
    """
    # Check if we already have settings (don't overwrite)
    current_root = self.settings.value(SETTINGS_KEY_ROOT, "", type=str)
    if current_root:
        return
    
    # Try to load legacy settings
    legacy_settings = QSettings("YourCompany", "Audio Folder Player")
    legacy_root = legacy_settings.value("root_dir", "", type=str)
    
    if legacy_root:
        # Migrate the root directory setting
        self.settings.setValue(SETTINGS_KEY_ROOT, legacy_root)
        # ... also migrate theme and volume if available
```

This migration runs automatically when the application starts, checking for settings from:
- Organization: "YourCompany"
- Application: "Audio Folder Player"
- Key: "root_dir"

If found and no current settings exist, it imports:
- Root directory path
- Theme preference
- Volume setting

### 5. Startup Folder Selection

**Feature**: Automatically prompt user to select a folder if none is configured.

**Implementation**: Added `Component.onCompleted` handler to `LibraryTab.qml`:

```qml
Component.onCompleted: {
    // Check if we have a directory set
    var currentDir = fileManager.getCurrentDirectory()
    if (!currentDir || currentDir.length === 0) {
        // No directory set, prompt user to select one
        promptForDirectory()
    }
}
```

This ensures that on first startup (or if settings are lost), the user is immediately prompted to select an audio directory, improving the first-run experience.

## Files Modified

1. **qml/main.qml**
   - Removed binding loop-causing property assignments from ClipsTab and FolderNotesTab

2. **qml/tabs/LibraryTab.qml**
   - Removed binding loop-causing property assignments from FileContextMenu
   - Fixed `Theme.foregroundColor` → `Theme.textColor`
   - Added `Component.onCompleted` for startup folder prompt

3. **qml/tabs/FolderNotesTab.qml**
   - Fixed `Theme.foregroundColor` → `Theme.textColor` (2 locations)

4. **qml/dialogs/FolderDialog.qml**
   - Replaced unsupported `FileDialog.OpenDirectory` with Qt6-compatible approach
   - Updated to extract parent directory from selected file

5. **backend/settings_manager.py**
   - Added `_migrate_legacy_settings()` method
   - Called migration method in `__init__`

## Testing

Created `test_binding_fixes.py` to verify all fixes:
- ✓ No binding loops in main.qml components
- ✓ All Theme.foregroundColor references replaced
- ✓ Legacy settings migration implemented
- ✓ Startup folder prompt implemented
- ✓ FolderDialog properly configured for Qt6
- ✓ FileContextMenu has no binding loops

All tests pass successfully.

## User Experience Improvements

1. **Cleaner Startup**: No more binding loop warnings in console
2. **Better First Run**: Automatically prompts for folder selection if none configured
3. **Seamless Migration**: Users upgrading from the old PyQt5 application will have their settings automatically imported
4. **Cross-Platform**: FileDialog workaround works on Windows, Linux, and macOS

## Notes

- Context properties exposed in `main.py` are globally accessible in QML and don't need to be passed as properties
- Qt Quick Dialogs in Qt6 has different API than Qt5 - some enums are not available
- The FolderDialog workaround (selecting a file to choose its parent directory) is a known limitation of Qt Quick Dialogs
