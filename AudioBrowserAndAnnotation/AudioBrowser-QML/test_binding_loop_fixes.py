#!/usr/bin/env python3
"""
Test to verify binding loop fixes in main.qml and Theme.qml
"""

import re
from pathlib import Path

def test_no_binding_loops_in_main():
    """Verify that main.qml doesn't have binding loop-causing property assignments."""
    main_qml = Path(__file__).parent / "qml" / "main.qml"
    
    with open(main_qml, 'r') as f:
        content = f.read()
    
    # Check for dialogs that should not have property assignments
    dialogs_to_check = [
        ("BatchRenameDialog", ["batchOperations", "fileManager"]),
        ("BatchConvertDialog", ["batchOperations"]),
        ("ProgressDialog", ["batchOperations"]),
        ("PracticeStatisticsDialog", ["practiceStatistics", "fileManager"]),
        ("PracticeGoalsDialog", ["practiceGoals", "practiceStatistics", "fileManager"]),
        ("SetlistBuilderDialog", ["setlistManager", "fileManager"]),
        ("ExportAnnotationsDialog", ["annotationManager", "fileManager"]),
        ("FingerprintsTab", ["fingerprintEngine", "fileManager", "fileListModel"]),
    ]
    
    all_passed = True
    
    for dialog_name, forbidden_props in dialogs_to_check:
        # Find the dialog declaration
        pattern = f"{dialog_name}\\s*{{[^}}]*?id:\\s*\\w+[^}}]*?}}"
        matches = re.findall(pattern, content, re.DOTALL)
        
        if not matches:
            print(f"✗ Could not find {dialog_name} in main.qml")
            all_passed = False
            continue
        
        dialog_section = matches[0]
        
        # Check for forbidden property assignments
        found_issues = []
        for prop in forbidden_props:
            # Check for patterns like "propertyName: propertyName"
            if re.search(f"\\b{prop}:\\s*{prop}\\b", dialog_section):
                found_issues.append(prop)
        
        if found_issues:
            print(f"✗ {dialog_name} still has binding loop-causing assignments: {found_issues}")
            all_passed = False
        else:
            print(f"✓ {dialog_name} has no binding loops")
    
    return all_passed

def test_theme_has_required_aliases():
    """Verify that Theme.qml has all required color aliases."""
    theme_qml = Path(__file__).parent / "qml" / "styles" / "Theme.qml"
    
    with open(theme_qml, 'r') as f:
        content = f.read()
    
    required_aliases = [
        "backgroundWhite",
        "primary",
        "success",
        "danger",
        "warning",
        "info",
        "textPrimary",
        "backgroundDark",
        "primaryDark",
        "highlightColor",
    ]
    
    all_passed = True
    
    for alias in required_aliases:
        if re.search(f"property\\s+color\\s+{alias}:", content):
            print(f"✓ Theme.{alias} is defined")
        else:
            print(f"✗ Theme.{alias} is NOT defined")
            all_passed = False
    
    return all_passed

def test_export_dialog_has_current_file():
    """Verify ExportAnnotationsDialog retains the currentFile binding."""
    main_qml = Path(__file__).parent / "qml" / "main.qml"
    
    with open(main_qml, 'r') as f:
        content = f.read()
    
    # Find ExportAnnotationsDialog section
    pattern = r"ExportAnnotationsDialog\s*{[^}]*?id:\s*exportAnnotationsDialog[^}]*?}"
    matches = re.findall(pattern, content, re.DOTALL)
    
    if not matches:
        print("✗ Could not find ExportAnnotationsDialog in main.qml")
        return False
    
    dialog_section = matches[0]
    
    # Check for currentFile binding
    if "currentFile:" in dialog_section:
        print("✓ ExportAnnotationsDialog retains currentFile binding")
        return True
    else:
        print("✗ ExportAnnotationsDialog is missing currentFile binding")
        return False

def main():
    print("=" * 60)
    print("Binding Loop Fixes Validation")
    print("=" * 60)
    
    test1 = test_no_binding_loops_in_main()
    print()
    test2 = test_theme_has_required_aliases()
    print()
    test3 = test_export_dialog_has_current_file()
    
    print()
    print("=" * 60)
    if test1 and test2 and test3:
        print("✓ All tests passed!")
        print("=" * 60)
        return 0
    else:
        print("✗ Some tests failed")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
