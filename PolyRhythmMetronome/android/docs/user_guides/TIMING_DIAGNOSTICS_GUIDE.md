# Timing Diagnostics Guide

## Overview

The Timing Diagnostics feature provides detailed logging information to help diagnose timing issues with the PolyRhythmMetronome Android app. This feature is especially useful when you notice that beats are not playing at the expected times.

## When to Use

Use timing diagnostics when you experience:
- Beats that seem to drift over time
- Irregular timing between beats
- Beats that are consistently early or late
- Audio clicks or stuttering
- Issues with specific subdivisions

## Enabling Timing Diagnostics

1. Open the PolyRhythmMetronome app
2. Look for the **TIMING DEBUG** button at the bottom of the screen (next to VIEW LOGS)
3. Tap the button to toggle diagnostics ON
4. The button will turn orange and display "TIMING DEBUG: ON"
5. If the metronome is running, it will automatically restart to apply the setting

## What Gets Logged

When timing diagnostics are enabled, the app logs the following information:

### Engine Configuration (on start)
- BPM and beats per measure
- Audio library in use (AudioTrack, simpleaudio, or Kivy)
- Number of left and right layers
- Platform and Python version
- Timer precision information

### Per-Layer Timing (first 10 beats)
For each layer, the app logs:
- **Timing errors**: How early or late the beat is compared to expected time
- **Sleep accuracy**: Requested sleep time vs actual sleep duration
- **Audio processing time**: Time to retrieve and play audio data
- **Sound played**: Name/details of the sound that was played

Example log output:
```
[timing] Layer left/abc123: Beat 5 arrived 0.15ms early, sleeping for 500.15ms
[timing] Layer left/abc123: Sleep accuracy: requested=500.15ms, actual=500.38ms, error=+0.23ms
[timing] Layer left/abc123: Beat 5 played tone 880Hz, audio_get=2.34ms, play_sound=5.67ms
```

### Periodic Statistics (every 50 beats)
- Average timing drift (shown as "early" or "late")
- Minimum and maximum timing errors
- Maximum drift from expected timing

Example:
```
[timing] Layer left/abc123: Stats after 50 beats - avg_drift=0.45ms early, min=-0.12ms, max=+1.23ms, max_drift=+1.23ms
```

### Final Statistics (when stopped)
Complete timing summary for the entire session.

## Interpreting the Logs

### Timing Drift
The system measures how early or late each beat arrives at its scheduled time:
- **"early"**: The beat processing started before the target time (gives time to sleep before playing)
- **"late"**: The beat processing started after the target time (playing will be delayed)
- **Acceptable range**: Within 5ms early/late is generally imperceptible
- **Warning range**: 10ms early/late may be noticeable
- **Problem range**: >20ms early/late indicates timing issues

**Note**: Arriving consistently early is actually good - it means the system has time to sleep and wake up precisely at the target time. Arriving late means the system is falling behind schedule.

### Sleep Accuracy
- Shows how accurately the system can sleep for requested duration
- Android systems typically have ~1-5ms sleep resolution
- Positive error means sleep took longer than requested
- Consistent positive errors can accumulate over time

### Audio Processing Time
- **audio_get**: Time to retrieve audio data (should be <5ms)
- **play_sound**: Time to queue audio for playback (varies by backend)
  - AudioTrack: typically 1-10ms
  - simpleaudio: typically 1-5ms  
  - Kivy: typically 10-50ms

## Common Issues and Solutions

### High Timing Errors (>10ms)
**Problem**: Beats are consistently late or early

**Possible causes**:
- CPU overload (too many layers or high subdivision)
- Background app interference
- Audio buffer underruns

**Solutions**:
- Reduce number of active layers
- Close other apps
- Use lower subdivisions (4 instead of 16)
- Try different audio backend

### Accumulating Drift
**Problem**: Timing error increases over time

**Possible causes**:
- Sleep inaccuracy accumulation
- CPU throttling
- Thread scheduling delays

**Solutions**:
- Enable high-performance mode on device
- Reduce screen timeout to keep device active
- Restart the metronome periodically

### Long Audio Processing Times
**Problem**: audio_get or play_sound times are >50ms

**Possible causes**:
- Audio codec issues (MP3 tick mode)
- Audio buffer configuration
- Device audio driver issues

**Solutions**:
- Switch to tone or drum mode
- Reduce audio buffer size
- Update device audio drivers
- Test on different device

### Sleep Inaccuracy
**Problem**: Actual sleep consistently >5ms more than requested

**Possible causes**:
- Android timer resolution limitations
- Power saving modes
- CPU governor settings

**Solutions**:
- Enable developer options and change CPU governor
- Disable battery optimization for the app
- Use device in high-performance mode

## Viewing Logs

1. Tap the **VIEW LOGS** button to see all captured logs
2. Use the **Refresh** button to update the log display
3. Use the **Copy** button to copy logs to clipboard for sharing
4. Logs persist for the current app session only

## Performance Impact

**Note**: Timing diagnostics adds some overhead:
- First 10 beats per layer: ~1-2ms extra per beat for logging
- Every 50th beat: ~0.5ms for statistics calculation
- Generally negligible impact on timing accuracy

For most accurate timing, disable diagnostics during actual use. Enable only when troubleshooting.

## Sharing Logs for Support

If you need to report a timing issue:

1. Enable timing diagnostics
2. Start the metronome with the problematic configuration
3. Let it run for at least 60 seconds
4. Stop the metronome
5. Open VIEW LOGS
6. Tap COPY to copy logs to clipboard
7. Share the logs along with:
   - Device model
   - Android version
   - BPM and subdivision used
   - Description of the problem

## Disabling Timing Diagnostics

1. Tap the **TIMING DEBUG** button again
2. Button will turn gray and display "TIMING DEBUG: OFF"
3. If metronome is running, it will restart without diagnostics

## Technical Details

The timing system uses:
- `time.perf_counter()` for high-precision timing (microsecond resolution)
- Per-layer threading for independent timing
- Smart sleep algorithm for CPU efficiency
- Real-time timing error correction

For more technical information, see:
- [Per-Layer Threading Architecture](../technical/PER_LAYER_THREADING.md)
- [Audio Implementation](../technical/AUDIO_IMPLEMENTATION.md)

---

**Version**: Added in v1.7.0  
**Last Updated**: 2025-10-13
