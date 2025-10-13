@echo off
REM Build script for PolyRhythmMetronome (Windows)

echo Building PolyRhythmMetronome...

REM Check if PyInstaller is installed
where pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__

REM Build with PyInstaller
echo Building executable...
pyinstaller Poly_Rhythm_Metronome.spec

REM Check if build was successful
if exist "dist\PolyRhythmMetronome.exe" (
    echo Build successful! Executable is in the dist folder.
) else (
    echo Build failed. Check the output above for errors.
    exit /b 1
)
