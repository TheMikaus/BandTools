# QML Signal Connections Documentation

This document describes all the signal connections in the AudioBrowser QML application and how they enable cross-component communication for user features.

## Overview

The application uses Qt's signal/slot mechanism extensively to enable:
- Cross-tab communication (e.g., switching tabs when requesting features)
- Component interaction (e.g., clicking markers to edit annotations)
- User workflow automation (e.g., loading files and opening dialogs in one action)

## Signal Flow Diagrams

### Context Menu → Annotation Feature

When a user right-clicks a file in the Library and selects "Add Annotation":

```
User Action: Right-click file → Add Annotation
  ↓
FileContextMenu.annotationRequested()
  ↓
LibraryTab.onAnnotationRequested:
  - Loads file in audio engine (if different)
  - Emits requestAnnotationTab(filePath)
  ↓
main.qml.onRequestAnnotationTab:
  - Sets tabBar.currentIndex = 1 (Annotations tab)
  - Calls annotationsTab.openAddDialog()
  ↓
Result: User is on Annotations tab with dialog open
```

### Context Menu → Clip Feature

When a user right-clicks a file in the Library and selects "Create Clip":

```
User Action: Right-click file → Create Clip
  ↓
FileContextMenu.clipRequested()
  ↓
LibraryTab.onClipRequested:
  - Loads file in audio engine (if different)
  - Emits requestClipsTab(filePath)
  ↓
main.qml.onRequestClipsTab:
  - Sets tabBar.currentIndex = 2 (Clips tab)
  - Calls clipsTab.openAddClipDialog()
  ↓
Result: User is on Clips tab with clip creation dialog open
```

### Waveform Clip Marker → Edit Clip

When a user double-clicks a clip marker on the waveform in the Annotations tab:

```
User Action: Double-click clip marker
  ↓
WaveformDisplay.clipDoubleClicked(clipIndex)
  ↓
AnnotationsTab.onClipDoubleClicked:
  - Emits requestClipEdit(clipIndex)
  ↓
main.qml.onRequestClipEdit:
  - Sets tabBar.currentIndex = 2 (Clips tab)
  - Calls clipsTab.selectAndEditClip(clipIndex)
  ↓
ClipsTab.selectAndEditClip:
  - Selects the clip in the list
  - Opens clip edit dialog
  ↓
Result: User is on Clips tab with selected clip in edit mode
```

### Waveform Clip Marker → Seek to Clip

When a user single-clicks a clip marker on the waveform:

```
User Action: Click clip marker
  ↓
WaveformDisplay.clipClicked(clipIndex)
  ↓
AnnotationsTab.onClipClicked:
  - Gets clip data from clipManager
  - Calls audioEngine.seek(clip.start_ms)
  ↓
Result: Playback position moves to clip start
```

### Waveform Annotation Marker → Edit Annotation

When a user double-clicks an annotation marker on the waveform:

```
User Action: Double-click annotation marker
  ↓
WaveformDisplay.annotationDoubleClicked(annotationData)
  ↓
AnnotationsTab.onAnnotationDoubleClicked:
  - Finds annotation index
  - Calls openEditDialog(index)
  ↓
Result: Annotation edit dialog opens
```

## Component Signal Reference

### WaveformDisplay

**Signals:**
- `annotationDoubleClicked(var annotationData)` - Emitted when annotation marker is double-clicked
- `clipClicked(int clipIndex)` - Emitted when clip marker is clicked
- `clipDoubleClicked(int clipIndex)` - Emitted when clip marker is double-clicked

**Usage:**
- Displayed in AnnotationsTab
- Shows both annotation and clip markers
- Enables direct interaction with markers

### FileContextMenu

**Signals:**
- `annotationRequested()` - User wants to add annotation to selected file
- `clipRequested()` - User wants to create clip from selected file
- `propertiesRequested()` - User wants to see file properties
- `editLibraryNameRequested()` - User wants to edit library name

**Usage:**
- Shown on right-click in Library file list
- All signals connected in LibraryTab
- Enables quick access to features from file list

### LibraryTab

**Signals:**
- `requestAnnotationTab(string filePath)` - Request to switch to Annotations tab
- `requestClipsTab(string filePath)` - Request to switch to Clips tab

**Usage:**
- Connected in main.qml
- Enables tab switching from context menu actions

### AnnotationsTab

**Signals:**
- `requestClipEdit(int clipIndex)` - Request to edit a specific clip

**Usage:**
- Connected in main.qml
- Enables clip editing from waveform markers

### BestTakeIndicator / PartialTakeIndicator

**Signals:**
- `clicked()` - User clicked the indicator

**Usage:**
- Shown in file list
- Connected to toggle best/partial take status
- Provides quick visual feedback

### NowPlayingPanel

**Signals:**
- `annotationRequested(string text)` - User entered annotation text

**Usage:**
- Connected in main.qml
- Adds annotation at current playback position
- Can auto-switch to Annotations tab if enabled

## Tab Index Reference

For programmatic tab switching:

- 0: Library
- 1: Annotations
- 2: Clips
- 3: Sections
- 4: Folder Notes
- 5: Fingerprints

## Testing Signal Connections

Use the `test_signal_connections.py` script to verify all signals are connected:

```bash
python3 test_signal_connections.py
```

This will check all signal declarations and verify they have handlers.

## Best Practices

1. **Signal Naming**: Use descriptive names that indicate the action (e.g., `requestAnnotationTab` not `switchTab`)

2. **Handler Naming**: Qt automatically creates handlers with `on` prefix (e.g., `onRequestAnnotationTab`)

3. **Cross-Component Communication**: Use signals to decouple components
   - Tabs shouldn't directly reference each other
   - Use parent (main.qml) to coordinate tab switching

4. **File Loading**: When switching tabs to work with a file:
   - Load the file in audioEngine first
   - Then switch tabs
   - Then open dialogs

5. **Error Handling**: Always check if objects exist before using them:
   ```qml
   if (audioEngine && audioEngine.getCurrentFile() !== "") {
       // Safe to use
   }
   ```

## Future Enhancements

Potential areas for additional signal connections:

1. **Sections Tab**: Add WaveformDisplay and connect clip/annotation signals
2. **Fingerprints Tab**: Add signals for match selection
3. **Folder Notes**: Add signals for note linking to files
4. **Practice Statistics**: Add signals for goal creation from statistics view

## Troubleshooting

**Signal not firing:**
- Check signal is declared with correct parameters
- Verify handler name matches (case-sensitive)
- Check component is actually instantiated

**Tab not switching:**
- Verify tabBar.currentIndex is being set
- Check tab index is correct (0-based)
- Ensure tab component has correct id

**Dialog not opening:**
- Verify dialog id is correct
- Check dialog's open() method exists
- Ensure dialog is instantiated (not in conditional)
