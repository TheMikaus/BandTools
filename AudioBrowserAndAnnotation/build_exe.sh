#!/bin/bash

# ==================================================================
# AudioBrowser Build Script (Cross-Platform)
# 
# This script builds an executable for the AudioBrowser 
# annotation software using PyInstaller.
# 
# Requirements:
# - Python 3.7+ installed and in PATH
# - PyInstaller installed: pip install pyinstaller
# - PyQt6 installed: pip install PyQt6
# - For GUI applications on Linux: display server or offscreen rendering
# 
# Usage: 
#   Make executable and run from the AudioBrowserAndAnnotation directory:
#   chmod +x build_exe.sh
#   ./build_exe.sh
#
# The executable will be created in the 'dist' directory.
# ==================================================================

set -e  # Exit on any error

echo
echo "===================================="
echo "AudioBrowser Executable Builder"
echo "===================================="
echo

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "ERROR: Python is not installed or not in PATH."
    echo "Please install Python 3.7+ and try again."
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "Python version:"
$PYTHON_CMD --version

# Check if we're in the right directory
if [ ! -f "audio_browser.py" ]; then
    echo "ERROR: audio_browser.py not found!"
    echo "Please run this script from the AudioBrowserAndAnnotation directory."
    exit 1
fi

echo
echo "Checking dependencies..."

# Function to check if a Python module is available
check_python_module() {
    $PYTHON_CMD -c "import $1" 2>/dev/null
}

# Check for PyInstaller
if ! check_python_module PyInstaller; then
    echo "Installing PyInstaller..."
    $PYTHON_CMD -m pip install PyInstaller
else
    echo "PyInstaller is already installed."
fi

# Check for PyQt6
if ! check_python_module PyQt6; then
    echo "Installing PyQt6..."
    $PYTHON_CMD -m pip install PyQt6
else
    echo "PyQt6 is already installed."
fi

echo
echo "Generating application icon..."

# Generate icon files (PNG and ICO)
# Use offscreen rendering for headless environments
echo "Using offscreen rendering for icon generation..."
QT_QPA_PLATFORM=offscreen $PYTHON_CMD make_icon.py

if [ $? -ne 0 ]; then
    echo "WARNING: Failed to generate icon files. Continuing without icon."
fi

echo
echo "Cleaning previous build..."

# Clean previous builds
rm -rf build dist

echo
echo "Building executable with PyInstaller..."
echo "This may take several minutes..."

# Build the executable
$PYTHON_CMD -m PyInstaller audio_browser.spec

if [ $? -ne 0 ]; then
    echo
    echo "ERROR: Build failed!"
    echo "Check the output above for error details."
    exit 1
fi

echo
echo "===================================="
echo "Build completed successfully!"
echo "===================================="
echo

# Determine the expected executable name based on the platform
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    EXECUTABLE_NAME="AudioFolderPlayer.exe"
else
    EXECUTABLE_NAME="AudioFolderPlayer"
fi

EXECUTABLE_PATH="dist/$EXECUTABLE_NAME"

echo "The AudioFolderPlayer executable is located at:"
echo "$(pwd)/$EXECUTABLE_PATH"
echo

# Check if the executable was created
if [ -f "$EXECUTABLE_PATH" ]; then
    echo "File details:"
    ls -lh "$EXECUTABLE_PATH"
    echo
    echo "You can now distribute this executable file!"
    
    # Make sure it's executable on Unix-like systems
    if [[ "$OSTYPE" != "msys" ]] && [[ "$OSTYPE" != "win32" ]] && [[ "$OSTYPE" != "cygwin" ]]; then
        chmod +x "$EXECUTABLE_PATH"
        echo "Made executable: $EXECUTABLE_PATH"
    fi
else
    echo "WARNING: Expected executable not found at $EXECUTABLE_PATH"
    echo "Check the dist directory for the actual output:"
    ls -la dist/
fi

echo
echo "Build script completed!"