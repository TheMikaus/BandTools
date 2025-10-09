#!/usr/bin/env python3
"""
Android Development Environment Setup Script for PolyRhythmMetronome

This script checks for and installs all required dependencies for building
the PolyRhythmMetronome Android app using Buildozer.

Usage:
    python3 setup_android_dev.py
    
    or with sudo for system packages:
    sudo python3 setup_android_dev.py

Features:
- Checks Python version (3.8+)
- Installs buildozer and cython (pip packages)
- Detects and installs system dependencies (Ubuntu/Debian)
- Installs OpenJDK 11
- Verifies all requirements are met
- Provides clear instructions for manual steps if needed
"""

import sys
import subprocess
import shutil
import os
import platform
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
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

def print_info(text):
    """Print an info message."""
    print(f"{BLUE}ℹ{RESET} {text}")

def run_command(cmd, check=True, capture_output=True, shell=False):
    """Run a shell command and return result."""
    try:
        if shell:
            result = subprocess.run(cmd, shell=True, capture_output=capture_output, 
                                    text=True, check=check)
        else:
            result = subprocess.run(cmd, capture_output=capture_output, 
                                    text=True, check=check)
        return result.returncode == 0, result.stdout if capture_output else "", result.stderr if capture_output else ""
    except subprocess.CalledProcessError as e:
        return False, e.stdout if capture_output else "", e.stderr if capture_output else ""
    except Exception as e:
        return False, "", str(e)

def check_python_version():
    """Check if Python version is 3.8 or higher."""
    print_info("Checking Python version...")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version_str} (OK - requires 3.8+)")
        return True
    else:
        print_error(f"Python {version_str} (Requires Python 3.8 or higher)")
        print_warning("Please install Python 3.8+ before continuing")
        return False

def check_pip():
    """Check if pip is available."""
    print_info("Checking pip availability...")
    
    success, stdout, stderr = run_command([sys.executable, "-m", "pip", "--version"])
    
    if success:
        print_success(f"pip is available: {stdout.strip()}")
        return True
    else:
        print_error("pip is not available")
        print_warning("Install pip with: sudo apt install python3-pip")
        return False

def check_and_install_pip_package(package_name, import_name=None, pip_name=None):
    """Check if a pip package is installed, install if not."""
    import_name = import_name or package_name
    pip_name = pip_name or package_name
    
    print_info(f"Checking {package_name}...")
    
    # Try to import the package
    try:
        __import__(import_name)
        print_success(f"{package_name} is already installed")
        return True
    except ImportError:
        print_warning(f"{package_name} is not installed")
        
        # Try to install
        print_info(f"Installing {package_name}...")
        success, stdout, stderr = run_command(
            [sys.executable, "-m", "pip", "install", "--user", pip_name],
            check=False
        )
        
        if success:
            print_success(f"{package_name} installed successfully")
            return True
        else:
            print_error(f"Failed to install {package_name}")
            print_warning(f"Try manually: pip install {pip_name}")
            return False

def detect_os():
    """Detect the operating system."""
    system = platform.system()
    
    if system == "Linux":
        # Try to detect distribution
        try:
            with open("/etc/os-release", "r") as f:
                content = f.read()
                if "Ubuntu" in content or "Debian" in content:
                    return "ubuntu"
                elif "Fedora" in content or "CentOS" in content or "Red Hat" in content:
                    return "fedora"
                else:
                    return "linux"
        except:
            return "linux"
    elif system == "Darwin":
        return "macos"
    elif system == "Windows":
        return "windows"
    else:
        return "unknown"

def check_system_command(command):
    """Check if a system command is available."""
    return shutil.which(command) is not None

def check_openjdk():
    """Check if OpenJDK 11 is installed."""
    print_info("Checking OpenJDK installation...")
    
    # Check for java command
    if not check_system_command("java"):
        print_warning("Java is not installed")
        return False
    
    # Check Java version
    success, stdout, stderr = run_command(["java", "-version"], check=False)
    
    if success or stderr:  # java -version outputs to stderr
        output = stderr if stderr else stdout
        if "openjdk" in output.lower() and ("11" in output or "17" in output or "21" in output):
            print_success(f"OpenJDK is installed: {output.split(chr(10))[0]}")
            return True
        elif "openjdk" in output.lower():
            print_warning(f"OpenJDK is installed but may not be version 11+: {output.split(chr(10))[0]}")
            print_info("OpenJDK 11 is recommended for Android builds")
            return True
        else:
            print_warning(f"Java is installed but not OpenJDK: {output.split(chr(10))[0]}")
            return False
    else:
        print_warning("Could not determine Java version")
        return False

def check_system_packages_ubuntu():
    """Check and install system packages for Ubuntu/Debian."""
    print_info("Checking system packages (Ubuntu/Debian)...")
    
    # Note: libtinfo5 removed as it's not available in Ubuntu 24.04+
    # ncurses6 provides the necessary functionality
    required_packages = [
        "git", "zip", "unzip", "autoconf", "libtool", "pkg-config",
        "zlib1g-dev", "libncurses-dev", "libncursesw5-dev", 
        "cmake", "libffi-dev", "libssl-dev"
    ]
    
    # Check which packages are installed
    missing_packages = []
    for package in required_packages:
        success, stdout, stderr = run_command(
            ["dpkg", "-s", package],
            check=False,
            capture_output=True
        )
        if not success:
            missing_packages.append(package)
    
    if not missing_packages:
        print_success("All required system packages are installed")
        return True
    
    print_warning(f"Missing packages: {', '.join(missing_packages)}")
    
    # Check if we have sudo
    if os.geteuid() != 0:
        print_error("Root/sudo access required to install system packages")
        print_info("Please run one of the following commands:")
        print(f"\n  sudo apt update")
        print(f"  sudo apt install -y {' '.join(missing_packages)}")
        print()
        return False
    
    # Install missing packages
    print_info("Installing missing packages...")
    print_info("Running: apt update")
    success, stdout, stderr = run_command(
        ["apt", "update"],
        check=False
    )
    
    if not success:
        print_error("Failed to update package list")
        return False
    
    print_info(f"Installing: {' '.join(missing_packages)}")
    success, stdout, stderr = run_command(
        ["apt", "install", "-y"] + missing_packages,
        check=False
    )
    
    if success:
        print_success("System packages installed successfully")
        return True
    else:
        print_error("Failed to install some packages")
        return False

def install_openjdk_ubuntu():
    """Install OpenJDK 11 on Ubuntu/Debian."""
    print_info("Installing OpenJDK 11...")
    
    if os.geteuid() != 0:
        print_error("Root/sudo access required to install OpenJDK")
        print_info("Please run: sudo apt install -y openjdk-11-jdk")
        return False
    
    success, stdout, stderr = run_command(
        ["apt", "install", "-y", "openjdk-11-jdk"],
        check=False
    )
    
    if success:
        print_success("OpenJDK 11 installed successfully")
        return True
    else:
        print_error("Failed to install OpenJDK 11")
        return False

def provide_manual_instructions(os_type):
    """Provide manual installation instructions for other OS."""
    print_header("Manual Installation Instructions")
    
    if os_type == "macos":
        print_info("For macOS, install dependencies using Homebrew:")
        print("\n  brew install python3")
        print("  brew install openjdk@11")
        print("  pip3 install buildozer cython")
        print()
        print_warning("Note: Android development on macOS may require additional setup")
        
    elif os_type == "fedora":
        print_info("For Fedora/RHEL-based systems:")
        print("\n  sudo dnf install python3 python3-pip java-11-openjdk-devel")
        print("  sudo dnf install git zip unzip autoconf libtool pkgconfig")
        print("  sudo dnf install zlib-devel ncurses-devel cmake libffi-devel openssl-devel")
        print("  pip3 install --user buildozer cython")
        print()
        
    elif os_type == "windows":
        print_error("Windows is not recommended for Android development with Buildozer")
        print_info("Consider using:")
        print("  - WSL2 (Windows Subsystem for Linux) with Ubuntu")
        print("  - Docker container with Linux")
        print("  - Linux VM")
        print()
        
    else:
        print_info("For your system, you'll need to install:")
        print("  - Python 3.8+")
        print("  - pip")
        print("  - OpenJDK 11")
        print("  - Build tools: git, zip, unzip, cmake")
        print("  - Development libraries: zlib, ncurses, libffi, openssl")
        print("  - Python packages: buildozer, cython")
        print()

def verify_buildozer_setup():
    """Verify buildozer is properly set up."""
    print_info("Verifying buildozer setup...")
    
    # Check if buildozer command is available
    if check_system_command("buildozer"):
        print_success("buildozer command is available")
        
        # Try to get buildozer version
        success, stdout, stderr = run_command(
            ["buildozer", "--version"],
            check=False
        )
        if success:
            print_success(f"buildozer version: {stdout.strip()}")
        
        return True
    else:
        print_warning("buildozer command not found in PATH")
        print_info("You may need to add ~/.local/bin to your PATH")
        print_info("Add this to your ~/.bashrc or ~/.zshrc:")
        print('  export PATH="$HOME/.local/bin:$PATH"')
        return False

def main():
    """Main setup function."""
    print_header("Android Development Environment Setup")
    print_info("Setting up environment for PolyRhythmMetronome Android build")
    
    os_type = detect_os()
    print_info(f"Detected OS: {os_type}")
    
    all_checks_passed = True
    
    # 1. Check Python version
    print_header("Step 1: Python Version Check")
    if not check_python_version():
        all_checks_passed = False
        print_error("Python version check failed")
        return 1
    
    # 2. Check pip
    print_header("Step 2: pip Check")
    if not check_pip():
        all_checks_passed = False
        print_error("pip check failed")
        return 1
    
    # 3. Install Python packages
    print_header("Step 3: Python Packages")
    
    buildozer_ok = check_and_install_pip_package("buildozer")
    cython_ok = check_and_install_pip_package("Cython", import_name="Cython", pip_name="cython")
    
    if not buildozer_ok or not cython_ok:
        all_checks_passed = False
    
    # 4. Verify buildozer
    verify_buildozer_setup()
    
    # 5. Check/Install system dependencies
    print_header("Step 4: System Dependencies")
    
    if os_type == "ubuntu":
        # Check OpenJDK
        openjdk_ok = check_openjdk()
        if not openjdk_ok:
            if os.geteuid() == 0:
                install_openjdk_ubuntu()
            else:
                print_warning("OpenJDK is not installed")
                print_info("Install with: sudo apt install -y openjdk-11-jdk")
                all_checks_passed = False
        
        # Check system packages
        packages_ok = check_system_packages_ubuntu()
        if not packages_ok:
            all_checks_passed = False
            
    elif os_type in ["macos", "fedora", "windows", "linux"]:
        print_warning("Automatic system package installation not available for this OS")
        provide_manual_instructions(os_type)
        
        # Still check for OpenJDK
        if not check_openjdk():
            all_checks_passed = False
    
    # 6. Summary
    print_header("Setup Summary")
    
    if all_checks_passed:
        print_success("All dependencies are installed!")
        print()
        print_info("Next steps:")
        print("  1. Navigate to the android directory:")
        print("     cd PolyRhythmMetronome/android")
        print()
        print("  2. Build the APK:")
        print("     buildozer -v android debug")
        print()
        print_info("Note: First build will download Android SDK/NDK (~2GB)")
        print_info("      and may take 30-60 minutes")
        print()
        return 0
    else:
        print_warning("Some dependencies are missing or could not be installed")
        print_info("Please review the messages above and install missing dependencies")
        print()
        
        if os_type == "ubuntu":
            print_info("For Ubuntu/Debian, you may need to run:")
            print("  sudo python3 setup_android_dev.py")
            print()
        
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
