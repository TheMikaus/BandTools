#!/usr/bin/env python3
"""
Validation script to check that the QML binding loop issues have been fixed.
This script checks that:
1. Dialog property bindings have been removed from main.qml
2. Context menu property bindings have been removed from LibraryTab.qml
3. Local property definitions have been removed from dialogs/components
4. Dialogs/components use context properties directly
"""

import sys
from pathlib import Path

def check_main_qml():
    """Check main.qml for binding loop issues."""
    print("\n1. Checking main.qml...")
    file_path = Path("qml/main.qml")
    
    if not file_path.exists():
        print(f"   ✗ File not found: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Check that dialog property bindings have been removed
    issues = []
    
    # Find PracticeStatisticsDialog
    in_practice_stats = False
    for i, line in enumerate(lines, 1):
        if 'PracticeStatisticsDialog {' in line:
            in_practice_stats = True
        elif in_practice_stats:
            if 'practiceStatistics:' in line:
                issues.append(f"Line {i}: PracticeStatisticsDialog has practiceStatistics binding")
            if 'fileManager:' in line and 'PracticeStatisticsDialog' not in line:
                issues.append(f"Line {i}: PracticeStatisticsDialog has fileManager binding")
            if '}' in line:
                in_practice_stats = False
    
    # Find PracticeGoalsDialog
    in_practice_goals = False
    for i, line in enumerate(lines, 1):
        if 'PracticeGoalsDialog {' in line:
            in_practice_goals = True
        elif in_practice_goals:
            if 'practiceGoals:' in line:
                issues.append(f"Line {i}: PracticeGoalsDialog has practiceGoals binding")
            if 'practiceStatistics:' in line:
                issues.append(f"Line {i}: PracticeGoalsDialog has practiceStatistics binding")
            if 'fileManager:' in line:
                issues.append(f"Line {i}: PracticeGoalsDialog has fileManager binding")
            if '}' in line:
                in_practice_goals = False
    
    # Find SetlistBuilderDialog
    in_setlist_builder = False
    for i, line in enumerate(lines, 1):
        if 'SetlistBuilderDialog {' in line:
            in_setlist_builder = True
        elif in_setlist_builder:
            if 'setlistManager:' in line:
                issues.append(f"Line {i}: SetlistBuilderDialog has setlistManager binding")
            if '}' in line:
                in_setlist_builder = False
    
    if issues:
        print(f"   ✗ Found binding issues:")
        for issue in issues:
            print(f"      {issue}")
        return False
    
    print(f"   ✓ No binding issues found in dialog instantiations")
    return True

def check_library_tab_qml():
    """Check LibraryTab.qml for binding loop issues."""
    print("\n2. Checking LibraryTab.qml...")
    file_path = Path("qml/tabs/LibraryTab.qml")
    
    if not file_path.exists():
        print(f"   ✗ File not found: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Check that FolderContextMenu property bindings have been removed
    issues = []
    
    in_folder_context_menu = False
    for i, line in enumerate(lines, 1):
        if 'FolderContextMenu {' in line:
            in_folder_context_menu = True
        elif in_folder_context_menu:
            if 'fingerprintEngine:' in line:
                issues.append(f"Line {i}: FolderContextMenu has fingerprintEngine binding")
            if 'waveformEngine:' in line:
                issues.append(f"Line {i}: FolderContextMenu has waveformEngine binding")
            if 'fileManager:' in line:
                issues.append(f"Line {i}: FolderContextMenu has fileManager binding")
            if '}' in line and 'MenuItem' not in line and 'Rectangle' not in line:
                in_folder_context_menu = False
    
    if issues:
        print(f"   ✗ Found binding issues:")
        for issue in issues:
            print(f"      {issue}")
        return False
    
    print(f"   ✓ No binding issues found in FolderContextMenu")
    return True

def check_practice_statistics_dialog():
    """Check PracticeStatisticsDialog.qml."""
    print("\n3. Checking PracticeStatisticsDialog.qml...")
    file_path = Path("qml/dialogs/PracticeStatisticsDialog.qml")
    
    if not file_path.exists():
        print(f"   ✗ File not found: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check that local property definitions have been removed
    issues = []
    
    if 'property var practiceStatistics:' in content:
        issues.append("Still has 'property var practiceStatistics' definition")
    if 'property var fileManager:' in content:
        issues.append("Still has 'property var fileManager' definition")
    
    # Check that context properties are used directly
    if 'practiceStatistics.' not in content:
        issues.append("Doesn't use practiceStatistics context property")
    if 'fileManager.' not in content:
        issues.append("Doesn't use fileManager context property")
    
    if issues:
        print(f"   ✗ Found issues:")
        for issue in issues:
            print(f"      {issue}")
        return False
    
    print(f"   ✓ Uses context properties correctly")
    return True

def check_practice_goals_dialog():
    """Check PracticeGoalsDialog.qml."""
    print("\n4. Checking PracticeGoalsDialog.qml...")
    file_path = Path("qml/dialogs/PracticeGoalsDialog.qml")
    
    if not file_path.exists():
        print(f"   ✗ File not found: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check that local property definitions have been removed
    issues = []
    
    if 'property var practiceGoals:' in content:
        issues.append("Still has 'property var practiceGoals' definition")
    if 'property var practiceStatistics:' in content:
        issues.append("Still has 'property var practiceStatistics' definition")
    if 'property var fileManager:' in content:
        issues.append("Still has 'property var fileManager' definition")
    
    # Check that context properties are used
    if 'practiceGoals.' not in content:
        issues.append("Doesn't use practiceGoals context property")
    
    if issues:
        print(f"   ✗ Found issues:")
        for issue in issues:
            print(f"      {issue}")
        return False
    
    print(f"   ✓ Uses context properties correctly")
    return True

def check_setlist_builder_dialog():
    """Check SetlistBuilderDialog.qml."""
    print("\n5. Checking SetlistBuilderDialog.qml...")
    file_path = Path("qml/dialogs/SetlistBuilderDialog.qml")
    
    if not file_path.exists():
        print(f"   ✗ File not found: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check that local property definitions have been removed
    issues = []
    
    if 'property var setlistManager:' in content:
        issues.append("Still has 'property var setlistManager' definition")
    
    # Check that context properties are used
    if 'setlistManager.' not in content:
        issues.append("Doesn't use setlistManager context property")
    
    if issues:
        print(f"   ✗ Found issues:")
        for issue in issues:
            print(f"      {issue}")
        return False
    
    print(f"   ✓ Uses context properties correctly")
    return True

def check_folder_context_menu():
    """Check FolderContextMenu.qml."""
    print("\n6. Checking FolderContextMenu.qml...")
    file_path = Path("qml/components/FolderContextMenu.qml")
    
    if not file_path.exists():
        print(f"   ✗ File not found: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check that local property definitions have been removed
    issues = []
    
    if 'property var fingerprintEngine:' in content:
        issues.append("Still has 'property var fingerprintEngine' definition")
    if 'property var waveformEngine:' in content:
        issues.append("Still has 'property var waveformEngine' definition")
    if 'property var fileManager:' in content:
        issues.append("Still has 'property var fileManager' definition")
    
    # Check that context properties are used
    if 'fingerprintEngine' not in content:
        issues.append("Doesn't reference fingerprintEngine context property")
    
    if issues:
        print(f"   ✗ Found issues:")
        for issue in issues:
            print(f"      {issue}")
        return False
    
    print(f"   ✓ Uses context properties correctly")
    return True

def main():
    print("=" * 60)
    print("QML Binding Loop Fix Validation")
    print("=" * 60)
    print("\nValidating fixes for QML binding loop errors:")
    
    all_passed = True
    
    # Run checks
    if not check_main_qml():
        all_passed = False
    
    if not check_library_tab_qml():
        all_passed = False
    
    if not check_practice_statistics_dialog():
        all_passed = False
    
    if not check_practice_goals_dialog():
        all_passed = False
    
    if not check_setlist_builder_dialog():
        all_passed = False
    
    if not check_folder_context_menu():
        all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All validation checks passed!")
        print("=" * 60)
        print("\nThe QML binding loops should now be fixed:")
        print("  ✓ Removed property bindings from main.qml")
        print("  ✓ Removed property bindings from LibraryTab.qml")
        print("  ✓ Removed local property definitions from dialogs")
        print("  ✓ Removed local property definitions from components")
        print("  ✓ Components now use context properties directly")
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
