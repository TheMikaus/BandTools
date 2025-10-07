# Spectrogram Feature User Guide

**Feature**: Spectrogram Overlay Visualization  
**Version**: AudioBrowser-QML Phase 9  
**Date**: January 2025

---

## Overview

The Spectrogram feature provides frequency analysis visualization for audio files. Instead of viewing just the amplitude over time (waveform), you can now see the frequency content over time, helping you understand the tonal characteristics of your recordings.

---

## What is a Spectrogram?

A spectrogram is a visual representation of the frequency spectrum of a sound signal as it varies with time. It shows:

- **Horizontal Axis**: Time (same as waveform)
- **Vertical Axis**: Frequency (low frequencies at bottom, high frequencies at top)
- **Color**: Magnitude/intensity of each frequency (Blue = quiet, Red = loud)

### Color Mapping

- **Blue**: Low magnitude (quiet/low energy frequencies)
- **Green**: Medium magnitude
- **Yellow**: Higher magnitude
- **Red**: High magnitude (loud/high energy frequencies)

---

## How to Use

### 1. Enable Spectrogram View

1. Open an audio file in AudioBrowser-QML
2. Navigate to the **Annotations** tab
3. In the toolbar at the top, find the **"Spectrogram"** checkbox
4. Check the box to enable spectrogram view

**Note**: The first time you enable spectrogram for a file, it will compute the spectral data (takes 1-10 seconds depending on file length). After that, it's instant!

### 2. Toggle Back to Waveform

Simply uncheck the **"Spectrogram"** checkbox to return to normal waveform view.

### 3. Use with Playback

- Click anywhere in the spectrogram to seek to that position
- The red playhead line shows current playback position
- Press Space or use playback controls as normal

### 4. Use with Tempo Markers

If you've set a BPM for the track:
- Measure markers (gray dashed lines) appear on the spectrogram
- Measure numbers (M4, M8, M12...) are visible
- Helps align frequency analysis with musical structure

### 5. Zoom Controls

- Use **Zoom In** (+) and **Zoom Out** (−) buttons to zoom horizontally
- Scroll horizontally when zoomed in
- Zoom works the same in both waveform and spectrogram modes

---

## Use Cases

### 1. Identify EQ Problems

**Problem**: Track sounds muddy or too bright  
**Solution**: 
- Enable spectrogram view
- Look for frequency ranges that are too prominent (lots of red/yellow)
- Low frequencies (bottom): If too much red = too much bass
- High frequencies (top): If too much red = too harsh/bright

### 2. Compare Takes

**Problem**: Need to choose the best take based on tone  
**Solution**:
- Open two takes of the same song
- Toggle spectrogram view on both
- Compare frequency content visually
- Choose the take with better tonal balance

### 3. Analyze Instruments

**Problem**: Want to understand instrument frequency ranges  
**Solution**:
- Load recording with isolated instrument
- Enable spectrogram view
- See where instrument frequencies are concentrated
- Example: Bass guitar = lots of red at bottom, Cymbals = lots of red at top

### 4. Identify Recording Issues

**Problem**: Strange sounds or artifacts in recording  
**Solution**:
- Enable spectrogram view
- Look for unusual patterns or unexpected frequency content
- Example: Hum at 60 Hz shows as horizontal red line at very bottom
- Example: Clipping shows as bright red across all frequencies

### 5. Educational Tool

**Problem**: Want to learn about frequency content of music  
**Solution**:
- Load various recordings (different genres, instruments)
- Toggle spectrogram view
- Observe patterns and frequency distributions
- Learn which instruments occupy which frequency ranges

---

## Tips and Tricks

### Performance

- **First Load**: Computing spectrogram takes 1-10 seconds (depending on file length)
- **Subsequent Toggles**: Instant (spectrogram is cached)
- **Memory**: Each spectrogram uses ~2-5 MB of memory
- **Recommendation**: Enable spectrogram only when needed for analysis

### Frequency Range

- **Range**: 60-8000 Hz (musical range)
- **Low Frequencies** (60-250 Hz): Bass, kick drum, low toms
- **Mid Frequencies** (250-2000 Hz): Most instruments, vocals
- **High Frequencies** (2000-8000 Hz): Cymbals, hi-hats, harmonics, brightness

### Log-Spaced Frequency

The frequency axis uses log spacing (like musical scales):
- More detail in bass/mid frequencies
- Less detail in high frequencies
- Matches human hearing perception

### Limitations

1. **Mono Analysis**: Stereo files are analyzed using left channel only
2. **Fixed Parameters**: FFT parameters are not user-configurable
3. **No Real-Time**: Spectrogram computed from file, not updated during playback
4. **NumPy Required**: Feature requires NumPy to be installed

---

## Troubleshooting

### "Spectrogram checkbox is grayed out"

**Problem**: Checkbox is disabled  
**Solution**: 
- Ensure NumPy is installed: `pip install numpy`
- Restart AudioBrowser-QML

### "Spectrogram shows mostly blue"

**Problem**: Very little red/yellow/green, mostly blue  
**Solution**: 
- This is normal for quiet recordings
- Recording may have low overall volume
- Try adjusting playback volume to hear it better

### "Spectrogram takes a long time to compute"

**Problem**: More than 10 seconds for a file  
**Solution**:
- This is expected for very long files (> 10 minutes)
- Consider splitting file into shorter segments
- Computation is one-time per file (cached after first time)

### "Spectrogram looks different from waveform"

**Problem**: Expected to see similar pattern to waveform  
**Solution**:
- This is normal! Spectrogram shows frequency, not amplitude
- Waveform shows amplitude over time
- Spectrogram shows frequency over time
- They represent different aspects of the audio

---

## Keyboard Shortcuts

Currently, there is no dedicated keyboard shortcut for toggling spectrogram. Use the mouse to check/uncheck the "Spectrogram" checkbox in the Annotations tab toolbar.

**Future Enhancement**: Consider adding Ctrl+Shift+P for toggle.

---

## Technical Details

For users interested in the technical implementation:

### STFT Parameters

- **FFT Size**: 2048 samples
- **Hop Length**: 512 samples (25% overlap)
- **Window**: Hanning window
- **Frequency Bins**: 128 (log-spaced)
- **Frequency Range**: 60-8000 Hz

### Computation Algorithm

1. Load audio samples from file
2. Apply Short-Time Fourier Transform (STFT) with Hanning window
3. Compute magnitude spectrum for each time frame
4. Map to log-spaced frequency bins (60-8000 Hz)
5. Apply log compression for better visualization
6. Normalize to 0-1 range
7. Cache result for instant toggling

### Color Mapping Algorithm

```
magnitude < 0.33: Blue → Green
magnitude 0.33-0.66: Green → Yellow
magnitude > 0.66: Yellow → Red
```

---

## Comparison with Waveform View

| Feature | Waveform | Spectrogram |
|---------|----------|-------------|
| **Shows** | Amplitude over time | Frequency over time |
| **Y-Axis** | Amplitude (volume) | Frequency (pitch) |
| **Color** | Single color (blue) | Gradient (blue-green-yellow-red) |
| **Best For** | Timing, volume, transients | Tone, frequency content, EQ issues |
| **Use Case** | Editing, timing, structure | Analysis, mixing, mastering |

**Tip**: Use both! Toggle between them to get complete understanding of your audio.

---

## Examples

### Example 1: Clean Guitar Recording

**Spectrogram Appearance**:
- Low frequencies (60-250 Hz): Some yellow/green (fundamental notes)
- Mid frequencies (250-2000 Hz): Lots of yellow/red (guitar body, harmonics)
- High frequencies (2000-8000 Hz): Some green/yellow (strings, pick attack)

### Example 2: Full Band Mix

**Spectrogram Appearance**:
- Low frequencies: Lots of red/yellow (bass, kick drum)
- Mid frequencies: Very busy, lots of colors (guitars, vocals, snare)
- High frequencies: Moderate red/yellow (cymbals, hi-hats, brightness)

### Example 3: Vocal Recording

**Spectrogram Appearance**:
- Low frequencies: Minimal (unless male vocal with low voice)
- Mid frequencies: Strong red/yellow bands (vocal formants)
- High frequencies: Some green/yellow (sibilance, air)
- Horizontal bands correspond to sung notes

---

## Future Enhancements

Planned improvements to the spectrogram feature:

1. **Opacity Slider**: Overlay spectrogram on waveform with adjustable opacity
2. **Stereo Spectrogram**: Separate visualizations for left/right channels
3. **Real-Time Updates**: Update spectrogram during playback (advanced)
4. **Export Spectrogram**: Save spectrogram as PNG image
5. **Adjustable Parameters**: User-configurable FFT size and frequency range
6. **Chromagram View**: Pitch class visualization (12 semitone classes)
7. **Mel-Spectrogram**: Perceptual frequency scale matching human hearing

---

## Feedback and Support

If you have questions or suggestions about the spectrogram feature:

1. Check this user guide first
2. Review ISSUE_7_IMPLEMENTATION_SUMMARY.md for technical details
3. Report issues or request features on GitHub

---

**Document Version**: 1.0  
**Last Updated**: January 2025  
**Author**: AudioBrowser-QML Development Team
