# Safe Audio Threading Pattern - Implementation Guide

## Problem Statement

The original implementation had multiple threads calling audio playback APIs (AudioTrack.write(), simpleaudio.play_buffer()) concurrently, which can cause:
- Interleaved buffers
- Audio clicks and pops
- Buffer underruns
- Unpredictable behavior on different devices

## Solution: Producer-Consumer Pattern with Lock-Free Queues

### Pattern Overview

```
Producer Threads (one per layer)
    ↓ generate audio blocks
    ↓ apply volume/gain/accent
    ↓ push to lock-free ring buffer
    
Lock-Free Ring Buffers (one per layer)
    ↓ buffer audio blocks
    
Single Render Thread
    ↓ pull from all ring buffers
    ↓ mix (sum audio from all sources)
    ↓ soft-clip to prevent harsh clipping
    ↓ write to audio device (single thread ownership)
```

### Key Components

#### 1. FloatRingBuffer

Lock-free-ish single-producer single-consumer ring buffer:
- Separate read/write indices (volatile due to Python GIL)
- Handles wrap-around for circular buffer
- Returns number of frames actually read/written
- Pads with zeros if insufficient data

```python
class FloatRingBuffer:
    def push(self, src):  # Producer writes here
        # Write up to available space
        # Returns frames actually written
    
    def pop(self, dst, frames):  # Consumer reads here
        # Read up to available frames
        # Pads with zeros if underrun
        # Returns frames actually read
```

#### 2. Source Class (Android)

Encapsulates one audio layer with its own ring buffer:
- Stores layer configuration (subdiv, volume, mute, etc.)
- Owns a FloatRingBuffer for its audio
- Atomic-ish control flags (mute, gain) due to GIL

```python
class Source:
    def __init__(self, layer, channel, bpm, beats_per_measure, audio_getter):
        self.ring = FloatRingBuffer(AUDIO_BLOCK_SIZE * RING_BUFFER_BLOCKS)
        self.muted = bool(layer.get("mute", False))
        self.gain = float(layer.get("vol", 1.0))
        # ... timing state
```

#### 3. Producer Threads

One thread per source/layer:
- Calculate next beat time
- Sleep until beat time
- Generate audio data (tone/drum/mp3)
- Apply volume, accent, master volume
- Push to source's ring buffer
- Trigger UI flash callback

```python
def _run_producer(self, source):
    while self.running:
        # Wait for next beat
        wait_time = source.next_beat_time - current_time
        if wait_time > 0:
            time.sleep(wait_time)
        
        # Generate and scale audio
        audio_data = source.audio_getter(source.layer, is_accent)
        scaled_audio = audio_data * volume
        
        # Push to ring buffer (non-blocking)
        source.ring.push(scaled_audio)
```

#### 4. Render Thread

Single thread that owns the audio device:
- Pre-allocate mix buffers
- Pull from all source ring buffers
- Sum to left/right channels
- Apply soft-clipping to prevent harsh digital clipping
- Interleave to stereo
- Write to audio device (AudioTrack, simpleaudio, etc.)

```python
def _run_render_thread(self):
    while self.running:
        # Clear mix buffers
        mix_left.fill(0.0)
        mix_right.fill(0.0)
        
        # Pull and mix from all sources
        for source in sources:
            n = source.ring.pop(tmp, frames_per_block)
            if source.channel == 'left':
                mix_left += tmp
            else:
                mix_right += tmp
        
        # Soft-clip to prevent harsh clipping
        mix_left = tanh_soft_clip(mix_left)
        mix_right = tanh_soft_clip(mix_right)
        
        # Interleave and write (single-threaded)
        stereo = interleave(mix_left, mix_right)
        audio_track.write(stereo)  # ONLY ONE THREAD CALLS THIS
```

#### 5. Soft-Clipping

Uses tanh function for gentle limiting:
```python
def tanh_soft_clip(x):
    """Soft clip audio using tanh to prevent harsh digital clipping"""
    a = 2.0
    return np.tanh(a * x) / np.tanh(a)
```

Benefits:
- Prevents harsh digital clipping when multiple layers sum above ±1.0
- More musical than hard clipping
- Maintains phase relationships

## Implementation Details

### Desktop Version (Poly_Rhythm_Metronome.py)

The Desktop version was already mostly safe:
- **sounddevice**: Uses callback that runs in single thread ✅
- **simpleaudio**: Was mixing then calling play_buffer once per beat cycle ✅

Changes made:
- Added `FloatRingBuffer` class (for potential future use)
- Added `tanh_soft_clip()` function
- Applied soft-clipping in both sounddevice callback and simpleaudio loop
- No architectural changes needed (already safe)

### Android Version (main.py)

The Android version had the problematic pattern and was completely refactored:

**Before:**
- Each layer had its own thread
- Each thread called `_play_sound()` which called `AudioTrack.write()` directly
- Multiple concurrent writes to AudioTrack → clicks and underruns

**After:**
- Producer threads (one per layer) generate audio and push to ring buffers
- Single render thread pulls from all buffers, mixes, and writes to AudioTrack
- Only one thread ever calls `AudioTrack.write()` ✅

Changes made:
1. Added `FloatRingBuffer` class
2. Added `tanh_soft_clip()` function
3. Created `Source` class to encapsulate layers with ring buffers
4. Replaced `_run_layer()` with:
   - `_run_producer()` - one per layer
   - `_run_render_thread()` - single mixer/writer
5. Removed per-sound AudioTrack creation in `_play_sound()`
6. Render thread creates single long-lived AudioTrack in MODE_STREAM

## Configuration

### Buffer Sizing

```python
AUDIO_BLOCK_SIZE = 1024  # frames per block
RING_BUFFER_BLOCKS = 8   # 8 blocks of headroom
```

Ring buffer capacity per source: `1024 * 8 = 8192 frames ≈ 186ms @ 44.1kHz`

This provides sufficient headroom for:
- Timing jitter from Python sleep()
- GC pauses
- System load variations

### Audio Format

- Sample rate: 44100 Hz
- Channels: 2 (stereo)
- Format: PCM 16-bit signed (for AudioTrack)
- Internal processing: float32 for better precision

## Best Practices

### Do's ✅

1. **One thread writes to audio device**
   - Desktop: sounddevice callback or simpleaudio loop
   - Android: render thread

2. **Use lock-free queues for audio data**
   - Producer threads push
   - Render thread pulls
   - No locks in critical path

3. **Apply soft-clipping when mixing**
   - Prevents harsh digital clipping
   - More musical than hard clipping

4. **Pre-allocate buffers**
   - Avoid allocations in audio threads
   - Reuse buffers across iterations

5. **Use atomic flags for control changes**
   - Mute/volume/gain stored in Source
   - Read atomically by render thread
   - Python GIL provides basic atomicity

6. **Set appropriate thread priority**
   - Desktop: Audio threads already have OS priority
   - Android: Consider using `Process.setThreadPriority(THREAD_PRIORITY_AUDIO)`

### Don'ts ❌

1. **Don't call write() from multiple threads**
   - AudioTrack doesn't serialize writes
   - Results in corrupted audio

2. **Don't lock in render thread**
   - Causes jitter and timing issues
   - Use lock-free queues instead

3. **Don't allocate in hot path**
   - No `new`, `malloc`, buffer creation
   - Pre-allocate everything

4. **Don't do file I/O in audio thread**
   - Pre-load all samples
   - Cache everything before playback starts

5. **Don't use regular mutexes**
   - Spin locks or lock-free structures only
   - Or rely on GIL for simple atomicity

## Performance Characteristics

### CPU Usage

- Producer threads: Minimal (mostly sleeping)
- Render thread: Constant, proportional to layer count
- Ring buffers: O(1) push/pop operations

### Latency

- Render thread latency: `AUDIO_BLOCK_SIZE / SAMPLE_RATE = 1024 / 44100 ≈ 23ms`
- Plus system audio pipeline latency (varies by device)
- Total latency typically 50-150ms (acceptable for metronome)

### Memory Usage

Per layer:
- Ring buffer: `AUDIO_BLOCK_SIZE * RING_BUFFER_BLOCKS * 4 bytes = 32KB`
- Audio samples: Cached, ~1.5KB per 100ms of audio
- Total: ~50-100KB per layer

## Testing

### Verify Safe Threading

1. **No concurrent writes**: Only render thread calls write()
2. **No audio glitches**: Listen for clicks, pops, or dropouts
3. **Stable timing**: Use timing diagnostics to verify accuracy
4. **Multiple layers**: Test with 4+ layers per channel
5. **Long-running**: Test for 10+ minutes continuously

### Performance Testing

```python
# Enable timing diagnostics
rhythm_state.timing_diagnostics = True

# Check logs for:
# - Average timing drift < 5ms
# - No ring buffer overruns
# - Consistent sleep accuracy
```

## Troubleshooting

### Symptom: Audio clicks/pops

**Possible causes:**
- Ring buffer too small (underruns)
- GC pauses
- System under heavy load

**Solutions:**
- Increase `RING_BUFFER_BLOCKS`
- Reduce layer count
- Close background apps

### Symptom: Timing drift

**Possible causes:**
- Python sleep() accuracy varies
- System scheduler latency
- Producer threads not keeping up

**Solutions:**
- Verify ring buffers have data (check `available()`)
- Reduce audio processing in producers
- Check system load

### Symptom: Delayed response

**Possible causes:**
- Large ring buffers add latency
- System audio pipeline latency

**Solutions:**
- Reduce `AUDIO_BLOCK_SIZE` (trade-off: more CPU)
- Accept latency (metronome tolerance is ~50ms)

## References

Based on the Kotlin example from problem statement, adapted to Python with:
- Python-specific considerations (GIL, threading model)
- Integration with existing metronome architecture
- Support for both Desktop and Android platforms

## Testing

A comprehensive test suite verifies the implementation:

```bash
cd PolyRhythmMetronome
python3 test_ring_buffer.py
```

Tests cover:
- ✅ Basic push/pop operations
- ✅ Wrap-around behavior
- ✅ Buffer overflow handling
- ✅ Buffer underrun (zero-padding)
- ✅ Soft-clipping function
- ✅ Producer-consumer pattern simulation

All tests pass, confirming correct implementation.

## Conclusion

The producer-consumer pattern with lock-free ring buffers ensures:
- ✅ Only one thread writes to audio device
- ✅ No locks in critical audio path
- ✅ Stable, glitch-free audio playback
- ✅ Proper mixing with soft-clipping
- ✅ Atomic control changes

This pattern works reliably across different platforms and audio backends (sounddevice, simpleaudio, AudioTrack).
