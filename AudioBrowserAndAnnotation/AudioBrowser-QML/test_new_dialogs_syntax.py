#!/usr/bin/env python3
"""
Test New Dialogs Syntax

Tests the syntax and structure of newly added dialogs:
- BatchRenameConfirmDialog
- FingerprintProgressDialog
"""

import sys
import subprocess
from pathlib import Path

def test_qml_syntax(qml_file: Path) -> tuple[bool, str]:
    """
    Test QML file syntax using qmllint.
    
    Returns:
        tuple[bool, str]: (success, error_message)
    """
    try:
        result = subprocess.run(
            ["qmllint", str(qml_file)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return True, ""
        else:
            return False, result.stdout + result.stderr
    
    except FileNotFoundError:
        # qmllint not available, skip test
        print(f"WARNING: qmllint not found, skipping syntax check for {qml_file.name}")
        return True, "qmllint not available"
    
    except subprocess.TimeoutExpired:
        return False, "qmllint timed out"
    
    except Exception as e:
        return False, f"Error running qmllint: {e}"


def test_file_structure(qml_file: Path) -> tuple[bool, str]:
    """
    Test that QML file has basic structure.
    
    Returns:
        tuple[bool, str]: (success, error_message)
    """
    try:
        content = qml_file.read_text()
        
        # Check for basic QML structure
        checks = [
            ("import QtQuick", "Missing QtQuick import"),
            ("Dialog {", "Missing Dialog root element"),
            ("}", "Missing closing brace"),
        ]
        
        for check, error in checks:
            if check not in content:
                return False, error
        
        return True, ""
    
    except Exception as e:
        return False, f"Error reading file: {e}"


def main():
    """Run all tests."""
    print("Testing New Dialogs Syntax")
    print("=" * 60)
    
    script_dir = Path(__file__).parent
    dialogs_dir = script_dir / "qml" / "dialogs"
    
    # Files to test
    test_files = [
        "BatchRenameConfirmDialog.qml",
        "FingerprintProgressDialog.qml"
    ]
    
    all_passed = True
    
    for filename in test_files:
        filepath = dialogs_dir / filename
        
        print(f"\nTesting {filename}...")
        
        # Check file exists
        if not filepath.exists():
            print(f"  ✗ File not found: {filepath}")
            all_passed = False
            continue
        
        # Test file structure
        success, error = test_file_structure(filepath)
        if success:
            print(f"  ✓ File structure OK")
        else:
            print(f"  ✗ File structure error: {error}")
            all_passed = False
        
        # Test QML syntax
        success, error = test_qml_syntax(filepath)
        if success:
            if error:
                print(f"  ⚠ Syntax check skipped: {error}")
            else:
                print(f"  ✓ QML syntax OK")
        else:
            print(f"  ✗ QML syntax error: {error}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests passed")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
