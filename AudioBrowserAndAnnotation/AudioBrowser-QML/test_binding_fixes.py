#!/usr/bin/env python3
"""
Test script to verify binding loop fixes and settings migration.
"""

import sys
from pathlib import Path


def test_main_qml_no_binding_loops():
    """Check that main.qml doesn't have binding loop issues."""
    print("Testing main.qml for binding loops...")
    
    qml_file = Path("qml/main.qml")
    if not qml_file.exists():
        print("  ✗ main.qml not found")
        return False
    
    with open(qml_file, 'r') as f:
        content = f.read()
    
    # Check that ClipsTab doesn't assign context properties
    if "ClipsTab {" in content:
        clips_section = content[content.find("ClipsTab {"):content.find("ClipsTab {") + 200]
        
        # Should NOT have clipManager: clipManager (causes binding loop)
        if "clipManager: clipManager" in clips_section:
            print("  ✗ ClipsTab still has binding loop (clipManager: clipManager)")
            return False
        
        if "audioEngine: audioEngine" in clips_section:
            print("  ✗ ClipsTab still has binding loop (audioEngine: audioEngine)")
            return False
        
        print("  ✓ ClipsTab has no binding loops")
    
    # Check that FolderNotesTab doesn't assign context properties
    if "FolderNotesTab {" in content:
        folder_section = content[content.find("FolderNotesTab {"):content.find("FolderNotesTab {") + 200]
        
        if "folderNotesManager: folderNotesManager" in folder_section:
            print("  ✗ FolderNotesTab still has binding loop (folderNotesManager: folderNotesManager)")
            return False
        
        print("  ✓ FolderNotesTab has no binding loops")
    
    return True


def test_theme_foreground_color_fixes():
    """Check that Theme.foregroundColor has been replaced with Theme.textColor."""
    print("\nTesting Theme.foregroundColor fixes...")
    
    files_to_check = [
        "qml/tabs/LibraryTab.qml",
        "qml/tabs/FolderNotesTab.qml"
    ]
    
    all_fixed = True
    for file_path in files_to_check:
        qml_file = Path(file_path)
        if not qml_file.exists():
            print(f"  ✗ {file_path} not found")
            all_fixed = False
            continue
        
        with open(qml_file, 'r') as f:
            content = f.read()
        
        if "Theme.foregroundColor" in content:
            print(f"  ✗ {file_path} still uses Theme.foregroundColor")
            all_fixed = False
        else:
            print(f"  ✓ {file_path} uses Theme.textColor")
    
    return all_fixed


def test_settings_migration():
    """Check that settings_manager has migration logic."""
    print("\nTesting legacy settings migration...")
    
    py_file = Path("backend/settings_manager.py")
    if not py_file.exists():
        print("  ✗ settings_manager.py not found")
        return False
    
    with open(py_file, 'r') as f:
        content = f.read()
    
    # Check for migration method
    if "_migrate_legacy_settings" not in content:
        print("  ✗ _migrate_legacy_settings method not found")
        return False
    
    print("  ✓ _migrate_legacy_settings method present")
    
    # Check for legacy settings reference
    if '"YourCompany"' not in content or '"Audio Folder Player"' not in content:
        print("  ✗ Legacy settings reference not found")
        return False
    
    print("  ✓ Legacy settings reference present")
    
    # Check that migration is called in __init__
    if "self._migrate_legacy_settings()" not in content:
        print("  ✗ Migration not called in __init__")
        return False
    
    print("  ✓ Migration called in __init__")
    
    return True


def test_startup_folder_prompt():
    """Check that LibraryTab prompts for folder on startup."""
    print("\nTesting startup folder prompt...")
    
    qml_file = Path("qml/tabs/LibraryTab.qml")
    if not qml_file.exists():
        print("  ✗ LibraryTab.qml not found")
        return False
    
    with open(qml_file, 'r') as f:
        content = f.read()
    
    # Check for Component.onCompleted
    if "Component.onCompleted" not in content:
        print("  ✗ Component.onCompleted not found")
        return False
    
    print("  ✓ Component.onCompleted present")
    
    # Check for directory check
    if "getCurrentDirectory()" not in content:
        print("  ✗ Directory check not found")
        return False
    
    print("  ✓ Directory check present")
    
    # Check for promptForDirectory call
    if "promptForDirectory()" not in content:
        print("  ✗ promptForDirectory call not found")
        return False
    
    print("  ✓ promptForDirectory call present")
    
    return True


def test_folder_dialog_configuration():
    """Check that FolderDialog is properly configured."""
    print("\nTesting FolderDialog configuration...")
    
    qml_file = Path("qml/dialogs/FolderDialog.qml")
    if not qml_file.exists():
        print("  ✗ FolderDialog.qml not found")
        return False
    
    with open(qml_file, 'r') as f:
        content = f.read()
    
    # Check that it doesn't use undefined OpenDirectory
    if "FileDialog.OpenDirectory" in content:
        print("  ✗ Still using FileDialog.OpenDirectory (undefined in Qt6)")
        return False
    
    print("  ✓ Not using FileDialog.OpenDirectory")
    
    # Check for file selection mode
    if "fileMode: FileDialog.OpenFile" in content:
        print("  ✓ Using FileDialog.OpenFile mode")
    else:
        print("  ✗ FileDialog.OpenFile mode not found")
        return False
    
    # Check for folder extraction logic
    if "lastIndexOf('/')" in content or "lastIndexOf('\\\\')" in content:
        print("  ✓ Folder extraction logic present")
    else:
        print("  ✗ Folder extraction logic not found")
        return False
    
    return True


def test_file_context_menu():
    """Check that FileContextMenu doesn't have binding loops."""
    print("\nTesting FileContextMenu configuration...")
    
    qml_file = Path("qml/tabs/LibraryTab.qml")
    if not qml_file.exists():
        print("  ✗ LibraryTab.qml not found")
        return False
    
    with open(qml_file, 'r') as f:
        content = f.read()
    
    # Find FileContextMenu section
    if "FileContextMenu {" not in content:
        print("  ✗ FileContextMenu not found")
        return False
    
    menu_section = content[content.find("FileContextMenu {"):content.find("FileContextMenu {") + 300]
    
    # Should NOT have property assignments that cause binding loops
    if "audioEngine: audioEngine" in menu_section:
        print("  ✗ FileContextMenu still has binding loop (audioEngine: audioEngine)")
        return False
    
    if "annotationManager: annotationManager" in menu_section:
        print("  ✗ FileContextMenu still has binding loop (annotationManager: annotationManager)")
        return False
    
    print("  ✓ FileContextMenu has no binding loops")
    
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Binding Loop Fixes and Settings Migration Tests")
    print("=" * 60)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    import os
    os.chdir(script_dir)
    
    tests = [
        test_main_qml_no_binding_loops,
        test_theme_foreground_color_fixes,
        test_settings_migration,
        test_startup_folder_prompt,
        test_folder_dialog_configuration,
        test_file_context_menu,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ✗ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    if all(results):
        print(f"✓✓✓ All {total} tests PASSED ✓✓✓")
        return 0
    else:
        print(f"✗ {total - passed} out of {total} tests FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
