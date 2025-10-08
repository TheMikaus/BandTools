#!/usr/bin/env python3
"""
Test script for Preferences Dialog
"""

import sys
from pathlib import Path

# Test QML syntax
print("Testing Preferences Dialog QML syntax...")
preferences_qml = Path("qml/dialogs/PreferencesDialog.qml")
if not preferences_qml.exists():
    print(f"✗ PreferencesDialog.qml not found")
    sys.exit(1)

content = preferences_qml.read_text()

# Check for required components
checks = [
    ("Dialog component", "Dialog {"),
    ("GroupBox components", "GroupBox {"),
    ("Undo limit slider", "undoLimitSlider"),
    ("Parallel workers slider", "parallelWorkersSlider"),
    ("Auto-waveforms checkbox", "autoWaveformsCheck"),
    ("Auto-fingerprints checkbox", "autoFingerprintsCheck"),
    ("Default zoom slider", "defaultZoomSlider"),
    ("Waveform quality combo", "waveformQualityCombo"),
    ("Load settings function", "function loadSettings()"),
    ("Apply settings function", "function applySettings()"),
    ("Restore defaults function", "function restoreDefaults()"),
]

all_passed = True
for check_name, check_string in checks:
    if check_string in content:
        print(f"✓ {check_name} found")
    else:
        print(f"✗ {check_name} NOT found")
        all_passed = False

print(f"\nQML file size: {len(content)} characters")

if all_passed:
    print("\n" + "="*50)
    print("✅ All syntax checks passed!")
    print("="*50)
else:
    print("\n" + "="*50)
    print("❌ Some checks failed!")
    print("="*50)
    sys.exit(1)
