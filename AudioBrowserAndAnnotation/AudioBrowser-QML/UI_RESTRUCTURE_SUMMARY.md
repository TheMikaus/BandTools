# UI Restructure and Annotation Tab Fix - Summary

## Problem Statement

The AudioBrowser QML application had two main issues:

1. **Annotation page does not populate** - When clicking or double-clicking a song from the library page, the annotation tab would not properly display annotations for the selected file.

2. **Library should always be visible** - The Library was grouped as a tab along with other tabs (Annotations, Clips, etc.), making it necessary to switch tabs to access the file list. The requirement was to make the Library always visible at the bottom of the panel.

## Solution Implemented

### 1. Fixed Annotation Tab Population

**Problem:** The LibraryTab component tried to directly access `tabBar.currentIndex` from within its scope, but `tabBar` was defined in the parent `main.qml` and was not accessible.

**Solution:**
- Added a new signal `switchToAnnotationsTab()` to LibraryTab
- Updated the double-click handler to emit this signal instead of directly accessing `tabBar`
- Connected the signal in main.qml to properly switch to the Annotations tab
- Updated single-click handler to support auto-switch functionality when enabled in settings

**Code Changes in LibraryTab.qml:**

```qml
// Added new signal
signal switchToAnnotationsTab()

// Updated double-click handler
onDoubleClicked: {
    console.log("Double-clicked file:", model.filepath)
    audioEngine.loadAndPlay(model.filepath)
    libraryTab.switchToAnnotationsTab()  // Use signal instead of direct access
}

// Updated single-click handler
onClicked: function(mouse) {
    // ... existing code ...
    audioEngine.loadAndPlay(model.filepath)
    
    // Auto-switch to Annotations tab if enabled
    if (settingsManager && settingsManager.getAutoSwitchAnnotations()) {
        libraryTab.switchToAnnotationsTab()
    }
}
```

**Code Changes in main.qml:**

```qml
LibraryTab {
    id: libraryTab
    
    // Connect signal for double-click on file to switch to Annotations tab
    onSwitchToAnnotationsTab: {
        tabBar.currentIndex = 0  // Annotations is now index 0
    }
}
```

### 2. Restructured UI Layout

**Problem:** Library was included as a tab in the TabBar, requiring users to switch tabs to access files.

**Solution:**
- Removed Library from the TabBar
- Created a new split layout with:
  - Tabs (Annotations, Clips, Sections, Folder Notes, Fingerprints) at the top
  - Library panel always visible at the bottom
- Adjusted all tab indices throughout the application
- Updated keyboard shortcuts to match new tab order

**Before:**
```
TabBar: [Library, Annotations, Clips, Sections, Folder Notes, Fingerprints]
StackLayout: [corresponding tab contents]
```

**After:**
```
┌─────────────────────────────────────────────┐
│ TabBar: [Annotations, Clips, Sections,     │
│          Folder Notes, Fingerprints]       │
├─────────────────────────────────────────────┤
│                                             │
│ Tab Content (top half)                      │
│ - Waveform and annotation controls          │
│ - Clip management                           │
│ - Section markers                           │
│ - Folder notes                              │
│ - Fingerprint matching                      │
│                                             │
├─────────────────────────────────────────────┤
│                                             │
│ Library Panel (always visible, bottom)      │
│ - Folder tree on left                       │
│ - File list on right                        │
│ - Batch operations toolbar                  │
│                                             │
└─────────────────────────────────────────────┘
```

## Tab Index Changes

All tab indices have been adjusted:

| Tab Name       | Old Index | New Index | Keyboard Shortcut |
|----------------|-----------|-----------|-------------------|
| Library        | 0         | N/A       | (always visible)  |
| Annotations    | 1         | 0         | Ctrl+1            |
| Clips          | 2         | 1         | Ctrl+2            |
| Sections       | 3         | 2         | Ctrl+3            |
| Folder Notes   | 4         | 3         | Ctrl+4            |
| Fingerprints   | 5         | 4         | Ctrl+5            |

## Signal Connection Updates

All signal connections that reference tab indices have been updated:

- `onSwitchToAnnotationsTab`: Now sets `tabBar.currentIndex = 0` (was 1)
- `onRequestAnnotationTab`: Now sets `tabBar.currentIndex = 0` (was 1)
- `onRequestClipsTab`: Now sets `tabBar.currentIndex = 1` (was 2)
- `onRequestClipEdit`: Now sets `tabBar.currentIndex = 1` (was 2)
- `NowPlayingPanel.onAnnotationRequested`: Now sets `tabBar.currentIndex = 0` (was 1)

## User Experience Improvements

1. **Better Workflow**: Users can now see the file library at all times while working in other tabs
2. **Easier Navigation**: No need to switch back to Library tab to select different files
3. **Working Annotation Switching**: Clicking/double-clicking files now properly populates the annotation tab
4. **Auto-Switch Support**: Single-click with auto-switch setting enabled now works correctly
5. **More Screen Space**: The tab content area (top) and library (bottom) can be sized independently

## Testing

Created comprehensive test suite in `test_ui_restructure.py` that validates:
- Library is removed from TabBar
- Library panel is always visible
- Annotations tab is first in TabBar
- Signal connections work properly
- Tab indices are correct in shortcuts and signal handlers
- Auto-switch functionality is implemented

All tests pass successfully.

## Backward Compatibility

This is a UI restructuring change that does not affect:
- Data storage formats
- Annotation files
- Audio file handling
- Existing features and functionality

Users will notice the improved layout immediately but all existing functionality remains intact.

## Files Modified

1. `qml/main.qml` - Major restructure of layout and tab organization
2. `qml/tabs/LibraryTab.qml` - Added signal and updated click handlers
3. `test_ui_restructure.py` - New test file to validate changes

## Future Enhancements

Potential improvements that could build on this change:
- Make the split between top tabs and library resizable
- Add a collapse/expand button for the library panel
- Save/restore the split ratio in user preferences
- Add drag-and-drop between library and tabs for quick operations
