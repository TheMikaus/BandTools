# Timing Diagnostics Test Plan - v1.7.0

## Overview

This test plan validates the timing diagnostics feature added in v1.7.0 to help diagnose timing issues.

## Test Environment

### Required
- Android device or emulator
- PolyRhythmMetronome Android v1.7.0 or later
- Ability to view logs (adb logcat or VIEW LOGS button)

### Recommended
- 2+ different Android devices (to test platform variations)
- High-resolution timer device for validation

## Test Suites

### Suite 1: UI Toggle Button

**Purpose**: Verify toggle button behavior and visual feedback

#### Test 1.1: Toggle Button Initial State
**Steps**:
1. Launch app
2. Locate TIMING DEBUG button
3. Observe initial state

**Expected**:
- Button displays "TIMING DEBUG: OFF"
- Button has gray background
- Button is in normal (not pressed) state

**Pass/Fail**: ___

---

#### Test 1.2: Toggle Button Enable
**Steps**:
1. Tap TIMING DEBUG button once
2. Observe button state

**Expected**:
- Button changes to "TIMING DEBUG: ON"
- Button background turns orange
- Button is in down (pressed) state
- Log message appears: "[timing] Timing diagnostics ENABLED"
- Info message lists what will be logged

**Pass/Fail**: ___

---

#### Test 1.3: Toggle Button Disable
**Steps**:
1. With diagnostics enabled, tap button again
2. Observe button state

**Expected**:
- Button changes to "TIMING DEBUG: OFF"
- Button background turns gray
- Button is in normal (not pressed) state
- Log message: "[timing] Timing diagnostics DISABLED"

**Pass/Fail**: ___

---

#### Test 1.4: Toggle Persists After Save
**Steps**:
1. Enable timing diagnostics
2. Tap SAVE button
3. Save to file "test_diag.json"
4. Disable timing diagnostics
5. Tap LOAD button
6. Load "test_diag.json"

**Expected**:
- After load, button shows "TIMING DEBUG: ON"
- Button is in down state

**Pass/Fail**: ___

---

### Suite 2: Engine Start/Stop Logging

**Purpose**: Verify comprehensive engine configuration logging

#### Test 2.1: Engine Start Logging (Diagnostics OFF)
**Steps**:
1. Ensure diagnostics OFF
2. Tap PLAY
3. View logs

**Expected logs**:
```
[engine] Starting metronome engine
[engine]   BPM: 120, Beats per measure: 4
[engine]   Audio library: android
[engine]   Left layers: 1, Right layers: 1
[engine]   Timing diagnostics: DISABLED
[engine]   Platform: android
[engine]   Python version: 3.x.x
[engine]   High-precision timer available: True
[engine]   Starting left layer 1: subdiv=4, mode=tone, muted=False
[engine]   Starting right layer 1: subdiv=4, mode=tone, muted=False
[engine] Metronome started with 2 layer threads
```

**Pass/Fail**: ___

---

#### Test 2.2: Engine Start Logging (Diagnostics ON)
**Steps**:
1. Enable timing diagnostics
2. Tap PLAY
3. View logs

**Expected**:
- Same logs as Test 2.1 but with "ENABLED" for timing diagnostics
- Additional layer start logs (detailed)

**Pass/Fail**: ___

---

#### Test 2.3: Engine Stop Logging
**Steps**:
1. Start metronome
2. Let run for 5 seconds
3. Tap STOP
4. View logs

**Expected logs**:
```
[engine] Stopping metronome with 2 threads...
[engine] Stopped 2 threads, 0 timed out
[engine] Metronome stopped
```

**Pass/Fail**: ___

---

### Suite 3: Layer Timing Logging

**Purpose**: Verify per-layer timing diagnostics

#### Test 3.1: Layer Start Logging
**Steps**:
1. Enable timing diagnostics
2. Set BPM to 120, subdiv to 4
3. Tap PLAY
4. View logs immediately

**Expected**:
- Log line: "[timing] Layer left/[uid]: Started with subdiv=4, interval=500.00ms, BPM=120"
- Similar for right layer

**Pass/Fail**: ___

---

#### Test 3.2: First 10 Beats Detail Logging
**Steps**:
1. Enable timing diagnostics
2. Start metronome
3. Let run for 10 beats (~5 seconds at 120 BPM, subdiv 4)
4. View logs

**Expected for each of first 10 beats**:
```
[timing] Layer left/[uid]: Beat N sleeping for XXX.XXms (error: +/-X.XXms)
[timing] Layer left/[uid]: Sleep accuracy: requested=XXX.XXms, actual=XXX.XXms, error=+/-X.XXms
[timing] Layer left/[uid]: Beat N audio_get=X.XXms, play_sound=X.XXms
```

**Validation**:
- Timing errors should be <5ms typically
- Sleep errors should be <10ms typically
- Audio processing <50ms typically

**Pass/Fail**: ___

---

#### Test 3.3: No Detailed Logs After Beat 10
**Steps**:
1. Enable timing diagnostics
2. Start metronome
3. Let run for 20 beats (~10 seconds)
4. View logs

**Expected**:
- Detailed logs for beats 0-9 only
- No detailed logs for beats 10-19
- Periodic stats at beat 50 (if running that long)

**Pass/Fail**: ___

---

#### Test 3.4: Periodic Statistics (Every 50 Beats)
**Steps**:
1. Enable timing diagnostics
2. Start metronome at 120 BPM, subdiv 4
3. Let run for 60 seconds (120 beats)
4. View logs

**Expected**:
- Stats log at beat 50:
  ```
  [timing] Layer left/[uid]: Stats after 50 beats - avg_error=+/-X.XXms, min=+/-X.XXms, max=+/-X.XXms, max_drift=+/-X.XXms
  ```
- Stats log at beat 100
- Similar for right layer

**Pass/Fail**: ___

---

#### Test 3.5: Final Statistics on Stop
**Steps**:
1. Enable timing diagnostics
2. Start metronome
3. Let run for 30 seconds
4. Stop metronome
5. View logs

**Expected**:
```
[timing] Layer left/[uid]: STOPPED after N beats - Final stats: avg_error=+/-X.XXms, min=+/-X.XXms, max=+/-X.XXms, max_drift=+/-X.XXms
```

**Pass/Fail**: ___

---

### Suite 4: Auto-Restart on Toggle

**Purpose**: Verify metronome restarts when diagnostics toggled during playback

#### Test 4.1: Enable During Playback
**Steps**:
1. Start metronome (diagnostics OFF)
2. Let run for 5 seconds
3. Enable timing diagnostics
4. Observe behavior

**Expected**:
- Log message: "[timing] Restarting metronome to apply timing diagnostics setting..."
- Metronome stops briefly
- Metronome starts with diagnostics enabled
- No need to manually stop/start

**Pass/Fail**: ___

---

#### Test 4.2: Disable During Playback
**Steps**:
1. Start metronome (diagnostics ON)
2. Let run for 5 seconds
3. Disable timing diagnostics
4. Observe behavior

**Expected**:
- Same auto-restart behavior
- Metronome restarts with diagnostics disabled

**Pass/Fail**: ___

---

### Suite 5: Performance Impact

**Purpose**: Verify diagnostics don't significantly impact timing accuracy

#### Test 5.1: CPU Usage Comparison
**Steps**:
1. Start metronome (diagnostics OFF)
2. Monitor CPU usage for 60 seconds
3. Record average CPU usage: ____%
4. Stop metronome
5. Enable diagnostics
6. Start metronome (diagnostics ON)
7. Monitor CPU usage for 60 seconds
8. Record average CPU usage: ____%

**Expected**:
- CPU increase <5%
- Timing remains stable

**Pass/Fail**: ___

---

#### Test 5.2: Timing Accuracy Not Degraded
**Steps**:
1. Run metronome for 60s with diagnostics OFF
2. Note any timing issues
3. Run metronome for 60s with diagnostics ON
4. Note any timing issues
5. Compare

**Expected**:
- No noticeable degradation in timing
- Both runs have similar timing quality

**Pass/Fail**: ___

---

### Suite 6: Log Viewing

**Purpose**: Verify logs are accessible via VIEW LOGS button

#### Test 6.1: View Logs After Session
**Steps**:
1. Enable timing diagnostics
2. Start metronome
3. Let run for 30 seconds
4. Stop metronome
5. Tap VIEW LOGS
6. Scroll through logs

**Expected**:
- All diagnostic logs visible
- Logs have timestamps
- Logs are readable
- Refresh button works
- Copy button works

**Pass/Fail**: ___

---

#### Test 6.2: Copy Logs to Clipboard
**Steps**:
1. Run test session with diagnostics
2. Tap VIEW LOGS
3. Tap COPY
4. Paste into text editor

**Expected**:
- Full log content copied
- Formatting preserved
- Can be saved to file

**Pass/Fail**: ___

---

### Suite 7: Edge Cases

**Purpose**: Test unusual configurations and scenarios

#### Test 7.1: Multiple Layers
**Steps**:
1. Add 4 left layers and 4 right layers
2. Enable diagnostics
3. Start metronome
4. View logs

**Expected**:
- Engine logs show 8 total threads
- Each layer gets its own timing logs
- Logs distinguish between layers by UID

**Pass/Fail**: ___

---

#### Test 7.2: Fast Tempo with High Subdivision
**Steps**:
1. Set BPM to 180, subdiv to 16
2. Enable diagnostics
3. Start metronome
4. Let run for 10 seconds
5. View logs

**Expected**:
- Logs show interval ~52ms (180 BPM * 16 subdiv)
- Timing still tracked accurately
- No excessive lag from logging
- First 10 beats logged as normal

**Pass/Fail**: ___

---

#### Test 7.3: Muted Layers
**Steps**:
1. Add 2 layers, mute one
2. Enable diagnostics
3. Start metronome
4. View logs

**Expected**:
- Both layers show timing logs
- Muted layer still tracks timing (just doesn't play audio)
- No errors for muted layer

**Pass/Fail**: ___

---

#### Test 7.4: Log Volume Test
**Steps**:
1. Enable diagnostics
2. Run for 5 minutes with subdiv 16 at 180 BPM
3. Check log size

**Expected**:
- Logs don't grow excessively
- Only first 10 beats get detailed logs
- Periodic stats every 50 beats
- App remains responsive

**Pass/Fail**: ___

---

## Test Summary

**Total Tests**: 24

**Tests Passed**: ___  
**Tests Failed**: ___  
**Tests Skipped**: ___

**Overall Status**: ___

## Issues Found

| Test ID | Issue Description | Severity | Status |
|---------|------------------|----------|--------|
|         |                  |          |        |

## Recommendations

Based on test results:

1. **Performance**:
   - [ ] Acceptable CPU overhead
   - [ ] No timing degradation
   - [ ] Log volume manageable

2. **Usability**:
   - [ ] Toggle button intuitive
   - [ ] Logs easy to read
   - [ ] Info helps diagnose issues

3. **Completeness**:
   - [ ] All necessary info logged
   - [ ] Missing info: _______________

## Notes

- Test date: ___________
- Tester: ___________
- Device: ___________
- Android version: ___________
- App version: v1.7.0

---

**Document Version**: 1.0  
**Created**: 2025-10-13  
**For**: PolyRhythmMetronome Android v1.7.0
