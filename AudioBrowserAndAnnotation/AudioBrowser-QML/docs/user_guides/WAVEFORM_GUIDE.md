# Waveform Display - User Guide

This guide explains how to use the waveform visualization features in AudioBrowser QML (Phase 2).

---

## Overview

The waveform display provides visual representation of audio files, making it easy to:
- Navigate through audio tracks visually
- Seek to specific positions by clicking
- Zoom in for detailed view
- Track playback position in real-time

---

## Accessing Waveform Display

1. Launch the AudioBrowser QML application
2. Navigate to the **Annotations** tab
3. Select an audio file from the Library tab (it will play)
4. The waveform will automatically generate and display

---

## Features

### Automatic Generation

When you select an audio file:
1. The waveform is automatically generated in the background
2. A loading indicator shows progress
3. Once complete, the waveform appears
4. Generated waveforms are cached for instant loading next time

### Click-to-Seek

Click anywhere on the waveform to:
- Jump to that position in the audio
- Audio playback will seek to the clicked position
- Works during playback or when paused

### Playback Position

A red vertical line (playhead) shows:
- Current playback position
- Updates in real-time during playback
- Moves smoothly across the waveform

### Zoom Controls

Located in the toolbar above the waveform:

- **− (Minus)**: Zoom out
- **+ (Plus)**: Zoom in
- **Reset**: Return to 100% zoom
- **Percentage Display**: Shows current zoom level (100%-1000%)

**Zoom Levels**:
- 100%: Normal view, entire waveform visible
- 150%, 225%, 337%, etc.: Progressive zoom levels
- 1000%: Maximum zoom (10x)

**Navigation When Zoomed**:
- Horizontal scrollbar appears automatically
- Drag scrollbar to navigate
- Click-to-seek still works in zoomed view

### Manual Generation

If auto-generation is disabled or fails:
1. Click the **Generate** button in the toolbar
2. Progress indicator shows generation status
3. Waveform appears when complete

---

## Toolbar Controls

```
Waveform Display | Zoom: − [100%] + Reset | 🔧 Generate | Current: filename.wav
```

**Elements**:
- **Title**: "Waveform Display" label
- **Zoom Controls**: Zoom in/out/reset with percentage
- **Generate Button**: Manual waveform generation
- **Current File**: Shows currently loaded file name

---

## States and Indicators

### Loading State

When generating a waveform:
```
┌─────────────────────────────────┐
│         [Spinner Icon]          │
│   Generating waveform...        │
│   [Progress Bar: 45%]           │
└─────────────────────────────────┘
```

### Error State

If generation fails:
```
┌─────────────────────────────────┐
│            ⚠                    │
│   Error generating waveform     │
│   [Error Message]               │
└─────────────────────────────────┘
```

Common errors:
- File not found
- Unsupported format
- Corrupted audio file
- Missing codecs (for MP3)

### Empty State

When no file is selected:
```
┌─────────────────────────────────┐
│            📊                   │
│   No audio file selected        │
│   Select an audio file to       │
│   view its waveform             │
└─────────────────────────────────┘
```

---

## Supported Audio Formats

### Native Support

- **.wav, .wave**: Full native support
  - No additional dependencies needed
  - Fast loading and generation
  - Best performance

### Optional Support

- **.mp3**: Requires pydub and FFmpeg
  - Install: `pip install pydub`
  - Requires FFmpeg installed on system
  - Slightly slower than WAV

---

## Keyboard Shortcuts

The following keyboard shortcuts work with waveform:

- **Space**: Toggle play/pause
- **Escape**: Stop playback
- **Ctrl+1**: Switch to Library tab
- **Ctrl+2**: Switch to Annotations tab (waveform view)

---

## Caching System

### How Caching Works

1. When a waveform is generated:
   - Peak data is saved to `.waveform_cache.json`
   - File signature (size + modification time) is stored
   - Next load is instant

2. Cache validation:
   - Checks if file was modified
   - Regenerates if file changed
   - Automatic cache cleanup

3. Cache location:
   - Same directory as audio files
   - One cache file per directory
   - JSON format for portability

### Cache Management

**Viewing Cache**:
```bash
# Cache file in each directory
cat .waveform_cache.json
```

**Clearing Cache**:
```bash
# Delete cache file to regenerate all waveforms
rm .waveform_cache.json
```

**Cache Size**:
- ~2-5 KB per audio file
- Minimal storage impact
- Significantly faster than regenerating

---

## Performance Tips

### For Best Performance

1. **Use WAV files**: Fastest generation
2. **Enable caching**: First load slow, subsequent loads instant
3. **Avoid very long files**: >1 hour may be slow
4. **Install numpy**: `pip install numpy` for 10-100x speedup

### Expected Generation Times

| File Size | WAV (numpy) | WAV (pure Python) | MP3 (with pydub) |
|-----------|-------------|-------------------|------------------|
| 3 MB      | <1 second   | 2-3 seconds      | 1-2 seconds      |
| 30 MB     | 1-2 seconds | 5-10 seconds     | 3-5 seconds      |
| 100 MB    | 3-5 seconds | 15-30 seconds    | 10-15 seconds    |

*Times are approximate and depend on system performance*

### Memory Usage

- Peak data cached in RAM: ~1-2 MB per file
- Waveform rendering: Minimal GPU usage
- Multiple files: Memory grows linearly

---

## Troubleshooting

### Waveform Not Generating

**Problem**: No waveform appears after selecting file

**Solutions**:
1. Check that file is a supported format (WAV or MP3)
2. Try clicking the "Generate" button manually
3. Check for error messages in the display area
4. Verify file is not corrupted

### Click-to-Seek Not Working

**Problem**: Clicking waveform doesn't seek

**Solutions**:
1. Ensure audio file is loaded
2. Check that playback is not stopped
3. Try playing the file first, then clicking
4. Verify waveform has finished generating

### Slow Generation

**Problem**: Waveform takes a long time to generate

**Solutions**:
1. Install numpy: `pip install numpy`
2. Use WAV files instead of MP3
3. Wait for generation to complete (check progress bar)
4. Close other applications to free resources

### MP3 Files Not Working

**Problem**: Error when loading MP3 files, or MP3 playback works but waveforms don't generate

**Important Note**: Qt Multimedia has built-in FFmpeg for audio *playback*, but **waveform generation requires a separate FFmpeg installation** that pydub can access.

**Solutions**:
1. Install pydub: `pip install pydub`
2. Install FFmpeg on your system:
   - **Windows**: `winget install ffmpeg` (recommended) or download from ffmpeg.org
   - **Linux**: `sudo apt install ffmpeg`
   - **macOS**: `brew install ffmpeg`
3. Verify FFmpeg detection: Run `python3 test_ffmpeg_detection.py` in the AudioBrowser-QML directory
4. If the above doesn't work, convert MP3 to WAV as a workaround

### Zoom Not Smooth

**Problem**: Zoom feels jumpy or unresponsive

**Solutions**:
1. This is expected behavior (discrete zoom levels)
2. Use mouse/trackpad to scroll when zoomed
3. Try Reset button to return to 100%

---

## Tips and Tricks

### Efficient Workflow

1. **Pre-generate waveforms**: 
   - Generate all waveforms once
   - Subsequent loads are instant from cache

2. **Use zoom effectively**:
   - Start at 100% for overview
   - Zoom in for precise seeking
   - Use scrollbar to navigate

3. **Combine with playback controls**:
   - Use waveform for rough positioning
   - Use seek slider for fine-tuning
   - Use keyboard shortcuts for quick control

### Power User Features

1. **Visual Analysis**:
   - Identify quiet sections (low peaks)
   - Find loud sections (high peaks)
   - See overall audio structure

2. **Precise Navigation**:
   - Zoom to 400%+ for precise seeking
   - Useful for finding specific sections
   - Good for annotation placement

3. **Performance Monitoring**:
   - Watch progress bar for generation speed
   - Compare cached vs. non-cached load times
   - Check cache file size for disk usage

---

## Future Features (Phase 3+)

The following features are planned for future releases:

- **Annotation Markers**: Visual markers on waveform
- **Marker Dragging**: Move annotations by dragging
- **Selection Regions**: Select audio regions for clips
- **Loop Markers**: A-B loop visualization
- **Tempo Grid**: Beat markers for practice
- **Stereo Visualization**: Left/right channel display
- **Spectral View**: Frequency domain visualization
- **Waveform Export**: Save waveform as image

---

## Frequently Asked Questions

### Q: Can I use the waveform without generating it?

**A**: No, waveform must be generated from the audio file. However, once generated, it's cached for instant loading.

### Q: Does zoom affect audio quality?

**A**: No, zoom only affects the visual display. Audio playback quality is unchanged.

### Q: Can I zoom beyond 1000%?

**A**: No, 1000% (10x) is the maximum zoom level to prevent performance issues.

### Q: Why is my waveform regenerating every time?

**A**: The file may have been modified (different size or modification time). Cache is automatically invalidated for changed files.

### Q: Can I use this with large audio files (>1 GB)?

**A**: Yes, but generation may take several minutes. Consider splitting very large files for better performance.

---

## Technical Details

For developers and advanced users:

### Waveform Resolution

- **Columns**: 2000 peaks by default
- **Sampling**: Min/max amplitude per column
- **Accuracy**: Sufficient for visual representation
- **File Size**: ~8 KB per cached waveform

### Color Scheme

- **Background**: From theme (dark or light)
- **Waveform**: Primary accent color (blue)
- **Playhead**: Danger color (red)
- **Axis**: Background light color

### Backend Architecture

- **Engine**: WaveformEngine (Python/Qt)
- **View**: WaveformView (QQuickPaintedItem)
- **Display**: WaveformDisplay (QML)
- **Threading**: Worker threads for generation
- **Caching**: JSON with file signatures

---

## Getting Help

If you encounter issues:

1. Check this guide for solutions
2. Verify your audio files are valid
3. Check console output for error messages
4. Report bugs on GitHub issue tracker

---

## Version History

- **v0.2.0**: Initial waveform display implementation
  - Basic waveform rendering
  - Click-to-seek functionality
  - Zoom controls (1x-10x)
  - Caching system
  - Loading/error states

---

*Last Updated: Phase 2 Implementation*  
*For technical documentation, see PHASE_2_SUMMARY.md*
