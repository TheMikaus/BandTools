#!/usr/bin/env python3
"""
Test to verify annotationManager null safety fixes in QML files.
This validates that all problematic lines identified in the error report have been fixed.
"""

import re
from pathlib import Path

def check_null_safety(file_path, line_numbers):
    """Check if specific lines have null safety checks."""
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    issues = []
    for line_num in line_numbers:
        if line_num > len(lines):
            issues.append(f"Line {line_num} doesn't exist")
            continue
        
        line = lines[line_num - 1]
        
        # Check if annotationManager is called without null check
        if 'annotationManager.' in line or 'annotationManager)' in line:
            # Look for null safety patterns
            has_ternary = '?' in line and ':' in line
            has_and_check = '&&' in line or 'annotationManager)' in line
            has_if_check = 'if (' in line or 'if(' in line
            
            # Check context (previous lines for if statements)
            context_start = max(0, line_num - 5)
            context_lines = ''.join(lines[context_start:line_num])
            has_if_in_context = 'if (' in context_lines or 'if(' in context_lines
            has_not_check = '!annotationManager' in context_lines or 'if (!annotationManager' in line
            
            if not (has_ternary or has_and_check or has_if_check or has_if_in_context or has_not_check):
                issues.append(f"Line {line_num}: Missing null check - {line.strip()}")
    
    return issues

def scan_for_unsafe_patterns(file_path):
    """Scan for any unsafe annotationManager usage patterns."""
    with open(file_path, 'r') as f:
        content = f.read()
        lines = content.split('\n')
    
    issues = []
    pattern = r'\bannotationManager\.(\w+)\('
    
    for i, line in enumerate(lines, 1):
        # Skip comments
        if '//' in line:
            line_before_comment = line[:line.index('//')]
        else:
            line_before_comment = line
        
        matches = re.finditer(pattern, line_before_comment)
        for match in matches:
            # Check for null safety in the line or context
            # Look back further to catch function-level guards
            context_start = max(0, i - 10)
            context_lines = '\n'.join(lines[context_start:i])
            
            # Look for safety patterns
            has_ternary = '?' in line_before_comment
            has_and_check = '&&' in line_before_comment or 'annotationManager)' in line_before_comment
            has_if_check = 'if (' in context_lines or 'if(' in context_lines
            has_not_check = '!annotationManager' in context_lines
            has_return_guard = 'if (!annotationManager) return' in context_lines or 'if (!annotationManager || ' in context_lines
            
            if not (has_ternary or has_and_check or has_if_check or has_not_check or has_return_guard):
                issues.append(f"Line {i}: Potential unsafe call - {line.strip()}")
    
    return issues

def main():
    """Run null safety validation."""
    base_path = Path(__file__).parent
    
    # Test cases from error report
    test_cases = {
        "qml/tabs/AnnotationsTab.qml": [
            81,   # getAnnotationCount
            114,  # getAnnotationCount  
            122,  # getAnnotationCount
            225,  # getAnnotationSets (in model)
            267,  # getAnnotationSets (in enabled)
            275,  # getAnnotationSets (in enabled)
            282,  # getShowAllSets (in checked)
            388,  # getAnnotationCount (in visible)
            598,  # getCurrentSetId
            661,  # getCurrentSetId
        ],
        "qml/components/WaveformDisplay.qml": [
            84,   # getAnnotations (in model)
        ],
    }
    
    all_passed = True
    
    print("Checking specific lines from error report...")
    for file_name, line_numbers in test_cases.items():
        file_path = base_path / file_name
        print(f"\n{file_name}:")
        
        if not file_path.exists():
            print(f"  ❌ File not found")
            all_passed = False
            continue
        
        issues = check_null_safety(file_path, line_numbers)
        if issues:
            print(f"  ❌ Found issues:")
            for issue in issues:
                print(f"    - {issue}")
            all_passed = False
        else:
            print(f"  ✓ All {len(line_numbers)} lines have null safety checks")
    
    print("\n" + "="*60)
    print("Scanning for any remaining unsafe patterns...")
    print("="*60)
    
    for file_name in test_cases.keys():
        file_path = base_path / file_name
        if not file_path.exists():
            continue
        
        print(f"\n{file_name}:")
        issues = scan_for_unsafe_patterns(file_path)
        if issues:
            print(f"  ⚠️  Found {len(issues)} potential issues:")
            for issue in issues[:10]:  # Show first 10
                print(f"    - {issue}")
            if len(issues) > 10:
                print(f"    ... and {len(issues) - 10} more")
            all_passed = False
        else:
            print(f"  ✓ No unsafe patterns detected")
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ All null safety checks are in place!")
        return 0
    else:
        print("❌ Some issues found - review needed")
        return 1

if __name__ == "__main__":
    exit(main())
