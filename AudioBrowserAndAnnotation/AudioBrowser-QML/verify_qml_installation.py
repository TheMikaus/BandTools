#!/usr/bin/env python3
"""
Comprehensive QML Installation Verification Script

This script checks that all QML fixes are properly applied and the environment
is correctly set up to run AudioBrowser-QML.
"""

import sys
from pathlib import Path
import subprocess

# Color codes for terminal output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    """Print a section header."""
    print(f"\n{BOLD}{'=' * 70}{RESET}")
    print(f"{BOLD}{text:^70}{RESET}")
    print(f"{BOLD}{'=' * 70}{RESET}\n")

def print_success(text):
    """Print a success message."""
    print(f"{GREEN}✓{RESET} {text}")

def print_warning(text):
    """Print a warning message."""
    print(f"{YELLOW}⚠{RESET} {text}")

def print_error(text):
    """Print an error message."""
    print(f"{RED}✗{RESET} {text}")

def check_file_exists(filepath, description):
    """Check if a file exists."""
    if filepath.exists():
        print_success(f"{description} exists")
        return True
    else:
        print_error(f"{description} not found: {filepath}")
        return False

def check_qml_fix_progressdialog():
    """Check if ProgressDialog.qml fix is applied."""
    print("\n1. Checking ProgressDialog.qml fix...")
    
    filepath = Path("qml/dialogs/ProgressDialog.qml")
    if not check_file_exists(filepath, "ProgressDialog.qml"):
        return False
    
    content = filepath.read_text()
    
    # Check that 'signal closed()' is NOT present
    if 'signal closed()' in content:
        print_error("Found duplicate 'signal closed()' - this should be removed")
        return False
    else:
        print_success("No duplicate 'signal closed()' found")
    
    # Check that 'signal cancelRequested()' IS present
    if 'signal cancelRequested()' not in content:
        print_error("Missing 'signal cancelRequested()'")
        return False
    else:
        print_success("'signal cancelRequested()' present")
    
    return True

def check_qml_fix_styledbutton():
    """Check if StyledButton.qml fix is applied."""
    print("\n2. Checking StyledButton.qml fix...")
    
    filepath = Path("qml/components/StyledButton.qml")
    if not check_file_exists(filepath, "StyledButton.qml"):
        return False
    
    content = filepath.read_text()
    
    # Check that 'property bool info' IS present
    if 'property bool info' not in content:
        print_error("Missing 'property bool info: false'")
        return False
    else:
        print_success("'property bool info: false' present")
    
    # Check that Theme.accentInfo is used
    if 'Theme.accentInfo' not in content:
        print_error("Missing Theme.accentInfo usage")
        return False
    else:
        print_success("Theme.accentInfo properly used")
    
    # Check key styling integrations
    checks = [
        ('if (primary || danger || success || info)', 'text color check'),
        ('if (info) return Qt.darker(Theme.accentInfo', 'pressed state'),
        ('if (info) return Qt.lighter(Theme.accentInfo', 'hover state'),
        ('if (info) return Theme.accentInfo', 'normal state'),
    ]
    
    for pattern, description in checks:
        if pattern in content:
            print_success(f"Info property used in {description}")
        else:
            print_warning(f"Info property might not be integrated in {description}")
    
    return True

def check_qml_fix_librarytab():
    """Check if LibraryTab.qml uses info property correctly."""
    print("\n3. Checking LibraryTab.qml usage...")
    
    filepath = Path("qml/tabs/LibraryTab.qml")
    if not check_file_exists(filepath, "LibraryTab.qml"):
        return False
    
    content = filepath.read_text()
    
    # Count uses of 'info:'
    info_count = content.count('info:')
    if info_count > 0:
        print_success(f"Found {info_count} uses of 'info:' property")
        return True
    else:
        print_warning("No uses of 'info:' property found (may be OK)")
        return True

def check_python_version():
    """Check Python version."""
    print("\n4. Checking Python version...")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major >= 3 and version.minor >= 7:
        print_success(f"Python {version_str} (OK)")
        return True
    else:
        print_error(f"Python {version_str} (Requires Python 3.7+)")
        return False

def check_pyqt6():
    """Check if PyQt6 is installed and working."""
    print("\n5. Checking PyQt6 installation...")
    
    try:
        import PyQt6.QtCore
        version = PyQt6.QtCore.QT_VERSION_STR
        print_success(f"PyQt6 installed (Qt {version})")
        return True
    except ImportError:
        print_warning("PyQt6 not installed - will be auto-installed on first run")
        return True  # Not a failure since main.py auto-installs

def check_validation_script():
    """Run the existing validation script if available."""
    print("\n6. Running comprehensive validation script...")
    
    script = Path("validate_qml_fixes.py")
    if not script.exists():
        print_warning("validate_qml_fixes.py not found - skipping detailed validation")
        return True
    
    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print_success("Validation script passed all checks")
            # Print key lines from output
            for line in result.stdout.split('\n'):
                if '✓' in line or 'passed' in line.lower():
                    print(f"  {line}")
            return True
        else:
            print_error("Validation script reported issues")
            print(result.stdout)
            return False
    except subprocess.TimeoutExpired:
        print_error("Validation script timed out")
        return False
    except Exception as e:
        print_warning(f"Could not run validation script: {e}")
        return True  # Not a hard failure

def check_main_files():
    """Check that main application files exist."""
    print("\n7. Checking main application files...")
    
    files = [
        ("main.py", "Main entry point"),
        ("qml/main.qml", "Main QML file"),
        ("qml/styles/Theme.qml", "Theme singleton"),
        ("backend/__init__.py", "Backend package"),
    ]
    
    all_ok = True
    for filepath, description in files:
        if not check_file_exists(Path(filepath), description):
            all_ok = False
    
    return all_ok

def main():
    """Run all verification checks."""
    print_header("AudioBrowser-QML Installation Verification")
    
    print("This script verifies that all QML fixes are applied and the")
    print("environment is properly set up to run AudioBrowser-QML.")
    
    # Change to script directory
    script_dir = Path(__file__).parent
    import os
    os.chdir(script_dir)
    print(f"\nWorking directory: {script_dir}")
    
    # Run all checks
    checks = [
        ("QML Fixes", [
            check_qml_fix_progressdialog,
            check_qml_fix_styledbutton,
            check_qml_fix_librarytab,
        ]),
        ("Environment", [
            check_python_version,
            check_pyqt6,
        ]),
        ("Application Files", [
            check_main_files,
            check_validation_script,
        ]),
    ]
    
    results = {}
    for category, check_funcs in checks:
        results[category] = all(check() for check in check_funcs)
    
    # Print summary
    print_header("Verification Summary")
    
    all_passed = True
    for category, passed in results.items():
        if passed:
            print_success(f"{category}: All checks passed")
        else:
            print_error(f"{category}: Some checks failed")
            all_passed = False
    
    # Final status
    print()
    if all_passed:
        print_success(f"{BOLD}SUCCESS: AudioBrowser-QML is ready to run!{RESET}")
        print(f"\nYou can start the application with:")
        print(f"  python3 main.py")
        print(f"\nFor troubleshooting, see:")
        print(f"  docs/user_guides/QML_ERROR_TROUBLESHOOTING.md")
        return 0
    else:
        print_error(f"{BOLD}ISSUES DETECTED: Please fix the issues above{RESET}")
        print(f"\nFor help, see:")
        print(f"  docs/user_guides/QML_ERROR_TROUBLESHOOTING.md")
        print(f"\nOr run the detailed validation script:")
        print(f"  python3 validate_qml_fixes.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())
