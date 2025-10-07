#!/usr/bin/env python3
"""
Test metadata loading from original AudioBrowser JSON files.
"""

import sys
import json
import tempfile
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

def test_provided_names_loading():
    """Test loading of .provided_names.json file."""
    print("Testing .provided_names.json loading...")
    
    # Import FileManager (but don't create QObject yet)
    from backend.file_manager import FileManager
    
    # Create a temporary directory with test data
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test audio file
        test_file = temp_path / "test_audio.wav"
        test_file.touch()
        
        # Create .provided_names.json
        names_data = {
            "test_audio.wav": "My Custom Song Name",
            "test_audio": "My Custom Song Name"  # Also test stem matching
        }
        names_file = temp_path / ".provided_names.json"
        with open(names_file, 'w') as f:
            json.dump(names_data, f)
        
        # Create FileManager instance (can't test Qt signals in headless mode)
        # Instead, test the private methods directly
        fm = FileManager()
        
        # Test _load_provided_names
        loaded_names = fm._load_provided_names(temp_path)
        if loaded_names == names_data:
            print("  ✓ Provided names loaded correctly")
        else:
            print(f"  ✗ Provided names mismatch: {loaded_names}")
            return False
        
        # Test getProvidedName
        name = fm.getProvidedName(str(test_file))
        if name == "My Custom Song Name":
            print("  ✓ getProvidedName works correctly")
        else:
            print(f"  ✗ getProvidedName returned: {name}")
            return False
    
    return True


def test_duration_cache_loading():
    """Test loading of .duration_cache.json file."""
    print("\nTesting .duration_cache.json loading...")
    
    from backend.file_manager import FileManager
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test audio file
        test_file = temp_path / "song.mp3"
        test_file.touch()
        
        # Create .duration_cache.json (in milliseconds)
        duration_data = {
            "song.mp3": 180000,  # 3 minutes in milliseconds
            "song": 180000
        }
        cache_file = temp_path / ".duration_cache.json"
        with open(cache_file, 'w') as f:
            json.dump(duration_data, f)
        
        # Create FileManager instance
        fm = FileManager()
        
        # Test _load_duration_cache
        loaded_cache = fm._load_duration_cache(temp_path)
        if loaded_cache == duration_data:
            print("  ✓ Duration cache loaded correctly")
        else:
            print(f"  ✗ Duration cache mismatch: {loaded_cache}")
            return False
        
        # Test getCachedDuration
        duration = fm.getCachedDuration(str(test_file))
        if duration == 180000:
            print("  ✓ getCachedDuration works correctly")
        else:
            print(f"  ✗ getCachedDuration returned: {duration}")
            return False
    
    return True


def test_duration_cache_seconds_conversion():
    """Test conversion of duration cache in seconds to milliseconds."""
    print("\nTesting duration cache seconds to milliseconds conversion...")
    
    from backend.file_manager import FileManager
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test audio file
        test_file = temp_path / "old_format.wav"
        test_file.touch()
        
        # Create .duration_cache.json in old format (seconds)
        duration_data = {
            "old_format.wav": 180.5,  # 180.5 seconds
        }
        cache_file = temp_path / ".duration_cache.json"
        with open(cache_file, 'w') as f:
            json.dump(duration_data, f)
        
        # Create FileManager instance
        fm = FileManager()
        
        # Test _load_duration_cache converts to milliseconds
        loaded_cache = fm._load_duration_cache(temp_path)
        expected_ms = 180500  # 180.5 seconds = 180500 milliseconds
        if "old_format.wav" in loaded_cache and loaded_cache["old_format.wav"] == expected_ms:
            print("  ✓ Duration cache converted from seconds to milliseconds")
        else:
            print(f"  ✗ Duration cache conversion failed: {loaded_cache}")
            return False
    
    return True


def test_missing_metadata_files():
    """Test behavior when metadata files don't exist."""
    print("\nTesting missing metadata files...")
    
    from backend.file_manager import FileManager
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test audio file but no metadata files
        test_file = temp_path / "no_metadata.wav"
        test_file.touch()
        
        # Create FileManager instance
        fm = FileManager()
        
        # Test getProvidedName with no metadata
        name = fm.getProvidedName(str(test_file))
        if name == "":
            print("  ✓ getProvidedName returns empty string when no metadata")
        else:
            print(f"  ✗ getProvidedName returned: {name}")
            return False
        
        # Test getCachedDuration with no metadata
        duration = fm.getCachedDuration(str(test_file))
        if duration == 0:
            print("  ✓ getCachedDuration returns 0 when no metadata")
        else:
            print(f"  ✗ getCachedDuration returned: {duration}")
            return False
    
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Metadata Loading Test Suite")
    print("=" * 60)
    
    provided_names_ok = test_provided_names_loading()
    duration_cache_ok = test_duration_cache_loading()
    seconds_conversion_ok = test_duration_cache_seconds_conversion()
    missing_files_ok = test_missing_metadata_files()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    print(f"Provided Names Loading: {'✓ PASS' if provided_names_ok else '✗ FAIL'}")
    print(f"Duration Cache Loading: {'✓ PASS' if duration_cache_ok else '✗ FAIL'}")
    print(f"Seconds Conversion: {'✓ PASS' if seconds_conversion_ok else '✗ FAIL'}")
    print(f"Missing Metadata Files: {'✓ PASS' if missing_files_ok else '✗ FAIL'}")
    
    if provided_names_ok and duration_cache_ok and seconds_conversion_ok and missing_files_ok:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
