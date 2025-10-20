#!/usr/bin/env python3
"""
Test to verify the annotation loading bug fix.

BUG: When using annotation sets, the setCurrentFile() method would try to load
legacy annotations, which would overwrite or interfere with the annotation sets.

FIX: Modified setCurrentFile() to check if annotation sets exist before attempting
to load legacy annotations.

This test creates annotation sets with data and verifies that setCurrentFile()
does not try to load legacy format when sets are being used.
"""

import sys
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtCore import QCoreApplication
from backend.annotation_manager import AnnotationManager


def test_annotation_loading_with_sets():
    """Test that annotations load correctly from sets, not legacy format."""
    print("Testing Annotation Loading Bug Fix...")
    print("=" * 80)
    
    # Create Qt application (required for signals)
    app = QCoreApplication(sys.argv)
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir)
        print(f"\n✓ Created test directory: {test_dir}")
        
        # Create test audio files
        audio_file1 = test_dir / "song1.wav"
        audio_file2 = test_dir / "song2.wav"
        audio_file1.touch()
        audio_file2.touch()
        print("✓ Created test audio files")
        
        # Create annotation manager
        manager = AnnotationManager()
        manager.setCurrentUser("TestUser")
        print("✓ Created annotation manager")
        
        # Set directory (should create default set)
        manager.setCurrentDirectory(test_dir)
        sets = manager.getAnnotationSets()
        assert len(sets) > 0, "No default set created"
        print(f"✓ Loaded annotation sets: {len(sets)} set(s)")
        
        # Add annotations to the set
        manager.setCurrentFile(str(audio_file1))
        manager.addAnnotation(1000, "First annotation", "timing", True, "#3498db")
        manager.addAnnotation(2000, "Second annotation", "energy", False, "#e74c3c")
        print("✓ Added 2 annotations to song1")
        
        # Verify annotations are in the set
        annotations = manager.getAnnotations()
        assert len(annotations) == 2, f"Expected 2 annotations, got {len(annotations)}"
        print(f"✓ Retrieved {len(annotations)} annotations from set")
        
        # Check that no legacy annotation file was created
        legacy_file = test_dir / ".song1_annotations.json"
        assert not legacy_file.exists(), "Legacy annotation file should not exist"
        print("✓ No legacy annotation file created (correct)")
        
        # Switch to another file and back to test setCurrentFile()
        manager.setCurrentFile(str(audio_file2))
        manager.addAnnotation(3000, "Song2 annotation", "notes", False, "#2ecc71")
        print("✓ Switched to song2 and added annotation")
        
        # Switch back to first file - THIS IS WHERE THE BUG WOULD OCCUR
        # Before fix: setCurrentFile would try to load legacy annotations
        # After fix: setCurrentFile skips legacy loading when sets exist
        manager.setCurrentFile(str(audio_file1))
        
        # Verify the original annotations are still there
        annotations = manager.getAnnotations()
        assert len(annotations) == 2, f"Expected 2 annotations after switching back, got {len(annotations)}"
        print(f"✓ Switched back to song1: {len(annotations)} annotations preserved")
        
        # Verify the annotations have the correct text
        texts = [a["text"] for a in annotations]
        assert "First annotation" in texts, "First annotation missing"
        assert "Second annotation" in texts, "Second annotation missing"
        print("✓ Annotation data preserved correctly")
        
        # Test that the internal _annotations dict is NOT populated
        # (this would indicate legacy loading was skipped)
        assert str(audio_file1) not in manager._annotations, \
            "Legacy _annotations dict should be empty when using sets"
        print("✓ Legacy _annotations dict is empty (correct behavior)")
        
        # Save and reload to test persistence
        manager._save_annotation_sets()
        print("✓ Saved annotation sets to disk")
        
        # Create new manager and load from disk
        manager2 = AnnotationManager()
        manager2.setCurrentUser("TestUser")
        manager2.setCurrentDirectory(test_dir)
        print("✓ Created new manager and loaded sets from disk")
        
        # Verify sets were loaded
        sets2 = manager2.getAnnotationSets()
        assert len(sets2) > 0, "No sets loaded from disk"
        print(f"✓ Loaded {len(sets2)} set(s) from disk")
        
        # Set current file - the bug would occur here too
        manager2.setCurrentFile(str(audio_file1))
        
        # Verify annotations loaded from sets
        annotations2 = manager2.getAnnotations()
        assert len(annotations2) == 2, f"Expected 2 annotations from loaded sets, got {len(annotations2)}"
        print(f"✓ Retrieved {len(annotations2)} annotations from loaded sets")
        
        # Verify the legacy _annotations dict is still empty
        assert str(audio_file1) not in manager2._annotations, \
            "Legacy _annotations dict should remain empty after loading sets"
        print("✓ Legacy loading still skipped after reload (correct)")
        
        print("\n" + "=" * 80)
        print("✅ ANNOTATION LOADING BUG FIX VERIFIED!")
        print("=" * 80)
        print("\nThe fix ensures that:")
        print("  1. setCurrentFile() checks if annotation sets exist")
        print("  2. If sets exist, legacy annotation loading is skipped")
        print("  3. Annotations are correctly retrieved from sets")
        print("  4. Legacy _annotations dict remains empty when using sets")
        print("  5. This behavior is consistent across file switches and reloads")
        return 0


def test_legacy_mode_still_works():
    """Test that legacy mode still works when no sets are used."""
    print("\n" + "=" * 80)
    print("Testing Legacy Mode Compatibility...")
    print("=" * 80)
    
    # Create Qt application (required for signals)
    app = QCoreApplication(sys.argv)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir)
        
        # Create test audio file
        audio_file = test_dir / "legacy_song.wav"
        audio_file.touch()
        
        # Create legacy annotation file manually
        import json
        legacy_annotations = [
            {
                "uid": 1,
                "timestamp_ms": 1000,
                "ms": 1000,
                "text": "Legacy annotation",
                "category": "notes",
                "important": False,
                "color": "#3498db",
                "user": "LegacyUser",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        ]
        legacy_file = test_dir / ".legacy_song_annotations.json"
        with open(legacy_file, 'w') as f:
            json.dump(legacy_annotations, f)
        print("✓ Created legacy annotation file")
        
        # Create annotation manager WITHOUT setting directory
        # This simulates legacy mode where sets are not used
        manager = AnnotationManager()
        manager.setCurrentUser("LegacyUser")
        print("✓ Created annotation manager (no directory set = no sets loaded)")
        
        # Verify no sets exist
        sets = manager.getAnnotationSets()
        assert len(sets) == 0, "Should have no sets in legacy mode"
        print("✓ No annotation sets loaded (legacy mode)")
        
        # Set current file - should load legacy format
        manager.setCurrentFile(str(audio_file))
        
        # Verify annotations loaded from legacy file
        annotations = manager.getAnnotations()
        assert len(annotations) == 1, f"Expected 1 legacy annotation, got {len(annotations)}"
        assert annotations[0]["text"] == "Legacy annotation", "Wrong annotation text"
        print(f"✓ Retrieved {len(annotations)} annotation from legacy file")
        
        # Verify it's in the _annotations dict
        assert str(audio_file) in manager._annotations, \
            "Legacy annotations should be in _annotations dict"
        print("✓ Legacy _annotations dict populated (correct for legacy mode)")
        
        print("\n✅ Legacy mode still works correctly!")
        return 0


if __name__ == "__main__":
    try:
        result1 = test_annotation_loading_with_sets()
        result2 = test_legacy_mode_still_works()
        
        if result1 == 0 and result2 == 0:
            print("\n" + "=" * 80)
            print("✅ ALL TESTS PASSED!")
            print("=" * 80)
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
