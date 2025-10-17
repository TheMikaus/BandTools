#!/usr/bin/env python3
"""
Test script to verify annotation population fix.

This test verifies that when a file is selected:
1. Annotations are loaded properly
2. getAnnotations() returns the loaded annotations
3. getAnnotationCount() matches the number of annotations returned
"""

import sys
import tempfile
import json
from pathlib import Path

# Add parent directory to path to import backend modules
sys.path.insert(0, str(Path(__file__).parent))

from backend.annotation_manager import AnnotationManager


def test_annotation_loading():
    """Test that annotations are properly loaded and retrieved."""
    print("Testing annotation loading and retrieval...")
    
    # Create a temporary directory with test files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create a mock audio file
        audio_file = temp_path / "test_song.wav"
        audio_file.touch()
        
        # Create annotation file in legacy format
        annotation_file = temp_path / ".test_song_annotations.json"
        test_annotations = [
            {
                "uid": 1,
                "timestamp_ms": 1000,
                "ms": 1000,
                "text": "Test annotation 1",
                "category": "timing",
                "important": True,
                "color": "#3498db",
                "user": "test_user",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            },
            {
                "uid": 2,
                "timestamp_ms": 2000,
                "ms": 2000,
                "text": "Test annotation 2",
                "category": "notes",
                "important": False,
                "color": "#e74c3c",
                "user": "test_user",
                "created_at": "2024-01-01T00:01:00",
                "updated_at": "2024-01-01T00:01:00"
            }
        ]
        
        with open(annotation_file, 'w') as f:
            json.dump(test_annotations, f, indent=2)
        
        # Create annotation manager
        manager = AnnotationManager()
        manager.setCurrentDirectory(temp_path)
        manager.setCurrentUser("test_user")
        
        # Set current file (this should trigger loading)
        manager.setCurrentFile(str(audio_file))
        
        # Test 1: Check annotation count
        count = manager.getAnnotationCount()
        print(f"  ✓ Annotation count: {count}")
        
        if count != len(test_annotations):
            print(f"  ✗ FAIL: Expected {len(test_annotations)} annotations, got {count}")
            return False
        
        # Test 2: Get annotations
        annotations = manager.getAnnotations()
        print(f"  ✓ Retrieved {len(annotations)} annotations")
        
        if len(annotations) != len(test_annotations):
            print(f"  ✗ FAIL: Expected {len(test_annotations)} annotations, got {len(annotations)}")
            return False
        
        # Test 3: Verify annotation content
        for i, ann in enumerate(annotations):
            expected = test_annotations[i]
            if ann["text"] != expected["text"]:
                print(f"  ✗ FAIL: Annotation {i} text mismatch")
                return False
            if ann["timestamp_ms"] != expected["timestamp_ms"]:
                print(f"  ✗ FAIL: Annotation {i} timestamp mismatch")
                return False
        
        print("  ✓ All annotation content verified")
        
        # Test 4: Test filtering
        important_annotations = manager.getImportantAnnotations()
        print(f"  ✓ Important annotations: {len(important_annotations)}")
        
        expected_important = sum(1 for a in test_annotations if a["important"])
        if len(important_annotations) != expected_important:
            print(f"  ✗ FAIL: Expected {expected_important} important annotations, got {len(important_annotations)}")
            return False
        
        print("  ✓ All tests passed!")
        return True


def test_empty_file():
    """Test behavior when file has no annotations."""
    print("\nTesting empty annotation file...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create a mock audio file with no annotation file
        audio_file = temp_path / "empty_song.wav"
        audio_file.touch()
        
        # Create annotation manager
        manager = AnnotationManager()
        manager.setCurrentDirectory(temp_path)
        manager.setCurrentFile(str(audio_file))
        
        # Should return empty list, not error
        count = manager.getAnnotationCount()
        annotations = manager.getAnnotations()
        
        if count != 0:
            print(f"  ✗ FAIL: Expected 0 annotations for empty file, got {count}")
            return False
        
        if len(annotations) != 0:
            print(f"  ✗ FAIL: Expected empty list, got {len(annotations)} annotations")
            return False
        
        print("  ✓ Empty file handled correctly")
        return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Annotation Population Test Suite")
    print("=" * 60)
    print()
    
    # Run tests
    test1_passed = test_annotation_loading()
    test2_passed = test_empty_file()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    print(f"Annotation Loading: {'✓ PASS' if test1_passed else '✗ FAIL'}")
    print(f"Empty File Handling: {'✓ PASS' if test2_passed else '✗ FAIL'}")
    
    if test1_passed and test2_passed:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
