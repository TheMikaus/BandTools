#!/usr/bin/env python3
"""
Validation script to check that the QML errors have been fixed.
This script checks for the specific issues mentioned in the error report:
1. Duplicate signal name in ProgressDialog.qml
2. Non-existent "info" property in StyledButton usage
"""

import sys
from pathlib import Path

def check_progress_dialog():
    """Check ProgressDialog.qml for duplicate signal."""
    print("\n1. Checking ProgressDialog.qml...")
    file_path = Path("qml/dialogs/ProgressDialog.qml")
    
    if not file_path.exists():
        print(f"   ✗ File not found: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
        lines = content.split('\n')
    
    # Check for duplicate "signal closed()" declaration
    signal_closed_count = 0
    signal_closed_lines = []
    
    for i, line in enumerate(lines, 1):
        if 'signal closed()' in line and not line.strip().startswith('//'):
            signal_closed_count += 1
            signal_closed_lines.append(i)
    
    if signal_closed_count > 0:
        print(f"   ✗ Found {signal_closed_count} 'signal closed()' declaration(s) at line(s): {signal_closed_lines}")
        print(f"      This conflicts with Dialog's built-in closed() signal")
        return False
    
    print(f"   ✓ No duplicate 'signal closed()' found")
    
    # Check that cancelRequested signal still exists
    if 'signal cancelRequested()' in content:
        print(f"   ✓ cancelRequested() signal present")
    else:
        print(f"   ✗ cancelRequested() signal missing")
        return False
    
    return True

def check_styled_button():
    """Check StyledButton.qml for info property."""
    print("\n2. Checking StyledButton.qml...")
    file_path = Path("qml/components/StyledButton.qml")
    
    if not file_path.exists():
        print(f"   ✗ File not found: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check for info property declaration
    if 'property bool info:' not in content:
        print(f"   ✗ 'property bool info' not found")
        return False
    
    print(f"   ✓ 'property bool info' property declared")
    
    # Check for Theme.accentInfo usage
    if 'Theme.accentInfo' not in content:
        print(f"   ✗ Theme.accentInfo not used")
        return False
    
    print(f"   ✓ Theme.accentInfo color used")
    
    # Check that info is included in color logic
    checks = [
        ('if (primary || danger || success || info)', 'text color check'),
        ('if (info) return Qt.darker(Theme.accentInfo', 'pressed state'),
        ('if (info) return Qt.lighter(Theme.accentInfo', 'hover state'),
        ('if (info) return Theme.accentInfo', 'normal state'),
        ('border.width: primary || danger || success || info', 'border width')
    ]
    
    for check_str, description in checks:
        if check_str in content:
            print(f"   ✓ Info property used in {description}")
        else:
            print(f"   ✗ Info property NOT used in {description}")
            return False
    
    return True

def check_library_tab():
    """Check LibraryTab.qml uses info property correctly."""
    print("\n3. Checking LibraryTab.qml...")
    file_path = Path("qml/tabs/LibraryTab.qml")
    
    if not file_path.exists():
        print(f"   ✗ File not found: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Count uses of info: property
    info_count = content.count('info:')
    
    if info_count == 0:
        print(f"   ✗ No 'info:' property usage found")
        return False
    
    print(f"   ✓ Found {info_count} uses of 'info:' property")
    
    # Make sure StyledButton is imported
    if 'StyledButton' in content:
        print(f"   ✓ StyledButton component used")
    else:
        print(f"   ✗ StyledButton component not found")
        return False
    
    return True

def main():
    print("=" * 60)
    print("QML Fix Validation")
    print("=" * 60)
    print("\nValidating fixes for reported QML errors:")
    print("  - ProgressDialog.qml:38 - Duplicate signal name")
    print("  - LibraryTab.qml:107 - Non-existent property 'info'")
    
    all_passed = True
    
    # Run checks
    if not check_progress_dialog():
        all_passed = False
    
    if not check_styled_button():
        all_passed = False
    
    if not check_library_tab():
        all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All validation checks passed!")
        print("=" * 60)
        print("\nThe QML errors should now be fixed:")
        print("  ✓ Removed duplicate 'signal closed()' from ProgressDialog")
        print("  ✓ Added 'info' property to StyledButton")
        print("  ✓ StyledButton properly styled with Theme.accentInfo")
        print("  ✓ LibraryTab can now use 'info: true'")
        return 0
    else:
        print("✗ Some validation checks failed")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    # Change to the script directory
    script_dir = Path(__file__).parent
    import os
    os.chdir(script_dir)
    
    sys.exit(main())
