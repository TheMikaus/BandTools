# Library Layout Changes - Left Side Panel

## Summary
Moved the Library panel from the bottom of the screen to the left side panel, making it more compact and always accessible alongside other tabs.

## Visual Changes

### BEFORE: Library at Bottom
```
┌─────────────────────────────────────────────────────────────┐
│ Menu Bar & Toolbar                                          │
├─────────────────────────────────────────────────────────────┤
│ Now Playing Panel                                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ┌───────────────────────────────────────────────────────┐ │
│ │ [Annotations] [Clips] [Sections] [Folder Notes] [...] │ │
│ ├───────────────────────────────────────────────────────┤ │
│ │                                                       │ │
│ │         Work Area (Annotations, Clips, etc.)         │ │
│ │                                                       │ │
│ └───────────────────────────────────────────────────────┘ │
│                                                             │
│ ╔═══════════════════════════════════════════════════════╗ │
│ ║ LIBRARY (Bottom - Full Width)                         ║ │
│ ║ Toolbar: Directory, Browse, Refresh, Actions, Filters ║ │
│ ║ ┌────────────────┬──────────────────────────────────┐ ║ │
│ ║ │ FOLDERS (LEFT) │ FILES (RIGHT)                    │ ║ │
│ ║ │ • Horizontal    │ • Take | File | Library | Dur   │ ║ │
│ ║ │   split         │ • Full table with columns       │ ║ │
│ ║ └────────────────┴──────────────────────────────────┘ ║ │
│ ╚═══════════════════════════════════════════════════════╝ │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Status Bar                                                  │
└─────────────────────────────────────────────────────────────┘
```

### AFTER: Library on Left Side
```
┌─────────────────────────────────────────────────────────────┐
│ Menu Bar & Toolbar                                          │
├─────────────────────────────────────────────────────────────┤
│ Now Playing Panel                                           │
├───────┬─────────────────────────────────────────────────────┤
│       │                                                     │
│ ╔═══╗ │ ┌───────────────────────────────────────────────┐ │
│ ║ L ║ │ │ [Annotations] [Clips] [Sections] [...]        │ │
│ ║ I ║ │ ├───────────────────────────────────────────────┤ │
│ ║ B ║ │ │                                               │ │
│ ║ R ║ │ │    Work Area (Annotations, Clips, etc.)      │ │
│ ║ A ║ │ │                                               │ │
│ ║ R ║ │ │    Takes up most of the screen width         │ │
│ ║ Y ║ │ │                                               │ │
│ ║   ║ │ └───────────────────────────────────────────────┘ │
│ ║   ║ │                                                     │
│ ╠═══╣ │                                                     │
│ ║ 📁║ │ Compact side panel (350px, min 250px):             │
│ ║ 🔄║ │ • Browse & Refresh buttons                         │
│ ║ ⋮ ║ │ • More menu (⋮) with all actions/filters          │
│ ╠═══╣ │                                                     │
│ ║FOL║ │                                                     │
│ ║DER║ │                                                     │
│ ║📁 ║ │                                                     │
│ ║📂 ║ │                                                     │
│ ╠═══╣ │                                                     │
│ ║FIL║ │                                                     │
│ ║ES ║ │                                                     │
│ ║★◐║ │                                                     │
│ ║   ║ │                                                     │
│ ╚═══╝ │                                                     │
│       │                                                     │
├───────┴─────────────────────────────────────────────────────┤
│ Status Bar                                                  │
└─────────────────────────────────────────────────────────────┘
```

## Key Changes

### 1. Layout Structure (main.qml)
- **Before**: `ColumnLayout` with Library at bottom (full width)
- **After**: `RowLayout` with Library on left (350px width, resizable to min 250px)

### 2. Library Panel Condensed (LibraryTab.qml)

#### Compact Toolbar
- **Before**: Two-row toolbar with:
  - Row 1: "Directory:" label, text field, "Browse...", "Refresh" buttons
  - Row 2: "Actions:", "Filters:", "Tools:" with 8+ buttons
- **After**: Single-row toolbar with:
  - 📁 Browse button (icon only with tooltip)
  - 🔄 Refresh button (icon only with tooltip)
  - ⋮ More menu (contains all actions, filters, and tools)

#### Folder/File Split
- **Before**: Horizontal split (Folders left, Files right)
- **After**: Vertical stack (Folders top, Files bottom)
  - Better use of narrow vertical space
  - Folders panel: 150px height (min 100px)
  - Files panel: Fills remaining space

#### File List Simplification
- **Before**: Full table with headers:
  - Take | File Name | Library | Duration
  - Column headers with sorting indicators
  - Separate filter field
- **After**: Compact list:
  - ★◐ filename duration
  - No column headers (saves space)
  - Smaller font sizes (fontSizeSmall)
  - Library name removed (not needed in compact view)

#### Size Reductions
- Header heights: 32px → 24px
- Row heights: 32px/28px → 28px/24px
- Font sizes: fontSizeNormal → fontSizeSmall
- Margins: spacingNormal → spacingSmall
- Removed: Status bar at bottom of Library panel

## Benefits

1. **More Screen Space for Work**: 
   - Work area (Annotations, Clips, etc.) now uses ~70% of screen width
   - Library uses ~30% of screen width

2. **Always Accessible**:
   - Library visible at all times
   - No need to scroll down to see files
   - Quick file selection while working

3. **Cleaner Interface**:
   - Consolidated toolbar using menu
   - Less visual clutter
   - More compact and efficient

4. **Better Workflow**:
   - Natural left-to-right flow: Select file → Work on it
   - Side-by-side view of library and work area
   - Easier to switch between files during annotation/editing

## Files Modified

1. **qml/main.qml**:
   - Changed main content area from ColumnLayout to RowLayout
   - Moved Library from bottom position to left side
   - Set Library width to 350px (min 250px)
   - Tabs now fill remaining width on right side

2. **qml/tabs/LibraryTab.qml**:
   - Condensed toolbar from 2 rows to 1 compact row
   - Moved actions/filters/tools to "More" menu (⋮)
   - Changed folder/file split from horizontal to vertical
   - Simplified file list to compact format
   - Reduced all spacing and font sizes
   - Removed Library panel status bar

## Testing Notes

To verify the changes:
1. Library panel should appear on the left side (350px width)
2. Tab bar and content should be on the right side
3. Library toolbar should be compact with Browse, Refresh, and More (⋮) buttons
4. Folders should be stacked on top, Files below
5. File list should show: indicators, filename, and duration only
6. All previous functionality should work (file selection, context menu, etc.)

## Backward Compatibility

All functionality is preserved:
- File selection and playback
- Context menus
- Batch operations (moved to More menu)
- Filters (moved to More menu)
- Tools/dialogs (moved to More menu)
- Folder tree navigation
- Take indicators (Best/Partial)
