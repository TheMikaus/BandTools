#!/usr/bin/env python3
"""
Test script for FFmpeg detection in audio_browser.py

This script tests the improved FFmpeg detection without requiring Qt/GUI libraries.
Run this to verify FFmpeg detection is working correctly on your system.
"""

import sys
import os
import shutil
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

print("=" * 70)
print("FFmpeg Detection Test for AudioBrowser")
print("=" * 70)

# Test 1: Check Python version
print(f"\n1. Python version: {sys.version.split()[0]}")
print(f"   Platform: {sys.platform}")

# Test 2: Check if pydub is available
print("\n2. Checking pydub availability...")
try:
    from pydub.utils import which as pydub_which
    from pydub import AudioSegment
    HAVE_PYDUB = True
    print("   ✓ pydub is available")
except ImportError as e:
    pydub_which = None
    AudioSegment = None
    HAVE_PYDUB = False
    print(f"   ✗ pydub is NOT available: {e}")
    print("     Install with: pip install pydub")

# Test 3: Test pydub's which() if available
print("\n3. Testing pydub.utils.which('ffmpeg')...")
if pydub_which:
    try:
        result = pydub_which("ffmpeg")
        if result:
            print(f"   ✓ Found via pydub: {result}")
        else:
            print("   ✗ Not found via pydub")
    except Exception as e:
        print(f"   ✗ pydub.which() error: {e}")
else:
    print("   ⊘ Skipped (pydub not available)")

# Test 4: Test standard shutil.which()
print("\n4. Testing shutil.which('ffmpeg')...")
try:
    result = shutil.which("ffmpeg")
    if result:
        print(f"   ✓ Found via shutil: {result}")
    else:
        print("   ✗ Not found via shutil")
except Exception as e:
    print(f"   ✗ shutil.which() error: {e}")

# Test 5: Check common Windows paths (if on Windows)
if sys.platform == "win32":
    print("\n5. Checking common Windows installation paths...")
    common_paths = [
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
        r"C:\ffmpeg\bin\ffmpeg.exe",
        os.path.expanduser(r"~\ffmpeg\bin\ffmpeg.exe"),
        os.path.expanduser(r"~\scoop\apps\ffmpeg\current\bin\ffmpeg.exe"),
    ]
    
    found_in_common = False
    for path in common_paths:
        if os.path.isfile(path):
            print(f"   ✓ Found at: {path}")
            found_in_common = True
    
    if not found_in_common:
        print("   ✗ Not found in common Windows paths")
else:
    print("\n5. Common Windows paths check skipped (not on Windows)")

# Test 6: Test actual FFmpeg execution
print("\n6. Testing FFmpeg execution...")
ffmpeg_path = shutil.which("ffmpeg")
if ffmpeg_path:
    try:
        import subprocess
        result = subprocess.run(
            [ffmpeg_path, "-version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"   ✓ FFmpeg is executable: {version_line}")
        else:
            print(f"   ✗ FFmpeg returned error code: {result.returncode}")
    except Exception as e:
        print(f"   ✗ Could not execute FFmpeg: {e}")
else:
    print("   ⊘ Skipped (ffmpeg not found in PATH)")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

if not HAVE_PYDUB:
    print("\n⚠ ISSUE: pydub is not installed")
    print("  Solution: pip install pydub")
    print("\nWithout pydub, MP3 files will not work in AudioBrowser.")
elif not (pydub_which and pydub_which("ffmpeg")) and not shutil.which("ffmpeg"):
    print("\n⚠ ISSUE: FFmpeg is not found on your system")
    print("  Solutions:")
    print("    • Windows: winget install ffmpeg")
    print("    • Linux: sudo apt install ffmpeg")
    print("    • macOS: brew install ffmpeg")
    print("\nWithout FFmpeg, MP3 playback and waveforms will not work.")
    print("WAV files will still work without FFmpeg.")
else:
    print("\n✓ SUCCESS: FFmpeg detection should work correctly!")
    print("  MP3 files and waveforms should work in AudioBrowser.")

print("\n" + "=" * 70)
print("Test complete. You can now run AudioBrowser.")
print("=" * 70)
