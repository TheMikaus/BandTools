# Test Plan: Stereo Waveform View and Channel Muting

**Version:** 1.0  
**Last Updated:** 2024  
**Feature:** Automatic stereo waveform view switching and seamless channel muting

---

## Overview

This test plan validates the automatic stereo waveform view switching feature and verifies that channel muting maintains playback position correctly.

### Test Scope

- Automatic mode switching based on audio file channel count
- Stereo waveform visualization
- Manual mode toggling
- Channel muting with position preservation
- UI state consistency

### Out of Scope

- Waveform generation performance
- Audio decoding quality
- Spectrogram view compatibility (covered in TEST_PLAN_SPECTRAL_ANALYSIS.md)

---

## Test Environment

### Prerequisites

- AudioBrowser application installed
- Test audio files:
  - At least 2 stereo audio files (WAV and/or MP3)
  - At least 2 mono audio files (WAV and/or MP3)
  - Files of varying lengths (short: <1 min, medium: 1-3 min, long: >3 min)

### Setup Steps

1. Launch AudioBrowser
2. Navigate to folder containing test audio files
3. Ensure Annotations tab is visible (where waveform is displayed)

---

## Test Cases

### Category 1: Automatic Stereo Mode Switching

#### Test Case 1.1: Load Stereo File - Auto Switch to Stereo
**Objective:** Verify app automatically switches to stereo view when loading stereo files  
**Preconditions:** Currently viewing a mono file or no file loaded  

**Steps:**
1. Select a stereo audio file from the file list
2. Switch to Annotations tab (if not already there)
3. Observe waveform display
4. Check button state

**Expected Results:**
- Waveform displays in stereo mode (split into left and right channels)
- Left channel shown in top half (blue/cyan color)
- Right channel shown in bottom half (pink/magenta color)
- Stereo/Mono toggle button shows "Stereo" text
- Button is enabled

**Priority:** P0 (Critical)

---

#### Test Case 1.2: Load Mono File - Auto Switch to Mono
**Objective:** Verify app automatically switches to mono view when loading mono files  
**Preconditions:** Currently viewing a stereo file in stereo mode  

**Steps:**
1. While in stereo view mode, select a mono audio file
2. Observe waveform display
3. Check button state

**Expected Results:**
- Waveform displays in mono mode (single centered waveform)
- Single waveform shown with default wave color
- Stereo/Mono toggle button shows "Mono" text
- Button is disabled (grayed out)

**Priority:** P0 (Critical)

---

#### Test Case 1.3: Switch Between Multiple Stereo Files
**Objective:** Verify stereo mode persists when switching between stereo files  
**Preconditions:** At least 2 stereo files in folder  

**Steps:**
1. Load first stereo file (should auto-switch to stereo view)
2. Load second stereo file
3. Observe waveform display

**Expected Results:**
- Both files display in stereo mode
- No flickering or mode switching between stereo files
- Waveform data updates correctly for each file

**Priority:** P1 (High)

---

#### Test Case 1.4: Cached Waveform Data
**Objective:** Verify mode switching works with cached waveform data  
**Preconditions:** Waveform cache exists for test files  

**Steps:**
1. Load stereo file (creates cache)
2. Load mono file (creates cache)
3. Reload stereo file (uses cache)
4. Reload mono file (uses cache)

**Expected Results:**
- Mode switches correctly when loading from cache
- No delays or errors
- Cache includes both mono and stereo peak data

**Priority:** P1 (High)

---

### Category 2: Manual Mode Toggling

#### Test Case 2.1: Manual Toggle from Mono to Stereo
**Objective:** Verify manual toggle works for stereo files  
**Preconditions:** Stereo file loaded in mono view (user manually switched to mono)  

**Steps:**
1. Load stereo file (auto-switches to stereo)
2. Click toggle button to switch to mono
3. Click toggle button again to switch back to stereo

**Expected Results:**
- Button toggles between "Mono" and "Stereo" text
- Waveform updates to show selected mode
- No errors or crashes

**Priority:** P1 (High)

---

#### Test Case 2.2: Button Disabled for Mono Files
**Objective:** Verify toggle button is disabled for mono files  
**Preconditions:** Mono file loaded  

**Steps:**
1. Load mono file
2. Attempt to click toggle button

**Expected Results:**
- Toggle button is grayed out (disabled)
- Button cannot be clicked
- Tooltip may indicate "Not available for mono files"

**Priority:** P1 (High)

---

### Category 3: Channel Muting with Position Preservation

#### Test Case 3.1: Mute Channel During Playback
**Objective:** Verify channel muting maintains playback position  
**Preconditions:** Stereo file playing  

**Steps:**
1. Play stereo audio file
2. Let it play for 10-15 seconds
3. Note current playback position
4. Uncheck "Left Channel" checkbox
5. Observe playback

**Expected Results:**
- Audio continues playing from the same position
- Only right channel is now audible
- Playback doesn't restart or skip
- "Now Playing" text updates to show "(Left Muted)"
- Position slider shows same position

**Priority:** P0 (Critical)

---

#### Test Case 3.2: Toggle Multiple Times During Playback
**Objective:** Verify repeated channel muting maintains position  
**Preconditions:** Stereo file playing  

**Steps:**
1. Play stereo audio file
2. Mute left channel (wait 2 seconds)
3. Unmute left channel (wait 2 seconds)
4. Mute right channel (wait 2 seconds)
5. Unmute right channel

**Expected Results:**
- Playback continues smoothly throughout
- Position is maintained for each toggle
- No audio glitches or gaps
- "Now Playing" text updates correctly for each state

**Priority:** P1 (High)

---

#### Test Case 3.3: Mute Channel While Paused
**Objective:** Verify channel muting works when paused  
**Preconditions:** Stereo file paused at specific position  

**Steps:**
1. Play stereo file
2. Pause at 15 seconds
3. Mute left channel
4. Resume playback

**Expected Results:**
- Playback resumes from 15 seconds
- Only right channel is audible
- No position change due to muting

**Priority:** P1 (High)

---

#### Test Case 3.4: Mute Both Channels
**Objective:** Verify both channels can be muted simultaneously  
**Preconditions:** Stereo file loaded  

**Steps:**
1. Play stereo file
2. Uncheck both "Left Channel" and "Right Channel"
3. Observe playback

**Expected Results:**
- Audio continues playing (silence)
- "Now Playing" shows "(Both Muted)"
- Position continues advancing
- Can unmute channels to restore audio

**Priority:** P2 (Medium)

---

#### Test Case 3.5: Channel Checkboxes Disabled for Mono
**Objective:** Verify channel controls disabled for mono files  
**Preconditions:** Mono file loaded  

**Steps:**
1. Load mono file
2. Observe channel checkboxes

**Expected Results:**
- Both "Left Channel" and "Right Channel" checkboxes are disabled (grayed out)
- Both checkboxes are checked (cannot be unchecked)
- Tooltip may indicate "Not available for mono files"

**Priority:** P1 (High)

---

### Category 4: UI State Consistency

#### Test Case 4.1: Mode and File Selection State
**Objective:** Verify UI state updates correctly on file selection  
**Preconditions:** None  

**Steps:**
1. Load stereo file (note button state: enabled, showing "Stereo")
2. Load mono file (note button state: disabled, showing "Mono")
3. Load different stereo file
4. Return to first stereo file

**Expected Results:**
- Button state always matches file capabilities
- Mode switches automatically and consistently
- No stale UI state

**Priority:** P1 (High)

---

#### Test Case 4.2: Waveform Ready Signal
**Objective:** Verify mode switching happens after waveform is loaded  
**Preconditions:** Waveform cache cleared for test file  

**Steps:**
1. Clear waveform cache for test stereo file
2. Load stereo file
3. Observe waveform loading progress
4. Watch when mode switches to stereo

**Expected Results:**
- Waveform shows "Analyzing waveform..." initially
- Mode switches when waveform data is ready
- No errors during loading
- Smooth transition to stereo view

**Priority:** P2 (Medium)

---

#### Test Case 4.3: Error Handling
**Objective:** Verify mode switching handles errors gracefully  
**Preconditions:** Corrupted or unsupported audio file  

**Steps:**
1. Attempt to load corrupted audio file
2. Observe error handling
3. Load valid stereo file after error

**Expected Results:**
- Error displayed appropriately
- Mode switching doesn't crash app
- Recovery to normal operation with next valid file

**Priority:** P2 (Medium)

---

### Category 5: Edge Cases

#### Test Case 5.1: Very Short Stereo File
**Objective:** Verify stereo mode works with very short files  
**Preconditions:** Stereo audio file < 3 seconds  

**Steps:**
1. Load very short stereo file
2. Observe waveform
3. Play and mute channels

**Expected Results:**
- Stereo mode activates correctly
- Waveform displays properly despite short duration
- Channel muting works

**Priority:** P2 (Medium)

---

#### Test Case 5.2: Mixed Format Files
**Objective:** Verify mode switching works with different formats  
**Preconditions:** Mix of WAV and MP3 stereo files  

**Steps:**
1. Load stereo WAV file
2. Load stereo MP3 file
3. Switch back to WAV

**Expected Results:**
- Stereo mode works for both formats
- No format-specific issues
- Smooth switching between formats

**Priority:** P1 (High)

---

#### Test Case 5.3: Rapid File Switching
**Objective:** Verify mode switching handles rapid selection changes  
**Preconditions:** Multiple stereo and mono files  

**Steps:**
1. Rapidly click through files (stereo→mono→stereo→mono)
2. Observe waveform updates
3. Check for any errors or UI issues

**Expected Results:**
- App handles rapid switching gracefully
- Mode updates correctly for each file
- No crashes or frozen UI

**Priority:** P2 (Medium)

---

## Success Criteria

### Must Pass (P0)
- Test Case 1.1: Auto switch to stereo for stereo files
- Test Case 1.2: Auto switch to mono for mono files
- Test Case 3.1: Channel muting maintains playback position

### Should Pass (P1)
- All other P1 test cases
- No regressions in existing functionality

### Nice to Have (P2)
- All edge case tests pass
- Performance is acceptable

---

## Known Issues / Limitations

1. **Stereo Data Detection:** Channel count detection may require brief file inspection
2. **Cache Warmup:** First load of stereo file may take longer than subsequent loads
3. **Temporary Files:** Channel-muted files stored in `.audiobrowser_temp` directory

---

## Test Results Template

| Test Case | Status | Notes | Tester | Date |
|-----------|--------|-------|--------|------|
| 1.1 | ☐ Pass / ☐ Fail | | | |
| 1.2 | ☐ Pass / ☐ Fail | | | |
| 1.3 | ☐ Pass / ☐ Fail | | | |
| ... | | | | |

---

## Regression Testing

When testing this feature, also verify:
- Annotation markers still work correctly in stereo view
- Tempo markers display properly in both modes
- Clip selection works in stereo view
- A-B loop markers work in stereo view
- Spectrogram view compatibility (if enabled)

---

## Related Documentation

- **User Guide:** [HOWTO_NEW_FEATURES.md](../user_guides/HOWTO_NEW_FEATURES.md#stereo-waveform-view)
- **Technical Docs:** [CURRENT_ARCHITECTURE_INVENTORY.md](../technical/CURRENT_ARCHITECTURE_INVENTORY.md)
- **Changelog:** [CHANGELOG.md](../../CHANGELOG.md)

---

**End of Test Plan**
