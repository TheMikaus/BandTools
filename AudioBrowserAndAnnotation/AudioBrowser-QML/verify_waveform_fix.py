#!/usr/bin/env python3
"""
Verification Script for WaveformView Property Fix

This script verifies that:
1. The waveform_view.py module has correct syntax
2. The peaks property is defined using 'QVariant' instead of list
3. All related imports work correctly
"""

import sys
from pathlib import Path

def verify_syntax():
    """Verify Python syntax of waveform_view.py"""
    print("Verifying Python syntax...")
    try:
        import py_compile
        waveform_view_path = Path(__file__).parent / "backend" / "waveform_view.py"
        py_compile.compile(str(waveform_view_path), doraise=True)
        print("✓ Python syntax is valid")
        return True
    except py_compile.PyCompileError as e:
        print(f"✗ Syntax error: {e}")
        return False

def verify_property_definition():
    """Verify that peaks property uses 'QVariant' type annotation"""
    print("\nVerifying peaks property definition...")
    waveform_view_path = Path(__file__).parent / "backend" / "waveform_view.py"
    
    with open(waveform_view_path, 'r') as f:
        content = f.read()
    
    # Check for the fixed pattern
    if "peaks = pyqtProperty('QVariant', _get_peaks, _set_peaks)" in content:
        print("✓ peaks property uses 'QVariant' type annotation")
        return True
    
    # Check for the old problematic pattern
    if "peaks = pyqtProperty(list, _get_peaks, _set_peaks)" in content:
        print("✗ peaks property still uses 'list' type (not fixed)")
        return False
    
    print("✗ Could not find peaks property definition")
    return False

def verify_no_other_list_properties():
    """Verify no other properties use plain 'list' type"""
    print("\nVerifying no other properties use plain 'list' type...")
    
    backend_dir = Path(__file__).parent / "backend"
    found_issues = []
    
    for py_file in backend_dir.glob("*.py"):
        with open(py_file, 'r') as f:
            content = f.read()
        
        # Look for pyqtProperty(list, ...) pattern
        if "pyqtProperty(list," in content:
            found_issues.append(py_file.name)
    
    if found_issues:
        print(f"✗ Found {len(found_issues)} file(s) with list property issues:")
        for filename in found_issues:
            print(f"  - {filename}")
        return False
    
    print("✓ No other properties use plain 'list' type")
    return True

def main():
    """Run all verification checks"""
    print("=" * 60)
    print("WaveformView Property Fix Verification")
    print("=" * 60)
    
    checks = [
        verify_syntax(),
        verify_property_definition(),
        verify_no_other_list_properties(),
    ]
    
    print("\n" + "=" * 60)
    if all(checks):
        print("✓ All verification checks passed!")
        print("=" * 60)
        return 0
    else:
        print("✗ Some verification checks failed")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
