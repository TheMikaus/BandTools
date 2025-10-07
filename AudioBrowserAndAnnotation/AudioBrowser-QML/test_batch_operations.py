#!/usr/bin/env python3
"""
Batch Operations Test Script

Tests the batch operations module for the AudioBrowser QML application.
This script validates batch rename, conversion, and other operations.
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

def test_imports():
    """Test that batch operations module can be imported."""
    print("Testing batch operations import...")
    
    try:
        from backend.batch_operations import BatchOperations, sanitize_library_name
        print("  ✓ BatchOperations imported")
        return True
    except Exception as e:
        print(f"  ✗ BatchOperations import failed: {e}")
        return False


def test_instantiation():
    """Test that BatchOperations can be instantiated."""
    print("\nTesting BatchOperations instantiation...")
    
    try:
        from backend.batch_operations import BatchOperations
        bo = BatchOperations()
        print("  ✓ BatchOperations instantiated")
        
        # Test availability checks
        pydub_available = bo.isPydubAvailable()
        ffmpeg_available = bo.isFfmpegAvailable()
        
        print(f"  ℹ Pydub available: {pydub_available}")
        print(f"  ℹ FFmpeg available: {ffmpeg_available}")
        
        if not pydub_available:
            print("  ⚠ pydub not installed - conversion features will be limited")
            print("    Install with: pip install pydub")
        
        if not ffmpeg_available:
            print("  ⚠ FFmpeg not found - conversion features will be limited")
            print("    Install FFmpeg to enable audio conversion")
        
        return True
    except Exception as e:
        print(f"  ✗ BatchOperations instantiation failed: {e}")
        return False


def test_sanitize_library_name():
    """Test the sanitize_library_name function."""
    print("\nTesting sanitize_library_name...")
    
    try:
        from backend.batch_operations import sanitize_library_name
        
        test_cases = [
            ("My Song Name", "my_song_name"),
            ("Song: With Special/Chars*", "song__with_special_chars_"),
            ("  Trimmed  Spaces  ", "trimmed_spaces"),
            ("CamelCase", "camelcase"),
            ("Multiple   Spaces", "multiple_spaces"),
        ]
        
        all_passed = True
        for input_str, expected in test_cases:
            result = sanitize_library_name(input_str)
            if result == expected:
                print(f"  ✓ '{input_str}' → '{result}'")
            else:
                print(f"  ✗ '{input_str}' → '{result}' (expected '{expected}')")
                all_passed = False
        
        return all_passed
    except Exception as e:
        print(f"  ✗ sanitize_library_name test failed: {e}")
        return False


def test_batch_rename_preview():
    """Test batch rename preview functionality."""
    print("\nTesting batch rename preview...")
    
    try:
        from backend.batch_operations import BatchOperations
        
        # Create temporary directory with test files
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create test files
            test_files = []
            for i in range(5):
                test_file = tmpdir_path / f"test_file_{i}.wav"
                test_file.touch()
                test_files.append(str(test_file))
            
            # Wait a bit to ensure different creation times
            import time
            time.sleep(0.1)
            
            bo = BatchOperations()
            bo.setCurrentDirectory(str(tmpdir_path))
            
            # Test preview without pattern (use existing names)
            preview = bo.previewBatchRename(test_files, "")
            
            if len(preview) == 5:
                print(f"  ✓ Preview returned {len(preview)} items")
                
                # Check that files are numbered sequentially
                for i, item in enumerate(preview, start=1):
                    print(f"    {item['oldName']} → {item['newName']}")
                    if item['newName'].startswith(f"0{i}_"):
                        print(f"      ✓ File {i} has correct numbering")
                    else:
                        print(f"      ✗ File {i} has incorrect numbering")
                        return False
            else:
                print(f"  ✗ Preview returned {len(preview)} items (expected 5)")
                return False
            
            # Test preview with pattern
            preview_with_pattern = bo.previewBatchRename(test_files, "my_song")
            
            if len(preview_with_pattern) == 5:
                print(f"  ✓ Preview with pattern returned {len(preview_with_pattern)} items")
                
                # Check that pattern is applied
                for i, item in enumerate(preview_with_pattern, start=1):
                    if "my_song" in item['newName']:
                        print(f"    ✓ {item['newName']} contains pattern")
                    else:
                        print(f"    ✗ {item['newName']} missing pattern")
                        return False
            else:
                print(f"  ✗ Preview with pattern returned {len(preview_with_pattern)} items (expected 5)")
                return False
        
        return True
    except Exception as e:
        print(f"  ✗ Batch rename preview test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_worker_classes():
    """Test that worker classes can be instantiated."""
    print("\nTesting worker classes...")
    
    try:
        from backend.batch_operations import (
            BatchRenameWorker, 
            ConvertWorker, 
            MonoConvertWorker,
            VolumeBoostWorker
        )
        
        # Test BatchRenameWorker
        rename_plan = [(Path("test1.wav"), Path("test2.wav"))]
        worker1 = BatchRenameWorker(rename_plan)
        print("  ✓ BatchRenameWorker instantiated")
        
        # Test ConvertWorker
        worker2 = ConvertWorker(["test.wav"], "192k")
        print("  ✓ ConvertWorker instantiated")
        
        # Test MonoConvertWorker
        worker3 = MonoConvertWorker("test.wav", True, True)
        print("  ✓ MonoConvertWorker instantiated")
        
        # Test VolumeBoostWorker
        worker4 = VolumeBoostWorker("test.wav", 3.0)
        print("  ✓ VolumeBoostWorker instantiated")
        
        return True
    except Exception as e:
        print(f"  ✗ Worker class test failed: {e}")
        return False


def test_syntax():
    """Test Python syntax for batch operations module."""
    import ast
    
    print("\nTesting Python syntax...")
    
    try:
        with open('backend/batch_operations.py', 'r') as f:
            ast.parse(f.read())
        print("  ✓ backend/batch_operations.py")
        return True
    except Exception as e:
        print(f"  ✗ backend/batch_operations.py: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("AudioBrowser QML Batch Operations Test Suite")
    print("=" * 60)
    
    # Test syntax first (doesn't require PyQt6)
    syntax_ok = test_syntax()
    
    # Try to run other tests (require PyQt6)
    try:
        import PyQt6
        imports_ok = test_imports()
        instantiation_ok = test_instantiation() if imports_ok else False
        sanitize_ok = test_sanitize_library_name() if imports_ok else False
        preview_ok = test_batch_rename_preview() if imports_ok else False
        workers_ok = test_worker_classes() if imports_ok else False
    except ImportError:
        print("\nWarning: PyQt6 not installed, skipping most tests")
        print("Install with: pip install PyQt6")
        imports_ok = None
        instantiation_ok = None
        sanitize_ok = None
        preview_ok = None
        workers_ok = None
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    print(f"Python Syntax: {'✓ PASS' if syntax_ok else '✗ FAIL'}")
    
    if imports_ok is not None:
        print(f"Module Import: {'✓ PASS' if imports_ok else '✗ FAIL'}")
        print(f"Instantiation: {'✓ PASS' if instantiation_ok else '✗ FAIL'}")
        print(f"Sanitize Names: {'✓ PASS' if sanitize_ok else '✗ FAIL'}")
        print(f"Rename Preview: {'✓ PASS' if preview_ok else '✗ FAIL'}")
        print(f"Worker Classes: {'✓ PASS' if workers_ok else '✗ FAIL'}")
    else:
        print("Other Tests: SKIPPED (PyQt6 not installed)")
    
    # Return success if all tests passed (or were skipped)
    all_passed = syntax_ok and (
        imports_ok is None or 
        (imports_ok and instantiation_ok and sanitize_ok and preview_ok and workers_ok)
    )
    
    if all_passed:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
