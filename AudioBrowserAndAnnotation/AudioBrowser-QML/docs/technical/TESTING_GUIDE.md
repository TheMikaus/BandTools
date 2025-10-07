# AudioBrowser QML - Testing Guide

This guide provides instructions for testing the AudioBrowser QML application to validate Phase 1 functionality.

## Prerequisites

Before testing, ensure you have:
- Python 3.8 or higher
- PyQt6 (will be installed automatically on first run)
- Audio files (.wav or .mp3) for testing

## Quick Start

1. Navigate to the AudioBrowser-QML directory:
   ```bash
   cd AudioBrowserAndAnnotation/AudioBrowser-QML
   ```

2. Run the application:
   ```bash
   python3 main.py
   ```

3. On first run, PyQt6 dependencies will be installed automatically.

## Phase 1 Testing Checklist

### 1. Application Launch ✅

- [ ] Application window opens without errors
- [ ] Window title shows "AudioBrowser (QML) - Phase 1 Development"
- [ ] Window size is approximately 1200x800
- [ ] Dark theme is applied by default

### 2. UI Components ✅

- [ ] Toolbar visible with:
  - [ ] Application title
  - [ ] Playback controls (prev/play/stop/next buttons)
  - [ ] Seek slider
  - [ ] Volume control
  - [ ] Theme toggle button
- [ ] Tab bar visible with three tabs:
  - [ ] Library
  - [ ] Annotations
  - [ ] Clips
- [ ] Status bar visible at bottom

### 3. Theme Switching ✅

- [ ] Click "Theme" button - UI switches to light theme
- [ ] Click "Theme" button again - UI switches back to dark theme
- [ ] Press Ctrl+T - Theme toggles
- [ ] All UI components update colors correctly

### 4. Library Tab ✅

#### Directory Selection
- [ ] Directory text field is visible
- [ ] Click "Browse..." button - file picker dialog opens
- [ ] Select a directory containing audio files
- [ ] Directory path appears in text field
- [ ] File list updates with audio files

#### File List
- [ ] Files are displayed with name and size
- [ ] File sizes are formatted (e.g., "1.5 MB")
- [ ] Hover over file - background color changes
- [ ] Double-click file - playback starts

#### File Filtering
- [ ] Type text in "Filter files..." field
- [ ] File list filters to show only matching files
- [ ] Clear filter - all files appear again

### 5. Audio Playback ✅

#### Basic Playback
- [ ] Select an audio file
- [ ] Click play button (▶) - playback starts
- [ ] Play button changes to pause (⏸)
- [ ] Status bar shows "Playing"
- [ ] Status bar shows current file name

#### Playback Controls
- [ ] Click pause button (⏸) - playback pauses
- [ ] Pause button changes to play (▶)
- [ ] Click stop button (⏹) - playback stops
- [ ] Position resets to beginning

#### Seek Control
- [ ] Play an audio file
- [ ] Drag seek slider - position changes
- [ ] Time display (MM:SS) updates on left
- [ ] Duration display (MM:SS) shows on right
- [ ] Seek slider position updates during playback

#### Volume Control
- [ ] Drag volume slider - volume changes
- [ ] Volume percentage updates (0-100%)
- [ ] Volume icon visible (🔊)
- [ ] Mute at 0%, full volume at 100%

### 6. Keyboard Shortcuts ✅

#### Playback Shortcuts
- [ ] Press Space - toggles play/pause
- [ ] Press Escape - stops playback
- [ ] Press + (plus) - volume increases by 5%
- [ ] Press - (minus) - volume decreases by 5%

#### Navigation Shortcuts
- [ ] Press Ctrl+1 - switches to Library tab
- [ ] Press Ctrl+2 - switches to Annotations tab
- [ ] Press Ctrl+3 - switches to Clips tab

#### Interface Shortcuts
- [ ] Press Ctrl+T - toggles theme

### 7. Annotations Tab 🚧

- [ ] Tab displays "Annotations (Phase 2)" message
- [ ] Tab content is placeholder for future implementation

### 8. Clips Tab 🚧

- [ ] Tab displays "Clips Management (Phase 3)" message
- [ ] Tab content is placeholder for future implementation

### 9. Status Bar ✅

- [ ] Playback state shows "Ready" when stopped
- [ ] Playback state shows "Playing" during playback
- [ ] Current file name displays when file is loaded
- [ ] Phase indicator shows "Phase 1 Development"
- [ ] Theme indicator shows current theme

## Common Issues and Solutions

### Issue: Application doesn't start
**Solution**: Ensure Python 3.8+ is installed and PyQt6 dependencies are available.

### Issue: No audio playback
**Solution**: 
- Check that audio file format is supported (.wav or .mp3)
- Verify system audio is working
- Check volume slider is not at 0%

### Issue: File picker doesn't work
**Solution**: This is a known Qt limitation in some environments. Type the directory path manually instead.

### Issue: Theme doesn't switch
**Solution**: 
- Try using Ctrl+T keyboard shortcut
- Check console for QML errors

## Performance Testing

### File Loading
- [ ] Test with small directory (10 files) - loads instantly
- [ ] Test with medium directory (100 files) - loads quickly
- [ ] Test with large directory (1000+ files) - acceptable load time

### Playback Performance
- [ ] Test with small WAV file (< 5 MB) - smooth playback
- [ ] Test with large WAV file (> 50 MB) - smooth playback
- [ ] Test with MP3 file - smooth playback
- [ ] Seek operations are responsive

### UI Responsiveness
- [ ] Theme switching is instant
- [ ] Tab switching is smooth
- [ ] File filtering updates immediately
- [ ] No lag when interacting with sliders

## Test Audio Files

For comprehensive testing, use:
- Small WAV file (< 5 MB)
- Large WAV file (> 50 MB)
- MP3 file with various bitrates
- Stereo audio files
- Mono audio files

## Reporting Issues

If you encounter any issues during testing:

1. Note the exact steps to reproduce
2. Check the console output for error messages
3. Include your system information (OS, Python version, PyQt6 version)
4. Document expected vs. actual behavior

## Advanced Testing (Optional)

### Stress Testing
- [ ] Load directory with 1000+ files
- [ ] Switch files rapidly during playback
- [ ] Toggle theme repeatedly
- [ ] Seek rapidly during playback

### Edge Cases
- [ ] Empty directory
- [ ] Directory with no audio files
- [ ] Invalid directory path
- [ ] Audio file that fails to load
- [ ] Very short audio file (< 1 second)
- [ ] Very long audio file (> 1 hour)

## Test Results Template

```
Date: YYYY-MM-DD
Tester: [Name]
System: [OS] [Version]
Python: [Version]
PyQt6: [Version]

Results:
- Application Launch: [ ] Pass [ ] Fail
- UI Components: [ ] Pass [ ] Fail
- Theme Switching: [ ] Pass [ ] Fail
- Library Tab: [ ] Pass [ ] Fail
- Audio Playback: [ ] Pass [ ] Fail
- Keyboard Shortcuts: [ ] Pass [ ] Fail
- Status Bar: [ ] Pass [ ] Fail

Overall: [ ] Pass [ ] Fail

Notes:
[Any issues or observations]
```

## Next Steps After Testing

Once Phase 1 testing is complete:
1. Document any bugs or issues found
2. Verify all keyboard shortcuts work
3. Confirm playback controls are responsive
4. Validate theme switching
5. Report results for Phase 2 planning

---

**Phase 1 Status**: 95% Complete (Pending Real-World Testing)  
**Last Updated**: 2024
