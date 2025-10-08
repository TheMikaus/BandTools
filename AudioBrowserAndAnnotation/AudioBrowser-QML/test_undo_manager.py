#!/usr/bin/env python3
"""
Test suite for Undo Manager

Tests the undo/redo functionality for AudioBrowser-QML.
"""

import sys
import tempfile
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.undo_manager import UndoManager, ProvidedNameCommand, AnnotationAddCommand, AnnotationDeleteCommand, AnnotationEditCommand
from backend.file_manager import FileManager
from backend.annotation_manager import AnnotationManager


def test_undo_manager_creation():
    """Test that UndoManager can be created."""
    print("Test 1: UndoManager creation...")
    undo_manager = UndoManager()
    assert undo_manager is not None
    assert not undo_manager.can_undo()
    assert not undo_manager.can_redo()
    assert undo_manager.get_undo_text() == ""
    assert undo_manager.get_redo_text() == ""
    print("✓ UndoManager created successfully")


def test_undo_manager_capacity():
    """Test that capacity setting works."""
    print("\nTest 2: Capacity setting...")
    undo_manager = UndoManager()
    undo_manager.setCapacity(50)
    # Test that capacity is enforced (we can't directly check _capacity)
    # but we can verify the manager still works
    assert undo_manager is not None
    print("✓ Capacity setting works")


def test_provided_name_undo():
    """Test undo/redo for provided name changes."""
    print("\nTest 3: Provided name undo/redo...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test audio file
        test_file = Path(tmpdir) / "test.wav"
        test_file.touch()
        
        # Create managers
        file_manager = FileManager()
        undo_manager = UndoManager()
        undo_manager.setFileManager(file_manager)
        
        # Set directory and provided name
        file_manager.setCurrentDirectory(tmpdir)
        file_manager.setProvidedName(str(test_file), "Original Name")
        
        # Record the change in undo manager
        command = ProvidedNameCommand(file_manager, str(test_file), "Original Name", "New Name")
        command.execute()  # Apply the new name
        undo_manager.push_command(command)
        
        # Check that we can undo
        assert undo_manager.can_undo()
        assert not undo_manager.can_redo()
        
        # Undo the change
        undo_manager.undo()
        name = file_manager.getProvidedName(str(test_file))
        assert name == "Original Name", f"Expected 'Original Name', got '{name}'"
        
        # Check that we can redo
        assert not undo_manager.can_undo()
        assert undo_manager.can_redo()
        
        # Redo the change
        undo_manager.redo()
        name = file_manager.getProvidedName(str(test_file))
        assert name == "New Name", f"Expected 'New Name', got '{name}'"
        
        print("✓ Provided name undo/redo works")


def test_annotation_add_undo():
    """Test undo/redo for annotation addition."""
    print("\nTest 4: Annotation add undo/redo...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test audio file
        test_file = Path(tmpdir) / "test.wav"
        test_file.touch()
        
        # Create managers
        annotation_manager = AnnotationManager()
        undo_manager = UndoManager()
        undo_manager.setAnnotationManager(annotation_manager)
        
        # Set current file
        annotation_manager.setCurrentFile(str(test_file))
        
        # Add an annotation
        annotation_manager.addAnnotation(5000, "Test annotation", "timing", False, "#3498db")
        annotations = annotation_manager.getAnnotations()
        assert len(annotations) == 1
        
        # Record the addition for undo
        added_annotation = annotations[0]
        undo_manager.record_annotation_add(str(test_file), added_annotation)
        
        # Check that we can undo
        assert undo_manager.can_undo()
        
        # Undo the addition (should delete the annotation)
        undo_manager.undo()
        annotations = annotation_manager.getAnnotations()
        assert len(annotations) == 0, f"Expected 0 annotations after undo, got {len(annotations)}"
        
        # Check that we can redo
        assert undo_manager.can_redo()
        
        # Redo the addition
        undo_manager.redo()
        annotations = annotation_manager.getAnnotations()
        assert len(annotations) == 1, f"Expected 1 annotation after redo, got {len(annotations)}"
        
        print("✓ Annotation add undo/redo works")


def test_undo_stack_trimming():
    """Test that the undo stack is trimmed to capacity."""
    print("\nTest 5: Undo stack trimming...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.wav"
        test_file.touch()
        
        file_manager = FileManager()
        undo_manager = UndoManager()
        undo_manager.setFileManager(file_manager)
        undo_manager.setCapacity(3)  # Small capacity for testing
        
        file_manager.setCurrentDirectory(tmpdir)
        
        # Add 5 commands (should trim to 3)
        for i in range(5):
            old_name = f"Name {i}"
            new_name = f"Name {i+1}"
            file_manager.setProvidedName(str(test_file), old_name)
            command = ProvidedNameCommand(file_manager, str(test_file), old_name, new_name)
            command.execute()
            undo_manager.push_command(command)
        
        # Should only be able to undo 3 times (capacity)
        undo_count = 0
        while undo_manager.can_undo():
            undo_manager.undo()
            undo_count += 1
        
        assert undo_count == 3, f"Expected to undo 3 times (capacity), but undid {undo_count} times"
        
        print("✓ Undo stack trimming works")


def test_qml_accessible_methods():
    """Test QML-accessible methods."""
    print("\nTest 6: QML-accessible methods...")
    
    undo_manager = UndoManager()
    
    # Test methods exist and return correct types
    assert isinstance(undo_manager.canUndo(), bool)
    assert isinstance(undo_manager.canRedo(), bool)
    assert isinstance(undo_manager.getUndoText(), str)
    assert isinstance(undo_manager.getRedoText(), str)
    assert isinstance(undo_manager.getStackSize(), int)
    assert isinstance(undo_manager.getCurrentIndex(), int)
    
    print("✓ QML-accessible methods work")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Running Undo Manager Tests")
    print("=" * 60)
    
    try:
        test_undo_manager_creation()
        test_undo_manager_capacity()
        test_provided_name_undo()
        test_annotation_add_undo()
        test_undo_stack_trimming()
        test_qml_accessible_methods()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed! (6/6)")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
