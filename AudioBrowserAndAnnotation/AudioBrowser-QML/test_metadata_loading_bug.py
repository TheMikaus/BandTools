#!/usr/bin/env python3
"""
Test to demonstrate the metadata loading bug.

BUG: When using annotation sets (new format), the FileManager's _load_takes_metadata()
method doesn't read best_take, partial_take, and other metadata from the annotation sets.
It only reads from the old .takes_metadata.json format.

This causes the library view to not show the correct indicators for best takes,
partial takes, and important annotations when annotation sets are in use.
"""

import sys
import tempfile
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_metadata_loading_from_sets():
    """Test that FileManager loads metadata from annotation sets."""
    print("Testing Metadata Loading from Annotation Sets...")
    print("=" * 80)
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir)
        print(f"\n✓ Created test directory: {test_dir}")
        
        # Create test audio files
        audio_file1 = test_dir / "song1.wav"
        audio_file2 = test_dir / "song2.wav"
        audio_file3 = test_dir / "song3.wav"
        audio_file1.touch()
        audio_file2.touch()
        audio_file3.touch()
        print("✓ Created 3 test audio files")
        
        # Create annotation sets file with metadata (new format)
        sets_data = {
            "version": 3,
            "updated": "2024-01-01T00:00:00",
            "sets": [
                {
                    "id": "set1",
                    "name": "TestUser",
                    "color": "#00cc66",
                    "visible": True,
                    "folder_notes": "",
                    "files": {
                        "song1.wav": {
                            "general": "",
                            "best_take": True,  # This should be read by FileManager
                            "partial_take": False,
                            "reference_song": False,
                            "notes": [
                                {
                                    "uid": 1,
                                    "ms": 1000,
                                    "text": "Important note",
                                    "important": True  # This should trigger hasImportantAnnotation
                                }
                            ]
                        },
                        "song2.wav": {
                            "general": "",
                            "best_take": False,
                            "partial_take": True,  # This should be read by FileManager
                            "reference_song": False,
                            "notes": []
                        },
                        "song3.wav": {
                            "general": "",
                            "best_take": False,
                            "partial_take": False,
                            "reference_song": False,
                            "notes": []
                        }
                    }
                }
            ],
            "current_set_id": "set1"
        }
        
        sets_file = test_dir / ".audio_notes_TestUser.json"
        with open(sets_file, 'w') as f:
            json.dump(sets_data, f, indent=2)
        print("✓ Created annotation sets file with metadata")
        print(f"  - song1.wav: best_take=True, has important annotation")
        print(f"  - song2.wav: partial_take=True")
        print(f"  - song3.wav: no special flags")
        
        # Now try to load with FileManager
        try:
            from PyQt6.QtCore import QCoreApplication
            from backend.file_manager import FileManager
            
            app = QCoreApplication(sys.argv)
            file_manager = FileManager()
            
            # Load the directory (should load metadata)
            file_manager.setCurrentDirectory(str(test_dir))
            print("\n✓ FileManager loaded directory")
            
            # Check if metadata was loaded correctly
            is_best_1 = file_manager.isBestTake(str(audio_file1))
            is_best_2 = file_manager.isBestTake(str(audio_file2))
            is_partial_1 = file_manager.isPartialTake(str(audio_file1))
            is_partial_2 = file_manager.isPartialTake(str(audio_file2))
            
            print("\nChecking metadata loaded by FileManager:")
            print(f"  song1.wav - isBestTake: {is_best_1} (expected: True)")
            print(f"  song2.wav - isBestTake: {is_best_2} (expected: False)")
            print(f"  song1.wav - isPartialTake: {is_partial_1} (expected: False)")
            print(f"  song2.wav - isPartialTake: {is_partial_2} (expected: True)")
            
            # Check if the bug exists
            if not is_best_1:
                print("\n❌ BUG CONFIRMED: FileManager did NOT load best_take from annotation sets!")
                print("   Expected song1.wav to be marked as best take, but it's not.")
                return 1
            
            if not is_partial_2:
                print("\n❌ BUG CONFIRMED: FileManager did NOT load partial_take from annotation sets!")
                print("   Expected song2.wav to be marked as partial take, but it's not.")
                return 1
            
            print("\n✅ Metadata loaded correctly from annotation sets!")
            return 0
            
        except ImportError as e:
            print(f"\n⚠️  Cannot run test: {e}")
            print("   PyQt6 not installed - skipping test")
            return 0
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            return 1


if __name__ == "__main__":
    sys.exit(test_metadata_loading_from_sets())
