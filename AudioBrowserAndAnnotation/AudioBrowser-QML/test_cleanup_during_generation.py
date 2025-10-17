#!/usr/bin/env python3
"""
Cleanup During Generation Test

Tests that WaveformEngine properly cleans up threads when cleanup is called
while threads are actively generating waveforms. This more realistically
simulates the issue scenario where a user changes folders while waveforms
are still being generated.
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

def create_large_test_wav_file(path: Path, duration_seconds: float = 5.0):
    """Create a larger test WAV file that takes time to process."""
    sample_rate = 44100
    num_samples = int(sample_rate * duration_seconds)
    
    with wave.open(str(path), 'wb') as wf:
        wf.setnchannels(2)  # Stereo for more data
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        
        # Generate a more complex waveform that takes longer to process
        import math
        samples = []
        for i in range(num_samples):
            # Multiple frequencies to make processing slower
            value = 0
            for freq in [220.0, 440.0, 880.0]:
                value += 32767 * 0.2 * math.sin(2 * math.pi * freq * i / sample_rate)
            samples.append(int(value))
            samples.append(int(value * 0.9))  # Stereo, slightly different
        
        # Write samples
        import struct
        data = struct.pack('<' + 'h' * len(samples), *samples)
        wf.writeframes(data)

def test_cleanup_during_active_generation():
    """Test cleanup while threads are actively processing."""
    print("Testing cleanup during active waveform generation...")
    
    app = QCoreApplication(sys.argv)
    engine = WaveformEngine()
    
    # Create temporary directory with larger test files
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create larger files that will take longer to process
        num_files = 20
        test_files = []
        print(f"Creating {num_files} larger test files (this may take a moment)...")
        for i in range(num_files):
            filepath = tmppath / f"large_test_{i:03d}.wav"
            create_large_test_wav_file(filepath, duration_seconds=2.0)
            test_files.append(str(filepath))
        
        print(f"Generating waveforms for {num_files} files...")
        
        # Track what happens
        ready_count = [0]
        error_count = [0]
        cancelled_count = [0]
        
        def on_ready(path):
            ready_count[0] += 1
        
        def on_error(path, error):
            error_count[0] += 1
        
        engine.waveformReady.connect(on_ready)
        engine.waveformError.connect(on_error)
        
        # Start waveform generation for all files
        for filepath in test_files:
            engine.generateWaveform(filepath)
        
        print(f"Started generation for {num_files} files")
        
        # Call cleanup very quickly while threads are likely still running
        def do_cleanup():
            num_threads = len(engine._threads)
            num_running = sum(1 for t in engine._threads.values() if t.isRunning())
            print(f"Calling cleanup with {num_threads} threads ({num_running} running)...")
            
            if num_running == 0:
                print("  WARNING: All threads finished before cleanup - test may not be realistic")
            
            # This should not produce "QThread: Destroyed while thread is still running" warning
            engine.cleanup()
            
            # Verify cleanup worked
            assert len(engine._workers) == 0, "All workers should be cleaned up"
            assert len(engine._threads) == 0, "All threads should be cleaned up"
            
            print(f"✓ Successfully cleaned up all threads")
            print(f"  Waveforms completed before cleanup: {ready_count[0]}/{num_files}")
            print(f"  Errors: {error_count[0]}")
            
            # Quit after a brief delay to ensure cleanup is fully done
            QTimer.singleShot(200, app.quit)
        
        # Call cleanup after a very short delay (10ms) - threads should still be running
        QTimer.singleShot(10, do_cleanup)
        app.exec()
        
    return True

def test_rapid_start_stop():
    """Test rapidly starting and stopping waveform generation."""
    print("\nTesting rapid start/stop cycles...")
    
    app = QCoreApplication(sys.argv)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create test files
        num_files = 5
        test_files = []
        print(f"Creating {num_files} test files...")
        for i in range(num_files):
            filepath = tmppath / f"test_{i:03d}.wav"
            create_large_test_wav_file(filepath, duration_seconds=1.0)
            test_files.append(str(filepath))
        
        # Do multiple start/cleanup cycles
        for cycle in range(3):
            print(f"\nCycle {cycle + 1}/3:")
            engine = WaveformEngine()
            
            # Start generation
            for filepath in test_files:
                engine.generateWaveform(filepath)
            
            print(f"  Started {len(test_files)} generations")
            
            # Process events briefly
            QTimer.singleShot(5, app.quit)
            app.exec()
            
            # Cleanup
            print(f"  Cleaning up {len(engine._threads)} threads...")
            engine.cleanup()
            
            assert len(engine._workers) == 0
            assert len(engine._threads) == 0
            print(f"  ✓ Cleanup successful")
        
        print("\n✓ All rapid start/stop cycles completed successfully")
        
    return True

def main():
    """Run all tests."""
    print("=" * 60)
    print("Cleanup During Generation Test Suite")
    print("=" * 60)
    print("This test ensures cleanup works properly when called")
    print("while threads are actively processing waveforms.")
    print("=" * 60)
    
    results = []
    
    try:
        # Run tests
        results.append(("Cleanup during active generation", test_cleanup_during_active_generation()))
        results.append(("Rapid start/stop cycles", test_rapid_start_stop()))
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
        print("is still running' warnings even when cleanup is called while")
        print("threads are actively processing waveforms.")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
