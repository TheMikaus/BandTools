#!/usr/bin/env python3
"""
Test script for Keyboard Shortcuts feature
"""

import sys
from pathlib import Path

# Test QML syntax
print("Testing Keyboard Shortcuts...")

# Check main.qml for shortcuts
main_qml = Path("qml/main.qml")
if not main_qml.exists():
    print(f"✗ main.qml not found")
    sys.exit(1)

main_content = main_qml.read_text()

# Check dialog exists
dialog_qml = Path("qml/dialogs/KeyboardShortcutsDialog.qml")
if not dialog_qml.exists():
    print(f"✗ KeyboardShortcutsDialog.qml not found")
    sys.exit(1)

dialog_content = dialog_qml.read_text()

# Check for shortcuts in main.qml
shortcuts_checks = [
    ("Space shortcut", 'sequence: "Space"'),
    ("Escape shortcut", 'sequence: "Escape"'),
    ("Theme toggle (Ctrl+T)", 'sequence: "Ctrl+T"'),
    ("Tab navigation (Ctrl+1-5)", 'sequence: "Ctrl+1"'),
    ("Annotation shortcut (Ctrl+A)", 'sequence: "Ctrl+A"'),
    ("Clip markers ([/])", 'sequence: "["'),
    ("Setlist Builder (Ctrl+Shift+T)", 'sequence: "Ctrl+Shift+T"'),
    ("Practice Stats (Ctrl+Shift+S)", 'sequence: "Ctrl+Shift+S"'),
    ("Practice Goals (Ctrl+Shift+G)", 'sequence: "Ctrl+Shift+G"'),
    ("Preferences (Ctrl+,)", 'sequence: "Ctrl+,"'),
    ("Help (Ctrl+/ or F1)", 'sequence: "Ctrl+/"'),
    ("Open Folder (Ctrl+O)", 'sequence: "Ctrl+O"'),
    ("Refresh (F5)", 'sequence: "F5"'),
    ("Quit (Ctrl+Q)", 'sequence: "Ctrl+Q"'),
    ("Fingerprints tab (Ctrl+5)", 'sequence: "Ctrl+5"'),
]

print("\nChecking main.qml shortcuts:")
all_passed = True
for check_name, check_string in shortcuts_checks:
    if check_string in main_content:
        print(f"✓ {check_name}")
    else:
        print(f"✗ {check_name} NOT found")
        all_passed = False

# Check dialog structure
dialog_checks = [
    ("Dialog component", "Dialog {"),
    ("Playback section", "Playback"),
    ("File Operations section", "File Operations"),
    ("Navigation section", "Navigation"),
    ("Annotations section", "Annotations & Clips"),
    ("Dialogs section", "Dialogs & Windows"),
    ("Appearance section", "Appearance"),
]

print("\nChecking KeyboardShortcutsDialog.qml structure:")
for check_name, check_string in dialog_checks:
    if check_string in dialog_content:
        print(f"✓ {check_name}")
    else:
        print(f"✗ {check_name} NOT found")
        all_passed = False

# Count shortcuts in main.qml
shortcut_count = main_content.count('Shortcut {')
print(f"\nTotal shortcuts in main.qml: {shortcut_count}")

# Expected shortcuts:
# Original: Space, Escape, Ctrl+T, Ctrl+1-4, +, -, Left, Right, Ctrl+A, [, ]
# Added: Ctrl+Shift+T, Ctrl+Shift+S, Ctrl+Shift+G, Ctrl+,, Ctrl+/, F1, Ctrl+O, F5, Ctrl+Q, Ctrl+5
# Total expected: ~21 shortcuts

if shortcut_count >= 21:
    print(f"✓ Expected at least 21 shortcuts, found {shortcut_count}")
else:
    print(f"✗ Expected at least 21 shortcuts, found only {shortcut_count}")
    all_passed = False

if all_passed:
    print("\n" + "="*50)
    print("✅ All tests passed!")
    print("="*50)
else:
    print("\n" + "="*50)
    print("❌ Some checks failed!")
    print("="*50)
    sys.exit(1)
