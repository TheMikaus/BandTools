# Visual Guide: Setlist Builder

**Feature**: Performance setlist management  
**Access**: Tools → "Setlist Builder" or `Ctrl+Shift+T`

---

## Overview

This visual guide shows the layout and functionality of the Setlist Builder dialog using ASCII diagrams.

---

## 1. Main Dialog Structure

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ AudioBrowser - Setlist Builder                                        [_][□][X] │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                   │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │ [Manage Setlists] [Practice Mode] [Export & Validation]                 │   │
│  ├──────────────────────────────────────────────────────────────────────────┤   │
│  │                                                                          │   │
│  │  (Content changes based on selected tab)                                │   │
│  │                                                                          │   │
│  │                                                                          │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                                                                   │
│                                                    [Close]                        │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Tab 1: Manage Setlists

### 2.1 Layout Overview

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│ [Manage Setlists] [Practice Mode] [Export & Validation]                          │
├───────────────────────────────┬───────────────────────────────────────────────────┤
│ LEFT PANEL (Setlist List)    │ RIGHT PANEL (Setlist Details)                     │
│                               │                                                   │
│ Your Setlists                 │ Setlist Details                                   │
│ ┌───────────────────────────┐ │ ┌───────────────────────────────────────────────┐ │
│ │ Summer Tour 2024 (12)     │ │ │  #  Song Name      ✓  Duration Folder Actions │ │
│ │ Fall Concert (8)          │ │ │ ──────────────────────────────────────────────│ │
│ │ Acoustic Set (5)          │◄┼►│  1  Sweet Home...  ✓  4:45    prac... [    ] │ │
│ │ Local Brewery (6)         │ │ │  2  Free Bird      ✓  9:30    prac... [    ] │ │
│ │                           │ │ │  3  Simple Man        5:20    prac... [    ] │ │
│ │                           │ │ │  4  Tuesday's Gone ✓  7:15    prac... [    ] │ │
│ │                           │ │ │                                               │ │
│ └───────────────────────────┘ │ └───────────────────────────────────────────────┘ │
│                               │                                                   │
│ [New Setlist] [Rename]        │ Total Duration: 26:50                             │
│            [Delete]           │                                                   │
│                               │ [Add Song...] [Remove] [↑ Up] [↓ Down]            │
│                               │                                                   │
│                               │ Performance Notes:                                │
│                               │ ┌───────────────────────────────────────────────┐ │
│                               │ │ Free Bird - Extended solo                     │ │
│                               │ │ Simple Man - Acoustic, drop D tuning          │ │
│                               │ └───────────────────────────────────────────────┘ │
└───────────────────────────────┴───────────────────────────────────────────────────┘
```

### 2.2 Setlist List (Left Panel)

Shows all your setlists:
```
┌─────────────────────────────┐
│ Summer Tour 2024 (12 songs) │  ← Selected (highlighted)
│ Fall Concert (8 songs)      │
│ Acoustic Set (5 songs)      │
│ Local Brewery Show (6 songs)│
│                             │
└─────────────────────────────┘

[New Setlist] [Rename] [Delete]
       ↓         ↓        ↓
    Create    Rename   Delete with
    new      existing  confirmation
```

### 2.3 Songs Table (Right Panel)

```
┌──────────────────────────────────────────────────────────────────────┐
│  #  │ Song Name              │ ✓ │ Duration │ Folder            │ Actions │
├─────┼────────────────────────┼───┼──────────┼───────────────────┼─────────┤
│  1  │ Sweet Home Alabama     │ ✓ │  4:45    │ practice_2024_01  │         │
│  2  │ Free Bird              │ ✓ │  9:30    │ practice_2024_02  │         │
│  3  │ Simple Man             │   │  5:20    │ practice_2024_03  │         │  ← No Best Take
│  4  │ Tuesday's Gone         │ ✓ │  7:15    │ practice_2024_01  │         │
│  5  │ Missing File           │   │  0:00    │ practice_2024_05  │         │  ← Red text (missing)
└─────┴────────────────────────┴───┴──────────┴───────────────────┴─────────┘

Total Duration: 26:50

[Add Song from Current Folder] [Remove Song] [↑ Move Up] [↓ Move Down]
            ↓                        ↓              ↓            ↓
      Add currently           Remove selected    Reorder    Reorder
      selected file           song from list      songs      songs
```

### 2.4 Performance Notes

```
Performance Notes:
┌────────────────────────────────────────────────────────────┐
│ Free Bird - Extended guitar solo in middle section        │
│ Simple Man - Acoustic guitar, drop to D tuning            │
│ Tuesday's Gone - Slide guitar for intro                   │
│ Equipment: Acoustic guitar, slide, capo                   │
└────────────────────────────────────────────────────────────┘
         ↑
    Auto-saves as you type
```

---

## 3. Tab 2: Practice Mode

### 3.1 Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│ [Manage Setlists] [Practice Mode] [Export & Validation]                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Practice Mode                                                          │
│                                                                         │
│  Select a setlist to practice. The application will play songs         │
│  in order and highlight them in the file tree.                         │
│                                                                         │
│  Select Setlist:                                                        │
│  ┌───────────────────────────────────────────────────────────────┐     │
│  │ Summer Tour 2024 (12 songs)                                   │◄─── Selected
│  │ Fall Concert (8 songs)                                        │     │
│  │ Acoustic Set (5 songs)                                        │     │
│  │ Local Brewery Show (6 songs)                                  │     │
│  │                                                               │     │
│  └───────────────────────────────────────────────────────────────┘     │
│                                                                         │
│  [Start Practice Mode]  [Stop Practice Mode]                           │
│         ↓                      ↓                                        │
│     Activate setlist      Deactivate                                   │
│     (button grays out     (enabled when                                │
│     when active)          mode active)                                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Practice Mode States

**Before Starting**:
```
[Start Practice Mode]    [Stop Practice Mode]
      (enabled)              (disabled/gray)
```

**After Starting**:
```
[Start Practice Mode]    [Stop Practice Mode]
    (disabled/gray)          (enabled)

Status bar: "Practice mode started: Summer Tour 2024"
```

---

## 4. Tab 3: Export & Validation

### 4.1 Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│ [Manage Setlists] [Practice Mode] [Export & Validation]                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Export & Validation                                                    │
│                                                                         │
│  Select Setlist:                                                        │
│  ┌───────────────────────────────────────────────────────────────┐     │
│  │ Summer Tour 2024 (12 songs)                                   │◄─── Selected
│  │ Fall Concert (8 songs)                                        │     │
│  │ Acoustic Set (5 songs)                                        │     │
│  └───────────────────────────────────────────────────────────────┘     │
│                                                                         │
│  Validation Results:                                                    │
│  ┌───────────────────────────────────────────────────────────────┐     │
│  │ === Setlist Validation Results ===                           │     │
│  │                                                               │     │
│  │ Total songs: 12                                               │     │
│  │ Missing files: 1                                              │     │
│  │ Songs without Best Take: 2                                    │     │
│  │                                                               │     │
│  │ ❌ Missing Files:                                             │     │
│  │   - Old Recording (practice_2023_12/song.mp3)                │     │
│  │                                                               │     │
│  │ ⚠️  Songs without Best Take:                                  │     │
│  │   - Simple Man                                                │     │
│  │   - Call Me the Breeze                                        │     │
│  └───────────────────────────────────────────────────────────────┘     │
│                                                                         │
│  [Validate Setlist]  [Export as Text]  [Export as PDF (Coming Soon)]  │
│         ↓                    ↓                    ↓                     │
│    Run validation      Save to .txt          Future feature            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Validation Status Examples

**Perfect Setlist**:
```
┌─────────────────────────────────────────────────────────────────┐
│ === Setlist Validation Results ===                             │
│                                                                 │
│ Total songs: 12                                                 │
│ Missing files: 0                                                │
│ Songs without Best Take: 0                                      │
│                                                                 │
│ ✓ All files exist                                               │
│                                                                 │
│ ✓ All songs have Best Takes                                     │
│                                                                 │
│ ✅ Setlist is ready for performance!                            │
└─────────────────────────────────────────────────────────────────┘
```

**Setlist with Issues**:
```
┌─────────────────────────────────────────────────────────────────┐
│ === Setlist Validation Results ===                             │
│                                                                 │
│ Total songs: 12                                                 │
│ Missing files: 2                                                │
│ Songs without Best Take: 3                                      │
│                                                                 │
│ ❌ Missing Files:                                               │
│   - Old Recording (practice_2023/01_old.mp3)                   │
│   - Demo Version (practice_temp/demo.mp3)                      │
│                                                                 │
│ ⚠️  Songs without Best Take:                                    │
│   - Simple Man                                                  │
│   - Call Me                                                     │
│   - Tuesday's Gone                                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Workflow Diagrams

### 5.1 Creating a Setlist

```
1. Open Dialog                 2. Create Setlist              3. Add Songs
   ┌──────────┐                  ┌──────────┐                 ┌──────────┐
   │ Ctrl+    │                  │ Click    │                 │ Select   │
   │ Shift+T  │ ──────────────► │ "New     │ ──────────────► │ file in  │
   │          │                  │ Setlist" │                 │ main     │
   └──────────┘                  └──────────┘                 │ window   │
                                                              └────┬─────┘
                                                                   │
                                                                   ▼
4. Reorder                     5. Add Notes                   6. Click "Add"
   ┌──────────┐                  ┌──────────┐                 ┌──────────┐
   │ Move     │                  │ Type     │                 │ Song     │
   │ Up/Down  │ ◄──────────────  │ notes    │ ◄────────────── │ added!   │
   │ buttons  │                  │ in box   │                 │          │
   └──────────┘                  └──────────┘                 └──────────┘
```

### 5.2 Validation and Export Workflow

```
1. Validate                    2. Fix Issues                  3. Export
   ┌──────────┐                  ┌──────────┐                 ┌──────────┐
   │ Click    │                  │ Remove   │                 │ Click    │
   │ Validate │ ──────────────► │ missing  │ ──────────────► │ Export   │
   │          │                  │ files or │                 │ as Text  │
   └──────────┘                  │ mark BT  │                 └──────────┘
                                 └──────────┘                       │
                                                                    ▼
      ┌───────────────────────────────────────────────┐      ┌──────────┐
      │ ✅ Setlist is ready for performance!          │      │ Save     │
      └───────────────────────────────────────────────┘      │ .txt     │
                                                              │ file     │
                                                              └──────────┘
```

### 5.3 Practice Mode Workflow

```
1. Select Setlist              2. Start Practice              3. Practice
   ┌──────────┐                  ┌──────────┐                 ┌──────────┐
   │ Choose   │                  │ Click    │                 │ Focus on │
   │ setlist  │ ──────────────► │ "Start   │ ──────────────► │ setlist  │
   │ from     │                  │ Practice │                 │ songs    │
   │ list     │                  │ Mode"    │                 │          │
   └──────────┘                  └──────────┘                 └──────────┘
                                                                    │
                                                                    ▼
4. Stop Practice                                              ┌──────────┐
   ┌──────────┐                                              │ Close    │
   │ Click    │ ◄───────────────────────────────────────────│ dialog   │
   │ "Stop"   │                                              │ (mode    │
   │ when     │                                              │ persists)│
   │ done     │                                              └──────────┘
   └──────────┘
```

---

## 6. Visual Indicators and Icons

### 6.1 Status Indicators in Songs Table

```
Song Name Column:
┌────────────────────────┐
│ Sweet Home Alabama     │  ← Black text: File exists, all good
│ Free Bird              │  ← Black text: File exists, all good
│ Missing Song           │  ← RED TEXT: File not found! ⚠️
│ Another Song           │  ← Black text: File exists, all good
└────────────────────────┘

Best Take Column:
┌───┐
│ ✓ │  ← Checkmark: Marked as Best Take
│   │  ← Empty: Not a Best Take
│ ✓ │  ← Checkmark: Marked as Best Take
│   │  ← Empty: Not a Best Take
└───┘
```

### 6.2 Button States

**Enabled Button**:
```
┌─────────────────────┐
│ Add Song from...    │  ← Normal appearance, clickable
└─────────────────────┘
```

**Disabled Button** (grayed out):
```
┌─────────────────────┐
│ Stop Practice Mode  │  ← Gray appearance, not clickable
└─────────────────────┘
```

---

## 7. Exported Text File Format

### 7.1 Example Export

```
────────────────────────────────────────────────────────────────
SETLIST: Summer Tour 2024
Created: 2025-01-15T12:00:00
Exported: 2025-01-20 15:30:00
============================================================

1. Sweet Home Alabama [BEST TAKE]
   Duration: 4:45
   Source: practice_2024_01_01/01_Sweet_Home_Alabama.mp3

2. Free Bird [BEST TAKE]
   Duration: 9:30
   Source: practice_2024_01_15/05_Free_Bird.mp3

3. Simple Man
   Duration: 5:20
   Source: practice_2024_02_01/03_Simple_Man.mp3

4. Tuesday's Gone [BEST TAKE]
   Duration: 7:15
   Source: practice_2024_01_01/04_Tuesdays_Gone.mp3

5. Old Recording [MISSING]
   Duration: 0:00
   Source: practice_2023_12/old_song.mp3

============================================================
Total Songs: 5
Total Duration: 26:50

PERFORMANCE NOTES:
Free Bird - Extended guitar solo in middle section
Simple Man - Acoustic guitar, drop to D tuning
Tuesday's Gone - Use slide guitar for intro
────────────────────────────────────────────────────────────────
```

---

## 8. Common UI Patterns

### 8.1 Dialog Confirmation Pattern

Used for destructive operations (like Delete):

```
┌─────────────────────────────────────────────┐
│ Delete Setlist                              │
├─────────────────────────────────────────────┤
│                                             │
│ Are you sure you want to delete             │
│ 'Summer Tour 2024'?                         │
│                                             │
│              [Yes]  [No]                    │
└─────────────────────────────────────────────┘
         Click Yes ──┘      └── Click No (cancel)
```

### 8.2 Input Dialog Pattern

Used for creating/renaming setlists:

```
┌─────────────────────────────────────────────┐
│ New Setlist                                 │
├─────────────────────────────────────────────┤
│                                             │
│ Enter setlist name:                         │
│ ┌─────────────────────────────────────────┐ │
│ │ Summer Tour 2024                        │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│              [OK]  [Cancel]                 │
└─────────────────────────────────────────────┘
```

### 8.3 Status Bar Messages

Appear at bottom of main window:

```
┌────────────────────────────────────────────────────────────┐
│ Created setlist: Summer Tour 2024                    (3s) │
└────────────────────────────────────────────────────────────┘
        ↑                                             ↑
    Message text                              Auto-dismiss timer


┌────────────────────────────────────────────────────────────┐
│ Added Song.mp3 to setlist                            (3s) │
└────────────────────────────────────────────────────────────┘


┌────────────────────────────────────────────────────────────┐
│ Practice mode started: Summer Tour 2024               (5s) │
└────────────────────────────────────────────────────────────┘
```

---

## 9. Data Flow Diagram

```
┌──────────────────┐         ┌──────────────────┐        ┌──────────────────┐
│  Practice        │         │  Setlist         │        │  .setlists.json  │
│  Folders         │◄────────│  Builder         │◄──────►│  (JSON file)     │
│                  │  Read   │  Dialog          │ Save   │                  │
│ - provided names │  song   │                  │ Load   │ - Setlist data   │
│ - durations      │  metadata                  │        │ - Song refs      │
│ - best takes     │         │                  │        │ - Notes          │
│ - annotations    │         │                  │        │                  │
└──────────────────┘         └──────────────────┘        └──────────────────┘
         │                            │                            │
         │                            ▼                            │
         │                   ┌──────────────────┐                │
         │                   │  Validation      │                │
         └──────────────────►│  Engine          │◄───────────────┘
                            │                  │
                            │ - Check files    │
                            │ - Check BT       │
                            │ - Generate report│
                            └──────────────────┘
                                     │
                                     ▼
                            ┌──────────────────┐
                            │  Export          │
                            │  Generator       │
                            │                  │
                            │ - Text format    │
                            │ - PDF (future)   │
                            └──────────────────┘
```

---

## 10. Quick Reference: All Buttons and Actions

### Main Dialog Buttons

| Button | Location | Action |
|--------|----------|--------|
| **New Setlist** | Manage tab, left panel | Create new empty setlist |
| **Rename** | Manage tab, left panel | Rename selected setlist |
| **Delete** | Manage tab, left panel | Delete selected setlist (with confirmation) |
| **Add Song from Current Folder** | Manage tab, right panel | Add currently selected file to setlist |
| **Remove Song** | Manage tab, right panel | Remove selected song from setlist |
| **↑ Move Up** | Manage tab, right panel | Move selected song earlier in list |
| **↓ Move Down** | Manage tab, right panel | Move selected song later in list |
| **Start Practice Mode** | Practice Mode tab | Activate setlist for practice |
| **Stop Practice Mode** | Practice Mode tab | Deactivate practice mode |
| **Validate Setlist** | Export & Validation tab | Check setlist readiness |
| **Export as Text** | Export & Validation tab | Save setlist to .txt file |
| **Export as PDF** | Export & Validation tab | (Coming soon - disabled) |

---

## 11. Color Coding Summary

| Color | Meaning | Where Used |
|-------|---------|------------|
| **Black** | Normal, file exists | Song names in table |
| **Red** | Missing/error | Missing file names in table |
| **Gray** | Disabled | Inactive buttons |
| **Green** | Success checkmark | Best Take indicator (✓) |
| **Highlight** | Selected | Selected setlist in list |
| **Light Yellow** | Background for forms | Performance notes area |

---

## 12. Keyboard Navigation

```
┌─────────────────────────────────────────────┐
│ Global Shortcut:                            │
│ Ctrl+Shift+T ─────► Open Setlist Builder   │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ Within Dialog:                              │
│ Tab          ─────► Move between controls   │
│ Space/Enter  ─────► Activate button         │
│ Esc          ─────► Close dialog            │
│ Arrow Keys   ─────► Navigate lists          │
└─────────────────────────────────────────────┘
```

---

## Summary

The Setlist Builder provides a comprehensive, three-tab interface for managing performance setlists:

1. **Manage Setlists** - Create, organize, and maintain setlists
2. **Practice Mode** - Focus practice on performance material
3. **Export & Validation** - Verify readiness and share with band

All data is stored in `.setlists.json` and persists across sessions. Songs are referenced (not copied), keeping disk usage minimal while providing complete flexibility in organizing performance material.

---

*For detailed usage instructions, see [SETLIST_BUILDER_GUIDE.md](SETLIST_BUILDER_GUIDE.md)*  
*For technical details, see [IMPLEMENTATION_SUMMARY_SETLIST_BUILDER.md](../technical/IMPLEMENTATION_SUMMARY_SETLIST_BUILDER.md)*  
*For testing, see [TEST_PLAN_SETLIST_BUILDER.md](../test_plans/TEST_PLAN_SETLIST_BUILDER.md)*
