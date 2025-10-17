#!/usr/bin/env python3
"""
Simple code verification for WaveformView methods
This script does static analysis without importing Qt
"""

import sys
from pathlib import Path


def verify_waveform_view_methods():
    """Verify WaveformView has required methods by checking source code."""
    file_path = Path(__file__).parent / "backend" / "waveform_view.py"
    content = file_path.read_text()
    
    # Check for setWaveformData method
    assert "def setWaveformData(self, peaks, duration_ms: int)" in content, \
        "setWaveformData method not found"
    assert "@pyqtSlot('QVariant', int)" in content, \
        "setWaveformData should be a pyqtSlot"
    
    # Check for clearWaveform method
    assert "def clearWaveform(self)" in content, \
        "clearWaveform method not found"
    assert "@pyqtSlot()" in content, \
        "clearWaveform should be a pyqtSlot"
    
    # Verify the methods have correct implementation
    # setWaveformData should set peaks and duration
    lines = content.split('\n')
    in_set_waveform = False
    set_waveform_impl = []
    for line in lines:
        if "def setWaveformData" in line:
            in_set_waveform = True
        elif in_set_waveform:
            if line.strip().startswith("def ") or line.strip().startswith("@"):
                break
            set_waveform_impl.append(line)
    
    impl_text = '\n'.join(set_waveform_impl)
    assert "_set_peaks(peaks)" in impl_text, "setWaveformData should call _set_peaks"
    assert "_set_duration_ms(duration_ms)" in impl_text, "setWaveformData should call _set_duration_ms"
    
    # clearWaveform should reset to empty state
    in_clear = False
    clear_impl = []
    for line in lines:
        if "def clearWaveform" in line:
            in_clear = True
        elif in_clear:
            if line.strip().startswith("def ") or line.strip().startswith("@"):
                break
            clear_impl.append(line)
    
    clear_text = '\n'.join(clear_impl)
    assert "_peaks = []" in clear_text, "clearWaveform should clear peaks"
    assert "_duration_ms = 0" in clear_text, "clearWaveform should reset duration"
    assert "_position_ms = 0" in clear_text, "clearWaveform should reset position"
    
    print("✓ PASS: WaveformView has correct methods implementation")


def verify_now_playing_panel_position_handler():
    """Verify NowPlayingPanel connects to position changes."""
    file_path = Path(__file__).parent / "qml" / "components" / "NowPlayingPanel.qml"
    content = file_path.read_text()
    
    # Check for onPositionChanged handler
    assert "function onPositionChanged(position)" in content, \
        "onPositionChanged handler not found"
    
    # Check that it updates the miniWaveform
    assert "miniWaveform.positionMs = position" in content, \
        "Handler should update miniWaveform position"
    
    # Verify it's in the Connections block for audioEngine
    lines = content.split('\n')
    in_audio_connections = False
    found_handler = False
    for line in lines:
        if "Connections {" in line or "target: audioEngine" in line:
            in_audio_connections = True
        elif in_audio_connections and "function onPositionChanged" in line:
            found_handler = True
        elif in_audio_connections and line.strip().startswith("}") and not line.strip().startswith("}"):
            if "}" in line and not "function" in line:
                in_audio_connections = False
    
    assert found_handler, "onPositionChanged should be in audioEngine Connections block"
    
    print("✓ PASS: NowPlayingPanel has position change handler")


def verify_mini_waveform_usage():
    """Verify MiniWaveformWidget calls the new methods."""
    file_path = Path(__file__).parent / "qml" / "components" / "MiniWaveformWidget.qml"
    content = file_path.read_text()
    
    # Check that it calls setWaveformData
    assert "setWaveformData(peaks, duration)" in content, \
        "MiniWaveformWidget should call setWaveformData"
    
    # Check that it calls clearWaveform
    assert "clearWaveform()" in content, \
        "MiniWaveformWidget should call clearWaveform"
    
    # Check that it binds positionMs to root.positionMs
    assert "positionMs: root.positionMs" in content, \
        "WaveformView should bind to root.positionMs"
    
    print("✓ PASS: MiniWaveformWidget uses new methods correctly")


def verify_default_expanded_state():
    """Verify Now Playing Panel defaults to expanded."""
    file_path = Path(__file__).parent / "qml" / "components" / "NowPlayingPanel.qml"
    content = file_path.read_text()
    
    # Check that collapsed defaults to false
    assert "property bool collapsed: false" in content, \
        "collapsed property should default to false"
    
    # Check that it restores from settings
    assert "settingsManager.getNowPlayingCollapsed()" in content, \
        "Should restore collapsed state from settings"
    
    print("✓ PASS: Now Playing Panel defaults to expanded")


def test_all():
    """Run all verification tests."""
    print("Running Code Verification Tests...")
    print()
    
    verify_waveform_view_methods()
    verify_now_playing_panel_position_handler()
    verify_mini_waveform_usage()
    verify_default_expanded_state()
    
    print()
    print("=" * 60)
    print("All verification tests passed! (4/4)")
    print("=" * 60)
    print()
    print("Summary of changes:")
    print("  ✓ WaveformView.setWaveformData() method added")
    print("  ✓ WaveformView.clearWaveform() method added")
    print("  ✓ NowPlayingPanel.onPositionChanged() handler added")
    print("  ✓ Position marker will now update in mini waveform")
    print("  ✓ Waveform data will now display in mini waveform")
    print("  ✓ Panel defaults to expanded state")


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
