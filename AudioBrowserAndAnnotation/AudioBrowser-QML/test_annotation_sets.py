#!/usr/bin/env python3
"""
Test annotation sets implementation for feature parity.

This test verifies that the multi-annotation sets system works correctly.
"""

import sys
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtCore import QCoreApplication
from backend.annotation_manager import AnnotationManager


def test_annotation_sets():
    """Test annotation sets functionality."""
    print("Testing Annotation Sets Implementation...")
    print("=" * 60)
    
    # Create Qt application (required for signals)
    app = QCoreApplication(sys.argv)
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir)
        print(f"\n✓ Created test directory: {test_dir}")
        
        # Create annotation manager
        manager = AnnotationManager()
        manager.setCurrentUser("TestUser")
        print("✓ Created annotation manager")
        
        # Set directory (should create default set)
        manager.setCurrentDirectory(test_dir)
        print("✓ Set current directory")
        
        # Check default set was created
        sets = manager.getAnnotationSets()
        assert len(sets) > 0, "No default set created"
        print(f"✓ Default set created: {sets[0]['name']}")
        
        # Get current set ID
        current_id = manager.getCurrentSetId()
        assert current_id, "No current set ID"
        print(f"✓ Current set ID: {current_id}")
        
        # Add a second annotation set
        new_set_id = manager.addAnnotationSet("Practice Set", "#ff5555")
        assert new_set_id, "Failed to create new set"
        print(f"✓ Created new set: Practice Set (ID: {new_set_id})")
        
        # Check we now have 2 sets
        sets = manager.getAnnotationSets()
        assert len(sets) == 2, f"Expected 2 sets, got {len(sets)}"
        print(f"✓ Total sets: {len(sets)}")
        
        # Verify new set became current
        assert manager.getCurrentSetId() == new_set_id, "New set not set as current"
        print("✓ New set is current")
        
        # Rename the set
        manager.renameAnnotationSet(new_set_id, "Performance Set")
        sets = manager.getAnnotationSets()
        renamed_set = next((s for s in sets if s['id'] == new_set_id), None)
        assert renamed_set and renamed_set['name'] == "Performance Set", "Set not renamed"
        print("✓ Set renamed successfully")
        
        # Test show all sets toggle
        assert not manager.getShowAllSets(), "Show all sets should default to False"
        print("✓ Show all sets defaults to False")
        
        manager.setShowAllSets(True)
        assert manager.getShowAllSets(), "Show all sets not set to True"
        print("✓ Show all sets toggle works")
        
        # Try to delete the only other set (should work since we have 2)
        first_set_id = sets[0]['id']
        success = manager.deleteAnnotationSet(first_set_id)
        assert success, "Failed to delete set"
        print("✓ Deleted first set successfully")
        
        # Try to delete the last set (should fail)
        sets = manager.getAnnotationSets()
        assert len(sets) == 1, "Should have 1 set remaining"
        last_set_id = sets[0]['id']
        success = manager.deleteAnnotationSet(last_set_id)
        assert not success, "Should not be able to delete last set"
        print("✓ Cannot delete last set (protection works)")
        
        # Test annotation addition with sets
        test_file = test_dir / "test_audio.wav"
        test_file.touch()  # Create empty file
        
        manager.setCurrentFile(str(test_file))
        manager.addAnnotation(5000, "Test annotation", "timing", False, "#3498db")
        print("✓ Added annotation to current set")
        
        # Get annotations (single set view)
        annotations = manager.getAnnotations()
        assert len(annotations) == 1, f"Expected 1 annotation, got {len(annotations)}"
        print(f"✓ Retrieved annotation: {annotations[0]['text']}")
        
        # Create another set and add annotation
        second_set_id = manager.addAnnotationSet("Second Set", "#55ff55")
        manager.setCurrentFile(str(test_file))
        manager.addAnnotation(10000, "Second set annotation", "energy", True, "#ff5555")
        print("✓ Added annotation to second set")
        
        # Test single set view
        manager.setShowAllSets(False)
        annotations = manager.getAnnotations()
        assert len(annotations) == 1, "Single set view should show 1 annotation"
        print(f"✓ Single set view: {len(annotations)} annotation")
        
        # Test merged view
        manager.setShowAllSets(True)
        annotations = manager.getAnnotations()
        assert len(annotations) == 2, f"Merged view should show 2 annotations, got {len(annotations)}"
        print(f"✓ Merged view: {len(annotations)} annotations")
        
        # Check that merged view annotations have set info
        for ann in annotations:
            assert "_set_name" in ann, "Merged annotation missing _set_name"
            assert "_set_color" in ann, "Merged annotation missing _set_color"
            assert "_set_id" in ann, "Merged annotation missing _set_id"
        print("✓ Merged annotations contain set metadata")
        
        # Test persistence
        manager._save_annotation_sets()
        print("✓ Saved annotation sets to disk")
        
        # Create new manager and load
        manager2 = AnnotationManager()
        manager2.setCurrentUser("TestUser")
        manager2.setCurrentDirectory(test_dir)
        
        sets2 = manager2.getAnnotationSets()
        assert len(sets2) == 2, f"Loaded {len(sets2)} sets, expected 2"
        print(f"✓ Loaded {len(sets2)} sets from disk")
        
        # Verify annotations persisted
        manager2.setCurrentFile(str(test_file))
        manager2.setShowAllSets(True)
        annotations2 = manager2.getAnnotations()
        assert len(annotations2) == 2, f"Loaded {len(annotations2)} annotations, expected 2"
        print(f"✓ Loaded {len(annotations2)} annotations from disk")
    
    print("\n" + "=" * 60)
    print("✅ All annotation sets tests PASSED!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(test_annotation_sets())
    except Exception as e:
        print(f"\n❌ Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
