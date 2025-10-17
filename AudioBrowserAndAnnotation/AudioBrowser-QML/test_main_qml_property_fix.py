#!/usr/bin/env python3
"""
Test to verify that main.qml uses the correct method call for getCurrentFile()
instead of accessing the non-existent currentFile property.

This test validates the fix for the QML error:
"Unable to assign [undefined] to QString"
"""

import sys
from pathlib import Path


def test_main_qml_property_usage():
    """Check that main.qml uses getCurrentFile() method, not currentFile property."""
    print("=" * 60)
    print("Testing main.qml for correct audioEngine property usage")
    print("=" * 60)
    
    main_qml = Path(__file__).parent / "qml" / "main.qml"
    
    if not main_qml.exists():
        print(f"Error: main.qml not found at {main_qml}")
        return False
    
    with open(main_qml, 'r') as f:
        content = f.read()
        lines = content.split('\n')
    
    # Check for incorrect usage: audioEngine.currentFile
    incorrect_pattern = "audioEngine.currentFile"
    incorrect_lines = []
    
    for i, line in enumerate(lines, start=1):
        if incorrect_pattern in line and "getCurrentFile()" not in line:
            incorrect_lines.append((i, line.strip()))
    
    # Check for correct usage: audioEngine.getCurrentFile()
    correct_pattern = "audioEngine.getCurrentFile()"
    correct_count = content.count(correct_pattern)
    
    print(f"\n✓ Found {correct_count} correct usages of audioEngine.getCurrentFile()")
    
    if incorrect_lines:
        print(f"\n✗ FAILED: Found {len(incorrect_lines)} incorrect usage(s) of audioEngine.currentFile:")
        for line_num, line_text in incorrect_lines:
            print(f"  Line {line_num}: {line_text}")
        print("\nThe AudioEngine class exposes getCurrentFile() as a method, not currentFile as a property.")
        print("Using audioEngine.currentFile results in 'undefined' being assigned to QString properties.")
        return False
    
    print("\n✓ PASSED: No incorrect usages found")
    print("  All references correctly use audioEngine.getCurrentFile() method")
    
    # Additional check: verify ExportAnnotationsDialog uses the correct pattern
    export_dialog_section = False
    for i, line in enumerate(lines, start=1):
        if "ExportAnnotationsDialog" in line:
            export_dialog_section = True
            start_line = i
        
        if export_dialog_section and "currentFile:" in line:
            if "audioEngine.getCurrentFile()" in line:
                print(f"\n✓ ExportAnnotationsDialog (line {i}) correctly uses getCurrentFile()")
            else:
                print(f"\n✗ ExportAnnotationsDialog (line {i}) has incorrect binding")
                return False
            export_dialog_section = False
    
    return True


if __name__ == "__main__":
    print(__doc__)
    success = test_main_qml_property_usage()
    print("\n" + "=" * 60)
    if success:
        print("All tests passed!")
        sys.exit(0)
    else:
        print("Tests failed!")
        sys.exit(1)
