# Verbose Logging Implementation

## Overview

This document describes the technical implementation of the verbose logging feature for the PolyRhythmMetronome application.

## Architecture

### Components

1. **StreamEngine** - Audio engine with verbose logging support
2. **App** - GUI with log window and controls
3. **Log Callback** - Thread-safe communication between engine and UI

### Data Flow

```
Audio Callback Thread          UI Thread
     |                            |
     | (sound scheduled)          |
     v                            |
_log_verbose()                    |
     |                            |
     | (via ui_after_callable)    |
     +--------------------------->|
                                  v
                            _append_log()
                                  |
                                  v
                            Log Text Widget
```

## StreamEngine Changes

### New Attributes

```python
self.verbose_logging = False        # Enable/disable verbose logging
self.log_callback = None            # Callback to send log messages to UI
self.L_last_play_time = []         # Last play time for each left layer
self.R_last_play_time = []         # Last play time for each right layer
```

### New Method: `_log_verbose()`

```python
def _log_verbose(self, msg: str):
    """Log verbose message to UI callback if enabled."""
    if self.verbose_logging and self.log_callback is not None:
        try:
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            self.ui_after(lambda: self.log_callback(f"[{timestamp}] {msg}"))
        except Exception:
            pass  # Silently fail if logging fails
```

**Key Design Decisions:**
- Uses `ui_after()` callback to safely communicate from audio thread to UI thread
- Includes timestamp generation in the audio thread for accuracy
- Silent failure prevents logging errors from affecting audio playback

### Modified Methods

#### `start()`
- Initializes `L_last_play_time` and `R_last_play_time` arrays
- Each element initialized to `None` to indicate first play

#### `update_live_from_state()`
- Modified `recalc()` helper to accept and preserve `old_last_play` parameter
- Maintains last play time tracking when layers change during playback

#### `_callback()` (sounddevice backend)
- Modified `schedule_side()` signature to accept `last_play_times` parameter
- Added verbose logging block after scheduling each sound:
  ```python
  if self.verbose_logging:
      side_name = "Left" if channel==0 else "Right"
      delta_str = "N/A (first)"
      if last_play_times[i] is not None:
          delta = t_sec - last_play_times[i]
          delta_str = f"{delta*1000:.2f}ms"
      expected_interval = iv * 1000  # Convert to ms
      self._log_verbose(f"{side_name} Layer {i+1} (subdiv={subdiv}): played | Delta: {delta_str} | Expected: {expected_interval:.2f}ms")
      last_play_times[i] = t_sec
  ```

#### `_sa_loop()` (simpleaudio backend)
- Similar verbose logging blocks added for left and right layer scheduling
- Uses `t_ev` (event time) instead of sample counter for consistency

## App (GUI) Changes

### New Attributes

```python
self.var_verbose_log = tk.BooleanVar(value=False)  # Checkbox state
self.log_frame = ttk.LabelFrame(...)               # Log window container
self.log_text = tk.Text(...)                       # Log display widget
```

### New UI Components

#### Verbose Log Checkbox
- Located in top control row
- Bound to `_toggle_verbose_log()` command

#### Log Window (LabelFrame)
- Contains scrollable Text widget
- Vertical and horizontal scrollbars
- "Clear Log" button
- Initially hidden (shown when checkbox enabled)
- Grid layout:
  ```
  Row 0: Text widget (col 0) | Vertical scrollbar (col 1)
  Row 1: Horizontal scrollbar (col 0)
  Row 2: Clear Log button (col 0)
  ```

### New Methods

#### `_toggle_verbose_log()`
```python
def _toggle_verbose_log(self):
    enabled = self.var_verbose_log.get()
    self.engine.verbose_logging = enabled
    if enabled:
        self.log_frame.grid(row=4, column=0, sticky="nsew", pady=(8,0))
        self._append_log("=== Verbose logging enabled ===")
    else:
        self.log_frame.grid_remove()
        self._append_log("=== Verbose logging disabled ===")
```

**Design Notes:**
- Uses `grid()` / `grid_remove()` instead of destroying/recreating widget
- Preserves log content when toggling
- Updates `engine.verbose_logging` flag directly

#### `_append_log()`
```python
def _append_log(self, message):
    """Append message to the log window."""
    self.log_text.configure(state="normal")
    self.log_text.insert("end", message + "\n")
    self.log_text.see("end")  # Auto-scroll to bottom
    self.log_text.configure(state="disabled")
```

**Design Notes:**
- Text widget kept in "disabled" state except when updating
- Prevents user editing
- Auto-scrolls to show latest entries

#### `_clear_log()`
```python
def _clear_log(self):
    """Clear the log window."""
    self.log_text.configure(state="normal")
    self.log_text.delete("1.0", "end")
    self.log_text.configure(state="disabled")
```

### Initialization

In `App.__init__()`:
```python
# Connect log callback to engine
self.engine.log_callback = self._append_log
```

This establishes the communication channel from audio engine to UI.

## Thread Safety

### Critical Considerations

1. **Audio Thread → UI Thread Communication**
   - Never call Tkinter methods directly from audio callback
   - Use `self.ui_after()` to schedule UI updates on main thread
   - Lambda wrapping ensures callback is queued, not executed immediately

2. **Timing Accuracy**
   - Timestamp generated in audio thread for accuracy
   - Formatting done before crossing thread boundary

3. **Silent Failure**
   - Exceptions in logging code are caught and ignored
   - Prevents logging errors from disrupting audio playback

## Performance Considerations

1. **When Disabled**
   - Single boolean check: `if self.verbose_logging:`
   - Negligible overhead (~1-2 CPU cycles)

2. **When Enabled**
   - String formatting in audio thread
   - Callback queuing (deferred execution)
   - UI updates happen on main thread
   - Estimated overhead: <1% CPU for typical usage

3. **Memory**
   - Log entries accumulate in Text widget
   - User should clear log periodically during long sessions
   - No automatic log rotation

## Testing Recommendations

1. **Basic Functionality**
   - Enable/disable verbose logging
   - Verify log entries appear
   - Check timestamp accuracy

2. **Timing Accuracy**
   - Run at various BPMs (60, 120, 240)
   - Verify delta matches expected interval
   - Test with multiple layers

3. **Thread Safety**
   - Run extended sessions (30+ minutes)
   - Monitor for crashes or deadlocks
   - Test with many rapid layer changes

4. **Performance**
   - Profile CPU usage with verbose logging on/off
   - Test with maximum layers (many subdivisions)
   - Monitor memory usage over time

## Future Enhancements

Potential improvements:

1. **Log to File** - Option to save logs to disk
2. **Filtering** - Show only specific layers or sides
3. **Statistics** - Display average/min/max timing deviations
4. **Color Coding** - Highlight timing errors in red
5. **Log Rotation** - Automatic clearing after N entries
6. **Export** - Save log as CSV for analysis
