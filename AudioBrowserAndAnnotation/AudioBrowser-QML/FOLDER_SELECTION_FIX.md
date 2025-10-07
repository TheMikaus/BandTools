# Folder Selection and Metadata Loading Fix

This document describes the fixes implemented to address folder selection issues and add metadata loading support from the original AudioBrowser application.

## Issues Fixed

### 1. Folder Dialog Requiring File Selection

**Problem**: When using the "Browse..." button to select a directory, the dialog was in file selection mode, requiring users to select a file instead of a folder.

**Root Cause**: The `FolderDialog.qml` component was using `FileDialog.SaveFile` mode as a workaround, and `LibraryTab.qml` was using `FileDialog.OpenFile` mode.

**Solution**: 
- Changed `FolderDialog.qml` to use `FileDialog.OpenDirectory` mode
- Updated the accepted handler to use `selectedFile` property (which contains the selected directory in OpenDirectory mode)
- Updated `LibraryTab.qml` to use the fixed `FolderDialog` component

### 2. Path Prepending Extra Slash

**Problem**: On Windows, selected folder paths would have an extra "/" prepended (e.g., `/C:/Users/...` instead of `C:/Users/...`).

**Root Cause**: Qt's `file://` URL scheme removal on Windows leaves a leading slash that should be removed for drive letter paths.

**Solution**:
```qml
// Remove file:// prefix
if (folderPath.startsWith("file://")) {
    folderPath = folderPath.substring(7)
}

// On Windows, handle the extra slash issue
// file:///C:/path becomes /C:/path, should be C:/path
if (folderPath.length > 2 && folderPath.charAt(0) === '/' && folderPath.charAt(2) === ':') {
    folderPath = folderPath.substring(1)
}
```

### 3. Missing Directory Prompt

**Problem**: When no directory was set, pressing Enter in the directory field or clicking Refresh would do nothing without feedback.

**Solution**:
- Added `noDirectoryDialog` that prompts user to select a directory
- Added `promptForDirectory()` function called when directory is empty
- Updated TextField `onAccepted` and Refresh button `onClicked` handlers

### 4. No Directory Initialization on Startup

**Problem**: The application wouldn't remember the last used directory between sessions.

**Solution**:
- Added initialization in `main.py` to load saved root directory from settings
- Connected `currentDirectoryChanged` signal to `setRootDir` to automatically save changes
- Validates directory exists before setting it

### 5. No Metadata Loading from Original Version

**Problem**: The QML version couldn't use metadata files created by the original PyQt6 AudioBrowser application (`.provided_names.json`, `.duration_cache.json`).

**Solution**:
- Added `_load_provided_names()` method to FileManager
- Added `_load_duration_cache()` method to FileManager
- Added `getProvidedName()` and `getCachedDuration()` slot methods
- Updated FileListModel to use metadata when available
- Handles both filename and stem matching for flexibility
- Automatically converts old duration format (seconds) to milliseconds

## Files Modified

### QML Files
- `qml/dialogs/FolderDialog.qml` - Fixed dialog mode and path handling
- `qml/tabs/LibraryTab.qml` - Added prompt dialog and updated to use FolderDialog

### Python Files
- `main.py` - Added directory initialization and settings persistence
- `backend/file_manager.py` - Added metadata loading methods
- `backend/models.py` - Updated FileListModel to use metadata

## Testing

Comprehensive tests were added to verify the fixes:

### Test Files
1. `test_folder_dialog.py` - Verifies QML configuration
2. `test_metadata_loading.py` - Verifies metadata loading functionality

### Test Coverage
- ✅ FolderDialog uses OpenDirectory mode
- ✅ Windows path handling present
- ✅ folderSelected signal defined
- ✅ LibraryTab uses FolderDialog component
- ✅ No directory prompt dialog present
- ✅ Metadata methods implemented
- ✅ Provided names loading works
- ✅ Duration cache loading works
- ✅ Seconds to milliseconds conversion works
- ✅ Missing metadata files handled gracefully

## Usage

### Setting Initial Directory
The application will automatically load the last used directory on startup. To set a directory:
1. Click "Browse..." button
2. Select a folder (not a file)
3. The directory will be set and remembered for next session

### Directory Text Field
You can also type or paste a directory path directly:
1. Click in the directory text field
2. Type or paste a valid directory path
3. Press Enter to navigate to that directory

### Metadata Support
If you have existing metadata files from the original AudioBrowser:
- `.provided_names.json` - Custom file display names will be used automatically
- `.duration_cache.json` - Cached durations will be loaded (faster than extraction)

The application will fall back to extracting information from audio files if metadata is not available.

## Benefits

1. **Improved User Experience**: Proper folder selection dialog
2. **Cross-Platform**: Works correctly on Windows, macOS, and Linux
3. **Session Persistence**: Remembers last directory across restarts
4. **Backward Compatible**: Works with metadata from original AudioBrowser
5. **Performance**: Uses cached durations when available
6. **Graceful Degradation**: Falls back to file extraction if no metadata
