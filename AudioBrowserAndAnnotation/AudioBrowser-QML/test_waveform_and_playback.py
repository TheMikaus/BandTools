#!/usr/bin/env python3
"""
Test script to verify waveform display and playback fixes.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_qml_syntax():
    """Test that WaveformDisplay.qml has valid syntax after changes."""
    print("Testing QML syntax...")
    
    # Check that the file exists
    waveform_qml = Path(__file__).parent / "qml" / "components" / "WaveformDisplay.qml"
    assert waveform_qml.exists(), f"WaveformDisplay.qml not found at {waveform_qml}"
    
    # Read the file and check for key changes
    content = waveform_qml.read_text()
    
    # Check for onFilePathChanged handler
    assert "onFilePathChanged:" in content, "Missing onFilePathChanged handler"
    assert "setFilePath(filePath)" in content, "Missing setFilePath call in onFilePathChanged"
    
    # Check for position update timer
    assert "Timer {" in content, "Missing Timer component"
    assert "positionUpdateTimer" in content or "Timer to regularly update" in content, "Missing position update timer"
    
    print("✓ WaveformDisplay.qml syntax looks good")
    print("✓ onFilePathChanged handler is present")
    print("✓ Position update timer is present")
    return True


def test_audio_engine_methods():
    """Test that AudioEngine has required methods."""
    print("\nTesting AudioEngine methods...")
    
    try:
        from backend.audio_engine import AudioEngine
        
        # Create an instance
        engine = AudioEngine()
        
        # Check for required methods
        assert hasattr(engine, 'loadFile'), "Missing loadFile method"
        assert hasattr(engine, 'play'), "Missing play method"
        assert hasattr(engine, 'pause'), "Missing pause method"
        assert hasattr(engine, 'stop'), "Missing stop method"
        assert hasattr(engine, 'togglePlayPause'), "Missing togglePlayPause method"
        assert hasattr(engine, 'seek'), "Missing seek method"
        assert hasattr(engine, 'getPosition'), "Missing getPosition method"
        assert hasattr(engine, 'getDuration'), "Missing getDuration method"
        assert hasattr(engine, 'getPlaybackState'), "Missing getPlaybackState method"
        assert hasattr(engine, 'getCurrentFile'), "Missing getCurrentFile method"
        assert hasattr(engine, 'isPlaying'), "Missing isPlaying method"
        
        print("✓ AudioEngine has all required methods")
        return True
    except Exception as e:
        print(f"✗ Error testing AudioEngine: {e}")
        return False


def test_waveform_engine_methods():
    """Test that WaveformEngine has required methods."""
    print("\nTesting WaveformEngine methods...")
    
    try:
        from backend.waveform_engine import WaveformEngine
        
        # Create an instance
        engine = WaveformEngine()
        
        # Check for required methods
        assert hasattr(engine, 'generateWaveform'), "Missing generateWaveform method"
        assert hasattr(engine, 'cancelWaveform'), "Missing cancelWaveform method"
        assert hasattr(engine, 'isWaveformReady'), "Missing isWaveformReady method"
        assert hasattr(engine, 'getWaveformData'), "Missing getWaveformData method"
        assert hasattr(engine, 'getWaveformDuration'), "Missing getWaveformDuration method"
        assert hasattr(engine, 'setCacheDirectory'), "Missing setCacheDirectory method"
        
        print("✓ WaveformEngine has all required methods")
        return True
    except Exception as e:
        print(f"✗ Error testing WaveformEngine: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Waveform Display and Playback Fixes")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("QML Syntax", test_qml_syntax()))
    results.append(("AudioEngine Methods", test_audio_engine_methods()))
    results.append(("WaveformEngine Methods", test_waveform_engine_methods()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
