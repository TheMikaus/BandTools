#!/usr/bin/env python3
"""
Test to verify all QML binding loop fixes and signal handler corrections.
"""

import re
from pathlib import Path


def test_binding_loops_fixed():
    """Verify that all dialogs with binding loop issues are fixed."""
    main_qml = Path(__file__).parent / "qml" / "main.qml"
    
    with open(main_qml, 'r') as f:
        content = f.read()
    
    # List of dialogs and their forbidden property assignments
    # These assignments cause binding loops because the properties
    # have the same name as context properties
    checks = [
        ("DocumentationBrowserDialog", "documentationManager"),
        ("AutoGenerationSettingsDialog", "settingsManager"),
        ("BackupSelectionDialog", "backupManager"),
    ]
    
    all_passed = True
    
    for dialog_name, forbidden_prop in checks:
        # Find the dialog declaration
        pattern = f"{dialog_name}\\s*{{[^}}]*?id:\\s*\\w+[^}}]*?}}"
        matches = re.findall(pattern, content, re.DOTALL)
        
        if not matches:
            print(f"✗ Could not find {dialog_name} in main.qml")
            all_passed = False
            continue
        
        dialog_section = matches[0]
        
        # Check for forbidden property assignment (e.g., "backupManager: backupManager")
        if re.search(f"\\b{forbidden_prop}:\\s*{forbidden_prop}\\b", dialog_section):
            print(f"✗ {dialog_name} still has binding loop: {forbidden_prop}: {forbidden_prop}")
            all_passed = False
        else:
            print(f"✓ {dialog_name} has no binding loop for {forbidden_prop}")
    
    return all_passed


def test_shortcut_fixes():
    """Verify that StandardKey shortcuts use 'sequences' instead of 'sequence'."""
    main_qml = Path(__file__).parent / "qml" / "main.qml"
    
    with open(main_qml, 'r') as f:
        content = f.read()
    
    # Check for old pattern: sequence: StandardKey.X
    old_pattern = re.findall(r'sequence:\s*StandardKey\.\w+', content)
    
    if old_pattern:
        print(f"✗ Found {len(old_pattern)} shortcuts using 'sequence:' instead of 'sequences:'")
        for match in old_pattern:
            print(f"  - {match}")
        return False
    else:
        print("✓ All StandardKey shortcuts use 'sequences:' syntax")
        
        # Verify new pattern exists
        new_pattern = re.findall(r'sequences:\s*\[StandardKey\.\w+\]', content)
        if new_pattern:
            print(f"  Found {len(new_pattern)} correctly formatted shortcuts")
        
        return True


def test_waveform_widget_fixes():
    """Verify MiniWaveformWidget uses correct signal handlers and methods."""
    widget_qml = Path(__file__).parent / "qml" / "components" / "MiniWaveformWidget.qml"
    
    with open(widget_qml, 'r') as f:
        content = f.read()
    
    all_passed = True
    
    # Check that incorrect method names are not used
    if "loadWaveform" in content:
        print("✗ MiniWaveformWidget still uses 'loadWaveform' (should be 'generateWaveform')")
        all_passed = False
    else:
        print("✓ MiniWaveformWidget doesn't use incorrect 'loadWaveform' method")
    
    if "clearWaveform()" in content and "waveformEngine.clearWaveform" in content:
        print("✗ MiniWaveformWidget still calls 'waveformEngine.clearWaveform()' (method doesn't exist)")
        all_passed = False
    else:
        print("✓ MiniWaveformWidget doesn't call non-existent 'waveformEngine.clearWaveform()'")
    
    # Check that non-existent signal handler is removed
    if "onWaveformCleared" in content:
        print("✗ MiniWaveformWidget still has 'onWaveformCleared' handler (signal doesn't exist)")
        all_passed = False
    else:
        print("✓ MiniWaveformWidget doesn't use non-existent 'onWaveformCleared' signal")
    
    # Check that correct method is used
    if "generateWaveform" in content:
        print("✓ MiniWaveformWidget uses correct 'generateWaveform' method")
    else:
        print("✗ MiniWaveformWidget doesn't use 'generateWaveform' method")
        all_passed = False
    
    # Check that waveformReady handler has correct signature
    if re.search(r'function onWaveformReady\s*\(\s*path\s*\)', content):
        print("✓ MiniWaveformWidget uses correct 'onWaveformReady(path)' signature")
    else:
        print("✗ MiniWaveformWidget doesn't have correct 'onWaveformReady(path)' signature")
        all_passed = False
    
    return all_passed


def main():
    print("=" * 70)
    print("QML Binding Loop and Signal Handler Fixes Validation")
    print("=" * 70)
    print()
    
    print("1. Testing Binding Loop Fixes...")
    print("-" * 70)
    binding_loops_ok = test_binding_loops_fixed()
    print()
    
    print("2. Testing Shortcut Fixes...")
    print("-" * 70)
    shortcuts_ok = test_shortcut_fixes()
    print()
    
    print("3. Testing Waveform Widget Fixes...")
    print("-" * 70)
    waveform_ok = test_waveform_widget_fixes()
    print()
    
    print("=" * 70)
    if binding_loops_ok and shortcuts_ok and waveform_ok:
        print("✓ All tests passed!")
        print("=" * 70)
        return 0
    else:
        print("✗ Some tests failed")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
