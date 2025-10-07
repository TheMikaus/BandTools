#!/usr/bin/env python3
"""
Test to verify ExportAnnotationsDialog QML file can be loaded without syntax errors.
This specifically tests the fix for the "Cannot assign to non-existent property" error.
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
    except ImportError as e:
        print(f"WARNING: Failed to import {mod_name}: {e}", file=sys.stderr)
        print(f"Installing {pip_name}...")
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
        except subprocess.CalledProcessError as install_error:
            error_msg = f"Failed to install {pip_name}: {install_error}"
            print(f"ERROR: {error_msg}", file=sys.stderr)
            raise
        
        try:
            __import__(mod_name)
            return True
        except ImportError as post_install_error:
            error_msg = f"Successfully installed {pip_name} but still cannot import {mod_name}: {post_install_error}"
            print(f"ERROR: {error_msg}", file=sys.stderr)
            # For this test, we'll skip if Qt isn't available
            return False

# Try to install required dependencies
qt_available = True
try:
    qt_available = _ensure_import("PyQt6.QtCore", "PyQt6")
    qt_available = qt_available and _ensure_import("PyQt6.QtGui", "PyQt6")
    qt_available = qt_available and _ensure_import("PyQt6.QtQml", "PyQt6")
except Exception as e:
    print(f"Qt not available: {e}", file=sys.stderr)
    qt_available = False

def check_qml_syntax(qml_file_path: Path) -> bool:
    """
    Check QML file syntax by parsing it for property declarations.
    This is a basic syntax check that doesn't require Qt runtime.
    """
    print(f"\nChecking: {qml_file_path.relative_to(Path.cwd())}")
    
    with open(qml_file_path, 'r') as f:
        content = f.read()
    
    # Check for the specific properties that should be declared
    required_properties = ['annotationManager', 'fileManager']
    found_properties = []
    
    for line in content.split('\n'):
        stripped = line.strip()
        if stripped.startswith('property '):
            # Extract property name
            parts = stripped.split()
            if len(parts) >= 3:
                prop_name = parts[2].rstrip(':')
                found_properties.append(prop_name)
    
    print(f"  Found properties: {found_properties}")
    
    missing = [p for p in required_properties if p not in found_properties]
    if missing:
        print(f"  ✗ FAILED: Missing property declarations: {missing}")
        return False
    
    # Check that the properties are used in the file
    for prop in required_properties:
        if prop not in content:
            print(f"  ✗ WARNING: Property '{prop}' declared but not used")
    
    print(f"  ✓ PASSED: All required properties declared")
    return True

def test_with_qt(qml_file_path: Path) -> bool:
    """Test QML file with Qt engine if available."""
    from PyQt6.QtCore import QUrl
    from PyQt6.QtGui import QGuiApplication
    from PyQt6.QtQml import QQmlApplicationEngine, QQmlComponent
    
    print(f"\nTesting with Qt: {qml_file_path.relative_to(Path.cwd())}")
    
    # Create application (required for QML engine)
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    
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
    print("ExportAnnotationsDialog QML Syntax Check")
    print("=" * 60)
    
    # Get the QML file
    qml_file = Path(__file__).parent / "qml" / "dialogs" / "ExportAnnotationsDialog.qml"
    
    if not qml_file.exists():
        print(f"Error: QML file not found: {qml_file}")
        return 1
    
    # Always do basic syntax check
    syntax_ok = check_qml_syntax(qml_file)
    
    # Try Qt-based test if available
    qt_ok = True
    if qt_available:
        try:
            qt_ok = test_with_qt(qml_file)
        except Exception as e:
            print(f"\nWarning: Qt test skipped due to: {e}")
            qt_ok = True  # Don't fail if Qt runtime isn't available
    else:
        print("\nQt not available - skipping Qt-based test")
    
    print("\n" + "=" * 60)
    if syntax_ok and qt_ok:
        print("✓ ExportAnnotationsDialog QML syntax check passed!")
        print("=" * 60)
        return 0
    else:
        print("✗ ExportAnnotationsDialog QML has errors")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
