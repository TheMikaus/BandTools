#!/usr/bin/env python3
"""
Best/Partial Take Indicators Test Script

Tests the best/partial take tracking functionality.
"""

import sys
import json
import tempfile
import shutil
from pathlib import Path

def test_file_manager_take_tracking():
    """Test FileManager best/partial take tracking."""
    print("Testing FileManager take tracking...")
    
    try:
        from PyQt6.QtCore import QCoreApplication
        from backend.file_manager import FileManager
        
        # Create QApplication for Qt signals
        app = QCoreApplication(sys.argv)
        
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test audio files
            test_file1 = temp_path / "test1.wav"
            test_file2 = temp_path / "test2.wav"
            test_file3 = temp_path / "test3.wav"
            
            test_file1.touch()
            test_file2.touch()
            test_file3.touch()
            
            # Create FileManager
            fm = FileManager()
            fm.setCurrentDirectory(str(temp_path))
            
            # Test marking as best take
            print("  Testing best take marking...")
            fm.markAsBestTake(str(test_file1))
            assert fm.isBestTake(str(test_file1)), "File should be marked as best take"
            assert not fm.isBestTake(str(test_file2)), "File should not be marked as best take"
            print("    ✓ Best take marking works")
            
            # Test marking as partial take
            print("  Testing partial take marking...")
            fm.markAsPartialTake(str(test_file2))
            assert fm.isPartialTake(str(test_file2)), "File should be marked as partial take"
            assert not fm.isPartialTake(str(test_file1)), "File should not be marked as partial take"
            print("    ✓ Partial take marking works")
            
            # Test persistence
            print("  Testing persistence...")
            metadata_file = temp_path / ".takes_metadata.json"
            assert metadata_file.exists(), "Metadata file should be created"
            
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            assert "test1.wav" in metadata.get("best_takes", []), "Best take should be persisted"
            assert "test2.wav" in metadata.get("partial_takes", []), "Partial take should be persisted"
            print("    ✓ Persistence works")
            
            # Test unmarking
            print("  Testing unmarking...")
            fm.unmarkAsBestTake(str(test_file1))
            assert not fm.isBestTake(str(test_file1)), "File should be unmarked as best take"
            
            fm.unmarkAsPartialTake(str(test_file2))
            assert not fm.isPartialTake(str(test_file2)), "File should be unmarked as partial take"
            print("    ✓ Unmarking works")
            
            # Test loading from existing metadata
            print("  Testing loading from metadata...")
            fm2 = FileManager()
            fm2.setCurrentDirectory(str(temp_path))
            
            # Mark some takes
            fm2.markAsBestTake(str(test_file1))
            fm2.markAsPartialTake(str(test_file2))
            
            # Create new manager and load
            fm3 = FileManager()
            fm3.setCurrentDirectory(str(temp_path))
            
            assert fm3.isBestTake(str(test_file1)), "Best take should be loaded from metadata"
            assert fm3.isPartialTake(str(test_file2)), "Partial take should be loaded from metadata"
            print("    ✓ Loading from metadata works")
            
            # Test get methods
            print("  Testing get methods...")
            best_takes = fm3.getBestTakes()
            partial_takes = fm3.getPartialTakes()
            
            assert str(test_file1) in best_takes, "Best takes list should include marked file"
            assert str(test_file2) in partial_takes, "Partial takes list should include marked file"
            print("    ✓ Get methods work")
            
        print("  ✓ All FileManager tests passed")
        return True
        
    except ImportError as e:
        print(f"  ✗ Cannot import required modules: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model_integration():
    """Test FileListModel integration with take tracking."""
    print("\nTesting FileListModel integration...")
    
    try:
        from PyQt6.QtCore import QCoreApplication
        from backend.file_manager import FileManager
        from backend.models import FileListModel
        
        # Create QApplication for Qt signals
        app = QCoreApplication(sys.argv)
        
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test audio files
            test_file1 = temp_path / "test1.wav"
            test_file2 = temp_path / "test2.wav"
            
            test_file1.touch()
            test_file2.touch()
            
            # Create FileManager and mark takes
            fm = FileManager()
            fm.setCurrentDirectory(str(temp_path))
            fm.markAsBestTake(str(test_file1))
            fm.markAsPartialTake(str(test_file2))
            
            # Create FileListModel
            model = FileListModel(file_manager=fm)
            model.setFiles([str(test_file1), str(test_file2)])
            
            # Check that model exposes take status
            print("  Checking model data...")
            assert model.rowCount() == 2, "Model should have 2 files"
            
            # Get data for first file (best take)
            index0 = model.index(0, 0)
            is_best_0 = model.data(index0, model.IsBestTakeRole)
            is_partial_0 = model.data(index0, model.IsPartialTakeRole)
            
            assert is_best_0 == True, "First file should be marked as best take"
            assert is_partial_0 == False, "First file should not be marked as partial take"
            print("    ✓ Best take status exposed correctly")
            
            # Get data for second file (partial take)
            index1 = model.index(1, 0)
            is_best_1 = model.data(index1, model.IsBestTakeRole)
            is_partial_1 = model.data(index1, model.IsPartialTakeRole)
            
            assert is_best_1 == False, "Second file should not be marked as best take"
            assert is_partial_1 == True, "Second file should be marked as partial take"
            print("    ✓ Partial take status exposed correctly")
            
        print("  ✓ All FileListModel tests passed")
        return True
        
    except ImportError as e:
        print(f"  ✗ Cannot import required modules: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_qml_components():
    """Test that QML components exist."""
    print("\nChecking QML components...")
    
    components = [
        'qml/components/BestTakeIndicator.qml',
        'qml/components/PartialTakeIndicator.qml',
    ]
    
    all_exist = True
    for component in components:
        if Path(component).exists():
            print(f"  ✓ {component}")
        else:
            print(f"  ✗ {component} not found")
            all_exist = False
    
    return all_exist


def main():
    """Run all tests."""
    print("=" * 60)
    print("Best/Partial Take Indicators Test Suite")
    print("=" * 60)
    
    # Test QML components
    qml_ok = test_qml_components()
    
    # Try to test backend functionality
    try:
        import PyQt6
        fm_ok = test_file_manager_take_tracking()
        model_ok = test_model_integration()
    except ImportError:
        print("\nWarning: PyQt6 not installed, skipping backend tests")
        print("Install with: pip install PyQt6")
        fm_ok = None
        model_ok = None
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    print(f"QML Components: {'✓ PASS' if qml_ok else '✗ FAIL'}")
    if fm_ok is not None:
        print(f"FileManager Tests: {'✓ PASS' if fm_ok else '✗ FAIL'}")
    else:
        print(f"FileManager Tests: SKIPPED (PyQt6 not installed)")
    if model_ok is not None:
        print(f"Model Tests: {'✓ PASS' if model_ok else '✗ FAIL'}")
    else:
        print(f"Model Tests: SKIPPED (PyQt6 not installed)")
    
    # Return success if all tests passed (or were skipped)
    if qml_ok and (fm_ok is None or fm_ok) and (model_ok is None or model_ok):
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
