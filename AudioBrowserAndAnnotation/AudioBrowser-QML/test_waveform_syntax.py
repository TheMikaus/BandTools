#!/usr/bin/env python3
"""
Waveform Syntax Test Script

Tests that waveform modules have valid Python syntax.
This test doesn't require PyQt6 or GUI libraries.
"""

import sys
import ast
from pathlib import Path

def test_syntax(filepath):
    """Test Python syntax of a file."""
    try:
        with open(filepath, 'r') as f:
            code = f.read()
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {e}"

def main():
    """Run all syntax tests."""
    print("=" * 60)
    print("Waveform Backend Syntax Test Suite")
    print("=" * 60)
    
    # Files to test
    test_files = [
        "backend/waveform_engine.py",
        "backend/waveform_view.py",
        "main.py"
    ]
    
    results = []
    
    for filepath in test_files:
        print(f"\nTesting {filepath}...")
        path = Path(filepath)
        
        if not path.exists():
            print(f"✗ File not found: {filepath}")
            results.append((filepath, False, "File not found"))
            continue
        
        success, error = test_syntax(path)
        
        if success:
            print(f"✓ Syntax OK")
            results.append((filepath, True, None))
        else:
            print(f"✗ Syntax Error: {error}")
            results.append((filepath, False, error))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for filepath, success, error in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {filepath}")
        if error:
            print(f"       Error: {error}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All syntax tests passed!")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
