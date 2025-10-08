"""
Test Enhanced Preferences Settings

Tests the new settings added to SettingsManager for Issue #18:
- Parallel workers
- Default zoom level
- Waveform quality
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from PyQt6.QtCore import QCoreApplication
from backend.settings_manager import SettingsManager


def test_enhanced_preferences():
    """Test enhanced preferences settings in SettingsManager."""
    print("Testing Enhanced Preferences Settings...")
    
    # Create QCoreApplication (required for QSettings)
    app = QCoreApplication(sys.argv)
    
    # Create settings manager with test organization/app name
    settings = SettingsManager("TestOrg", "TestApp")
    
    # Test 1: Parallel Workers
    print("\n1. Testing Parallel Workers setting...")
    assert hasattr(settings, 'getParallelWorkers'), "Missing getParallelWorkers method"
    assert hasattr(settings, 'setParallelWorkers'), "Missing setParallelWorkers method"
    
    # Test default value
    default_workers = settings.getParallelWorkers()
    assert default_workers == 4, f"Expected default workers 4, got {default_workers}"
    print(f"   ✓ Default parallel workers: {default_workers}")
    
    # Test setting value
    settings.setParallelWorkers(8)
    workers = settings.getParallelWorkers()
    assert workers == 8, f"Expected workers 8, got {workers}"
    print(f"   ✓ Set parallel workers to: {workers}")
    
    # Test auto mode (0)
    settings.setParallelWorkers(0)
    workers = settings.getParallelWorkers()
    assert workers == 0, f"Expected workers 0 (auto), got {workers}"
    print(f"   ✓ Auto mode (0 workers): {workers}")
    
    # Test 2: Default Zoom Level
    print("\n2. Testing Default Zoom Level setting...")
    assert hasattr(settings, 'getDefaultZoom'), "Missing getDefaultZoom method"
    assert hasattr(settings, 'setDefaultZoom'), "Missing setDefaultZoom method"
    
    # Test default value
    default_zoom = settings.getDefaultZoom()
    assert default_zoom == 1, f"Expected default zoom 1, got {default_zoom}"
    print(f"   ✓ Default zoom level: {default_zoom}×")
    
    # Test setting value
    settings.setDefaultZoom(5)
    zoom = settings.getDefaultZoom()
    assert zoom == 5, f"Expected zoom 5, got {zoom}"
    print(f"   ✓ Set default zoom to: {zoom}×")
    
    # Test max value
    settings.setDefaultZoom(10)
    zoom = settings.getDefaultZoom()
    assert zoom == 10, f"Expected zoom 10, got {zoom}"
    print(f"   ✓ Max zoom level: {zoom}×")
    
    # Test 3: Waveform Quality
    print("\n3. Testing Waveform Quality setting...")
    assert hasattr(settings, 'getWaveformQuality'), "Missing getWaveformQuality method"
    assert hasattr(settings, 'setWaveformQuality'), "Missing setWaveformQuality method"
    
    # Test default value
    default_quality = settings.getWaveformQuality()
    assert default_quality == "medium", f"Expected default quality 'medium', got '{default_quality}'"
    print(f"   ✓ Default waveform quality: {default_quality}")
    
    # Test low quality
    settings.setWaveformQuality("low")
    quality = settings.getWaveformQuality()
    assert quality == "low", f"Expected quality 'low', got '{quality}'"
    print(f"   ✓ Set waveform quality to: {quality}")
    
    # Test high quality
    settings.setWaveformQuality("high")
    quality = settings.getWaveformQuality()
    assert quality == "high", f"Expected quality 'high', got '{quality}'"
    print(f"   ✓ Set waveform quality to: {quality}")
    
    # Test 4: Persistence
    print("\n4. Testing settings persistence...")
    settings.setParallelWorkers(6)
    settings.setDefaultZoom(3)
    settings.setWaveformQuality("low")
    
    # Create new settings manager instance
    settings2 = SettingsManager("TestOrg", "TestApp")
    
    # Verify persisted values
    assert settings2.getParallelWorkers() == 6, "Parallel workers not persisted"
    assert settings2.getDefaultZoom() == 3, "Default zoom not persisted"
    assert settings2.getWaveformQuality() == "low", "Waveform quality not persisted"
    print("   ✓ All settings persisted correctly")
    
    print("\n✅ All Enhanced Preferences tests passed!")
    return True


if __name__ == "__main__":
    try:
        success = test_enhanced_preferences()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
