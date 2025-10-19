#!/usr/bin/env python3
"""
Test script for hidden song functionality.

Tests that the FileManager can:
1. Mark/unmark songs as hidden
2. Persist hidden song state to .takes_metadata.json
3. Load hidden song state from .takes_metadata.json
4. Check if a song is hidden
"""

import sys
import json
import tempfile
from pathlib import Path

def test_hidden_songs():
    """Test hidden song functionality."""
    print("=" * 60)
    print("Testing Hidden Song Functionality")
    print("=" * 60)
    
    # Test imports
    print("\n1. Testing module imports...")
    try:
        from backend.file_manager import FileManager
        from backend.models import FileListModel
        print("   ✓ Modules imported successfully")
    except Exception as e:
        print(f"   ✗ Failed to import modules: {e}")
        return False
    
    # Test FileManager has hidden song methods
    print("\n2. Testing FileManager has hidden song methods...")
    try:
        fm = FileManager()
        assert hasattr(fm, 'markAsHidden'), "FileManager missing markAsHidden method"
        assert hasattr(fm, 'unmarkAsHidden'), "FileManager missing unmarkAsHidden method"
        assert hasattr(fm, 'isHidden'), "FileManager missing isHidden method"
        assert hasattr(fm, '_hidden_songs'), "FileManager missing _hidden_songs attribute"
        print("   ✓ FileManager has all hidden song methods")
    except Exception as e:
        print(f"   ✗ FileManager missing methods: {e}")
        return False
    
    # Test FileListModel has IsHidden role
    print("\n3. Testing FileListModel has IsHidden role...")
    try:
        assert hasattr(FileListModel, 'IsHiddenRole'), "FileListModel missing IsHiddenRole"
        print("   ✓ FileListModel has IsHidden role")
    except Exception as e:
        print(f"   ✗ FileListModel missing role: {e}")
        return False
    
    # Test marking/unmarking files as hidden
    print("\n4. Testing mark/unmark as hidden...")
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create a test audio file
            test_file = tmppath / "test_song.wav"
            test_file.write_text("fake audio data")
            
            fm = FileManager()
            
            # Initially not hidden
            assert not fm.isHidden(str(test_file)), "File should not be hidden initially"
            print("   ✓ File not hidden initially")
            
            # Mark as hidden
            fm.markAsHidden(str(test_file))
            assert fm.isHidden(str(test_file)), "File should be hidden after marking"
            print("   ✓ File marked as hidden successfully")
            
            # Unmark as hidden
            fm.unmarkAsHidden(str(test_file))
            assert not fm.isHidden(str(test_file)), "File should not be hidden after unmarking"
            print("   ✓ File unmarked as hidden successfully")
            
    except Exception as e:
        print(f"   ✗ Mark/unmark test failed: {e}")
        return False
    
    # Test persistence to .takes_metadata.json
    print("\n5. Testing persistence to .takes_metadata.json...")
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create test audio files
            test_file1 = tmppath / "song1.wav"
            test_file2 = tmppath / "song2.wav"
            test_file1.write_text("fake audio data 1")
            test_file2.write_text("fake audio data 2")
            
            fm = FileManager()
            
            # Mark one file as hidden
            fm.markAsHidden(str(test_file1))
            
            # Check that .takes_metadata.json was created
            metadata_file = tmppath / ".takes_metadata.json"
            assert metadata_file.exists(), ".takes_metadata.json not created"
            
            # Load and verify contents
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            assert "hidden_songs" in metadata, "metadata missing hidden_songs key"
            assert "song1.wav" in metadata["hidden_songs"], "song1.wav not in hidden_songs list"
            assert "song2.wav" not in metadata["hidden_songs"], "song2.wav should not be in hidden_songs list"
            print("   ✓ Hidden songs persisted to .takes_metadata.json")
            
            # Test loading from file
            fm2 = FileManager()
            fm2._load_takes_for_directory(tmppath)
            
            assert fm2.isHidden(str(test_file1)), "song1.wav should be loaded as hidden"
            assert not fm2.isHidden(str(test_file2)), "song2.wav should not be loaded as hidden"
            print("   ✓ Hidden songs loaded from .takes_metadata.json")
            
    except Exception as e:
        print(f"   ✗ Persistence test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test FileListModel includes hidden status
    print("\n6. Testing FileListModel includes hidden status...")
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create test audio file
            test_file = tmppath / "test.wav"
            test_file.write_text("fake audio data")
            
            fm = FileManager()
            fm.markAsHidden(str(test_file))
            
            model = FileListModel(file_manager=fm)
            model.setFiles([str(test_file)])
            
            # Check that the model has the file
            assert model.rowCount() == 1, "Model should have 1 file"
            
            # Check that isHidden role returns True
            index = model.index(0, 0)
            is_hidden = model.data(index, FileListModel.IsHiddenRole)
            assert is_hidden == True, "File should be marked as hidden in model"
            print("   ✓ FileListModel includes hidden status")
            
    except Exception as e:
        print(f"   ✗ FileListModel test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_hidden_songs()
    sys.exit(0 if success else 1)
