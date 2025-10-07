@echo off
REM ==================================================================
REM AudioBrowser Build Script for Windows
REM 
REM This batch file builds an executable for the AudioBrowser 
REM annotation software using PyInstaller.
REM 
REM Requirements:
REM - Python 3.7+ installed and in PATH
REM - PyInstaller installed: pip install pyinstaller
REM - PyQt6 installed: pip install PyQt6
REM 
REM Usage: 
REM   Simply run this batch file from the AudioBrowserAndAnnotation directory:
REM   build_exe.bat
REM
REM The executable will be created in the 'dist' directory.
REM ==================================================================

echo.
echo ====================================
echo AudioBrowser Executable Builder
echo ====================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.7+ and try again.
    pause
    exit /b 1
)

echo Python version:
python --version

REM Check if we're in the right directory
if not exist "audio_browser.py" (
    echo ERROR: audio_browser.py not found!
    echo Please run this script from the AudioBrowserAndAnnotation directory.
    pause
    exit /b 1
)

echo.
echo Checking dependencies...

REM Check for PyInstaller
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install PyInstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
) else (
    echo PyInstaller is already installed.
)

REM Check for PyQt6
python -c "import PyQt6" 2>nul
if errorlevel 1 (
    echo Installing PyQt6...
    pip install PyQt6
    if errorlevel 1 (
        echo ERROR: Failed to install PyQt6
        pause
        exit /b 1
    )
) else (
    echo PyQt6 is already installed.
)

echo.
echo Generating application icon...

REM Generate icon files (PNG and ICO)
python make_icon.py
if errorlevel 1 (
    echo WARNING: Failed to generate icon files. Continuing without icon.
)

echo.
echo Cleaning previous build...

REM Clean previous builds
if exist "build\" rmdir /s /q build
if exist "dist\" rmdir /s /q dist

echo.
echo Building executable with PyInstaller...
echo This may take several minutes...

REM Build the executable
python -m PyInstaller audio_browser.spec

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo Check the output above for error details.
    pause
    exit /b 1
)

echo.
echo ====================================
echo Build completed successfully!
echo ====================================
echo.
echo The AudioFolderPlayer executable is located at:
echo %cd%\dist\AudioFolderPlayer.exe
echo.

REM Check if the executable was created
if exist "dist\AudioFolderPlayer.exe" (
    echo File size:
    dir dist\AudioFolderPlayer.exe | findstr AudioFolderPlayer.exe
    echo.
    echo You can now distribute this executable file!
) else (
    echo WARNING: Expected executable not found at dist\AudioFolderPlayer.exe
    echo Check the dist directory for the actual output.
    dir dist
)

echo.
echo Press any key to exit...
pause >nul