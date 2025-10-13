# MP3 MediaCodec Implementation

## Overview

This document describes the implementation of native MP3 decoding for the Android version of PolyRhythmMetronome using Android's MediaExtractor and MediaCodec APIs.

## Architecture

### Key Components

1. **WaveCache** - Caches decoded audio samples
2. **Mp3TickCache** - Manages MP3 tick files from the `ticks/` folder
3. **SimpleMetronomeEngine** - Updated to support mp3_tick mode

### Why MediaCodec?

The Desktop version uses pydub (which requires ffmpeg) for MP3 decoding. On Android, we use native APIs instead:

- **No external dependencies** - ffmpeg is not needed
- **Smaller APK size** - No codec libraries to bundle
- **Hardware acceleration** - Uses device's hardware decoder when available
- **Better performance** - Native code is faster than Python-wrapped ffmpeg
- **Better compatibility** - Works on all Android devices with API 21+

## Implementation Details

### MediaCodec Decoding Process

```
MP3 File → MediaExtractor → MediaCodec Decoder → PCM Samples → NumPy Array
```

#### Step 1: Extract Audio Track

```python
from jnius import autoclass

MediaExtractor = autoclass('android.media.MediaExtractor')
extractor = MediaExtractor()
extractor.setDataSource(path)

# Find audio track
for i in range(extractor.getTrackCount()):
    format = extractor.getTrackFormat(i)
    mime = format.getString(MediaFormat.KEY_MIME)
    if mime.startswith('audio/'):
        extractor.selectTrack(i)
        break
```

#### Step 2: Configure Decoder

```python
MediaCodec = autoclass('android.media.MediaCodec')

mime = audio_format.getString(MediaFormat.KEY_MIME)
decoder = MediaCodec.createDecoderByType(mime)
decoder.configure(audio_format, None, None, 0)
decoder.start()
```

#### Step 3: Decode Loop

The decoder operates in a push-pull model:

1. **Push** - Queue input buffers with compressed data
2. **Pull** - Dequeue output buffers with PCM data

```python
while not output_eof:
    # Feed input
    if not input_eof:
        input_buffer_index = decoder.dequeueInputBuffer(timeout_us)
        if input_buffer_index >= 0:
            input_buffer = decoder.getInputBuffer(input_buffer_index)
            sample_size = extractor.readSampleData(input_buffer, 0)
            
            if sample_size < 0:
                decoder.queueInputBuffer(input_buffer_index, 0, 0, 0, 
                                        MediaCodec.BUFFER_FLAG_END_OF_STREAM)
                input_eof = True
            else:
                decoder.queueInputBuffer(input_buffer_index, 0, sample_size, 
                                        extractor.getSampleTime(), 0)
                extractor.advance()
    
    # Get output
    output_buffer_index = decoder.dequeueOutputBuffer(buffer_info, timeout_us)
    if output_buffer_index >= 0:
        output_buffer = decoder.getOutputBuffer(output_buffer_index)
        # Read PCM data...
        decoder.releaseOutputBuffer(output_buffer_index, False)
```

#### Step 4: Convert to NumPy

```python
# Read bytes from ByteBuffer
byte_array = bytearray(buffer_info.size)
output_buffer.position(buffer_info.offset)
for i in range(buffer_info.size):
    byte_array[i] = output_buffer.get() & 0xFF

# Convert to int16 samples (assuming 16-bit PCM)
samples = np.frombuffer(byte_array, dtype=np.int16)
```

#### Step 5: Post-Processing

```python
# Convert to mono if stereo
if channel_count > 1:
    audio_data = audio_data.reshape(-1, channel_count).mean(axis=1)

# Normalize to float32 in range [-1.0, 1.0]
audio_data = audio_data.astype(np.float32) / 32768.0

# Resample if needed
if sample_rate != target_rate:
    audio_data = _resample_linear(audio_data, sample_rate, target_rate)
```

## MP3 Tick File Management

### File Naming Conventions

- **Single file**: `click.mp3` → "click" in UI
- **Paired files**: `woodblock_1.mp3` + `woodblock_2.mp3` → "woodblock" in UI
  - `_1` file plays on accented beats (first beat of measure)
  - `_2` file plays on regular beats

### Scanning Algorithm

```python
def _scan_ticks_folder(self):
    mp3_files = {}
    for filename in os.listdir(self.ticks_dir):
        if filename.lower().endswith('.mp3'):
            name_without_ext = os.path.splitext(filename)[0]
            mp3_files[name_without_ext] = full_path
    
    # Identify pairs
    for name in mp3_files:
        if name.endswith('_1'):
            base_name = name[:-2]
            pair_name = base_name + '_2'
            if pair_name in mp3_files:
                self._pairs[base_name] = (mp3_files[name], mp3_files[pair_name])
```

### Caching Strategy

- MP3 files are decoded once at app startup
- Decoded samples are cached in memory as NumPy float32 arrays
- Cache key is the absolute file path
- Memory usage: ~176 KB per second of 44.1kHz mono audio

## Integration with Metronome Engine

### Layer Configuration

Each layer now supports an `mp3_tick` field:

```python
layer = {
    "mode": "mp3_tick",
    "mp3_tick": "woodblock",  # Name without _1/_2 suffix
    "vol": 1.0,
    "subdiv": 4,
    # ... other fields
}
```

### Accent Beat Detection

```python
def _get_audio_data(self, layer, is_accent=False):
    mode = layer.get("mode", "tone")
    
    if mode == "mp3_tick" and layer.get("mp3_tick"):
        data = self.mp3_ticks.get(layer["mp3_tick"], is_accent=is_accent)
        if data is not None:
            return data
    
    # Fallback to tone/drum
```

## Performance Considerations

### Startup Time

- MP3 decoding happens at startup (lazy loading)
- Typical 100ms tick sound decodes in ~10-50ms depending on device
- Multiple files are decoded sequentially
- Large tick libraries (100+ files) may increase startup time

### Memory Usage

Example memory calculation:
- 1 second of 44.1kHz mono audio = 44,100 samples
- float32 = 4 bytes per sample
- Memory = 44,100 × 4 = 176,400 bytes (~172 KB)

For a typical tick sound (50-200ms):
- 50ms = 8.6 KB
- 100ms = 17.2 KB
- 200ms = 34.4 KB

### Runtime Performance

- **Cached playback**: Instant (array access)
- **Volume adjustment**: O(n) multiplication
- **Stereo conversion**: O(n) array operation
- **No I/O during playback**: All data is pre-loaded

## Error Handling

### Graceful Degradation

If MP3 loading fails, the layer falls back to tone mode:

```python
try:
    data = self.mp3_ticks.get(layer["mp3_tick"], is_accent=is_accent)
    if data is not None:
        return data
except Exception as e:
    print(f"[audio] Failed to load MP3 tick: {e}")

# Fallback to tone
freq = float(layer.get("freq", 880.0))
return self.tone_gen.generate_beep(freq, duration_ms=50)
```

### Common Errors

1. **No audio track found**: MP3 file has no audio stream
2. **Decoder creation failed**: Unsupported MP3 format/codec
3. **Timeout**: Decoder stuck (usually indicates corrupted file)
4. **Memory error**: File too large or too many files loaded

## Testing Recommendations

### Unit Tests
1. Test MP3 decoding with various sample rates (22050, 44100, 48000 Hz)
2. Test mono vs stereo MP3 files
3. Test paired vs single file detection
4. Test cache hit/miss behavior

### Integration Tests
1. Load MP3 ticks and verify playback
2. Test accent vs regular beat distinction
3. Test switching between MP3 ticks during playback
4. Test memory usage with large tick libraries

### Device Testing
1. Test on multiple Android versions (5.0, 7.0, 9.0, 10+)
2. Test on different device architectures (ARM, ARM64, x86)
3. Test with various MP3 encodings (CBR, VBR, different bitrates)
4. Test performance on low-end devices

## Comparison with Desktop Version

| Feature | Desktop (pydub + ffmpeg) | Android (MediaCodec) |
|---------|--------------------------|----------------------|
| **Dependencies** | pydub, ffmpeg | None (built-in) |
| **Library Size** | ~50+ MB (ffmpeg) | 0 MB |
| **Performance** | Medium (Python wrapper) | Fast (native) |
| **Hardware Accel** | No | Yes (if available) |
| **Supported Formats** | Many (via ffmpeg) | MP3, AAC, FLAC, OGG, WAV |
| **Compatibility** | All platforms with ffmpeg | Android API 21+ |

## Future Enhancements

Potential improvements:
1. **Async loading** - Load MP3s in background thread
2. **Progress indicator** - Show loading status for large libraries
3. **Format support** - Add WAV, OGG support via MediaCodec
4. **Preview** - Add button to preview tick sound before adding layer
5. **Waveform display** - Show visual waveform of selected tick
6. **Compression** - Use AAC instead of PCM for cached data to reduce memory

## References

- [Android MediaCodec Documentation](https://developer.android.com/reference/android/media/MediaCodec)
- [Android MediaExtractor Documentation](https://developer.android.com/reference/android/media/MediaExtractor)
- [Audio Decoding Best Practices](https://developer.android.com/guide/topics/media/mediacodec)
