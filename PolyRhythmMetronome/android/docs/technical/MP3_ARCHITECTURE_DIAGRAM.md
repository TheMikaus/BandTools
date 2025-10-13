# MP3 Implementation Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        PolyRhythmMetronome Android                        │
│                       MP3 Tick Sound Architecture                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                              App Startup                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  1. App Launches                                                          │
│       ↓                                                                   │
│  2. SimpleMetronomeEngine.__init__()                                      │
│       ↓                                                                   │
│  3. Mp3TickCache.__init__()                                              │
│       ↓                                                                   │
│  4. _scan_ticks_folder()  ──→  Reads ticks/ directory                   │
│       ↓                         Identifies single/paired MP3s            │
│  5. Tick names available        Populates _pairs dictionary              │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                           User Adds Layer                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  1. User taps + button                                                    │
│       ↓                                                                   │
│  2. LayerWidget created                                                   │
│       ↓                                                                   │
│  3. Mode spinner shows: ["tone", "drum", "mp3_tick"]                     │
│       ↓                                                                   │
│  4. User selects "mp3_tick"                                              │
│       ↓                                                                   │
│  5. _build_mode_value() called                                           │
│       ↓                                                                   │
│  6. get_mp3_tick_choices() ──→ Mp3TickCache.get_available_ticks()       │
│       ↓                                                                   │
│  7. Tick dropdown populated with available ticks                         │
│       ↓                                                                   │
│  8. User selects tick (e.g., "woodblock")                                │
│       ↓                                                                   │
│  9. layer["mp3_tick"] = "woodblock"                                      │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                         Metronome Playback                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  SimpleMetronomeEngine._run() [metronome thread]                         │
│       ↓                                                                   │
│  For each layer on beat:                                                  │
│       ↓                                                                   │
│  1. Determine if accent beat (first of measure)                          │
│       ↓                                                                   │
│  2. _get_audio_data(layer, is_accent=True/False)                         │
│       │                                                                   │
│       ├──→ if mode == "mp3_tick":                                        │
│       │      ↓                                                            │
│       │    mp3_ticks.get(layer["mp3_tick"], is_accent)                   │
│       │      ↓                                                            │
│       │    Mp3TickCache.get("woodblock", is_accent=True)                 │
│       │      │                                                            │
│       │      ├──→ Look up in _pairs: ("woodblock_1.mp3", "woodblock_2.mp3") │
│       │      │                                                            │
│       │      ├──→ If is_accent: path = "woodblock_1.mp3"                 │
│       │      │    Else:          path = "woodblock_2.mp3"                │
│       │      │                                                            │
│       │      └──→ _wave_cache.get(path)                                  │
│       │             ↓                                                     │
│       │           WaveCache.get(path)                                    │
│       │             │                                                     │
│       │             ├──→ Check cache: if cached, return                  │
│       │             │                                                     │
│       │             └──→ Not cached:                                     │
│       │                    ↓                                              │
│       │                  _read_mp3(path)  [see below]                    │
│       │                    ↓                                              │
│       │                  Cache and return samples                        │
│       │                                                                   │
│       └──→ Return numpy array of float32 samples                         │
│                                                                           │
│  3. Apply volume: audio_data * volume                                    │
│       ↓                                                                   │
│  4. _play_sound(audio_data, volume, channel)                             │
│       ↓                                                                   │
│  5. Convert to stereo, int16                                             │
│       ↓                                                                   │
│  6. AudioTrack.write() ──→ Audio plays                                   │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                    MP3 Decoding Process (First Load)                      │
│                         WaveCache._read_mp3()                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  Input: MP3 file path                                                     │
│       ↓                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐        │
│  │                  Android MediaExtractor                       │        │
│  │  - Load MP3 file                                             │        │
│  │  - Find audio track                                          │        │
│  │  - Extract format info (sample rate, channels, codec)       │        │
│  └─────────────────────────────────────────────────────────────┘        │
│       ↓                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐        │
│  │                  Android MediaCodec                           │        │
│  │  - Create decoder for MP3 codec                              │        │
│  │  - Configure with audio format                               │        │
│  │  - Start decoder                                             │        │
│  └─────────────────────────────────────────────────────────────┘        │
│       ↓                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐        │
│  │                    Decode Loop                                │        │
│  │                                                               │        │
│  │  While not EOF:                                              │        │
│  │    1. Dequeue input buffer                                   │        │
│  │    2. Read compressed data from extractor                    │        │
│  │    3. Queue input buffer                                     │        │
│  │    4. Dequeue output buffer                                  │        │
│  │    5. Read PCM samples                                       │        │
│  │    6. Append to samples list                                 │        │
│  │    7. Release output buffer                                  │        │
│  └─────────────────────────────────────────────────────────────┘        │
│       ↓                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐        │
│  │               Post-Processing                                 │        │
│  │  - Concatenate all decoded samples                           │        │
│  │  - Convert stereo to mono (if needed)                        │        │
│  │  - Normalize to float32 [-1.0, 1.0]                          │        │
│  └─────────────────────────────────────────────────────────────┘        │
│       ↓                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐        │
│  │               Resampling (if needed)                          │        │
│  │  - If sample_rate != 44100:                                  │        │
│  │    - Linear interpolation                                    │        │
│  │    - Resample to 44100 Hz                                    │        │
│  └─────────────────────────────────────────────────────────────┘        │
│       ↓                                                                   │
│  Output: NumPy array[float32] of audio samples                           │
│       ↓                                                                   │
│  Cached in WaveCache._c dictionary                                       │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
┌──────────────┐
│   ticks/     │
│   folder     │
│              │
│ • click.mp3  │
│ • wood_1.mp3 │
│ • wood_2.mp3 │
└──────┬───────┘
       │
       │ App Startup
       │
       ↓
┌─────────────────────┐
│   Mp3TickCache      │
│                     │
│ _scan_ticks_folder()│
│         ↓           │
│   _pairs = {        │
│     "click": ("click.mp3", None),
│     "wood":  ("wood_1.mp3", "wood_2.mp3")
│   }                 │
└──────┬──────────────┘
       │
       │ get_available_ticks()
       │
       ↓
┌─────────────────────┐
│   UI Dropdown       │
│                     │
│ • click             │
│ • wood              │
└──────┬──────────────┘
       │
       │ User selects "wood"
       │
       ↓
┌─────────────────────┐
│   Layer Data        │
│                     │
│ {                   │
│   "mode": "mp3_tick"│
│   "mp3_tick": "wood"│
│   ...               │
│ }                   │
└──────┬──────────────┘
       │
       │ On beat (is_accent=True)
       │
       ↓
┌─────────────────────┐
│ Mp3TickCache.get()  │
│   ("wood", True)    │
│         ↓           │
│   Select wood_1.mp3 │
└──────┬──────────────┘
       │
       ↓
┌─────────────────────┐
│  WaveCache.get()    │
│  ("wood_1.mp3")     │
│         ↓           │
│   Check cache?      │
│    ├─Yes → Return   │
│    └─No  → Decode   │
└──────┬──────────────┘
       │
       │ If not cached
       │
       ↓
┌─────────────────────────────┐
│  MediaExtractor              │
│  + MediaCodec                │
│                              │
│  MP3 → PCM (int16)          │
│      → NumPy (float32)      │
│      → Cache + Return       │
└──────┬──────────────────────┘
       │
       ↓
┌─────────────────────┐
│  Audio samples      │
│  [0.1, 0.3, -0.2...]│
│  (float32 array)    │
└──────┬──────────────┘
       │
       │ Apply volume
       │
       ↓
┌─────────────────────┐
│  _play_sound()      │
│                     │
│  • Convert to stereo│
│  • Convert to int16 │
│  • AudioTrack.write │
└──────┬──────────────┘
       │
       ↓
   🔊 Sound!
```

## Class Relationships

```
┌──────────────────────────────────────────────────────┐
│              SimpleMetronomeEngine                     │
│                                                        │
│  Fields:                                              │
│    • tone_gen: ToneGenerator                          │
│    • drum_synth: DrumSynth                            │
│    • mp3_ticks: Mp3TickCache ◄────────┐              │
│                                        │              │
│  Methods:                              │              │
│    • _get_audio_data(layer, is_accent)│              │
│         ↓                              │              │
│         Calls mp3_ticks.get()          │              │
└────────────────────────────────────────┼──────────────┘
                                         │
                                         │ has-a
                                         │
                    ┌────────────────────┴──────────────────┐
                    │        Mp3TickCache                    │
                    │                                        │
                    │  Fields:                              │
                    │    • _wave_cache: WaveCache ◄─────┐   │
                    │    • _pairs: dict                  │   │
                    │                                    │   │
                    │  Methods:                          │   │
                    │    • _scan_ticks_folder()          │   │
                    │    • get_available_ticks()         │   │
                    │    • get(name, is_accent)          │   │
                    │         ↓                          │   │
                    │         Calls _wave_cache.get()    │   │
                    └────────────────────────────────────┼───┘
                                                         │
                                                         │ has-a
                                                         │
                                      ┌──────────────────┴──────────────┐
                                      │       WaveCache                  │
                                      │                                  │
                                      │  Fields:                        │
                                      │    • _c: dict (cache)           │
                                      │                                  │
                                      │  Methods:                        │
                                      │    • get(path)                  │
                                      │    • _read_mp3(path)            │
                                      │    • _read_wav_any(path)        │
                                      │    • _resample_linear()         │
                                      │         ↓                        │
                                      │         Uses MediaExtractor      │
                                      │              + MediaCodec        │
                                      └──────────────────────────────────┘
```

## State Machine - Layer Mode

```
┌─────────────┐
│  Layer      │
│  Created    │
└──────┬──────┘
       │
       ↓
┌─────────────┐     mode = "tone"
│             ├────────────────────────┐
│   Mode      │     mode = "drum"      │
│  Selection  ├────────────────────────┤
│             │     mode = "mp3_tick"  │
└─────────────┤                        │
              │                        │
              │                        ↓
              │              ┌──────────────────┐
              │              │  MP3 Tick Mode   │
              │              │                  │
              │              │  • Tick dropdown │
              │              │  • Select tick   │
              │              │  • Play          │
              │              └──────────────────┘
              │                        │
              │                        ↓
              │              ┌──────────────────┐
              │              │  On Beat         │
              │              │                  │
              │              │  is_accent?      │
              │              │    ├─Yes: _1 file│
              │              │    └─No:  _2 file│
              │              └──────────────────┘
              │
              ↓
       [Other modes...]
```

## Threading Model

```
┌─────────────────────────────────────────────────────────┐
│                     Main UI Thread                       │
│  • Kivy event loop                                       │
│  • User interactions                                     │
│  • LayerWidget updates                                   │
│  • Dropdown population                                   │
└─────────────────────────────────────────────────────────┘
                         │
                         │ Start metronome
                         │
                         ↓
┌─────────────────────────────────────────────────────────┐
│             SimpleMetronomeEngine._run()                 │
│                  (Separate Thread)                       │
│                                                          │
│  • Beat timing loop                                     │
│  • Calls _get_audio_data() ──→ Mp3TickCache            │
│  • Calls _play_sound()      ──→ AudioTrack.write()     │
│  • No file I/O (all cached)                             │
│                                                          │
└─────────────────────────────────────────────────────────┘
                         │
                         │ Schedule callback
                         │
                         ↓
┌─────────────────────────────────────────────────────────┐
│              Clock.schedule_once()                       │
│              (Back to UI Thread)                         │
│                                                          │
│  • Visual feedback (color flash)                        │
│  • UI updates                                            │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## File Scanning Logic

```
Startup: Mp3TickCache.__init__() → _scan_ticks_folder()

For each .mp3 file in ticks/:
    
    Extract name without extension
    
    If name ends with "_1":
        base_name = name[:-2]
        
        Look for matching "_2" file:
            If found:
                _pairs[base_name] = (path_1, path_2)  # Paired
            Else:
                _pairs[name] = (path, None)            # Single (keeps _1)
    
    Else if name ends with "_2":
        (Only process if no matching _1 was found)
    
    Else:
        _pairs[name] = (path, None)                    # Single

Examples:
    click.mp3                    → _pairs["click"] = (click.mp3, None)
    wood_1.mp3 + wood_2.mp3     → _pairs["wood"] = (wood_1.mp3, wood_2.mp3)
    test_1.mp3 (no matching _2) → _pairs["test_1"] = (test_1.mp3, None)
```

## Performance Characteristics

```
┌──────────────────┬────────────────┬─────────────────┐
│   Operation      │   When         │   Performance   │
├──────────────────┼────────────────┼─────────────────┤
│ Scan ticks/      │ App startup    │ O(n) files      │
│ Decode MP3       │ First use      │ ~10-50ms/file   │
│ Cache lookup     │ Every beat     │ O(1)            │
│ Array access     │ Every beat     │ O(1)            │
│ Volume adjust    │ Every beat     │ O(m) samples    │
│ Stereo convert   │ Every beat     │ O(m) samples    │
└──────────────────┴────────────────┴─────────────────┘

Memory per tick sound (example):
    100ms @ 44.1kHz mono = 4,410 samples
    float32 = 4 bytes/sample
    Memory = 4,410 × 4 = 17,640 bytes (~17 KB)
```

## Error Handling Flow

```
User selects MP3 tick
        ↓
_get_audio_data(layer, is_accent)
        ↓
    try:
        mp3_ticks.get(tick_name, is_accent)
            ↓
        WaveCache.get(path)
            ↓
        _read_mp3(path)
            ↓
        [MediaCodec decode]
            ↓
        Return samples
    catch Exception:
        Log error ──────────────────┐
        Return None                 │
        ↓                           ↓
    If None:                  User sees in logs
        Fallback to tone      (doesn't crash)
        Return beep
```

This architecture ensures robust operation even when MP3 files are missing or corrupted.
