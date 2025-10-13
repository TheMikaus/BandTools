#!/bin/bash
# Build script for PolyRhythmMetronome

echo "Building PolyRhythmMetronome..."

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist __pycache__

# Build with PyInstaller
echo "Building executable..."
pyinstaller Poly_Rhythm_Metronome.spec

# Check if build was successful
if [ -f "dist/PolyRhythmMetronome" ] || [ -f "dist/PolyRhythmMetronome.exe" ]; then
    echo "Build successful! Executable is in the dist folder."
else
    echo "Build failed. Check the output above for errors."
    exit 1
fi
