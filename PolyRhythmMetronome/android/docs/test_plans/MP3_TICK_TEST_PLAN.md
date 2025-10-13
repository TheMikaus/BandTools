# MP3 Tick Sounds - Test Plan

## Overview

This test plan covers the MP3 tick sound feature implementation, which uses Android's native MediaCodec API for MP3 decoding without requiring ffmpeg.

## Test Environment

### Minimum Requirements
- Android device with API level 21+ (Android 5.0 Lollipop)
- PolyRhythmMetronome Android app installed
- Test MP3 files in `ticks/` folder

### Recommended Test Devices
- **Low-end**: Android 5.0 device with limited RAM
- **Mid-range**: Android 7.0-9.0 device
- **High-end**: Android 10+ device
- **Target device**: Kindle Fire HD 10 (Fire OS / Android 9)

## Test Files Preparation

Create the following test files in `ticks/` folder:

### Test Set 1: Basic Files
```
ticks/
  ├── click.mp3           (50ms, 44.1kHz, mono)
  ├── woodblock.mp3       (100ms, 44.1kHz, mono)
  └── cowbell.mp3         (200ms, 44.1kHz, mono)
```

### Test Set 2: Paired Files
```
ticks/
  ├── paired_1.mp3        (100ms, 44.1kHz, mono, high pitch)
  ├── paired_2.mp3        (100ms, 44.1kHz, mono, low pitch)
  ├── woodblock_1.mp3     (100ms, 44.1kHz, mono)
  └── woodblock_2.mp3     (100ms, 44.1kHz, mono)
```

### Test Set 3: Edge Cases
```
ticks/
  ├── stereo.mp3          (100ms, 44.1kHz, stereo)
  ├── high_rate.mp3       (100ms, 48kHz, mono)
  ├── low_rate.mp3        (100ms, 22.05kHz, mono)
  ├── long_sound.mp3      (1000ms, 44.1kHz, mono)
  ├── tiny.mp3            (10ms, 44.1kHz, mono)
  └── large_file.mp3      (5000ms, 44.1kHz, mono)
```

### Test Set 4: Invalid/Corrupted
```
ticks/
  ├── corrupted.mp3       (intentionally corrupted file)
  ├── not_audio.mp3       (renamed image file)
  └── empty.mp3           (0 byte file)
```

## Test Cases

### TC-01: App Startup with MP3 Files
**Priority**: Critical  
**Precondition**: Test Set 1 files in `ticks/` folder

**Steps:**
1. Launch the app
2. Observe startup time
3. Check logs for MP3 loading messages

**Expected Results:**
- App starts successfully
- No crashes or errors
- Logs show: `[audio] Loaded MP3 tick: click`, etc.
- Startup time < 5 seconds

**Pass/Fail**: _____

---

### TC-02: Single MP3 File in Dropdown
**Priority**: Critical  
**Precondition**: TC-01 passed

**Steps:**
1. Add a new layer (tap + button)
2. Change mode to "mp3_tick"
3. Check the second dropdown (tick selector)

**Expected Results:**
- Second dropdown appears
- Contains entries: "click", "cowbell", "woodblock"
- Entries are sorted alphabetically

**Pass/Fail**: _____

---

### TC-03: Play Single MP3 Tick
**Priority**: Critical  
**Precondition**: TC-02 passed

**Steps:**
1. Add layer with mp3_tick mode
2. Select "click" from dropdown
3. Set subdivision to 4
4. Tap Play button
5. Listen for 4 beats

**Expected Results:**
- Click sound plays on each beat
- Sound is clear, no distortion
- Volume is appropriate
- No lag or stuttering

**Pass/Fail**: _____

---

### TC-04: Paired MP3 Files Detection
**Priority**: Critical  
**Precondition**: Test Set 2 files added

**Steps:**
1. Restart app (to rescan ticks folder)
2. Add new layer, set mode to mp3_tick
3. Check tick dropdown

**Expected Results:**
- Dropdown contains "paired" (not "paired_1" or "paired_2")
- Dropdown contains "woodblock" (not "woodblock_1" or "woodblock_2")
- Single files still appear individually

**Pass/Fail**: _____

---

### TC-05: Paired MP3 Accent Behavior
**Priority**: Critical  
**Precondition**: TC-04 passed

**Steps:**
1. Add layer with mp3_tick mode
2. Select "paired" from dropdown
3. Set subdivision to 4, beats per measure to 4
4. Tap Play
5. Listen to first beat vs other beats

**Expected Results:**
- First beat of measure plays `paired_1.mp3` (high pitch)
- Beats 2, 3, 4 play `paired_2.mp3` (low pitch)
- Pattern repeats each measure
- Sounds are distinctly different

**Pass/Fail**: _____

---

### TC-06: Volume Control
**Priority**: High  
**Precondition**: TC-03 passed

**Steps:**
1. Layer with mp3_tick "click" playing
2. Adjust volume slider to 0.0
3. Observe sound
4. Adjust to 1.0
5. Observe sound
6. Adjust to 2.0
7. Observe sound

**Expected Results:**
- At 0.0: No sound (silent)
- At 1.0: Normal volume
- At 2.0: Louder (but not distorted if original level was reasonable)

**Pass/Fail**: _____

---

### TC-07: Accent Volume Control
**Priority**: High  
**Precondition**: TC-05 passed

**Steps:**
1. Layer with paired mp3_tick playing
2. Accent slider at 1.0 (no accent)
3. Listen to beats
4. Adjust accent slider to 2.0
5. Listen again

**Expected Results:**
- At 1.0: _1 and _2 files at same volume
- At 2.0: _1 file is twice as loud as _2 file

**Pass/Fail**: _____

---

### TC-08: Switch MP3 During Playback
**Priority**: Medium  
**Precondition**: TC-03 passed

**Steps:**
1. Layer with "click" playing
2. While metronome is running, change tick to "woodblock"
3. Observe sound change
4. Change back to "click"

**Expected Results:**
- Sound changes immediately
- No crashes or audio glitches
- New sound plays correctly

**Pass/Fail**: _____

---

### TC-09: Multiple Layers with MP3 Ticks
**Priority**: High  
**Precondition**: TC-03 passed

**Steps:**
1. Left ear: Add layer with "click", subdiv 4
2. Right ear: Add layer with "woodblock", subdiv 8
3. Play metronome

**Expected Results:**
- Both sounds play simultaneously
- Left ear plays click on quarter notes
- Right ear plays woodblock on eighth notes
- No mixing issues or distortion

**Pass/Fail**: _____

---

### TC-10: Stereo MP3 Conversion
**Priority**: Medium  
**Precondition**: Test Set 3 files added

**Steps:**
1. Restart app
2. Add layer with mp3_tick mode
3. Select "stereo" from dropdown
4. Play metronome

**Expected Results:**
- Stereo file loads successfully
- Plays as mono (left + right averaged)
- Sound quality is good
- No crashes

**Pass/Fail**: _____

---

### TC-11: High Sample Rate Resampling
**Priority**: Medium  
**Precondition**: Test Set 3 files added

**Steps:**
1. Add layer with "high_rate" (48kHz)
2. Play metronome
3. Listen to sound quality

**Expected Results:**
- File loads successfully
- Resampled to 44.1kHz
- Sound quality is acceptable
- No artifacts or distortion

**Pass/Fail**: _____

---

### TC-12: Low Sample Rate Resampling
**Priority**: Medium  
**Precondition**: Test Set 3 files added

**Steps:**
1. Add layer with "low_rate" (22.05kHz)
2. Play metronome
3. Listen to sound quality

**Expected Results:**
- File loads successfully
- Resampled to 44.1kHz
- Sound is slightly muffled (expected for low rate)
- No crashes or artifacts

**Pass/Fail**: _____

---

### TC-13: Long Audio File
**Priority**: Medium  
**Precondition**: Test Set 3 files added

**Steps:**
1. Add layer with "long_sound" (1 second)
2. Play metronome at slow tempo (60 BPM)

**Expected Results:**
- Long file loads (may take a moment at startup)
- Plays correctly (full sound or gets cut off by next beat)
- No memory issues
- No crashes

**Pass/Fail**: _____

---

### TC-14: Tiny Audio File
**Priority**: Low  
**Precondition**: Test Set 3 files added

**Steps:**
1. Add layer with "tiny" (10ms)
2. Play metronome

**Expected Results:**
- Tiny file loads successfully
- Sound is very short (may be almost inaudible)
- No crashes

**Pass/Fail**: _____

---

### TC-15: Corrupted MP3 File
**Priority**: High  
**Precondition**: Test Set 4 files added

**Steps:**
1. Restart app
2. Check logs for errors
3. Try to add layer with mp3_tick mode
4. Check dropdown contents

**Expected Results:**
- App doesn't crash at startup
- Logs show error: "Failed to read MP3 file"
- Corrupted files don't appear in dropdown
- Valid files still work

**Pass/Fail**: _____

---

### TC-16: Empty MP3 File
**Priority**: Medium  
**Precondition**: Test Set 4 files added

**Steps:**
1. Restart app
2. Check logs for errors
3. Check dropdown

**Expected Results:**
- App doesn't crash
- Empty file either doesn't appear or shows error
- Other files still work

**Pass/Fail**: _____

---

### TC-17: Save/Load with MP3 Ticks
**Priority**: High  
**Precondition**: TC-03 passed

**Steps:**
1. Create pattern with mp3_tick layers
2. Tap Save button
3. Enter name "test_mp3"
4. Tap New button
5. Tap Load button
6. Select "test_mp3"

**Expected Results:**
- Pattern saves successfully
- Pattern loads successfully
- MP3 tick settings are restored
- Correct tick is selected in dropdown

**Pass/Fail**: _____

---

### TC-18: Memory Usage with Many Files
**Priority**: Medium  
**Precondition**: 20+ MP3 files in ticks folder

**Steps:**
1. Restart app
2. Monitor memory usage (use Android Studio Profiler or similar)
3. Note startup time
4. Add layers with different ticks

**Expected Results:**
- Memory usage is reasonable (< 100 MB increase)
- Startup time < 10 seconds
- No memory leaks
- No OutOfMemory errors

**Pass/Fail**: _____

---

### TC-19: App Restart Persistence
**Priority**: Medium  
**Precondition**: TC-03 passed

**Steps:**
1. Create layer with mp3_tick "click"
2. Play briefly, then stop
3. Close app completely
4. Restart app

**Expected Results:**
- Auto-save restored the state
- MP3 tick layer is still there
- Mode is still "mp3_tick"
- Tick is still "click"

**Pass/Fail**: _____

---

### TC-20: No Ticks Folder
**Priority**: Medium  
**Precondition**: Remove/rename ticks folder

**Steps:**
1. Delete or rename ticks folder
2. Restart app
3. Try to add layer with mp3_tick mode

**Expected Results:**
- App doesn't crash
- mp3_tick mode still appears in dropdown
- Tick dropdown shows "(no ticks)" or is empty
- Fallback to tone mode if tick is unavailable

**Pass/Fail**: _____

---

### TC-21: Performance - Rapid Tempo
**Priority**: Medium  
**Precondition**: TC-03 passed

**Steps:**
1. Add layer with mp3_tick "click"
2. Set subdivision to 16 (sixteenth notes)
3. Set BPM to 240 (maximum)
4. Play for 30 seconds

**Expected Results:**
- Sounds play correctly at high speed
- No audio dropouts or stuttering
- No crashes
- CPU usage is reasonable

**Pass/Fail**: _____

---

### TC-22: Mute Control
**Priority**: Medium  
**Precondition**: TC-03 passed

**Steps:**
1. Layer with mp3_tick playing
2. Tap Mute button
3. Observe sound
4. Tap Mute again
5. Observe sound

**Expected Results:**
- Muted: No sound plays
- Unmuted: Sound returns immediately
- No crashes or glitches

**Pass/Fail**: _____

---

### TC-23: Mix of Modes
**Priority**: High  
**Precondition**: TC-03 passed

**Steps:**
1. Left ear:
   - Layer 1: Tone mode, 880 Hz
   - Layer 2: MP3 tick "click"
2. Right ear:
   - Layer 1: Drum mode, "kick"
   - Layer 2: MP3 tick "woodblock"
3. Play metronome

**Expected Results:**
- All four layers play correctly
- Sounds mix without issues
- No audio artifacts
- No performance problems

**Pass/Fail**: _____

---

### TC-24: Fallback to Tone on Error
**Priority**: High  
**Precondition**: TC-15 passed (corrupted file test)

**Steps:**
1. Create layer with mp3_tick mode
2. Select a valid tick
3. Save pattern
4. Exit app
5. Delete the MP3 file
6. Restart app
7. Load pattern
8. Play metronome

**Expected Results:**
- Pattern loads
- Missing MP3 causes fallback to tone mode
- Tone plays instead of crashing
- Error logged but app continues

**Pass/Fail**: _____

---

## Regression Tests

### RT-01: Tone Mode Still Works
**Priority**: Critical

**Steps:**
1. Add layer with tone mode
2. Set frequency to 440 Hz
3. Play metronome

**Expected Results:**
- Tone plays correctly
- No impact from MP3 feature

**Pass/Fail**: _____

---

### RT-02: Drum Mode Still Works
**Priority**: Critical

**Steps:**
1. Add layer with drum mode
2. Select "kick"
3. Play metronome

**Expected Results:**
- Drum sound plays correctly
- No impact from MP3 feature

**Pass/Fail**: _____

---

### RT-03: Existing Save Files Compatible
**Priority**: High

**Steps:**
1. Load a pattern saved before MP3 feature
2. Play metronome

**Expected Results:**
- Old save files load successfully
- Backward compatible (no mp3_tick field is OK)
- Plays correctly

**Pass/Fail**: _____

---

## Device-Specific Tests

### DT-01: Kindle Fire HD 10
**Device**: Kindle Fire HD 10 (Fire OS)

**Steps:**
1. Run TC-01 through TC-23 on Kindle Fire
2. Note any device-specific issues

**Expected Results:**
- All tests pass
- Performance is acceptable
- No Fire OS-specific crashes

**Pass/Fail**: _____

---

### DT-02: Low-End Device
**Device**: Android 5.0, 1GB RAM

**Steps:**
1. Run TC-01, TC-03, TC-18, TC-21
2. Monitor performance and memory

**Expected Results:**
- App runs without OutOfMemory errors
- Performance may be slower but acceptable
- Audio doesn't stutter

**Pass/Fail**: _____

---

## Summary

Total Test Cases: 24 (core) + 3 (regression) + 2 (device-specific) = **29 tests**

### Priority Breakdown
- **Critical**: 7 tests
- **High**: 8 tests
- **Medium**: 12 tests
- **Low**: 2 tests

### Estimated Testing Time
- First-time setup: 30 minutes
- Core tests: 2 hours
- Regression tests: 30 minutes
- Device-specific: 1 hour per device
- **Total**: ~4-6 hours

## Test Results Summary

| Test ID | Description | Status | Notes |
|---------|-------------|--------|-------|
| TC-01 | App startup | | |
| TC-02 | Dropdown | | |
| TC-03 | Single MP3 | | |
| TC-04 | Paired detection | | |
| TC-05 | Accent behavior | | |
| TC-06 | Volume | | |
| TC-07 | Accent volume | | |
| TC-08 | Switch tick | | |
| TC-09 | Multiple layers | | |
| TC-10 | Stereo conversion | | |
| TC-11 | High sample rate | | |
| TC-12 | Low sample rate | | |
| TC-13 | Long file | | |
| TC-14 | Tiny file | | |
| TC-15 | Corrupted file | | |
| TC-16 | Empty file | | |
| TC-17 | Save/load | | |
| TC-18 | Memory usage | | |
| TC-19 | Persistence | | |
| TC-20 | No ticks folder | | |
| TC-21 | Rapid tempo | | |
| TC-22 | Mute | | |
| TC-23 | Mix of modes | | |
| TC-24 | Fallback | | |
| RT-01 | Tone regression | | |
| RT-02 | Drum regression | | |
| RT-03 | Compatibility | | |
| DT-01 | Kindle Fire | | |
| DT-02 | Low-end device | | |

## Known Limitations

Document any known limitations discovered during testing:

1. 
2. 
3. 

## Issues Found

Document any bugs or issues discovered:

| Issue ID | Description | Severity | Status |
|----------|-------------|----------|--------|
| | | | |
