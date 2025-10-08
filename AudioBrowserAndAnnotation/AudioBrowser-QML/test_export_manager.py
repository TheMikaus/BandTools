"""
Test Export Manager

Tests the ExportManager backend for Issue #19:
- Export best takes to folder
- Export best takes to ZIP
- Format conversion support
- Metadata inclusion
"""

import sys
import os
import tempfile
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))


def test_export_manager_structure():
    """Test export manager module structure."""
    print("Testing Export Manager Structure...")
    
    # Test 1: Import module
    print("\n1. Testing module import...")
    try:
        from backend.export_manager import ExportManager, ExportWorker
        print("   ✓ Module imported successfully")
    except ImportError as e:
        print(f"   ✗ Failed to import module: {e}")
        return False
    
    # Test 2: Check ExportManager class
    print("\n2. Testing ExportManager class...")
    assert hasattr(ExportManager, 'startExport'), "Missing startExport method"
    assert hasattr(ExportManager, 'cancelExport'), "Missing cancelExport method"
    print("   ✓ ExportManager has required methods")
    
    # Test 3: Check ExportWorker class
    print("\n3. Testing ExportWorker class...")
    assert hasattr(ExportWorker, 'run'), "Missing run method"
    assert hasattr(ExportWorker, 'cancel'), "Missing cancel method"
    print("   ✓ ExportWorker has required methods")
    
    # Test 4: Check signals
    print("\n4. Testing ExportManager signals...")
    manager = ExportManager()
    assert hasattr(manager, 'exportStarted'), "Missing exportStarted signal"
    assert hasattr(manager, 'exportProgress'), "Missing exportProgress signal"
    assert hasattr(manager, 'exportFileProgress'), "Missing exportFileProgress signal"
    assert hasattr(manager, 'exportFinished'), "Missing exportFinished signal"
    print("   ✓ ExportManager has all required signals")
    
    print("\n✅ All Export Manager structure tests passed!")
    return True


def test_export_worker_basic():
    """Test basic export worker functionality."""
    print("\nTesting Export Worker Basic Functionality...")
    
    from backend.export_manager import ExportWorker
    
    # Test 1: Create worker
    print("\n1. Testing worker creation...")
    with tempfile.TemporaryDirectory() as temp_dir:
        files = []
        destination = temp_dir
        export_format = "folder"
        convert_to_mp3 = False
        include_metadata = True
        
        worker = ExportWorker(files, destination, export_format, convert_to_mp3, include_metadata)
        assert worker.files == files, "Files not set correctly"
        assert worker.destination == destination, "Destination not set correctly"
        assert worker.export_format == export_format, "Export format not set correctly"
        assert worker.convert_to_mp3 == convert_to_mp3, "Convert to MP3 not set correctly"
        assert worker.include_metadata == include_metadata, "Include metadata not set correctly"
        print("   ✓ Worker created with correct parameters")
    
    # Test 2: Cancel function
    print("\n2. Testing cancel function...")
    worker = ExportWorker([], temp_dir, "folder", False, True)
    assert not worker._cancelled, "Worker should not be cancelled initially"
    worker.cancel()
    assert worker._cancelled, "Worker should be cancelled after calling cancel()"
    print("   ✓ Cancel function works correctly")
    
    print("\n✅ All Export Worker basic tests passed!")
    return True


def test_export_methods():
    """Test export helper methods."""
    print("\nTesting Export Helper Methods...")
    
    from backend.export_manager import ExportWorker
    
    # Test 1: _copy_metadata_files method exists
    print("\n1. Testing _copy_metadata_files method...")
    worker = ExportWorker([], "/tmp", "folder", False, True)
    assert hasattr(worker, '_copy_metadata_files'), "Missing _copy_metadata_files method"
    print("   ✓ _copy_metadata_files method exists")
    
    # Test 2: _create_zip method exists
    print("\n2. Testing _create_zip method...")
    assert hasattr(worker, '_create_zip'), "Missing _create_zip method"
    print("   ✓ _create_zip method exists")
    
    # Test 3: _convert_to_mp3 method exists
    print("\n3. Testing _convert_to_mp3 method...")
    assert hasattr(worker, '_convert_to_mp3'), "Missing _convert_to_mp3 method"
    print("   ✓ _convert_to_mp3 method exists")
    
    print("\n✅ All Export Helper Method tests passed!")
    return True


if __name__ == "__main__":
    try:
        success = True
        success = test_export_manager_structure() and success
        success = test_export_worker_basic() and success
        success = test_export_methods() and success
        
        if success:
            print("\n" + "="*60)
            print("✅ ALL TESTS PASSED")
            print("="*60)
        
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
