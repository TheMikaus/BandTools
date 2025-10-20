# Manual Test Plan for Logging Fixes

## Overview
This document provides manual testing steps to verify the logging improvements made to address the issues reported in the problem statement.

## Issues Addressed

1. **Empty mp3_tick in logs**: Previously showed `played mp3_tick ''`, now shows `played mp3_tick 'none'`
2. **Confusing timing messages**: Previously showed `error: -5ms` (negative seems bad), now shows `arrived 5ms early` (clearly good)
3. **Non-intuitive statistics**: Previously showed `avg_error=-0.5ms`, now shows `avg_drift=0.5ms early`
4. **High sleep errors**: Now displays warning `⚠️ HIGH` for sleep errors >50ms

## Prerequisites

- Android device with PolyRhythmMetronome installed
- Timing diagnostics enabled (TIMING DEBUG button ON)
- Ability to view logs (VIEW LOGS button)

## Test Cases

### Test 1: Empty mp3_tick Display

**Steps**:
1. Create a new layer in tone or drum mode (not mp3_tick mode)
2. Enable timing diagnostics (TIMING DEBUG: ON)
3. Start the metronome
4. View logs (VIEW LOGS button)

**Expected Result**:
- For non-mp3_tick layers, logs should show tone or drum information
- No empty mp3_tick strings should appear

**Verification**:
- ✓ No messages like `mp3_tick ''` appear in logs
- ✓ Only relevant sound types are logged

### Test 2: MP3 Tick with No File Selected

**Steps**:
1. Switch a layer to mp3_tick mode without selecting a file
2. Enable timing diagnostics
3. Start the metronome
4. View logs

**Expected Result**:
- Layer start log shows: `mp3_tick 'none'` (not empty string)
- Beat logs show: `played mp3_tick 'none'` (not empty string)

**Verification**:
- ✓ Messages show `mp3_tick 'none'` instead of `mp3_tick ''`

### Test 3: MP3 Tick with File Selected

**Steps**:
1. Select an mp3_tick file (e.g., "click" or any available tick sound)
2. Enable timing diagnostics
3. Start the metronome
4. View logs

**Expected Result**:
- Layer start log shows: `mp3_tick 'click'` (or whatever file name)
- Beat logs show: `played mp3_tick 'click'` (or `played mp3_tick 'click' (accent)`)

**Verification**:
- ✓ Correct file name appears in logs
- ✓ Accent variations are noted when appropriate

### Test 4: Timing Drift Display - Early Arrival

**Setup**: Use low BPM (60) and low subdivision (4) to minimize timing stress

**Steps**:
1. Enable timing diagnostics
2. Start the metronome
3. View logs for first 10 beats

**Expected Result**:
- Messages show: `Beat N arrived X.XXms early, sleeping for X.XXms`
- The "early" and sleep time should be approximately equal (expected behavior)
- **NOT** showing negative numbers like `error: -X.XXms`

**Verification**:
- ✓ Messages clearly say "early" or "late"
- ✓ No confusing negative numbers
- ✓ Arrival time ≈ sleep time (this is normal)

### Test 5: Timing Drift Display - Late Arrival

**Setup**: Use high BPM (180) and high subdivision (16) to stress the system

**Steps**:
1. Enable timing diagnostics
2. Start the metronome
3. Let it run for at least 50 beats
4. View logs

**Expected Result**:
- Some beats may show: `Beat N arrived X.XXms late, sleeping for X.XXms` (or no sleep if too late)
- Or warning: `Beat N LATE by X.XXms! Skipping sleep.`

**Verification**:
- ✓ Late arrivals clearly marked as "late"
- ✓ Severe lateness triggers skip sleep message

### Test 6: Average Drift Statistics

**Steps**:
1. Enable timing diagnostics
2. Start the metronome
3. Let it run for at least 50 beats
4. View logs for statistics message

**Expected Result**:
- Message shows: `Stats after 50 beats - avg_drift=X.XXms early` (or "late")
- **NOT**: `avg_error=-X.XXms` or `avg_error=+X.XXms`

**Verification**:
- ✓ Statistics show "early" or "late" descriptor
- ✓ Value is always positive (absolute value)
- ✓ Clear whether the system is running ahead or behind

### Test 7: High Sleep Error Warning

**Setup**: Try to create system stress (background apps, battery saver, etc.)

**Steps**:
1. Enable timing diagnostics
2. Enable battery saver mode or start other apps
3. Start the metronome
4. View logs for sleep accuracy

**Expected Result**:
- If sleep error is >50ms: `Sleep accuracy: requested=XXms, actual=XXms, error=+XXms ⚠️ HIGH`
- If sleep error is ≤50ms: Normal message without warning

**Verification**:
- ✓ Warning appears only when sleep error exceeds 50ms
- ✓ Warning emoji is visible: ⚠️

### Test 8: Final Stop Statistics

**Steps**:
1. Enable timing diagnostics
2. Start the metronome
3. Let it run for a while (100+ beats)
4. Stop the metronome
5. View logs for final statistics

**Expected Result**:
- Message shows: `STOPPED after N beats - Final stats: avg_drift=X.XXms early/late, min=..., max=..., max_drift=...`
- Clear indication of overall timing performance

**Verification**:
- ✓ Final statistics use "early" or "late" descriptor
- ✓ Values are interpretable and clear

## Common Log Patterns

### Good Timing
```
[timing] Layer left/abc123: Beat 5 arrived 1.23ms early, sleeping for 501.23ms
[timing] Layer left/abc123: Sleep accuracy: requested=501.23ms, actual=501.45ms, error=+0.22ms
[timing] Layer left/abc123: Beat 5 played tone 880Hz, audio_get=2.34ms, play_sound=5.67ms
```

### Problematic Timing
```
[timing] Layer left/abc123: Beat 5 arrived 15.67ms late, sleeping for 484.33ms
[timing] Layer left/abc123: Sleep accuracy: requested=484.33ms, actual=550.12ms, error=+65.79ms ⚠️ HIGH
[timing] Layer left/abc123: Beat 5 played tone 880Hz, audio_get=2.34ms, play_sound=5.67ms
```

### Severe Issues
```
[timing] Layer left/abc123: Beat 5 arrived 523.45ms late, sleeping for 0.00ms
[timing] Layer left/abc123: Beat 5 LATE by 23.45ms! Skipping sleep.
```

## Regression Testing

Verify that existing functionality still works:
1. ✓ Metronome plays sounds correctly
2. ✓ Multiple layers work independently
3. ✓ BPM and subdivision changes are respected
4. ✓ Save/load functionality works
5. ✓ Visual flashing still works
6. ✓ Timing diagnostics can be toggled on/off

## Success Criteria

All test cases pass AND:
- No confusing negative numbers in timing logs
- mp3_tick always shows a value (not empty string)
- "early" vs "late" is always clear
- High sleep errors are clearly marked
- Documentation matches actual behavior

## Notes for Testers

- The "arrived early" time matching "sleeping for" time is **expected and normal**
- Negative timing errors are now shown as positive "early" values (less confusing)
- Large sleep errors (>1 second) indicate serious system problems, not code bugs
- The ⚠️ HIGH warning helps identify these system-level issues

---

**Date**: 2025-10-14  
**Version**: Fixes for issue "Wave/mp3 doesn't play log shows empty file"
