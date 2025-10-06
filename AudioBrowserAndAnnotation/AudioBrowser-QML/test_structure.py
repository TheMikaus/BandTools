#!/usr/bin/env python3
"""
Structure validation test for AudioBrowser QML

Tests that all files exist and are syntactically valid without requiring PyQt6.
"""

import ast
import sys
from pathlib import Path

def test_python_files():
    """Test that all Python files are syntactically valid."""
    print("Testing Python files...")
    
    python_files = [
        "main.py",
        "backend/__init__.py",
        "backend/settings_manager.py",
        "backend/color_manager.py",
        "backend/audio_engine.py",
        "backend/file_manager.py",
        "backend/models.py",
    ]
    
    for file_path in python_files:
        path = Path(file_path)
        if not path.exists():
            print(f"  ✗ {file_path} - MISSING")
            return False
        
        try:
            with open(path) as f:
                ast.parse(f.read())
            print(f"  ✓ {file_path}")
        except SyntaxError as e:
            print(f"  ✗ {file_path} - SYNTAX ERROR: {e}")
            return False
    
    return True

def test_qml_files():
    """Test that all QML files exist."""
    print("\nTesting QML files...")
    
    qml_files = [
        "qml/main.qml",
        "qml/styles/Theme.qml",
        "qml/components/StyledButton.qml",
        "qml/components/StyledLabel.qml",
        "qml/components/StyledTextField.qml",
        "qml/components/StyledSlider.qml",
        "qml/components/PlaybackControls.qml",
        "qml/tabs/LibraryTab.qml",
        "qml/tabs/AnnotationsTab.qml",
        "qml/tabs/ClipsTab.qml",
        "qml/dialogs/FolderDialog.qml",
    ]
    
    for file_path in qml_files:
        path = Path(file_path)
        if not path.exists():
            print(f"  ✗ {file_path} - MISSING")
            return False
        print(f"  ✓ {file_path}")
    
    return True

def test_documentation():
    """Test that documentation files exist."""
    print("\nTesting documentation files...")
    
    doc_files = [
        "README.md",
        "PHASE_1_SUMMARY.md",
        "DEVELOPER_GUIDE.md",
        "KEYBOARD_SHORTCUTS.md",
    ]
    
    for file_path in doc_files:
        path = Path(file_path)
        if not path.exists():
            print(f"  ✗ {file_path} - MISSING")
            return False
        print(f"  ✓ {file_path}")
    
    return True

def test_backend_structure():
    """Test backend module structure."""
    print("\nTesting backend module structure...")
    
    # Check that backend modules have expected classes/functions
    tests = [
        ("backend/settings_manager.py", "SettingsManager"),
        ("backend/color_manager.py", "ColorManager"),
        ("backend/audio_engine.py", "AudioEngine"),
        ("backend/file_manager.py", "FileManager"),
        ("backend/models.py", "FileListModel"),
        ("backend/models.py", "AnnotationsModel"),
    ]
    
    for file_path, expected_class in tests:
        with open(file_path) as f:
            content = f.read()
            if f"class {expected_class}" in content:
                print(f"  ✓ {file_path} contains {expected_class}")
            else:
                print(f"  ✗ {file_path} missing {expected_class}")
                return False
    
    return True

def main():
    """Run all tests."""
    print("=" * 60)
    print("AudioBrowser QML Structure Validation")
    print("=" * 60)
    print()
    
    all_passed = True
    
    if not test_python_files():
        all_passed = False
    
    if not test_qml_files():
        all_passed = False
    
    if not test_documentation():
        all_passed = False
    
    if not test_backend_structure():
        all_passed = False
    
    print()
    print("=" * 60)
    if all_passed:
        print("✓✓✓ All structure tests PASSED ✓✓✓")
        print("=" * 60)
        return 0
    else:
        print("✗✗✗ Some tests FAILED ✗✗✗")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
