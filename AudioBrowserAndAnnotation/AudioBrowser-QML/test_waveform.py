#!/usr/bin/env python3
"""
Waveform Backend Test Script

Tests the waveform engine and view backend modules.
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all required imports work."""
    print("Testing imports...")
    try:
        from PyQt6.QtCore import QObject, pyqtSignal
        from PyQt6.QtGui import QGuiApplication
        from backend.waveform_engine import WaveformEngine, WaveformWorker
        from backend.waveform_view import WaveformView
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_waveform_engine():
    """Test WaveformEngine instantiation."""
    print("\nTesting WaveformEngine...")
    try:
        from PyQt6.QtCore import QCoreApplication
        from backend.waveform_engine import WaveformEngine
        
        app = QCoreApplication(sys.argv)
        engine = WaveformEngine()
        
        # Test basic methods
        assert hasattr(engine, 'generateWaveform')
        assert hasattr(engine, 'isWaveformReady')
        assert hasattr(engine, 'getWaveformData')
        assert hasattr(engine, 'setCacheDirectory')
        
        # Test signals
        assert hasattr(engine, 'waveformReady')
        assert hasattr(engine, 'waveformProgress')
        assert hasattr(engine, 'waveformError')
        
        print("✓ WaveformEngine instantiation successful")
        print("✓ All required methods present")
        print("✓ All required signals present")
        return True
    except Exception as e:
        print(f"✗ WaveformEngine test failed: {e}")
        return False

def test_waveform_view():
    """Test WaveformView instantiation."""
    print("\nTesting WaveformView...")
    try:
        from PyQt6.QtGui import QGuiApplication
        from backend.waveform_view import WaveformView
        
        app = QGuiApplication(sys.argv)
        view = WaveformView()
        
        # Test properties
        assert hasattr(view, 'peaks')
        assert hasattr(view, 'durationMs')
        assert hasattr(view, 'positionMs')
        assert hasattr(view, 'backgroundColor')
        assert hasattr(view, 'waveformColor')
        assert hasattr(view, 'playheadColor')
        
        # Test signals
        assert hasattr(view, 'seekRequested')
        
        # Test methods
        assert hasattr(view, 'paint')
        
        print("✓ WaveformView instantiation successful")
        print("✓ All required properties present")
        print("✓ All required signals present")
        print("✓ Paint method present")
        return True
    except Exception as e:
        print(f"✗ WaveformView test failed: {e}")
        return False

def test_waveform_worker():
    """Test WaveformWorker basic functionality."""
    print("\nTesting WaveformWorker...")
    try:
        from backend.waveform_engine import WaveformWorker
        
        # Create worker with dummy path
        worker = WaveformWorker("/tmp/test.wav", 2000)
        
        # Test signals
        assert hasattr(worker, 'progress')
        assert hasattr(worker, 'finished')
        assert hasattr(worker, 'error')
        
        # Test methods
        assert hasattr(worker, 'run')
        assert hasattr(worker, 'cancel')
        
        print("✓ WaveformWorker instantiation successful")
        print("✓ All required signals present")
        print("✓ All required methods present")
        return True
    except Exception as e:
        print(f"✗ WaveformWorker test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Waveform Backend Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    
    if results[0][1]:  # Only continue if imports work
        results.append(("WaveformEngine", test_waveform_engine()))
        results.append(("WaveformView", test_waveform_view()))
        results.append(("WaveformWorker", test_waveform_worker()))
    
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
