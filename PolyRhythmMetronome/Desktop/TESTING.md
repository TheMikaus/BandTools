# PolyRhythmMetronome Testing Guide

This document describes manual testing procedures for the new features.

## Color Randomization Tests

### Test 1: Random Dark Colors for New Layers
**Steps:**
1. Launch the application
2. Click "Add to Left" or "Add to Right" multiple times
3. Observe the colors assigned to each new layer

**Expected Results:**
- Each new layer should have a different dark color
- Colors should be visually distinct from each other
- Colors should be dark enough to contrast with white text
- The color picker button in the "New Layer" section should show a new random color after each add

**Pass/Fail:** ___________

### Test 2: Auto-Generated Flash Colors
**Steps:**
1. Launch the application
2. Add a new layer with a dark color
3. Enable the "Flash" checkbox in the global settings
4. Click "Play" and observe the layer flashing

**Expected Results:**
- The layer should flash with a brighter version of its inactive color
- The flash should be clearly visible
- The brightness should be approximately 2x the original color values (capped at 255)

**Pass/Fail:** ___________

## MP3 Tick Support Tests

### Test 3: Single MP3 Tick
**Steps:**
1. Place a single MP3 file (e.g., `click.mp3`) in the `ticks` folder
2. Launch the application
3. Select "MP3" mode in the "New Layer" section
4. Select the MP3 tick from the dropdown
5. Add the layer and play

**Expected Results:**
- The MP3 tick should appear in the dropdown
- The sound should play on each subdivision beat
- The sound should be clear without distortion

**Pass/Fail:** ___________

### Test 4: Paired MP3 Ticks (Accent vs Regular)
**Steps:**
1. Place two MP3 files named `test_1.mp3` and `test_2.mp3` in the `ticks` folder
2. Launch the application
3. Select "MP3" mode
4. Select "test" from the dropdown (should see the pair without _1/_2 suffix)
5. Add the layer with subdivision 4 and beats per measure 4
6. Play the metronome

**Expected Results:**
- The pair should appear as a single "test" entry in the dropdown
- On the first beat of each measure (accent), `test_1.mp3` should play
- On beats 2, 3, and 4, `test_2.mp3` should play
- The two sounds should be distinctly different

**Pass/Fail:** ___________

### Test 5: MP3 Tick Persistence
**Steps:**
1. Add an MP3 tick layer
2. Save the rhythm pattern
3. Close the application
4. Reopen and load the rhythm pattern

**Expected Results:**
- The MP3 tick layer should load correctly
- The MP3 tick name should still be selected
- Playing should work as before

**Pass/Fail:** ___________

## AudioTrack Fix (Android Only)

### Test 6: Tone Playback on Android
**Platform:** Android only

**Steps:**
1. Install the app on an Android device
2. Add a tone layer (default 880Hz)
3. Click Play

**Expected Results:**
- No "play called on uninitialized AudioTrack" error
- Tone should play clearly
- No crashes or audio stuttering

**Pass/Fail:** ___________

## Build Tests

### Test 7: Build with PyInstaller (Desktop)
**Steps:**
1. Run `./build.sh` (Linux/Mac) or `build.bat` (Windows)
2. Navigate to `dist` folder
3. Run the executable

**Expected Results:**
- Build completes without errors
- Executable runs without requiring Python installation
- `ticks` folder is included in the build
- Application functions normally

**Pass/Fail:** ___________

## Threading Tests

### Test 8: Flash Timing During Audio Playback
**Steps:**
1. Add multiple layers to both left and right
2. Set different subdivisions (e.g., 3, 4, 5, 7)
3. Enable "Flash" checkbox
4. Play at various BPM settings (60, 120, 180)

**Expected Results:**
- Flashes should occur precisely on beat
- No lag or delay between sound and flash
- UI should remain responsive during playback
- No frame drops or stuttering

**Pass/Fail:** ___________

### Test 9: Audio Timing Accuracy
**Steps:**
1. Add a simple 4/4 pattern with quarter note subdivisions
2. Use external metronome app or recording to verify timing
3. Play for at least 1 minute

**Expected Results:**
- Timing should be accurate and stable
- No drift over time
- Audio should stay in sync with external reference

**Pass/Fail:** ___________

## Edge Cases

### Test 10: Empty Ticks Folder
**Steps:**
1. Delete all files from the `ticks` folder (keep the folder itself)
2. Launch the application
3. Try to select MP3 mode

**Expected Results:**
- Application should launch without errors
- MP3 tick dropdown should be empty or show placeholder
- Other modes should work normally

**Pass/Fail:** ___________

### Test 11: Invalid MP3 Files
**Steps:**
1. Place a non-MP3 file renamed with .mp3 extension in `ticks` folder
2. Launch application and try to use it

**Expected Results:**
- Application should handle gracefully (error message or skip)
- Should not crash
- Other valid MP3 ticks should still work

**Pass/Fail:** ___________

### Test 12: Color Picker Edge Cases
**Steps:**
1. Pick pure black (#000000) as layer color
2. Observe flash color
3. Pick pure white (#FFFFFF) as layer color
4. Observe flash color

**Expected Results:**
- Black should brighten to a visible gray
- White should remain white (capped at 255)
- No crashes or rendering issues

**Pass/Fail:** ___________

## Performance Tests

### Test 13: Many Layers Performance
**Steps:**
1. Add 10+ layers to each side (left and right)
2. Use different modes (tone, drum, MP3)
3. Play at 180 BPM

**Expected Results:**
- No audio glitches or dropouts
- CPU usage reasonable
- UI remains responsive
- Flash animations smooth

**Pass/Fail:** ___________

## Test Summary

Total Tests: 13
Passed: ___________
Failed: ___________
Not Tested: ___________

## Notes

[Add any additional observations or issues discovered during testing]
