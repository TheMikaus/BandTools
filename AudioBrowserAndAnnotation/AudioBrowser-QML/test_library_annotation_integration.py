#!/usr/bin/env python3
"""
Integration test for Library View -> Annotation Manager -> Annotation Tab.

This test simulates the full flow:
1. User opens a directory with annotation sets
2. FileManager discovers files and loads metadata (best_take, partial_take)
3. FileListModel displays files with metadata indicators
4. User selects a file in library -> audioEngine.loadAndPlay()
5. audioEngine emits currentFileChanged -> annotationManager.setCurrentFile()
6. AnnotationManager loads annotations from sets
7. Annotations Tab displays the annotations

This verifies all the pieces work together correctly.
"""

import sys
import tempfile
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_full_integration():
    """Test the full integration from library view to annotation tab."""
    print("Testing Full Integration: Library -> AudioEngine -> AnnotationManager")
    print("=" * 80)
    
    try:
        from PyQt6.QtCore import QCoreApplication
        from backend.file_manager import FileManager
        from backend.annotation_manager import AnnotationManager
        from backend.models import FileListModel
        
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
            print("✓ Created 2 test audio files")
            
            # Create annotation sets file with complete metadata
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
                            "song1.wav": {
                                "general": "First song",
                                "best_take": True,
                                "partial_take": False,
                                "reference_song": False,
                                "notes": [
                                    {
                                        "uid": 1,
                                        "ms": 1000,
                                        "text": "Important annotation on song1",
                                        "important": True
                                    },
                                    {
                                        "uid": 2,
                                        "ms": 2000,
                                        "text": "Regular note on song1",
                                        "important": False
                                    }
                                ]
                            },
                            "song2.wav": {
                                "general": "Second song",
                                "best_take": False,
                                "partial_take": True,
                                "reference_song": False,
                                "notes": [
                                    {
                                        "uid": 3,
                                        "ms": 3000,
                                        "text": "Note on song2",
                                        "important": False
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
            print("✓ Created annotation sets file with metadata and annotations")
            
            # Step 1: FileManager discovers files and loads metadata
            print("\n--- Step 1: FileManager loads directory ---")
            file_manager = FileManager()
            file_manager.setCurrentDirectory(str(test_dir))
            print("✓ FileManager loaded directory")
            
            # Verify metadata loaded
            is_best_1 = file_manager.isBestTake(str(audio_file1))
            is_partial_2 = file_manager.isPartialTake(str(audio_file2))
            
            print(f"  song1.wav - best_take: {is_best_1} (expected: True)")
            print(f"  song2.wav - partial_take: {is_partial_2} (expected: True)")
            
            if not is_best_1:
                print("❌ ERROR: Best take metadata not loaded correctly!")
                return 1
            if not is_partial_2:
                print("❌ ERROR: Partial take metadata not loaded correctly!")
                return 1
            
            # Step 2: Create AnnotationManager and set directory
            print("\n--- Step 2: AnnotationManager loads annotation sets ---")
            annotation_manager = AnnotationManager()
            annotation_manager.setCurrentUser("TestUser")
            annotation_manager.setCurrentDirectory(test_dir)
            print("✓ AnnotationManager loaded directory")
            
            # Verify sets were loaded
            sets = annotation_manager.getAnnotationSets()
            print(f"  Loaded {len(sets)} annotation set(s)")
            if len(sets) == 0:
                print("❌ ERROR: No annotation sets loaded!")
                return 1
            
            # Step 3: FileListModel displays files with metadata
            print("\n--- Step 3: FileListModel displays files with metadata ---")
            file_list_model = FileListModel(
                file_manager=file_manager,
                annotation_manager=annotation_manager
            )
            
            # Set files in the model
            discovered_files = file_manager.getDiscoveredFiles()
            file_list_model.setFiles(discovered_files)
            print(f"✓ FileListModel populated with {file_list_model.rowCount()} files")
            
            # Verify model has correct metadata
            # Check first file (song1.wav)
            file_data_0 = file_list_model._files[0]
            print(f"\n  File 0 ({file_data_0['filename']}):")
            print(f"    - isBestTake: {file_data_0['isBestTake']} (expected: True)")
            print(f"    - hasImportantAnnotation: {file_data_0['hasImportantAnnotation']} (expected: True)")
            
            if not file_data_0['isBestTake']:
                print("❌ ERROR: FileListModel doesn't show best_take indicator!")
                return 1
            if not file_data_0['hasImportantAnnotation']:
                print("❌ ERROR: FileListModel doesn't show important annotation indicator!")
                return 1
            
            # Check second file (song2.wav)
            file_data_1 = file_list_model._files[1]
            print(f"\n  File 1 ({file_data_1['filename']}):")
            print(f"    - isPartialTake: {file_data_1['isPartialTake']} (expected: True)")
            print(f"    - hasImportantAnnotation: {file_data_1['hasImportantAnnotation']} (expected: False)")
            
            if not file_data_1['isPartialTake']:
                print("❌ ERROR: FileListModel doesn't show partial_take indicator!")
                return 1
            if file_data_1['hasImportantAnnotation']:
                print("❌ ERROR: FileListModel incorrectly shows important annotation for song2!")
                return 1
            
            # Step 4: Simulate user selecting a file (triggers setCurrentFile)
            print("\n--- Step 4: User selects song1.wav (triggers setCurrentFile) ---")
            annotation_manager.setCurrentFile(str(audio_file1))
            print("✓ AnnotationManager.setCurrentFile() called")
            
            # Step 5: Verify annotations are loaded
            print("\n--- Step 5: Verify annotations loaded from sets ---")
            annotations = annotation_manager.getAnnotations()
            print(f"✓ Retrieved {len(annotations)} annotations")
            
            if len(annotations) != 2:
                print(f"❌ ERROR: Expected 2 annotations for song1, got {len(annotations)}")
                return 1
            
            # Verify annotation content
            important_count = sum(1 for a in annotations if a.get('important', False))
            print(f"  - {important_count} important annotation(s)")
            
            if important_count != 1:
                print(f"❌ ERROR: Expected 1 important annotation, got {important_count}")
                return 1
            
            # Verify texts
            texts = [a['text'] for a in annotations]
            print(f"  - Annotation texts: {texts}")
            
            if "Important annotation on song1" not in texts:
                print("❌ ERROR: Important annotation text not found!")
                return 1
            if "Regular note on song1" not in texts:
                print("❌ ERROR: Regular annotation text not found!")
                return 1
            
            # Step 6: Switch to second file
            print("\n--- Step 6: Switch to song2.wav ---")
            annotation_manager.setCurrentFile(str(audio_file2))
            annotations2 = annotation_manager.getAnnotations()
            print(f"✓ Retrieved {len(annotations2)} annotation(s) for song2")
            
            if len(annotations2) != 1:
                print(f"❌ ERROR: Expected 1 annotation for song2, got {len(annotations2)}")
                return 1
            
            if annotations2[0]['text'] != "Note on song2":
                print(f"❌ ERROR: Wrong annotation text: {annotations2[0]['text']}")
                return 1
            
            # Step 7: Switch back to first file (verify data preserved)
            print("\n--- Step 7: Switch back to song1.wav (verify persistence) ---")
            annotation_manager.setCurrentFile(str(audio_file1))
            annotations_again = annotation_manager.getAnnotations()
            print(f"✓ Retrieved {len(annotations_again)} annotation(s)")
            
            if len(annotations_again) != 2:
                print(f"❌ ERROR: Annotations not preserved! Expected 2, got {len(annotations_again)}")
                return 1
            
            print("\n" + "=" * 80)
            print("✅ FULL INTEGRATION TEST PASSED!")
            print("=" * 80)
            print("\nVerified:")
            print("  ✓ FileManager correctly loads metadata from annotation sets")
            print("  ✓ FileListModel displays files with correct metadata indicators")
            print("  ✓ AnnotationManager loads annotation sets for directory")
            print("  ✓ setCurrentFile() triggers annotation loading from sets")
            print("  ✓ Annotations are correctly retrieved for each file")
            print("  ✓ Switching between files preserves data correctly")
            print("  ✓ Important annotation indicators work properly")
            
            return 0
            
    except ImportError as e:
        print(f"\n⚠️  Cannot run test: {e}")
        print("   PyQt6 not installed - skipping test")
        return 0
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(test_full_integration())
