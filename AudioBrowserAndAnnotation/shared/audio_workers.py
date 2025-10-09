"""
Audio Workers

Common audio processing worker classes used across AudioBrowser applications.
These workers run in background threads to avoid blocking the UI.
"""

import sys
import subprocess
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal


def _ensure_import(mod_name: str, pip_name: str | None = None) -> tuple[bool, str]:
    """Try to import a module, auto-installing if needed.
    
    Args:
        mod_name: Module name to import
        pip_name: Package name for pip (defaults to mod_name)
    
    Returns:
        tuple[bool, str]: (success, error_message)
    """
    try:
        __import__(mod_name)
        return True, ""
    except ImportError as e:
        print(f"WARNING: Failed to import {mod_name}: {e}", file=sys.stderr)
        
        if getattr(sys, "frozen", False):
            error_msg = f"{mod_name} is not available in this frozen build"
            print(f"ERROR: {error_msg}", file=sys.stderr)
            return False, error_msg
        
        pkg = pip_name or mod_name
        
        print(f"Installing {pkg}...")
        install_errors = []
        for args in ([sys.executable, "-m", "pip", "install", pkg],
                     [sys.executable, "-m", "pip", "install", "--user", pkg]):
            try:
                subprocess.check_call(args)
                break
            except subprocess.CalledProcessError as e:
                install_errors.append(f"'{' '.join(args)}' failed with exit code {e.returncode}")
                continue
        else:
            error_msg = f"Failed to install {pkg}. Attempted installations:\n" + "\n".join(f"  - {err}" for err in install_errors)
            print(f"ERROR: {error_msg}", file=sys.stderr)
            return False, error_msg
        
        try:
            __import__(mod_name)
            return True, ""
        except ImportError as e:
            error_msg = f"Successfully installed {pkg} but still cannot import {mod_name}: {e}"
            print(f"ERROR: {error_msg}", file=sys.stderr)
            return False, error_msg


# Try to import pydub with auto-install
HAVE_PYDUB, pydub_error = _ensure_import("pydub", "pydub")
if HAVE_PYDUB:
    try:
        from pydub import AudioSegment
    except ImportError:
        HAVE_PYDUB = False
        AudioSegment = None
else:
    AudioSegment = None


# Global FFmpeg path cache
_ffmpeg_path: Optional[str] = None


def find_ffmpeg() -> Optional[str]:
    """
    Find FFmpeg executable on the system.
    
    Returns:
        Path to FFmpeg executable or None if not found
    """
    global _ffmpeg_path
    
    if _ffmpeg_path is not None:
        return _ffmpeg_path
    
    # Try to find FFmpeg
    try:
        import shutil
        _ffmpeg_path = shutil.which("ffmpeg")
        if _ffmpeg_path:
            return _ffmpeg_path
    except Exception:
        pass
    
    # If pydub is available, try its which function
    if HAVE_PYDUB:
        try:
            from pydub.utils import which as pydub_which
            _ffmpeg_path = pydub_which("ffmpeg")
            if _ffmpeg_path:
                return _ffmpeg_path
        except Exception:
            pass
    
    return None


class ChannelMutingWorker(QObject):
    """
    Worker thread for creating channel-muted audio files.
    
    This worker processes audio files to mute specific channels (left/right)
    by reducing their volume significantly. Used for creating practice tracks
    where musicians can mute their own channel.
    """
    
    finished = pyqtSignal(str, str)  # temp_path, error_message (empty string if success)

    def __init__(self, audio_path: str, left_enabled: bool, right_enabled: bool, temp_path: str):
        """
        Initialize the channel muting worker.
        
        Args:
            audio_path: Path to the input audio file
            left_enabled: Whether to keep the left channel audible
            right_enabled: Whether to keep the right channel audible
            temp_path: Path where the output file should be written
        """
        super().__init__()
        self._path = str(audio_path)
        self._left_enabled = left_enabled
        self._right_enabled = right_enabled
        self._temp_path = str(temp_path)

    def run(self):
        """Create channel-muted audio file in background."""
        # Ensure FFmpeg is found and configured before processing
        find_ffmpeg()
        
        try:
            if not HAVE_PYDUB:
                self.finished.emit("", "pydub is not available")
                return
            
            from pydub import AudioSegment
            
            # Load the audio file
            audio = AudioSegment.from_file(self._path)
            
            if audio.channels >= 2:
                # Split into individual channels
                channels = audio.split_to_mono()
                
                # Decrease the volume by a large number of decibels to mute
                if not self._left_enabled:
                    channels[0] = channels[0] - 100
                
                if not self._right_enabled:
                    channels[1] = channels[1] - 100
                
                # Create stereo audio with muted channels
                muted_audio = AudioSegment.from_mono_audiosegments(channels[0], channels[1])
            else:
                # For mono files, just use original or silence
                muted_audio = audio if (self._left_enabled or self._right_enabled) else AudioSegment.silent(duration=len(audio))
            
            # Export temporary file
            temp_path = Path(self._temp_path)
            suffix = temp_path.suffix[1:].lower() if temp_path.suffix else 'wav'
            muted_audio.export(str(temp_path), format=suffix)
            
            self.finished.emit(self._temp_path, "")
            
        except Exception as e:
            print(f"Error creating channel-muted file: {e}")
            self.finished.emit("", str(e))
