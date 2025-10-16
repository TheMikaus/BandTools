# Quick Access Features - User Guide

This guide explains the quick access features that allow you to perform actions across different tabs without manually switching between them.

## Context Menu Features

### Adding Annotations from File List

You can add an annotation to any file directly from the Library without manually switching to the Annotations tab:

1. **Right-click** on a file in the Library file list
2. Select **"📝 Add Annotation..."** from the context menu
3. The application will:
   - Automatically load the file (if not already playing)
   - Switch to the Annotations tab
   - Open the annotation dialog at the current playback position
4. Enter your annotation details and save

**Benefits:**
- No need to manually switch tabs
- File is loaded automatically
- Annotation dialog opens at the right position

### Creating Clips from File List

You can create a clip from any file directly from the Library:

1. **Right-click** on a file in the Library file list
2. Select **"✂ Create Clip..."** from the context menu
3. The application will:
   - Automatically load the file (if not already playing)
   - Switch to the Clips tab
   - Open the clip creation dialog
4. Set your clip start/end times and save

**Benefits:**
- Quick clip creation without navigation
- File is loaded automatically
- Default clip duration is set (5 seconds from current position)

## Waveform Interaction

### Clicking Clip Markers

When viewing the waveform in the Annotations tab, you'll see visual markers for any clips that have been created:

**Single Click:**
- Click a clip marker to **seek** to the start of that clip
- Useful for quickly navigating to specific clips while reviewing annotations

**Double Click:**
- Double-click a clip marker to **edit** that clip
- The application will:
  - Switch to the Clips tab
  - Select the clip in the list
  - Open the clip edit dialog
- Make your changes and save

**Benefits:**
- Visual overview of clips while working with annotations
- Quick navigation to clip positions
- Direct access to clip editing

### Clicking Annotation Markers

**Double Click:**
- Double-click an annotation marker on the waveform to edit it
- The annotation edit dialog opens immediately
- Make your changes and save

**Single Click:**
- Click an annotation marker to seek to that annotation's timestamp
- Useful for quickly navigating to annotated positions

## Keyboard Shortcuts

These shortcuts work in conjunction with the signal system:

### Global Shortcuts

- **Space**: Play/Pause
- **Escape**: Stop playback
- **Left Arrow**: Seek backward 5 seconds
- **Right Arrow**: Seek forward 5 seconds
- **+**: Increase volume
- **-**: Decrease volume

### Tab Switching

- **Ctrl+1**: Library tab
- **Ctrl+2**: Annotations tab
- **Ctrl+3**: Clips tab
- **Ctrl+4**: Sections tab
- **Ctrl+5**: Folder Notes tab

### Feature Shortcuts

- **Ctrl+A**: Add annotation (when not in text field)
- **[**: Set clip start marker
- **]**: Set clip end marker
- **Ctrl+O**: Open folder

## Now Playing Panel

The Now Playing panel provides quick annotation access while listening:

1. **Expand** the panel using the ▼ button (if collapsed)
2. **Type** your annotation in the quick annotation field
3. **Press Enter** or click the button
4. The annotation is added at the current playback position
5. If "Auto-switch to Annotations" is enabled, you'll automatically see the Annotations tab

**Benefits:**
- No interruption to playback
- Quick capture of thoughts while listening
- Optional automatic tab switching

## Tips and Tricks

### Efficient Workflow: Annotation Review

1. Load your audio file in the Library
2. Switch to Annotations tab (Ctrl+2)
3. Use the waveform to:
   - See all annotations at once
   - Click markers to jump between annotations
   - Double-click to edit annotations
   - View clip positions relative to annotations

### Efficient Workflow: Clip Creation

**Method 1: Keyboard Markers**
1. Start playback
2. Press **[** when you reach the clip start
3. Press **]** when you reach the clip end
4. The clip dialog opens automatically
5. Name your clip and save

**Method 2: Context Menu**
1. Right-click the file
2. Select "Create Clip..."
3. Adjust start/end times
4. Save

### Efficient Workflow: Best Take Review

1. Right-click files and mark as "Best Take" (★)
2. Use the filter in Library to show only best takes
3. Right-click any best take
4. Add annotations or create clips directly from the context menu

## Troubleshooting

**Q: Context menu doesn't show?**
- Make sure you're right-clicking directly on a file row
- Try clicking the file first, then right-clicking

**Q: Tab doesn't switch when using context menu?**
- This is expected - the feature is designed to switch tabs automatically
- If it's not switching, verify the file loaded successfully

**Q: Clip markers don't appear on waveform?**
- Make sure you're on the Annotations tab (clips are shown there)
- Verify clips exist for the current file
- Check that the waveform has been generated

**Q: Double-click not working on markers?**
- Try clicking more slowly (system may interpret as two single clicks)
- Make sure you're clicking directly on the marker
- Check if a dialog is already open

## Related Documentation

- [Keyboard Shortcuts](../user_guides/KEYBOARD_SHORTCUTS.md) - Complete keyboard reference
- [Signal Connections](../technical/SIGNAL_CONNECTIONS.md) - Technical implementation details
- [Annotations Guide](../user_guides/ANNOTATIONS.md) - Detailed annotation features
- [Clips Guide](../user_guides/CLIPS.md) - Detailed clip management features
