# Visual Guide: Workspace Layouts & Status Bar Progress Indicators

**Version**: 1.0  
**Date**: January 2025  
**Status**: Implementation Complete

---

## Overview

This guide provides visual descriptions of the new features added to AudioBrowser. Since these are GUI features, this document describes what users will see and how to interact with the new functionality.

---

## 1. View Menu (New)

### Menu Location
```
Menu Bar
├─ File
├─ View  ← NEW MENU
└─ Help
```

### View Menu Contents
```
View
├─ Save Window Layout         Ctrl+Shift+L
├─ Restore Window Layout      Ctrl+Shift+R
└─ Reset to Default Layout
```

**Visual Description**:
- New "View" menu appears between "File" and "Help" in the menu bar
- Menu contains 3 actions for managing workspace layouts
- First two items have keyboard shortcuts displayed
- Standard menu styling consistent with application theme

---

## 2. Workspace Layout Features

### 2.1 Default Window State

**First Launch (or after reset):**
```
┌────────────────────────────────────────────────────────┐
│ AudioBrowser - Version 1.xxx               [_][□][X]   │
├────────────────────────────────────────────────────────┤
│ File   View   Help                                     │
├────────────────────────────────────────────────────────┤
│ [↶] [↷] | [⬆] | [☑ Auto-switch to Annotations] | [☁]  │
├────────────────────────────────────────────────────────┤
│ Band Practice Directory: /path/to/practice             │
├───────────────────────┬────────────────────────────────┤
│                       │                                │
│   File Tree           │   Content Area                 │
│   (40% width)         │   (60% width)                  │
│                       │                                │
│   [Filter: ______]    │   [Tabs: Folder | Library |   │
│   ├─ Folder1/         │          Annotations]         │
│   ├─ Folder2/         │                                │
│   └─ Recording1.wav   │   [Content displays here]     │
│                       │                                │
│                       │                                │
│                       │                                │
├───────────────────────┴────────────────────────────────┤
│ 12 files | 5 reviewed | 2 best takes                  │
└────────────────────────────────────────────────────────┘
Window Size: 1360 x 900
Splitter Ratio: 40:60 (left:right)
```

### 2.2 Custom Layout Example

**After User Customization:**
```
┌──────────────────────────────────────────────────────────────────┐
│ AudioBrowser - Version 1.xxx                       [_][□][X]     │
├──────────────────────────────────────────────────────────────────┤
│ File   View   Help                                               │
├──────────────────────────────────────────────────────────────────┤
│ [↶] [↷] | [⬆] | [☑ Auto-switch to Annotations] | [☁]            │
├──────────────────────────────────────────────────────────────────┤
│ Band Practice Directory: /path/to/practice                       │
├──────────────────┬───────────────────────────────────────────────┤
│                  │                                               │
│   File Tree      │                                               │
│   (30% width)    │   Content Area (70% width)                   │
│                  │                                               │
│   [Filter: ___]  │   [Tabs: Folder | Library | Annotations]    │
│   ├─ Song1.wav   │                                               │
│   ├─ Song2.wav   │   [Larger waveform display]                 │
│   └─ Song3.wav   │   [More annotation space]                    │
│                  │                                               │
│                  │                                               │
│                  │                                               │
├──────────────────┴───────────────────────────────────────────────┤
│ 12 files | 5 reviewed | 2 best takes                            │
└──────────────────────────────────────────────────────────────────┘
Window Size: 1600 x 1000 (user customized)
Splitter Ratio: 30:70 (user customized for wider content area)
```

**How It Works**:
1. User resizes window to 1600x1000
2. User drags splitter left to give more space to content
3. User presses **Ctrl+Shift+L** to save
4. ✅ Status bar briefly shows: "Window layout saved"
5. Next launch: Window automatically opens at 1600x1000 with 30:70 split

---

## 3. Status Bar Progress Indicators

### 3.1 Status Bar Layout

**Before (No Progress):**
```
┌────────────────────────────────────────────────────────┐
│ 12 files | 5 reviewed | 3 without names | 2 best takes│
└────────────────────────────────────────────────────────┘
         ↑ File statistics (left-aligned)
```

**During Progress:**
```
┌──────────────────────────────────────────────────────────────────────┐
│ 12 files | 5 reviewed           Generating waveforms: 5/20  [████░░░░]│
└──────────────────────────────────────────────────────────────────────┘
         ↑                                    ↑                    ↑
    File stats                         Progress label          Progress bar
    (left, temporary)                  (right, permanent)      (right, permanent)
```

### 3.2 Progress Indicator States

#### State 1: Waveform Generation Starting
```
Status Bar:
├─ Left side: "12 files | 5 reviewed | 2 best takes"
└─ Right side: "Generating waveforms: 1/20 (Song_01.wav) [█░░░░░░░░░░░]"
                                      ↑    ↑         ↑         ↑
                                   Current Total   Filename  Progress Bar
                                                              (5% filled)
```

#### State 2: Waveform Generation In Progress
```
Status Bar:
├─ Left side: "12 files | 5 reviewed | 2 best takes"
└─ Right side: "Generating waveforms: 10/20 (Song_10.wav) [█████░░░░░░]"
                                                                ↑
                                                         (50% filled)
```

#### State 3: Waveform Generation Complete
```
Status Bar:
├─ Left side: "12 files | 5 reviewed | 2 best takes"
└─ Right side: (progress indicators hidden)
```

#### State 4: Fingerprint Generation
```
Status Bar:
├─ Left side: "12 files | 5 reviewed | 2 best takes"
└─ Right side: "Generating fingerprints: 3/15 (MySong.mp3) [██░░░░░░░░░]"
                                         ↑    ↑          ↑        ↑
                                      Current Total   Filename  Progress Bar
                                                               (20% filled)
```

#### State 5: Long Filename Truncation
```
Status Bar:
├─ Left side: "12 files | 5 reviewed"
└─ Right side: "Generating waveforms: 8/20 (VeryLongFileNam...) [████░░░░]"
                                                    ↑
                                              Truncated with "..."
                                           (prevents layout overflow)
```

### 3.3 Progress Bar Visual Details

**Progress Bar Component:**
```
Empty:    [░░░░░░░░░░░░░░░░░░░░]  0%
25%:      [█████░░░░░░░░░░░░░░░] 25%
50%:      [██████████░░░░░░░░░░] 50%
75%:      [███████████████░░░░░] 75%
100%:     [████████████████████] 100%
```

**Visual Characteristics**:
- Width: ~200 pixels (fixed)
- Height: Standard Qt progress bar height (~20px)
- Color: Theme-appropriate (blue in light mode, lighter blue in dark mode)
- Style: Native Qt progress bar styling
- Text: Shows percentage inside bar (optional, depends on Qt style)

---

## 4. User Interaction Flows

### 4.1 Saving a Custom Layout

**Step-by-Step Visual Flow:**

1. **Initial State**
   ```
   User sees default 1360x900 window with 40:60 splitter
   ```

2. **User Customizes**
   ```
   User resizes window → 1600x1000
   User drags splitter → 30:70 ratio
   ```

3. **User Saves**
   ```
   User presses Ctrl+Shift+L
   (or clicks View → Save Window Layout)
   ```

4. **Confirmation**
   ```
   Status bar shows: "Window layout saved" (3 seconds)
   ┌────────────────────────────────────┐
   │ Window layout saved                │
   └────────────────────────────────────┘
   ```

5. **Next Launch**
   ```
   Application opens with saved 1600x1000 size and 30:70 split
   ```

### 4.2 Watching Background Progress

**Visual Timeline:**

1. **User Opens Large Folder (20 files, no waveforms)**
   ```
   Immediately after opening:
   Status bar: "Auto-generation will start shortly..."
   ```

2. **Progress Appears (after 1-2 seconds)**
   ```
   Status bar right side:
   "Generating waveforms: 1/20 (First_Song.wav) [█░░░░░░░░░░]"
   ```

3. **Progress Updates (every ~1-2 seconds per file)**
   ```
   "Generating waveforms: 2/20 (Second_Song.wav) [██░░░░░░░░]"
   "Generating waveforms: 3/20 (Third_Song.wav) [███░░░░░░░]"
   ...
   "Generating waveforms: 19/20 (Last_Song.wav) [█████████░]"
   ```

4. **Progress Completes**
   ```
   "Generating waveforms: 20/20 (Last_Song.wav) [██████████]"
   (displays briefly)
   ```

5. **Progress Hides**
   ```
   Progress bar and label disappear
   Status bar returns to showing file statistics only
   ```

---

## 5. Theme Integration

### 5.1 Light Theme

**Window Appearance:**
- Background: White/light gray
- Text: Dark gray/black
- Progress bar: Blue fill
- Status bar: Light gray background

**Progress Indicator Colors:**
```
Progress bar fill: #0078D4 (blue)
Progress bar background: #E0E0E0 (light gray)
Progress label text: #333333 (dark gray)
```

### 5.2 Dark Theme

**Window Appearance:**
- Background: Dark gray/charcoal
- Text: White/light gray
- Progress bar: Light blue fill
- Status bar: Very dark gray background

**Progress Indicator Colors:**
```
Progress bar fill: #4A9EFF (light blue)
Progress bar background: #3A3A3A (dark gray)
Progress label text: #E0E0E0 (light gray)
```

---

## 6. Keyboard Shortcuts Reference

### New Shortcuts

| Shortcut | Action | Description |
|----------|--------|-------------|
| **Ctrl+Shift+L** | Save Window Layout | Saves current window geometry and splitter position |
| **Ctrl+Shift+R** | Restore Window Layout | Restores previously saved layout |

### Existing Shortcuts (for reference)
| Shortcut | Action |
|----------|--------|
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |
| Alt+Up | Navigate up to parent folder |
| Ctrl+Shift+S | Practice Statistics |

---

## 7. Edge Cases and Special Behaviors

### 7.1 No Saved Layout
```
First launch (or after reset):
- Window opens at default 1360x900
- Splitter at default 40:60
- No auto-restore happens
```

### 7.2 Saved Layout on Different Monitor
```
Layout saved on 1920x1080 monitor
Opened on 1366x768 laptop:
- Window may be partially off-screen
- User can use View → Reset to Default Layout
- Or manually resize and save new layout
```

### 7.3 Progress During Window Operations
```
User resizes window while progress is active:
- Progress bar and label remain visible
- Progress bar stays on right side of status bar
- Progress continues to update normally
- No visual glitches or layout issues
```

### 7.4 Multiple Sequential Operations
```
Waveforms complete → Fingerprints start:

[Waveforms: 20/20] → [Fingerprints: 1/15]
      ↓                      ↓
   Completes             Begins
      ↓                      ↓
  Hides progress      Shows new progress
```

---

## 8. Accessibility Notes

### Visual Indicators
- Progress bar has sufficient color contrast (WCAG AA compliant)
- Progress label text is readable at default size
- Status bar messages are clear and concise

### Keyboard Accessibility
- All layout operations accessible via keyboard shortcuts
- Menu items have proper keyboard navigation
- No mouse-only operations

### Screen Reader Support
- Progress bar has accessible text (percentage)
- Menu items have descriptive text
- Status messages are announced

---

## 9. Troubleshooting Visual Guide

### Issue: "Layout Doesn't Restore After Restart"

**Check These Visual Indicators:**
1. Did status bar show "Window layout saved" when you saved?
   - ✅ If yes: Layout should restore
   - ❌ If no: Layout was not saved

2. Try manually restoring:
   - Press **Ctrl+Shift+R**
   - Look for window to resize

3. If still not working:
   - View → Reset to Default Layout
   - Manually resize to desired size
   - Press **Ctrl+Shift+L** again

### Issue: "Progress Bar Doesn't Appear"

**Check These Conditions:**
1. Are you opening a folder with audio files that need waveforms?
   - Files without waveforms will trigger generation
   - Files with existing waveforms won't show progress

2. Is auto-generation enabled?
   - Check File → Auto-Generation Settings
   - Enable "Auto-generate waveforms"

3. Progress only shows for:
   - ✅ Waveform generation
   - ✅ Fingerprint generation (auto or manual)
   - ❌ File playback
   - ❌ Annotation editing

---

## 10. Visual Comparison Summary

### Before This Implementation

**Window Management:**
```
❌ Had to manually resize every time
❌ Splitter position reset on restart
❌ No way to save preferred layout
❌ Inconsistent experience across sessions
```

**Background Operations:**
```
❌ No visual progress feedback
❌ Unclear if operations were running
❌ No indication of completion time
❌ Users uncertain if app was frozen
```

### After This Implementation

**Window Management:**
```
✅ Window size persists automatically
✅ Splitter position persists
✅ One-click save and restore
✅ Consistent, personalized experience
✅ Easy reset to default if needed
```

**Background Operations:**
```
✅ Clear visual progress bar
✅ Percentage completion shown
✅ Current file being processed
✅ Time estimation (X/Y files)
✅ Professional, polished feedback
```

---

## 11. Future Visual Enhancements

Based on feedback and usage, future versions could add:

1. **Multiple Named Layouts**
   ```
   View → Layouts →
   ├─ Review Mode ✓
   ├─ Edit Mode
   ├─ Performance Mode
   └─ Save Current As...
   ```

2. **Enhanced Progress**
   ```
   Clickable progress bar to cancel
   Estimated time remaining
   Operation history in tooltip
   ```

3. **Layout Presets**
   ```
   View → Layouts →
   ├─ Wide File Tree (20:80)
   ├─ Balanced (50:50)
   ├─ Wide Content (70:30)
   └─ Custom (saved)
   ```

---

**Note**: All visual descriptions in this guide are ASCII representations. Actual UI uses native Qt widgets with platform-appropriate styling. Visual appearance may vary slightly by operating system (Windows, macOS, Linux) and theme.

---

**Last Updated**: January 2025  
**Implementation Version**: 1.0  
**Documentation Status**: Complete
