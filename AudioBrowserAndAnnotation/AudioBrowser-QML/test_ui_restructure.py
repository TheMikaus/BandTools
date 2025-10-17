#!/usr/bin/env python3
"""
Test script to verify UI restructure and annotation tab switching.

This test validates:
1. LibraryTab signal connections work properly
2. Tab indices are correct after restructuring
3. Annotation tab switching works when clicking files
"""

import sys
from pathlib import Path

def test_qml_structure():
    """Test that QML files have expected structure."""
    print("Testing QML structure...")
    
    main_qml = Path("qml/main.qml")
    library_qml = Path("qml/tabs/LibraryTab.qml")
    
    # Check main.qml
    with open(main_qml, 'r') as f:
        main_content = f.read()
    
    # Verify Library is not in TabBar anymore
    if 'TabButton {\n                text: "Library"' in main_content:
        print("  ✗ FAIL: Library is still in TabBar")
        return False
    else:
        print("  ✓ Library removed from TabBar")
    
    # Verify Library is always visible on the left side
    if 'LibraryTab {' in main_content and '// Library panel (always visible on left side)' in main_content:
        print("  ✓ Library panel is always visible on left side")
    else:
        print("  ✗ FAIL: Library panel not found or not always visible")
        return False
    
    # Verify Annotations tab is first (index 0)
    if 'text: "Annotations"' in main_content:
        # Check it comes before other tabs
        annotations_pos = main_content.find('text: "Annotations"')
        clips_pos = main_content.find('text: "Clips"')
        if annotations_pos < clips_pos:
            print("  ✓ Annotations tab is first in TabBar")
        else:
            print("  ✗ FAIL: Tab order incorrect")
            return False
    else:
        print("  ✗ FAIL: Annotations tab not found")
        return False
    
    # Check LibraryTab.qml
    with open(library_qml, 'r') as f:
        library_content = f.read()
    
    # Verify signal exists
    if 'signal switchToAnnotationsTab()' in library_content:
        print("  ✓ switchToAnnotationsTab signal defined")
    else:
        print("  ✗ FAIL: switchToAnnotationsTab signal not found")
        return False
    
    # Verify signal is emitted on double-click
    if 'libraryTab.switchToAnnotationsTab()' in library_content:
        print("  ✓ Signal emitted on double-click")
    else:
        print("  ✗ FAIL: Signal not emitted properly")
        return False
    
    # Verify auto-switch on single click
    if 'settingsManager.getAutoSwitchAnnotations()' in library_content:
        print("  ✓ Auto-switch on single click implemented")
    else:
        print("  ✗ FAIL: Auto-switch not implemented")
        return False
    
    print("  ✓ All structure tests passed!")
    return True


def test_tab_indices():
    """Test that tab indices are correctly updated."""
    print("\nTesting tab indices...")
    
    main_qml = Path("qml/main.qml")
    with open(main_qml, 'r') as f:
        content = f.read()
    
    # Check keyboard shortcuts
    shortcuts = [
        ("Ctrl+1", "0", "Annotations"),
        ("Ctrl+2", "1", "Clips"),
        ("Ctrl+3", "2", "Sections"),
        ("Ctrl+4", "3", "Folder Notes"),
        ("Ctrl+5", "4", "Fingerprints"),
    ]
    
    for shortcut, expected_index, tab_name in shortcuts:
        pattern = f'sequence: "{shortcut}"'
        if pattern in content:
            # Find the onActivated line after this shortcut
            shortcut_pos = content.find(pattern)
            next_activated = content.find("onActivated: tabBar.currentIndex =", shortcut_pos)
            if next_activated > shortcut_pos:
                line_end = content.find("\n", next_activated)
                line = content[next_activated:line_end]
                if f"= {expected_index}" in line:
                    print(f"  ✓ {shortcut} -> {tab_name} (index {expected_index})")
                else:
                    print(f"  ✗ FAIL: {shortcut} has wrong index")
                    return False
    
    # Check signal connections use correct indices
    checks = [
        ("onSwitchToAnnotationsTab", "tabBar.currentIndex = 0", "Library double-click"),
        ("onRequestAnnotationTab", "tabBar.currentIndex = 0", "Context menu annotation"),
        ("onRequestClipsTab", "tabBar.currentIndex = 1", "Context menu clips"),
        ("onRequestClipEdit", "tabBar.currentIndex = 1", "Clip edit from annotations"),
    ]
    
    for signal, expected_code, description in checks:
        if signal in content:
            # Find the code after this signal
            signal_pos = content.find(signal)
            next_section = content.find(expected_code, signal_pos, signal_pos + 500)
            if next_section > signal_pos:
                print(f"  ✓ {description} uses correct index")
            else:
                print(f"  ✗ FAIL: {description} index incorrect")
                return False
    
    print("  ✓ All tab indices correct!")
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("UI Restructure Test Suite")
    print("=" * 60)
    print()
    
    # Change to test directory
    test_dir = Path(__file__).parent
    import os
    os.chdir(test_dir)
    
    # Run tests
    test1_passed = test_qml_structure()
    test2_passed = test_tab_indices()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    print(f"QML Structure: {'✓ PASS' if test1_passed else '✗ FAIL'}")
    print(f"Tab Indices: {'✓ PASS' if test2_passed else '✗ FAIL'}")
    
    if test1_passed and test2_passed:
        print("\n✓ All tests passed!")
        print("\nExpected behavior:")
        print("  - Library panel is always visible on the left side (350px width)")
        print("  - Annotations, Clips, Sections, Folder Notes, and Fingerprints tabs are on the right")
        print("  - Double-clicking a file in Library switches to Annotations tab")
        print("  - Single-clicking a file with auto-switch enabled switches to Annotations tab")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
