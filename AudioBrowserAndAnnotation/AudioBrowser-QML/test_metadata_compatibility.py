#!/usr/bin/env python3
"""
Test script to verify backward compatibility with legacy metadata files.
"""

import sys
import json
from pathlib import Path
import tempfile
import shutil


def test_legacy_audio_notes_format():
    """Test that legacy .audio_notes_*.json files are loaded correctly."""
    print("\n=== Testing Legacy Audio Notes Format ===\n")
    
    # Create a temporary directory structure
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir) / "test_practice"
        test_dir.mkdir()
        
        # Create some dummy audio files
        (test_dir / "song1.wav").touch()
        (test_dir / "song2.wav").touch()
        (test_dir / "song3.wav").touch()
        
        # Create legacy .audio_notes_user.json file
        legacy_notes = {
            "song1.wav": {
                "best_take": True,
                "partial_take": False,
                "annotations": []
            },
            "song2.wav": {
                "best_take": False,
                "partial_take": True,
                "annotations": []
            },
            "song3.wav": {
                "best_take": True,
                "partial_take": True,
                "annotations": []
            }
        }
        
        notes_file = test_dir / ".audio_notes_testuser.json"
        with open(notes_file, 'w') as f:
            json.dump(legacy_notes, f, indent=2)
        
        print(f"✓ Created test directory: {test_dir}")
        print(f"✓ Created legacy notes file: {notes_file}")
        
        # Test loading with FileManager
        sys.path.insert(0, str(Path(__file__).parent / "backend"))
        from file_manager import FileManager
        from PyQt6.QtCore import QCoreApplication
        
        app = QCoreApplication(sys.argv)
        file_manager = FileManager()
        
        # Load takes metadata
        file_manager.setCurrentDirectory(str(test_dir))
        
        # Check best takes
        best_takes = file_manager.getBestTakes()
        print(f"\nBest takes loaded: {len(best_takes)}")
        for take in best_takes:
            print(f"  - {Path(take).name}")
        
        # Check partial takes
        partial_takes = file_manager.getPartialTakes()
        print(f"\nPartial takes loaded: {len(partial_takes)}")
        for take in partial_takes:
            print(f"  - {Path(take).name}")
        
        # Verify results
        assert len(best_takes) == 2, f"Expected 2 best takes, got {len(best_takes)}"
        assert len(partial_takes) == 2, f"Expected 2 partial takes, got {len(partial_takes)}"
        
        print("\n✓ Legacy audio notes format loaded correctly!")
        return True


def test_new_takes_metadata_format():
    """Test that new .takes_metadata.json format works."""
    print("\n=== Testing New Takes Metadata Format ===\n")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir) / "test_practice"
        test_dir.mkdir()
        
        # Create some dummy audio files
        (test_dir / "song1.mp3").touch()
        (test_dir / "song2.mp3").touch()
        
        # Create new .takes_metadata.json file
        new_metadata = {
            "best_takes": ["song1.mp3"],
            "partial_takes": ["song2.mp3"]
        }
        
        metadata_file = test_dir / ".takes_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(new_metadata, f, indent=2)
        
        print(f"✓ Created test directory: {test_dir}")
        print(f"✓ Created new metadata file: {metadata_file}")
        
        # Test loading with FileManager
        sys.path.insert(0, str(Path(__file__).parent / "backend"))
        from file_manager import FileManager
        from PyQt6.QtCore import QCoreApplication
        
        app = QCoreApplication(sys.argv)
        file_manager = FileManager()
        
        # Load takes metadata
        file_manager.setCurrentDirectory(str(test_dir))
        
        # Check best takes
        best_takes = file_manager.getBestTakes()
        print(f"\nBest takes loaded: {len(best_takes)}")
        for take in best_takes:
            print(f"  - {Path(take).name}")
        
        # Check partial takes
        partial_takes = file_manager.getPartialTakes()
        print(f"\nPartial takes loaded: {len(partial_takes)}")
        for take in partial_takes:
            print(f"  - {Path(take).name}")
        
        # Verify results
        assert len(best_takes) == 1, f"Expected 1 best take, got {len(best_takes)}"
        assert len(partial_takes) == 1, f"Expected 1 partial take, got {len(partial_takes)}"
        
        print("\n✓ New takes metadata format loaded correctly!")
        return True


def test_provided_names():
    """Test that .provided_names.json is loaded correctly."""
    print("\n=== Testing Provided Names ===\n")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir) / "test_practice"
        test_dir.mkdir()
        
        # Create some dummy audio files
        (test_dir / "rec001.wav").touch()
        (test_dir / "rec002.wav").touch()
        
        # Create .provided_names.json
        provided_names = {
            "rec001.wav": "Amazing Song",
            "rec002.wav": "Cool Tune"
        }
        
        names_file = test_dir / ".provided_names.json"
        with open(names_file, 'w') as f:
            json.dump(provided_names, f, indent=2)
        
        print(f"✓ Created test directory: {test_dir}")
        print(f"✓ Created provided names file: {names_file}")
        
        # Test loading with FileManager
        sys.path.insert(0, str(Path(__file__).parent / "backend"))
        from file_manager import FileManager
        from PyQt6.QtCore import QCoreApplication
        
        app = QCoreApplication(sys.argv)
        file_manager = FileManager()
        
        # Test getting provided names
        name1 = file_manager.getProvidedName(str(test_dir / "rec001.wav"))
        name2 = file_manager.getProvidedName(str(test_dir / "rec002.wav"))
        
        print(f"\nProvided names:")
        print(f"  rec001.wav -> '{name1}'")
        print(f"  rec002.wav -> '{name2}'")
        
        assert name1 == "Amazing Song", f"Expected 'Amazing Song', got '{name1}'"
        assert name2 == "Cool Tune", f"Expected 'Cool Tune', got '{name2}'"
        
        print("\n✓ Provided names loaded correctly!")
        return True


def test_duration_cache():
    """Test that .duration_cache.json is loaded correctly."""
    print("\n=== Testing Duration Cache ===\n")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir) / "test_practice"
        test_dir.mkdir()
        
        # Create some dummy audio files
        (test_dir / "track1.mp3").touch()
        (test_dir / "track2.mp3").touch()
        
        # Create .duration_cache.json (old format uses seconds)
        duration_cache = {
            "track1.mp3": 180.5,  # 180.5 seconds
            "track2.mp3": 245.2   # 245.2 seconds
        }
        
        cache_file = test_dir / ".duration_cache.json"
        with open(cache_file, 'w') as f:
            json.dump(duration_cache, f, indent=2)
        
        print(f"✓ Created test directory: {test_dir}")
        print(f"✓ Created duration cache file: {cache_file}")
        
        # Test loading with FileManager
        sys.path.insert(0, str(Path(__file__).parent / "backend"))
        from file_manager import FileManager
        from PyQt6.QtCore import QCoreApplication
        
        app = QCoreApplication(sys.argv)
        file_manager = FileManager()
        
        # Test getting cached durations
        duration1 = file_manager.getCachedDuration(str(test_dir / "track1.mp3"))
        duration2 = file_manager.getCachedDuration(str(test_dir / "track2.mp3"))
        
        print(f"\nCached durations (in milliseconds):")
        print(f"  track1.mp3 -> {duration1} ms ({duration1/1000:.1f} seconds)")
        print(f"  track2.mp3 -> {duration2} ms ({duration2/1000:.1f} seconds)")
        
        # Verify conversion from seconds to milliseconds
        assert duration1 == 180500, f"Expected 180500 ms, got {duration1} ms"
        assert duration2 == 245200, f"Expected 245200 ms, got {duration2} ms"
        
        print("\n✓ Duration cache loaded and converted correctly!")
        return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Metadata Compatibility Test Suite")
    print("=" * 60)
    
    try:
        # Run tests
        test_legacy_audio_notes_format()
        test_new_takes_metadata_format()
        test_provided_names()
        test_duration_cache()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
