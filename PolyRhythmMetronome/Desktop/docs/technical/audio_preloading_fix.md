# Audio Pre-loading Fix for Wave/MP3 Timing Issues

## Problem Description

Wave and MP3 files were not playing on time when starting playback from a freshly opened application. The timing issues occurred because audio files were being loaded from disk during the audio callback, causing delays.

## Root Cause

The audio caching system (`WaveCache`, `Mp3TickCache`) was already implemented, but files were only loaded into cache when first accessed during playback. This meant:

1. When the audio callback requested a wave/mp3 file for the first time
2. The cache would read from disk (slow I/O operation)
3. This disk I/O happened in the audio thread/callback
4. The delay caused the audio to play late, resulting in timing problems

## Solution

Implemented pre-loading of all audio files into cache before the audio thread starts:

### Code Changes

#### 1. Added `_preload_audio_files()` Method

```python
def _preload_audio_files(self):
    """Pre-load all wave/mp3 files into cache before starting playback.
    This prevents disk I/O delays during audio callbacks that cause timing issues."""
    for lay in self.left_layers + self.right_layers:
        mode = lay.get("mode", "tone")
        try:
            if mode == "mp3_tick" and lay.get("mp3_tick"):
                # Pre-load both accent and non-accent versions
                self.mp3_ticks.get(lay["mp3_tick"], is_accent=True)
                self.mp3_ticks.get(lay["mp3_tick"], is_accent=False)
            elif mode == "file" and lay.get("wav_path"):
                # Pre-load wav file
                self.waves.get(lay["wav_path"])
        except Exception as e:
            # Log but don't fail - the error will be caught during playback
            print(f"Warning: Failed to preload audio for layer: {e}", file=sys.stderr)
```

#### 2. Modified `start()` Method

Added a call to `_preload_audio_files()` after setting up layers but before starting the audio stream:

```python
def start(self):
    # ... existing setup code ...
    self.sample_counter=0; self.active.clear()
    # Pre-load all audio files to prevent timing issues on first play
    self._preload_audio_files()
    if sd is not None:
        # ... start audio stream ...
```

## How It Works

### Before the Fix

```
User clicks Play
  → Audio thread starts
  → First audio callback
  → Needs wave file
  → Cache miss - loads from disk (SLOW)
  → Audio plays late
  → Timing problems
```

### After the Fix

```
User clicks Play
  → Pre-load all audio files
  → All files cached in memory
  → Audio thread starts
  → First audio callback
  → Needs wave file
  → Cache hit - instant retrieval
  → Audio plays on time
  → Perfect timing
```

## Benefits

1. **Eliminates First-Play Timing Issues**: All audio is ready in memory before playback
2. **No Disk I/O During Playback**: Audio callbacks are fast and deterministic
3. **Graceful Error Handling**: Failed pre-loads don't prevent playback attempt
4. **Supports All Audio Modes**:
   - MP3 tick sounds (both accent and regular)
   - Custom WAV/MP3 files
   - Tone and drum modes (already fast, no pre-load needed)

## Technical Details

### Caching System

The application uses several cache classes:

- **`ToneCache`**: Generates and caches tone frequencies
- **`WaveCache`**: Loads and caches WAV/MP3 files from disk
- **`Mp3TickCache`**: Manages MP3 tick sounds, wraps WaveCache
- **`DrumSynth`**: Generates and caches synthesized drum sounds

### Pre-loading Strategy

1. **Iterate all layers**: Both left and right ear layers
2. **Identify file-based audio**: MP3 ticks and custom WAV/MP3 files
3. **Load into cache**: Call `get()` to trigger loading
4. **Handle failures**: Log warnings but continue

### MP3 Tick Special Case

MP3 ticks can have paired files (e.g., `cowbell_1.wav`, `cowbell_2.wav`):
- File 1 is used for accented beats
- File 2 is used for regular beats

Pre-loading loads BOTH versions to ensure no delays during accent beats.

## Performance Impact

- **Startup Time**: Minimal increase (typically <100ms for a few small audio files)
- **Memory Usage**: Small increase (typical audio files are 5-50KB in memory)
- **Runtime Performance**: Significant improvement (no disk I/O during playback)

## Testing

To verify the fix works:

1. **Fresh App Test**:
   - Close the application completely
   - Open it again
   - Load a rhythm with WAV/MP3 layers
   - Click Play immediately
   - Audio should play on time from the first beat

2. **Multiple Layers Test**:
   - Add multiple layers with different audio files
   - Each should play on time without delays

3. **MP3 Tick Test**:
   - Use MP3 tick sounds
   - Verify both accented and regular beats play correctly

## Related Files

- `Poly_Rhythm_Metronome.py`: Main implementation
- `CHANGELOG.md`: User-facing documentation
- This file: Technical documentation

## Future Improvements

Possible enhancements:
- Progress indicator during pre-loading for large files
- Async pre-loading to avoid blocking UI
- Cache size limits for memory management
- Pre-loading on layer add (before play is clicked)
