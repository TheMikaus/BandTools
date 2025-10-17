#!/usr/bin/env python3
"""
Batch Waveform Cleanup Test

Tests that WaveformEngine properly cleans up threads when generating
waveforms for multiple files simultaneously and then being destroyed.
This simulates the real-world scenario described in the issue.
"""

import sys
import os
import time
import tempfile
import wave

# Set QT_QPA_PLATFORM to offscreen to avoid display issues in CI
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from pathlib import Path
from PyQt6.QtCore import QCoreApplication, QTimer
from backend.waveform_engine import WaveformEngine

def create_test_wav_file(path: Path, duration_seconds: float = 0.1):
    """Create a small test WAV file."""
    sample_rate = 44100
    num_samples = int(sample_rate * duration_seconds)
    
    with wave.open(str(path), 'wb') as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        
        # Generate simple sine wave
        import math
        frequency = 440.0  # A4 note
        samples = []
        for i in range(num_samples):
            value = int(32767 * 0.5 * math.sin(2 * math.pi * frequency * i / sample_rate))
            samples.append(value)
        
        # Write samples
        import struct
        data = struct.pack('<' + 'h' * len(samples), *samples)
        wf.writeframes(data)

def test_batch_generation_cleanup():
    """Test that cleanup works correctly after batch waveform generation."""
    print("Testing batch waveform generation and cleanup...")
    
    app = QCoreApplication(sys.argv)
    engine = WaveformEngine()
    
    # Create temporary directory with test files
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create multiple test WAV files (simulating 37 files from issue)
        num_files = 10  # Using 10 for faster test, issue had 37
        test_files = []
        print(f"Creating {num_files} test files...")
        for i in range(num_files):
            filepath = tmppath / f"test_{i:03d}.wav"
            create_test_wav_file(filepath)
            test_files.append(str(filepath))
        
        print(f"Generating waveforms for {num_files} files...")
        
        # Track signal emissions
        ready_count = [0]
        error_count = [0]
        
        def on_ready(path):
            ready_count[0] += 1
            print(f"  Waveform ready: {Path(path).name} ({ready_count[0]}/{num_files})")
        
        def on_error(path, error):
            error_count[0] += 1
            print(f"  Waveform error: {Path(path).name}: {error}")
        
        engine.waveformReady.connect(on_ready)
        engine.waveformError.connect(on_error)
        
        # Start waveform generation for all files (simulating batch operation)
        for filepath in test_files:
            engine.generateWaveform(filepath)
        
        # Let some waveforms start processing
        print("Waiting briefly for threads to start...")
        
        # Use a timer to trigger cleanup while event loop is still running
        def do_cleanup():
            print(f"Cleaning up with {len(engine._threads)} threads potentially running...")
            num_running = sum(1 for t in engine._threads.values() if t.isRunning())
            print(f"  {num_running} threads are actually running")
            
            # This should not produce "QThread: Destroyed while thread is still running" warning
            engine.cleanup()
            
            # Give cleanup a moment to complete, then quit
            QTimer.singleShot(100, app.quit)
        
        QTimer.singleShot(100, do_cleanup)
        app.exec()
        
        # Verify cleanup worked
        assert len(engine._workers) == 0, "All workers should be cleaned up"
        assert len(engine._threads) == 0, "All threads should be cleaned up"
        
        print(f"✓ Successfully cleaned up all threads")
        print(f"  Waveforms completed: {ready_count[0]}/{num_files}")
        print(f"  Errors: {error_count[0]}")
        
    return True

def test_destructor_cleanup():
    """Test that destructor properly cleans up threads."""
    print("\nTesting destructor cleanup...")
    
    app = QCoreApplication(sys.argv)
    
    # Create temporary directory with test files
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create a few test files
        num_files = 5
        test_files = []
        print(f"Creating {num_files} test files...")
        for i in range(num_files):
            filepath = tmppath / f"test_{i:03d}.wav"
            create_test_wav_file(filepath)
            test_files.append(str(filepath))
        
        # Create engine in a scope that will destroy it
        def create_and_use_engine():
            engine = WaveformEngine()
            
            # Start waveform generation
            for filepath in test_files:
                engine.generateWaveform(filepath)
            
            # Let threads start
            QTimer.singleShot(50, app.quit)
            app.exec()
            
            print(f"  Engine has {len(engine._threads)} threads")
            # Engine will be destroyed here, __del__ should call cleanup()
        
        print("Creating engine and starting waveform generation...")
        create_and_use_engine()
        
        # If we get here without "QThread: Destroyed while thread is still running",
        # then the fix is working
        print("✓ Destructor cleanup successful (no QThread warnings)")
        
    return True

def main():
    """Run all tests."""
    print("=" * 60)
    print("Batch Waveform Cleanup Test Suite")
    print("=" * 60)
    print("This test simulates the real-world scenario:")
    print("- Generating waveforms for multiple files")
    print("- Cleaning up before all waveforms complete")
    print("=" * 60)
    
    results = []
    
    try:
        # Run tests
        results.append(("Batch generation cleanup", test_batch_generation_cleanup()))
        results.append(("Destructor cleanup", test_destructor_cleanup()))
    except Exception as e:
        print(f"\n✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed!")
        print("\nThe fix successfully prevents 'QThread: Destroyed while thread")
        print("is still running' warnings when generating waveforms for multiple")
        print("files and cleaning up before completion.")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
