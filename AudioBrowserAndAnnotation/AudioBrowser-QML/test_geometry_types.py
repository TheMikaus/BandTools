#!/usr/bin/env python3
"""
Test script to verify geometry methods return proper types for QML compatibility.

This test validates that getGeometry() and getSplitterState() return strings
instead of None or bytes, which prevents TypeError in PyQt6 QML bridge.
"""

import sys
import os
from pathlib import Path

# Mock PyQt6 classes for testing without GUI
class MockQSettings:
    def __init__(self, *args):
        self.data = {}
    
    def value(self, key, default=None, type=None):
        return self.data.get(key, default)
    
    def setValue(self, key, value):
        self.data[key] = value

class MockQObject:
    def __init__(self):
        pass

class MockQThread:
    def __init__(self):
        pass

class MockSignal:
    def emit(self, *args):
        pass
    def connect(self, *args):
        pass

def mock_pyqtSignal(*args, **kwargs):
    return MockSignal()

def mock_pyqtSlot(*args, **kwargs):
    def decorator(func):
        return func
    return decorator

# Install mocks
class MockQtCore:
    QObject = MockQObject
    QSettings = MockQSettings
    QThread = MockQThread
    pyqtSignal = staticmethod(mock_pyqtSignal)
    pyqtSlot = staticmethod(mock_pyqtSlot)

class MockPyQt6:
    QtCore = MockQtCore()

sys.modules['PyQt6'] = MockPyQt6()
sys.modules['PyQt6.QtCore'] = MockQtCore()

# Now we can import the module
from backend.settings_manager import SettingsManager


def test_geometry_methods():
    """Test that geometry methods return proper types."""
    print("Testing geometry methods...")
    
    # Create settings manager
    settings = SettingsManager()
    
    # Test getGeometry when no value is saved
    geometry = settings.getGeometry()
    print(f"  getGeometry() returned: {repr(geometry)}")
    assert isinstance(geometry, str), f"Expected str, got {type(geometry)}"
    assert geometry == "", f"Expected empty string, got {repr(geometry)}"
    print("  ✓ getGeometry() returns empty string when no value saved")
    
    # Test setGeometry with string
    test_json = '{"x": 100, "y": 200, "width": 800, "height": 600}'
    settings.setGeometry(test_json)
    print(f"  setGeometry() called with: {repr(test_json)}")
    
    # Test getGeometry returns the saved value
    geometry = settings.getGeometry()
    print(f"  getGeometry() returned: {repr(geometry)}")
    assert isinstance(geometry, str), f"Expected str, got {type(geometry)}"
    assert geometry == test_json, f"Expected {repr(test_json)}, got {repr(geometry)}"
    print("  ✓ getGeometry() returns saved string value")
    
    # Test getSplitterState when no value is saved
    splitter = settings.getSplitterState()
    print(f"  getSplitterState() returned: {repr(splitter)}")
    assert isinstance(splitter, str), f"Expected str, got {type(splitter)}"
    assert splitter == "", f"Expected empty string, got {repr(splitter)}"
    print("  ✓ getSplitterState() returns empty string when no value saved")
    
    # Test setSplitterState with string
    test_state = "some,splitter,state"
    settings.setSplitterState(test_state)
    print(f"  setSplitterState() called with: {repr(test_state)}")
    
    # Test getSplitterState returns the saved value
    splitter = settings.getSplitterState()
    print(f"  getSplitterState() returned: {repr(splitter)}")
    assert isinstance(splitter, str), f"Expected str, got {type(splitter)}"
    assert splitter == test_state, f"Expected {repr(test_state)}, got {repr(splitter)}"
    print("  ✓ getSplitterState() returns saved string value")
    
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Geometry Methods Type Safety Test")
    print("=" * 60)
    
    try:
        result = test_geometry_methods()
        
        print("\n" + "=" * 60)
        if result:
            print("✅ All tests passed!")
            print("=" * 60)
            print("\nThe geometry methods now return proper string types")
            print("that are compatible with QML JSON operations.")
            return 0
        else:
            print("❌ Tests failed!")
            print("=" * 60)
            return 1
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
