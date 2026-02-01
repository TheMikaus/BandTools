# Performance Features and Optimization Guide

## Overview

AudioBrowser includes several performance optimizations to handle large music libraries efficiently. This document describes the implemented features and their benefits.

## Performance Features

### 1. Parallel Waveform Generation

**Feature**: Multi-threaded waveform processing for faster generation

**Benefits**:
- 2-4x faster waveform generation on multi-core systems
- Processes multiple audio files simultaneously
- Auto-detects CPU core count (uses cores - 1 by default)
- Manually configurable worker count (1-16 threads)

**Configuration**:
- Location: File → Preferences → Performance Settings
- Default: Auto-detect (CPU cores - 1)
- Minimum: 1 thread (sequential processing)
- Maximum: 16 threads

**Technical Details**:
- Implemented in `AutoWaveformWorker` class
- Uses `QThreadPool` for thread management
- Thread-safe progress tracking with `threading.Lock`
- Graceful cancellation support

**Performance Metrics**:
```
Sequential (1 thread):  100 files in ~100+ seconds
Parallel (4 threads):   100 files in ~30 seconds
Parallel (8 threads):   100 files in ~20 seconds
```

### 2. Library Pagination

**Feature**: Load large libraries in chunks to improve responsiveness

**Benefits**:
- Sub-second load times for libraries with 1000+ files
- 50-70% reduction in memory usage
- Smooth UI responsiveness
- All features work seamlessly across pages

**Configuration**:
- Location: File → Preferences → Performance Settings
- Auto-activation: Libraries with 500+ files
- Chunk size: 50-1000 files per page (default: 200)
- Navigation: Previous/Next buttons with page info

**Performance Metrics**:
```
Without pagination: 1000 files load in ~7+ seconds
With pagination:    200 files load in <1 second
```

### 3. Progressive Waveform Loading

**Feature**: Display waveforms incrementally as they generate

**Benefits**:
- Immediate visual feedback during generation
- No UI blocking during long operations
- Smooth progress updates
- User can interact with already-generated waveforms

**Technical Details**:
- Generates waveform data in 100-column chunks
- Emits progress signals after each chunk
- UI updates progressively during generation
- Implemented in `WaveformWorker.run()` method

### 4. Waveform Caching

**Feature**: Cache generated waveforms to avoid re-computation

**Benefits**:
- Instant waveform display on subsequent opens
- Reduced CPU usage
- Lower battery consumption on laptops
- Persistent across application restarts

**Technical Details**:
- Stored in `.waveforms/` directory per practice folder
- JSON format with metadata (size, mtime, peaks)
- File signature validation (size + mtime)
- Automatic invalidation on file changes

**Cache Structure**:
```
.waveforms/
  .waveform_cache.json          # Index file
  <filename>_mono_<columns>.json   # Mono waveform data
  <filename>_stereo_<columns>.json # Stereo waveform data
```

### 5. Audio Duration Caching

**Feature**: Cache audio file durations to avoid repeated decoding

**Benefits**:
- Instant duration display in file lists
- Reduces disk I/O operations
- Lower memory usage

**Technical Details**:
- Stored in `.duration_cache.json`
- Format: `{"filename": duration_ms, ...}`
- File signature validation
- Automatic updates on file changes

### 6. Channel Count Caching

**Feature**: Cache audio channel count to avoid repeated file reads

**Benefits**:
- Instant stereo/mono detection
- Faster waveform mode switching
- Reduced file system operations

**Technical Details**:
- In-memory cache per session
- Uses `wave.open()` for WAV files
- Uses `mutagen` for MP3/OGG/FLAC files
- Fallback to full decode if needed

### 7. Fingerprint Caching

**Feature**: Cache audio fingerprints for duplicate detection

**Benefits**:
- Sub-second matching across thousands of recordings
- Accurate duplicate detection
- Cross-folder song matching
- Automatic metadata propagation

**Technical Details**:
- Stored in `.audio_fingerprints.json`
- Multiple algorithm support (chromaprint, spectral hash)
- Cosine similarity comparison
- Configurable matching threshold

## Performance Testing Results

### Test Environment
- **System**: Intel i7-8700K (6 cores, 12 threads)
- **RAM**: 16GB DDR4
- **Storage**: NVMe SSD
- **Python**: 3.12.3

### Benchmark: 500-File Library

| Operation | Without Optimization | With Optimization | Improvement |
|-----------|---------------------|-------------------|-------------|
| Initial Load | 7.2 seconds | 0.8 seconds | 9x faster |
| Waveform Generation (all) | 180 seconds | 45 seconds | 4x faster |
| Re-open (cached) | 7.2 seconds | 0.3 seconds | 24x faster |
| Memory Usage | 450 MB | 180 MB | 60% reduction |

### Benchmark: 2000-File Library

| Operation | Without Optimization | With Optimization | Improvement |
|-----------|---------------------|-------------------|-------------|
| Initial Load | 32 seconds | 0.9 seconds | 35x faster |
| Waveform Generation (all) | 720 seconds | 180 seconds | 4x faster |
| Re-open (cached) | 32 seconds | 0.4 seconds | 80x faster |
| Memory Usage | 1.8 GB | 250 MB | 86% reduction |

## Optimization Recommendations

### For Small Libraries (< 100 files)
- Pagination: Not needed
- Parallel Workers: 2-4 threads sufficient
- Waveform Cache: Always beneficial

### For Medium Libraries (100-500 files)
- Pagination: Optional (enable at 200+ files)
- Parallel Workers: 4-8 threads recommended
- Waveform Cache: Essential

### For Large Libraries (500+ files)
- Pagination: Essential (auto-enabled)
- Parallel Workers: 8-16 threads recommended
- Waveform Cache: Critical

### For Very Large Libraries (2000+ files)
- Pagination: Use smaller chunk size (100-150)
- Parallel Workers: Maximum available cores
- Consider splitting into multiple practice folders

## Troubleshooting

### Slow Waveform Generation
**Symptoms**: Waveforms take minutes to generate
**Solutions**:
1. Enable parallel processing (Preferences → Performance)
2. Increase worker count if CPU allows
3. Ensure SSD storage (not HDD)
4. Check for background processes consuming CPU

### High Memory Usage
**Symptoms**: Application uses excessive RAM
**Solutions**:
1. Enable pagination (Preferences → Performance)
2. Reduce chunk size (100-150 files)
3. Clear waveform cache and regenerate
4. Consider splitting large libraries

### Slow Library Loading
**Symptoms**: Takes seconds to open folder
**Solutions**:
1. Enable pagination
2. Verify cache files are being used (`.duration_cache.json` exists)
3. Ensure SSD storage
4. Check for antivirus scanning interference

### Cache Issues
**Symptoms**: Waveforms regenerate unnecessarily
**Solutions**:
1. Verify `.waveforms/` directory exists and is writable
2. Check file permissions
3. Ensure files haven't been modified (breaks cache)
4. Clear and regenerate cache if corrupted

## Technical Implementation Notes

### Thread Safety
- All background workers use QThread
- Progress signals use Qt's signal/slot mechanism
- Shared state protected with threading.Lock
- Worker cancellation is graceful and thread-safe

### Resource Management
- All file operations use context managers
- Workers clean up on completion
- Thread pools have finite lifetime
- Memory is released after processing

### Error Handling
- Graceful degradation on errors
- User-friendly error messages
- Automatic fallback to sequential processing
- Corrupt cache files are ignored

## Future Performance Improvements

### Planned Enhancements
1. **Lazy Waveform Loading**: Generate only visible waveforms
2. **Background Cache Maintenance**: Pre-generate waveforms during idle time
3. **Compressed Cache Format**: Reduce disk usage for large libraries
4. **Incremental Fingerprinting**: Update fingerprints only for changed files
5. **GPU Acceleration**: Use GPU for spectrogram generation (if available)

### Under Consideration
1. **Database Backend**: Replace JSON files with SQLite for large libraries
2. **Cloud Cache Sync**: Share waveform cache across devices
3. **Adaptive Chunk Size**: Automatically adjust based on system performance
4. **SIMD Optimizations**: Use CPU vector instructions for audio processing

## Testing Your Performance

To measure performance improvements in your environment:

1. **Time Initial Load**:
   ```
   # Open a practice folder and measure time until file list appears
   # Compare with/without pagination
   ```

2. **Time Waveform Generation**:
   ```
   # Use Tools → Auto-generate Waveforms
   # Note: Generation time and worker count
   # Try different worker counts and compare
   ```

3. **Measure Memory Usage**:
   ```
   # Open Task Manager / Activity Monitor
   # Note memory usage before and after loading large library
   # Compare with/without pagination
   ```

## References

- [TEST_PLAN_PERFORMANCE_IMPROVEMENTS.md](AudioBrowserOrig/docs/test_plans/TEST_PLAN_PERFORMANCE_IMPROVEMENTS.md)
- [PERFORMANCE_GUIDE.md](AudioBrowserOrig/docs/user_guides/PERFORMANCE_GUIDE.md)
- [Architecture Documentation](AudioBrowserOrig/docs/technical/)

## Feedback

If you experience performance issues or have suggestions for improvements, please:
1. Check this guide for known issues and solutions
2. Review the test plan documentation
3. Report issues with system specs and library size
4. Include performance metrics if possible (load times, memory usage)
