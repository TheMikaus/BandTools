#!/usr/bin/env python3
"""
Integration test for annotation tab population.

This test simulates the user workflow:
1. Application loads with a directory
2. User selects a song from the library
3. Annotation tab should display annotations for that song

This test verifies the complete data flow without requiring GUI.
"""

import sys
import tempfile
import json
from pathlib import Path

# Add parent directory to path to import backend modules
sys.path.insert(0, str(Path(__file__).parent))

# Import without GUI to avoid display issues in headless environments
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from backend.annotation_manager import AnnotationManager
from backend.file_manager import FileManager
from backend.models import AnnotationsModel


def create_test_environment():
    """Create a test directory with audio files and annotations."""
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)
    
    # Create test audio files
    songs = ["song1.wav", "song2.mp3", "song3.wav"]
    for song in songs:
        (temp_path / song).touch()
    
    # Create annotations for song1
    song1_annotations = [
        {
            "uid": 1,
            "timestamp_ms": 5000,
            "ms": 5000,
            "text": "Intro starts here",
            "category": "timing",
            "important": True,
            "color": "#3498db",
            "user": "test_user",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        },
        {
            "uid": 2,
            "timestamp_ms": 15000,
            "ms": 15000,
            "text": "Great guitar solo",
            "category": "notes",
            "important": False,
            "color": "#2ecc71",
            "user": "test_user",
            "created_at": "2024-01-01T00:01:00",
            "updated_at": "2024-01-01T00:01:00"
        },
        {
            "uid": 3,
            "timestamp_ms": 30000,
            "ms": 30000,
            "text": "Tempo change - watch carefully",
            "category": "timing",
            "important": True,
            "color": "#e74c3c",
            "user": "test_user",
            "created_at": "2024-01-01T00:02:00",
            "updated_at": "2024-01-01T00:02:00"
        }
    ]
    
    annotation_file = temp_path / ".song1_annotations.json"
    with open(annotation_file, 'w') as f:
        json.dump(song1_annotations, f, indent=2)
    
    # Create annotations for song2
    song2_annotations = [
        {
            "uid": 4,
            "timestamp_ms": 10000,
            "ms": 10000,
            "text": "Chorus starts",
            "category": "harmony",
            "important": True,
            "color": "#9b59b6",
            "user": "test_user",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        }
    ]
    
    annotation_file2 = temp_path / ".song2_annotations.json"
    with open(annotation_file2, 'w') as f:
        json.dump(song2_annotations, f, indent=2)
    
    # song3 has no annotations (test empty case)
    
    return temp_path, songs, song1_annotations, song2_annotations


def test_workflow():
    """Test the complete user workflow."""
    print("Setting up test environment...")
    temp_path, songs, song1_annotations, song2_annotations = create_test_environment()
    
    print(f"✓ Created test directory: {temp_path}")
    print(f"✓ Created {len(songs)} test audio files")
    print(f"✓ Created annotations for 2 songs")
    
    # Step 1: Initialize managers (simulating app startup)
    print("\n1. Initializing application components...")
    annotation_manager = AnnotationManager()
    file_manager = FileManager()
    annotations_model = AnnotationsModel()
    
    print("  ✓ AnnotationManager created")
    print("  ✓ FileManager created")
    print("  ✓ AnnotationsModel created")
    
    # Step 2: Set directory (simulating folder selection)
    print(f"\n2. Setting directory to: {temp_path}")
    annotation_manager.setCurrentDirectory(temp_path)
    file_manager.setCurrentDirectory(str(temp_path))
    
    print("  ✓ Directory set in managers")
    
    # Step 3: Select first song (simulating user clicking on song1)
    print(f"\n3. Selecting song: {songs[0]}")
    song1_path = str(temp_path / songs[0])
    annotation_manager.setCurrentFile(song1_path)
    
    print(f"  ✓ Current file set to: {songs[0]}")
    
    # Step 4: Retrieve annotations (what the UI does)
    print("\n4. Retrieving annotations for display...")
    annotations = annotation_manager.getAnnotations()
    annotation_count = annotation_manager.getAnnotationCount()
    
    print(f"  ✓ Retrieved {len(annotations)} annotations")
    print(f"  ✓ Annotation count: {annotation_count}")
    
    # Verify annotations match what we created
    if len(annotations) != len(song1_annotations):
        print(f"  ✗ FAIL: Expected {len(song1_annotations)} annotations, got {len(annotations)}")
        return False
    
    if annotation_count != len(song1_annotations):
        print(f"  ✗ FAIL: Count mismatch - expected {len(song1_annotations)}, got {annotation_count}")
        return False
    
    # Step 5: Populate model (what the QML does)
    print("\n5. Populating AnnotationsModel...")
    annotations_model.setAnnotations(annotations)
    model_count = annotations_model.count()
    
    print(f"  ✓ Model populated with {model_count} rows")
    
    if model_count != len(song1_annotations):
        print(f"  ✗ FAIL: Model count mismatch - expected {len(song1_annotations)}, got {model_count}")
        return False
    
    # Step 6: Verify annotation details
    print("\n6. Verifying annotation content...")
    for i, ann in enumerate(annotations):
        expected = song1_annotations[i]
        if ann["text"] != expected["text"]:
            print(f"  ✗ FAIL: Annotation {i} text mismatch")
            return False
        if ann["timestamp_ms"] != expected["timestamp_ms"]:
            print(f"  ✗ FAIL: Annotation {i} timestamp mismatch")
            return False
        print(f"  ✓ Annotation {i}: '{ann['text']}' at {ann['timestamp_ms']}ms")
    
    # Step 7: Switch to another song (simulating user selecting song2)
    print(f"\n7. Switching to song: {songs[1]}")
    song2_path = str(temp_path / songs[1])
    annotation_manager.setCurrentFile(song2_path)
    
    annotations2 = annotation_manager.getAnnotations()
    print(f"  ✓ Retrieved {len(annotations2)} annotations for song2")
    
    if len(annotations2) != len(song2_annotations):
        print(f"  ✗ FAIL: Expected {len(song2_annotations)} annotations for song2, got {len(annotations2)}")
        return False
    
    # Step 8: Test empty song (no annotations)
    print(f"\n8. Switching to song with no annotations: {songs[2]}")
    song3_path = str(temp_path / songs[2])
    annotation_manager.setCurrentFile(song3_path)
    
    annotations3 = annotation_manager.getAnnotations()
    count3 = annotation_manager.getAnnotationCount()
    
    print(f"  ✓ Retrieved {len(annotations3)} annotations (should be 0)")
    print(f"  ✓ Count is {count3} (should be 0)")
    
    if len(annotations3) != 0 or count3 != 0:
        print(f"  ✗ FAIL: Expected 0 annotations for song3")
        return False
    
    # Step 9: Test important annotations filtering
    print(f"\n9. Testing important annotations filtering...")
    annotation_manager.setCurrentFile(song1_path)  # Back to song1
    important = annotation_manager.getImportantAnnotations()
    
    expected_important = sum(1 for a in song1_annotations if a["important"])
    print(f"  ✓ Found {len(important)} important annotations")
    
    if len(important) != expected_important:
        print(f"  ✗ FAIL: Expected {expected_important} important annotations, got {len(important)}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ ALL INTEGRATION TESTS PASSED!")
    print("=" * 60)
    print("\nThe annotation tab population fix is working correctly:")
    print("  • Annotations load when a song is selected")
    print("  • The model is properly populated with annotation data")
    print("  • Switching between songs updates annotations correctly")
    print("  • Empty files are handled gracefully")
    print("  • Filtering works as expected")
    
    return True


def main():
    """Run the integration test."""
    print("=" * 60)
    print("Annotation Tab Integration Test")
    print("=" * 60)
    print("\nSimulating complete user workflow:")
    print("  1. App starts and loads directory")
    print("  2. User selects a song")
    print("  3. Annotations should populate in the tab")
    print()
    
    try:
        success = test_workflow()
        return 0 if success else 1
    except Exception as e:
        print(f"\n✗ TEST FAILED WITH EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
