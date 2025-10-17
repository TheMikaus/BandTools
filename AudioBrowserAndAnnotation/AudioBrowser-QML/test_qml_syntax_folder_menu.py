#!/usr/bin/env python3
"""
Test script to verify QML syntax for folder context menu.

This doesn't actually run the GUI, just checks that QML files can be loaded.
"""

import sys
from pathlib import Path

# Ensure PyQt6 dependencies are available
def _ensure_import(mod_name: str, pip_name: str | None = None) -> bool:
    """Try to import a module, installing it if necessary."""
    if pip_name is None:
        pip_name = mod_name
    
    try:
        __import__(mod_name)
        return True
    except ImportError:
        print(f"Installing {pip_name}...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
        __import__(mod_name)
        return True

_ensure_import("PyQt6.QtCore", "PyQt6")
_ensure_import("PyQt6.QtQml", "PyQt6")

from PyQt6.QtCore import QUrl
from PyQt6.QtQml import QQmlComponent, QQmlEngine
from PyQt6.QtWidgets import QApplication


def test_qml_file(qml_path: Path) -> bool:
    """Test if a QML file can be loaded without syntax errors."""
    print(f"Testing {qml_path.name}...", end=" ")
    
    engine = QQmlEngine()
    component = QQmlComponent(engine, QUrl.fromLocalFile(str(qml_path)))
    
    if component.isError():
        print("✗ FAILED")
        for error in component.errors():
            print(f"  Error: {error.toString()}")
        return False
    else:
        print("✓ OK")
        return True


def main():
    """Run QML syntax tests."""
    app = QApplication(sys.argv)
    
    print("=" * 60)
    print("Testing QML Syntax for Folder Context Menu")
    print("=" * 60)
    print()
    
    base_dir = Path(__file__).parent / "qml"
    
    # Test the new FolderContextMenu component
    folder_menu = base_dir / "components" / "FolderContextMenu.qml"
    
    # Test the modified LibraryTab
    library_tab = base_dir / "tabs" / "LibraryTab.qml"
    
    all_ok = True
    
    if folder_menu.exists():
        all_ok = test_qml_file(folder_menu) and all_ok
    else:
        print(f"✗ {folder_menu.name} not found")
        all_ok = False
    
    if library_tab.exists():
        all_ok = test_qml_file(library_tab) and all_ok
    else:
        print(f"✗ {library_tab.name} not found")
        all_ok = False
    
    print()
    print("=" * 60)
    if all_ok:
        print("All QML syntax tests passed! ✓")
    else:
        print("Some QML syntax tests failed! ✗")
    print("=" * 60)
    
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
