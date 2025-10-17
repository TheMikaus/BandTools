# Library Layout - Visual Mockup

## New Layout (Left Side Panel)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ File | Edit | View | Help                                    [Theme] [x]    │
├──────────────────────────────────────────────────────────────────────────────┤
│ AudioBrowser QML    [◄◄] [▶] [■] [►►]  ⚪━━━━━━━━●───  🔊  [Auto-switch ☑] │
├──────────────────────────────────────────────────────────────────────────────┤
│ ♪ Now Playing: song_take_3.wav              02:45 / 03:42  [Add Annotation] │
├────────────┬─────────────────────────────────────────────────────────────────┤
│            │                                                                  │
│  LIBRARY   │  ┌──────────────────────────────────────────────────────────┐  │
│  (350px)   │  │ [Annotations] [Clips] [Sections] [Folder Notes] [...]    │  │
│            │  ├──────────────────────────────────────────────────────────┤  │
│ [📁] [🔄] ⋮│  │                                                          │  │
│            │  │  ANNOTATIONS TAB CONTENT                                 │  │
│ ┌────────┐ │  │                                                          │  │
│ │FOLDERS │ │  │  ┌──────────────────────────────────────────────────┐   │  │
│ ├────────┤ │  │  │ Waveform Display                                 │   │  │
│ │📁 Root │ │  │  │  ╱╲  ╱╲╱╲ ╱╲                                     │   │  │
│ │📂 Music│ │  │  │ ╱  ╲╱    ╲  ╲  ╱╲                                │   │  │
│ │  📂 Rck│ │  │  │        ▼     ▼  Annotation markers               │   │  │
│ │  📁 Jaz│ │  │  └──────────────────────────────────────────────────┘   │  │
│ └────────┘ │  │                                                          │  │
│            │  │  [Add] [Edit] [Delete] [Clear] [Export]                 │  │
│ ┌────────┐ │  │                                                          │  │
│ │ FILES  │ │  │  Time     │ Category    │ Text                          │  │
│ ├────────┤ │  │  ─────────┼─────────────┼──────────────────────         │  │
│ │★◐ sg1 │ │  │  00:15.3  │ Structure   │ Intro ends                    │  │
│ │  sg2   │ │  │  00:42.1  │ Structure   │ Verse 1 starts                │  │
│ │★ sg3   │ │  │  01:23.8  │ Performance │ Fix this note                 │  │
│ │⭐sg4   │ │  │                                                          │  │
│ │  sg5   │ │  │                                                          │  │
│ └────────┘ │  │                                                          │  │
│            │  └──────────────────────────────────────────────────────────┘  │
│            │                                                                  │
├────────────┴─────────────────────────────────────────────────────────────────┤
│ Ready  •  song_take_3.wav                                           v1.25    │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Key Features of New Layout

### Library Panel (Left Side - 350px)
```
┌──────────────┐
│ [📁] [🔄] ⋮  │  ← Compact toolbar
├──────────────┤
│ FOLDERS      │  ← Folders panel (150px)
│ 📁 Root      │
│ 📂 Music (5) │
│   📂 Rock    │
│   📁 Jazz    │
├──────────────┤
│ FILES (23)   │  ← Files panel (fills rest)
│ ★◐ song1 3:42│
│    song2 2:34│
│ ★  song3 4:12│
│ ⭐ song4 3:01│
│    song5 2:45│
│      ...     │
└──────────────┘
```

### More Menu (⋮) Contents
```
┌──────────────────────┐
│ Batch Rename         │
│ Convert WAV→MP3      │
├──────────────────────┤
│ ☑ ★ Best Takes       │  ← Filters (checkable)
│ ☐ ◐ Partial Takes    │
├──────────────────────┤
│ 📊 Practice Stats    │
│ 🎯 Practice Goals    │
│ 🎵 Setlist Builder   │
└──────────────────────┘
```

## Space Comparison

### Before (Bottom Layout)
```
┌─────────────────────────────────────────┐
│                                         │
│  Work Area (Annotations/Clips/etc.)     │
│  Height: ~40% of screen                 │
│                                         │
├─────────────────────────────────────────┤
│  Library Panel (Full Width)             │
│  Height: ~40% of screen                 │
│  ┌──────────────┬────────────────────┐  │
│  │ Folders 25% │ Files 75%          │  │
│  └──────────────┴────────────────────┘  │
└─────────────────────────────────────────┘
```

### After (Left Side Layout)
```
┌──────────┬──────────────────────────────┐
│          │                              │
│ Library  │  Work Area                   │
│ 350px    │  (Annotations/Clips/etc.)    │
│ (30%)    │  ~70% of screen width        │
│          │  100% of content height      │
│ ┌──────┐ │                              │
│ │Fldrs │ │                              │
│ ├──────┤ │                              │
│ │Files │ │                              │
│ │      │ │                              │
│ └──────┘ │                              │
└──────────┴──────────────────────────────┘
```

## Benefits

1. **More Work Space**: 
   - Before: 40% screen height for work
   - After: 100% screen height for work, 70% width

2. **Side-by-Side Workflow**:
   - See library and work area simultaneously
   - Natural left-to-right flow: select → work

3. **Compact Design**:
   - Toolbar: 2 rows → 1 row (menu-based)
   - Panel: Full width → 350px
   - Better use of vertical space

4. **Always Accessible**:
   - No scrolling needed to reach files
   - Quick file switching during annotation work
   - Library visible in all tabs
