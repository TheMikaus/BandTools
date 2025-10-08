#!/usr/bin/env python3
"""
Test script for Workspace Layouts feature
"""

import sys
from pathlib import Path

# Test QML syntax
print("Testing Workspace Layouts...")

# Check main.qml for layout functions
main_qml = Path("qml/main.qml")
if not main_qml.exists():
    print(f"✗ main.qml not found")
    sys.exit(1)

main_content = main_qml.read_text()

# Check for layout functions
layout_checks = [
    ("saveWindowGeometry function", "function saveWindowGeometry()"),
    ("restoreWindowGeometry function", "function restoreWindowGeometry()"),
    ("resetToDefaultLayout function", "function resetToDefaultLayout()"),
    ("Component.onCompleted handler", "Component.onCompleted"),
    ("onClosing handler", "onClosing"),
    ("Save layout shortcut", 'sequence: "Ctrl+Shift+L"'),
    ("Reset layout shortcut", 'sequence: "Ctrl+Shift+R"'),
    ("View menu", 'title: "&View"'),
    ("Save Layout menu item", 'text: "Save Layout"'),
    ("Reset Layout menu item", 'text: "Reset Layout to Default"'),
]

print("\nChecking main.qml layout features:")
all_passed = True
for check_name, check_string in layout_checks:
    if check_string in main_content:
        print(f"✓ {check_name}")
    else:
        print(f"✗ {check_name} NOT found")
        all_passed = False

# Check keyboard shortcuts dialog
shortcuts_qml = Path("qml/dialogs/KeyboardShortcutsDialog.qml")
if shortcuts_qml.exists():
    shortcuts_content = shortcuts_qml.read_text()
    if "Workspace Layout" in shortcuts_content:
        print("✓ Workspace Layout section in Keyboard Shortcuts dialog")
    else:
        print("✗ Workspace Layout section NOT in Keyboard Shortcuts dialog")
        all_passed = False
else:
    print("✗ KeyboardShortcutsDialog.qml not found")
    all_passed = False

# Check SettingsManager for geometry methods
settings_py = Path("backend/settings_manager.py")
if settings_py.exists():
    settings_content = settings_py.read_text()
    if "def getGeometry" in settings_content and "def setGeometry" in settings_content:
        print("✓ SettingsManager has geometry methods")
    else:
        print("✗ SettingsManager missing geometry methods")
        all_passed = False
else:
    print("✗ settings_manager.py not found")
    all_passed = False

if all_passed:
    print("\n" + "="*50)
    print("✅ All tests passed!")
    print("="*50)
    print("\nWorkspace Layout Features:")
    print("- Save window geometry on close")
    print("- Restore window geometry on startup")
    print("- Manual save via View menu or Ctrl+Shift+L")
    print("- Reset to defaults via View menu or Ctrl+Shift+R")
    print("- Integration with SettingsManager")
else:
    print("\n" + "="*50)
    print("❌ Some checks failed!")
    print("="*50)
    sys.exit(1)
