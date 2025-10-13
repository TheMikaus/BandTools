# Feature Enhancements Test Plan - Android PolyRhythmMetronome

## Overview

**Version**: TBD  
**Changes**: Multiple enhancements based on user feedback  
**Date**: 2025-10-13

## Changes Summary

1. **Removed flash color picker** - Flash color is now automatically generated from base color
2. **Added accent frequency control** - Tone mode can now have different frequencies for accent beats
3. **Auto-restart on layer changes** - Metronome now restarts automatically when layers are added, deleted, or muted

## Test Cases

### 1. Flash Color Auto-Generation

#### TC-1.1: Flash Color Picker Removed
**Priority**: CRITICAL  
**Description**: Verify flash color picker button is removed from UI

**Steps**:
1. Launch the app
2. Observe layer widget UI (Row 2)
3. Count color picker buttons

**Expected Result**:
- Only ONE color picker button visible (inactive color)
- No secondary/flash color picker button
- Volume slider takes up more space
- UI looks clean and uncluttered

**Status**: [ ] Pass [ ] Fail

---

#### TC-1.2: Flash Color Auto-Generated
**Priority**: HIGH  
**Description**: Verify flash color is automatically generated when base color changes

**Steps**:
1. Select a layer's color picker button
2. Choose a dark color (e.g., dark blue #1E3A8A)
3. Click OK
4. Press PLAY and observe the flash

**Expected Result**:
- Flash color is automatically brighter than base color
- Flash is clearly visible (approximately 2x brightness)
- No need to manually set flash color
- Flash synchronizes with audio

**Status**: [ ] Pass [ ] Fail

---

### 2. Accent Frequency Control

#### TC-2.1: Accent Frequency UI
**Priority**: CRITICAL  
**Description**: Verify accent frequency input field appears for tone mode

**Steps**:
1. Launch app
2. Ensure a layer is in "tone" mode
3. Observe the mode value area (after mode selector)

**Expected Result**:
- Two frequency input fields visible (stacked vertically)
- Top field: Regular frequency (labeled "Hz")
- Bottom field: Accent frequency (labeled "Acc Hz")
- Both fields accept numeric input
- Font size slightly smaller to fit both fields

**Status**: [ ] Pass [ ] Fail

---

#### TC-2.2: Accent Frequency Defaults
**Priority**: HIGH  
**Description**: Verify accent frequency defaults to regular frequency

**Steps**:
1. Add a new layer in tone mode
2. Set regular frequency to 880 Hz
3. Observe accent frequency field

**Expected Result**:
- Accent frequency automatically shows 880 Hz
- Matches regular frequency by default
- Can be changed independently

**Status**: [ ] Pass [ ] Fail

---

#### TC-2.3: Accent Frequency Playback
**Priority**: CRITICAL  
**Description**: Verify accent beats use accent frequency

**Steps**:
1. Set layer to tone mode
2. Set regular frequency: 440 Hz
3. Set accent frequency: 880 Hz (one octave higher)
4. Set subdivision: 4
5. Set beats per measure: 4 (default)
6. Press PLAY
7. Listen carefully to first beat of each measure

**Expected Result**:
- First beat of measure plays at 880 Hz (higher pitch)
- Beats 2, 3, 4 play at 440 Hz (lower pitch)
- Pattern repeats every measure
- Pitch difference is clearly audible
- Visual flash synchronized with audio

**Status**: [ ] Pass [ ] Fail

---

#### TC-2.4: Accent Frequency with Different Modes
**Priority**: MEDIUM  
**Description**: Verify accent frequency only affects tone mode

**Steps**:
1. Set layer to tone mode, test accent frequency (should work)
2. Change to drum mode, observe UI
3. Change to mp3_tick mode, observe UI

**Expected Result**:
- Tone mode: Shows both frequency fields
- Drum mode: Shows drum selector only (no frequency fields)
- MP3 tick mode: Shows mp3 selector only (no frequency fields)
- Accent frequency only applies to tone mode

**Status**: [ ] Pass [ ] Fail

---

### 3. Auto-Restart on Layer Changes

#### TC-3.1: Add Layer While Playing
**Priority**: CRITICAL  
**Description**: Verify metronome restarts when adding a layer

**Steps**:
1. Start with one layer per side
2. Press PLAY
3. While playing, click the "+" button to add a new layer
4. Observe behavior

**Expected Result**:
- Metronome stops briefly
- Metronome automatically restarts
- New layer is immediately active and playing
- No manual stop/start required
- Timing resets from beginning

**Status**: [ ] Pass [ ] Fail

---

#### TC-3.2: Delete Layer While Playing
**Priority**: CRITICAL  
**Description**: Verify metronome restarts when deleting a layer

**Steps**:
1. Start with two layers per side
2. Press PLAY
3. While playing, click "X" button to delete a layer
4. Observe behavior

**Expected Result**:
- Metronome stops briefly
- Metronome automatically restarts
- Deleted layer is no longer playing
- Remaining layers continue from beginning
- No manual stop/start required

**Status**: [ ] Pass [ ] Fail

---

#### TC-3.3: Mute Layer While Playing
**Priority**: CRITICAL  
**Description**: Verify metronome restarts when muting a layer

**Steps**:
1. Start with two layers per side
2. Press PLAY
3. While playing, click "M" button to mute a layer
4. Observe behavior

**Expected Result**:
- Metronome stops briefly
- Metronome automatically restarts
- Muted layer stops playing
- Other layers continue from beginning
- Visual flash may still occur but no audio

**Status**: [ ] Pass [ ] Fail

---

#### TC-3.4: Unmute Layer While Playing
**Priority**: HIGH  
**Description**: Verify metronome restarts when unmuting a layer

**Steps**:
1. Start with two layers, one muted
2. Press PLAY (muted layer not playing)
3. While playing, click "M" to unmute the layer
4. Observe behavior

**Expected Result**:
- Metronome stops briefly
- Metronome automatically restarts
- Previously muted layer now plays
- All layers synchronized from beginning

**Status**: [ ] Pass [ ] Fail

---

#### TC-3.5: Change Layer Settings While Playing
**Priority**: MEDIUM  
**Description**: Verify if other layer changes also trigger restart

**Steps**:
1. Press PLAY
2. Change layer frequency (tone mode)
3. Observe if restart occurs
4. Change layer subdivision
5. Change layer volume
6. Change layer accent volume

**Expected Result**:
- Frequency/drum/mp3 changes: May or may not restart (implementation dependent)
- Subdivision changes: May or may not restart (implementation dependent)
- Volume changes: Should NOT restart (volume is applied in real-time)
- Accent volume changes: Should NOT restart (volume is applied in real-time)

**Status**: [ ] Pass [ ] Fail

---

### 4. Data Persistence

#### TC-4.1: Accent Frequency Saved
**Priority**: HIGH  
**Description**: Verify accent_freq is saved with layers

**Steps**:
1. Create layer with tone mode
2. Set regular freq: 440 Hz
3. Set accent freq: 880 Hz
4. Save rhythm pattern
5. Close and reopen app
6. Load saved pattern

**Expected Result**:
- Accent frequency restored correctly (880 Hz)
- Regular frequency restored correctly (440 Hz)
- Both fields show correct values in UI

**Status**: [ ] Pass [ ] Fail

---

#### TC-4.2: Autosave Works
**Priority**: HIGH  
**Description**: Verify autosave includes new features

**Steps**:
1. Make changes (add layers, set accent freq, etc.)
2. Close app (don't manually save)
3. Reopen app

**Expected Result**:
- All changes restored from autosave
- Accent frequencies preserved
- Flash colors auto-generated if needed
- No data loss

**Status**: [ ] Pass [ ] Fail

---

### 5. Backwards Compatibility

#### TC-5.1: Load Old Patterns
**Priority**: CRITICAL  
**Description**: Verify old saved patterns still load

**Steps**:
1. Load a pattern saved before these changes (without accent_freq field)
2. Observe behavior

**Expected Result**:
- Pattern loads successfully
- Missing accent_freq defaults to regular freq
- No errors or crashes
- All other fields load correctly
- Can edit and save again with new format

**Status**: [ ] Pass [ ] Fail

---

## Integration Testing

### IT-1: All Features Together
**Priority**: CRITICAL  
**Description**: Test all new features in combination

**Steps**:
1. Create complex pattern with multiple layers
2. Set different accent frequencies on tone layers
3. Add and remove layers while playing
4. Change colors and observe auto-generated flash colors
5. Test with various subdivisions (including 3)
6. Save and reload

**Expected Result**:
- All features work together smoothly
- No conflicts or unexpected behavior
- Performance remains good
- UI remains responsive

**Status**: [ ] Pass [ ] Fail

---

## Regression Testing

### RT-1: Existing Features Unchanged
**Priority**: HIGH  
**Description**: Verify no regression in existing functionality

**Features to verify**:
- [ ] BPM control works
- [ ] Master volume works
- [ ] Drum mode works
- [ ] MP3 tick mode works
- [ ] Save/Load works
- [ ] NEW button works
- [ ] Multiple layers work
- [ ] Accent volume control works
- [ ] Visual flashing works
- [ ] Timing accuracy maintained

**Status**: [ ] Pass [ ] Fail

---

## Test Summary

**Date**: ________________  
**Tester**: ________________  
**Device**: ________________  
**Android Version**: ________________  
**Total Tests**: 19 test cases  
**Passed**: ___ / 19  
**Failed**: ___ / 19  
**Critical Issues**: ___  
**Approved**: YES / NO

## Notes

Additional observations:
```
[Space for notes]
```

## Known Issues

None expected. Changes are additive and backwards compatible.

## Recommendations

Based on testing results:
```
[Recommendations]
```
