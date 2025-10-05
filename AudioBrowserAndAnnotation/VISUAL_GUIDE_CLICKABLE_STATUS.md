# Visual Guide: Clickable Status Bar Items

**Feature**: Interactive status bar statistics  
**Access**: Automatically visible in status bar at bottom of main window

---

## Overview

The status bar now contains clickable items that provide quick access to specific file categories. Click on any blue underlined statistic to filter and navigate to relevant files.

---

## 1. Status Bar Layout

```
┌────────────────────────────────────────────────────────────────────┐
│ AudioBrowser - Practice Session                              [_][□][×]│
├────────────────────────────────────────────────────────────────────┤
│  [File] [Edit] [View] [Tools] [Help]                              │
├────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐                         │
│  │   File Tree     │  │   Library Tab   │                         │
│  │                 │  │                 │                         │
│  │  ♪ song1.wav    │  │  [Table View]   │                         │
│  │  ♪ song2.wav    │  │                 │                         │
│  │  ♪ song3.wav    │  │                 │                         │
│  └─────────────────┘  └─────────────────┘                         │
├────────────────────────────────────────────────────────────────────┤
│ 12 files | 5 reviewed | 3 without names | 2 best takes | 1 partial take │
│          └─────┬─────┘  └──────┬──────┘  └─────┬─────┘  └────┬────┘    │
│           Clickable     Clickable        Clickable      Clickable       │
└────────────────────────────────────────────────────────────────────┘
```

**Status Bar Components**:
- **"12 files"**: Total file count (NOT clickable - informational only)
- **"5 reviewed"**: Clickable - shows list of reviewed files
- **"3 without names"**: Clickable - jumps to Library tab and shows unnamed files
- **"2 best takes"**: Clickable - jumps to Library tab and shows best take files
- **"1 partial take"**: Clickable - jumps to Library tab and shows partial take files

---

## 2. Visual States

### 2.1 Normal State (Not Hovering)
```
12 files | 5 reviewed | 3 without names | 2 best takes
           ──────────   ────────────────   ──────────
           Blue, underlined = clickable
```

### 2.2 Hover State
```
12 files | 𝟱 𝗿𝗲𝘃𝗶𝗲𝘄𝗲𝗱 | 3 without names | 2 best takes
           ──────────                            👆 Hand cursor
           Bold text when hovering
```

### 2.3 Empty Counts (Hidden)
```
When count is 0, item doesn't appear:

12 files | 3 without names | 2 best takes
(no "reviewed" item because count is 0)
```

---

## 3. Click Action: "X reviewed"

**What it does**: Shows list of reviewed files

**Visual Flow**:
```
1. Click on "5 reviewed"
     │
     ▼
2. Dialog appears:
   ┌─────────────────────────────────────┐
   │ Filter: Reviewed Files         [×]  │
   ├─────────────────────────────────────┤
   │                                     │
   │ Showing 5 reviewed files:           │
   │                                     │
   │ song1.wav                           │
   │ song2.wav                           │
   │ song3.wav                           │
   │ song4.wav                           │
   │ song5.wav                           │
   │                                     │
   │              [OK]                   │
   └─────────────────────────────────────┘
```

**Use Case**: Quickly see which files you've already reviewed in this session.

---

## 4. Click Action: "X without names"

**What it does**: Switches to Library tab and shows list of files needing names

**Visual Flow**:
```
1. Click on "3 without names"
     │
     ▼
2. Automatically switches to Library tab
     │
     ▼
3. Dialog appears:
   ┌──────────────────────────────────────────┐
   │ Filter: Files Without Names        [×]   │
   ├──────────────────────────────────────────┤
   │                                          │
   │ Found 3 files without provided names:    │
   │                                          │
   │ 01_unknown.wav                           │
   │ 02_unknown.wav                           │
   │ recording_003.wav                        │
   │                                          │
   │ Switched to Library tab.                 │
   │ You can provide names using the table.   │
   │                                          │
   │                 [OK]                     │
   └──────────────────────────────────────────┘
     │
     ▼
4. Now on Library tab - provide names in the table
```

**Use Case**: Quickly find and name unnamed files.

---

## 5. Click Action: "X best takes"

**What it does**: Switches to Library tab and shows best take files

**Visual Flow**:
```
1. Click on "2 best takes"
     │
     ▼
2. Automatically switches to Library tab
     │
     ▼
3. Dialog appears:
   ┌──────────────────────────────────────────┐
   │ Filter: Best Takes                 [×]   │
   ├──────────────────────────────────────────┤
   │                                          │
   │ Found 2 best take files:                 │
   │                                          │
   │ Highway_Blues_Take3.wav                  │
   │ Midnight_Rider_Take1.wav                 │
   │                                          │
   │ Switched to Library tab.                 │
   │ Best takes are highlighted.              │
   │                                          │
   │                 [OK]                     │
   └──────────────────────────────────────────┘
     │
     ▼
4. Library tab shows files - best takes have light green background
```

**Use Case**: Quickly find best takes for export or performance preparation.

---

## 6. Click Action: "X partial takes"

**What it does**: Switches to Library tab and shows partial take files

**Visual Flow**:
```
1. Click on "1 partial take"
     │
     ▼
2. Automatically switches to Library tab
     │
     ▼
3. Dialog appears:
   ┌──────────────────────────────────────────┐
   │ Filter: Partial Takes              [×]   │
   ├──────────────────────────────────────────┤
   │                                          │
   │ Found 1 partial take file:               │
   │                                          │
   │ Practice_Run_Incomplete.wav              │
   │                                          │
   │ Switched to Library tab.                 │
   │ Partial takes are highlighted.           │
   │                                          │
   │                 [OK]                     │
   └──────────────────────────────────────────┘
     │
     ▼
4. Library tab shows files - partial takes have light orange background
```

**Use Case**: Quickly find incomplete takes that need re-recording.

---

## 7. Dynamic Updates

Status bar updates automatically when you make changes:

### Scenario 1: Marking a file as best take
```
Before: 12 files | 3 without names | 1 best take
            │
            │ [Right-click file → Mark as Best Take]
            ▼
After:  12 files | 3 without names | 2 best takes
                                     └─ Count updated!
```

### Scenario 2: Providing a name
```
Before: 12 files | 3 without names | 2 best takes
            │
            │ [Type name in Library table]
            ▼
After:  12 files | 2 without names | 2 best takes
                   └─ Count decreased!
```

### Scenario 3: All files have names
```
Before: 12 files | 1 without names | 2 best takes
            │
            │ [Provide last name]
            ▼
After:  12 files | 2 best takes
                   └─ "without names" removed when count reaches 0
```

---

## 8. Color Coding

| Element | Color | Meaning |
|---------|-------|---------|
| Total file count | Default text color | Informational only (not clickable) |
| Clickable items | Blue (#0066cc) | Interactive - can be clicked |
| Underline | Blue | Indicates clickability (like web links) |
| Bold on hover | Same color, bold | Visual feedback for hover |
| Separators (\|) | Default text color | Visual separators only |

---

## 9. Keyboard & Mouse Shortcuts

### Mouse Interaction
- **Left Click**: Activate the filter/navigation
- **Hover**: Show bold text and hand cursor
- **No Right Click**: No context menu for status items

### Keyboard (Future Enhancement)
- **Tab**: Navigate between clickable items (not yet implemented)
- **Enter/Space**: Activate focused item (not yet implemented)

---

## 10. Workflow Examples

### Example 1: "I want to name all my files"
```
1. Look at status bar: "12 files | 7 without names | ..."
2. Click "7 without names" 
3. See dialog listing the 7 files
4. Click OK
5. Now on Library tab - provide names in the table
6. Status bar updates as you type: "6 without names", "5 without names", etc.
```

### Example 2: "I want to export my best takes"
```
1. Look at status bar: "12 files | ... | 3 best takes"
2. Click "3 best takes"
3. See dialog listing the 3 best take files
4. Click OK
5. Now on Library tab - best takes are highlighted
6. Right-click highlighted files → Export with boost
```

### Example 3: "I want to finish incomplete recordings"
```
1. Look at status bar: "12 files | ... | 2 partial takes"
2. Click "2 partial takes"
3. See dialog listing the 2 partial take files
4. Click OK
5. Now on Library tab - partial takes are highlighted
6. Play files to hear what needs completion
7. Re-record or complete the takes
8. Unmark as partial when done
```

---

## 11. Tips & Best Practices

### ✅ Do's
- Click status items to quickly navigate to specific file categories
- Use status bar to monitor your workflow progress
- Check "without names" count to ensure all files are properly named before export
- Use "reviewed" count to track your review progress

### ❌ Don'ts
- Don't try to right-click status items (no context menu)
- Don't expect status items to filter the file tree (shows dialog instead)
- Don't expect keyboard navigation yet (future enhancement)

---

## 12. Troubleshooting

### Issue: Clickable items don't appear
**Cause**: Count is 0 for that category  
**Solution**: Items only appear when count > 0. Mark files appropriately to see items.

### Issue: Can't click on total file count
**Cause**: Total count is informational only  
**Solution**: This is by design - only specific categories are clickable.

### Issue: Dialog shows "..." after 10 files
**Cause**: Long lists are truncated for readability  
**Solution**: This is normal - first 10 files shown, remaining count indicated.

### Issue: Want actual tree filtering instead of dialogs
**Status**: Future enhancement  
**Workaround**: Use the dialog information to manually search in tree.

---

## 13. Quick Reference

| Status Item | Action | Result |
|-------------|--------|--------|
| **X files** | Not clickable | Total file count (info only) |
| **X reviewed** | Click → Dialog | Shows list of reviewed files |
| **X without names** | Click → Library + Dialog | Jump to Library, show unnamed files |
| **X best takes** | Click → Library + Dialog | Jump to Library, show best takes |
| **X partial takes** | Click → Library + Dialog | Jump to Library, show partial takes |

---

## Summary

Clickable status bar items provide a fast, visual way to:
- **Monitor** your workflow progress at a glance
- **Navigate** to specific file categories with one click
- **Discover** which files need attention (names, review, completion)
- **Improve** efficiency by reducing manual searching

The blue, underlined styling makes it clear which items are interactive, and the hover effect provides immediate feedback. Status bar updates automatically as you work, keeping information current.

---

**For more information, see:**
- [IMPLEMENTATION_SUMMARY_CLICKABLE_STATUS.md](IMPLEMENTATION_SUMMARY_CLICKABLE_STATUS.md) - Technical details
- [TEST_PLAN_CLICKABLE_STATUS.md](TEST_PLAN_CLICKABLE_STATUS.md) - Complete test plan
- [INTERFACE_IMPROVEMENT_IDEAS.md](INTERFACE_IMPROVEMENT_IDEAS.md) - Section 1.5.3
