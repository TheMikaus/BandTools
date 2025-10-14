# Timing Diagnostics UI - Visual Changes

## UI Layout Changes in v1.7.0

### Before (v1.6.0)
```
┌─────────────────────────────────────────┐
│  PolyRhythm Metronome                   │
│  BPM: [120] [─────────────]             │
│  Master: [1.0x] [─────────────]         │
│  [60][80][100][120][140][160][180][200] │
├─────────────────────────────────────────┤
│  LEFT LAYERS    │    RIGHT LAYERS       │
│  ┌──────────┐   │   ┌──────────┐        │
│  │ Layer 1  │   │   │ Layer 1  │        │
│  └──────────┘   │   └──────────┘        │
├─────────────────────────────────────────┤
│         [      PLAY      ]              │ ← Height: 140dp
│  [NEW] [LOAD] [SAVE]    [LOGS]         │
└─────────────────────────────────────────┘
```

### After (v1.7.0)
```
┌─────────────────────────────────────────┐
│  PolyRhythm Metronome                   │
│  BPM: [120] [─────────────]             │
│  Master: [1.0x] [─────────────]         │
│  [60][80][100][120][140][160][180][200] │
├─────────────────────────────────────────┤
│  LEFT LAYERS    │    RIGHT LAYERS       │
│  ┌──────────┐   │   ┌──────────┐        │
│  │ Layer 1  │   │   │ Layer 1  │        │
│  └──────────┘   │   └──────────┘        │
├─────────────────────────────────────────┤
│         [      PLAY      ]              │ ← Height: 180dp
│      [NEW] [LOAD] [SAVE]                │ ← NEW: Separate row
│  [TIMING DEBUG: OFF]  [VIEW LOGS]      │ ← NEW: Diagnostics row
└─────────────────────────────────────────┘
```

**Key Changes**:
- Controls section height: 140dp → 180dp
- Button layout: 2 rows → 3 rows
- New button: TIMING DEBUG toggle

---

## Timing Debug Button States

### OFF State (Default)
```
┌────────────────────────────────┐
│     TIMING DEBUG: OFF          │  ← Gray background (0.5, 0.5, 0.5)
└────────────────────────────────┘
```

**Visual properties**:
- Text: "TIMING DEBUG: OFF"
- Background: Gray (#808080)
- Button state: normal (not pressed)
- Font size: 12sp

### ON State (Enabled)
```
┌────────────────────────────────┐
│     TIMING DEBUG: ON           │  ← Orange background (0.8, 0.5, 0.2)
└────────────────────────────────┘
```

**Visual properties**:
- Text: "TIMING DEBUG: ON"
- Background: Orange (#CC8033)
- Button state: down (pressed/toggled)
- Font size: 12sp

---

## Control Section Layout Details

### Row Heights (Total: 180dp)

**Row 1: Play/Stop Button (40%)**
```
┌─────────────────────────────────────────┐
│                                         │
│            [      PLAY      ]           │  ← 72dp (40% of 180dp)
│                                         │
└─────────────────────────────────────────┘
```

**Row 2: File Operations (30%)**
```
┌─────────────────────────────────────────┐
│    [NEW]      [LOAD]      [SAVE]        │  ← 54dp (30% of 180dp)
└─────────────────────────────────────────┘
```

**Row 3: Diagnostics & Logs (30%)**
```
┌─────────────────────────────────────────┐
│  [TIMING DEBUG: OFF]    [VIEW LOGS]     │  ← 54dp (30% of 180dp)
└─────────────────────────────────────────┘
```

---

## Button Arrangement - Detailed View

### Before v1.7.0
```
Controls BoxLayout (orientation='vertical', height='140dp')
├─ Play Button (size_hint_y=0.5, height=70dp)
│  └─ Text: "PLAY" or "STOP"
│
└─ File/Logs BoxLayout (size_hint_y=0.5, height=70dp)
   ├─ NEW Button
   ├─ LOAD Button
   ├─ SAVE Button
   ├─ Spacer (size_hint_x=0.3)
   └─ LOGS Button
```

### After v1.7.0
```
Controls BoxLayout (orientation='vertical', height='180dp')
├─ Play Button (size_hint_y=0.4, height=72dp)
│  └─ Text: "PLAY" or "STOP"
│
├─ File BoxLayout (size_hint_y=0.3, height=54dp)
│  ├─ NEW Button
│  ├─ LOAD Button
│  └─ SAVE Button
│
└─ Diagnostics BoxLayout (size_hint_y=0.3, height=54dp)
   ├─ TIMING DEBUG ToggleButton
   └─ VIEW LOGS Button
```

**Changes**:
- Removed spacer between file ops and logs
- Separated into 3 distinct rows
- File operations now fill width evenly
- Diagnostics row has two equal-width buttons

---

## Visual Feedback Flow

### User Interaction: Enabling Diagnostics

**Step 1: Initial State**
```
┌────────────────────────────────┐
│  [TIMING DEBUG: OFF]  [LOGS]   │  ← Gray button
└────────────────────────────────┘
```

**Step 2: User Taps Button**
```
┌────────────────────────────────┐
│  [TIMING DEBUG: OFF]  [LOGS]   │  ← Button press animation
└────────────────────────────────┘
          ↓ (tap)
```

**Step 3: Button Changes State**
```
┌────────────────────────────────┐
│  [TIMING DEBUG: ON]   [LOGS]   │  ← Orange button, "ON" text
└────────────────────────────────┘
```

**Step 4: Log Message Appears**
```
Console/LogCapture:
[23:45:12.345] [timing] Timing diagnostics ENABLED - verbose logging active
[23:45:12.345] [timing] Diagnostics will show:
[23:45:12.345] [timing]   - Beat timing errors (expected vs actual)
[23:45:12.345] [timing]   - Sleep accuracy (requested vs actual sleep time)
[23:45:12.345] [timing]   - Audio processing times (get_audio_data and play_sound)
[23:45:12.345] [timing]   - Periodic statistics every 50 beats
[23:45:12.345] [timing]   - Final statistics when metronome stops
```

**Step 5: If Metronome is Running**
```
Console:
[23:45:12.346] [timing] Restarting metronome to apply timing diagnostics setting...
[23:45:12.347] [engine] Stopping metronome with 2 threads...
[23:45:12.348] [engine] Stopped 2 threads, 0 timed out
[23:45:12.348] [engine] Metronome stopped
[23:45:12.349] [engine] Starting metronome engine
[23:45:12.349] [engine]   BPM: 120, Beats per measure: 4
[23:45:12.349] [engine]   Timing diagnostics: ENABLED
...
```

---

## Color Specifications

### Button Background Colors

| State    | RGB Values        | Hex Code | Visual Description |
|----------|-------------------|----------|--------------------|
| OFF      | (0.5, 0.5, 0.5)   | #808080  | Medium gray        |
| ON       | (0.8, 0.5, 0.2)   | #CC8033  | Burnt orange       |

### Play/Stop Button Colors

| State    | RGB Values        | Hex Code | Visual Description |
|----------|-------------------|----------|--------------------|
| PLAY     | (0.2, 0.8, 0.2)   | #33CC33  | Green              |
| STOP     | (0.8, 0.2, 0.2)   | #CC3333  | Red                |

### VIEW LOGS Button Color

| State    | RGB Values        | Hex Code | Visual Description |
|----------|-------------------|----------|--------------------|
| Normal   | (0.3, 0.3, 0.8)   | #4D4DCC  | Blue               |

---

## Screen Space Impact

### Before v1.7.0
- Controls section: 140dp
- Available space for layers: Screen height - 180dp (header) - 140dp (controls) = Variable

### After v1.7.0
- Controls section: 180dp (+40dp increase)
- Available space for layers: Screen height - 180dp (header) - 180dp (controls) = Variable

**Impact on 10" tablet (1200px height)**:
- Before: 880px for layers
- After: 840px for layers (-40px, ~4.5% reduction)
- Still ample space for 4-6 layers per side

**Impact on 7" tablet (800px height)**:
- Before: 480px for layers
- After: 440px for layers (-40px, ~8% reduction)
- Still adequate for 2-3 layers per side

---

## Responsive Behavior

### Portrait Mode
```
┌──────────────────┐
│     Header       │ 180dp
├──────────────────┤
│     Layers       │ Variable
│  Left │ Right    │ (Scrollable)
├──────────────────┤
│    Controls      │ 180dp
│  [PLAY]          │
│  [File Ops]      │
│  [Diagnostics]   │
└──────────────────┘
```

### Landscape Mode
```
┌──────────────────────────────────┐
│           Header                 │ 180dp
├──────────────────────────────────┤
│   Layers     │    Controls       │ Variable
│ Left │ Right │  [PLAY]           │
│              │  [File Ops]       │
│              │  [Diagnostics]    │
└──────────────────────────────────┘
```

Note: Layout automatically adapts based on Window.size

---

## Accessibility Considerations

### Font Sizes
- TIMING DEBUG button: 12sp (readable on all devices)
- VIEW LOGS button: 12sp (matches TIMING DEBUG)
- File operation buttons: 14sp (slightly larger)
- Play/Stop button: 24sp (largest, most important)

### Touch Targets
- All buttons meet minimum 48dp touch target (Android guideline)
- Row heights (54dp and 72dp) exceed minimum requirements
- Adequate spacing (5dp) between buttons for tap accuracy

### Color Contrast
- OFF state (gray): Good contrast with dark background
- ON state (orange): Excellent contrast, high visibility
- Color-blind safe: Distinct brightness levels even without color

---

## Implementation Notes

### Button Creation Code
```python
# Timing diagnostics toggle button
self.timing_diag_btn = ToggleButton(
    text="TIMING DEBUG: OFF",
    font_size='12sp',
    background_color=(0.5, 0.5, 0.5, 1),
    state='down' if self.state.timing_diagnostics else 'normal'
)
self.timing_diag_btn.bind(on_press=self.on_toggle_timing_diagnostics)
```

### State Management
```python
def on_toggle_timing_diagnostics(self, instance):
    self.state.timing_diagnostics = instance.state == 'down'
    
    if self.state.timing_diagnostics:
        instance.text = "TIMING DEBUG: ON"
        instance.background_color = (0.8, 0.5, 0.2, 1)  # Orange
    else:
        instance.text = "TIMING DEBUG: OFF"
        instance.background_color = (0.5, 0.5, 0.5, 1)  # Gray
```

---

## Testing Checklist

Visual verification:
- [ ] Button appears at bottom of screen
- [ ] Button is next to VIEW LOGS
- [ ] OFF state shows gray background
- [ ] ON state shows orange background
- [ ] Text changes between "OFF" and "ON"
- [ ] Button is easily tappable
- [ ] Layout doesn't break on small screens
- [ ] Layout doesn't break on large screens
- [ ] Orientation changes preserve state
- [ ] State persists after save/load

---

**Version**: v1.7.0  
**UI Changes**: Controls section height +40dp, new diagnostics row  
**New Button**: TIMING DEBUG toggle (gray when OFF, orange when ON)  
**Last Updated**: 2025-10-13
