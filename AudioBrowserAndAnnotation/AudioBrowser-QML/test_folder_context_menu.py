#!/usr/bin/env python3
"""
Test script for folder context menu features.

Tests the new folder reference/ignore functionality in fingerprint_engine.py
"""

import sys
import tempfile
from pathlib import Path

# Add parent directory to path to import backend modules
sys.path.insert(0, str(Path(__file__).parent))

from backend.fingerprint_engine import (
    is_folder_reference,
    toggle_folder_reference,
    is_folder_ignored,
    toggle_folder_ignore,
    load_fingerprint_cache,
    save_fingerprint_cache,
)


def test_folder_reference():
    """Test folder reference functionality."""
    print("Testing folder reference functionality...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        folder_path = Path(tmpdir)
        
        # Initially should not be a reference folder
        assert not is_folder_reference(folder_path), "Folder should not be reference initially"
        print("✓ Initial state: not a reference folder")
        
        # Toggle to make it a reference folder
        result = toggle_folder_reference(folder_path)
        assert result is True, "Toggle should return True when making folder a reference"
        assert is_folder_reference(folder_path), "Folder should now be a reference folder"
        print("✓ After toggle: is now a reference folder")
        
        # Toggle again to remove reference status
        result = toggle_folder_reference(folder_path)
        assert result is False, "Toggle should return False when removing reference status"
        assert not is_folder_reference(folder_path), "Folder should no longer be a reference folder"
        print("✓ After second toggle: is no longer a reference folder")
        
        # Verify persistence - load cache and check
        cache = load_fingerprint_cache(folder_path)
        assert "is_reference_folder" in cache, "Cache should have is_reference_folder key"
        assert cache["is_reference_folder"] is False, "Cache should show reference status as False"
        print("✓ Reference status is persisted in cache")


def test_folder_ignore():
    """Test folder ignore functionality."""
    print("\nTesting folder ignore functionality...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        folder_path = Path(tmpdir)
        
        # Initially should not be ignored
        assert not is_folder_ignored(folder_path), "Folder should not be ignored initially"
        print("✓ Initial state: not ignored")
        
        # Toggle to make it ignored
        result = toggle_folder_ignore(folder_path)
        assert result is True, "Toggle should return True when making folder ignored"
        assert is_folder_ignored(folder_path), "Folder should now be ignored"
        print("✓ After toggle: is now ignored")
        
        # Toggle again to remove ignored status
        result = toggle_folder_ignore(folder_path)
        assert result is False, "Toggle should return False when removing ignored status"
        assert not is_folder_ignored(folder_path), "Folder should no longer be ignored"
        print("✓ After second toggle: is no longer ignored")
        
        # Verify persistence - load cache and check
        cache = load_fingerprint_cache(folder_path)
        assert "ignore_fingerprints" in cache, "Cache should have ignore_fingerprints key"
        assert cache["ignore_fingerprints"] is False, "Cache should show ignore status as False"
        print("✓ Ignore status is persisted in cache")


def test_combined_flags():
    """Test that both flags can be set independently."""
    print("\nTesting combined flags...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        folder_path = Path(tmpdir)
        
        # Set both flags
        toggle_folder_reference(folder_path)
        toggle_folder_ignore(folder_path)
        
        assert is_folder_reference(folder_path), "Folder should be a reference"
        assert is_folder_ignored(folder_path), "Folder should be ignored"
        print("✓ Both flags can be set independently")
        
        # Remove one flag
        toggle_folder_reference(folder_path)
        
        assert not is_folder_reference(folder_path), "Folder should no longer be a reference"
        assert is_folder_ignored(folder_path), "Folder should still be ignored"
        print("✓ Flags are independent of each other")


def test_cache_structure():
    """Test that cache structure is preserved."""
    print("\nTesting cache structure...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        folder_path = Path(tmpdir)
        
        # Create a cache with existing data
        cache = {
            "version": 1,
            "files": {"test.wav": {"duration": 123}},
            "excluded_files": ["excluded.wav"]
        }
        save_fingerprint_cache(folder_path, cache)
        
        # Toggle reference status
        toggle_folder_reference(folder_path)
        
        # Load and verify cache structure is preserved
        loaded_cache = load_fingerprint_cache(folder_path)
        assert loaded_cache["version"] == 1, "Version should be preserved"
        assert "test.wav" in loaded_cache["files"], "Files data should be preserved"
        assert "excluded.wav" in loaded_cache["excluded_files"], "Excluded files should be preserved"
        assert loaded_cache["is_reference_folder"] is True, "Reference flag should be set"
        print("✓ Existing cache structure is preserved when adding new flags")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Folder Context Menu Backend Functionality")
    print("=" * 60)
    
    try:
        test_folder_reference()
        test_folder_ignore()
        test_combined_flags()
        test_cache_structure()
        
        print("\n" + "=" * 60)
        print("All tests passed! ✓")
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
