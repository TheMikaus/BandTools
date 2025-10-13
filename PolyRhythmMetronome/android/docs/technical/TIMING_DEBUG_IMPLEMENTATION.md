# Timing Debug Implementation - Technical Documentation

## Overview

This document describes the implementation of the timing diagnostics feature added in v1.7.0 to help diagnose timing issues in the Android PolyRhythmMetronome app.

## Motivation

Users reported that "timing is still off" after the v1.6.0 per-layer threading refactor. To diagnose the issue, we needed comprehensive logging that could capture:
- Actual vs expected beat timing
- Sleep accuracy on Android devices
- Audio processing latency
- Timing drift over time

## Architecture

### State Management

Added `timing_diagnostics` flag to `RhythmState`:

```python
class RhythmState:
    def __init__(self):
        # ... existing fields ...
        self.timing_diagnostics = False  # Enable verbose timing logging
```

This flag is:
- Persisted in save/load operations
- Thread-safe (accessed within `_lock`)
- Checked at layer thread start (cached for performance)

### UI Toggle Button

Added toggle button in `MetronomeWidget._build_controls()`:

```python
self.timing_diag_btn = ToggleButton(
    text="TIMING DEBUG: OFF",
    font_size='12sp',
    background_color=(0.5, 0.5, 0.5, 1),
    state='down' if self.state.timing_diagnostics else 'normal'
)
```

**Visual feedback**:
- OFF: Gray background
- ON: Orange background (#CC8033)

**Behavior**:
- Toggle persists to autosave
- Automatically restarts metronome if running to apply setting

### Layer Thread Logging

Modified `SimpleMetronomeEngine._run_layer()` to add comprehensive logging:

#### 1. Layer Start Logging

```python
if diagnostics_enabled:
    print(f"[timing] Layer {channel}/{layer_id}: Started with subdiv={subdiv}, interval={interval*1000:.2f}ms, BPM={bpm}")
```

#### 2. Per-Beat Timing (First 10 Beats)

```python
if diagnostics_enabled and beat_count < 10:
    # Before sleep
    print(f"[timing] Layer {channel}/{layer_id}: Beat {beat_count} sleeping for {wait_time*1000:.2f}ms (error: {timing_error*1000:+.2f}ms)")
    
    # Sleep accuracy
    sleep_actual = time.perf_counter() - sleep_start
    sleep_error = (sleep_actual - wait_time) * 1000
    print(f"[timing] Layer {channel}/{layer_id}: Sleep accuracy: requested={wait_time*1000:.2f}ms, actual={sleep_actual*1000:.2f}ms, error={sleep_error:+.2f}ms")
    
    # Audio processing times
    print(f"[timing] Layer {channel}/{layer_id}: Beat {beat_count} audio_get={audio_get_time:.2f}ms, play_sound={play_duration:.2f}ms")
```

**Why first 10 beats only?**
- Captures initial behavior (most critical for diagnosing issues)
- Avoids log spam (would be ~200 lines per second for subdiv 16 at 180 BPM)
- Reduces performance overhead

#### 3. Periodic Statistics (Every 50 Beats)

```python
if diagnostics_enabled and beat_count > 0 and beat_count % 50 == 0:
    if timing_errors:
        avg_error = sum(timing_errors) / len(timing_errors) * 1000
        min_error = min(timing_errors) * 1000
        max_error = max(timing_errors) * 1000
        print(f"[timing] Layer {channel}/{layer_id}: Stats after {beat_count} beats - avg_error={avg_error:+.2f}ms, min={min_error:+.2f}ms, max={max_error:+.2f}ms, max_drift={max_drift*1000:+.2f}ms")
```

**Tracks**:
- `timing_errors`: List of timing errors (actual - expected time)
- `max_drift`: Largest absolute timing error observed
- Statistics: average, min, max errors

#### 4. Layer Stop Logging

```python
if diagnostics_enabled:
    print(f"[timing] Layer {channel}/{layer_id}: STOPPED after {beat_count} beats - Final stats: avg_error={avg_error:+.2f}ms, min={min_error:+.2f}ms, max={max_error:+.2f}ms, max_drift={max_drift*1000:+.2f}ms")
```

### Engine Start/Stop Logging

Added detailed logging to `start()` and `stop()` methods:

#### Engine Start

```python
print(f"[engine] Starting metronome engine")
print(f"[engine]   BPM: {bpm}, Beats per measure: {beats_per_measure}")
print(f"[engine]   Audio library: {self.audio_lib}")
print(f"[engine]   Left layers: {len(left_layers)}, Right layers: {len(right_layers)}")
print(f"[engine]   Timing diagnostics: {'ENABLED' if diagnostics_enabled else 'DISABLED'}")
print(f"[engine]   Platform: {platform}")
print(f"[engine]   Python version: {sys.version.split()[0]}")
print(f"[engine]   High-precision timer available: {hasattr(time, 'perf_counter')}")
```

**Per-layer info**:
```python
print(f"[engine]   Starting left layer {i+1}: subdiv={subdiv}, mode={mode}, muted={muted}")
```

#### Engine Stop

```python
print(f"[engine] Stopping metronome with {len(self.threads)} threads...")
# ... thread cleanup ...
print(f"[engine] Stopped {stopped_count} threads, {timeout_count} timed out")
print(f"[engine] Metronome stopped")
```

## Timing Measurements

### Timing Error Calculation

```python
current_time = time.perf_counter() - start_time
timing_error = current_time - next_beat_time
```

**Interpretation**:
- `timing_error > 0`: Beat is late (current time past expected time)
- `timing_error < 0`: Beat is early (current time before expected time)
- `timing_error == 0`: Perfect timing (practically impossible)

### Sleep Accuracy Measurement

```python
sleep_start = time.perf_counter()
time.sleep(wait_time)
sleep_actual = time.perf_counter() - sleep_start
sleep_error = (sleep_actual - wait_time) * 1000
```

**Notes**:
- Android sleep resolution is typically 1-10ms
- Positive error indicates sleep took longer than requested
- Consistent positive errors can accumulate as drift

### Audio Processing Times

```python
audio_start = time.perf_counter()
audio_data = self._get_audio_data(layer, is_accent=is_accent)
audio_get_time = (time.perf_counter() - audio_start) * 1000

play_start = time.perf_counter()
self._play_sound(audio_data, volume, channel)
play_duration = (time.perf_counter() - play_start) * 1000
```

**Expected ranges**:
- `audio_get_time`: <5ms (cached audio)
- `play_duration`: 
  - AudioTrack: 1-10ms
  - simpleaudio: 1-5ms
  - Kivy: 10-50ms

## Performance Considerations

### Memory Overhead

- `timing_errors` list: ~8 bytes per beat × beats = ~8KB for 1000 beats
- Negligible compared to audio buffers (~100KB per layer)

### CPU Overhead

**When enabled**:
- First 10 beats: ~1-2ms per beat for string formatting and I/O
- Every 50th beat: ~0.5ms for statistics calculation
- Negligible impact on timing accuracy

**When disabled**:
- Single boolean check per beat: <0.001ms
- No performance impact

### Log Volume

**Example**: 120 BPM, subdiv 4, 2 layers, 60 seconds
- First 10 beats: ~30 lines per layer = 60 lines
- Periodic stats: 7 stats per layer = 14 lines
- Start/stop: ~20 lines
- **Total**: ~94 lines for 60 seconds

**With subdiv 16** (4x more beats):
- Same first 10 beats: 60 lines
- More periodic stats: 28 stats = 56 lines
- **Total**: ~136 lines for 60 seconds

## LogCapture Integration

The timing logs are captured by the existing `LogCapture` class:

```python
class LogCapture:
    def write(self, text):
        if text and text.strip():
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            line = f"[{timestamp}] {text}"
            self.buffer.write(line)
```

**Features**:
- Timestamps on all log lines
- Thread-safe buffering
- Available via VIEW LOGS button

## Diagnostic Workflow

### For Users

1. Enable timing diagnostics
2. Start metronome
3. Let run for 60+ seconds
4. Stop metronome
5. View logs
6. Share logs if needed

### For Developers

1. Analyze engine configuration (audio backend, platform)
2. Check layer start parameters (interval, subdiv)
3. Review first 10 beats for patterns:
   - Consistent timing errors → drift accumulation
   - High sleep errors → platform limitations
   - Long audio processing → backend issues
4. Review periodic statistics:
   - Increasing max_drift → timing instability
   - High average error → systematic bias
5. Check stop logs:
   - Thread timeout warnings → thread not exiting cleanly

## Known Limitations

### Beat Count Limit

Only first 10 beats per layer get detailed logging:
- **Reason**: Prevent log spam
- **Mitigation**: 10 beats is usually enough to diagnose issues
- **Future**: Could make configurable (e.g., first N beats)

### No Real-Time Display

Logs must be viewed via VIEW LOGS:
- **Reason**: UI performance (continuous display would be expensive)
- **Mitigation**: Logs persist in buffer throughout session
- **Future**: Could add live log tail view

### Single Session Only

Logs don't persist across app restarts:
- **Reason**: LogCapture uses in-memory buffer
- **Mitigation**: Use COPY button to save logs externally
- **Future**: Could add log file export

## Testing Recommendations

### Unit Testing (Not Currently Implemented)

```python
def test_timing_diagnostics_enabled():
    state = RhythmState()
    state.timing_diagnostics = True
    
    # Verify flag persists
    data = state.to_dict()
    assert data['timing_diagnostics'] == True
    
    # Verify load
    state2 = RhythmState()
    state2.from_dict(data)
    assert state2.timing_diagnostics == True
```

### Integration Testing

1. Toggle diagnostics ON/OFF
2. Verify button visual feedback
3. Start/stop metronome
4. Verify logs appear in VIEW LOGS
5. Verify metronome restarts on toggle during playback

### Performance Testing

1. Run with diagnostics OFF: baseline CPU/memory
2. Run with diagnostics ON: measure overhead
3. Verify overhead <5% CPU, <10MB memory

## Future Enhancements

### Configurable Verbosity Levels

```python
TIMING_DIAGNOSTICS_LEVEL = {
    0: "OFF",
    1: "MINIMAL",  # Start/stop only
    2: "STANDARD", # + periodic stats
    3: "VERBOSE",  # + first 10 beats
    4: "FULL"      # All beats (warning: log spam)
}
```

### Real-Time Timing Display

Add live timing indicator to UI:
```
[Layer 1] Drift: +0.5ms  Avg: +0.3ms
[Layer 2] Drift: -0.2ms  Avg: -0.1ms
```

### Log Export to File

```python
def export_logs_to_file(self):
    """Export logs to timestamped file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"metronome_logs_{timestamp}.txt"
    # ... save to external storage ...
```

### Historical Timing Graphs

Plot timing error over time for visualization:
- X-axis: Beat number
- Y-axis: Timing error (ms)
- Shows patterns and trends visually

## Related Documentation

- [Timing Diagnostics User Guide](../user_guides/TIMING_DIAGNOSTICS_GUIDE.md)
- [Per-Layer Threading Architecture](PER_LAYER_THREADING.md)
- [Audio Implementation](AUDIO_IMPLEMENTATION.md)

---

**Version**: v1.7.0  
**Implementation Date**: 2025-10-13  
**Lines Added**: ~150  
**Files Modified**: `main.py`
