#!/usr/bin/env python3
"""
Test to verify QML files can be loaded without syntax errors.
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

# Install required dependencies
_ensure_import("PyQt6.QtCore", "PyQt6")
_ensure_import("PyQt6.QtGui", "PyQt6")
_ensure_import("PyQt6.QtQml", "PyQt6")

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtQml import QQmlApplicationEngine, QQmlComponent

def test_qml_file(qml_file_path: Path, engine: QQmlApplicationEngine) -> bool:
    """Test if a QML file can be loaded without errors."""
    print(f"\nTesting: {qml_file_path.relative_to(Path.cwd())}")
    
    # Create a component from the QML file
    url = QUrl.fromLocalFile(str(qml_file_path.absolute()))
    component = QQmlComponent(engine, url)
    
    # Check for errors
    if component.isError():
        print(f"  ✗ FAILED with errors:")
        for error in component.errors():
            print(f"    - Line {error.line()}: {error.description()}")
        return False
    
    print(f"  ✓ PASSED")
    return True

def main():
    print("=" * 60)
    print("QML Syntax Testing")
    print("=" * 60)
    
    # Create application (required for QML engine)
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    
    # Get the qml directory
    qml_dir = Path(__file__).parent / "qml"
    
    if not qml_dir.exists():
        print(f"Error: QML directory not found: {qml_dir}")
        return 1
    
    # Test specific files that were mentioned in the errors
    test_files = [
        qml_dir / "dialogs" / "ProgressDialog.qml",
        qml_dir / "tabs" / "LibraryTab.qml",
        qml_dir / "components" / "StyledButton.qml",
    ]
    
    all_passed = True
    for qml_file in test_files:
        if qml_file.exists():
            if not test_qml_file(qml_file, engine):
                all_passed = False
        else:
            print(f"\nWarning: File not found: {qml_file}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All QML files passed syntax check!")
        print("=" * 60)
        return 0
    else:
        print("✗ Some QML files have errors")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
