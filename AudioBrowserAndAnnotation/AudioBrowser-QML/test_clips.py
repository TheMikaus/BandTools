#!/usr/bin/env python3
"""
Test script for ClipManager functionality.

Tests basic CRUD operations without requiring GUI.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.clip_manager import ClipManager


def test_clip_manager():
    """Test ClipManager basic functionality."""
    print("Testing ClipManager...")
    
    # Create manager
    manager = ClipManager()
    print("✓ ClipManager created")
    
    # Test file: Set a dummy audio file
    test_file = "/tmp/test_audio.wav"
    manager.setCurrentFile(test_file)
    assert manager.getCurrentFile() == test_file
    print("✓ setCurrentFile/getCurrentFile works")
    
    # Test add clip
    success = manager.addClip(1000, 5000, "Test Clip", "Test notes")
    assert success, "Failed to add clip"
    print("✓ addClip works")
    
    # Test get clips
    clips = manager.getClips()
    assert len(clips) == 1, f"Expected 1 clip, got {len(clips)}"
    assert clips[0]["start_ms"] == 1000
    assert clips[0]["end_ms"] == 5000
    assert clips[0]["name"] == "Test Clip"
    assert clips[0]["notes"] == "Test notes"
    assert clips[0]["duration_ms"] == 4000
    print("✓ getClips works")
    
    # Test get clip by index
    clip = manager.getClip(0)
    assert clip["start_ms"] == 1000
    print("✓ getClip works")
    
    # Test clip count
    count = manager.getClipCount()
    assert count == 1
    print("✓ getClipCount works")
    
    # Test update clip
    success = manager.updateClip(0, 2000, 6000, "Updated Clip", "Updated notes")
    assert success, "Failed to update clip"
    clip = manager.getClip(0)
    assert clip["start_ms"] == 2000
    assert clip["end_ms"] == 6000
    assert clip["name"] == "Updated Clip"
    assert clip["duration_ms"] == 4000
    print("✓ updateClip works")
    
    # Test add second clip
    success = manager.addClip(7000, 10000, "Second Clip", "")
    assert success, "Failed to add second clip"
    assert manager.getClipCount() == 2
    print("✓ Multiple clips work")
    
    # Test delete clip
    success = manager.deleteClip(0)
    assert success, "Failed to delete clip"
    assert manager.getClipCount() == 1
    clip = manager.getClip(0)
    assert clip["name"] == "Second Clip"
    print("✓ deleteClip works")
    
    # Test clear clips
    success = manager.clearClips()
    assert success, "Failed to clear clips"
    assert manager.getClipCount() == 0
    print("✓ clearClips works")
    
    # Test validation - negative timestamps
    success = manager.addClip(-1000, 5000, "Invalid", "")
    assert not success, "Should reject negative start time"
    print("✓ Validation: rejects negative timestamps")
    
    # Test validation - start >= end
    success = manager.addClip(5000, 5000, "Invalid", "")
    assert not success, "Should reject start >= end"
    success = manager.addClip(6000, 5000, "Invalid", "")
    assert not success, "Should reject start > end"
    print("✓ Validation: rejects invalid time ranges")
    
    # Test empty file path
    manager.setCurrentFile("")
    success = manager.addClip(1000, 5000, "Test", "")
    assert not success, "Should reject operations with no file"
    print("✓ Validation: rejects operations without file")
    
    print("\n✅ All ClipManager tests passed!")
    return True


def test_persistence():
    """Test JSON persistence."""
    print("\nTesting persistence...")
    
    # Create temporary file
    import tempfile
    import os
    temp_dir = tempfile.mkdtemp()
    test_file = os.path.join(temp_dir, "test.wav")
    
    # Create dummy audio file
    Path(test_file).touch()
    
    # Create manager and add clips
    manager1 = ClipManager()
    manager1.setCurrentFile(test_file)
    manager1.addClip(1000, 5000, "Clip 1", "Note 1")
    manager1.addClip(6000, 10000, "Clip 2", "Note 2")
    print(f"✓ Created 2 clips for {test_file}")
    
    # Create new manager and load same file
    manager2 = ClipManager()
    manager2.setCurrentFile(test_file)
    
    # Verify clips were loaded
    clips = manager2.getClips()
    assert len(clips) == 2, f"Expected 2 clips, got {len(clips)}"
    assert clips[0]["name"] == "Clip 1"
    assert clips[1]["name"] == "Clip 2"
    print("✓ Clips persisted and loaded correctly")
    
    # Cleanup
    clips_file = Path(temp_dir) / ".test_clips.json"
    if clips_file.exists():
        clips_file.unlink()
    Path(test_file).unlink()
    os.rmdir(temp_dir)
    print("✓ Cleanup successful")
    
    print("\n✅ Persistence tests passed!")
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("ClipManager Test Suite")
    print("=" * 60)
    print()
    
    try:
        test_clip_manager()
        test_persistence()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
