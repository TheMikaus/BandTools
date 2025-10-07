#!/usr/bin/env python3
"""
Test Practice Statistics Backend Module

Tests the practice statistics generation logic without requiring QML/Qt.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Mock PyQt6 for testing without Qt installed
class MockQObject:
    def __init__(self):
        pass

class MockSignal:
    def __init__(self, *args):
        pass
    
    def emit(self, *args):
        pass
    
    def connect(self, *args):
        pass

def mock_slot(*args, **kwargs):
    def decorator(func):
        return func
    return decorator

# Create mock modules
class MockQtCore:
    QObject = MockQObject
    pyqtSignal = MockSignal
    pyqtSlot = mock_slot

class MockPyQt6:
    QtCore = MockQtCore()

# Install mocks
sys.modules['PyQt6'] = MockPyQt6()
sys.modules['PyQt6.QtCore'] = MockQtCore()

# Import the statistics functions (not the QObject)
from backend.practice_statistics import (
    discover_directories_with_audio_files,
    load_json,
    AUDIO_EXTS,
    NAMES_JSON
)


def test_discover_directories():
    """Test directory discovery function."""
    print("Testing directory discovery...")
    
    # Create test directory structure
    test_root = Path("/tmp/test_practice_stats")
    test_root.mkdir(exist_ok=True)
    
    # Create some test directories
    practice1 = test_root / "2024-01-15-Practice"
    practice1.mkdir(exist_ok=True)
    
    # Create audio files
    (practice1 / "song1.wav").touch()
    (practice1 / "song2.mp3").touch()
    
    practice2 = test_root / "2024-01-20-Session"
    practice2.mkdir(exist_ok=True)
    (practice2 / "song3.wav").touch()
    
    # Empty directory (should be skipped)
    empty_dir = test_root / "empty"
    empty_dir.mkdir(exist_ok=True)
    
    # Discover directories
    discovered = discover_directories_with_audio_files(test_root)
    
    print(f"  ✓ Found {len(discovered)} directories with audio files")
    
    # Check that we found the right directories
    assert len(discovered) == 2, f"Expected 2 directories, found {len(discovered)}"
    assert practice1 in discovered, "practice1 not found"
    assert practice2 in discovered, "practice2 not found"
    assert empty_dir not in discovered, "empty dir should not be included"
    
    # Cleanup
    for f in practice1.iterdir():
        f.unlink()
    for f in practice2.iterdir():
        f.unlink()
    practice1.rmdir()
    practice2.rmdir()
    empty_dir.rmdir()
    test_root.rmdir()
    
    print("  ✓ Directory discovery works correctly")
    return True


def test_json_loading():
    """Test JSON loading function."""
    print("Testing JSON loading...")
    
    test_file = Path("/tmp/test_stats.json")
    
    # Test with non-existent file
    result = load_json(test_file, {"default": True})
    assert result == {"default": True}, "Default not returned for missing file"
    
    # Test with valid JSON
    test_data = {"songs": ["song1", "song2"], "count": 2}
    with open(test_file, 'w') as f:
        json.dump(test_data, f)
    
    result = load_json(test_file)
    assert result == test_data, "JSON not loaded correctly"
    
    # Cleanup
    test_file.unlink()
    
    print("  ✓ JSON loading works correctly")
    return True


def test_statistics_structure():
    """Test that we can import and create the structure."""
    print("Testing statistics module structure...")
    
    # Test that we can import the main class (even if we can't instantiate it without Qt)
    try:
        from backend.practice_statistics import PracticeStatistics
        print("  ✓ PracticeStatistics class can be imported")
    except Exception as e:
        print(f"  ✗ Failed to import PracticeStatistics: {e}")
        return False
    
    # Test constants
    assert ".wav" in AUDIO_EXTS, "WAV extension not in AUDIO_EXTS"
    assert ".mp3" in AUDIO_EXTS, "MP3 extension not in AUDIO_EXTS"
    assert NAMES_JSON == ".provided_names.json", "NAMES_JSON constant incorrect"
    
    print("  ✓ Module structure is correct")
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Practice Statistics Backend Test Suite")
    print("=" * 60)
    
    tests = [
        test_statistics_structure,
        test_json_loading,
        test_discover_directories,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"  ✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
