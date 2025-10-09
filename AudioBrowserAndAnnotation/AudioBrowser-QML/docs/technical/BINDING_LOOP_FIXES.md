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
QML BatchRenameDialog: Binding loop detected for property "batchOperations"
QML BatchRenameDialog: Binding loop detected for property "fileManager"
QML BatchConvertDialog: Binding loop detected for property "batchOperations"
QML ProgressDialog: Binding loop detected for property "batchOperations"
QML PracticeStatisticsDialog: Binding loop detected for property "practiceStatistics"
QML PracticeStatisticsDialog: Binding loop detected for property "fileManager"
QML PracticeGoalsDialog: Binding loop detected for property "practiceGoals"
QML PracticeGoalsDialog: Binding loop detected for property "practiceStatistics"
QML PracticeGoalsDialog: Binding loop detected for property "fileManager"
QML SetlistBuilderDialog: Binding loop detected for property "setlistManager"
QML SetlistBuilderDialog: Binding loop detected for property "fileManager"
QML ExportAnnotationsDialog: Binding loop detected for property "annotationManager"
QML ExportAnnotationsDialog: Binding loop detected for property "fileManager"
QML FingerprintsTab: Binding loop detected for property "fingerprintEngine"
QML FingerprintsTab: Binding loop detected for property "fileManager"
QML FingerprintsTab: Binding loop detected for property "fileListModel"
```

**Root Cause**: Components were defining properties with the same names as context properties, and then trying to assign the context property to the local property (e.g., `clipManager: clipManager`). This creates a binding loop because QML tries to bind the property to itself.

**Solution**: Removed redundant property assignments in `main.qml` and `LibraryTab.qml`:

- **main.qml**: Removed property assignments from ClipsTab, FolderNotesTab, and all dialogs
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
  
  // Before:
  BatchRenameDialog {
      id: batchRenameDialog
      batchOperations: batchOperations  // Binding loop!
      fileManager: fileManager  // Binding loop!
  }
  
  // After:
  BatchRenameDialog {
      id: batchRenameDialog
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

The following components were fixed:
- ClipsTab
- FolderNotesTab
- FileContextMenu
- BatchRenameDialog
- BatchConvertDialog
- ProgressDialog
- PracticeStatisticsDialog
- PracticeGoalsDialog
- SetlistBuilderDialog
- ExportAnnotationsDialog (kept currentFile binding)
- FingerprintsTab

Since these objects are exposed as context properties in `main.py`, they are globally accessible to all QML components and don't need to be passed down.

### 2. QColor Assignment Errors

**Problem**: Multiple "Unable to assign [undefined] to QColor" errors:
```
Unable to assign [undefined] to QColor (at LibraryTab.qml:480)
Unable to assign [undefined] to QColor (at FolderNotesTab.qml:199)
Unable to assign [undefined] to QColor (at FolderNotesTab.qml:242)
Unable to assign [undefined] to QColor (at BatchRenameDialog.qml:141)
Unable to assign [undefined] to QColor (at BatchConvertDialog.qml:167)
Unable to assign [undefined] to QColor (at ProgressDialog.qml:150)
Unable to assign [undefined] to QColor (at PracticeGoalsDialog.qml:236)
Unable to assign [undefined] to QColor (at SetlistBuilderDialog.qml:182)
... and many more
```

**Root Cause**: Components were using Theme properties that didn't exist in the Theme singleton:
- `Theme.foregroundColor` (doesn't exist, should be `Theme.textColor`)
- `Theme.backgroundWhite` (didn't exist)
- `Theme.primary` (didn't exist, accentPrimary existed)
- `Theme.success` (didn't exist, accentSuccess existed)
- `Theme.danger` (didn't exist, accentDanger existed)
- `Theme.warning` (didn't exist, accentWarning existed)
- `Theme.info` (didn't exist, accentInfo existed)
- `Theme.textPrimary` (didn't exist, textColor existed)
- `Theme.backgroundDark` (didn't exist)
- `Theme.primaryDark` (didn't exist)
- `Theme.highlightColor` (didn't exist)

**Solution**: 
1. Replaced all instances of `Theme.foregroundColor` with `Theme.textColor`:
   - `qml/tabs/LibraryTab.qml` (line 476)
   - `qml/tabs/FolderNotesTab.qml` (lines 199, 242)

2. Added convenience aliases to `qml/styles/Theme.qml`:
   ```qml
   // === Convenience Aliases for Common Usage ===
   readonly property color backgroundWhite: backgroundLight
   readonly property color backgroundDark: backgroundColor
   readonly property color textPrimary: textColor
   readonly property color primary: accentPrimary
   readonly property color success: accentSuccess
   readonly property color danger: accentDanger
   readonly property color warning: accentWarning
   readonly property color info: accentInfo
   readonly property color primaryDark: Qt.darker(accentPrimary, 1.2)
   readonly property color highlightColor: accentPrimary
   ```

This approach maintains backward compatibility while allowing dialogs to use more intuitive property names.

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
   - Removed binding loop-causing property assignments from all dialogs:
     - BatchRenameDialog
     - BatchConvertDialog
     - ProgressDialog
     - PracticeStatisticsDialog
     - PracticeGoalsDialog
     - SetlistBuilderDialog
     - ExportAnnotationsDialog (kept currentFile binding)
   - Removed binding loop-causing property assignments from FingerprintsTab

2. **qml/tabs/LibraryTab.qml**
   - Removed binding loop-causing property assignments from FileContextMenu
   - Fixed `Theme.foregroundColor` → `Theme.textColor`
   - Added `Component.onCompleted` for startup folder prompt

3. **qml/tabs/FolderNotesTab.qml**
   - Fixed `Theme.foregroundColor` → `Theme.textColor` (2 locations)

4. **qml/styles/Theme.qml**
   - Added convenience property aliases for common color names:
     - `backgroundWhite`, `backgroundDark`, `textPrimary`
     - `primary`, `success`, `danger`, `warning`, `info`
     - `primaryDark`, `highlightColor`

5. **qml/dialogs/FolderDialog.qml**
   - Replaced unsupported `FileDialog.OpenDirectory` with Qt6-compatible approach
   - Updated to extract parent directory from selected file

6. **backend/settings_manager.py**
   - Added `_migrate_legacy_settings()` method
   - Called migration method in `__init__`

## Additional Fixes (Phase 2)

### 6. Additional Dialog Binding Loops

**Problem**: Three more dialogs were found to have binding loop errors:
```
QML BackupSelectionDialog: Binding loop detected for property "backupManager"
QML AutoGenerationSettingsDialog: Binding loop detected for property "settingsManager"
QML DocumentationBrowserDialog: Binding loop detected for property "documentationManager"
```

**Solution**: Removed redundant property assignments in `main.qml`:

| Dialog | Properties Removed |
|--------|-------------------|
| DocumentationBrowserDialog | `documentationManager` |
| AutoGenerationSettingsDialog | `settingsManager` |
| BackupSelectionDialog | `backupManager` |

```qml
// Before:
DocumentationBrowserDialog {
    id: documentationBrowserDialog
    documentationManager: documentationManager  // Binding loop!
}

// After:
DocumentationBrowserDialog {
    id: documentationBrowserDialog
    // documentationManager is accessed from context properties
}
```

### 7. Shortcut Warnings

**Problem**: Shortcuts using `StandardKey` were generating warnings:
```
QML Shortcut: Only binding to one of multiple key bindings associated with 11/12
```

**Root Cause**: Qt 6 deprecated the `sequence:` syntax for `StandardKey` shortcuts when multiple key sequences exist.

**Solution**: Changed `sequence:` to `sequences: []` in `main.qml`:

```qml
// Before:
Shortcut {
    sequence: StandardKey.Undo  // Warning!
}

// After:
Shortcut {
    sequences: [StandardKey.Undo]  // Correct!
}
```

Applied to:
- Line 184: Undo shortcut
- Line 202: Redo shortcut

### 8. MiniWaveformWidget Signal Handler Errors

**Problem**: MiniWaveformWidget.qml had incorrect method calls and signal handlers:
```
QML Connections: Detected function "onWaveformCleared" in Connections element
TypeError: unable to convert a Python 'NoneType' object to a C++ 'PyQt_PyObject' instance
```

**Root Cause**: 
- Called non-existent methods: `loadWaveform()`, `clearWaveform()`
- Used non-existent signal handler: `onWaveformCleared()`
- Wrong signal signature: `onWaveformReady(peaks, duration)` instead of `onWaveformReady(path)`

**Solution**: Fixed method calls and signal handlers in `qml/components/MiniWaveformWidget.qml`:

```qml
// Before:
onFilePathChanged: {
    if (filePath && filePath.length > 0) {
        waveformEngine.loadWaveform(filePath)  // Wrong method!
    } else {
        waveformEngine.clearWaveform()  // Doesn't exist!
    }
}

Connections {
    target: waveformEngine
    
    function onWaveformReady(peaks, duration) {  // Wrong signature!
        miniWaveform.setWaveformData(peaks, duration)
        root.durationMs = duration
    }
    
    function onWaveformCleared() {  // Signal doesn't exist!
        miniWaveform.clearWaveform()
        root.durationMs = 0
    }
}

// After:
onFilePathChanged: {
    if (filePath && filePath.length > 0) {
        waveformEngine.generateWaveform(filePath)  // Correct method!
    } else {
        miniWaveform.clearWaveform()
        root.durationMs = 0
    }
}

Connections {
    target: waveformEngine
    
    function onWaveformReady(path) {  // Correct signature!
        if (path === filePath) {
            var peaks = waveformEngine.getWaveformData(path)
            var duration = waveformEngine.getWaveformDuration(path)
            miniWaveform.setWaveformData(peaks, duration)
            root.durationMs = duration
        }
    }
}
```

## Testing

Created `test_binding_fixes.py`, `test_binding_loop_fixes.py`, and `test_qml_binding_fixes.py` to verify all fixes:
- ✓ No binding loops in main.qml components (ClipsTab, FolderNotesTab)
- ✓ No binding loops in all dialogs (BatchRenameDialog, BatchConvertDialog, ProgressDialog, etc.)
- ✓ No binding loops in additional dialogs (DocumentationBrowserDialog, AutoGenerationSettingsDialog, BackupSelectionDialog)
- ✓ No binding loops in FingerprintsTab
- ✓ All Theme.foregroundColor references replaced
- ✓ All Theme color aliases properly defined (backgroundWhite, primary, success, etc.)
- ✓ ExportAnnotationsDialog properly retains currentFile binding
- ✓ Legacy settings migration implemented
- ✓ Startup folder prompt implemented
- ✓ FolderDialog properly configured for Qt6
- ✓ FileContextMenu has no binding loops
- ✓ All StandardKey shortcuts use correct 'sequences:' syntax
- ✓ MiniWaveformWidget uses correct methods and signal handlers

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
