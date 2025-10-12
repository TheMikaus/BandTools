# Bug Fix v1.5 - Test Plan

## Overview

**Version**: 1.5.0  
**Issue**: Tone feature doesn't work (drums do though)  
**Fix**: Corrected AudioTrack buffer size calculation for stereo audio

## Root Cause

The buffer size calculation in `_play_sound()` method used `len(audio_int16) * 2` which only counted the number of rows (samples) instead of total elements. For stereo audio with shape `(n, 2)`, this resulted in only half the required buffer size being allocated.

**Impact**: 
- Tones (~50ms, 2205 samples) failed to play correctly due to insufficient buffer
- Drums (~300-1200ms, 13230+ samples) still worked despite the bug due to longer duration

**Fix**: Changed to `audio_int16.size * 2` to correctly calculate total elements × 2 bytes per int16.

## Test Environment

**Primary Test**: Android device with AudioTrack support  
**Secondary Test**: Desktop testing with simpleaudio fallback  
**Verification Method**: Manual testing with audio output

## Test Cases

### 1. Tone Playback Functionality

#### TC-1.1: Basic Tone Playback
**Priority**: CRITICAL  
**Description**: Verify that tone mode now produces audible output

**Steps**:
1. Launch the app
2. Ensure default layer is in "tone" mode (should be default)
3. Verify frequency is set (e.g., 880 Hz for left, 440 Hz for right)
4. Press the PLAY button
5. Listen for audio output

**Expected Result**:
- Tone plays from device speakers/headphones
- Left channel plays 880 Hz tone
- Right channel plays 440 Hz tone
- Tone is clearly audible
- Visual flash synchronizes with audio

**Status**: [ ] Pass [ ] Fail

---

#### TC-1.2: Multiple Tone Frequencies
**Priority**: HIGH  
**Description**: Verify tones work at various frequencies

**Steps**:
1. Create/modify layer to use tone mode
2. Test with frequency 220 Hz - press PLAY
3. Change to 440 Hz - press PLAY
4. Change to 880 Hz - press PLAY
5. Change to 1760 Hz - press PLAY

**Expected Result**:
- All frequencies produce audible tones
- Pitch changes are clearly distinguishable
- No distortion or cutoff
- Visual flash remains synchronized

**Status**: [ ] Pass [ ] Fail

---

#### TC-1.3: Tone Volume Control
**Priority**: HIGH  
**Description**: Verify volume slider works with tones

**Steps**:
1. Set layer to tone mode (880 Hz)
2. Set volume to 0.0 - press PLAY
3. Set volume to 0.5 - press PLAY
4. Set volume to 1.0 - press PLAY
5. Set volume to 1.5 - press PLAY

**Expected Result**:
- Volume 0.0: Silent or very quiet
- Volume 0.5: Half loudness
- Volume 1.0: Normal loudness
- Volume 1.5: Louder (but no distortion)

**Status**: [ ] Pass [ ] Fail

---

### 2. Drum Playback Verification

#### TC-2.1: Drum Sounds Still Work
**Priority**: CRITICAL  
**Description**: Verify the fix doesn't break drum playback

**Steps**:
1. Set layer to "drum" mode
2. Select "kick" drum
3. Press PLAY
4. Repeat for: snare, hihat, crash, tom, ride

**Expected Result**:
- All drum sounds play correctly
- No regression in drum functionality
- Audio quality unchanged
- Visual flash synchronized

**Status**: [ ] Pass [ ] Fail

---

### 3. Mixed Mode Testing

#### TC-3.1: Tone and Drum Together
**Priority**: HIGH  
**Description**: Verify tones and drums can play simultaneously

**Steps**:
1. Add left layer: tone mode, 880 Hz, subdiv 4
2. Add right layer: drum mode, snare, subdiv 4
3. Press PLAY
4. Listen for both sounds

**Expected Result**:
- Tone plays in left channel
- Snare plays in right channel
- Both sounds are clearly audible
- No interference between modes
- Visual flashes work for both

**Status**: [ ] Pass [ ] Fail

---

#### TC-3.2: Multiple Layers Mixed
**Priority**: MEDIUM  
**Description**: Test with multiple tone and drum layers

**Steps**:
1. Left: 2 tone layers (440 Hz, 880 Hz) with different subdivisions
2. Right: 2 drum layers (kick, snare) with different subdivisions
3. Press PLAY

**Expected Result**:
- All 4 layers audible
- Tones and drums mix properly
- No audio dropouts
- Timing remains accurate

**Status**: [ ] Pass [ ] Fail

---

### 4. Timing and Synchronization

#### TC-4.1: Tone Timing Accuracy
**Priority**: HIGH  
**Description**: Verify tone timing is accurate

**Steps**:
1. Set BPM to 60 (one beat per second)
2. Set tone layer to subdiv 4 (quarter notes)
3. Press PLAY
4. Use stopwatch/timer to verify timing

**Expected Result**:
- Exactly one tone per second
- No drift over 60 seconds
- Visual flash matches audio
- Consistent timing throughout

**Status**: [ ] Pass [ ] Fail

---

#### TC-4.2: Tone vs Drum Timing
**Priority**: MEDIUM  
**Description**: Verify tones and drums stay synchronized

**Steps**:
1. Left: tone layer, 880 Hz, subdiv 4
2. Right: drum layer, kick, subdiv 4
3. BPM 120
4. Press PLAY
5. Listen for synchronization

**Expected Result**:
- Tone and drum hit at exactly the same time
- No phase drift over 2+ minutes
- Both maintain steady timing

**Status**: [ ] Pass [ ] Fail

---

### 5. Platform-Specific Testing

#### TC-5.1: Android AudioTrack Backend
**Priority**: CRITICAL  
**Description**: Test on Android with native AudioTrack

**Steps**:
1. Deploy to Android device
2. Check logs for "Using Android AudioTrack"
3. Test tone playback (TC-1.1)
4. Test drum playback (TC-2.1)

**Expected Result**:
- AudioTrack backend loads successfully
- Both tone and drum work
- Low latency
- No audio artifacts

**Status**: [ ] Pass [ ] Fail  
**Device**: ________________  
**Android Version**: ________________

---

#### TC-5.2: Simpleaudio Backend
**Priority**: MEDIUM  
**Description**: Test on desktop/device with simpleaudio

**Steps**:
1. Run on system with simpleaudio
2. Check logs for "Using simpleaudio"
3. Test tone playback (TC-1.1)
4. Test drum playback (TC-2.1)

**Expected Result**:
- Simpleaudio backend works
- Both tone and drum functional
- Acceptable latency

**Status**: [ ] Pass [ ] Fail  
**Platform**: ________________

---

#### TC-5.3: Kivy SoundLoader Backend
**Priority**: LOW  
**Description**: Test fallback to Kivy audio

**Steps**:
1. Test on system without AudioTrack or simpleaudio
2. Check logs for "Using Kivy SoundLoader"
3. Test tone playback (TC-1.1)
4. Test drum playback (TC-2.1)

**Expected Result**:
- Kivy backend loads as fallback
- Both tone and drum work
- May have higher latency (acceptable)

**Status**: [ ] Pass [ ] Fail  
**Platform**: ________________

---

### 6. Regression Testing

#### TC-6.1: Other Features Unchanged
**Priority**: HIGH  
**Description**: Verify the fix doesn't break other functionality

**Steps**:
1. Test BPM control (slider and presets)
2. Test layer add/remove
3. Test mute buttons
4. Test save/load
5. Test NEW button

**Expected Result**:
- All features work as before
- No new bugs introduced
- UI remains responsive

**Status**: [ ] Pass [ ] Fail

---

## Performance Testing

### PT-1: CPU Usage
**Priority**: MEDIUM  
**Description**: Verify fix doesn't increase CPU usage

**Steps**:
1. Monitor CPU usage while playing tone layers
2. Compare to drum layers
3. Check for any spikes or sustained high usage

**Expected Result**:
- CPU usage similar to drum mode
- No significant increase
- Remains under 20% on target device

**Status**: [ ] Pass [ ] Fail  
**Measured CPU**: ________%

---

### PT-2: Memory Usage
**Priority**: LOW  
**Description**: Verify no memory leaks from fix

**Steps**:
1. Play tones for 5 minutes
2. Monitor memory usage
3. Stop and check for memory release

**Expected Result**:
- Memory stable during playback
- No gradual increase
- Memory released after stop

**Status**: [ ] Pass [ ] Fail  
**Peak Memory**: ________MB

---

## Code Review Checklist

- [x] Buffer size calculation uses `audio_int16.size * 2`
- [x] Works for both mono sources (tone/drum) converted to stereo
- [x] Comment explains the calculation
- [x] No changes to drum or other audio code paths
- [x] Python syntax valid
- [x] CHANGELOG.md updated
- [x] No breaking changes to API or file format

## Test Summary

**Date**: ________________  
**Tester**: ________________  
**Total Tests**: 16 test cases  
**Passed**: ___ / 16  
**Failed**: ___ / 16  
**Critical Issues**: ___  
**Approved**: YES / NO

## Notes

Additional observations or issues:
```
[Space for notes]
```

## Known Limitations

None expected. This is a surgical fix to a specific buffer calculation bug.

## Future Improvements

None required for this fix, but general audio improvements could include:
- Audio latency optimization
- Buffer size tuning for different devices
- Advanced audio mixing
