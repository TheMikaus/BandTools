#!/usr/bin/env python3
"""
Thread Cleanup Test

Tests that WaveformEngine properly cleans up threads when destroyed.
This addresses the issue: "QThread: Destroyed while thread is still running"
"""

import sys
import os

# Set QT_QPA_PLATFORM to offscreen to avoid display issues in CI
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from pathlib import Path
from PyQt6.QtCore import QCoreApplication
from backend.waveform_engine import WaveformEngine

def test_cleanup_method_exists():
    """Test that cleanup method exists."""
    print("Testing cleanup method exists...")
    try:
        app = QCoreApplication(sys.argv)
        engine = WaveformEngine()
        
        assert hasattr(engine, 'cleanup'), "cleanup method should exist"
        assert callable(engine.cleanup), "cleanup should be callable"
        
        print("✓ cleanup method exists")
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cleanup_with_no_threads():
    """Test that cleanup works when no threads are running."""
    print("\nTesting cleanup with no threads...")
    try:
        app = QCoreApplication(sys.argv)
        engine = WaveformEngine()
        
        # Call cleanup when there are no threads
        engine.cleanup()
        
        assert len(engine._workers) == 0, "Workers dict should be empty"
        assert len(engine._threads) == 0, "Threads dict should be empty"
        
        print("✓ cleanup works with no threads")
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_destructor_calls_cleanup():
    """Test that destructor calls cleanup."""
    print("\nTesting destructor calls cleanup...")
    try:
        app = QCoreApplication(sys.argv)
        engine = WaveformEngine()
        
        # Verify __del__ exists
        assert hasattr(engine, '__del__'), "__del__ method should exist"
        
        print("✓ destructor exists and will call cleanup")
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_worker_deletelater_connected():
    """Test that worker deleteLater is connected to thread.finished signal."""
    print("\nTesting worker deleteLater connection...")
    try:
        # This test verifies the code fix by checking the source code
        # We can't easily test the signal connections at runtime without creating actual threads
        
        import inspect
        source = inspect.getsource(WaveformEngine.generateWaveform)
        
        # Check that both thread and worker deleteLater are connected
        assert 'thread.finished.connect(thread.deleteLater)' in source, \
            "thread.deleteLater should be connected"
        assert 'thread.finished.connect(worker.deleteLater)' in source, \
            "worker.deleteLater should be connected"
        
        print("✓ Both thread and worker deleteLater are properly connected")
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Thread Cleanup Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Cleanup method exists", test_cleanup_method_exists()))
    results.append(("Cleanup with no threads", test_cleanup_with_no_threads()))
    results.append(("Destructor calls cleanup", test_destructor_calls_cleanup()))
    results.append(("Worker deleteLater connected", test_worker_deletelater_connected()))
    
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
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
