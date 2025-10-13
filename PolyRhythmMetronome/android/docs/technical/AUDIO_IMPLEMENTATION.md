# Audio Implementation - Technical Documentation

## Overview
This document describes the audio playback implementation added in version 1.1.0 to fix the critical "Play button does not play audio" bug.

## Architecture

### Audio Flow
```
User presses PLAY
    ↓
MetronomeWidget.on_play_stop()
    ↓
SimpleMetronomeEngine.start()
    ↓
Thread spawned running _run()
    ↓
Loop: Check each layer's next beat time
    ↓
For each beat:
    _get_audio_data(layer) → audio samples
    _play_sound(audio, volume, channel)
    on_beat_callback() → visual flash
```

### Key Components

#### 1. SimpleMetronomeEngine
**Purpose**: Core audio timing and playback engine

**Key Methods**:
- `__init__()`: Initializes audio library (tries Android AudioTrack, then simpleaudio, then Kivy)
- `start()`: Spawns metronome thread
- `stop()`: Terminates playback
- `_run()`: Main timing loop (runs in separate thread)
- `_get_audio_data()`: Retrieves tone or drum audio samples
- `_play_sound()`: Plays audio through speakers/headphones using available backend

**Threading**:
- Uses Python threading for timing loop
- Runs in daemon thread (auto-exits on app close)
- 1ms sleep in loop to avoid busy-waiting
- Thread-safe access to RhythmState via locks

#### 2. Audio Libraries

The engine supports three audio backends with automatic fallback:

**Primary: Android AudioTrack (via pyjnius)**
- Native Android audio API
- Direct PCM buffer playback
- Lowest latency on Android devices
- Requires pyjnius (included in buildozer by default)
- Only available when running on Android platform

**Secondary: simpleaudio**
- Desktop/some Android builds
- Plays raw PCM audio buffers
- Low latency
- Simple API
- Must be pre-installed (no runtime installation)

**Fallback: Kivy SoundLoader**
- Used if neither AudioTrack nor simpleaudio available
- Higher level API
- File-based audio (writes temporary WAV files)
- Slightly higher latency due to file I/O
- Always available with Kivy

**Graceful Degradation**:
- If no audio library available, playback is skipped
- Visual feedback still works
- No crashes or errors

### Audio Generation

#### ToneGenerator
Generates pure sine wave tones:
- Configurable frequency (Hz)
- 50ms duration by default
- Applies fade in/out envelope to prevent clicks
- Caches generated tones for performance

**Formula**:
```python
tone = sin(2π × frequency × time)
envelope = fade_in × tone × fade_out
```

#### DrumSynth
Synthesizes realistic drum sounds:
- **Kick**: Frequency sweep from 120Hz to 50Hz with exponential decay
- **Snare**: Noise + 190Hz body tone
- **Hi-hat**: Short burst of filtered noise
- **Crash**: Long noise decay (1.2s)
- **Tom**: 160Hz tone with decay
- **Ride**: 900Hz ping + noise

Each drum sound uses:
- NumPy for efficient array operations
- Envelope shaping for natural decay
- Noise generation for percussion character
- Cached samples for performance

### Audio Format

**Specifications**:
- Sample Rate: 44,100 Hz (CD quality)
- Channels: 2 (stereo)
- Bit Depth: 16-bit signed integer (for playback)
- Internal: 32-bit float (for processing)

**Stereo Panning**:
```python
# Left channel
stereo = [audio_data, zeros]

# Right channel  
stereo = [zeros, audio_data]

# Center
stereo = [audio_data, audio_data]
```

### Timing System

#### Beat Calculation
```python
def calc_interval(subdiv):
    notes_per_beat = subdiv / 4.0
    return 60.0 / (bpm × notes_per_beat)
```

**Examples** (at 120 BPM):
- Subdiv 1 (whole): 2.0 seconds
- Subdiv 2 (half): 1.0 seconds
- Subdiv 4 (quarter): 0.5 seconds
- Subdiv 8 (eighth): 0.25 seconds
- Subdiv 16 (sixteenth): 0.125 seconds

#### Timing Loop
```python
start_time = time.perf_counter()
next_times = [0.0] * num_layers

while running:
    # Find next event across ALL layers
    next_event = min(next_times)
    current_time = time.perf_counter() - start_time
    
    # Smart sleep until event time
    wait = next_event - current_time
    if wait > 0.005:
        time.sleep(wait - 0.003)  # Sleep most, leave 3ms for precision
    elif wait > 0:
        time.sleep(0.0001)  # Minimal sleep for precision
    else:
        # Process all events at this time
        for i, layer in enumerate(layers):
            if abs(next_times[i] - next_event) < TOLERANCE:
                play_beat(layer)
                next_times[i] += intervals[i]
```

**Precision**:
- Uses `time.perf_counter()` for high-precision monotonic timing
- Smart sleep reduces CPU while maintaining accuracy
- Events within 0.1ms tolerance fire together
- Guarantees consistent timing regardless of layer count
- Muted layers maintain timing state to avoid drift

## Performance Considerations

### Memory Usage
- Tone cache: ~5KB per frequency
- Drum cache: ~50KB per drum type
- Total audio cache: <500KB typically
- NumPy arrays use memory-mapped operations

### CPU Usage
- Timing loop: <1% CPU (smart sleep-based scheduling)
- Audio synthesis: One-time on first use (cached)
- Playback: Handled by OS audio system
- Thread overhead: Minimal (single daemon thread)
- Optimized for minimal CPU usage while maintaining precision

### Latency
- Target: <50ms from beat time to audio output
- Factors:
  - Timing precision: ~1ms
  - Audio buffer: ~10-30ms (OS dependent)
  - Speaker/DAC: <10ms
- Total typical: 20-50ms (acceptable for metronome)

## Implementation Details

### Audio Buffer Management
```python
# Convert float32 [-1.0, 1.0] to int16 [-32767, 32767]
audio_int16 = (audio_data * 32767.0).astype(np.int16)

# Clip to prevent overflow
audio_data = np.clip(audio_data, -1.0, 1.0)
```

### Volume Control
Volume is applied in float space before conversion:
```python
audio_data = audio_data * volume
```

**Range**: 0.0 (silent) to 1.5 (150%, may clip)

### Stereo Mixing
Multiple layers in same channel:
- Played independently (not mixed in software)
- OS audio system handles mixing
- Each layer gets own play_buffer() call
- Potential for slight timing variations (<1ms)

## Error Handling

### Audio Library Not Available
```python
if self.audio_lib is None:
    return  # Skip playback, no error
```

### Playback Failures
```python
try:
    play_obj = self.sa.play_buffer(...)
except Exception as e:
    print(f"Audio playback error: {e}")
    # Continue timing loop
```

### Invalid Audio Data
- NumPy clipping prevents overflow
- Envelope ensures smooth start/stop
- Cache validation on first use

## Testing Audio System

### Unit Tests
```python
# Test tone generation
tone_gen = ToneGenerator()
audio = tone_gen.generate_beep(440.0, 50)
assert len(audio) == expected_samples

# Test drum synthesis
drum = DrumSynth()
kick = drum.get("kick")
assert kick is not None and len(kick) > 0
```

### Integration Tests
1. Create layers with different modes
2. Start engine
3. Verify audio callbacks occur at correct intervals
4. Stop engine and verify cleanup

### Manual Tests
1. **Audible Test**: Listen for correct pitch/drum
2. **Timing Test**: Tap along to verify accuracy
3. **Stereo Test**: Use headphones to verify L/R separation
4. **Volume Test**: Adjust sliders, verify levels
5. **Stress Test**: Many layers, verify no dropouts

## Known Limitations

### Current Implementation
- **No software mixing**: Each layer plays independently
- **No audio processing**: No reverb, EQ, or effects
- **Fixed sample rate**: 44.1kHz only
- **No latency compensation**: Assumes OS handles it well

### Platform-Specific
- **Android**: Variable latency by device (20-200ms)
- **Fire OS**: May have audio restrictions
- **iOS**: Not tested (Kivy compatibility issues)

## Future Enhancements

### Short Term (v1.2)
- [ ] Measure and display actual latency
- [ ] Pre-mix layers in software for better sync
- [ ] Add audio buffer size control
- [ ] Implement Kivy audio fallback

### Long Term (v2.0)
- [ ] WAV file playback support
- [ ] Audio effects (reverb, delay)
- [ ] Export to audio file
- [ ] Real-time BPM adjustment
- [ ] Swing/shuffle timing
- [ ] Audio visualization

## Debugging Audio Issues

### No Sound
1. Check `engine.audio_lib` value (should be 'android', 'simpleaudio', or 'kivy')
2. On Android: Verify pyjnius is in buildozer requirements
3. Check device volume and audio output
4. Look for playback errors in console/logcat
5. Test with simple tone layer first
6. On Android: Check app has audio permissions

### Timing Issues
1. Verify BPM is reasonable (60-200)
2. Check for high CPU usage
3. Ensure timing loop is running (check thread)
4. Test with single layer first
5. Timing is now consistent regardless of layer count (fixed in v1.4.0)

### Distortion/Clipping
1. Reduce layer volumes (<1.0)
2. Check for volume >1.5
3. Verify NumPy clipping is working
4. Test with fewer simultaneous layers

### Latency/Lag
1. Measure with visual flash sync
2. Try different audio backends
3. Close other apps using audio
4. Check device performance
5. Consider device limitations

## References

### Libraries
- [Android AudioTrack](https://developer.android.com/reference/android/media/AudioTrack) - Native Android audio
- [pyjnius](https://pyjnius.readthedocs.io/) - Python-Java bridge for Android APIs
- [simpleaudio](https://simpleaudio.readthedocs.io/) - Desktop audio playback
- [NumPy](https://numpy.org/) - Array operations
- [Kivy Audio](https://kivy.org/doc/stable/api-kivy.core.audio.html) - Fallback audio

### Audio Concepts
- [PCM Audio](https://en.wikipedia.org/wiki/Pulse-code_modulation) - Digital audio encoding
- [Audio Latency](https://en.wikipedia.org/wiki/Latency_(audio)) - Timing delays
- [Stereo Sound](https://en.wikipedia.org/wiki/Stereophonic_sound) - Multi-channel audio

### Code Examples
- See `Desktop/Poly_Rhythm_Metronome.py` for reference implementation
- Check `main.py` lines 305-420 for complete audio engine

## Changelog

### v1.4.0 (Timing and Performance Improvements)
- **Fixed**: Subdivision 3 (triplets) now have evenly spaced notes regardless of other layers
- **Improved**: Switched to `time.perf_counter()` for high-precision timing
- **Optimized**: Smart sleep algorithm reduces CPU usage while maintaining accuracy
- **Fixed**: Beats now stay on time regardless of number of layers (including muted layers)
- **Added**: Event tolerance window (0.1ms) for truly simultaneous events
- **Performance**: Timing loop only wakes when needed, reducing overhead
- **Documentation**: Updated timing implementation details

### v1.3.0 (Audio Backend Improvements)
- **Fixed**: Removed runtime auto-install of simpleaudio (not possible on Android)
- **Added**: Android AudioTrack support via pyjnius (primary backend for Android)
- **Implemented**: Kivy SoundLoader fallback with WAV file caching
- **Added**: pyjnius to buildozer requirements
- **Improved**: Three-tier audio backend system with automatic fallback
- Audio backends now try: Android AudioTrack → simpleaudio → Kivy SoundLoader

### v1.1.0 (Initial Implementation)
- Added simpleaudio integration
- Implemented _play_sound() method
- Connected timing loop to audio playback
- Added graceful fallback for missing library
- Tested on Android (Kindle Fire) and desktop

---

**Last Updated**: 2025-10-13  
**Version**: 1.4.0  
**Author**: Copilot AI / TheMikaus
