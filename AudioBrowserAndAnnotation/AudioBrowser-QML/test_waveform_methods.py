#!/usr/bin/env python3
"""
Test suite for WaveformView methods added for Now Playing Panel
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_waveform_view_has_methods():
    """Test that WaveformView has the required methods for MiniWaveformWidget."""
    # Import the module to check methods exist
    import inspect
    from backend import waveform_view
    
    # Get the class
    waveform_class = waveform_view.WaveformView
    
    # Check that methods exist in the class
    methods = [name for name, _ in inspect.getmembers(waveform_class, predicate=inspect.isfunction)]
    
    assert 'setWaveformData' in methods, "WaveformView should have setWaveformData method"
    assert 'clearWaveform' in methods, "WaveformView should have clearWaveform method"
    assert 'setAudioFile' in methods, "WaveformView should have setAudioFile method"
    
    print("✓ PASS: WaveformView has all required methods")


def test_waveform_view_set_data():
    """Test that setWaveformData method signature is correct."""
    import inspect
    from backend import waveform_view
    
    # Get method signature
    sig = inspect.signature(waveform_view.WaveformView.setWaveformData)
    params = list(sig.parameters.keys())
    
    # Should have self, peaks, and duration_ms parameters
    assert 'peaks' in params, "setWaveformData should have 'peaks' parameter"
    assert 'duration_ms' in params, "setWaveformData should have 'duration_ms' parameter"
    
    print("✓ PASS: setWaveformData signature is correct")


def test_waveform_view_clear():
    """Test that clearWaveform method signature is correct."""
    import inspect
    from backend import waveform_view
    
    # Get method signature
    sig = inspect.signature(waveform_view.WaveformView.clearWaveform)
    params = list(sig.parameters.keys())
    
    # Should only have self parameter (no arguments)
    assert len(params) == 0, "clearWaveform should have no parameters (other than self)"
    
    print("✓ PASS: clearWaveform signature is correct")


def test_waveform_view_position():
    """Test that WaveformView has position property."""
    from backend import waveform_view
    
    # Check that the property exists
    assert hasattr(waveform_view.WaveformView, 'positionMs'), "WaveformView should have positionMs property"
    
    print("✓ PASS: Position property exists")


def test_now_playing_panel_signal_handler():
    """Test that NowPlayingPanel.qml has position signal handler."""
    qml_file = Path(__file__).parent / "qml" / "components" / "NowPlayingPanel.qml"
    
    content = qml_file.read_text()
    
    # Check for onPositionChanged handler
    assert "function onPositionChanged(position)" in content, "Missing onPositionChanged handler"
    
    # Check that it updates miniWaveform position
    assert "miniWaveform.positionMs = position" in content, "Handler should update miniWaveform.positionMs"
    
    print("✓ PASS: NowPlayingPanel has position signal handler")


def test_mini_waveform_calls_methods():
    """Test that MiniWaveformWidget calls the new methods."""
    qml_file = Path(__file__).parent / "qml" / "components" / "MiniWaveformWidget.qml"
    
    content = qml_file.read_text()
    
    # Check that it calls setWaveformData
    assert "setWaveformData(peaks, duration)" in content, "Should call setWaveformData"
    
    # Check that it calls clearWaveform
    assert "clearWaveform()" in content, "Should call clearWaveform"
    
    print("✓ PASS: MiniWaveformWidget calls new methods")


def test_all():
    """Run all tests."""
    print("Running WaveformView Methods Tests...")
    print()
    
    test_waveform_view_has_methods()
    test_waveform_view_set_data()
    test_waveform_view_clear()
    test_waveform_view_position()
    test_now_playing_panel_signal_handler()
    test_mini_waveform_calls_methods()
    
    print()
    print("=" * 60)
    print("All tests passed! (6/6)")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_all()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ FAIL: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
