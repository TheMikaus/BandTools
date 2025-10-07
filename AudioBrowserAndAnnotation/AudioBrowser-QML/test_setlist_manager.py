#!/usr/bin/env python3
"""
Test Suite for SetlistManager

Tests the setlist management functionality for AudioBrowser QML.

Author: AI-assisted development
Date: January 2025
"""

import sys
import json
import tempfile
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtCore import QCoreApplication
from backend.setlist_manager import SetlistManager


def test_setlist_manager_initialization():
    """Test SetlistManager initialization."""
    print("\n=== Test 1: SetlistManager Initialization ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        root_path = Path(tmpdir)
        manager = SetlistManager(root_path)
        
        assert manager.root_path == root_path
        assert isinstance(manager.setlists, dict)
        assert len(manager.setlists) == 0
        print("✓ SetlistManager initialized successfully")


def test_create_setlist():
    """Test creating a new setlist."""
    print("\n=== Test 2: Create Setlist ===")
    
    app = QCoreApplication(sys.argv)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        root_path = Path(tmpdir)
        manager = SetlistManager(root_path)
        
        # Create a setlist
        success = manager.createSetlist("Summer Tour 2024")
        assert success, "Failed to create setlist"
        assert len(manager.setlists) == 1
        
        # Get the setlist
        setlist_id = list(manager.setlists.keys())[0]
        setlist = manager.setlists[setlist_id]
        
        assert setlist["name"] == "Summer Tour 2024"
        assert setlist["songs"] == []
        assert setlist["notes"] == ""
        assert "created_date" in setlist
        assert "last_modified" in setlist
        
        # Test empty name (should fail)
        success = manager.createSetlist("")
        assert not success, "Should not create setlist with empty name"
        assert len(manager.setlists) == 1
        
        print("✓ Setlist created successfully")
        print(f"  - Setlist ID: {setlist_id}")
        print(f"  - Name: {setlist['name']}")


def test_rename_setlist():
    """Test renaming a setlist."""
    print("\n=== Test 3: Rename Setlist ===")
    
    app = QCoreApplication(sys.argv)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        root_path = Path(tmpdir)
        manager = SetlistManager(root_path)
        
        # Create and rename
        manager.createSetlist("Old Name")
        setlist_id = list(manager.setlists.keys())[0]
        
        success = manager.renameSetlist(setlist_id, "New Name")
        assert success, "Failed to rename setlist"
        assert manager.setlists[setlist_id]["name"] == "New Name"
        
        # Test invalid ID
        success = manager.renameSetlist("invalid-id", "Test")
        assert not success, "Should not rename non-existent setlist"
        
        print("✓ Setlist renamed successfully")


def test_delete_setlist():
    """Test deleting a setlist."""
    print("\n=== Test 4: Delete Setlist ===")
    
    app = QCoreApplication(sys.argv)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        root_path = Path(tmpdir)
        manager = SetlistManager(root_path)
        
        # Create and delete
        manager.createSetlist("To Be Deleted")
        setlist_id = list(manager.setlists.keys())[0]
        assert len(manager.setlists) == 1
        
        success = manager.deleteSetlist(setlist_id)
        assert success, "Failed to delete setlist"
        assert len(manager.setlists) == 0
        
        # Test invalid ID
        success = manager.deleteSetlist("invalid-id")
        assert not success, "Should not delete non-existent setlist"
        
        print("✓ Setlist deleted successfully")


def test_add_remove_songs():
    """Test adding and removing songs."""
    print("\n=== Test 5: Add and Remove Songs ===")
    
    app = QCoreApplication(sys.argv)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        root_path = Path(tmpdir)
        manager = SetlistManager(root_path)
        
        # Create setlist
        manager.createSetlist("Test Setlist")
        setlist_id = list(manager.setlists.keys())[0]
        
        # Add songs
        success = manager.addSong(setlist_id, "practice_2024_01_01", "01_Song1.mp3")
        assert success, "Failed to add song"
        assert len(manager.setlists[setlist_id]["songs"]) == 1
        
        success = manager.addSong(setlist_id, "practice_2024_01_02", "02_Song2.mp3")
        assert success, "Failed to add second song"
        assert len(manager.setlists[setlist_id]["songs"]) == 2
        
        # Try to add duplicate
        success = manager.addSong(setlist_id, "practice_2024_01_01", "01_Song1.mp3")
        assert not success, "Should not add duplicate song"
        assert len(manager.setlists[setlist_id]["songs"]) == 2
        
        # Remove song
        success = manager.removeSong(setlist_id, 0)
        assert success, "Failed to remove song"
        assert len(manager.setlists[setlist_id]["songs"]) == 1
        
        # Test invalid index
        success = manager.removeSong(setlist_id, 10)
        assert not success, "Should not remove with invalid index"
        
        print("✓ Songs added and removed successfully")


def test_move_songs():
    """Test reordering songs."""
    print("\n=== Test 6: Move Songs ===")
    
    app = QCoreApplication(sys.argv)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        root_path = Path(tmpdir)
        manager = SetlistManager(root_path)
        
        # Create setlist with songs
        manager.createSetlist("Test Setlist")
        setlist_id = list(manager.setlists.keys())[0]
        
        manager.addSong(setlist_id, "folder1", "song1.mp3")
        manager.addSong(setlist_id, "folder2", "song2.mp3")
        manager.addSong(setlist_id, "folder3", "song3.mp3")
        
        songs = manager.setlists[setlist_id]["songs"]
        assert songs[0]["filename"] == "song1.mp3"
        assert songs[1]["filename"] == "song2.mp3"
        assert songs[2]["filename"] == "song3.mp3"
        
        # Move song from index 0 to index 2
        success = manager.moveSong(setlist_id, 0, 2)
        assert success, "Failed to move song"
        
        songs = manager.setlists[setlist_id]["songs"]
        assert songs[0]["filename"] == "song2.mp3"
        assert songs[1]["filename"] == "song3.mp3"
        assert songs[2]["filename"] == "song1.mp3"
        
        print("✓ Songs moved successfully")


def test_update_notes():
    """Test updating performance notes."""
    print("\n=== Test 7: Update Notes ===")
    
    app = QCoreApplication(sys.argv)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        root_path = Path(tmpdir)
        manager = SetlistManager(root_path)
        
        # Create setlist
        manager.createSetlist("Test Setlist")
        setlist_id = list(manager.setlists.keys())[0]
        
        # Update notes
        notes = "Key: D major, Tuning: Drop D"
        success = manager.updateNotes(setlist_id, notes)
        assert success, "Failed to update notes"
        assert manager.setlists[setlist_id]["notes"] == notes
        
        print("✓ Notes updated successfully")


def test_persistence():
    """Test saving and loading setlists."""
    print("\n=== Test 8: Persistence ===")
    
    app = QCoreApplication(sys.argv)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        root_path = Path(tmpdir)
        
        # Create and save
        manager1 = SetlistManager(root_path)
        manager1.createSetlist("Persisted Setlist")
        setlist_id = list(manager1.setlists.keys())[0]
        manager1.addSong(setlist_id, "folder1", "song1.mp3")
        manager1.updateNotes(setlist_id, "Test notes")
        
        # Load in new instance
        manager2 = SetlistManager(root_path)
        assert len(manager2.setlists) == 1
        
        loaded_setlist = manager2.setlists[setlist_id]
        assert loaded_setlist["name"] == "Persisted Setlist"
        assert len(loaded_setlist["songs"]) == 1
        assert loaded_setlist["notes"] == "Test notes"
        
        print("✓ Setlists persisted and loaded successfully")


def test_validate_setlist():
    """Test setlist validation."""
    print("\n=== Test 9: Validate Setlist ===")
    
    app = QCoreApplication(sys.argv)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        root_path = Path(tmpdir)
        manager = SetlistManager(root_path)
        
        # Create setlist with non-existent files
        manager.createSetlist("Test Setlist")
        setlist_id = list(manager.setlists.keys())[0]
        manager.addSong(setlist_id, "nonexistent_folder", "missing.mp3")
        
        # Validate
        result_json = manager.validateSetlist(setlist_id)
        result = json.loads(result_json)
        
        assert not result["valid"], "Setlist should be invalid (missing files)"
        assert result["total_songs"] == 1
        assert len(result["missing_files"]) == 1
        assert result["missing_files"][0]["filename"] == "missing.mp3"
        
        print("✓ Setlist validation working correctly")


def test_get_all_setlists_json():
    """Test getting all setlists as JSON."""
    print("\n=== Test 10: Get All Setlists JSON ===")
    
    app = QCoreApplication(sys.argv)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        root_path = Path(tmpdir)
        manager = SetlistManager(root_path)
        
        # Create multiple setlists
        manager.createSetlist("Setlist 1")
        manager.createSetlist("Setlist 2")
        manager.createSetlist("Setlist 3")
        
        # Get JSON
        json_str = manager.getAllSetlistsJson()
        setlists = json.loads(json_str)
        
        assert len(setlists) == 3
        assert all("id" in s for s in setlists)
        assert all("name" in s for s in setlists)
        assert all("songCount" in s for s in setlists)
        
        print("✓ getAllSetlistsJson working correctly")
        print(f"  - Returned {len(setlists)} setlists")


def test_export_to_text():
    """Test exporting setlist to text file."""
    print("\n=== Test 11: Export to Text ===")
    
    app = QCoreApplication(sys.argv)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        root_path = Path(tmpdir)
        manager = SetlistManager(root_path)
        
        # Create setlist with songs
        manager.createSetlist("Export Test")
        setlist_id = list(manager.setlists.keys())[0]
        manager.addSong(setlist_id, "folder1", "song1.mp3")
        manager.addSong(setlist_id, "folder2", "song2.mp3")
        manager.updateNotes(setlist_id, "Test performance notes")
        
        # Export
        output_path = Path(tmpdir) / "setlist.txt"
        success = manager.exportToText(setlist_id, str(output_path))
        assert success, "Failed to export setlist"
        assert output_path.exists(), "Export file not created"
        
        # Check content
        content = output_path.read_text(encoding='utf-8')
        assert "SETLIST: Export Test" in content
        assert "Test performance notes" in content
        assert "song1.mp3" in content
        assert "song2.mp3" in content
        
        print("✓ Setlist exported successfully")


def run_all_tests():
    """Run all tests."""
    print("=" * 70)
    print("SETLIST MANAGER TEST SUITE")
    print("=" * 70)
    
    try:
        test_setlist_manager_initialization()
        test_create_setlist()
        test_rename_setlist()
        test_delete_setlist()
        test_add_remove_songs()
        test_move_songs()
        test_update_notes()
        test_persistence()
        test_validate_setlist()
        test_get_all_setlists_json()
        test_export_to_text()
        
        print("\n" + "=" * 70)
        print("ALL TESTS PASSED! ✓")
        print("=" * 70)
        return True
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
