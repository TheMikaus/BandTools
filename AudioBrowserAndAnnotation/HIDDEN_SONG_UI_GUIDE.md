# Hidden Song Feature - Visual UI Guide

## AudioBrowser-QML UI Changes

### 1. Library Tab - More Menu (⋮)

**Location:** Library tab toolbar, rightmost button

**New Menu Item:**
```
┌─────────────────────────────────┐
│ ⋮ More Menu                     │
├─────────────────────────────────┤
│ 🔍 Find Audio Files             │
│ 🔄 Match All Fingerprints       │
│ ────────────────────────────────│
│ 📦 Batch Convert WAV to MP3     │
│ ────────────────────────────────│
│ ★ Best Takes                 ✓  │  ← Existing filter
│ ◐ Partial Takes              ✓  │  ← Existing filter
│ 👁 Show Hidden Songs         ✓  │  ← NEW! Toggle hidden songs
│ ────────────────────────────────│
│ 📊 Practice Stats               │
│ ...                             │
└─────────────────────────────────┘
```

**Behavior:**
- Unchecked (default): Hidden songs are NOT shown in file list
- Checked: Hidden songs ARE shown in file list
- Checkmark (✓) appears when enabled

### 2. File Context Menu (Right-Click)

**Location:** Right-click on any file in Library tab

**New Menu Item:**
```
┌─────────────────────────────────┐
│ File Context Menu               │
├─────────────────────────────────┤
│ ▶ Play                          │
│ ────────────────────────────────│
│ 📝 Add Annotation...            │
│ ✂ Create Clip...                │
│ ────────────────────────────────│
│ ★ Mark as Best Take             │  ← Existing option
│ ◐ Mark as Partial Take          │  ← Existing option
│ 🚫 Hide Song                    │  ← NEW! (or "👁 Unhide Song")
│ ────────────────────────────────│
│ ✏ Edit Library Name...          │
│ ────────────────────────────────│
│ 📁 Show in Explorer             │
│ 📋 Copy Path                    │
│ ────────────────────────────────│
│ ℹ Properties                    │
└─────────────────────────────────┘
```

**Dynamic Text:**
- When file is NOT hidden: Shows "🚫 Hide Song"
- When file IS hidden: Shows "👁 Unhide Song"

## AudioBrowserOrig UI Changes

### 1. View Menu

**Location:** Top menu bar → View

**New Menu Item:**
```
┌─────────────────────────────────┐
│ View Menu                       │
├─────────────────────────────────┤
│ Save Window Layout           ⌘⇧L│
│ Restore Window Layout        ⌘⇧R│
│ Reset to Default Layout         │
│ ────────────────────────────────│
│ ☑ Show Hidden Songs             │  ← NEW! Checkbox toggle
└─────────────────────────────────┘
```

**Behavior:**
- Unchecked (default): Hidden songs are NOT shown in file list
- Checked: Hidden songs ARE shown in file list
- Checkbox state persists during session

### 2. File Context Menu (Right-Click)

**Location:** Right-click on any file in the file tree

**New Menu Item:**
```
┌─────────────────────────────────┐
│ File Context Menu               │
├─────────────────────────────────┤
│ ▶ Play                          │
│ 📝 Add annotation at 0:00       │
│ ────────────────────────────────│
│ ✏ Quick rename...               │
│ 📋 Copy filename to provided... │
│ ────────────────────────────────│
│ 🔍 Jump to in Library tab       │
│ 🔍 Jump to in Annotations tab   │
│ ────────────────────────────────│
│ 📁 Open in Explorer             │
│ ────────────────────────────────│
│ Mark as Best Take               │  ← Existing option
│ Mark as Partial Take            │  ← Existing option
│ Mark as Reference Song          │  ← Existing option
│ 🚫 Hide Song                    │  ← NEW! (or "👁 Unhide Song")
│ ────────────────────────────────│
│ Export to Mono                  │
│ Regenerate Waveform             │
│ ...                             │
└─────────────────────────────────┘
```

**Dynamic Text:**
- When file is NOT hidden: Shows "🚫 Hide Song"
- When file IS hidden: Shows "👁 Unhide Song"

## User Workflows

### Workflow 1: Hide a Song

**AudioBrowser-QML:**
1. Navigate to Library tab
2. Right-click on a file
3. Click "🚫 Hide Song"
4. File disappears from list
5. Confirmation: File is hidden

**AudioBrowserOrig:**
1. Right-click on a file in the tree
2. Click "🚫 Hide Song"
3. Dialog: "File 'song.wav' is now hidden. Hidden songs can be shown via View > Show Hidden Songs."
4. Click OK
5. File disappears from list

### Workflow 2: View Hidden Songs

**AudioBrowser-QML:**
1. In Library tab, click More menu (⋮)
2. Click "👁 Show Hidden Songs" (adds checkmark)
3. File list refreshes to include hidden songs
4. Hidden songs now visible

**AudioBrowserOrig:**
1. Open View menu
2. Click "Show Hidden Songs" (adds checkmark)
3. File list refreshes to include hidden songs
4. Hidden songs now visible

### Workflow 3: Unhide a Song

**AudioBrowser-QML:**
1. Enable "Show Hidden Songs" (see Workflow 2)
2. Right-click on the hidden song
3. Click "👁 Unhide Song"
4. File remains visible (even if you disable "Show Hidden Songs")

**AudioBrowserOrig:**
1. Enable View > Show Hidden Songs
2. Right-click on the hidden song
3. Click "👁 Unhide Song"
4. Dialog: "File 'song.wav' is now unhidden."
5. Click OK
6. File remains visible

## Visual Indicators

### File List Display

**Without "Show Hidden Songs" enabled:**
```
Files (5)
├─ song1.wav
├─ song2.wav        ★ (best take)
├─ song3.wav        ◐ (partial take)
├─ song5.wav
└─ song6.wav

(song4.wav is hidden - not shown)
```

**With "Show Hidden Songs" enabled:**
```
Files (6)
├─ song1.wav
├─ song2.wav        ★ (best take)
├─ song3.wav        ◐ (partial take)
├─ song4.wav        [Hidden - shown because toggle enabled]
├─ song5.wav
└─ song6.wav
```

**Note:** The actual visual indicator for hidden files (when shown) may vary by implementation. This is illustrative.

## Keyboard Shortcuts

Currently, there are no keyboard shortcuts for the hidden song feature. Future enhancement could add:
- `Ctrl+H` - Toggle show hidden songs
- `H` - Mark selected file as hidden
- `Shift+H` - Unhide selected file

## Icons Reference

- 🚫 - Hide Song icon
- 👁 - Show/Unhide icon  
- ⋮ - More menu icon
- ★ - Best take indicator
- ◐ - Partial take indicator
- ✓ - Checkmark (enabled state)

## Tooltips

**QML - File Context Menu:**
- "🚫 Hide Song" - Tooltip: None (clear from label)
- "👁 Unhide Song" - Tooltip: None (clear from label)

**QML - More Menu:**
- "👁 Show Hidden Songs" - Tooltip: "Show or hide songs marked as hidden"

**AudioBrowserOrig - File Context Menu:**
- "🚫 Hide Song" - Tooltip: "Hide this file from the file list (can be shown via View menu)"
- "👁 Unhide Song" - Tooltip: "Make this file visible in the file list"

**AudioBrowserOrig - View Menu:**
- "Show Hidden Songs" - No tooltip (menu items don't show tooltips)

## Color Scheme

The hidden song feature uses the existing theme colors:
- Menu items use default text color
- Hover state uses default highlight color
- No special colors for hidden songs (consistent with best take/partial take which also use no special colors in the list)

## Responsive Behavior

**When hiding a currently playing song:**
- The song continues to play
- User can still see playback controls
- Song disappears from list (if "Show Hidden Songs" is off)

**When filtering with other options:**
- Hidden songs are excluded FIRST, then other filters apply
- Example: If filtering for "Best Takes" and a file is both a best take AND hidden:
  - Without "Show Hidden Songs": File is NOT shown
  - With "Show Hidden Songs": File IS shown

**When searching/sorting:**
- Hidden songs are excluded from search results (unless "Show Hidden Songs" is enabled)
- Hidden songs are excluded from sort (unless "Show Hidden Songs" is enabled)

## Accessibility Notes

- All menu items are keyboard accessible via standard menu navigation
- Screen readers will read the icon + text (e.g., "Hide Song button")
- Checkable menu items announce their checked state
- No color-only indicators (text always accompanies icons)

## Platform Compatibility

The hidden song feature works identically on:
- ✓ Windows
- ✓ macOS  
- ✓ Linux

Emoji icons (🚫, 👁, etc.) display on all platforms, though appearance may vary slightly based on OS emoji rendering.
