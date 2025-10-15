# Verbose Logging UI Preview

This document provides a visual preview of the verbose logging feature UI.

## Main Window with Verbose Logging Enabled

```
╔═══════════════════════════════════════════════════════════════════════════╗
║ Stereo Subdivision Metronome — Compact                              [_][□][X]
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  ┌─────────────────────────────────────────────────────────────────────┐  ║
║  │ BPM [120 ] Beats [4 ] Accent × [1.6 ] ☑ Flash ☑ Verbose Log      │  ║
║  └─────────────────────────────────────────────────────────────────────┘  ║
║                                                                             ║
║  ┌─ New Layer ─────────────────────────────────────────────────────────┐  ║
║  │ Subdiv [4 ] Vol [1.0] ⦿ Tone ○ WAV ○ Drum ○ MP3  Color [Pick]    │  ║
║  │ Freq (Hz) [880  ]  WAV [              ] [Browse]  Drum [snare ▾]  │  ║
║  │          [     Add to Left     ]      [     Add to Right     ]     │  ║
║  └─────────────────────────────────────────────────────────────────────┘  ║
║                                                                             ║
║  ┌─ Left Ear Layers ────┐      ┌───┐      ┌─ Right Ear Layers ────┐      ║
║  │ ■ Layer 1: subdiv=4  │      │ → │      │ ■ Layer 1: subdiv=3   │      ║
║  │   Volume: 1.0        │      │   │      │   Volume: 1.0         │      ║
║  │   Tone (800/400 Hz)  │      │ ← │      │   Tone (800/400 Hz)   │      ║
║  │                      │      │   │      │                       │      ║
║  │ ■ Layer 2: subdiv=8  │      └───┘      │                       │      ║
║  │   Volume: 0.8        │                 │                       │      ║
║  │   WAV: click.wav     │                 │                       │      ║
║  │                      │                 │                       │      ║
║  │                      │                 │                       │      ║
║  └──────────────────────┘                 └───────────────────────┘      ║
║                                                                             ║
║  [  Play  ][  Stop  ][ Save WAV… ][ Save Rhythm… ][ Load… ][ New ]        ║
║                                                                             ║
║  ┌─ Verbose Log ──────────────────────────────────────────────────────┐  ║
║  │ [14:23:45.100] === Verbose logging enabled ===                    │↑ ║
║  │ [14:23:45.101] Started playback with sounddevice                  │█ ║
║  │ [14:23:45.101] Left Layer 1 (subdiv=4): played | Delta: N/A (fir│█ ║
║  │ st) | Expected: 125.00ms                                          │█ ║
║  │ [14:23:45.101] Right Layer 1 (subdiv=3): played | Delta: N/A (fi│  ║
║  │ rst) | Expected: 166.67ms                                         │  ║
║  │ [14:23:45.101] Left Layer 2 (subdiv=8): played | Delta: N/A (fir│  ║
║  │ st) | Expected: 62.50ms                                           │  ║
║  │ [14:23:45.164] Left Layer 2 (subdiv=8): played | Delta: 62.50ms │↓ ║
║  │ | Expected: 62.50ms                                               │  ║
║  │◄─────────────────────────────────────────────────────────────────►│  ║
║  │ [Clear Log]                                                        │  ║
║  └────────────────────────────────────────────────────────────────────┘  ║
║                                                                             ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

## UI Components Description

### 1. Verbose Log Checkbox
**Location:** Top control bar, after the "Flash" checkbox

**Behavior:**
- Unchecked by default
- When checked: Log window appears at bottom of application
- When unchecked: Log window is hidden (content preserved)

### 2. Log Window (LabelFrame)
**Location:** Bottom of application, below transport controls

**Components:**
- **Title:** "Verbose Log"
- **Text Widget:** 
  - Height: 8 rows (approximately 8 lines visible)
  - Background: Light gray (#f8f9fa)
  - Text: Dark gray (#212529)
  - Font: Courier 9pt (monospace for alignment)
  - State: Read-only (disabled except during updates)
- **Vertical Scrollbar (↑↓):** Right side of text widget
- **Horizontal Scrollbar (◄►):** Bottom of text widget
- **Clear Log Button:** Bottom left of log frame

### 3. Log Entry Format

Each line shows:
```
[HH:MM:SS.mmm] Side Layer N (subdiv=X): played | Delta: DDD.DDms | Expected: EEE.EEms
```

**Example entries:**
```
[14:23:45.101] Left Layer 1 (subdiv=4): played | Delta: N/A (first) | Expected: 125.00ms
[14:23:45.226] Left Layer 1 (subdiv=4): played | Delta: 125.00ms | Expected: 125.00ms
[14:23:45.268] Right Layer 1 (subdiv=3): played | Delta: 167.00ms | Expected: 166.67ms
```

## Window Size

**Default dimensions:**
- Width: 820 pixels
- Height: Approximately 740 pixels (100 pixels taller with log window shown)

**Minimum dimensions:**
- Width: 720 pixels
- Height: 560 pixels (without log window)

## Behavior Details

### Showing the Log Window
1. User checks "Verbose Log" checkbox
2. Log window grid appears at row 4 (below transport buttons)
3. Initial message: `=== Verbose logging enabled ===`
4. Window may need to be resized by user to accommodate log window

### Hiding the Log Window
1. User unchecks "Verbose Log" checkbox
2. Log window is hidden using `grid_remove()`
3. Final message: `=== Verbose logging disabled ===`
4. Previous log entries are preserved (still in widget memory)
5. Window shrinks back to original size

### During Playback
1. As metronome plays, log entries appear in real-time
2. Window auto-scrolls to show latest entries
3. User can scroll up to view older entries
4. Entries accumulate until "Clear Log" is pressed

### Clearing the Log
1. User clicks "Clear Log" button
2. All text content is removed from widget
3. Next log entry starts fresh

## Color Scheme

- **Window background:** Default system theme (gray/white)
- **Log text background:** Light gray (#f8f9fa)
- **Log text foreground:** Dark gray (#212529)
- **Scrollbars:** System default
- **Buttons:** System default (ttk themed)

## Accessibility Notes

- Monospace font ensures timing values align vertically
- High contrast text (dark on light)
- Scrollable for users who need larger text
- All functionality keyboard accessible via tab navigation
- Clear labeling of all controls

## Layout Grid Structure

```
Row 0: Top controls (BPM, Beats, Accent, Flash, Verbose Log)
Row 1: New Layer controls
Row 2: Layer lists (Left | Move buttons | Right)
Row 3: Transport buttons
Row 4: Verbose Log window (only when enabled)
```

## Responsive Behavior

- Log window expands/contracts with main window
- Text widget fills available space
- Scrollbars appear as needed
- Layer list panels maintain equal width

## Performance Notes

- Log updates happen on UI thread (no blocking)
- Typical log entry: ~100 bytes
- At 120 BPM with 3 layers: ~60 entries/minute
- Memory usage: Negligible for typical sessions (<1 MB)
- Consider clearing log during extended practice (>30 minutes)
