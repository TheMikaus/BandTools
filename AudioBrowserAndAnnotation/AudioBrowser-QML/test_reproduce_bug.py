#!/usr/bin/env python3
"""
Test to reproduce the actual reported bug.

The bug report says: "the annotation manager has a bug where it never loads 
the annotations it is supposed to"

Let's create a scenario that would cause this and see what happens.
"""

import sys
import tempfile
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtCore import QCoreApplication
from backend.annotation_manager import AnnotationManager


def test_reproduce_bug():
    """Try to reproduce the actual bug."""
    print("Attempting to reproduce the reported bug...")
    print("=" * 80)
    
    app = QCoreApplication(sys.argv)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir)
        print(f"\n✓ Created test directory: {test_dir}")
        
        # Create a test audio file
        audio_file = test_dir / "song.wav"
        audio_file.touch()
        
        # Create annotation sets file with annotations (simulating existing data)
        sets_data = {
            "version": 3,
            "updated": "2024-01-01T00:00:00",
            "sets": [
                {
                    "id": "set1",
                    "name": "TestUser",
                    "color": "#00cc66",
                    "visible": True,
                    "folder_notes": "",
                    "files": {
                        "song.wav": {
                            "general": "",
                            "best_take": False,
                            "partial_take": False,
                            "reference_song": False,
                            "notes": [
                                {
                                    "uid": 1,
                                    "ms": 1000,
                                    "text": "Test annotation from sets",
                                    "important": True
                                }
                            ]
                        }
                    }
                }
            ],
            "current_set_id": "set1"
        }
        
        sets_file = test_dir / ".audio_notes_TestUser.json"
        with open(sets_file, 'w') as f:
            json.dump(sets_data, f, indent=2)
        print("✓ Created annotation sets file with 1 annotation for song.wav")
        
        # Create annotation manager
        manager = AnnotationManager()
        manager.setCurrentUser("TestUser")
        print("✓ Created annotation manager")
        
        # Set directory - this should load the annotation sets
        manager.setCurrentDirectory(test_dir)
        print("✓ Set current directory (should load annotation sets)")
        
        # Check that sets were loaded
        sets = manager.getAnnotationSets()
        print(f"✓ Loaded {len(sets)} annotation set(s)")
        
        # Set current file
        manager.setCurrentFile(str(audio_file))
        print(f"✓ Set current file: {audio_file.name}")
        
        # Try to get annotations - THIS IS WHERE THE BUG WOULD SHOW
        annotations = manager.getAnnotations()
        count = manager.getAnnotationCount()
        
        print(f"\nResult:")
        print(f"  Annotation count: {count}")
        print(f"  Annotations: {annotations}")
        
        if count == 0:
            print("\n❌ BUG REPRODUCED!")
            print("   Annotations exist in the sets file but getAnnotations() returns empty!")
            print("\n   Diagnosis:")
            print(f"   - Annotation sets exist: {len(manager._annotation_sets) > 0}")
            print(f"   - Current set ID: {manager._current_set_id}")
            print(f"   - Current file: {manager._current_file}")
            
            # Check what's in the set
            if manager._annotation_sets:
                current_set = manager._get_current_set_object()
                if current_set:
                    file_name = Path(audio_file).name
                    file_data = current_set.get("files", {}).get(file_name, {})
                    notes = file_data.get("notes", [])
                    print(f"   - Notes in current set for file: {len(notes)}")
                    if notes:
                        print(f"   - First note: {notes[0]}")
            
            return False
        elif count == 1:
            print("\n✅ Annotations loaded correctly!")
            print(f"   Text: {annotations[0].get('text')}")
            return True
        else:
            print(f"\n⚠️  Unexpected result: got {count} annotations")
            return False


if __name__ == "__main__":
    try:
        if test_reproduce_bug():
            print("\n" + "=" * 80)
            print("The bug is FIXED or was not reproducible with this scenario.")
            print("=" * 80)
            sys.exit(0)
        else:
            print("\n" + "=" * 80)
            print("The bug was REPRODUCED.")
            print("=" * 80)
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
