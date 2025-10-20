# Visual Changes Guide

## 1. Media Buttons - Before and After

### Before:
```
[⏮] [▶] [⏹] [⏭]
36px  40px 36px 36px
Small, thin text, hard to see
```

### After:
```
[⏮] [▶] [⏹] [⏭]
40px  44px 40px 40px
Larger, BOLD text, easy to see
Font size: 18-20px instead of default (~14px)
```

The play/pause button is now clearly the primary control with bold white text on blue background.

---

## 2. Layout Reorganization

### Before:
```
┌─────────────────────────────┐
│ Toolbar & Playback Controls │
├─────────────────────────────┤
│ Tab Bar                     │ ← Tabs at top
├─────────────────────────────┤
│                             │
│ Tab Content Area            │
│ (Library/Annotations/etc)   │
│                             │
├─────────────────────────────┤
│ Now Playing Panel           │ ← At bottom, hard to see
├─────────────────────────────┤
│ Status Bar                  │
└─────────────────────────────┘
```

### After:
```
┌─────────────────────────────┐
│ Toolbar & Playback Controls │
├─────────────────────────────┤
│ Now Playing Panel           │ ← Moved up for prominence
├─────────────────────────────┤
│ Tab Bar                     │
├─────────────────────────────┤
│                             │
│ Tab Content Area            │
│ (Library/Annotations/etc)   │
│                             │
├─────────────────────────────┤
│ Status Bar                  │
└─────────────────────────────┘
```

---

## 3. Library Tab - File List

### Before:
```
Take | File Name                    | Library      | Duration
-----|------------------------------|--------------|----------
★ ◐  | song_take_1.wav              | MySong       |    --:--
     | song_take_2.mp3              |              |    03:45
★    | song_take_3.wav              | MySong       |    --:--
```
Issues:
- Missing durations (--:--)
- No way to edit library names
- Duration right-aligned

### After:
```
Take | File Name                    | Library      |  Duration
-----|------------------------------|--------------|----------
★ ◐  | song_take_1.wav              | MySong       |   03:42
     | song_take_2.mp3              | Rock Ballad  |   03:45
★    | song_take_3.wav              | MySong       |   03:41
```
Right-click menu now includes:
```
┌─────────────────────────┐
│ ▶ Play                  │
├─────────────────────────┤
│ 📝 Add Annotation...    │
│ ✂ Create Clip...        │
├─────────────────────────┤
│ ★ Mark as Best Take     │
│ ◐ Mark as Partial Take  │
├─────────────────────────┤
│ ✏ Edit Library Name...  │ ← NEW!
├─────────────────────────┤
│ 📁 Show in Explorer     │
│ 📋 Copy Path            │
├─────────────────────────┤
│ ℹ Properties            │
└─────────────────────────┘
```

**Edit Library Name Dialog:**
```
┌──────────────────────────────────────┐
│ Edit Library Name                 [X]│
├──────────────────────────────────────┤
│ File: song_take_2.mp3                │
│                                      │
│ Library Name (Song Title):           │
│ ┌──────────────────────────────────┐ │
│ │ Rock Ballad                      │ │
│ └──────────────────────────────────┘ │
│                                      │
│ Tip: This name will be used to       │
│ identify the song in your library.   │
│                                      │
│              [Cancel]  [OK]          │
└──────────────────────────────────────┘
```

---

## 4. Annotations Tab - Waveform Added

### Before:
```
┌─────────────────────────────────────────┐
│ Annotations Tab                         │
├─────────────────────────────────────────┤
│                                         │
│ [Add] [Edit] [Delete] [Clear] [Export] │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ Time    │ Text      │ Category      │ │
│ ├─────────┼───────────┼───────────────┤ │
│ │ 00:15.3 │ Intro end │ Structure     │ │
│ │ 00:42.1 │ Verse 1   │ Structure     │ │
│ │ 01:23.8 │ Fix note  │ Performance   │ │
│ └─────────────────────────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
```

### After:
```
┌─────────────────────────────────────────┐
│ Annotations Tab                         │
├─────────────────────────────────────────┤
│ ┌─────────────────────────────────────┐ │
│ │ Waveform Display                    │ │ ← NEW!
│ │                                     │ │
│ │     ╱╲    ╱╲╱╲  ╱╲                 │ │
│ │    ╱  ╲  ╱    ╲╱  ╲    ╱╲          │ │
│ │   ╱    ╲╱          ╲  ╱  ╲         │ │
│ │  ────▼─────▼────────▼───────        │ │
│ │  │   │    │        │               │ │
│ │  Intro  V1    Fix note             │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [Add] [Edit] [Delete] [Clear] [Export] │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ Time    │ Text      │ Category      │ │
│ ├─────────┼───────────┼───────────────┤ │
│ │ 00:15.3 │ Intro end │ Structure     │ │
│ │ 00:42.1 │ Verse 1   │ Structure     │ │
│ │ 01:23.8 │ Fix note  │ Performance   │ │
│ └─────────────────────────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
```

Features:
- Visual representation of audio
- Annotation markers shown on waveform
- Double-click markers to edit annotations
- Auto-generates when file is selected

---

## 5. Duration Display Improvements

### Column Header Alignment:
```
Before:                    After:
Take │ File Name │ Duration    Take │ File Name │  Duration
     │           │ 03:42            │           │   03:42
(left aligned)              (center aligned)
```

### All Files Now Show Duration:
- Previously: Many files showed `--:--` (no duration)
- Now: All files display actual duration
- Format: `MM:SS` for times under 1 hour, `HH:MM:SS` for longer files
- Automatically extracted on first view
- Cached for fast subsequent loads

---

## Technical Implementation Details

### Media Buttons (PlaybackControls.qml):
```qml
// Before:
StyledButton {
    text: "▶"
    implicitWidth: 40
    implicitHeight: 32
}

// After:
StyledButton {
    text: "▶"
    implicitWidth: 44
    implicitHeight: 36
    
    contentItem: Text {
        text: parent.text
        font.pixelSize: 20
        font.bold: true
        color: "#ffffff"
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
}
```

### Duration Extraction (file_manager.py):
```python
@pyqtSlot(str, result=int)
def extractDuration(self, file_path: str) -> int:
    # Try mutagen for all formats
    from mutagen import File as MutagenFile
    audio = MutagenFile(str(path))
    if audio and hasattr(audio.info, 'length'):
        duration_ms = int(audio.info.length * 1000)
        self._cache_duration(file_path, duration_ms)
        return duration_ms
    
    # Fallback to wave module for WAV
    import wave
    with wave.open(str(path), 'rb') as wav_file:
        frames = wav_file.getnframes()
        rate = wav_file.getframerate()
        duration_ms = int((frames / rate) * 1000)
        self._cache_duration(file_path, duration_ms)
        return duration_ms
```

### Library Name Editing (file_manager.py):
```python
@pyqtSlot(str, str)
def setProvidedName(self, file_path: str, provided_name: str) -> None:
    directory = Path(file_path).parent
    names_file = directory / ".provided_names.json"
    
    provided_names = self._load_provided_names(directory)
    
    if provided_name.strip():
        provided_names[filename] = provided_name.strip()
    else:
        provided_names.pop(filename, None)
    
    with open(names_file, 'w', encoding='utf-8') as f:
        json.dump(provided_names, f, indent=2, ensure_ascii=False)
    
    self.filesChanged.emit()  # Refresh UI
```

---

## User Experience Improvements

1. **Easier Media Control**: Larger, bolder buttons reduce click errors and eye strain
2. **Better Workflow**: Now Playing panel is more visible when switching between tabs
3. **Library Management**: Can organize songs without editing JSON files manually
4. **Visual Feedback**: Waveform helps understand annotation context
5. **Complete Information**: All files show duration, no missing data
6. **Professional Look**: Centered duration column looks more polished

---

## Backward Compatibility

All changes are fully backward compatible:
- Existing `.provided_names.json` files work unchanged
- Existing annotations and metadata preserved
- No migration needed
- Optional features degrade gracefully (e.g., mutagen library)
