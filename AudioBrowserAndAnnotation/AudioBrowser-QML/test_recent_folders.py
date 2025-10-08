#!/usr/bin/env python3
"""
Test script for Recent Folders feature
"""

import sys
from pathlib import Path

# Test imports
print("Testing imports...")
try:
    from PyQt6.QtCore import QSettings
    print("✓ PyQt6.QtCore imported successfully")
except ImportError as e:
    print(f"✗ Failed to import PyQt6.QtCore: {e}")
    sys.exit(1)

try:
    from backend.settings_manager import SettingsManager
    print("✓ SettingsManager imported successfully")
except ImportError as e:
    print(f"✗ Failed to import SettingsManager: {e}")
    sys.exit(1)

# Test SettingsManager recent folders functionality
print("\nTesting SettingsManager recent folders...")
settings = SettingsManager("BandTools", "AudioBrowser-QML-Test")

# Clear any existing recent folders
settings.clearRecentFolders()
recent = settings.getRecentFolders()
assert recent == [], f"Expected empty list after clear, got {recent}"
print("✓ clearRecentFolders() works")

# Add a folder
test_folder1 = "/home/test/music1"
settings.addRecentFolder(test_folder1, 10)
recent = settings.getRecentFolders()
assert recent == [test_folder1], f"Expected [{test_folder1}], got {recent}"
print("✓ addRecentFolder() works")

# Add another folder
test_folder2 = "/home/test/music2"
settings.addRecentFolder(test_folder2, 10)
recent = settings.getRecentFolders()
assert recent == [test_folder2, test_folder1], f"Expected [{test_folder2}, {test_folder1}], got {recent}"
print("✓ Multiple folders work (most recent first)")

# Add duplicate (should move to front)
settings.addRecentFolder(test_folder1, 10)
recent = settings.getRecentFolders()
assert recent == [test_folder1, test_folder2], f"Expected [{test_folder1}, {test_folder2}], got {recent}"
print("✓ Duplicate handling works (moved to front)")

# Test max limit
for i in range(3, 13):
    settings.addRecentFolder(f"/home/test/music{i}", 10)
recent = settings.getRecentFolders()
assert len(recent) == 10, f"Expected max 10 folders, got {len(recent)}"
print(f"✓ Max limit works (got {len(recent)} folders)")

# Clear for cleanup
settings.clearRecentFolders()
recent = settings.getRecentFolders()
assert recent == [], f"Expected empty list after final clear, got {recent}"
print("✓ Final cleanup successful")

print("\n" + "="*50)
print("✅ All tests passed!")
print("="*50)
