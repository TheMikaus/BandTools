#!/usr/bin/env python3
"""
Test suite for annotation export functionality.

Tests the export methods in AnnotationManager for:
- Plain text export
- CSV export  
- Markdown export
"""

import sys
import os
import tempfile
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_export_functionality():
    """Test annotation export in different formats."""
    print("=" * 60)
    print("Annotation Export Test Suite")
    print("=" * 60)
    
    # Mock PyQt6 for testing
    class MockQObject:
        def __init__(self, *args, **kwargs):
            pass
    
    class MockSignal:
        def emit(self, *args):
            pass
    
    sys.modules['PyQt6'] = type(sys)('PyQt6')
    sys.modules['PyQt6.QtCore'] = type(sys)('QtCore')
    sys.modules['PyQt6.QtCore'].QObject = MockQObject
    sys.modules['PyQt6.QtCore'].pyqtSignal = lambda *args, **kwargs: MockSignal()
    sys.modules['PyQt6.QtCore'].pyqtSlot = lambda *args, **kwargs: lambda f: f
    
    from annotation_manager import AnnotationManager
    
    # Create test instance
    manager = AnnotationManager()
    
    # Create test annotations
    test_file = "/tmp/test_audio.wav"
    manager.setCurrentFile(test_file)
    
    # Add sample annotations
    manager.addAnnotation(5000, "timing", "Tempo feels a bit slow here", False)
    manager.addAnnotation(15000, "energy", "Great energy in this section!", True)
    manager.addAnnotation(30000, "harmony", "Chord progression could be smoother", False)
    manager.addAnnotation(45000, "dynamics", "Volume drop needs attention", True)
    
    print(f"\n✓ Created {manager.getAnnotationCount()} test annotations")
    
    # Test exports
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Test 1: Plain text export
        print("\nTesting plain text export...")
        text_file = tmpdir_path / "annotations.txt"
        success = manager.exportAnnotations(str(text_file), "text")
        
        if success and text_file.exists():
            content = text_file.read_text(encoding='utf-8')
            print(f"  ✓ Text export successful ({len(content)} bytes)")
            print(f"  ✓ File contains: {content.count('[') - 1} annotations")  # -1 for header
            
            # Verify content
            assert "Tempo feels a bit slow here" in content
            assert "Great energy in this section!" in content
            assert "⭐ IMPORTANT" in content
            print("  ✓ Content verification passed")
        else:
            print("  ✗ Text export failed")
            return False
        
        # Test 2: CSV export
        print("\nTesting CSV export...")
        csv_file = tmpdir_path / "annotations.csv"
        success = manager.exportAnnotations(str(csv_file), "csv")
        
        if success and csv_file.exists():
            content = csv_file.read_text(encoding='utf-8')
            print(f"  ✓ CSV export successful ({len(content)} bytes)")
            
            # Verify CSV structure
            lines = content.strip().split('\n')
            assert len(lines) == 5  # Header + 4 annotations
            assert "Timestamp,Time" in lines[0]
            assert "timing" in content
            assert "energy" in content
            print("  ✓ CSV structure verification passed")
        else:
            print("  ✗ CSV export failed")
            return False
        
        # Test 3: Markdown export
        print("\nTesting Markdown export...")
        md_file = tmpdir_path / "annotations.md"
        success = manager.exportAnnotations(str(md_file), "markdown")
        
        if success and md_file.exists():
            content = md_file.read_text(encoding='utf-8')
            print(f"  ✓ Markdown export successful ({len(content)} bytes)")
            
            # Verify Markdown structure
            assert "# Annotations for" in content
            assert "## " in content  # Section headers
            assert "**Category:**" in content
            assert "⭐" in content  # Important marker
            print("  ✓ Markdown structure verification passed")
        else:
            print("  ✗ Markdown export failed")
            return False
        
        # Test 4: Export with no annotations
        print("\nTesting export with no annotations...")
        manager2 = AnnotationManager()
        manager2.setCurrentFile("/tmp/empty.wav")
        
        empty_file = tmpdir_path / "empty.txt"
        success = manager2.exportAnnotations(str(empty_file), "text")
        
        if not success:
            print("  ✓ Correctly rejected export with no annotations")
        else:
            print("  ✗ Should have rejected export with no annotations")
            return False
    
    return True

def test_export_formatting():
    """Test that export formatting is correct."""
    print("\n" + "=" * 60)
    print("Export Formatting Test")
    print("=" * 60)
    
    # Mock PyQt6
    class MockQObject:
        def __init__(self, *args, **kwargs):
            pass
    
    class MockSignal:
        def emit(self, *args):
            pass
    
    sys.modules['PyQt6'] = type(sys)('PyQt6')
    sys.modules['PyQt6.QtCore'] = type(sys)('QtCore')
    sys.modules['PyQt6.QtCore'].QObject = MockQObject
    sys.modules['PyQt6.QtCore'].pyqtSignal = lambda *args, **kwargs: MockSignal()
    sys.modules['PyQt6.QtCore'].pyqtSlot = lambda *args, **kwargs: lambda f: f
    
    from annotation_manager import AnnotationManager
    
    manager = AnnotationManager()
    test_file = "/tmp/format_test.wav"
    manager.setCurrentFile(test_file)
    
    # Add annotation with specific timestamp to test formatting
    manager.addAnnotation(125500, "notes", "Test formatting at 2:05.500", False)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Export and check timestamp formatting
        text_file = tmpdir_path / "format_test.txt"
        manager.exportAnnotations(str(text_file), "text")
        
        content = text_file.read_text(encoding='utf-8')
        
        # Check for proper time formatting (MM:SS.mmm)
        if "02:05.500" in content or "2:05.500" in content:
            print("✓ Timestamp formatting is correct")
            return True
        else:
            print(f"✗ Timestamp formatting is incorrect")
            print(f"Content: {content}")
            return False

def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Running Annotation Export Tests")
    print("=" * 60)
    
    tests = [
        ("Export Functionality", test_export_functionality),
        ("Export Formatting", test_export_formatting),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✓ {test_name}: PASSED")
            else:
                failed += 1
                print(f"\n✗ {test_name}: FAILED")
        except Exception as e:
            failed += 1
            print(f"\n✗ {test_name}: FAILED with exception")
            print(f"  Error: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    print("=" * 60)
    
    if failed == 0:
        print("\n✓ All tests passed!\n")
        return 0
    else:
        print(f"\n✗ {failed} test(s) failed\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
