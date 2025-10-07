#!/usr/bin/env python3
"""
Test script to verify folder dialog and file manager changes.
"""

import sys
from pathlib import Path

def test_folder_dialog_qml():
    """Check FolderDialog.qml for correct configuration."""
    print("Testing FolderDialog.qml configuration...")
    
    qml_file = Path("qml/dialogs/FolderDialog.qml")
    if not qml_file.exists():
        print("  ✗ FolderDialog.qml not found")
        return False
    
    with open(qml_file, 'r') as f:
        content = f.read()
    
    # Check for OpenDirectory mode
    if "FileDialog.OpenDirectory" in content:
        print("  ✓ Using FileDialog.OpenDirectory mode")
    else:
        print("  ✗ Not using FileDialog.OpenDirectory mode")
        return False
    
    # Check for Windows path handling
    if "charAt(2) === ':'" in content:
        print("  ✓ Windows path handling present")
    else:
        print("  ✗ Windows path handling missing")
        return False
    
    # Check for folderSelected signal
    if "signal folderSelected" in content:
        print("  ✓ folderSelected signal defined")
    else:
        print("  ✗ folderSelected signal missing")
        return False
    
    return True


def test_library_tab_qml():
    """Check LibraryTab.qml for correct usage of FolderDialog."""
    print("\nTesting LibraryTab.qml configuration...")
    
    qml_file = Path("qml/tabs/LibraryTab.qml")
    if not qml_file.exists():
        print("  ✗ LibraryTab.qml not found")
        return False
    
    with open(qml_file, 'r') as f:
        content = f.read()
    
    # Check for FolderDialog usage
    if "FolderDialog {" in content:
        print("  ✓ Using FolderDialog component")
    else:
        print("  ✗ Not using FolderDialog component")
        return False
    
    # Check for onFolderSelected handler
    if "onFolderSelected:" in content:
        print("  ✓ onFolderSelected handler present")
    else:
        print("  ✗ onFolderSelected handler missing")
        return False
    
    # Check for noDirectoryDialog
    if "noDirectoryDialog" in content:
        print("  ✓ No directory prompt dialog present")
    else:
        print("  ✗ No directory prompt dialog missing")
        return False
    
    # Check for promptForDirectory function
    if "function promptForDirectory()" in content:
        print("  ✓ promptForDirectory function defined")
    else:
        print("  ✗ promptForDirectory function missing")
        return False
    
    return True


def test_file_manager_py():
    """Check file_manager.py for metadata loading methods."""
    print("\nTesting file_manager.py metadata methods...")
    
    py_file = Path("backend/file_manager.py")
    if not py_file.exists():
        print("  ✗ file_manager.py not found")
        return False
    
    with open(py_file, 'r') as f:
        content = f.read()
    
    # Check for metadata loading methods
    if "_load_provided_names" in content:
        print("  ✓ _load_provided_names method present")
    else:
        print("  ✗ _load_provided_names method missing")
        return False
    
    if "_load_duration_cache" in content:
        print("  ✓ _load_duration_cache method present")
    else:
        print("  ✗ _load_duration_cache method missing")
        return False
    
    if "getProvidedName" in content:
        print("  ✓ getProvidedName method present")
    else:
        print("  ✗ getProvidedName method missing")
        return False
    
    if "getCachedDuration" in content:
        print("  ✓ getCachedDuration method present")
    else:
        print("  ✗ getCachedDuration method missing")
        return False
    
    # Check for .provided_names.json reference
    if ".provided_names.json" in content:
        print("  ✓ .provided_names.json file reference present")
    else:
        print("  ✗ .provided_names.json file reference missing")
        return False
    
    # Check for .duration_cache.json reference
    if ".duration_cache.json" in content:
        print("  ✓ .duration_cache.json file reference present")
    else:
        print("  ✗ .duration_cache.json file reference missing")
        return False
    
    return True


def test_main_py():
    """Check main.py for directory initialization."""
    print("\nTesting main.py initialization...")
    
    py_file = Path("main.py")
    if not py_file.exists():
        print("  ✗ main.py not found")
        return False
    
    with open(py_file, 'r') as f:
        content = f.read()
    
    # Check for getRootDir call
    if "getRootDir()" in content:
        print("  ✓ getRootDir() call present")
    else:
        print("  ✗ getRootDir() call missing")
        return False
    
    # Check for setCurrentDirectory on startup
    if "setCurrentDirectory(saved_root)" in content or "setCurrentDirectory(root" in content:
        print("  ✓ setCurrentDirectory on startup present")
    else:
        print("  ✗ setCurrentDirectory on startup missing")
        return False
    
    # Check for setRootDir connection
    if "setRootDir" in content:
        print("  ✓ setRootDir connection present")
    else:
        print("  ✗ setRootDir connection missing")
        return False
    
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Folder Dialog and Metadata Loading Test Suite")
    print("=" * 60)
    
    folder_dialog_ok = test_folder_dialog_qml()
    library_tab_ok = test_library_tab_qml()
    file_manager_ok = test_file_manager_py()
    main_py_ok = test_main_py()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    print(f"FolderDialog.qml: {'✓ PASS' if folder_dialog_ok else '✗ FAIL'}")
    print(f"LibraryTab.qml: {'✓ PASS' if library_tab_ok else '✗ FAIL'}")
    print(f"file_manager.py: {'✓ PASS' if file_manager_ok else '✗ FAIL'}")
    print(f"main.py: {'✓ PASS' if main_py_ok else '✗ FAIL'}")
    
    if folder_dialog_ok and library_tab_ok and file_manager_ok and main_py_ok:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
