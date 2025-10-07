#!/usr/bin/env python3
"""
Test script to verify folder tree functionality.
"""

import sys
from pathlib import Path
import tempfile


def test_recursive_folder_discovery():
    """Test that recursive folder discovery works correctly."""
    print("\n=== Testing Recursive Folder Discovery ===\n")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a directory structure:
        # root/
        #   ├── song1.wav
        #   ├── song2.mp3
        #   ├── practice1/
        #   │   ├── take1.wav
        #   │   └── take2.wav
        #   ├── practice2/
        #   │   ├── song3.mp3
        #   │   └── subfolder/
        #   │       └── recording.wav
        #   └── empty_folder/
        
        root = Path(tmpdir)
        (root / "song1.wav").touch()
        (root / "song2.mp3").touch()
        
        practice1 = root / "practice1"
        practice1.mkdir()
        (practice1 / "take1.wav").touch()
        (practice1 / "take2.wav").touch()
        
        practice2 = root / "practice2"
        practice2.mkdir()
        (practice2 / "song3.mp3").touch()
        
        subfolder = practice2 / "subfolder"
        subfolder.mkdir()
        (subfolder / "recording.wav").touch()
        
        empty = root / "empty_folder"
        empty.mkdir()
        
        print(f"✓ Created test directory structure at: {root}")
        
        # Test with FileManager
        sys.path.insert(0, str(Path(__file__).parent / "backend"))
        from file_manager import FileManager
        from PyQt6.QtCore import QCoreApplication
        
        app = QCoreApplication(sys.argv)
        file_manager = FileManager()
        
        # Get directories with audio files
        directories = file_manager.getDirectoriesWithAudioFiles(str(root))
        
        print(f"\nDirectories with audio files: {len(directories)}")
        for dir_info in directories:
            indent = "  " * dir_info.get('level', 0)
            name = dir_info.get('name', '')
            count = dir_info.get('audioCount', 0)
            is_root = dir_info.get('isRoot', False)
            print(f"{indent}{'📁' if is_root else '📂'} {name} ({count} files)")
        
        # Verify results
        assert len(directories) == 4, f"Expected 4 directories with audio, got {len(directories)}"
        
        # Verify root has audio
        root_dir = next((d for d in directories if d.get('isRoot')), None)
        assert root_dir is not None, "Root directory not found"
        assert root_dir['audioCount'] == 2, f"Expected 2 audio files in root, got {root_dir['audioCount']}"
        
        print("\n✓ Recursive folder discovery works correctly!")
        return True


def test_folder_audio_file_discovery():
    """Test that audio files are discovered correctly in each folder."""
    print("\n=== Testing Folder Audio File Discovery ===\n")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create root with files
        (root / "root1.wav").touch()
        (root / "root2.mp3").touch()
        
        # Create subfolder with files
        sub1 = root / "recordings"
        sub1.mkdir()
        (sub1 / "rec1.wav").touch()
        (sub1 / "rec2.wav").touch()
        (sub1 / "rec3.mp3").touch()
        
        print(f"✓ Created test directory: {root}")
        
        # Test with FileManager
        sys.path.insert(0, str(Path(__file__).parent / "backend"))
        from file_manager import FileManager
        from PyQt6.QtCore import QCoreApplication
        
        app = QCoreApplication(sys.argv)
        file_manager = FileManager()
        
        # Set root directory and discover files
        file_manager.setCurrentDirectory(str(root))
        root_files = file_manager.getDiscoveredFiles()
        
        print(f"\nFiles in root: {len(root_files)}")
        for f in root_files:
            print(f"  - {Path(f).name}")
        
        # Set subfolder directory and discover files
        file_manager.setCurrentDirectory(str(sub1))
        sub_files = file_manager.getDiscoveredFiles()
        
        print(f"\nFiles in subfolder: {len(sub_files)}")
        for f in sub_files:
            print(f"  - {Path(f).name}")
        
        # Verify results
        assert len(root_files) == 2, f"Expected 2 files in root, got {len(root_files)}"
        assert len(sub_files) == 3, f"Expected 3 files in subfolder, got {len(sub_files)}"
        
        print("\n✓ Folder audio file discovery works correctly!")
        return True


def test_metadata_from_subfolder():
    """Test that metadata is loaded from the correct subfolder."""
    print("\n=== Testing Metadata from Subfolder ===\n")
    
    import json
    
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create root with metadata
        (root / "root_song.wav").touch()
        root_metadata = {"root_song.wav": "Root Song Name"}
        with open(root / ".provided_names.json", 'w') as f:
            json.dump(root_metadata, f)
        
        # Create subfolder with different metadata
        sub = root / "practice_session"
        sub.mkdir()
        (sub / "practice_song.wav").touch()
        sub_metadata = {"practice_song.wav": "Practice Song Name"}
        with open(sub / ".provided_names.json", 'w') as f:
            json.dump(sub_metadata, f)
        
        print(f"✓ Created test directory with metadata: {root}")
        
        # Test with FileManager
        sys.path.insert(0, str(Path(__file__).parent / "backend"))
        from file_manager import FileManager
        from PyQt6.QtCore import QCoreApplication
        
        app = QCoreApplication(sys.argv)
        file_manager = FileManager()
        
        # Get provided name from root file
        root_name = file_manager.getProvidedName(str(root / "root_song.wav"))
        print(f"\nRoot file name: '{root_name}'")
        
        # Get provided name from subfolder file
        sub_name = file_manager.getProvidedName(str(sub / "practice_song.wav"))
        print(f"Subfolder file name: '{sub_name}'")
        
        # Verify results
        assert root_name == "Root Song Name", f"Expected 'Root Song Name', got '{root_name}'"
        assert sub_name == "Practice Song Name", f"Expected 'Practice Song Name', got '{sub_name}'"
        
        print("\n✓ Metadata is loaded from correct subfolder!")
        return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Folder Tree Functionality Test Suite")
    print("=" * 60)
    
    try:
        # Run tests
        test_recursive_folder_discovery()
        test_folder_audio_file_discovery()
        test_metadata_from_subfolder()
        
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
