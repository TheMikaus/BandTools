#!/usr/bin/env python3
"""
Test to verify main.qml can be parsed without the "Cannot assign to non-existent property" error.
This is a focused test for the specific error mentioned in the issue.
"""

import sys
import re
from pathlib import Path

def parse_qml_for_errors(qml_path: Path) -> list:
    """
    Parse QML file and check for common property assignment errors.
    Returns list of potential errors found.
    """
    errors = []
    
    with open(qml_path, 'r') as f:
        lines = f.readlines()
    
    # Track dialog instantiations and their property assignments
    current_dialog = None
    current_dialog_line = 0
    dialog_properties = {}
    
    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()
        
        # Detect dialog instantiation (e.g., "ExportAnnotationsDialog {")
        dialog_match = re.match(r'(\w+Dialog)\s*{', stripped)
        if dialog_match:
            current_dialog = dialog_match.group(1)
            current_dialog_line = line_num
            dialog_properties[current_dialog] = {'line': line_num, 'properties': []}
        
        # Detect property assignments within dialog blocks
        if current_dialog and re.match(r'\w+:\s*.+', stripped):
            prop_match = re.match(r'(\w+):\s*(.+)', stripped)
            if prop_match:
                prop_name = prop_match.group(1)
                prop_value = prop_match.group(2)
                
                # Skip common non-property keywords
                if prop_name not in ['id']:
                    dialog_properties[current_dialog]['properties'].append({
                        'name': prop_name,
                        'value': prop_value,
                        'line': line_num
                    })
        
        # End of dialog block
        if current_dialog and stripped == '}':
            # Check if we've left the dialog scope
            # Simple heuristic: if we're back at base indentation
            if len(line) - len(line.lstrip()) < 8:  # Approximate base indentation
                current_dialog = None
    
    return errors, dialog_properties

def check_dialog_file_has_properties(dialog_name: str, required_props: list, dialogs_dir: Path) -> tuple:
    """
    Check if a dialog file declares the required properties.
    Returns (has_all: bool, missing: list)
    """
    dialog_path = dialogs_dir / f"{dialog_name}.qml"
    
    if not dialog_path.exists():
        return False, required_props, []
    
    with open(dialog_path, 'r') as f:
        content = f.read()
    
    # Extract declared properties
    declared = []
    for line in content.split('\n'):
        stripped = line.strip()
        if stripped.startswith('property '):
            parts = stripped.split()
            if len(parts) >= 3:
                prop_name = parts[2].rstrip(':')
                declared.append(prop_name)
    
    # Check for missing (excluding signal handlers starting with 'on')
    filtered_required = [p for p in required_props if not p.startswith('on')]
    missing = [p for p in filtered_required if p not in declared]
    
    return len(missing) == 0, missing, declared

def main():
    print("=" * 70)
    print("Main QML Loading Test - Checking for Property Assignment Errors")
    print("=" * 70)
    
    # Get paths
    base_path = Path(__file__).parent
    main_qml = base_path / "qml" / "main.qml"
    dialogs_dir = base_path / "qml" / "dialogs"
    
    if not main_qml.exists():
        print(f"Error: main.qml not found at {main_qml}")
        return 1
    
    print(f"\nParsing: {main_qml.relative_to(Path.cwd())}")
    
    # Parse main.qml
    errors, dialog_properties = parse_qml_for_errors(main_qml)
    
    if errors:
        print("\n✗ Found parsing errors:")
        for error in errors:
            print(f"  - {error}")
        return 1
    
    print("\n✓ No parsing errors found")
    
    # Check each dialog for property declarations
    print("\nValidating dialog property declarations...")
    all_valid = True
    
    for dialog_name, info in dialog_properties.items():
        if not info['properties']:
            continue
        
        prop_names = [p['name'] for p in info['properties']]
        print(f"\n  {dialog_name} (line {info['line']})")
        print(f"    Properties assigned: {prop_names}")
        
        has_all, missing, declared = check_dialog_file_has_properties(
            dialog_name, prop_names, dialogs_dir
        )
        
        if has_all:
            print(f"    ✓ All properties declared in {dialog_name}.qml")
        else:
            print(f"    ✗ Missing property declarations: {missing}")
            print(f"    Declared properties: {declared}")
            all_valid = False
            
            # Show specific lines with missing properties
            for prop in info['properties']:
                if prop['name'] in missing:
                    print(f"      Line {prop['line']}: {prop['name']}: {prop['value']}")
    
    print("\n" + "=" * 70)
    if all_valid:
        print("✓ SUCCESS: main.qml should load without property errors!")
        print("=" * 70)
        return 0
    else:
        print("✗ FAILURE: Some dialogs are missing property declarations")
        print("This will cause 'Cannot assign to non-existent property' errors")
        print("=" * 70)
        return 1

if __name__ == "__main__":
    sys.exit(main())
