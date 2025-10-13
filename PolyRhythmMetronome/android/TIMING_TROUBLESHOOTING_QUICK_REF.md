# Timing Troubleshooting - Quick Reference

## Quick Start

**Having timing issues?** Follow these steps:

### 1. Enable Timing Diagnostics
1. Open PolyRhythmMetronome
2. Tap **TIMING DEBUG** button (bottom of screen)
3. Button turns orange and shows "ON"

### 2. Reproduce the Issue
1. Configure your metronome (BPM, subdivisions, layers)
2. Tap PLAY
3. Let it run for at least 60 seconds
4. Tap STOP

### 3. View the Logs
1. Tap **VIEW LOGS** button
2. Scroll through the timing information
3. Look for warnings or high error values

### 4. Share the Results
1. Tap **COPY** in the log viewer
2. Paste logs into issue report
3. Include:
   - Device model
   - Android version
   - BPM and subdivision settings
   - Description of the problem

---

## What to Look For in Logs

### Engine Configuration (Top of Log)
```
[engine] Starting metronome engine
[engine]   BPM: 120, Beats per measure: 4
[engine]   Audio library: android          ← Check which audio backend is used
[engine]   Timing diagnostics: ENABLED
[engine]   Platform: android
```

**Key info**: Audio library (should be "android" for best performance)

---

### Timing Errors (Per Beat)
```
[timing] Layer left/abc123: Beat 1 sleeping for 500.00ms (error: +0.15ms)
                                                              ^^^^^^^^^^^
                                                              This is the timing error
```

**Good**: ±0.5ms average error  
**Warning**: ±2-5ms average error  
**Problem**: >±5ms average error  

---

### Sleep Accuracy
```
[timing] Layer left/abc123: Sleep accuracy: requested=500.00ms, actual=500.23ms, error=+0.23ms
                                                                                      ^^^^^^^^^^
                                                                                      Sleep error
```

**Good**: <5ms sleep error  
**Warning**: 5-10ms sleep error  
**Problem**: >10ms sleep error (Android system limitation)

---

### Audio Processing Times
```
[timing] Layer left/abc123: Beat 1 audio_get=2.34ms, play_sound=5.67ms
                                            ^^^^^^^^             ^^^^^^^^
                                        Get audio time    Play audio time
```

**Good**: audio_get <5ms, play_sound <20ms  
**Warning**: audio_get 5-10ms, play_sound 20-50ms  
**Problem**: audio_get >10ms, play_sound >50ms  

---

### Statistics (Every 50 Beats)
```
[timing] Layer left/abc123: Stats after 50 beats - avg_error=+0.45ms, min=-0.12ms, max=+1.23ms, max_drift=+1.23ms
                                                               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                                               Overall timing statistics
```

**Key metrics**:
- **avg_error**: Should be close to 0ms (positive = late, negative = early)
- **min/max**: Range of errors (narrower is better)
- **max_drift**: Largest error seen (should be <5ms)

---

## Common Issues & Quick Fixes

### Issue: High Average Error (>±2ms)

**Symptoms**: Beats consistently early or late

**Possible causes**:
- CPU overload
- Background app interference
- Wrong audio backend

**Quick fixes**:
1. Close other apps
2. Reduce number of layers
3. Lower subdivision (use 4 instead of 16)
4. Check audio library (should be "android")

---

### Issue: Large Sleep Errors (>10ms)

**Symptoms**: "Sleep accuracy: error=+15ms" or higher

**Possible causes**:
- Android power saving mode
- CPU throttling
- System timer resolution

**Quick fixes**:
1. Enable high-performance mode
2. Disable battery optimization for app
3. Keep screen on during use
4. Update device firmware

---

### Issue: Long Audio Processing (>50ms)

**Symptoms**: "play_sound=85ms" or higher

**Possible causes**:
- MP3 tick mode issues
- Audio buffer problems
- Device audio driver

**Quick fixes**:
1. Switch to tone or drum mode
2. Test with different sound modes
3. Restart app
4. Test on different device

---

### Issue: Increasing Drift Over Time

**Symptoms**: max_drift grows from 1ms to 10ms+ over 60 seconds

**Possible causes**:
- Sleep accuracy accumulation
- Thread scheduling issues
- CPU throttling

**Quick fixes**:
1. Restart metronome periodically
2. Enable high-performance mode
3. Close background apps
4. Reduce number of layers

---

## Performance Benchmarks

### Expected Timing Accuracy

| BPM | Subdivision | Expected Error |
|-----|-------------|----------------|
| 60  | 4           | ±1ms          |
| 120 | 4           | ±1ms          |
| 180 | 4           | ±2ms          |
| 120 | 16          | ±2ms          |
| 180 | 16          | ±3ms          |

### Audio Processing Times

| Backend    | Typical Time | Max Acceptable |
|------------|-------------|----------------|
| AudioTrack | 1-10ms      | 20ms           |
| simpleaudio| 1-5ms       | 10ms           |
| Kivy       | 10-50ms     | 75ms           |

---

## When to Disable Diagnostics

**Disable when**:
- Done troubleshooting
- Recording actual performance
- Concerned about battery life
- Testing final timing accuracy

**Note**: Diagnostics add ~1-2ms overhead on first 10 beats only, negligible impact on overall timing.

---

## Need More Help?

### Full Documentation
- [Timing Diagnostics Guide](docs/user_guides/TIMING_DIAGNOSTICS_GUIDE.md) - Complete user guide
- [Technical Implementation](docs/technical/TIMING_DEBUG_IMPLEMENTATION.md) - For developers

### Reporting Issues
Include in your report:
1. Full logs (from VIEW LOGS → COPY)
2. Device: Model and Android version
3. Settings: BPM, subdivision, number of layers
4. Audio backend: From logs (look for "Audio library: ___")
5. Description: What's wrong and when it happens

### Developer Contact
File an issue on GitHub with logs attached.

---

**Quick Tip**: Most timing issues are solved by:
1. Using "android" audio backend (automatic on Android)
2. Closing background apps
3. Enabling high-performance mode
4. Using reasonable settings (BPM 60-180, subdiv ≤8)

---

**Version**: v1.7.0  
**Last Updated**: 2025-10-13
