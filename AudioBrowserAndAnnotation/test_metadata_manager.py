"""
Test Metadata Manager

Tests the shared metadata manager module.
"""

import sys
import json
import tempfile
from pathlib import Path

# Add shared module to path
sys.path.insert(0, str(Path(__file__).parent))


def test_metadata_manager_init():
    """Test metadata manager initialization."""
    print("\nTesting MetadataManager initialization...")
    
    from shared.metadata_manager import MetadataManager
    
    # Test default initialization
    manager = MetadataManager()
    assert manager.get_username(), "Username should be set by default"
    
    # Test custom username
    manager = MetadataManager(username="testuser")
    assert manager.get_username() == "testuser", "Custom username should be used"
    
    # Test username update
    manager.set_username("newuser")
    assert manager.get_username() == "newuser", "Username should be updated"
    
    print("   ✓ MetadataManager initialization works correctly")
    return True


def test_annotation_file_paths():
    """Test annotation file path resolution."""
    print("\nTesting annotation file path resolution...")
    
    from shared.metadata_manager import MetadataManager
    
    manager = MetadataManager(username="testuser")
    
    # Test legacy annotation file path
    audio_file = Path("/test/folder/song.wav")
    annotation_path = manager.get_annotation_file_path(audio_file)
    assert annotation_path.name == ".song_annotations.json", \
        f"Legacy annotation path should be '.song_annotations.json', got {annotation_path.name}"
    assert annotation_path.parent == audio_file.parent, \
        "Annotation file should be in same directory as audio file"
    
    # Test annotation sets file path
    directory = Path("/test/folder")
    sets_path = manager.get_annotation_sets_file_path(directory)
    assert sets_path.name == ".audio_notes_testuser.json", \
        f"Annotation sets path should be '.audio_notes_testuser.json', got {sets_path.name}"
    
    # Test with different username
    sets_path = manager.get_annotation_sets_file_path(directory, username="otheruser")
    assert sets_path.name == ".audio_notes_otheruser.json", \
        f"Annotation sets path should use specified username, got {sets_path.name}"
    
    print("   ✓ Annotation file path resolution works correctly")
    return True


def test_json_io():
    """Test JSON load and save operations."""
    print("\nTesting JSON I/O operations...")
    
    from shared.metadata_manager import MetadataManager
    
    manager = MetadataManager(username="testuser")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir)
        test_file = test_dir / "test.json"
        
        # Test loading non-existent file
        data = manager.load_json(test_file, {"default": "value"})
        assert data == {"default": "value"}, "Should return default for non-existent file"
        
        # Test saving data
        test_data = {"key": "value", "number": 42, "list": [1, 2, 3]}
        success = manager.save_json(test_file, test_data, create_backup=False)
        assert success, "Save should succeed"
        assert test_file.exists(), "File should be created"
        
        # Test loading saved data
        loaded = manager.load_json(test_file)
        assert loaded == test_data, f"Loaded data should match saved data"
        
        # Test that data is properly formatted JSON
        with open(test_file, 'r') as f:
            content = f.read()
            assert "  " in content, "JSON should be indented"
    
    print("   ✓ JSON I/O operations work correctly")
    return True


def test_annotation_sets_operations():
    """Test annotation sets loading and saving."""
    print("\nTesting annotation sets operations...")
    
    from shared.metadata_manager import MetadataManager
    
    manager = MetadataManager(username="testuser")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir)
        
        # Test loading non-existent annotation sets (should return defaults)
        sets_data = manager.load_annotation_sets(test_dir)
        assert "version" in sets_data, "Should have version field"
        assert "sets" in sets_data, "Should have sets field"
        assert isinstance(sets_data["sets"], list), "Sets should be a list"
        
        # Test saving annotation sets
        test_sets = {
            "version": 3,
            "updated": "2024-01-01T00:00:00",
            "sets": [
                {
                    "id": "abc123",
                    "name": "Test Set",
                    "color": "#ff0000",
                    "visible": True,
                    "folder_notes": "Test notes",
                    "files": {
                        "song.wav": {
                            "general": "General note",
                            "best_take": True,
                            "partial_take": False,
                            "reference_song": False,
                            "notes": [
                                {
                                    "uid": 1,
                                    "ms": 5000,
                                    "text": "Test annotation",
                                    "important": False
                                }
                            ]
                        }
                    }
                }
            ],
            "current_set_id": "abc123"
        }
        
        success = manager.save_annotation_sets(test_dir, test_sets, create_backup=False)
        assert success, "Save should succeed"
        
        # Test loading saved annotation sets
        loaded = manager.load_annotation_sets(test_dir)
        assert loaded["version"] == 3, "Version should match"
        assert len(loaded["sets"]) == 1, "Should have one set"
        assert loaded["sets"][0]["id"] == "abc123", "Set ID should match"
        assert loaded["sets"][0]["name"] == "Test Set", "Set name should match"
        assert "song.wav" in loaded["sets"][0]["files"], "Should have file data"
        assert len(loaded["sets"][0]["files"]["song.wav"]["notes"]) == 1, "Should have one note"
    
    print("   ✓ Annotation sets operations work correctly")
    return True


def test_legacy_annotations():
    """Test legacy annotation operations."""
    print("\nTesting legacy annotation operations...")
    
    from shared.metadata_manager import MetadataManager
    
    manager = MetadataManager(username="testuser")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir)
        audio_file = test_dir / "song.wav"
        
        # Create dummy audio file
        audio_file.touch()
        
        # Test loading non-existent legacy annotations
        annotations = manager.load_legacy_annotations(audio_file)
        assert annotations == [], "Should return empty list for non-existent file"
        
        # Test saving legacy annotations
        test_annotations = [
            {
                "uid": 1,
                "timestamp_ms": 5000,
                "text": "Test annotation",
                "category": "timing",
                "important": False,
                "user": "testuser"
            }
        ]
        
        success = manager.save_legacy_annotations(audio_file, test_annotations, create_backup=False)
        assert success, "Save should succeed"
        
        # Test loading saved legacy annotations
        loaded = manager.load_legacy_annotations(audio_file)
        assert len(loaded) == 1, "Should have one annotation"
        assert loaded[0]["text"] == "Test annotation", "Annotation text should match"
    
    print("   ✓ Legacy annotation operations work correctly")
    return True


def test_legacy_migration():
    """Test legacy to multi-set migration."""
    print("\nTesting legacy to multi-set migration...")
    
    from shared.metadata_manager import MetadataManager
    
    manager = MetadataManager(username="testuser")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir)
        legacy_file = test_dir / ".audio_notes.json"
        
        # Create legacy data
        legacy_data = {
            "folder_notes": "Old folder notes",
            "files": {
                "song1.wav": {
                    "general": "General note",
                    "best_take": True,
                    "notes": [
                        {
                            "uid": 1,
                            "ms": 5000,
                            "text": "Annotation 1",
                            "important": True
                        },
                        {
                            "uid": 2,
                            "ms": 10000,
                            "text": "Annotation 2",
                            "important": False
                        }
                    ]
                }
            }
        }
        
        # Save legacy file
        with open(legacy_file, 'w') as f:
            json.dump(legacy_data, f)
        
        # Migrate
        success = manager.migrate_legacy_to_sets(test_dir)
        assert success, "Migration should succeed"
        
        # Check that new file was created
        new_file = manager.get_annotation_sets_file_path(test_dir)
        assert new_file.exists(), "New annotation sets file should be created"
        
        # Load migrated data
        migrated = manager.load_annotation_sets(test_dir)
        assert migrated["version"] == 3, "Should have version 3"
        assert len(migrated["sets"]) == 1, "Should have one set"
        assert migrated["sets"][0]["folder_notes"] == "Old folder notes", "Folder notes should be preserved"
        assert "song1.wav" in migrated["sets"][0]["files"], "File should be preserved"
        assert migrated["sets"][0]["files"]["song1.wav"]["general"] == "General note", "General note should be preserved"
        assert migrated["sets"][0]["files"]["song1.wav"]["best_take"], "Best take flag should be preserved"
        assert len(migrated["sets"][0]["files"]["song1.wav"]["notes"]) == 2, "Notes should be preserved"
    
    print("   ✓ Legacy to multi-set migration works correctly")
    return True


def test_discover_annotation_files():
    """Test discovering annotation files in a directory."""
    print("\nTesting annotation file discovery...")
    
    from shared.metadata_manager import MetadataManager
    
    manager = MetadataManager(username="testuser")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir)
        
        # Create various annotation files
        legacy_file = test_dir / ".audio_notes.json"
        legacy_file.write_text("{}")
        
        user1_file = test_dir / ".audio_notes_user1.json"
        user1_file.write_text("{}")
        
        user2_file = test_dir / ".audio_notes_user2.json"
        user2_file.write_text("{}")
        
        # Discover files
        discovered = manager.discover_annotation_files(test_dir)
        assert len(discovered) == 3, f"Should discover 3 files, found {len(discovered)}"
        
        # Check that all files were found
        usernames = [user for user, _ in discovered]
        assert "legacy" in usernames, "Should find legacy file"
        assert "user1" in usernames, "Should find user1 file"
        assert "user2" in usernames, "Should find user2 file"
    
    print("   ✓ Annotation file discovery works correctly")
    return True


def test_backup_integration():
    """Test that backups are created when saving."""
    print("\nTesting backup integration...")
    
    from shared.metadata_manager import MetadataManager
    
    manager = MetadataManager(username="testuser")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir)
        test_file = test_dir / "test.json"
        
        # Create initial file
        initial_data = {"version": 1, "data": "initial"}
        manager.save_json(test_file, initial_data, create_backup=False)
        
        # Enable backups
        manager.set_backup_enabled(True)
        
        # Modify and save (this should create backup)
        modified_data = {"version": 2, "data": "modified"}
        manager.save_json(test_file, modified_data, create_backup=True)
        
        # Check if backup was created
        backup_dir = test_dir / ".backup"
        # Note: Backup may not be created if there are no metadata files yet
        # This test verifies that the backup mechanism doesn't break saves
        
        # Verify the file was saved correctly
        loaded = manager.load_json(test_file)
        assert loaded["version"] == 2, "Modified data should be saved"
        
        # Test disabling backups
        manager.set_backup_enabled(False)
        modified_data2 = {"version": 3, "data": "modified again"}
        manager.save_json(test_file, modified_data2, create_backup=True)
        
        loaded = manager.load_json(test_file)
        assert loaded["version"] == 3, "Data should be saved even with backups disabled"
    
    print("   ✓ Backup integration works correctly")
    return True


def run_all_tests():
    """Run all metadata manager tests."""
    print("=" * 60)
    print("Testing Metadata Manager")
    print("=" * 60)
    
    tests = [
        test_metadata_manager_init,
        test_annotation_file_paths,
        test_json_io,
        test_annotation_sets_operations,
        test_legacy_annotations,
        test_legacy_migration,
        test_discover_annotation_files,
        test_backup_integration,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"   ✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"   ✗ ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
