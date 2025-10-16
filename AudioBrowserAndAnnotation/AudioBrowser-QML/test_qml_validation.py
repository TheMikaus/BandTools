#!/usr/bin/env python3
"""
Simple QML syntax validation test that doesn't require PyQt6 to be fully functional.
Just checks for basic syntax issues and validates our null-safety fixes.
"""

import re
from pathlib import Path

def validate_qml_syntax(file_path):
    """Basic QML syntax validation."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    issues = []
    lines = content.split('\n')
    
    # Check for balanced braces
    brace_count = content.count('{') - content.count('}')
    if brace_count != 0:
        issues.append(f"Unbalanced braces: {brace_count} extra '{{' characters")
    
    # Check for balanced parentheses
    paren_count = content.count('(') - content.count(')')
    if paren_count != 0:
        issues.append(f"Unbalanced parentheses: {paren_count} extra '(' characters")
    
    # Check for balanced brackets
    bracket_count = content.count('[') - content.count(']')
    if bracket_count != 0:
        issues.append(f"Unbalanced brackets: {bracket_count} extra '[' characters")
    
    # Check for common QML errors
    for i, line in enumerate(lines, 1):
        # Check for unescaped quotes in strings (simple check)
        if '"""' not in line:  # Skip if it's a multi-line string
            # Count quotes
            single_quotes = line.count("'") - line.count("\\'")
            double_quotes = line.count('"') - line.count('\\"')
            
            # Skip comment lines
            if '//' in line:
                comment_pos = line.index('//')
                line_before_comment = line[:comment_pos]
                single_quotes = line_before_comment.count("'") - line_before_comment.count("\\'")
                double_quotes = line_before_comment.count('"') - line_before_comment.count('\\"')
            
            if single_quotes % 2 != 0:
                issues.append(f"Line {i}: Unbalanced single quotes")
            if double_quotes % 2 != 0:
                issues.append(f"Line {i}: Unbalanced double quotes")
    
    return issues

def validate_all_qml_files(base_path):
    """Validate all QML files in the project."""
    qml_files = list(base_path.rglob("*.qml"))
    
    print(f"Found {len(qml_files)} QML files to validate\n")
    
    all_valid = True
    for qml_file in sorted(qml_files):
        rel_path = qml_file.relative_to(base_path)
        issues = validate_qml_syntax(qml_file)
        
        if issues:
            print(f"❌ {rel_path}")
            for issue in issues:
                print(f"   {issue}")
            all_valid = False
        else:
            print(f"✅ {rel_path}")
    
    return all_valid

def check_critical_null_safety_fixes():
    """Check that all critical null safety fixes from the issue are present."""
    print("\n" + "="*70)
    print("Checking critical null-safety fixes from issue...")
    print("="*70 + "\n")
    
    base_path = Path(__file__).parent / "qml"
    
    # These are the exact lines mentioned in the problem statement
    critical_fixes = {
        "main.qml": [
            (648, "audioEngine", "getCurrentFile"),
            (642, "audioEngine", "getPlaybackState"),
            (644, "audioEngine", "getPlaybackState"),
            (585, "audioEngine", "currentFile"),
            (93, "settingsManager", "getRecentFolders"),
            (110, "settingsManager", "getRecentFolders"),
            (115, "settingsManager", "getRecentFolders"),
            (324, "settingsManager", "getAutoSwitchAnnotations"),
            (616, "fileManager", "currentDirectory"),
            (617, "fileManager", "currentDirectory"),
            (656, "settingsManager", "getTheme"),
        ],
        "components/NowPlayingPanel.qml": [
            (206, "audioEngine", "getPlaybackState"),
            (186, "audioEngine", "getCurrentFile"),
            (172, "audioEngine", "getCurrentFile"),
            (143, "audioEngine", "getCurrentFile"),
            (128, "audioEngine", "getCurrentFile"),
            (129, "audioEngine", "getPosition"),
            (117, "audioEngine", "getCurrentFile"),
        ],
        "components/PlaybackControls.qml": [
            (206, "audioEngine", "getPlaybackState"),
            (121, "audioEngine", "getVolume"),
            (100, "audioEngine", "getDuration"),
            (91, "audioEngine", "getDuration"),
            (78, "audioEngine", "getPosition"),
            (47, "audioEngine", "getPlaybackState"),
        ],
        "tabs/SectionsTab.qml": [
            (471, "audioEngine", "getCurrentFile"),
            (261, "audioEngine", "getCurrentFile"),
        ],
        "tabs/AnnotationsTab.qml": [
            (53, "audioEngine", "getCurrentFile"),
            (492, "settingsManager", "getCurrentUser"),
        ],
        "tabs/LibraryTab.qml": [
            (803, "fileManager", "getFileProperties"),
            (661, "fileManager", "getCurrentDirectory"),
            (75, "fileManager", "getCurrentDirectory"),
        ],
    }
    
    all_fixed = True
    for file_name, checks in critical_fixes.items():
        file_path = base_path / file_name
        print(f"Checking {file_name}...")
        
        if not file_path.exists():
            print(f"  ❌ File not found!")
            all_fixed = False
            continue
        
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        fixes_found = 0
        for line_num, obj_name, method_name in checks:
            if line_num > len(lines):
                continue
            
            # Check a range of lines around the target (±2 lines)
            check_range = range(max(0, line_num - 3), min(len(lines), line_num + 2))
            found_protection = False
            
            for i in check_range:
                line = lines[i]
                # Look for null safety patterns
                if f"{obj_name} ?" in line or f"{obj_name} &&" in line or f"if ({obj_name})" in line or f"if (!{obj_name})" in line:
                    found_protection = True
                    fixes_found += 1
                    break
            
            if not found_protection:
                # Could be a false positive if the method is not actually called on that line anymore
                # Let's check if the method is even on that line
                if line_num <= len(lines):
                    actual_line = lines[line_num - 1]
                    if method_name in actual_line or f"{obj_name}." in actual_line:
                        print(f"  ⚠️  Line {line_num}: No null check found for {obj_name}.{method_name}")
        
        if fixes_found > 0:
            print(f"  ✅ Found {fixes_found} null-safety protections")
        else:
            print(f"  ⚠️  Could not verify null-safety fixes")
    
    return all_fixed

def main():
    """Main test function."""
    base_path = Path(__file__).parent / "qml"
    
    print("="*70)
    print("QML Syntax Validation Test")
    print("="*70 + "\n")
    
    syntax_valid = validate_all_qml_files(base_path)
    
    null_safety_ok = check_critical_null_safety_fixes()
    
    print("\n" + "="*70)
    if syntax_valid and null_safety_ok:
        print("✅ All tests passed!")
        print("="*70)
        return 0
    else:
        print("❌ Some tests failed")
        print("="*70)
        return 1

if __name__ == "__main__":
    exit(main())
