# PolyRhythmMetronome - Test Suite

This directory contains tests for verifying the safe audio threading pattern implementation.

## Test Files

### 1. `test_ring_buffer.py`
Tests the core lock-free ring buffer implementation and soft-clipping function.

**Run:**
```bash
cd PolyRhythmMetronome
python3 test_ring_buffer.py
```

**Tests:**
- ✓ Basic push/pop operations
- ✓ Wrap-around behavior
- ✓ Buffer overflow handling
- ✓ Buffer underrun (zero-padding)
- ✓ Soft-clipping function
- ✓ Producer-consumer pattern simulation

**Dependencies:** numpy

**Status:** ✅ All tests passing

---

### 2. `test_desktop_engine.py`
Verifies the Desktop version compiles and has safe threading components.

**Run:**
```bash
cd PolyRhythmMetronome
python3 test_desktop_engine.py
```

**Tests:**
- ✓ Python compilation
- ✓ Required classes present (FloatRingBuffer, StreamEngine, etc.)
- ✓ Required functions present (tanh_soft_clip, etc.)
- ✓ Soft-clipping applied in both sounddevice and simpleaudio paths

**Dependencies:** numpy

**Status:** ✅ All tests passing

**Note:** Does not require GUI (tkinter) or audio hardware. Full functional testing requires those.

---

### 3. `test_android_engine.py`
Verifies the Android version compiles and has safe producer-consumer pattern.

**Run:**
```bash
cd PolyRhythmMetronome
python3 test_android_engine.py
```

**Tests:**
- ✓ Python compilation
- ✓ Required classes present (FloatRingBuffer, Source, SimpleMetronomeEngine, etc.)
- ✓ Producer-consumer pattern implemented (_run_producer, _run_render_thread)
- ✓ Single AudioTrack.write() call in render thread only
- ✓ Old concurrent-write methods not called in new pattern

**Dependencies:** numpy

**Status:** ✅ All tests passing

**Note:** Does not require Kivy, Android SDK, or audio hardware. Full functional testing requires those.

---

## Running All Tests

```bash
cd PolyRhythmMetronome
python3 test_ring_buffer.py && \
python3 test_desktop_engine.py && \
python3 test_android_engine.py && \
echo "" && \
echo "=====================================" && \
echo "✓ ALL TEST SUITES PASSED" && \
echo "====================================="
```

## Test Summary

| Test File | Purpose | Dependencies | Status |
|-----------|---------|--------------|--------|
| test_ring_buffer.py | Unit tests for ring buffer | numpy | ✅ Pass |
| test_desktop_engine.py | Desktop compilation & structure | numpy | ✅ Pass |
| test_android_engine.py | Android compilation & pattern | numpy | ✅ Pass |

## What's Tested

### Safe Threading Pattern Verification

1. **Lock-Free Ring Buffers**
   - Push/pop operations work correctly
   - Wrap-around handled properly
   - Overflow/underrun behavior correct

2. **Soft-Clipping**
   - Prevents harsh digital clipping
   - Monotonic (preserves order)
   - Compresses large values appropriately

3. **Desktop Version**
   - sounddevice callback applies soft-clipping
   - simpleaudio loop applies soft-clipping
   - Already safe (single write per cycle)

4. **Android Version**
   - Producer threads generate and push to ring buffers
   - Single render thread pulls, mixes, and writes
   - Only one AudioTrack.write() call in render thread
   - No concurrent writes

## What's NOT Tested

These tests verify compilation and structure but do NOT test:
- Actual audio playback
- Real-time timing accuracy
- UI functionality
- Hardware compatibility
- Platform-specific behavior

For full functional testing, manual testing is required with:
- Appropriate hardware (desktop/Android device)
- Audio output devices
- GUI (tkinter for Desktop, Kivy for Android)

## Continuous Integration

These tests can be run in CI without GUI or audio hardware:

```yaml
# Example GitHub Actions workflow
- name: Test PolyRhythmMetronome
  run: |
    pip install numpy
    cd PolyRhythmMetronome
    python3 test_ring_buffer.py
    python3 test_desktop_engine.py
    python3 test_android_engine.py
```

## Manual Testing Recommendations

After automated tests pass, manually test:

1. **Desktop Version**
   - Launch application
   - Add 4+ layers per channel
   - Play for 10+ minutes
   - Listen for clicks, pops, dropouts
   - Monitor CPU usage

2. **Android Version**
   - Build APK with buildozer
   - Install on device
   - Add multiple layers
   - Play for 10+ minutes
   - Check battery usage
   - Test with background apps

3. **Timing Accuracy**
   - Enable timing diagnostics
   - Check average drift < 5ms
   - Verify no ring buffer overruns
   - Compare against external metronome

## Troubleshooting

### Test Fails: "Module not found"
Install dependencies: `pip install numpy`

### Test Fails: Compilation error
Check Python syntax in source files

### Test Fails: Pattern not implemented
Re-run git pull to get latest changes

### All Tests Pass But Audio Has Issues
Tests only verify structure, not runtime behavior.
Check:
- Audio hardware is working
- System audio not muted
- Correct audio backend installed (sounddevice, simpleaudio, etc.)

## Documentation

For detailed implementation documentation, see:
- `SAFE_THREADING_PATTERN.md` - Complete implementation guide
- `IMPLEMENTATION_SUMMARY.md` - High-level overview
- Source code comments in `Desktop/Poly_Rhythm_Metronome.py` and `android/main.py`
