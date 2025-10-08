# Auto-Switch to Annotations Tab Feature

## Overview

The "Auto-switch to Annotations" feature automatically switches to the Annotations tab when you double-click a file in the Library tab. This streamlines the workflow for users who frequently annotate audio files.

**Status**: ✅ Implemented (Phase 11)

## Features

### 1. Toolbar Checkbox
- Checkbox labeled "Auto-switch to Annotations" in the main toolbar
- Located between playback controls and theme toggle
- Checked by default for optimal workflow
- Tooltip explains functionality: "Automatically switch to Annotations tab when selecting a file"

### 2. Persistent Setting
- Setting persists across application sessions
- Stored in application preferences
- Independent for each user

### 3. Smart Behavior
- **Single-click**: Loads file (does not switch tabs)
- **Double-click**: Loads file, plays audio, AND switches to Annotations tab (if enabled)
- No tab switching when checkbox is unchecked

## Usage

### Enabling Auto-Switch

1. Launch AudioBrowser-QML
2. The checkbox is **checked by default** in the toolbar
3. Double-click any file in the Library tab
4. Application automatically switches to Annotations tab
5. Audio begins playing

### Disabling Auto-Switch

1. Uncheck the "Auto-switch to Annotations" checkbox in toolbar
2. Double-click files in Library tab
3. Audio plays but you remain in the Library tab
4. Manually switch to Annotations tab if needed

## Workflow Examples

### Example 1: Annotation-Focused Workflow (Auto-Switch ON)

**Scenario**: Annotating practice recordings

1. ✅ Checkbox is checked (default)
2. Browse files in Library tab
3. Double-click "Practice_2025-01-15.wav"
4. → **Automatically switches to Annotations tab**
5. Audio plays, waveform displays
6. Add annotations while listening
7. Return to Library tab for next file
8. Repeat process

**Benefits**:
- Fewer clicks required
- Faster workflow for annotation tasks
- Always in the right tab for annotating

### Example 2: Library Management Workflow (Auto-Switch OFF)

**Scenario**: Organizing and renaming files

1. Uncheck the checkbox
2. Double-click files to preview
3. Stay in Library tab to:
   - View file metadata
   - Mark best/partial takes
   - Batch rename files
   - Update provided names
4. No unwanted tab switching

**Benefits**:
- Stay focused on library management
- Preview files without leaving Library tab
- Better for batch operations

### Example 3: Mixed Workflow

**Scenario**: Review session then annotation

1. Start with checkbox **unchecked**
2. Quick preview multiple files in Library
3. Find the file needing annotations
4. **Check the checkbox**
5. Double-click file → Switches to Annotations
6. Work on detailed annotations
7. When done, uncheck for more browsing

## Technical Implementation

### Backend (Python)

**SettingsManager** (`backend/settings_manager.py`):
- `SETTINGS_KEY_AUTO_SWITCH_ANNOTATIONS` = "preferences/auto_switch_annotations"
- `getAutoSwitchAnnotations()` → Returns `bool` (default: `True`)
- `setAutoSwitchAnnotations(enabled: bool)` → Saves preference
- Handles string/boolean conversion for QSettings compatibility

### Frontend (QML)

**Main Window** (`qml/main.qml`):
- `autoSwitchCheckbox` CheckBox in toolbar
- Bound to `settingsManager.getAutoSwitchAnnotations()`
- Updates setting on checked state change
- Styled to match application theme

**Library Tab** (`qml/tabs/LibraryTab.qml`):
- Double-click handler checks `autoSwitchCheckbox.checked`
- If enabled: `tabBar.currentIndex = 1` (Annotations tab)
- If disabled: No tab switching occurs

### Data Storage

Setting stored in QSettings:
- **Key**: `preferences/auto_switch_annotations`
- **Type**: Boolean
- **Default**: `true`
- **Location**: Platform-specific QSettings storage

## Benefits

### For Annotation-Heavy Users
- Saves time with automatic tab switching
- Reduces repetitive clicking
- Streamlines annotation workflow
- Natural flow: select file → annotate

### For Flexible Users
- Toggle on/off as needed
- Adapt to different tasks
- No forced behavior
- User control over workflow

### For New Users
- Sensible default (enabled)
- Guides users to Annotations tab
- Discovers annotation features naturally
- Tooltip provides explanation

## Comparison with Original

### Original AudioBrowser
- Checkbox in toolbar: "Auto-switch to Annotations"
- Same behavior: switches on file selection
- Setting persists across sessions

### QML Implementation
- ✅ Feature parity achieved
- Same checkbox location and text
- Same default (enabled)
- Enhanced with tooltip for better UX

## Related Features

This feature works seamlessly with:
- **Multi-user annotations**: Switch to view merged annotations
- **Annotation filters**: Auto-switch respects current filter settings
- **Keyboard shortcuts**: Ctrl+1/Ctrl+2 to manually switch tabs
- **Recent files**: Auto-switch works with recently opened files

## Future Enhancements

Potential improvements:
- Option to switch on single-click (not just double-click)
- Remember per-folder preference (some folders for annotation, others not)
- Smart switching: only switch if file has existing annotations
- Configurable target tab (not just Annotations)

## Testing

Run the test suite to verify implementation:

```bash
cd AudioBrowser-QML
python3 test_auto_switch_annotations.py
```

Tests verify:
- Settings key exists
- Backend methods work correctly
- QML checkbox present
- Tab switching logic integrated

## Summary

The auto-switch to Annotations feature provides:
- ✅ Streamlined annotation workflow
- ✅ User control via toolbar checkbox
- ✅ Persistent preferences
- ✅ Smart default behavior
- ✅ Tooltip for discoverability

**Feature Parity**: Fully implements the auto-switch feature from original AudioBrowser, matching behavior and defaults. Advances QML version from 89% to 90% feature parity.

---

**Document Version**: 1.0  
**Last Updated**: January 2025  
**Implementation Phase**: Phase 11  
**Status**: ✅ Complete
