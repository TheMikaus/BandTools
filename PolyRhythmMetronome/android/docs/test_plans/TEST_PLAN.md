# Test Plan - PolyRhythmMetronome Android

## Overview

This document outlines the testing strategy for the Android version of PolyRhythmMetronome.

**Target Device**: Kindle Fire HD 10  
**Minimum API**: Android 5.0 (API 21)  
**Target API**: Android 12 (API 31)

## Test Categories

### 1. Installation Tests

#### 1.1 Fresh Installation
- [ ] APK installs successfully on Kindle Fire HD 10
- [ ] APK installs on standard Android device (API 21)
- [ ] APK installs on newer Android device (API 31+)
- [ ] App icon appears in app drawer
- [ ] App launches on first run
- [ ] Permissions dialog appears on first run

#### 1.2 Upgrade Installation
- [ ] Upgrade from previous version preserves settings
- [ ] Upgrade from previous version preserves saved files
- [ ] No data loss during upgrade

#### 1.3 Uninstallation
- [ ] App uninstalls cleanly
- [ ] Private data is removed (optional test)

### 2. UI Tests

#### 2.1 Layout and Display
- [ ] All UI elements visible on Kindle Fire HD 10 (1920x1200)
- [ ] No text cutoff or overlapping elements
- [ ] Touch targets are at least 48dp
- [ ] Proper spacing between elements
- [ ] Colors have sufficient contrast
- [ ] Portrait orientation displays correctly
- [ ] Font sizes are readable

#### 2.2 Touch Interaction
- [ ] All buttons respond to touch
- [ ] Sliders can be dragged smoothly
- [ ] Toggle buttons change state correctly
- [ ] Text input fields accept input
- [ ] Spinners open and close properly
- [ ] No accidental double-taps required

#### 2.3 Visual Feedback
- [ ] Beat indicators (●) flash on left side
- [ ] Beat indicators (●) flash on right side
- [ ] Flash timing matches audio
- [ ] Flash duration is appropriate (120ms)
- [ ] PLAY button changes to STOP when playing
- [ ] STOP button changes to PLAY when stopped
- [ ] Button colors change appropriately

### 3. Audio Tests

#### 3.1 Basic Playback
- [ ] Audio plays when PLAY is pressed
- [ ] Audio stops when STOP is pressed
- [ ] Left ear audio plays in left channel only
- [ ] Right ear audio plays in right channel only
- [ ] No audio when ear is MUTED
- [ ] Audio resumes when ear is UNMUTED

#### 3.2 Tone Generation
- [ ] Default frequencies (880 Hz, 440 Hz) sound correct
- [ ] Custom frequencies work (test 220, 1760 Hz)
- [ ] Volume slider affects loudness
- [ ] Volume can be set to 0 (silent)
- [ ] Volume can be increased above 1.0
- [ ] No distortion at high volumes

#### 3.3 Timing and Rhythm
- [ ] BPM 60: One click per second (verified with stopwatch)
- [ ] BPM 120: Two clicks per second
- [ ] BPM 180: Three clicks per second
- [ ] Subdivisions produce correct click count
- [ ] Left and right stay synchronized
- [ ] Polyrhythms sound correct (3:4, 5:4)
- [ ] No drift over extended playback (5+ minutes)

#### 3.4 Audio Latency
- [ ] Initial start latency is acceptable (<100ms)
- [ ] No audio stuttering during playback
- [ ] No clicks or pops between beats
- [ ] Visual indicators match audio timing

### 4. Control Tests

#### 4.1 BPM Control
- [ ] Slider adjusts BPM from 40 to 240
- [ ] BPM value label updates immediately
- [ ] Preset buttons set correct BPM (60, 80, 100, 120, 140, 160, 180, 200)
- [ ] BPM changes apply immediately when playing
- [ ] BPM persists after restart

#### 4.2 Layer Controls (Left)
- [ ] MUTE toggle works
- [ ] Subdivision spinner changes values (1, 2, 4, 8, 16)
- [ ] Frequency input accepts valid Hz values
- [ ] Volume slider adjusts level
- [ ] Changes apply immediately when playing

#### 4.3 Layer Controls (Right)
- [ ] MUTE toggle works
- [ ] Subdivision spinner changes values
- [ ] Frequency input accepts valid Hz values
- [ ] Volume slider adjusts level
- [ ] Changes apply immediately when playing

#### 4.4 Play/Stop Control
- [ ] PLAY starts metronome
- [ ] STOP stops metronome
- [ ] Button text changes appropriately
- [ ] Button color changes (green/red)
- [ ] State persists through screen rotation (if supported)

### 5. File Operations

#### 5.1 Auto-save
- [ ] Settings auto-save on changes
- [ ] Auto-save file created on first run
- [ ] Settings restored on app restart
- [ ] Auto-save doesn't interfere with performance

#### 5.2 Manual Save
- [ ] SAVE button opens dialog
- [ ] Can enter filename
- [ ] File saves successfully
- [ ] Success message appears
- [ ] File can be found in storage
- [ ] JSON format is valid

#### 5.3 Manual Load
- [ ] LOAD button opens dialog
- [ ] Can enter filename
- [ ] File loads successfully
- [ ] Settings restore correctly
- [ ] Success message appears
- [ ] Error message for missing file

#### 5.4 File Format
- [ ] JSON files are human-readable
- [ ] All settings saved correctly
- [ ] No data corruption
- [ ] Compatible with desktop format (partial)

### 6. Error Handling

#### 6.1 Invalid Input
- [ ] Invalid frequency values handled gracefully
- [ ] Non-numeric text in frequency field handled
- [ ] Empty filename handled on save/load
- [ ] Missing file handled on load

#### 6.2 Audio Errors
- [ ] Audio device busy: Error message shown
- [ ] No audio hardware: Error message shown
- [ ] App doesn't crash on audio failure

#### 6.3 Storage Errors
- [ ] No storage permission: Appropriate message
- [ ] Insufficient storage: Error message
- [ ] Write failure handled gracefully

### 7. Performance Tests

#### 7.1 Resource Usage
- [ ] CPU usage acceptable during playback (<20%)
- [ ] Memory usage reasonable (<100MB)
- [ ] Battery drain acceptable
- [ ] No memory leaks over extended use

#### 7.2 Responsiveness
- [ ] UI remains responsive during playback
- [ ] No lag when adjusting controls
- [ ] Smooth slider movement
- [ ] Quick app launch time (<2 seconds)

#### 7.3 Stress Tests
- [ ] Playback for 1 hour: No issues
- [ ] Rapid BPM changes: No crashes
- [ ] Rapid subdivision changes: No crashes
- [ ] Multiple save/load cycles: No corruption

### 8. Platform-Specific Tests

#### 8.1 Kindle Fire HD 10
- [ ] App works on Fire OS 7
- [ ] App works on Fire OS 8
- [ ] Audio plays through device speakers
- [ ] Audio plays through Bluetooth headphones
- [ ] Volume buttons affect app volume
- [ ] Fire-specific UI elements don't interfere

#### 8.2 Standard Android
- [ ] Works on Samsung devices
- [ ] Works on Google Pixel devices
- [ ] Works on various screen sizes (7", 10", phone)
- [ ] Material Design elements display correctly

### 9. Integration Tests

#### 9.1 System Integration
- [ ] Volume buttons control app volume
- [ ] Home button pauses/stops audio
- [ ] Notification shade doesn't interfere
- [ ] Other apps can play audio simultaneously (if supported)
- [ ] Bluetooth audio works
- [ ] Wired headphones work

#### 9.2 Background Behavior
- [ ] App stops when backgrounded
- [ ] App resumes state when foregrounded
- [ ] No background audio (expected behavior)
- [ ] Settings preserved during background

### 10. Compatibility Tests

#### 10.1 Android Versions
- [ ] Android 5.0 (API 21)
- [ ] Android 6.0 (API 23)
- [ ] Android 7.0 (API 24)
- [ ] Android 8.0 (API 26)
- [ ] Android 9.0 (API 28)
- [ ] Android 10 (API 29)
- [ ] Android 11 (API 30)
- [ ] Android 12 (API 31)
- [ ] Android 13 (API 33)

#### 10.2 Screen Sizes
- [ ] 7" tablet (1024x600)
- [ ] 10" tablet (1920x1200) ← Primary target
- [ ] 5" phone (1080x1920)
- [ ] 6" phone (1440x2960)

#### 10.3 Hardware Variations
- [ ] Different CPU architectures (ARM, x86)
- [ ] Low-end devices (1GB RAM)
- [ ] High-end devices (8GB+ RAM)
- [ ] Various audio hardware

## Test Execution

### Priority Levels

**P0 (Critical)**: Must pass before release
- Installation on target device
- Basic audio playback
- Core controls (BPM, play/stop)
- No crashes

**P1 (High)**: Should pass before release
- All UI elements functional
- File save/load
- All controls work correctly
- Audio quality

**P2 (Medium)**: Nice to have
- Performance optimization
- Edge case handling
- Extended stress tests

**P3 (Low)**: Future improvements
- Rare device compatibility
- Advanced features
- Minor visual issues

### Test Environment

**Primary Test Device**:
- Kindle Fire HD 10 (11th Gen)
- Fire OS 8
- Clean install

**Secondary Test Devices**:
- Android emulator (API 31)
- Physical Android device (API 28+)

### Test Data

Create test rhythm patterns:
- `test_simple.json`: BPM 120, both ears subdiv 4
- `test_polyrhythm.json`: BPM 120, left subdiv 4, right subdiv 8
- `test_extremes.json`: BPM 240, subdiv 16, high volume

### Regression Testing

Run full test suite after:
- Any code changes
- Build system updates
- Dependency updates
- Before each release

## Bug Reporting

When a test fails, document:
- Device model and OS version
- Steps to reproduce
- Expected behavior
- Actual behavior
- Screenshots/videos if applicable
- Logcat output

## Test Results

### Test Run Template

```
Date: YYYY-MM-DD
Version: 1.0.0
Device: Kindle Fire HD 10 (11th Gen)
OS: Fire OS 8

[P0] Installation: PASS
[P0] Basic Playback: PASS
[P0] Core Controls: PASS
[P1] UI Elements: PASS
[P1] File Operations: PASS
[P2] Performance: PASS

Total: X/Y tests passed
Critical Issues: 0
Major Issues: 0
Minor Issues: 0
```

## Automation Potential

Future automation candidates:
- UI interaction tests (using Appium)
- Audio timing verification
- File operation tests
- Regression test suite
- Performance monitoring

## Sign-off

**Tester**: ________________  
**Date**: ________________  
**Approved for Release**: YES / NO  
**Notes**: ________________
