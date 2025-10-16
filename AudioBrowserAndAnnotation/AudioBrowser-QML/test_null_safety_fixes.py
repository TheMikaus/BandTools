#!/usr/bin/env python3
"""
Test script to validate null-safety fixes in QML files.
This script checks that all known problematic lines have been fixed with null checks.
"""

import re
from pathlib import Path

def check_null_safety_patterns(file_path, patterns):
    """Check if file contains proper null safety patterns."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    issues = []
    for line_num, pattern_type, pattern in patterns:
        # Check if the line still has unsafe pattern
        lines = content.split('\n')
        if line_num <= len(lines):
            line = lines[line_num - 1]
            if pattern_type == "unsafe" and pattern in line:
                issues.append(f"Line {line_num}: Still contains unsafe pattern '{pattern}'")
            elif pattern_type == "safe" and pattern not in content:
                issues.append(f"Missing safe pattern '{pattern}' around line {line_num}")
    
    return issues

def main():
    """Run null-safety validation tests."""
    base_path = Path(__file__).parent / "qml"
    
    test_cases = {
        "main.qml": [
            # Check that audioEngine calls have null checks
            (642, "safe", "audioEngine && audioEngine.getPlaybackState()"),
            (648, "safe", "audioEngine && audioEngine.getCurrentFile()"),
            # Check settingsManager calls have null checks
            (93, "safe", "settingsManager ? settingsManager.getRecentFolders()"),
            (324, "safe", "settingsManager ? settingsManager.getAutoSwitchAnnotations()"),
        ],
        "components/NowPlayingPanel.qml": [
            (115, "safe", "audioEngine && audioEngine.getCurrentFile()"),
            (128, "safe", "audioEngine ? audioEngine.getCurrentFile()"),
            (206, "safe", "audioEngine && audioEngine.getPlaybackState()"),
        ],
        "components/PlaybackControls.qml": [
            (47, "safe", "audioEngine && audioEngine.getPlaybackState()"),
            (78, "safe", "audioEngine ? audioEngine.getPosition()"),
            (121, "safe", "audioEngine ? audioEngine.getVolume()"),
        ],
        "tabs/SectionsTab.qml": [
            (261, "safe", "audioEngine && audioEngine.getCurrentFile()"),
        ],
        "tabs/AnnotationsTab.qml": [
            (53, "safe", "audioEngine && audioEngine.getCurrentFile()"),
        ],
        "tabs/LibraryTab.qml": [
            (75, "safe", "fileManager ? fileManager.getCurrentDirectory()"),
        ],
    }
    
    all_passed = True
    for file_name, patterns in test_cases.items():
        file_path = base_path / file_name
        print(f"Checking {file_name}...")
        
        if not file_path.exists():
            print(f"  ❌ File not found: {file_path}")
            all_passed = False
            continue
        
        issues = check_null_safety_patterns(file_path, patterns)
        if issues:
            print(f"  ❌ Found issues:")
            for issue in issues:
                print(f"    - {issue}")
            all_passed = False
        else:
            print(f"  ✓ All null-safety checks present")
    
    # Additional pattern check: look for any remaining unsafe patterns
    print("\nScanning for remaining unsafe patterns...")
    unsafe_patterns = [
        (r'\baudioEngine\.get\w+\(\)', 'audioEngine method call without null check'),
        (r'\bsettingsManager\.get\w+\(\)', 'settingsManager method call without null check'),
        (r'\bfileManager\.get\w+\(\)', 'fileManager method call without null check'),
    ]
    
    files_to_check = [
        "main.qml",
        "components/NowPlayingPanel.qml",
        "components/PlaybackControls.qml",
        "tabs/SectionsTab.qml",
        "tabs/AnnotationsTab.qml",
        "tabs/LibraryTab.qml",
    ]
    
    for file_name in files_to_check:
        file_path = base_path / file_name
        if not file_path.exists():
            continue
            
        with open(file_path, 'r') as f:
            content = f.read()
            lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip comments
            if '//' in line:
                line = line[:line.index('//')]
            if '/*' in line or '*/' in line:
                continue
                
            for pattern, description in unsafe_patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    # Check if there's a null check nearby (within 20 chars before)
                    start_pos = max(0, match.start() - 50)
                    context = line[start_pos:match.start()]
                    
                    # Look for ternary operator or && check
                    if '?' in context or '&&' in context or 'if (' in context:
                        continue  # Likely has null check
                    
                    # Check if it's in a function definition (not a call site)
                    if 'function' in context:
                        continue
                    
                    print(f"  ⚠️  {file_name}:{line_num} - Potential unsafe {description}")
                    print(f"      {line.strip()}")
    
    if all_passed:
        print("\n✅ All null-safety tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed")
        return 1

if __name__ == "__main__":
    exit(main())
