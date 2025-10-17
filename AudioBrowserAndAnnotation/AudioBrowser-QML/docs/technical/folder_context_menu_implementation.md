# Folder Context Menu Implementation

## Overview

This document describes the technical implementation of the folder context menu feature, including the UI components, backend integration, and data storage.

## Architecture

### Components

1. **FolderContextMenu.qml** - QML component defining the context menu
2. **LibraryTab.qml** - Modified to handle right-click events on folders
3. **fingerprint_engine.py** - Backend module with folder metadata methods
4. **main.qml** - Signal routing for tab switching

### Data Flow

```
User right-clicks folder
    ↓
LibraryTab MouseArea detects right-click
    ↓
FolderContextMenu.popup() with folder path
    ↓
User selects menu option
    ↓
Signal emitted (e.g., generateFingerprintsRequested)
    ↓
Signal handler in LibraryTab calls backend method
    ↓
Backend updates cache/processes files
    ↓
UI updates (tab switch, progress indicators)
```

## Implementation Details

### QML Components

#### FolderContextMenu.qml

Location: `qml/components/FolderContextMenu.qml`

**Properties:**
- `folderPath: string` - Path to the folder
- `folderName: string` - Display name of the folder
- `fingerprintEngine: var` - Reference to FingerprintEngine backend
- `waveformEngine: var` - Reference to WaveformEngine backend
- `fileManager: var` - Reference to FileManager backend

**Signals:**
- `generateFingerprintsRequested()` - Emitted when user selects fingerprint generation
- `generateWaveformsRequested()` - Emitted when user selects waveform generation

**Menu Items:**
1. Generate Fingerprints - Calls `generateFingerprintsRequested()` signal
2. Mark as Reference Folder - Calls `fingerprintEngine.toggleFolderReference()`
3. Mark as Ignore Fingerprints - Calls `fingerprintEngine.toggleFolderIgnore()`
4. Generate Waveforms - Calls `generateWaveformsRequested()` signal

#### LibraryTab.qml Modifications

**Changes:**
1. Added `acceptedButtons: Qt.LeftButton | Qt.RightButton` to folder MouseArea
2. Modified `onClicked` to handle both left and right clicks:
   ```javascript
   onClicked: function(mouse) {
       if (mouse.button === Qt.RightButton) {
           // Show context menu
           folderContextMenu.folderPath = model.path
           folderContextMenu.folderName = model.name
           folderContextMenu.popup()
       } else {
           // Normal folder selection
           // ... existing code ...
       }
   }
   ```

3. Added FolderContextMenu instance with signal handlers:
   ```javascript
   FolderContextMenu {
       id: folderContextMenu
       
       onGenerateFingerprintsRequested: {
           // Get files and start generation
           var files = fileManager.discoverAudioFilesRecursive(folderPath)
           fingerprintEngine.generateFingerprints(files)
           // Switch to Fingerprints tab
           libraryTab.requestFingerprintsTab()
       }
       
       onGenerateWaveformsRequested: {
           // Get files and generate waveforms
           var files = fileManager.discoverAudioFilesRecursive(folderPath)
           for (var i = 0; i < files.length; i++) {
               waveformEngine.generateWaveform(files[i])
           }
       }
   }
   ```

4. Added `requestFingerprintsTab()` signal

#### main.qml Modifications

**Changes:**
1. Added signal handler for `requestFingerprintsTab`:
   ```javascript
   onRequestFingerprintsTab: {
       // Find and switch to Fingerprints tab
       for (var i = 0; i < tabBar.count; i++) {
           var tabButton = tabBar.itemAt(i)
           if (tabButton && tabButton.text === "Fingerprints") {
               tabBar.currentIndex = i
               break
           }
       }
   }
   ```

### Backend Implementation

#### fingerprint_engine.py

**New Functions:**

```python
def is_folder_reference(dirpath: Path) -> bool:
    """Check if a folder is marked as a reference folder."""
    cache = load_fingerprint_cache(dirpath)
    return cache.get("is_reference_folder", False)

def toggle_folder_reference(dirpath: Path) -> bool:
    """Toggle reference folder status. Returns new reference status."""
    cache = load_fingerprint_cache(dirpath)
    current_status = cache.get("is_reference_folder", False)
    cache["is_reference_folder"] = not current_status
    save_fingerprint_cache(dirpath, cache)
    return cache["is_reference_folder"]

def is_folder_ignored(dirpath: Path) -> bool:
    """Check if a folder is marked to be ignored for fingerprint matching."""
    cache = load_fingerprint_cache(dirpath)
    return cache.get("ignore_fingerprints", False)

def toggle_folder_ignore(dirpath: Path) -> bool:
    """Toggle folder ignore status. Returns new ignore status."""
    cache = load_fingerprint_cache(dirpath)
    current_status = cache.get("ignore_fingerprints", False)
    cache["ignore_fingerprints"] = not current_status
    save_fingerprint_cache(dirpath, cache)
    return cache["ignore_fingerprints"]
```

**New PyQt Slots in FingerprintEngine class:**

```python
@pyqtSlot(str, result=bool)
def isFolderReference(self, directory: str) -> bool:
    """Check if folder is marked as reference folder."""
    return is_folder_reference(Path(directory))

@pyqtSlot(str, result=bool)
def toggleFolderReference(self, directory: str) -> bool:
    """Toggle folder reference status."""
    return toggle_folder_reference(Path(directory))

@pyqtSlot(str, result=bool)
def isFolderIgnored(self, directory: str) -> bool:
    """Check if folder is ignored for fingerprint matching."""
    return is_folder_ignored(Path(directory))

@pyqtSlot(str, result=bool)
def toggleFolderIgnore(self, directory: str) -> bool:
    """Toggle folder ignore status."""
    return toggle_folder_ignore(Path(directory))
```

### Data Storage

#### Fingerprint Cache Structure

The folder metadata is stored in each folder's `.audio_fingerprints.json` file:

```json
{
  "version": 1,
  "files": {
    "song1.wav": {
      "fingerprints": { ... }
    }
  },
  "excluded_files": ["test.wav"],
  "is_reference_folder": false,
  "ignore_fingerprints": false
}
```

**New Fields:**
- `is_reference_folder` (bool) - True if folder should have higher matching weight
- `ignore_fingerprints` (bool) - True if folder should be excluded from matching

**Backward Compatibility:**
- Old caches without these fields default to `false`
- Existing cache data (files, excluded_files) is preserved when toggling flags
- Cache migration is handled automatically by `load_fingerprint_cache()`

## Batch Operations Fix

### Problem

The "Batch Rename" and "Convert WAV→MP3" menu items in the Library tab's "More" menu were not enabling properly when files were present.

### Root Cause

The `enabled` property was evaluated when the menu was created, not when it was opened. This meant that if files were loaded after the menu was created, the menu items would remain disabled.

### Solution

Added a dynamic property and `onAboutToShow` handler to re-evaluate the file count:

```javascript
Menu {
    id: moreMenu
    
    property int fileCount: 0
    
    onAboutToShow: {
        // Update file count when menu is about to show
        fileCount = fileListModel ? fileListModel.count() : 0
    }
    
    MenuItem {
        text: "Batch Rename"
        enabled: moreMenu.fileCount > 0
        // ...
    }
    
    MenuItem {
        text: "Convert WAV→MP3"
        enabled: moreMenu.fileCount > 0
        // ...
    }
}
```

**Changes:**
1. Added `fileCount` property to the menu
2. Added `onAboutToShow` handler that updates `fileCount` from `fileListModel.count()`
3. Changed `enabled` expressions to use `moreMenu.fileCount` instead of direct model access

## Testing

### Unit Tests

**test_folder_context_menu.py** - Tests backend functionality:
- `test_folder_reference()` - Tests reference folder flag toggling
- `test_folder_ignore()` - Tests ignore flag toggling
- `test_combined_flags()` - Tests that flags are independent
- `test_cache_structure()` - Tests that existing cache data is preserved

### Manual Testing Checklist

1. **Folder Context Menu Display**
   - [ ] Right-click on folder shows context menu
   - [ ] All menu items are visible
   - [ ] Menu appears at cursor position

2. **Generate Fingerprints**
   - [ ] Starts background generation
   - [ ] Switches to Fingerprints tab
   - [ ] Shows progress updates
   - [ ] Handles empty folders gracefully

3. **Reference Folder Toggle**
   - [ ] Toggles on first click
   - [ ] Menu text updates to show current state
   - [ ] Persists across app restarts
   - [ ] Works independently of ignore flag

4. **Ignore Fingerprints Toggle**
   - [ ] Toggles on first click
   - [ ] Menu text updates to show current state
   - [ ] Persists across app restarts
   - [ ] Works independently of reference flag

5. **Generate Waveforms**
   - [ ] Generates waveforms in background
   - [ ] Handles empty folders gracefully
   - [ ] Doesn't block UI
   - [ ] Waveforms appear when files are selected

6. **Batch Operations**
   - [ ] "Batch Rename" is enabled when files are present
   - [ ] "Convert WAV→MP3" is enabled when files are present
   - [ ] Both are disabled when no files are present
   - [ ] Menu updates when switching folders

## Future Enhancements

1. **Progress Indicators**
   - Add progress bar for waveform generation
   - Show estimated time remaining

2. **Folder Badges**
   - Visual indicators in folder tree for reference/ignored folders
   - Icon overlays or color coding

3. **Bulk Operations**
   - Apply reference/ignore flags to multiple folders at once
   - Folder selection mode

4. **Settings Integration**
   - Default fingerprint algorithm for folder operations
   - Option to auto-generate waveforms on folder selection

5. **Matching Algorithm**
   - Actually use the reference folder weighting in matching
   - Respect the ignore flag in matching operations
