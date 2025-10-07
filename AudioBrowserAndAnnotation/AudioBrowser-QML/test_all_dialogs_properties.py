#!/usr/bin/env python3
"""
Test to verify all Dialog components have proper property declarations
for properties assigned in main.qml.
"""

import sys
import re
from pathlib import Path

def extract_property_assignments(main_qml_path: Path) -> dict:
    """
    Extract property assignments from main.qml for each dialog.
    Returns dict: {dialog_id: [list of properties assigned]}
    """
    with open(main_qml_path, 'r') as f:
        content = f.read()
    
    assignments = {}
    current_dialog = None
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Detect dialog declarations
        if 'Dialog {' in stripped or stripped.endswith('Dialog {'):
            # Look ahead for id
            for j in range(i, min(i+5, len(lines))):
                id_match = re.search(r'id:\s*(\w+)', lines[j])
                if id_match:
                    current_dialog = id_match.group(1)
                    assignments[current_dialog] = []
                    break
        
        # Detect property assignments
        if current_dialog and ':' in stripped:
            # Match property assignments like "propertyName: value"
            prop_match = re.match(r'(\w+):\s*.+', stripped)
            if prop_match:
                prop_name = prop_match.group(1)
                # Skip common non-property keywords
                if prop_name not in ['id', 'import', 'property', 'function', 'signal', 
                                     'onClicked', 'onAccepted', 'onRejected', 'onClosed']:
                    assignments[current_dialog].append(prop_name)
        
        # End of dialog block
        if current_dialog and stripped == '}' and 'Dialog' in str(lines[i-10:i]):
            current_dialog = None
    
    return assignments

def check_dialog_properties(dialog_path: Path, expected_props: list) -> tuple:
    """
    Check if dialog file declares all expected properties.
    Returns (success: bool, missing_props: list, declared_props: list)
    """
    with open(dialog_path, 'r') as f:
        content = f.read()
    
    # Extract declared properties
    declared_props = []
    for line in content.split('\n'):
        stripped = line.strip()
        if stripped.startswith('property '):
            # Extract property name
            parts = stripped.split()
            if len(parts) >= 3:
                prop_name = parts[2].rstrip(':')
                declared_props.append(prop_name)
    
    # Check for missing properties
    # Filter out properties that are likely internal Qt properties or signal handlers
    expected_filtered = [p for p in expected_props 
                        if p not in ['anchors', 'visible', 'x', 'y', 'width', 'height']
                        and not p.startswith('on')]  # Signal handlers like onClicked, onRenameCompleted
    
    missing = [p for p in expected_filtered if p not in declared_props and p not in content]
    
    return len(missing) == 0, missing, declared_props

def main():
    print("=" * 60)
    print("Dialog Properties Validation")
    print("=" * 60)
    
    # Get paths
    base_path = Path(__file__).parent
    main_qml = base_path / "qml" / "main.qml"
    dialogs_dir = base_path / "qml" / "dialogs"
    
    if not main_qml.exists():
        print(f"Error: main.qml not found at {main_qml}")
        return 1
    
    if not dialogs_dir.exists():
        print(f"Error: dialogs directory not found at {dialogs_dir}")
        return 1
    
    # Extract property assignments from main.qml
    print("\nExtracting property assignments from main.qml...")
    assignments = extract_property_assignments(main_qml)
    
    all_passed = True
    
    # Check each dialog
    for dialog_id, props in assignments.items():
        if not props:
            continue
        
        # Find the dialog file
        # Convert camelCase ID to expected filename
        # e.g., batchRenameDialog -> BatchRenameDialog.qml
        dialog_filename = ''.join(word.capitalize() for word in 
                                 re.findall(r'[A-Z][a-z]*|[a-z]+', dialog_id)) + '.qml'
        dialog_path = dialogs_dir / dialog_filename
        
        if not dialog_path.exists():
            print(f"\n⚠  Warning: Dialog file not found for {dialog_id}: {dialog_filename}")
            continue
        
        print(f"\nChecking: {dialog_filename}")
        print(f"  Dialog ID: {dialog_id}")
        print(f"  Properties assigned in main.qml: {props}")
        
        success, missing, declared = check_dialog_properties(dialog_path, props)
        
        print(f"  Properties declared in dialog: {declared}")
        
        if not success:
            print(f"  ✗ FAILED: Missing property declarations: {missing}")
            all_passed = False
        else:
            print(f"  ✓ PASSED: All required properties declared")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All dialogs have proper property declarations!")
        print("=" * 60)
        return 0
    else:
        print("✗ Some dialogs are missing property declarations")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
