#!/usr/bin/env python3
"""
Test suite for Now Playing Panel implementation
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_backend_settings():
    """Test that SettingsManager has Now Playing panel methods."""
    from backend.settings_manager import SettingsManager
    
    sm = SettingsManager()
    
    # Test getting collapsed state (should have default)
    collapsed = sm.getNowPlayingCollapsed()
    assert isinstance(collapsed, bool), "getNowPlayingCollapsed should return bool"
    
    # Test setting collapsed state
    sm.setNowPlayingCollapsed(True)
    assert sm.getNowPlayingCollapsed() == True, "setNowPlayingCollapsed should persist"
    
    sm.setNowPlayingCollapsed(False)
    assert sm.getNowPlayingCollapsed() == False, "setNowPlayingCollapsed should update"
    
    print("✓ PASS: Backend settings methods work correctly")


def test_mini_waveform_qml_syntax():
    """Test that MiniWaveformWidget.qml has correct syntax."""
    qml_file = Path(__file__).parent / "qml" / "components" / "MiniWaveformWidget.qml"
    
    assert qml_file.exists(), f"MiniWaveformWidget.qml not found at {qml_file}"
    
    content = qml_file.read_text()
    
    # Check required imports
    assert "import QtQuick" in content, "Missing QtQuick import"
    assert "import AudioBrowser" in content, "Missing AudioBrowser import"
    
    # Check for WaveformView usage
    assert "WaveformView" in content, "Missing WaveformView component"
    
    # Check for required properties
    assert "property string filePath" in content, "Missing filePath property"
    assert "property int positionMs" in content, "Missing positionMs property"
    
    # Check balanced braces
    assert content.count('{') == content.count('}'), "Mismatched braces"
    
    print("✓ PASS: MiniWaveformWidget.qml syntax is correct")


def test_now_playing_panel_qml_syntax():
    """Test that NowPlayingPanel.qml has correct syntax."""
    qml_file = Path(__file__).parent / "qml" / "components" / "NowPlayingPanel.qml"
    
    assert qml_file.exists(), f"NowPlayingPanel.qml not found at {qml_file}"
    
    content = qml_file.read_text()
    
    # Check required imports
    assert "import QtQuick" in content, "Missing QtQuick import"
    assert "import QtQuick.Controls.Basic" in content, "Missing Controls import"
    assert "import QtQuick.Layouts" in content, "Missing Layouts import"
    
    # Check for MiniWaveformWidget usage
    assert "MiniWaveformWidget" in content, "Missing MiniWaveformWidget component"
    
    # Check for required components
    assert "StyledButton" in content, "Missing StyledButton component"
    assert "StyledTextField" in content, "Missing StyledTextField component"
    
    # Check for collapsed property
    assert "property bool collapsed" in content, "Missing collapsed property"
    
    # Check for annotation signal
    assert "signal annotationRequested" in content, "Missing annotationRequested signal"
    
    # Check for settings integration
    assert "settingsManager.getNowPlayingCollapsed" in content, "Missing getNowPlayingCollapsed call"
    assert "settingsManager.setNowPlayingCollapsed" in content, "Missing setNowPlayingCollapsed call"
    
    # Check balanced braces
    assert content.count('{') == content.count('}'), "Mismatched braces"
    
    print("✓ PASS: NowPlayingPanel.qml syntax is correct")


def test_main_qml_integration():
    """Test that main.qml integrates Now Playing Panel."""
    qml_file = Path(__file__).parent / "qml" / "main.qml"
    
    assert qml_file.exists(), f"main.qml not found at {qml_file}"
    
    content = qml_file.read_text()
    
    # Check for NowPlayingPanel declaration
    assert "NowPlayingPanel {" in content, "Missing NowPlayingPanel declaration"
    assert "id: nowPlayingPanel" in content, "Missing nowPlayingPanel id"
    
    # Check for annotation handler
    assert "onAnnotationRequested" in content, "Missing onAnnotationRequested handler"
    
    # Check for View menu integration
    assert "Toggle Now Playing Panel" in content, "Missing menu item for Now Playing Panel"
    assert "nowPlayingPanel.collapsed" in content, "Missing collapsed state reference"
    
    # Check balanced braces
    assert content.count('{') == content.count('}'), "Mismatched braces"
    
    print("✓ PASS: main.qml integration is correct")


def test_all():
    """Run all tests."""
    print("Running Now Playing Panel Tests...")
    print()
    
    test_backend_settings()
    test_mini_waveform_qml_syntax()
    test_now_playing_panel_qml_syntax()
    test_main_qml_integration()
    
    print()
    print("=" * 60)
    print("All tests passed! (4/4)")
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
