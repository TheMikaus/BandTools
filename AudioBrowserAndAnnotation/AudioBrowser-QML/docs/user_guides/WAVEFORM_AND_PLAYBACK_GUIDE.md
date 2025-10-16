# Using Waveform Display and Playback

## Overview
AudioBrowserQML provides powerful waveform visualization and audio playback features to help you work with your audio files efficiently.

## Waveform Display

### What is a Waveform?
A waveform is a visual representation of your audio file showing the amplitude (volume) over time. It helps you:
- Quickly identify loud and quiet sections
- Navigate to specific parts of the audio
- Visualize annotation markers and clip boundaries
- See the overall structure of your recording

### Viewing Waveforms

1. **Automatic Generation**: When you select an audio file in the Library tab, the waveform is automatically generated
2. **First-Time Generation**: The first time you view a file, waveform generation may take a few seconds
3. **Cached Waveforms**: Once generated, waveforms are cached and load instantly next time
4. **Switching Tabs**: Switch to the Annotations tab to see the full waveform display

### Waveform Features

#### Visual Elements
- **Blue Waveform**: Shows the audio amplitude (volume) over time
- **Red Playhead**: Vertical line showing current playback position
- **Center Axis**: Gray horizontal line at zero amplitude
- **Measure Markers**: Dashed vertical lines (if BPM is detected) showing musical measures

#### Interacting with Waveforms
- **Click to Seek**: Click anywhere on the waveform to jump to that position
- **Annotation Markers**: See and click markers for annotations you've added
- **Clip Markers**: See highlighted regions for defined clips
- **Zoom Controls**: Use zoom buttons to zoom in/out on the waveform (if available)

## Audio Playback

### Playing Audio Files

There are several ways to play an audio file:

1. **Single Click** (Library Tab):
   - Click once on any file in the file list
   - Playback starts automatically

2. **Double Click** (Library Tab):
   - Double-click on any file
   - Playback starts and the Annotations tab opens

3. **Context Menu** (Library Tab):
   - Right-click on a file
   - Select "Play" from the menu

4. **Playback Controls**:
   - Use the play/pause button (▶/⏸) in the playback controls bar
   - Press spacebar for play/pause (keyboard shortcut)

### Playback Controls

The playback control bar includes:

#### Transport Controls
- **Play/Pause (▶/⏸)**: Start or pause playback
- **Stop (⏹)**: Stop playback and return to beginning
- **Previous/Next (⏮/⏭)**: Navigate between files (when enabled)

#### Position Controls
- **Time Display**: Shows current position (MM:SS)
- **Seek Slider**: Drag to jump to any position
- **Duration Display**: Shows total file length (MM:SS)

#### Audio Controls
- **Volume Slider**: Adjust playback volume (0-100%)
- **Channel Mode**: Select Stereo, Mono, Left, or Right channel

### Playback Features

#### Smooth Position Tracking
The playback position is updated 20 times per second for smooth visual feedback:
- Watch the red playhead move across the waveform
- See the position time update in real-time
- Seek slider follows playback automatically

#### Clip Playback
When working with clips (see Clips tab):
- Play specific sections of your audio
- Loop clips for practice
- Jump between clip boundaries

#### Speed Control
Adjust playback speed (if available):
- Slow down for detailed listening
- Speed up for quick review
- Pitch is maintained at different speeds

## Troubleshooting

### Waveform Not Appearing

If the waveform doesn't appear:
1. **Check File Format**: Ensure your file is a supported format (WAV, MP3)
2. **Wait for Generation**: First-time generation may take 5-30 seconds
3. **Check Error Messages**: Look for error messages in the waveform area
4. **File Accessibility**: Ensure the file exists and is readable

### Playback Not Starting

If playback doesn't start:
1. **Check File Selection**: Make sure a file is selected (highlighted)
2. **Audio Output**: Check that your audio device is working
3. **File Format**: Ensure the file format is supported
4. **Volume Level**: Check that volume is not muted or at zero
5. **Error Messages**: Look for error notifications

### Performance Issues

If waveforms are slow to generate:
1. **Large Files**: Very large files (>1 hour) take longer to process
2. **MP3 Files**: MP3 files require FFmpeg and may be slower than WAV
3. **Disk Speed**: Slow hard drives can affect generation time
4. **First Time**: Remember that waveforms are cached after first generation

## Tips and Best Practices

### Efficient Workflow
1. **Pre-generate Waveforms**: Open files once to cache waveforms for future use
2. **Use WAV Files**: WAV files generate waveforms faster than compressed formats
3. **Clear Cache**: If waveforms look wrong, use Settings → Clear Waveform Cache

### Navigation
1. **Click to Jump**: Clicking on the waveform is the fastest way to navigate
2. **Use Annotations**: Add annotations at important points for quick navigation
3. **Measure Markers**: If BPM is detected, use measure markers to navigate musically

### Organization
1. **Mark Best Takes**: Use best take indicators to mark your favorite recordings
2. **Create Clips**: Define clips for sections you want to practice or loop
3. **Add Notes**: Use annotations to document what happens at different times

## Keyboard Shortcuts

Common shortcuts for playback:
- **Spacebar**: Play/Pause
- **Home**: Jump to beginning
- **End**: Jump to end
- **Left/Right Arrow**: Skip backward/forward (if enabled)

(Note: Check the Keyboard Shortcuts dialog in the application for a complete list)

## Related Features

- **Annotations**: Add timestamped notes and markers (see Annotations tab)
- **Clips**: Define and play specific regions (see Clips tab)
- **Tempo Detection**: Automatic BPM detection shows measure markers
- **Best Takes**: Mark your best recordings for easy identification

## Getting Help

If you continue to experience issues:
1. Check the application logs (View → Logs menu)
2. Consult the technical documentation
3. Report issues with specific file formats to the development team
