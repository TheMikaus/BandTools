#!/usr/bin/env python3
"""
Test script to verify annotation tab switching and population.

This test validates that:
1. File selection properly loads annotations
2. Tab switching signal works correctly
3. Auto-switch functionality is connected properly
"""

import sys
import tempfile
import json
from pathlib import Path

# Add parent directory to path to import backend modules
sys.path.insert(0, str(Path(__file__).parent))

from backend.annotation_manager import AnnotationManager


def test_annotation_loading_on_file_change():
    """Test that annotations load when current file changes."""
    print("Testing annotation loading on file change...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create two mock audio files
        audio_file1 = temp_path / "song1.wav"
        audio_file1.touch()
        audio_file2 = temp_path / "song2.wav"
        audio_file2.touch()
        
        # Create annotation file for song1
        annotation_file1 = temp_path / ".song1_annotations.json"
        test_annotations1 = [
            {
                "uid": 1,
                "timestamp_ms": 1000,
                "ms": 1000,
                "text": "Song 1 annotation",
                "category": "timing",
                "important": True,
                "color": "#3498db",
                "user": "test_user",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        ]
        with open(annotation_file1, 'w') as f:
            json.dump(test_annotations1, f)
        
        # Create annotation file for song2
        annotation_file2 = temp_path / ".song2_annotations.json"
        test_annotations2 = [
            {
                "uid": 1,
                "timestamp_ms": 2000,
                "ms": 2000,
                "text": "Song 2 annotation 1",
                "category": "notes",
                "important": False,
                "color": "#e74c3c",
                "user": "test_user",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            },
            {
                "uid": 2,
                "timestamp_ms": 3000,
                "ms": 3000,
                "text": "Song 2 annotation 2",
                "category": "timing",
                "important": True,
                "color": "#2ecc71",
                "user": "test_user",
                "created_at": "2024-01-01T00:01:00",
                "updated_at": "2024-01-01T00:01:00"
            }
        ]
        with open(annotation_file2, 'w') as f:
            json.dump(test_annotations2, f)
        
        # Create annotation manager
        manager = AnnotationManager()
        manager.setCurrentDirectory(temp_path)
        manager.setCurrentUser("test_user")
        
        # Test 1: Load first file
        manager.setCurrentFile(str(audio_file1))
        count1 = manager.getAnnotationCount()
        annotations1 = manager.getAnnotations()
        
        if count1 != 1:
            print(f"  ✗ FAIL: Expected 1 annotation for song1, got {count1}")
            return False
        
        if annotations1[0]["text"] != "Song 1 annotation":
            print(f"  ✗ FAIL: Wrong annotation text for song1")
            return False
        
        print(f"  ✓ Song1 loaded: {count1} annotation")
        
        # Test 2: Switch to second file (simulating user clicking on different file)
        manager.setCurrentFile(str(audio_file2))
        count2 = manager.getAnnotationCount()
        annotations2 = manager.getAnnotations()
        
        if count2 != 2:
            print(f"  ✗ FAIL: Expected 2 annotations for song2, got {count2}")
            return False
        
        if annotations2[0]["text"] != "Song 2 annotation 1":
            print(f"  ✗ FAIL: Wrong annotation text for song2")
            return False
        
        print(f"  ✓ Song2 loaded: {count2} annotations")
        
        # Test 3: Switch back to first file
        manager.setCurrentFile(str(audio_file1))
        count3 = manager.getAnnotationCount()
        
        if count3 != 1:
            print(f"  ✗ FAIL: Expected 1 annotation when switching back to song1, got {count3}")
            return False
        
        print(f"  ✓ Switched back to Song1: {count3} annotation")
        
        print("  ✓ All file switching tests passed!")
        return True


def test_signal_connection_structure():
    """Test that the signal connection structure is correct in QML files."""
    print("\nTesting signal connection structure...")
    
    main_qml = Path("qml/main.qml")
    library_qml = Path("qml/tabs/LibraryTab.qml")
    
    # Check that LibraryTab has the signal
    with open(library_qml, 'r') as f:
        library_content = f.read()
    
    if 'signal switchToAnnotationsTab()' not in library_content:
        print("  ✗ FAIL: switchToAnnotationsTab signal not defined")
        return False
    print("  ✓ switchToAnnotationsTab signal is defined")
    
    # Check that the signal is emitted
    if 'libraryTab.switchToAnnotationsTab()' not in library_content:
        print("  ✗ FAIL: Signal not emitted")
        return False
    print("  ✓ Signal is emitted on user action")
    
    # Check that main.qml connects the signal
    with open(main_qml, 'r') as f:
        main_content = f.read()
    
    if 'onSwitchToAnnotationsTab:' not in main_content:
        print("  ✗ FAIL: Signal handler not connected in main.qml")
        return False
    print("  ✓ Signal handler connected in main.qml")
    
    # Check that the handler sets the correct tab index
    if 'onSwitchToAnnotationsTab: {' in main_content:
        # Find the handler and check it sets currentIndex
        handler_start = main_content.find('onSwitchToAnnotationsTab:')
        handler_end = main_content.find('}', handler_start) + 1
        handler_code = main_content[handler_start:handler_end]
        
        if 'tabBar.currentIndex = 0' in handler_code:
            print("  ✓ Handler sets correct tab index (0 for Annotations)")
        else:
            print("  ✗ FAIL: Handler doesn't set correct tab index")
            return False
    
    print("  ✓ All signal connection tests passed!")
    return True


def test_auto_switch_implementation():
    """Test that auto-switch is properly implemented."""
    print("\nTesting auto-switch implementation...")
    
    library_qml = Path("qml/tabs/LibraryTab.qml")
    
    with open(library_qml, 'r') as f:
        content = f.read()
    
    # Check for auto-switch check in single-click handler
    if 'settingsManager.getAutoSwitchAnnotations()' not in content:
        print("  ✗ FAIL: Auto-switch check not found")
        return False
    print("  ✓ Auto-switch check implemented")
    
    # Check that it emits the signal when auto-switch is enabled
    # Find the auto-switch section
    auto_switch_pos = content.find('settingsManager.getAutoSwitchAnnotations()')
    if auto_switch_pos > 0:
        # Check the next few lines for the signal emission
        next_section = content[auto_switch_pos:auto_switch_pos + 200]
        if 'libraryTab.switchToAnnotationsTab()' in next_section:
            print("  ✓ Auto-switch emits signal correctly")
        else:
            print("  ✗ FAIL: Auto-switch doesn't emit signal")
            return False
    
    print("  ✓ All auto-switch tests passed!")
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Annotation Tab Switching Test Suite")
    print("=" * 60)
    print()
    
    # Run tests
    test1_passed = test_annotation_loading_on_file_change()
    test2_passed = test_signal_connection_structure()
    test3_passed = test_auto_switch_implementation()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    print(f"Annotation Loading on File Change: {'✓ PASS' if test1_passed else '✗ FAIL'}")
    print(f"Signal Connection Structure: {'✓ PASS' if test2_passed else '✗ FAIL'}")
    print(f"Auto-Switch Implementation: {'✓ PASS' if test3_passed else '✗ FAIL'}")
    
    if test1_passed and test2_passed and test3_passed:
        print("\n✓ All tests passed!")
        print("\nExpected behavior:")
        print("  1. Clicking a file in Library loads and plays it")
        print("  2. Double-clicking a file switches to Annotations tab")
        print("  3. Single-click with auto-switch enabled switches to Annotations tab")
        print("  4. Annotations are properly loaded when file changes")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
