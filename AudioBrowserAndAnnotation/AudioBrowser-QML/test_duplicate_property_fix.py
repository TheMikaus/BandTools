#!/usr/bin/env python3
"""
Test to verify that main.qml does not have duplicate property assignments.
This specifically tests for the "Property value set multiple times" error
at line 391 in the menuBar section.

The fix removed the duplicate 'background' property that was defined twice 
at the MenuBar root level (lines 81 and 391).
"""

import sys
from pathlib import Path


def check_menubar_duplicate_background():
    """
    Check that MenuBar doesn't have duplicate 'background' property at the root level.
    
    The issue was that 'background' was defined twice at the MenuBar root:
    - Once at the beginning (line ~81)
    - Once at the end (line ~391)
    
    This test verifies only one 'background' property exists at MenuBar root level.
    Note: Nested delegates can have their own 'background' properties - those are fine.
    """
    print("=" * 70)
    print("Testing main.qml for duplicate MenuBar root-level properties")
    print("=" * 70)
    
    main_qml = Path(__file__).parent / "qml" / "main.qml"
    
    if not main_qml.exists():
        print(f"Error: main.qml not found at {main_qml}")
        return False
    
    with open(main_qml, 'r') as f:
        lines = f.readlines()
    
    # Find the MenuBar section and look for root-level background properties
    in_menubar = False
    menubar_start = 0
    menubar_end = 0
    depth = 0  # Track nesting depth
    root_background_lines = []  # Only root-level background properties
    
    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        
        # Detect MenuBar start
        if 'menuBar: MenuBar {' in line:
            in_menubar = True
            menubar_start = i
            depth = 0  # Start at depth 0, will become 1 after processing this line
        
        if in_menubar:
            # Check for 'background' property at depth 0 (root level inside MenuBar)
            # This must be done BEFORE updating depth
            if stripped.startswith('background:') and depth == 0:
                root_background_lines.append(i)
            
            # Track depth by counting braces
            depth += line.count('{') - line.count('}')
            
            # End of MenuBar section (depth becomes negative when we close MenuBar)
            if depth < 0:
                menubar_end = i
                in_menubar = False
                break
    
    print(f"\nMenuBar section: lines {menubar_start}-{menubar_end}")
    print(f"Found {len(root_background_lines)} root-level 'background' property definition(s)")
    
    if len(root_background_lines) > 1:
        print(f"\n✗ FAILED: Multiple root-level 'background' properties found at lines:")
        for line_num in root_background_lines:
            print(f"  Line {line_num}: {lines[line_num-1].strip()}")
        print("\nQML error: Property value set multiple times")
        print("Fix: Remove the duplicate 'background' property definition")
        return False
    elif len(root_background_lines) == 1:
        print(f"  Line {root_background_lines[0]}: {lines[root_background_lines[0]-1].strip()}")
        print("\n✓ PASSED: Only one root-level 'background' property definition found")
        return True
    else:
        print("\n⚠ WARNING: No root-level 'background' property found in MenuBar")
        return True


def check_line_391_removed():
    """Verify that line 391 no longer has a duplicate 'background: Rectangle' statement."""
    print("\n" + "=" * 70)
    print("Verifying specific fix: line 391 duplicate removed")
    print("=" * 70)
    
    main_qml = Path(__file__).parent / "qml" / "main.qml"
    
    with open(main_qml, 'r') as f:
        lines = f.readlines()
    
    # Check around line 391 (accounting for potential line number shifts)
    # The old code had "background: Rectangle {" around line 391 after the Help menu
    # After fix, line 391 should be in the main content area, not in MenuBar
    
    context_start = max(0, 390 - 5)  # Check a few lines before
    context_end = min(len(lines), 391 + 5)  # Check a few lines after
    
    print(f"\nChecking lines {context_start+1}-{context_end} around former line 391:")
    
    found_duplicate = False
    for i in range(context_start, context_end):
        if i < len(lines):
            line = lines[i]
            line_num = i + 1
            
            # Show context
            if 385 <= line_num <= 395:
                prefix = "  "
                if line_num == 391:
                    prefix = "→ "
                print(f"{prefix}Line {line_num:3d}: {line.rstrip()}")
            
            # Check if this line has the problematic duplicate
            if line_num == 391 and 'background: Rectangle' in line:
                found_duplicate = True
    
    if found_duplicate:
        print("\n✗ FAILED: Line 391 still has 'background: Rectangle'")
        print("The duplicate property was not removed")
        return False
    else:
        print("\n✓ PASSED: Line 391 no longer has duplicate 'background: Rectangle'")
        print("The fix has been successfully applied")
        return True


if __name__ == "__main__":
    print(__doc__)
    
    # Run the specific MenuBar check
    menubar_ok = check_menubar_duplicate_background()
    
    # Run line 391 specific check
    line391_ok = check_line_391_removed()
    
    print("\n" + "=" * 70)
    if menubar_ok and line391_ok:
        print("✓ All tests passed!")
        print("The QML file should load without 'Property value set multiple times' error")
        print("=" * 70)
        sys.exit(0)
    else:
        print("✗ Tests failed!")
        print("=" * 70)
        sys.exit(1)
