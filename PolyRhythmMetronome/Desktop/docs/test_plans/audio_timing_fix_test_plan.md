# Test Plan: Audio Pre-loading and Timing Fix

## Overview

This test plan verifies that wave and MP3 files play on time from a freshly opened application after implementing audio pre-loading.

## Test Environment

- **Application**: PolyRhythmMetronome Desktop
- **OS**: Windows/Linux/MacOS
- **Audio Files**: WAV and MP3 files in `ticks` folder
- **Test Duration**: ~15 minutes

## Pre-Test Setup

1. Close the PolyRhythmMetronome application completely
2. Verify `ticks` folder contains audio files:
   - WAV files: `click.wav`, `cowbell_1.wav`, `cowbell_2.wav`, etc.
   - Ensure at least 2-3 different audio files are available
3. Clear any autosave state (optional)

## Test Cases

### Test 1: Fresh Start with WAV File

**Objective**: Verify WAV files play on time from first beat after fresh app start

**Steps**:
1. Open the application (fresh start)
2. Add a layer to Left ear:
   - Mode: "WAV file"
   - Select `ticks/click.wav`
   - Subdivision: 4
3. Set BPM to 120
4. Click Play immediately
5. Listen to the first 4-5 beats

**Expected Result**:
- Audio plays immediately on the first beat
- Timing is consistent from the start
- No delayed or skipped first beat
- Steady rhythm throughout

**Pass/Fail**: ___________

**Notes**: _______________________________

---

### Test 2: Fresh Start with MP3 Tick

**Objective**: Verify MP3 tick sounds play on time with accent/regular variations

**Steps**:
1. Close and reopen the application
2. Add a layer to Right ear:
   - Mode: "MP3 Tick"
   - Select "cowbell" (or any paired tick)
   - Subdivision: 4
3. Set Beats per Measure to 4
4. Set Accent Factor to 2.0
5. Click Play
6. Listen for 2 complete measures (8 beats)

**Expected Result**:
- First beat plays on time (no delay)
- Accent beat (beat 1) sounds different/louder
- Regular beats sound consistent
- No timing variations between accent and regular

**Pass/Fail**: ___________

**Notes**: _______________________________

---

### Test 3: Multiple Layers with Different Files

**Objective**: Verify multiple audio files pre-load correctly

**Steps**:
1. Close and reopen the application
2. Add layers:
   - Left: `cowbell_1.wav` at subdivision 4
   - Left: `woodblock_1.wav` at subdivision 8
   - Right: `hiclick_1.wav` at subdivision 4
3. Click Play
4. Listen for timing accuracy

**Expected Result**:
- All layers start on time
- No delays or stuttering
- Clean polyrhythm from the start
- No gradual "warm-up" period

**Pass/Fail**: ___________

**Notes**: _______________________________

---

### Test 4: Rapid Play/Stop/Play

**Objective**: Verify cache persists across stop/start cycles

**Steps**:
1. With layers already configured (from Test 3)
2. Click Play
3. After 2 beats, click Stop
4. Immediately click Play again
5. Repeat stop/play 2-3 times

**Expected Result**:
- Each play starts immediately on time
- No delays even on rapid restarts
- Cache remains valid

**Pass/Fail**: ___________

**Notes**: _______________________________

---

### Test 5: Add Layer During Stopped State

**Objective**: Verify new layers pre-load when play is clicked

**Steps**:
1. Start with 1 layer configured
2. Click Play, then Stop after a few beats
3. Add a new layer with a different audio file
4. Click Play

**Expected Result**:
- New audio file plays on time from first beat
- Pre-loading happens for the new file
- No delay on playback start

**Pass/Fail**: ___________

**Notes**: _______________________________

---

### Test 6: Missing Audio File Handling

**Objective**: Verify graceful handling of missing files

**Steps**:
1. Add a layer with a custom WAV file path
2. Enter a path to a non-existent file: `/nonexistent/audio.wav`
3. Add another layer with a valid file
4. Click Play

**Expected Result**:
- Warning message may appear (optional)
- Valid layer still plays correctly
- Application doesn't crash
- Timing is correct for valid layers

**Pass/Fail**: ___________

**Notes**: _______________________________

---

### Test 7: Large Audio File

**Objective**: Verify pre-loading works with larger files

**Steps**:
1. Add a custom WAV/MP3 file (1-2 seconds long)
2. Use it in a layer
3. Click Play from fresh start

**Expected Result**:
- Slight delay before playback starts (acceptable)
- Once started, plays on time
- No stuttering during playback

**Pass/Fail**: ___________

**Notes**: _______________________________

---

### Test 8: Verify Cache Status (Developer Test)

**Objective**: Confirm files are in cache before audio thread starts

**Steps**:
1. Add debug logging to `_preload_audio_files()`
2. Configure layers with audio files
3. Click Play
4. Check console/log output

**Expected Result**:
- Log shows files being loaded
- Pre-loading happens before "stream started"
- Cache hit messages during playback

**Pass/Fail**: ___________

**Notes**: _______________________________

---

## Performance Tests

### Test P1: Memory Usage

**Steps**:
1. Open application
2. Note memory usage (Task Manager/Activity Monitor)
3. Add 5 layers with different audio files
4. Click Play
5. Note memory usage after pre-load

**Expected Result**:
- Memory increase is reasonable (<50MB for typical files)
- No memory leaks during playback

**Measurement**: Before: ______ MB, After: ______ MB

---

### Test P2: Startup Time

**Steps**:
1. Configure 3-4 layers with audio files
2. Time from click Play to first sound
3. Repeat 3 times, average the results

**Expected Result**:
- Startup time < 500ms for typical files
- Consistent across multiple plays

**Measurements**: 
- Try 1: ______ ms
- Try 2: ______ ms
- Try 3: ______ ms
- Average: ______ ms

---

## Regression Tests

### Test R1: Tone Mode Still Works

**Objective**: Verify tone generation isn't affected

**Steps**:
1. Add layer with Mode: Tone, Frequency: 440Hz
2. Click Play

**Expected Result**:
- Tone plays immediately
- No timing issues

**Pass/Fail**: ___________

---

### Test R2: Drum Mode Still Works

**Objective**: Verify drum synthesis isn't affected

**Steps**:
1. Add layer with Mode: Drum, Type: Snare
2. Click Play

**Expected Result**:
- Drum sound plays immediately
- No timing issues

**Pass/Fail**: ___________

---

## Acceptance Criteria

The fix is considered successful if:

- [ ] All Test Cases (1-8) pass
- [ ] Performance is acceptable (P1, P2)
- [ ] No regressions in existing features (R1, R2)
- [ ] User reports no timing issues from fresh start
- [ ] Documentation is complete

## Issues Found

| Test # | Description | Severity | Status |
|--------|-------------|----------|--------|
|        |             |          |        |

## Test Summary

- **Total Tests**: 13
- **Passed**: _____
- **Failed**: _____
- **Skipped**: _____

**Overall Result**: PASS / FAIL

**Tester**: ___________________

**Date**: ___________________

**Notes**: 
_____________________________________________
_____________________________________________
_____________________________________________
