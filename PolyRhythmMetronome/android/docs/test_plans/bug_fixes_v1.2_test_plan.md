# Bug Fixes v1.2 - Test Plan

**Version**: 1.2.0  
**Date**: 2025-10-12  
**Tester**: _____________  
**Device**: _____________  
**OS Version**: _____________

## Overview

This test plan covers bug fixes and UI improvements for version 1.2.0 of the PolyRhythmMetronome Android app. The main focus is on improving audio playback reliability, UI layout optimization, and visual feedback enhancements.

## Test Environment

- [ ] Device: ___________________________
- [ ] Android/Fire OS Version: __________
- [ ] Screen Resolution: ________________
- [ ] Previous App Version Installed: Yes / No

---

## Bug Verification

### BV-1: Audio Playback Improvement
**Priority**: HIGH  
**Description**: Verify Play button properly plays audio

**Original Issue**: Play button does not play audio  
**Fix**: Improved simpleaudio auto-installation

**Steps**:
1. Launch the app (fresh install if possible)
2. Observe console/log for audio library initialization
3. Add layers with different sounds (tone and drum modes)
4. Press PLAY button
5. Listen for audio output

**Expected Result**:
- Console shows "[audio] Using simpleaudio for playback"
- Audio plays immediately when PLAY is pressed
- Both tone and drum sounds are audible
- Stereo separation works (left/right channels)

**Status**: [ ] Pass [ ] Fail  
**Notes**: _________________________________

---

### BV-2: Per-Layer Visual Flashing
**Priority**: HIGH  
**Description**: Verify individual layer rows flash instead of full screen

**Original Issue**: Full screen flashes on each beat, making it hard to see which layer is playing  
**Fix**: Implemented per-layer row flashing matching desktop behavior

**Steps**:
1. Add 2-3 layers to left ear with different subdivisions (÷1, ÷2, ÷4)
2. Add 2-3 layers to right ear with different subdivisions
3. Set different colors for each layer
4. Press PLAY
5. Observe visual feedback

**Expected Result**:
- Only the specific layer row flashes when its beat occurs
- Flash color matches the layer's configured color
- Multiple layers can flash independently
- Flash is visible but not overwhelming
- Full screen does not flash

**Status**: [ ] Pass [ ] Fail  
**Notes**: _________________________________

---

### BV-3: BPM Button Layout
**Priority**: MEDIUM  
**Description**: Verify BPM buttons are taller but thinner and fit in one row

**Original Issue**: BPM buttons too small and in 2 rows  
**Fix**: Changed from 4 columns (2 rows) to 8 columns (1 row)

**Steps**:
1. Launch the app
2. Observe BPM preset buttons (60, 80, 100, 120, 140, 160, 180, 200)
3. Verify all 8 buttons are visible in one row
4. Test tapping each button

**Expected Result**:
- All 8 BPM buttons visible in one horizontal row
- Buttons are taller (more vertical space)
- Buttons are thinner (less horizontal space)
- All buttons are easy to tap
- No scrolling needed to see all buttons
- BPM changes when buttons are tapped

**Status**: [ ] Pass [ ] Fail  
**Notes**: _________________________________

---

### BV-4: Reduced UI Spacing
**Priority**: LOW  
**Description**: Verify reduced gap between BPM buttons and layer lists

**Original Issue**: Large gap wastes screen space  
**Fix**: Reduced spacing from 10dp to 2dp

**Steps**:
1. Launch the app
2. Observe spacing between BPM preset buttons and layer list titles
3. Compare with previous version if available

**Expected Result**:
- Minimal gap between BPM buttons and "LEFT Layers" / "RIGHT Layers" titles
- More screen space available for layer lists
- UI looks more compact but not cramped

**Status**: [ ] Pass [ ] Fail  
**Notes**: _________________________________

---

## Feature Tests

### FT-1: Audio Playback Reliability

#### TC-1.1: Multiple Audio Libraries
**Priority**: HIGH  
**Description**: Verify audio works with simpleaudio

**Steps**:
1. Fresh install of app
2. Launch and check logs for audio library detection
3. Test audio playback

**Expected Result**:
- App successfully loads simpleaudio
- Audio plays without errors
- If simpleaudio fails, app falls back gracefully

**Status**: [ ] Pass [ ] Fail

---

#### TC-1.2: Audio During Playback Changes
**Priority**: MEDIUM  
**Description**: Verify audio continues correctly when layers change

**Steps**:
1. Start playback with 2 layers
2. While playing, add a new layer
3. While playing, delete a layer
4. While playing, mute a layer
5. While playing, change BPM

**Expected Result**:
- Audio continues playing smoothly
- New layers start playing immediately
- Deleted layers stop immediately
- Muted layers go silent
- BPM changes take effect immediately

**Status**: [ ] Pass [ ] Fail

---

### FT-2: Layer Row Flashing

#### TC-2.1: Single Layer Flash
**Priority**: HIGH  
**Description**: Verify single layer flashes correctly

**Steps**:
1. Create one layer in left ear with ÷4 subdivision
2. Set layer color to #FF0000 (red)
3. Press PLAY
4. Observe the layer widget

**Expected Result**:
- Layer row flashes red on each quarter note beat
- Flash duration is brief (~120ms)
- Only that specific row flashes, not full screen
- Flash is clearly visible

**Status**: [ ] Pass [ ] Fail

---

#### TC-2.2: Multiple Layer Flash
**Priority**: HIGH  
**Description**: Verify multiple layers flash independently

**Steps**:
1. Create left layer with ÷1 (whole notes) and color #FF0000 (red)
2. Create left layer with ÷4 (quarter notes) and color #00FF00 (green)
3. Create left layer with ÷8 (eighth notes) and color #0000FF (blue)
4. Press PLAY
5. Observe all three layer rows

**Expected Result**:
- Each layer flashes with its own color
- Flash timing matches the subdivision (÷1 is 4x slower than ÷4, ÷8 is 2x faster than ÷4)
- Flashes are synchronized correctly
- Multiple layers can flash simultaneously without interference

**Status**: [ ] Pass [ ] Fail

---

#### TC-2.3: Flash with Custom Colors
**Priority**: MEDIUM  
**Description**: Verify flash works with various colors

**Steps**:
1. Create layers with different colors:
   - #FF0000 (red)
   - #00FF00 (green)
   - #0000FF (blue)
   - #FFFF00 (yellow)
   - #FF00FF (magenta)
2. Press PLAY
3. Observe flashing

**Expected Result**:
- Each layer flashes with its configured color
- Colors are clearly distinguishable
- Flash effect is visible for all colors

**Status**: [ ] Pass [ ] Fail

---

### FT-3: BPM Button Layout

#### TC-3.1: Button Visibility
**Priority**: HIGH  
**Description**: Verify all BPM buttons are visible and usable

**Steps**:
1. Launch app in portrait mode
2. Observe BPM preset button area
3. Count visible buttons
4. Switch to landscape mode
5. Observe buttons again

**Expected Result**:
- All 8 buttons (60, 80, 100, 120, 140, 160, 180, 200) visible in both orientations
- Buttons are in a single horizontal row
- No scrolling required
- Buttons have adequate touch target size

**Status**: [ ] Pass [ ] Fail

---

#### TC-3.2: Button Functionality
**Priority**: HIGH  
**Description**: Verify BPM buttons work correctly

**Steps**:
1. Tap each BPM preset button (60, 80, 100, 120, 140, 160, 180, 200)
2. Observe BPM value display
3. Press PLAY to test audio tempo

**Expected Result**:
- BPM value updates immediately
- Slider position matches selected BPM
- Audio tempo changes if already playing
- All buttons respond correctly

**Status**: [ ] Pass [ ] Fail

---

#### TC-3.3: Layout Proportions
**Priority**: MEDIUM  
**Description**: Verify buttons are taller but thinner

**Steps**:
1. Observe BPM buttons
2. Compare button height to previous version (if available)
3. Compare button width to previous version (if available)

**Expected Result**:
- Buttons are noticeably taller than previous version
- Buttons are noticeably thinner than previous version
- Text is still readable at 20sp font size
- Touch targets are adequate

**Status**: [ ] Pass [ ] Fail

---

### FT-4: UI Spacing

#### TC-4.1: Visual Inspection
**Priority**: LOW  
**Description**: Verify UI spacing looks appropriate

**Steps**:
1. Launch app
2. Observe overall layout
3. Check spacing between:
   - Title and BPM slider
   - BPM slider and preset buttons
   - Preset buttons and layer lists
   - Layer lists and control buttons

**Expected Result**:
- Layout looks compact but not cramped
- More screen space for layer lists
- No excessive gaps or overlapping elements

**Status**: [ ] Pass [ ] Fail

---

## Integration Tests

### IT-1: Complete Workflow Test
**Priority**: HIGH  
**Description**: Test complete user workflow with all new features

**Steps**:
1. Launch app (fresh install)
2. Use BPM preset buttons to set tempo
3. Add 3 layers to left with different colors and subdivisions
4. Add 3 layers to right with different colors and subdivisions
5. Press PLAY
6. Observe audio playback and visual flashing
7. While playing, change BPM
8. While playing, add/remove layers
9. Save rhythm pattern
10. Stop playback
11. Load rhythm pattern
12. Press PLAY again

**Expected Result**:
- All features work together seamlessly
- Audio plays correctly throughout
- Visual feedback is helpful and not distracting
- UI is responsive
- Save/load preserves all settings

**Status**: [ ] Pass [ ] Fail

---

## Regression Tests

### RT-1: Existing Features Still Work

#### TC-RT-1: Layer Management
**Priority**: HIGH  
**Steps**:
1. Add layers
2. Delete layers (including deleting all layers)
3. Edit layer properties (mode, subdivision, frequency/drum, volume, color)
4. Mute/unmute layers

**Expected Result**: All work as before

**Status**: [ ] Pass [ ] Fail

---

#### TC-RT-2: BPM Control
**Priority**: HIGH  
**Steps**:
1. Use BPM slider
2. Use BPM preset buttons
3. Test range from 40 to 240 BPM

**Expected Result**: All work as before

**Status**: [ ] Pass [ ] Fail

---

#### TC-RT-3: Save/Load
**Priority**: HIGH  
**Steps**:
1. Create complex rhythm pattern
2. Save to file
3. Create new pattern
4. Load previous file
5. Verify all settings restored

**Expected Result**: Save/load works correctly

**Status**: [ ] Pass [ ] Fail

---

#### TC-RT-4: NEW Button
**Priority**: MEDIUM  
**Steps**:
1. Create complex pattern with many layers
2. Press NEW button
3. Confirm reset

**Expected Result**: Pattern resets to default single layer per ear

**Status**: [ ] Pass [ ] Fail

---

## Performance Tests

### PT-1: Audio Performance

**Steps**:
1. Create 5+ layers per ear
2. All layers playing different subdivisions
3. Press PLAY
4. Monitor for audio glitches or lag

**Expected Result**: Smooth audio playback without glitches

**Status**: [ ] Pass [ ] Fail

---

### PT-2: Visual Performance

**Steps**:
1. Create 5+ layers per ear
2. Set to fast tempo (200 BPM)
3. Use fast subdivisions (÷8 or ÷16)
4. Press PLAY
5. Observe flashing performance

**Expected Result**: Flashing is smooth without lag or missed beats

**Status**: [ ] Pass [ ] Fail

---

## Edge Cases

### EC-1: No Layers Playback
**Priority**: MEDIUM  
**Steps**:
1. Delete all layers from both left and right
2. Press PLAY

**Expected Result**: App doesn't crash, PLAY button works (silent playback)

**Status**: [ ] Pass [ ] Fail

---

### EC-2: Invalid Color Codes
**Priority**: LOW  
**Steps**:
1. Enter invalid color codes in layer color field
2. Press PLAY

**Expected Result**: App handles gracefully, uses default color or skips flashing

**Status**: [ ] Pass [ ] Fail

---

## Summary

**Total Tests**: _____ / _____  
**Passed**: _____  
**Failed**: _____  
**Blocked**: _____  

### Critical Issues Found
_________________________________
_________________________________
_________________________________

### Notes
_________________________________
_________________________________
_________________________________

---

**Tester Signature**: _____________  
**Date**: _____________
