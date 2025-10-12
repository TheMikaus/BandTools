# Bug Fixes v1.1 - Test Plan

## Overview
This test plan covers the bug fixes and enhancements made in version 1.1.0 of the Android PolyRhythmMetronome.

## Test Environment
- **Platform**: Android (Kindle Fire HD 10 or similar)
- **OS**: Fire OS / Android 5.0+
- **Build**: Kivy-based APK

## Test Cases

### 1. Audio Playback Fix

#### TC-1.1: Basic Audio Playback
**Priority**: CRITICAL  
**Description**: Verify that the Play button now produces audio output

**Steps**:
1. Launch the app
2. Ensure at least one layer exists (default state)
3. Press the PLAY button
4. Listen for audio output

**Expected Result**:
- Audio plays from the device speakers/headphones
- Left channel layers play in left ear
- Right channel layers play in right ear
- Tone or drum sound matches layer configuration

**Status**: [ ] Pass [ ] Fail

---

#### TC-1.2: Multiple Layers Audio
**Priority**: HIGH  
**Description**: Verify audio plays correctly with multiple layers

**Steps**:
1. Add 2-3 layers to left channel with different subdivisions (e.g., 4, 8, 16)
2. Add 2-3 layers to right channel with different subdivisions
3. Set different sounds (mix of tones and drums)
4. Press PLAY

**Expected Result**:
- All unmuted layers produce audio
- Subdivisions are correctly timed
- Left and right channels maintain separation
- No audio distortion or cutoff

**Status**: [ ] Pass [ ] Fail

---

#### TC-1.3: Drum Sounds
**Priority**: HIGH  
**Description**: Verify all drum sounds play correctly

**Steps**:
1. For each drum sound (kick, snare, hihat, crash, tom, ride):
   - Create a layer
   - Set mode to "drum"
   - Select the drum sound
   - Press PLAY
   - Listen to the sound

**Expected Result**:
- Each drum sound is distinct and audible
- Sounds match their names (kick is bass, hihat is high, etc.)
- No silence or errors

**Status**: [ ] Pass [ ] Fail

---

### 2. Color Picker Feature

#### TC-2.1: Color Input Field
**Priority**: MEDIUM  
**Description**: Verify color input field appears and accepts input

**Steps**:
1. Launch the app
2. Observe any layer widget
3. Locate the "Color:" field

**Expected Result**:
- Color input field is visible
- Shows current color (e.g., #3B82F6 for left, #EF4444 for right)
- Field is editable

**Status**: [ ] Pass [ ] Fail

---

#### TC-2.2: Valid Color Entry
**Priority**: MEDIUM  
**Description**: Verify valid hex colors are accepted

**Steps**:
1. Click on a layer's color field
2. Enter a valid hex color: #FF0000 (red)
3. Tab away or click elsewhere
4. Observe layer background

**Expected Result**:
- Layer background updates to red tint
- Color is saved in layer configuration
- No errors displayed

**Test Data**:
- #FF0000 (red)
- #00FF00 (green)
- #0000FF (blue)
- #FFFF00 (yellow)
- #F0F (short form - magenta)

**Status**: [ ] Pass [ ] Fail

---

#### TC-2.3: Invalid Color Entry
**Priority**: LOW  
**Description**: Verify invalid colors are rejected gracefully

**Steps**:
1. Enter invalid color values in color field
2. Observe behavior

**Expected Result**:
- Invalid colors are ignored
- No crash or error dialog
- Previous valid color retained

**Test Data**:
- INVALID
- 123456 (no # prefix)
- #GGGGGG (invalid hex)
- #12 (too short)

**Status**: [ ] Pass [ ] Fail

---

### 3. Visual Flashing

#### TC-3.1: Basic Flash on Beat
**Priority**: HIGH  
**Description**: Verify screen flashes when beat occurs

**Steps**:
1. Create a layer with subdivision 4 (quarter notes)
2. Set color to #FF0000 (red)
3. Press PLAY
4. Observe screen

**Expected Result**:
- Screen flashes red on each quarter note
- Flash lasts approximately 0.12 seconds
- Flash is visible but not too bright
- Flash color matches layer color

**Status**: [ ] Pass [ ] Fail

---

#### TC-3.2: Multiple Layer Flashing
**Priority**: HIGH  
**Description**: Verify multiple layers flash independently

**Steps**:
1. Create left layer: subdiv=4, color=#FF0000 (red)
2. Create right layer: subdiv=8, color=#0000FF (blue)
3. Press PLAY
4. Observe flashing pattern

**Expected Result**:
- Red flash every quarter note
- Blue flash every eighth note
- Flashes are synchronized to subdivisions
- When both beat simultaneously, colors may blend briefly

**Status**: [ ] Pass [ ] Fail

---

#### TC-3.3: Flash Timing Accuracy
**Priority**: MEDIUM  
**Description**: Verify flash timing matches beat divisions

**Steps**:
1. Set BPM to 120
2. Create layers with subdivisions: 1, 2, 4, 8, 16
3. Set distinct colors for each
4. Press PLAY
5. Count flashes per measure for each layer

**Expected Result**:
- Subdiv 1: 1 flash per measure
- Subdiv 2: 2 flashes per measure
- Subdiv 4: 4 flashes per measure
- Subdiv 8: 8 flashes per measure
- Subdiv 16: 16 flashes per measure

**Status**: [ ] Pass [ ] Fail

---

### 4. BPM Button Size

#### TC-4.1: Button Visibility
**Priority**: MEDIUM  
**Description**: Verify BPM preset buttons are larger and easier to tap

**Steps**:
1. Launch the app
2. Observe BPM preset buttons (60, 80, 100, 120, 140, 160, 180, 200)
3. Compare to previous version if available

**Expected Result**:
- Text is larger (20sp vs 14sp)
- Buttons are easier to read
- Touch targets feel appropriate for finger tapping

**Status**: [ ] Pass [ ] Fail

---

#### TC-4.2: Button Functionality
**Priority**: HIGH  
**Description**: Verify BPM buttons still work correctly

**Steps**:
1. Tap each BPM preset button
2. Observe BPM value display

**Expected Result**:
- BPM changes to selected value
- Slider updates to match
- Playing audio tempo changes immediately

**Status**: [ ] Pass [ ] Fail

---

### 5. Layer Deletion

#### TC-5.1: Delete All Left Layers
**Priority**: HIGH  
**Description**: Verify all left layers can be removed

**Steps**:
1. Ensure multiple layers exist on left side
2. Click X button on each left layer until none remain
3. Observe behavior

**Expected Result**:
- All layers can be deleted
- No error or forced layer addition
- Left channel has zero layers
- Right channel unaffected

**Status**: [ ] Pass [ ] Fail

---

#### TC-5.2: Delete All Right Layers
**Priority**: HIGH  
**Description**: Verify all right layers can be removed

**Steps**:
1. Ensure multiple layers exist on right side
2. Click X button on each right layer until none remain
3. Observe behavior

**Expected Result**:
- All layers can be deleted
- No error or forced layer addition
- Right channel has zero layers
- Left channel unaffected

**Status**: [ ] Pass [ ] Fail

---

#### TC-5.3: Delete All Layers Both Sides
**Priority**: HIGH  
**Description**: Verify all layers can be removed from both sides

**Steps**:
1. Delete all left layers
2. Delete all right layers
3. Press PLAY
4. Observe behavior

**Expected Result**:
- App allows zero layers total
- PLAY button still works (even if silent)
- No crash or error
- Can add new layers after deletion

**Status**: [ ] Pass [ ] Fail

---

#### TC-5.4: Load State with Empty Channels
**Priority**: MEDIUM  
**Description**: Verify saved states with empty channels load correctly

**Steps**:
1. Delete all layers from one or both channels
2. Save the rhythm
3. Load a different rhythm
4. Load the saved rhythm with empty channels

**Expected Result**:
- Empty channels remain empty
- No forced layer addition
- App functions normally

**Status**: [ ] Pass [ ] Fail

---

### 6. Integration Tests

#### TC-6.1: Full Feature Integration
**Priority**: HIGH  
**Description**: Test all features working together

**Steps**:
1. Create 3 layers on left with different colors, subdivisions, and sounds
2. Create 2 layers on right with different colors, subdivisions, and sounds
3. Set custom colors for all layers
4. Adjust BPM using preset buttons
5. Press PLAY
6. Observe audio and visual feedback

**Expected Result**:
- Audio plays correctly for all layers
- Visual flashing matches each layer's color and subdivision
- BPM affects all layers
- No glitches or performance issues

**Status**: [ ] Pass [ ] Fail

---

#### TC-6.2: Save/Load with New Features
**Priority**: MEDIUM  
**Description**: Verify new features persist across save/load

**Steps**:
1. Create layers with custom colors
2. Save rhythm to file
3. Close and reopen app (or load different rhythm)
4. Load saved rhythm

**Expected Result**:
- Layer colors are preserved
- All layer settings restored correctly
- Audio and visual feedback work as before saving

**Status**: [ ] Pass [ ] Fail

---

## Regression Tests

### RT-1: Existing Features Still Work
**Priority**: HIGH  
**Description**: Verify existing features not affected by changes

**Test Items**:
- [ ] Mode switching (tone/drum)
- [ ] Frequency adjustment
- [ ] Volume sliders
- [ ] Mute buttons
- [ ] Subdivision selection
- [ ] Add layer button
- [ ] NEW button (reset to defaults)
- [ ] Save/Load dialogs
- [ ] BPM slider

**Status**: [ ] Pass [ ] Fail

---

## Performance Tests

### PT-1: Audio Latency
**Priority**: MEDIUM  
**Description**: Verify audio playback has acceptable latency

**Steps**:
1. Create a simple layer (subdiv 4)
2. Press PLAY
3. Compare visual flash to audio

**Expected Result**:
- Audio and visual flash are synchronized
- Latency is not noticeable (<50ms)
- No audio stuttering

**Status**: [ ] Pass [ ] Fail

---

### PT-2: Multiple Layers Performance
**Priority**: MEDIUM  
**Description**: Verify performance with many layers

**Steps**:
1. Create 10 layers total (5 left, 5 right)
2. Use different subdivisions and sounds
3. Press PLAY
4. Monitor app responsiveness

**Expected Result**:
- Audio plays smoothly
- UI remains responsive
- No dropped beats
- No crashes or freezes

**Status**: [ ] Pass [ ] Fail

---

## Bug Verification

### BV-1: Original Bug - No Audio
**Priority**: CRITICAL  
**Description**: Verify the original "Play button does not play audio" bug is fixed

**Original Issue**: Play button did nothing  
**Fix**: Added audio playback in engine

**Steps**:
1. Launch app
2. Press PLAY

**Expected Result**: Audio plays

**Status**: [ ] Pass [ ] Fail

---

### BV-2: Original Bug - No Color Flash
**Priority**: HIGH  
**Description**: Verify color flash feature is implemented

**Original Issue**: No way to specify or see flash colors  
**Fix**: Added color picker and flash overlay

**Steps**:
1. Set layer color
2. Press PLAY

**Expected Result**: Screen flashes with layer color

**Status**: [ ] Pass [ ] Fail

---

### BV-3: Original Bug - BPM Buttons Too Small
**Priority**: MEDIUM  
**Description**: Verify BPM buttons are larger

**Original Issue**: Buttons hard to tap  
**Fix**: Increased font size to 20sp

**Steps**:
1. Observe BPM buttons

**Expected Result**: Buttons are larger and easier to tap

**Status**: [ ] Pass [ ] Fail

---

### BV-4: Original Bug - Cannot Remove All Layers
**Priority**: HIGH  
**Description**: Verify all layers can be removed

**Original Issue**: Forced to keep at least one layer  
**Fix**: Removed minimum layer enforcement

**Steps**:
1. Delete all layers

**Expected Result**: All layers can be deleted

**Status**: [ ] Pass [ ] Fail

---

### BV-5: Original Bug - Drum Sounds Don't Work
**Priority**: HIGH  
**Description**: Verify drum sounds play

**Original Issue**: Drum mode didn't produce sound  
**Fix**: Audio playback now includes drum synthesis

**Steps**:
1. Create layer with drum mode
2. Press PLAY

**Expected Result**: Drum sound plays

**Status**: [ ] Pass [ ] Fail

---

## Test Execution Summary

**Total Test Cases**: 26  
**Passed**: ___  
**Failed**: ___  
**Blocked**: ___  
**Not Executed**: ___

**Tested By**: _______________  
**Date**: _______________  
**Build Version**: 1.1.0  

## Notes

_Add any additional observations, issues, or comments here._
