# Verbose Logging Feature

## Overview

The Verbose Logging feature provides real-time timing information for each sound that the metronome plays. This is useful for debugging timing issues, verifying accurate tempo, and understanding how different rhythm layers interact.

## Enabling Verbose Logging

1. Check the **"Verbose Log"** checkbox in the top control row (next to the "Flash" checkbox)
2. A log window will appear at the bottom of the application
3. Start playing the metronome - log entries will appear in real-time

## Log Window Features

- **Scrollable**: Both vertical and horizontal scrollbars allow viewing long log entries
- **Auto-scroll**: Automatically scrolls to show the latest entries
- **Clear Log**: Button to clear all accumulated log entries
- **Monospace Font**: Makes timing data easy to read and compare

## Understanding Log Entries

Each log entry shows:

```
[HH:MM:SS.mmm] Side Layer N (subdiv=X): played | Delta: XXX.XXms | Expected: XXX.XXms
```

### Components:

- **Timestamp** (`[HH:MM:SS.mmm]`): Exact time the sound was scheduled, with millisecond precision
- **Side**: Which ear/channel - "Left" or "Right"
- **Layer N**: Layer number (1, 2, 3, etc.)
- **subdiv=X**: Subdivision value for that layer
- **Delta**: Time since this layer last played
  - Shows "N/A (first)" on the first play
  - In milliseconds (ms)
- **Expected**: The calculated interval based on BPM and subdivision
  - In milliseconds (ms)

## Example Usage

### Scenario 1: Verifying Timing Accuracy

At 120 BPM with two layers (subdiv=4 and subdiv=3):

```
[14:23:45.100] Left Layer 1 (subdiv=4): played | Delta: N/A (first) | Expected: 125.00ms
[14:23:45.100] Right Layer 1 (subdiv=3): played | Delta: N/A (first) | Expected: 166.67ms
[14:23:45.225] Left Layer 1 (subdiv=4): played | Delta: 125.00ms | Expected: 125.00ms
[14:23:45.267] Right Layer 1 (subdiv=3): played | Delta: 167.00ms | Expected: 166.67ms
```

The Delta values should closely match the Expected values for accurate timing.

### Scenario 2: Debugging Timing Drift

If you notice the metronome sounds irregular:

1. Enable Verbose Logging
2. Watch the Delta values as the metronome plays
3. Compare Delta to Expected - significant differences indicate timing issues
4. Example of timing drift:
   ```
   Expected: 125.00ms | Delta: 125.00ms  ← Good
   Expected: 125.00ms | Delta: 124.50ms  ← Good (minor variation)
   Expected: 125.00ms | Delta: 140.00ms  ← Bad (significant drift)
   ```

## Performance Notes

- Verbose logging adds minimal overhead to the audio engine
- Log entries are sent to the UI asynchronously to avoid blocking audio
- When disabled, verbose logging has no performance impact
- Consider clearing the log periodically during long practice sessions to prevent memory buildup

## Tips

1. **Use with Flash**: Enable both "Flash" and "Verbose Log" to correlate visual flashing with log entries
2. **Test Simple First**: Start with a single layer to understand the log format before adding complexity
3. **Monitor Over Time**: Watch for patterns in timing variations - consistent drift vs random jitter
4. **Export for Analysis**: You can copy text from the log window for external analysis

## Disabling Verbose Logging

1. Uncheck the **"Verbose Log"** checkbox
2. The log window will be hidden
3. Logging stops immediately
4. You can re-enable it at any time - previous log entries are preserved until cleared

## Technical Details

For developers interested in the implementation:

- Timestamps use `datetime.now()` with millisecond precision
- Delta calculation: `current_time - last_play_time`
- Expected interval: `60.0 / BPM / subdivision * 1000` (in ms)
- Logging occurs in both `sounddevice` callback and `simpleaudio` loop
- Thread-safe message passing via `ui_after_callable`
