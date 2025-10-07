#!/usr/bin/env python3
"""
Test suite for spectrogram functionality.

Tests spectrogram computation, toggle functionality, and integration.
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def test_imports():
    """Test that all required imports are available."""
    print("Test 1: Import test...")
    
    try:
        from waveform_view import WaveformView, HAVE_NUMPY
        print(f"  ✓ WaveformView imported successfully")
        print(f"  ✓ NumPy available: {HAVE_NUMPY}")
        return True
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        return False


def test_spectrogram_properties():
    """Test that spectrogram properties exist on WaveformView."""
    print("\nTest 2: Spectrogram properties test...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from waveform_view import WaveformView
        
        # Create QApplication if needed
        app = QApplication.instance() or QApplication(sys.argv)
        
        # Create WaveformView instance
        waveform = WaveformView()
        
        # Check spectrogram properties
        assert hasattr(waveform, '_show_spectrogram'), "Missing _show_spectrogram attribute"
        assert hasattr(waveform, '_spectrogram_data'), "Missing _spectrogram_data attribute"
        assert hasattr(waveform, '_current_audio_file'), "Missing _current_audio_file attribute"
        
        # Check initial values
        assert waveform._show_spectrogram == False, "Initial show_spectrogram should be False"
        assert waveform._spectrogram_data is None, "Initial spectrogram_data should be None"
        assert waveform._current_audio_file == "", "Initial current_audio_file should be empty"
        
        print("  ✓ All spectrogram properties exist with correct initial values")
        return True
        
    except Exception as e:
        print(f"  ✗ Properties test failed: {e}")
        return False


def test_spectrogram_toggle():
    """Test toggling spectrogram mode."""
    print("\nTest 3: Spectrogram toggle test...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from waveform_view import WaveformView
        
        # Create QApplication if needed
        app = QApplication.instance() or QApplication(sys.argv)
        
        # Create WaveformView instance
        waveform = WaveformView()
        
        # Test toggling
        assert waveform._show_spectrogram == False, "Should start disabled"
        
        # Enable spectrogram
        waveform.showSpectrogram = True
        assert waveform._show_spectrogram == True, "Should be enabled after setting to True"
        
        # Disable spectrogram
        waveform.showSpectrogram = False
        assert waveform._show_spectrogram == False, "Should be disabled after setting to False"
        
        print("  ✓ Spectrogram toggle works correctly")
        return True
        
    except Exception as e:
        print(f"  ✗ Toggle test failed: {e}")
        return False


def test_spectrogram_methods():
    """Test that spectrogram-related methods exist."""
    print("\nTest 4: Spectrogram methods test...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from waveform_view import WaveformView
        
        # Create QApplication if needed
        app = QApplication.instance() or QApplication(sys.argv)
        
        # Create WaveformView instance
        waveform = WaveformView()
        
        # Check methods exist
        assert hasattr(waveform, 'setAudioFile'), "Missing setAudioFile method"
        assert hasattr(waveform, '_compute_spectrogram'), "Missing _compute_spectrogram method"
        assert hasattr(waveform, '_load_audio_samples'), "Missing _load_audio_samples method"
        assert hasattr(waveform, '_draw_spectrogram'), "Missing _draw_spectrogram method"
        
        # Check methods are callable
        assert callable(waveform.setAudioFile), "setAudioFile should be callable"
        assert callable(waveform._compute_spectrogram), "_compute_spectrogram should be callable"
        assert callable(waveform._load_audio_samples), "_load_audio_samples should be callable"
        assert callable(waveform._draw_spectrogram), "_draw_spectrogram should be callable"
        
        print("  ✓ All spectrogram methods exist and are callable")
        return True
        
    except Exception as e:
        print(f"  ✗ Methods test failed: {e}")
        return False


def test_set_audio_file():
    """Test setting audio file path."""
    print("\nTest 5: Set audio file test...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from waveform_view import WaveformView
        
        # Create QApplication if needed
        app = QApplication.instance() or QApplication(sys.argv)
        
        # Create WaveformView instance
        waveform = WaveformView()
        
        # Set audio file
        test_file = "/path/to/test.wav"
        waveform.setAudioFile(test_file)
        
        assert waveform._current_audio_file == test_file, "Audio file path should be set"
        
        # Setting different file should clear spectrogram data
        waveform._spectrogram_data = [[1, 2, 3]]  # Fake data
        waveform.setAudioFile("/path/to/different.wav")
        
        assert waveform._spectrogram_data is None, "Spectrogram data should be cleared on file change"
        
        print("  ✓ setAudioFile works correctly")
        return True
        
    except Exception as e:
        print(f"  ✗ Set audio file test failed: {e}")
        return False


def test_paint_integration():
    """Test that paint method handles spectrogram mode."""
    print("\nTest 6: Paint integration test...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QPainter, QImage
        from waveform_view import WaveformView
        
        # Create QApplication if needed
        app = QApplication.instance() or QApplication(sys.argv)
        
        # Create WaveformView instance
        waveform = WaveformView()
        waveform.setWidth(800)
        waveform.setHeight(400)
        
        # Create test image and painter
        image = QImage(800, 400, QImage.Format.Format_ARGB32)
        painter = QPainter(image)
        
        # Test normal mode (should not crash)
        waveform._show_spectrogram = False
        try:
            waveform.paint(painter)
            print("  ✓ Paint in waveform mode works")
        except Exception as e:
            print(f"  ✗ Paint in waveform mode failed: {e}")
            return False
        
        # Test spectrogram mode without data (should fallback gracefully)
        waveform._show_spectrogram = True
        waveform._spectrogram_data = None
        try:
            waveform.paint(painter)
            print("  ✓ Paint in spectrogram mode (no data) works")
        except Exception as e:
            print(f"  ✗ Paint in spectrogram mode (no data) failed: {e}")
            return False
        
        painter.end()
        print("  ✓ Paint integration test passed")
        return True
        
    except Exception as e:
        print(f"  ✗ Paint integration test failed: {e}")
        return False


def run_all_tests():
    """Run all tests and report results."""
    print("=" * 60)
    print("Spectrogram Feature Test Suite")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_spectrogram_properties,
        test_spectrogram_toggle,
        test_spectrogram_methods,
        test_set_audio_file,
        test_paint_integration,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ✗ Test crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    if all(results):
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
