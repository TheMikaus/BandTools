#!/usr/bin/env python3
"""
Test WaveformView property type conversion
"""

import sys
from pathlib import Path

def test_waveform_view_peaks_property():
    """Test that WaveformView peaks property works with QVariant."""
    print("Testing WaveformView peaks property...")
    try:
        from PyQt6.QtGui import QGuiApplication
        from PyQt6.QtQml import qmlRegisterType
        from backend.waveform_view import WaveformView
        
        app = QGuiApplication(sys.argv)
        
        # Register the type
        qmlRegisterType(WaveformView, "AudioBrowser", 1, 0, "WaveformView")
        
        # Create an instance
        view = WaveformView()
        
        # Test setting peaks to None (should not crash)
        view.peaks = None
        assert view.peaks == [] or view.peaks is None, "peaks should handle None gracefully"
        
        # Test setting peaks to empty list
        view.peaks = []
        assert view.peaks == [], "peaks should be empty list"
        
        # Test setting peaks to actual data
        test_peaks = [[0.5, -0.3], [0.7, -0.5]]
        view.peaks = test_peaks
        assert view.peaks == test_peaks, f"peaks should be {test_peaks}"
        
        print("✓ WaveformView peaks property works correctly with QVariant")
        return True
    except Exception as e:
        print(f"✗ WaveformView peaks property test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_waveform_view_peaks_property()
    sys.exit(0 if success else 1)
