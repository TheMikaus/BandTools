#!/usr/bin/env python3
"""
PolyRhythmMetronome - Android Version
A touch-optimized metronome for Android devices (Kindle Fire HD 10)

Features:
- Multiple layers per ear (like desktop version)
- Touch-optimized large buttons and sliders
- Sound options: Tone and Drum synthesis
- BPM control with preset buttons and slider
- Save/Load rhythm patterns
- Visual feedback with color flashing
- Landscape and portrait orientation support
"""

import sys
import subprocess
import importlib
import json
import os
import threading
import math
import time
import uuid
from pathlib import Path
from io import StringIO
from datetime import datetime

# ---------------- Auto-install missing packages ---------------- #

def ensure_pkg(pkg_name: str, import_name: str = None):
    """Auto-install packages if not available (not for frozen builds)"""
    mod_name = import_name or pkg_name
    try:
        return importlib.import_module(mod_name)
    except ImportError as first_err:
        if getattr(sys, "frozen", False):
            raise first_err
        try:
            print(f"[setup] Installing '{pkg_name}' ...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg_name])
            return importlib.import_module(mod_name)
        except Exception as install_err:
            print(f"[setup] Failed to auto-install '{pkg_name}'. Error:\n{install_err}")
            raise first_err

# Ensure numpy is installed
np = ensure_pkg("numpy")

# Try to import Kivy
try:
    kivy = ensure_pkg("kivy")
    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.floatlayout import FloatLayout
    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.button import Button
    from kivy.uix.label import Label
    from kivy.uix.slider import Slider
    from kivy.uix.togglebutton import ToggleButton
    from kivy.uix.spinner import Spinner
    from kivy.uix.popup import Popup
    from kivy.uix.textinput import TextInput
    from kivy.clock import Clock
    from kivy.graphics import Color, Rectangle
    from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ListProperty
    from kivy.utils import platform
    from kivy.core.window import Window
except ImportError as e:
    print(f"Error importing Kivy: {e}")
    print("Please install Kivy: pip install kivy")
    sys.exit(1)

# Android-specific imports
if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])

# ---------------- Log Capture ---------------- #

class LogCapture:
    """Captures stdout/stderr for display in the app"""
    def __init__(self):
        self.buffer = StringIO()
        self.start_time = datetime.now()
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        
    def write(self, text):
        """Capture text to buffer and pass through to original"""
        if text and text.strip():
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            line = f"[{timestamp}] {text}"
            self.buffer.write(line)
            if not line.endswith('\n'):
                self.buffer.write('\n')
        # Also write to original output
        self.original_stdout.write(text)
        
    def flush(self):
        """Flush both buffer and original stdout"""
        self.buffer.flush()
        self.original_stdout.flush()
        
    def get_logs(self):
        """Get all captured logs"""
        return self.buffer.getvalue()

# Initialize log capture at module level
log_capture = LogCapture()
sys.stdout = log_capture
sys.stderr = log_capture

# ---------------- Constants ---------------- #

SAMPLE_RATE = 44100
BASE_AMP = 0.22
DEFAULT_ACCENT_FACTOR = 1.6
FLASH_DURATION = 0.12  # seconds
AUTOSAVE_FILE = "metronome_autosave.json"

# BPM presets for quick access
BPM_PRESETS = [60, 80, 100, 120, 140, 160, 180, 200]

# Subdivision options (notes per beat)
SUBDIV_OPTIONS = ["2", "3", "4", "5", "6", "7", "8", "16", "32", "64"]

# Drum sound options
DRUM_CHOICES = ["kick", "snare", "hihat", "crash", "tom", "ride"]

# Sound mode options
SOUND_MODES = ["tone", "drum", "mp3_tick"]

# ---------------- Audio Generation ---------------- #

class ToneGenerator:
    """Generate simple tone beeps for metronome clicks"""
    
    def __init__(self, sample_rate=SAMPLE_RATE):
        self.sample_rate = sample_rate
        self.cache = {}
    
    def generate_beep(self, frequency, duration_ms=50):
        """Generate a short beep at the specified frequency"""
        key = (frequency, duration_ms)
        if key in self.cache:
            return self.cache[key]
        
        num_samples = int(self.sample_rate * (duration_ms / 1000.0))
        t = np.arange(num_samples, dtype=np.float32) / self.sample_rate
        
        # Generate tone with envelope
        tone = np.sin(2 * np.pi * frequency * t)
        
        # Apply fade in/out envelope
        fade_samples = min(int(num_samples * 0.1), num_samples // 2)
        envelope = np.ones(num_samples, dtype=np.float32)
        envelope[:fade_samples] = np.linspace(0.0, 1.0, fade_samples)
        envelope[-fade_samples:] = np.linspace(1.0, 0.0, fade_samples)
        
        audio_data = (tone * envelope * 0.3).astype(np.float32)
        self.cache[key] = audio_data
        return audio_data


class DrumSynth:
    """Synthesize drum sounds"""
    
    def __init__(self, sample_rate=SAMPLE_RATE):
        self.sample_rate = sample_rate
        self.cache = {}
    
    def get(self, drum_name):
        """Get drum sound by name"""
        key = (drum_name or "").lower()
        if key in self.cache:
            return self.cache[key]
        
        method = getattr(self, f"_make_{key}", None)
        data = method() if method else self._make_snare()
        self.cache[key] = data
        return data
    
    def _make_kick(self):
        """Generate improved kick drum sound with punch and depth"""
        sr = self.sample_rate
        dur = 0.35
        n = int(sr * dur)
        t = np.arange(n, dtype=np.float32) / sr
        
        # Two-stage frequency sweep for more realistic kick
        # Stage 1: Quick drop for punch (150Hz to 60Hz)
        f0, f1 = 150.0, 60.0
        k = np.log(f1 / f0) / (dur * 0.3)
        phase1 = 2 * np.pi * (f0 * (np.expm1(k * t) / k))
        tone1 = np.sin(phase1) * np.exp(-t / 0.08)
        
        # Stage 2: Lower fundamental for depth (60Hz to 45Hz)
        f2, f3 = 60.0, 45.0
        k2 = np.log(f3 / f2) / dur
        phase2 = 2 * np.pi * (f2 * (np.expm1(k2 * t) / k2))
        tone2 = np.sin(phase2) * np.exp(-t / 0.18)
        
        # Attack click for beater impact
        click = np.exp(-t / 0.005) * 0.3
        
        # Combine elements with envelope
        env = np.exp(-t / 0.20).astype(np.float32)
        kick = (0.5 * tone1 + 0.4 * tone2 + click) * env
        
        return kick.astype(np.float32)
    
    def _make_snare(self):
        """Generate improved snare drum sound with crisp snap"""
        sr = self.sample_rate
        dur = 0.25
        n = int(sr * dur)
        t = np.arange(n, dtype=np.float32) / sr
        
        # High-passed noise for snare wire sound
        noise = np.random.uniform(-1, 1, size=n).astype(np.float32)
        # Simple high-pass by differencing
        noise_hp = np.diff(noise, prepend=0)
        env_n = np.exp(-t / 0.10).astype(np.float32)
        
        # Multi-frequency body for richer tone
        body1 = np.sin(2 * np.pi * 180 * t) * np.exp(-t / 0.08)
        body2 = np.sin(2 * np.pi * 330 * t) * np.exp(-t / 0.06)
        
        # Sharp attack transient
        attack = np.exp(-t / 0.003) * 0.4
        
        # Combine elements
        snare = (0.6 * noise_hp * env_n + 0.2 * body1 + 0.15 * body2 + attack)
        
        return snare.astype(np.float32)
    
    def _make_hihat(self):
        """Generate improved hi-hat sound with metallic character"""
        sr = self.sample_rate
        dur = 0.08
        n = int(sr * dur)
        t = np.arange(n, dtype=np.float32) / sr
        
        # Band-limited noise for metallic character
        noise = np.random.uniform(-1, 1, size=n).astype(np.float32)
        # Add high-frequency oscillations for shimmer
        metallic = np.sin(2 * np.pi * 8000 * t) * np.sin(2 * np.pi * 11000 * t)
        
        # Fast decay envelope
        env = np.exp(-t / 0.025).astype(np.float32)
        
        hihat = (0.7 * noise + 0.3 * metallic) * env
        
        return hihat.astype(np.float32)
    
    def _make_crash(self):
        """Generate improved crash cymbal sound with shimmer"""
        sr = self.sample_rate
        dur = 1.5
        n = int(sr * dur)
        t = np.arange(n, dtype=np.float32) / sr
        
        # Complex noise for metallic character
        noise = np.random.uniform(-1, 1, size=n).astype(np.float32)
        
        # Add multiple high-frequency components for shimmer
        shimmer1 = np.sin(2 * np.pi * 3500 * t) * np.sin(2 * np.pi * 1.3 * t)
        shimmer2 = np.sin(2 * np.pi * 7000 * t) * np.sin(2 * np.pi * 2.1 * t)
        
        # Slow decay with slight modulation
        env = np.exp(-t / 0.7) * (1 + 0.1 * np.sin(2 * np.pi * 3 * t))
        
        crash = (0.5 * noise + 0.25 * shimmer1 + 0.25 * shimmer2) * env
        
        return crash.astype(np.float32)
    
    def _make_tom(self):
        """Generate improved tom drum sound with resonance"""
        sr = self.sample_rate
        dur = 0.5
        n = int(sr * dur)
        t = np.arange(n, dtype=np.float32) / sr
        
        # Frequency sweep for realistic tom pitch bend
        f0, f1 = 200.0, 160.0
        k = np.log(f1 / f0) / (dur * 0.2)
        # Clip k*t to avoid overflow in expm1 (values > 88 cause overflow for float32)
        kt_clipped = np.clip(k * t, -88, 88)
        phase = 2 * np.pi * (f0 * (np.expm1(kt_clipped) / k))
        fundamental = np.sin(phase)
        
        # Add harmonics for richer tone
        harmonic2 = np.sin(2 * phase) * 0.3
        harmonic3 = np.sin(3 * phase) * 0.15
        
        # Envelope with slight ring
        env = np.exp(-t / 0.30).astype(np.float32)
        
        tom = (fundamental + harmonic2 + harmonic3) * env
        
        return tom.astype(np.float32)
    
    def _make_ride(self):
        """Generate improved ride cymbal sound with bell-like ping"""
        sr = self.sample_rate
        dur = 1.0
        n = int(sr * dur)
        t = np.arange(n, dtype=np.float32) / sr
        
        # Bell-like ping with harmonics
        ping1 = np.sin(2 * np.pi * 850 * t) * np.exp(-t / 0.35)
        ping2 = np.sin(2 * np.pi * 1700 * t) * np.exp(-t / 0.25) * 0.4
        ping3 = np.sin(2 * np.pi * 2550 * t) * np.exp(-t / 0.20) * 0.2
        
        # Sustained wash
        noise = np.random.uniform(-1, 1, size=n).astype(np.float32)
        wash = noise * np.exp(-t / 0.9) * 0.15
        
        ride = ping1 + ping2 + ping3 + wash
        
        return ride.astype(np.float32)


# ---------------- Audio File Loading (MP3 support via Android MediaCodec) ---------------- #

class WaveCache:
    """Cache for loading and resampling audio files, including MP3 via Android MediaCodec"""
    
    def __init__(self, sr=SAMPLE_RATE):
        self.sr = sr
        self._c = {}
    
    def get(self, path: str):
        """Load an audio file and return normalized float32 samples"""
        if not path:
            return None
        
        key = os.path.abspath(path)
        if key in self._c:
            return self._c[key]
        
        if not os.path.exists(key):
            raise FileNotFoundError(f"Audio file not found: {key}")
        
        # Check if it's an MP3 file
        if key.lower().endswith('.mp3'):
            data, sr = self._read_mp3(key)
        else:
            data, sr = self._read_wav_any(key)
        
        # Resample if needed
        if sr != self.sr:
            data = self._resample_linear(data, sr, self.sr)
        
        self._c[key] = data.astype(np.float32, copy=False)
        return self._c[key]
    
    @staticmethod
    def _read_mp3(path):
        """Read MP3 file using Android MediaCodec (native, no ffmpeg needed)"""
        if platform != 'android':
            raise RuntimeError("Android MediaCodec MP3 decoding only works on Android")
        
        try:
            from jnius import autoclass
            
            # Import Android media classes
            MediaExtractor = autoclass('android.media.MediaExtractor')
            MediaCodec = autoclass('android.media.MediaCodec')
            MediaFormat = autoclass('android.media.MediaFormat')
            ByteBuffer = autoclass('java.nio.ByteBuffer')
            
            # Create extractor and set data source
            extractor = MediaExtractor()
            extractor.setDataSource(path)
            
            # Find audio track
            num_tracks = extractor.getTrackCount()
            audio_track_index = -1
            audio_format = None
            
            for i in range(num_tracks):
                format = extractor.getTrackFormat(i)
                mime = format.getString(MediaFormat.KEY_MIME)
                if mime.startswith('audio/'):
                    audio_track_index = i
                    audio_format = format
                    break
            
            if audio_track_index < 0:
                raise RuntimeError(f"No audio track found in {path}")
            
            # Select the audio track
            extractor.selectTrack(audio_track_index)
            
            # Get audio properties
            sample_rate = audio_format.getInteger(MediaFormat.KEY_SAMPLE_RATE)
            channel_count = audio_format.getInteger(MediaFormat.KEY_CHANNEL_COUNT)
            
            # Create decoder
            mime = audio_format.getString(MediaFormat.KEY_MIME)
            decoder = MediaCodec.createDecoderByType(mime)
            decoder.configure(audio_format, None, None, 0)
            decoder.start()
            
            # Decode audio
            decoded_samples = []
            input_eof = False
            output_eof = False
            timeout_us = 10000  # 10ms timeout
            
            while not output_eof:
                # Feed input
                if not input_eof:
                    input_buffer_index = decoder.dequeueInputBuffer(timeout_us)
                    if input_buffer_index >= 0:
                        input_buffer = decoder.getInputBuffer(input_buffer_index)
                        sample_size = extractor.readSampleData(input_buffer, 0)
                        
                        if sample_size < 0:
                            # End of input
                            decoder.queueInputBuffer(input_buffer_index, 0, 0, 0, MediaCodec.BUFFER_FLAG_END_OF_STREAM)
                            input_eof = True
                        else:
                            presentation_time_us = extractor.getSampleTime()
                            decoder.queueInputBuffer(input_buffer_index, 0, sample_size, presentation_time_us, 0)
                            extractor.advance()
                
                # Get output
                buffer_info = autoclass('android.media.MediaCodec$BufferInfo')()
                output_buffer_index = decoder.dequeueOutputBuffer(buffer_info, timeout_us)
                
                if output_buffer_index >= 0:
                    output_buffer = decoder.getOutputBuffer(output_buffer_index)
                    
                    if buffer_info.size > 0:
                        # Read PCM data from output buffer
                        # Create a byte array to hold the data
                        byte_array = bytearray(buffer_info.size)
                        output_buffer.position(buffer_info.offset)
                        
                        # Read bytes from ByteBuffer
                        for i in range(buffer_info.size):
                            byte_array[i] = output_buffer.get() & 0xFF
                        
                        # Convert bytes to int16 samples (assuming 16-bit PCM)
                        samples = np.frombuffer(byte_array, dtype=np.int16)
                        decoded_samples.append(samples)
                    
                    decoder.releaseOutputBuffer(output_buffer_index, False)
                    
                    if (buffer_info.flags & MediaCodec.BUFFER_FLAG_END_OF_STREAM) != 0:
                        output_eof = True
                elif output_buffer_index == MediaCodec.INFO_OUTPUT_FORMAT_CHANGED:
                    # Output format changed (not critical for our use case)
                    pass
            
            # Clean up
            decoder.stop()
            decoder.release()
            extractor.release()
            
            # Concatenate all decoded samples
            if not decoded_samples:
                raise RuntimeError(f"No audio data decoded from {path}")
            
            audio_data = np.concatenate(decoded_samples)
            
            # Convert to mono if stereo
            if channel_count > 1:
                audio_data = audio_data.reshape(-1, channel_count).mean(axis=1)
            
            # Normalize to float32 in range [-1.0, 1.0]
            audio_data = audio_data.astype(np.float32) / 32768.0
            
            return audio_data, sample_rate
            
        except Exception as e:
            raise RuntimeError(f"Failed to read MP3 file {path}: {e}")
    
    @staticmethod
    def _read_wav_any(path):
        """Read WAV file"""
        import wave
        
        with wave.open(path, 'rb') as wf:
            ch = wf.getnchannels()
            sw = wf.getsampwidth()
            fr = wf.getframerate()
            nf = wf.getnframes()
            raw = wf.readframes(nf)
        
        # Convert based on sample width
        if sw == 1:
            data = np.frombuffer(raw, dtype=np.uint8).astype(np.float32)
            data = (data - 128.0) / 128.0
        elif sw == 2:
            data = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        elif sw == 4:
            arr = np.frombuffer(raw, dtype=np.int32)
            if np.max(np.abs(arr)) < 1e6:
                data = np.frombuffer(raw, dtype=np.float32)
            else:
                data = arr.astype(np.float32) / 2147483648.0
        else:
            raise ValueError("Only 8/16/32-bit or float32 WAV supported.")
        
        # Convert to mono if needed
        if ch > 1:
            data = data.reshape(-1, ch).mean(axis=1)
        
        return data.astype(np.float32, copy=False), fr
    
    @staticmethod
    def _resample_linear(x, sr_from, sr_to):
        """Simple linear resampling"""
        if sr_from == sr_to or len(x) == 0:
            return x
        
        dur = len(x) / float(sr_from)
        new_len = int(round(dur * sr_to))
        
        if new_len <= 1:
            return np.zeros(1, dtype=np.float32)
        
        xp = np.linspace(0.0, 1.0, len(x), dtype=np.float32)
        xnew = np.linspace(0.0, 1.0, new_len, dtype=np.float32)
        
        return np.interp(xnew, xp, x.astype(np.float32, copy=False)).astype(np.float32)


class Mp3TickCache:
    """Manage MP3 tick sounds from the ticks folder"""
    
    def __init__(self, sr=SAMPLE_RATE, ticks_dir="ticks"):
        self.sr = sr
        self.ticks_dir = ticks_dir
        self._wave_cache = WaveCache(sr)
        self._pairs = {}  # name -> (path1, path2) or (path, None)
        self._scan_ticks_folder()
    
    def _scan_ticks_folder(self):
        """Scan the ticks folder for MP3 files and identify pairs"""
        if not os.path.exists(self.ticks_dir):
            return
        
        mp3_files = {}
        for filename in os.listdir(self.ticks_dir):
            if filename.lower().endswith('.mp3'):
                full_path = os.path.join(self.ticks_dir, filename)
                name_without_ext = os.path.splitext(filename)[0]
                mp3_files[name_without_ext] = full_path
        
        # Identify pairs (files ending in _1 and _2)
        processed = set()
        for name in mp3_files:
            if name in processed:
                continue
            
            if name.endswith('_1'):
                base_name = name[:-2]
                pair_name = base_name + '_2'
                if pair_name in mp3_files:
                    # Found a pair
                    self._pairs[base_name] = (mp3_files[name], mp3_files[pair_name])
                    processed.add(name)
                    processed.add(pair_name)
                else:
                    # Single file with _1 suffix
                    self._pairs[name] = (mp3_files[name], None)
                    processed.add(name)
            elif name.endswith('_2'):
                # Check if corresponding _1 exists
                base_name = name[:-2]
                pair_name = base_name + '_1'
                if pair_name not in mp3_files:
                    # Orphan _2 file
                    self._pairs[name] = (mp3_files[name], None)
                    processed.add(name)
            else:
                # Regular single file
                self._pairs[name] = (mp3_files[name], None)
                processed.add(name)
    
    def get_available_ticks(self):
        """Return list of available tick names"""
        return sorted(self._pairs.keys())
    
    def get(self, name: str, is_accent: bool = False):
        """Get the tick sound for the given name. If it's a pair, return the appropriate one."""
        if name not in self._pairs:
            return None
        
        path1, path2 = self._pairs[name]
        if path2 is not None:
            # It's a pair - use path1 for accent, path2 for regular
            path = path1 if is_accent else path2
        else:
            # Single file
            path = path1
        
        try:
            return self._wave_cache.get(path)
        except Exception:
            return None


def get_mp3_tick_choices():
    """Get list of available MP3 ticks from the ticks folder"""
    mp3_cache = Mp3TickCache()
    return mp3_cache.get_available_ticks()


# ---------------- Rhythm State (Data Model) ---------------- #

def new_uid():
    """Generate unique ID for layers"""
    return uuid.uuid4().hex


def color_distance(color1, color2):
    """Calculate Euclidean distance between two hex colors"""
    try:
        # Parse first color
        c1 = color1.lstrip('#')
        r1 = int(c1[0:2], 16)
        g1 = int(c1[2:4], 16)
        b1 = int(c1[4:6], 16)
        
        # Parse second color
        c2 = color2.lstrip('#')
        r2 = int(c2[0:2], 16)
        g2 = int(c2[2:4], 16)
        b2 = int(c2[4:6], 16)
        
        # Calculate Euclidean distance
        return ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5
    except Exception:
        return 0


def random_dark_color(previous_color=None, min_distance=80):
    """Generate a random dark color suitable for inactive layer background
    
    Args:
        previous_color: Previous color to avoid (hex string)
        min_distance: Minimum Euclidean distance from previous color (default 80)
    """
    import random
    
    max_attempts = 20
    for attempt in range(max_attempts):
        # Generate RGB values in the range 40-120 to ensure dark but visible colors
        r = random.randint(40, 120)
        g = random.randint(40, 120)
        b = random.randint(40, 120)
        new_color = f"#{r:02x}{g:02x}{b:02x}"
        
        # If no previous color, return immediately
        if previous_color is None:
            return new_color
        
        # Check distance from previous color
        distance = color_distance(new_color, previous_color)
        if distance >= min_distance:
            return new_color
    
    # If we couldn't find a distant color after max_attempts, return the last one
    return new_color


def brighten_color(hex_color, factor=2.0):
    """Create a brighter version of a hex color for flash effect"""
    try:
        # Remove # if present
        hex_color = hex_color.lstrip('#')
        # Parse RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        # Brighten by factor, capping at 255
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        # Fallback to original color if parsing fails
        return hex_color


def make_layer(subdiv=4, freq=880.0, vol=1.0, mute=False, mode="tone", drum="snare", mp3_tick="", color="#9CA3AF", flash_color=None, accent_vol=1.6, uid=None):
    """Create a layer dictionary"""
    # Auto-generate flash_color if not provided
    if flash_color is None:
        flash_color = brighten_color(color)
    return {
        "uid": uid or new_uid(),
        "subdiv": int(subdiv),
        "freq": float(freq),
        "vol": float(vol),
        "mute": bool(mute),
        "mode": mode,
        "drum": drum,
        "mp3_tick": mp3_tick,
        "color": color,
        "flash_color": flash_color,
        "accent_vol": float(accent_vol)  # Volume multiplier for first beat of measure
    }


class RhythmState:
    """Stores the current rhythm configuration with multiple layers per ear"""
    
    def __init__(self):
        self.bpm = 120.0
        self.beats_per_measure = 4
        self.accent_factor = DEFAULT_ACCENT_FACTOR
        self.flash_enabled = False
        self.master_volume = 1.0  # Master volume control (0.0 to 2.0)
        
        # Multiple layers per ear (like desktop)
        self.left = []  # List of layer dictionaries
        self.right = []  # List of layer dictionaries
        
        self._lock = threading.RLock()
        
        # Start with one default layer per ear
        self.left.append(make_layer(subdiv=4, freq=880.0, vol=1.0, color="#3B82F6"))
        self.right.append(make_layer(subdiv=4, freq=440.0, vol=1.0, color="#EF4444"))
    
    def to_dict(self):
        """Serialize to dictionary for saving"""
        with self._lock:
            return {
                "bpm": self.bpm,
                "beats_per_measure": self.beats_per_measure,
                "accent_factor": self.accent_factor,
                "flash_enabled": self.flash_enabled,
                "master_volume": self.master_volume,
                "left": self.left,
                "right": self.right
            }
    
    def from_dict(self, data):
        """Load from dictionary"""
        with self._lock:
            self.bpm = float(data.get("bpm", 120.0))
            self.beats_per_measure = int(data.get("beats_per_measure", 4))
            self.accent_factor = float(data.get("accent_factor", DEFAULT_ACCENT_FACTOR))
            self.flash_enabled = bool(data.get("flash_enabled", False))
            self.master_volume = float(data.get("master_volume", 1.0))
            
            def normalize(x):
                x = dict(x)
                x.setdefault("mode", "tone")
                x.setdefault("drum", "snare")
                x.setdefault("mp3_tick", "")
                x.setdefault("color", "#9CA3AF")
                x.setdefault("flash_color", x.get("color", "#9CA3AF"))  # Default to color if not set
                x.setdefault("accent_vol", 1.6)
                x.setdefault("uid", new_uid())
                return x
            
            self.left = [make_layer(**normalize(x)) for x in data.get("left", [])]
            self.right = [make_layer(**normalize(x)) for x in data.get("right", [])]

# ---------------- Metronome Engine ---------------- #

class SimpleMetronomeEngine:
    """Audio engine for Android with multiple layers and drum support"""
    
    def __init__(self, rhythm_state, on_beat_callback=None):
        self.state = rhythm_state
        self.on_beat_callback = on_beat_callback
        self.tone_gen = ToneGenerator()
        self.drum_synth = DrumSynth()
        self.mp3_ticks = Mp3TickCache()
        
        self.running = False
        self.thread = None
        self._lock = threading.RLock()
        
        # Try to import audio playback library
        self.audio_lib = None
        
        # On Android, try pyjnius AudioTrack first (most reliable)
        if platform == 'android':
            try:
                from jnius import autoclass
                AudioTrack = autoclass('android.media.AudioTrack')
                AudioManager = autoclass('android.media.AudioManager')
                AudioFormat = autoclass('android.media.AudioFormat')
                
                self.AudioTrack = AudioTrack
                self.AudioManager = AudioManager
                self.AudioFormat = AudioFormat
                self.audio_lib = 'android'
                print(f"[audio] Using Android AudioTrack for playback")
            except Exception as e:
                print(f"[audio] Could not load Android AudioTrack: {e}")
        
        # Try simpleaudio (desktop/some Android builds with it pre-installed)
        if self.audio_lib is None:
            try:
                import simpleaudio as sa
                self.sa = sa
                self.audio_lib = 'simpleaudio'
                print(f"[audio] Using simpleaudio for playback")
            except ImportError as e:
                print(f"[audio] Could not load simpleaudio: {e}")
        
        # Fallback to Kivy audio
        if self.audio_lib is None:
            try:
                from kivy.core.audio import SoundLoader
                self.SoundLoader = SoundLoader
                self.audio_lib = 'kivy'
                self.temp_audio_files = {}  # Cache for temporary audio files
                print(f"[audio] Using Kivy SoundLoader for playback")
            except ImportError:
                print("Warning: No audio playback library available")
                self.audio_lib = None
        
    def start(self):
        """Start the metronome"""
        if self.running:
            return
        
        # Allow starting even with no layers - just won't play any sounds
        # This lets users add layers while running
        
        self.running = True
        
        # Start the metronome thread
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop the metronome"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None
    
    def _get_audio_data(self, layer, is_accent=False):
        """Get audio data for a layer based on its mode"""
        mode = layer.get("mode", "tone")
        
        if mode == "mp3_tick" and layer.get("mp3_tick"):
            try:
                data = self.mp3_ticks.get(layer["mp3_tick"], is_accent=is_accent)
                if data is not None:
                    return data
            except Exception as e:
                print(f"[audio] Failed to load MP3 tick: {e}")
        
        if mode == "drum":
            drum_name = layer.get("drum", "snare")
            return self.drum_synth.get(drum_name)
        else:  # tone mode (fallback)
            freq = float(layer.get("freq", 880.0))
            return self.tone_gen.generate_beep(freq, duration_ms=50)
    
    def _play_sound(self, audio_data, volume=1.0, channel='center'):
        """Play audio data using available library"""
        if self.audio_lib is None:
            # No audio library available, skip playback
            return
        
        # Apply volume and clip
        audio_data = audio_data * volume
        audio_data = np.clip(audio_data, -1.0, 1.0)
        
        # Create stereo from mono
        if channel == 'left':
            stereo = np.column_stack([audio_data, audio_data * 0.0])
        elif channel == 'right':
            stereo = np.column_stack([audio_data * 0.0, audio_data])
        else:  # center
            stereo = np.column_stack([audio_data, audio_data])
        
        if self.audio_lib == 'android':
            try:
                # Convert to int16 for Android AudioTrack
                audio_int16 = (stereo * 32767.0).astype(np.int16)
                
                # Get the actual data size in bytes
                audio_bytes = audio_int16.tobytes()
                data_size = len(audio_bytes)
                
                # Get minimum buffer size required by AudioTrack
                min_buffer_size = self.AudioTrack.getMinBufferSize(
                    SAMPLE_RATE,
                    self.AudioFormat.CHANNEL_OUT_STEREO,
                    self.AudioFormat.ENCODING_PCM_16BIT
                )
                
                # Use the larger of minimum required or actual data size
                buffer_size = max(min_buffer_size, data_size)
                
                # Create AudioTrack with MODE_STREAM for better compatibility
                audio_track = self.AudioTrack(
                    self.AudioManager.STREAM_MUSIC,
                    SAMPLE_RATE,
                    self.AudioFormat.CHANNEL_OUT_STEREO,
                    self.AudioFormat.ENCODING_PCM_16BIT,
                    buffer_size,
                    self.AudioTrack.MODE_STREAM
                )
                
                # Initialize the AudioTrack before writing
                if hasattr(audio_track, 'getState'):
                    state = audio_track.getState()
                    if state != self.AudioTrack.STATE_INITIALIZED:
                        print(f"Warning: AudioTrack not properly initialized (state: {state})")
                        return
                
                # Write audio data and play
                audio_track.write(audio_bytes, 0, data_size)
                audio_track.play()
                
                # Schedule release after playback
                # Calculate duration and schedule cleanup
                duration_ms = int((len(audio_int16) / SAMPLE_RATE) * 1000) + 100
                Clock.schedule_once(lambda dt: audio_track.release() if hasattr(audio_track, 'release') else None, duration_ms / 1000.0)
            except Exception as e:
                print(f"Android audio playback error: {e}")
                
        elif self.audio_lib == 'simpleaudio':
            try:
                audio_int16 = (stereo * 32767.0).astype(np.int16)
                play_obj = self.sa.play_buffer(audio_int16, 2, 2, SAMPLE_RATE)
            except Exception as e:
                print(f"simpleaudio playback error: {e}")
                
        elif self.audio_lib == 'kivy':
            try:
                # Kivy SoundLoader requires file-based audio
                # We'll save to a temporary WAV file and play it
                import tempfile
                import wave
                
                # Create a unique hash based on stereo audio data
                # This allows caching the same sound for reuse
                audio_hash = hash(stereo.tobytes())
                
                # Check cache
                if audio_hash not in self.temp_audio_files:
                    # Create temporary WAV file
                    with tempfile.NamedTemporaryFile(mode='wb', suffix='.wav', delete=False) as f:
                        temp_path = f.name
                        
                        # Write WAV file
                        with wave.open(f, 'wb') as wav:
                            wav.setnchannels(2)  # Stereo
                            wav.setsampwidth(2)  # 16-bit
                            wav.setframerate(SAMPLE_RATE)
                            
                            # Convert to int16 and write
                            audio_int16 = (stereo * 32767.0).astype(np.int16)
                            wav.writeframes(audio_int16.tobytes())
                        
                        self.temp_audio_files[audio_hash] = temp_path
                
                # Load and play the cached sound
                sound = self.SoundLoader.load(self.temp_audio_files[audio_hash])
                if sound:
                    sound.play()
                else:
                    print(f"[audio] Failed to load sound file")
            except Exception as e:
                print(f"Kivy audio playback error: {e}")
    
    def _run(self):
        """Main metronome loop with multiple layers and accent support"""
        with self.state._lock:
            bpm = self.state.bpm
            beats_per_measure = self.state.beats_per_measure
            
            # Calculate intervals for each layer
            left_layers = [dict(layer) for layer in self.state.left]
            right_layers = [dict(layer) for layer in self.state.right]
            
            # Calculate interval in seconds for each layer
            def calc_interval(subdiv):
                notes_per_beat = subdiv / 4.0
                return 60.0 / (bpm * notes_per_beat)
            
            left_intervals = [calc_interval(layer["subdiv"]) for layer in left_layers]
            right_intervals = [calc_interval(layer["subdiv"]) for layer in right_layers]
        
        # Calculate measure duration for accent detection
        measure_duration = (60.0 / bpm) * beats_per_measure
        
        start_time = time.time()
        left_next_times = [0.0] * len(left_layers)
        right_next_times = [0.0] * len(right_layers)
        
        # Track beat counts for accent detection
        left_beat_counts = [0] * len(left_layers)
        right_beat_counts = [0] * len(right_layers)
        
        while self.running:
            current_time = time.time() - start_time
            
            # Check left layers
            for i, layer in enumerate(left_layers):
                if not layer.get("mute", False) and current_time >= left_next_times[i]:
                    # Determine if this is an accent beat (first beat of measure)
                    is_accent = (left_beat_counts[i] % beats_per_measure) == 0
                    
                    # Get audio data
                    audio_data = self._get_audio_data(layer, is_accent=is_accent)
                    
                    # Apply volume with accent if it's first beat and master volume
                    base_volume = float(layer.get("vol", 1.0))
                    accent_multiplier = float(layer.get("accent_vol", 1.6)) if is_accent else 1.0
                    master_volume = float(self.state.master_volume)
                    volume = base_volume * accent_multiplier * master_volume
                    
                    self._play_sound(audio_data, volume, 'left')
                    
                    # Trigger visual callback
                    if self.on_beat_callback:
                        uid = layer.get("uid")
                        flash_color = layer.get("flash_color", layer.get("color", "#3B82F6"))
                        Clock.schedule_once(lambda dt, u=uid, c=flash_color: self.on_beat_callback('left', u, c), 0)
                    
                    left_next_times[i] += left_intervals[i]
                    left_beat_counts[i] += 1
            
            # Check right layers
            for i, layer in enumerate(right_layers):
                if not layer.get("mute", False) and current_time >= right_next_times[i]:
                    # Determine if this is an accent beat (first beat of measure)
                    is_accent = (right_beat_counts[i] % beats_per_measure) == 0
                    
                    # Get audio data
                    audio_data = self._get_audio_data(layer, is_accent=is_accent)
                    
                    # Apply volume with accent if it's first beat and master volume
                    base_volume = float(layer.get("vol", 1.0))
                    accent_multiplier = float(layer.get("accent_vol", 1.6)) if is_accent else 1.0
                    master_volume = float(self.state.master_volume)
                    volume = base_volume * accent_multiplier * master_volume
                    
                    self._play_sound(audio_data, volume, 'right')
                    
                    # Trigger visual callback
                    if self.on_beat_callback:
                        uid = layer.get("uid")
                        flash_color = layer.get("flash_color", layer.get("color", "#EF4444"))
                        Clock.schedule_once(lambda dt, u=uid, c=flash_color: self.on_beat_callback('right', u, c), 0)
                    
                    right_next_times[i] += right_intervals[i]
                    right_beat_counts[i] += 1
            
            # Small sleep to avoid busy waiting
            time.sleep(0.001)

# ---------------- UI Components ---------------- #

class LayerWidget(BoxLayout):
    """Widget for displaying and controlling a single layer"""
    
    def __init__(self, layer, side, on_change=None, on_delete=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = '100dp'  # Slightly taller for accent control
        self.padding = '5dp'
        self.spacing = '2dp'
        
        self.layer = layer
        self.side = side
        self.on_change = on_change
        self.on_delete_callback = on_delete
        
        # Set background color
        with self.canvas.before:
            color = layer.get("color", "#9CA3AF")
            # Convert hex to RGB
            r = int(color[1:3], 16) / 255.0
            g = int(color[3:5], 16) / 255.0
            b = int(color[5:7], 16) / 255.0
            self.bg_color = Color(r, g, b, 0.3)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)
        
        # Track base color for flashing
        self.base_rgba = (r, g, b, 0.3)
        self.flash_scheduled = None
        
        self._build_ui()
    
    def _update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos
    
    def flash(self, color=None, duration=0.12):
        """Flash the layer widget with the specified color"""
        if color is None:
            # Use flash_color if available, otherwise use regular color
            color = self.layer.get("flash_color", self.layer.get("color", "#9CA3AF"))
        
        # Parse hex color
        try:
            r = int(color[1:3], 16) / 255.0
            g = int(color[3:5], 16) / 255.0
            b = int(color[5:7], 16) / 255.0
            
            # Set flash color with full opacity
            self.bg_color.rgba = (r, g, b, 0.8)
            
            # Cancel any pending flash clear
            if self.flash_scheduled:
                self.flash_scheduled.cancel()
            
            # Schedule flash to clear after duration
            self.flash_scheduled = Clock.schedule_once(lambda dt: self._clear_flash(), duration)
        except (ValueError, IndexError):
            pass  # Invalid color, skip flash
    
    def _clear_flash(self):
        """Restore the base background color"""
        self.bg_color.rgba = self.base_rgba
    
    def _build_ui(self):
        # Row 1: [Mode][modeValue] / [subdivision] [Mute] [X]
        top_row = BoxLayout(size_hint_y=0.5, spacing='3dp')
        
        # Mode selector
        self.mode_spinner = Spinner(
            text=self.layer.get("mode", "tone"),
            values=SOUND_MODES,
            size_hint_x=0.15,
            font_size='12sp'
        )
        self.mode_spinner.bind(text=self._on_mode_change)
        top_row.add_widget(self.mode_spinner)
        
        # Mode value (frequency or drum)
        self.mode_value_container = BoxLayout(size_hint_x=0.25, spacing='2dp')
        self._build_mode_value()
        top_row.add_widget(self.mode_value_container)
        
        # Separator
        top_row.add_widget(Label(text="/", size_hint_x=0.05, font_size='16sp'))
        
        # Subdivision
        self.subdiv_spinner = Spinner(
            text=str(self.layer.get("subdiv", 4)),
            values=SUBDIV_OPTIONS,
            size_hint_x=0.15,
            font_size='12sp'
        )
        self.subdiv_spinner.bind(text=self._on_subdiv_change)
        top_row.add_widget(self.subdiv_spinner)
        
        # Mute button
        self.mute_button = ToggleButton(
            text="M",
            size_hint_x=0.15,
            font_size='12sp',
            state='down' if self.layer.get("mute", False) else 'normal'
        )
        self.mute_button.bind(state=self._on_mute_change)
        top_row.add_widget(self.mute_button)
        
        # Delete button
        delete_button = Button(
            text="X",
            size_hint_x=0.15,
            font_size='12sp',
            background_color=(0.8, 0.2, 0.2, 1)
        )
        delete_button.bind(on_press=lambda x: self.on_delete_callback(self.layer) if self.on_delete_callback else None)
        top_row.add_widget(delete_button)
        
        self.add_widget(top_row)
        
        # Row 2: [InactiveColor] [ActiveColor] [Volume slider]
        bottom_row = BoxLayout(size_hint_y=0.5, spacing='3dp')
        
        # Inactive color picker button
        self.color_button = Button(
            text="",
            size_hint_x=0.1,
            background_color=self._hex_to_rgba(self.layer.get("color", "#9CA3AF"))
        )
        self.color_button.bind(on_press=lambda x: self._open_color_picker("inactive"))
        bottom_row.add_widget(self.color_button)
        
        # Active/Flash color picker button
        self.flash_color_button = Button(
            text="",
            size_hint_x=0.1,
            background_color=self._hex_to_rgba(self.layer.get("flash_color", self.layer.get("color", "#9CA3AF")))
        )
        self.flash_color_button.bind(on_press=lambda x: self._open_color_picker("active"))
        bottom_row.add_widget(self.flash_color_button)
        
        # Volume label
        vol_label = Label(text="Vol:", size_hint_x=0.08, font_size='12sp')
        bottom_row.add_widget(vol_label)
        
        # Volume slider
        self.vol_slider = Slider(
            min=0.0,
            max=1.5,
            value=self.layer.get("vol", 1.0),
            size_hint_x=0.72
        )
        self.vol_slider.bind(value=self._on_vol_change)
        bottom_row.add_widget(self.vol_slider)
        
        self.add_widget(bottom_row)
        
        # Row 3: [Accent label] [Accent slider]
        accent_row = BoxLayout(size_hint_y=0.33, spacing='3dp')
        
        # Accent label
        accent_label = Label(text="Accent:", size_hint_x=0.2, font_size='11sp')
        accent_row.add_widget(accent_label)
        
        # Accent volume slider (multiplier for first beat)
        self.accent_slider = Slider(
            min=1.0,
            max=3.0,
            value=self.layer.get("accent_vol", 1.6),
            size_hint_x=0.8
        )
        self.accent_slider.bind(value=self._on_accent_change)
        accent_row.add_widget(self.accent_slider)
        
        self.add_widget(accent_row)
    
    def _build_mode_value(self):
        """Build the mode value widget (frequency input, drum selector, or mp3 tick selector)"""
        self.mode_value_container.clear_widgets()
        
        mode = self.layer.get("mode", "tone")
        
        if mode == "tone":
            self.freq_input = TextInput(
                text=str(int(self.layer.get("freq", 880))),
                multiline=False,
                input_filter='int',
                font_size='12sp',
                hint_text='Hz'
            )
            self.freq_input.bind(text=self._on_freq_change)
            self.mode_value_container.add_widget(self.freq_input)
        elif mode == "drum":
            self.drum_spinner = Spinner(
                text=self.layer.get("drum", "snare"),
                values=DRUM_CHOICES,
                font_size='12sp'
            )
            self.drum_spinner.bind(text=self._on_drum_change)
            self.mode_value_container.add_widget(self.drum_spinner)
        elif mode == "mp3_tick":
            mp3_choices = get_mp3_tick_choices()
            current_mp3 = self.layer.get("mp3_tick", "")
            if not mp3_choices:
                mp3_choices = ["(no ticks)"]
                current_mp3 = mp3_choices[0]
            elif current_mp3 not in mp3_choices and mp3_choices:
                current_mp3 = mp3_choices[0]
            
            self.mp3_spinner = Spinner(
                text=current_mp3,
                values=mp3_choices,
                font_size='12sp'
            )
            self.mp3_spinner.bind(text=self._on_mp3_change)
            self.mode_value_container.add_widget(self.mp3_spinner)
    
    def _hex_to_rgba(self, hex_color):
        """Convert hex color to RGBA tuple for Kivy"""
        try:
            if hex_color.startswith('#'):
                hex_color = hex_color[1:]
            if len(hex_color) == 3:
                hex_color = ''.join([c*2 for c in hex_color])
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
            return (r, g, b, 1)
        except (ValueError, IndexError):
            return (0.6, 0.6, 0.6, 1)
    
    def _open_color_picker(self, color_type):
        """Open color picker popup for inactive or active color"""
        from kivy.uix.colorpicker import ColorPicker
        
        content = BoxLayout(orientation='vertical', spacing='10dp', padding='10dp')
        
        # Get current color based on type
        if color_type == "active":
            current_color = self.layer.get("flash_color", self.layer.get("color", "#9CA3AF"))
        else:
            current_color = self.layer.get("color", "#9CA3AF")
        
        color_picker = ColorPicker(
            color=self._hex_to_rgba(current_color)
        )
        content.add_widget(color_picker)
        
        # Buttons
        button_box = BoxLayout(size_hint_y=0.2, spacing='10dp')
        
        title = 'Pick Active Color' if color_type == "active" else 'Pick Inactive Color'
        popup = Popup(title=title, content=content, size_hint=(0.9, 0.9))
        
        def on_ok(btn):
            # Convert RGBA to hex
            r, g, b, a = color_picker.color
            hex_color = '#{:02x}{:02x}{:02x}'.format(int(r*255), int(g*255), int(b*255))
            
            if color_type == "active":
                # Update flash color
                self.layer["flash_color"] = hex_color
                self.flash_color_button.background_color = color_picker.color
            else:
                # Update inactive color and background
                self.layer["color"] = hex_color
                self.color_button.background_color = color_picker.color
                
                # Update background color
                with self.canvas.before:
                    self.canvas.before.clear()
                    Color(r, g, b, 0.3)
                    self.rect = Rectangle(size=self.size, pos=self.pos)
                
                self.base_rgba = (r, g, b, 0.3)
            
            if self.on_change:
                self.on_change()
            popup.dismiss()
        
        def on_cancel(btn):
            popup.dismiss()
        
        ok_btn = Button(text='OK', size_hint_x=0.5)
        ok_btn.bind(on_press=on_ok)
        button_box.add_widget(ok_btn)
        
        cancel_btn = Button(text='Cancel', size_hint_x=0.5)
        cancel_btn.bind(on_press=on_cancel)
        button_box.add_widget(cancel_btn)
        
        content.add_widget(button_box)
        
        popup.open()
    
    def _on_mode_change(self, spinner, value):
        self.layer["mode"] = value
        self._build_mode_value()
        if self.on_change:
            self.on_change()
    
    def _on_subdiv_change(self, spinner, value):
        try:
            self.layer["subdiv"] = int(value)
            if self.on_change:
                self.on_change()
        except ValueError:
            pass
    
    def _on_mute_change(self, button, value):
        self.layer["mute"] = (value == 'down')
        if self.on_change:
            self.on_change()
    
    def _on_freq_change(self, input, value):
        try:
            if value:
                self.layer["freq"] = float(value)
                if self.on_change:
                    self.on_change()
        except ValueError:
            pass
    
    def _on_drum_change(self, spinner, value):
        self.layer["drum"] = value
        if self.on_change:
            self.on_change()
    
    def _on_mp3_change(self, spinner, value):
        self.layer["mp3_tick"] = value
        if self.on_change:
            self.on_change()
    
    def _on_vol_change(self, slider, value):
        self.layer["vol"] = value
        if self.on_change:
            self.on_change()
    
    def _on_accent_change(self, slider, value):
        self.layer["accent_vol"] = value
        if self.on_change:
            self.on_change()
    



class LayerListWidget(BoxLayout):
    """Widget for displaying a list of layers with add/remove"""
    
    def __init__(self, state, side, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = '5dp'
        self.spacing = '5dp'
        
        self.state = state
        self.side = side
        self.on_change = None
        
        # Track layer widgets by UID for flashing
        self.uid_to_widget = {}
        
        # Title
        title_box = BoxLayout(size_hint_y=None, height='40dp')
        title = Label(
            text=f"{side.upper()} Layers",
            font_size='18sp',
            bold=True,
            size_hint_x=0.7
        )
        title_box.add_widget(title)
        
        # Add button
        add_button = Button(
            text="+",
            size_hint_x=0.3,
            font_size='20sp',
            background_color=(0.2, 0.8, 0.2, 1)
        )
        add_button.bind(on_press=self._on_add_layer)
        title_box.add_widget(add_button)
        
        self.add_widget(title_box)
        
        # Scroll view for layers with darker background
        self.scroll = ScrollView(size_hint=(1, 1))
        
        # Add darker background to scroll area
        with self.scroll.canvas.before:
            Color(0.15, 0.15, 0.15, 1)  # Darker than main panel
            self.scroll_bg = Rectangle(size=self.scroll.size, pos=self.scroll.pos)
        self.scroll.bind(size=self._update_scroll_bg, pos=self._update_scroll_bg)
        
        self.layers_container = BoxLayout(orientation='vertical', size_hint_y=None, spacing='5dp')
        self.layers_container.bind(minimum_height=self.layers_container.setter('height'))
        self.scroll.add_widget(self.layers_container)
        self.add_widget(self.scroll)
        
        self.refresh()
    
    def _update_scroll_bg(self, *args):
        """Update scroll background rectangle size and position"""
        self.scroll_bg.size = self.scroll.size
        self.scroll_bg.pos = self.scroll.pos
    
    def refresh(self):
        self.layers_container.clear_widgets()
        self.uid_to_widget.clear()
        
        layers = self.state.left if self.side == "left" else self.state.right
        
        for layer in layers:
            layer_widget = LayerWidget(
                layer,
                self.side,
                on_change=self._notify_change,
                on_delete=self._on_delete_layer
            )
            self.layers_container.add_widget(layer_widget)
            
            # Track widget by UID for flashing
            uid = layer.get("uid")
            if uid:
                self.uid_to_widget[uid] = layer_widget
    
    def _on_add_layer(self, button):
        layers = self.state.left if self.side == "left" else self.state.right
        # Use random dark color for new layers, avoiding the last layer's color
        previous_color = layers[-1].get("color") if layers else None
        color = random_dark_color(previous_color=previous_color)
        new_layer = make_layer(subdiv=4, freq=880.0 if self.side == "left" else 440.0, vol=1.0, color=color)
        layers.append(new_layer)
        self.refresh()
        self._notify_change()
    
    def _on_delete_layer(self, layer):
        layers = self.state.left if self.side == "left" else self.state.right
        if layer in layers:
            layers.remove(layer)
            self.refresh()
            self._notify_change()
    
    def _notify_change(self):
        if self.on_change:
            self.on_change()
    
    def flash_uid(self, uid, color):
        """Flash the layer widget with the specified UID"""
        widget = self.uid_to_widget.get(uid)
        if widget:
            widget.flash(color)


class MetronomeWidget(BoxLayout):
    """Main metronome control widget"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = '10dp'
        self.spacing = '10dp'
        
        # Set a slightly lighter background for the main panel
        with self.canvas.before:
            Color(0.22, 0.22, 0.22, 1)  # Slightly lighter than default dark
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg_rect, pos=self._update_bg_rect)
        
        # Initialize state and engine
        self.state = RhythmState()
        self.engine = SimpleMetronomeEngine(self.state, on_beat_callback=self.on_beat)
        
        # Load autosave if exists
        self._load_autosave()
        
        # Build UI
        self._build_ui()
        
        # Bind to window size changes for orientation support
        Window.bind(on_resize=self.on_window_resize)
    
    def _update_bg_rect(self, *args):
        """Update background rectangle size and position"""
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos
    
    def on_window_resize(self, window, width, height):
        """Handle orientation changes"""
        # Rebuild UI for new orientation if needed
        pass
    
    def _build_ui(self):
        """Build the user interface"""
        
        # Title and BPM
        header = self._build_header()
        self.add_widget(header)
        
        # Layer lists (side by side)
        layers_section = BoxLayout(orientation='horizontal', spacing='10dp')
        
        # Left layers
        self.left_list = LayerListWidget(self.state, "left", size_hint_x=0.5)
        self.left_list.on_change = self._autosave
        layers_section.add_widget(self.left_list)
        
        # Right layers
        self.right_list = LayerListWidget(self.state, "right", size_hint_x=0.5)
        self.right_list.on_change = self._autosave
        layers_section.add_widget(self.right_list)
        
        self.add_widget(layers_section)
        
        # Control buttons
        controls = self._build_controls()
        self.add_widget(controls)
    

    def _build_header(self):
        """Build title and BPM controls"""
        header = BoxLayout(orientation='vertical', size_hint_y=None, height='180dp', spacing='2dp')
        
        # Title
        title = Label(text="PolyRhythm Metronome", font_size='24sp', bold=True, size_hint_y=0.25)
        header.add_widget(title)
        
        # BPM row
        bpm_row = BoxLayout(size_hint_y=0.3, spacing='5dp')
        bpm_row.add_widget(Label(text="BPM:", font_size='18sp', size_hint_x=0.2))
        
        self.bpm_value_label = Label(
            text=str(int(self.state.bpm)),
            font_size='24sp',
            bold=True,
            size_hint_x=0.3
        )
        bpm_row.add_widget(self.bpm_value_label)
        
        self.bpm_slider = Slider(
            min=40,
            max=240,
            value=self.state.bpm,
            step=1,
            size_hint_x=0.5
        )
        self.bpm_slider.bind(value=self.on_bpm_change)
        bpm_row.add_widget(self.bpm_slider)
        
        header.add_widget(bpm_row)
        
        # Master Volume row
        volume_row = BoxLayout(size_hint_y=0.3, spacing='5dp')
        volume_row.add_widget(Label(text="Master:", font_size='14sp', size_hint_x=0.2))
        
        self.volume_value_label = Label(
            text=f"{self.state.master_volume:.1f}x",
            font_size='18sp',
            bold=True,
            size_hint_x=0.3
        )
        volume_row.add_widget(self.volume_value_label)
        
        self.volume_slider = Slider(
            min=0.0,
            max=2.0,
            value=self.state.master_volume,
            step=0.1,
            size_hint_x=0.5
        )
        self.volume_slider.bind(value=self.on_master_volume_change)
        volume_row.add_widget(self.volume_slider)
        
        header.add_widget(volume_row)
        
        # BPM presets - all 8 buttons in one row, taller but thinner
        preset_grid = GridLayout(cols=8, size_hint_y=0.45, spacing='2dp', height='50dp')
        for bpm in BPM_PRESETS:
            btn = Button(text=str(bpm), font_size='20sp')
            btn.bind(on_press=lambda x, b=bpm: self.set_bpm(b))
            preset_grid.add_widget(btn)
        
        header.add_widget(preset_grid)
        
        return header
    
    def _build_controls(self):
        """Build play/stop and file operation controls"""
        controls = BoxLayout(orientation='vertical', size_hint_y=None, height='140dp', spacing='5dp')
        
        # Play/Stop button - taller
        self.play_button = Button(
            text="PLAY",
            font_size='24sp',
            size_hint_y=0.5,
            background_color=(0.2, 0.8, 0.2, 1)
        )
        self.play_button.bind(on_press=self.on_play_stop)
        controls.add_widget(self.play_button)
        
        # File operations and logs: [NEW][LOAD][SAVE] space [LOGS]
        file_box = BoxLayout(size_hint_y=0.5, spacing='5dp')
        
        new_btn = Button(text="NEW", font_size='14sp')
        new_btn.bind(on_press=self.on_new)
        file_box.add_widget(new_btn)
        
        load_btn = Button(text="LOAD", font_size='14sp')
        load_btn.bind(on_press=self.on_load)
        file_box.add_widget(load_btn)
        
        save_btn = Button(text="SAVE", font_size='14sp')
        save_btn.bind(on_press=self.on_save)
        file_box.add_widget(save_btn)
        
        # Spacer
        file_box.add_widget(Label(text='', size_hint_x=0.3))
        
        logs_btn = Button(
            text="LOGS",
            font_size='14sp',
            background_color=(0.3, 0.3, 0.8, 1)
        )
        logs_btn.bind(on_press=self.on_view_logs)
        file_box.add_widget(logs_btn)
        
        controls.add_widget(file_box)
        
        return controls
    
    # Event Handlers
    
    def on_bpm_change(self, instance, value):
        """Handle BPM slider change"""
        self.state.bpm = value
        self.bpm_value_label.text = str(int(value))
        self._autosave()
    
    def set_bpm(self, bpm):
        """Set BPM to a specific value"""
        self.bpm_slider.value = bpm
    
    def on_master_volume_change(self, instance, value):
        """Handle master volume slider change"""
        self.state.master_volume = value
        self.volume_value_label.text = f"{value:.1f}x"
        self._autosave()
    
    def on_play_stop(self, instance):
        """Handle play/stop button press"""
        if self.engine.running:
            self.engine.stop()
            self.play_button.text = "PLAY"
            self.play_button.background_color = (0.2, 0.8, 0.2, 1)
        else:
            self.engine.start()
            self.play_button.text = "STOP"
            self.play_button.background_color = (0.8, 0.2, 0.2, 1)
    
    def on_beat(self, side, uid, color):
        """Called when a beat occurs - flash the specific layer row"""
        # Flash the specific layer widget
        if side == 'left':
            self.left_list.flash_uid(uid, color)
        else:
            self.right_list.flash_uid(uid, color)
    
    def on_new(self, instance):
        """Create new rhythm pattern"""
        self.state.left.clear()
        self.state.right.clear()
        self.state.left.append(make_layer(subdiv=4, freq=880.0, vol=1.0, color="#3B82F6"))
        self.state.right.append(make_layer(subdiv=4, freq=440.0, vol=1.0, color="#EF4444"))
        self.left_list.refresh()
        self.right_list.refresh()
        self._autosave()
    
    def on_save(self, instance):
        """Handle save button press"""
        content = BoxLayout(orientation='vertical', spacing='10dp', padding='10dp')
        
        filename_input = TextInput(
            text="my_rhythm.json",
            multiline=False,
            size_hint=(1, 0.3)
        )
        content.add_widget(Label(text="Enter filename:", size_hint=(1, 0.3)))
        content.add_widget(filename_input)
        
        button_box = BoxLayout(size_hint=(1, 0.4), spacing='10dp')
        
        popup = Popup(title="Save Rhythm", content=content, size_hint=(0.8, 0.4))
        
        def do_save(instance):
            filename = filename_input.text
            if filename:
                self._save_rhythm(filename)
            popup.dismiss()
        
        save_button = Button(text="Save")
        save_button.bind(on_press=do_save)
        button_box.add_widget(save_button)
        
        cancel_button = Button(text="Cancel")
        cancel_button.bind(on_press=popup.dismiss)
        button_box.add_widget(cancel_button)
        
        content.add_widget(button_box)
        popup.open()
    
    def on_load(self, instance):
        """Handle load button press"""
        content = BoxLayout(orientation='vertical', spacing='10dp', padding='10dp')
        
        filename_input = TextInput(
            text="my_rhythm.json",
            multiline=False,
            size_hint=(1, 0.3)
        )
        content.add_widget(Label(text="Enter filename:", size_hint=(1, 0.3)))
        content.add_widget(filename_input)
        
        button_box = BoxLayout(size_hint=(1, 0.4), spacing='10dp')
        
        popup = Popup(title="Load Rhythm", content=content, size_hint=(0.8, 0.4))
        
        def do_load(instance):
            filename = filename_input.text
            if filename:
                self._load_rhythm(filename)
            popup.dismiss()
        
        load_button = Button(text="Load")
        load_button.bind(on_press=do_load)
        button_box.add_widget(load_button)
        
        cancel_button = Button(text="Cancel")
        cancel_button.bind(on_press=popup.dismiss)
        button_box.add_widget(cancel_button)
        
        content.add_widget(button_box)
        popup.open()
    
    def on_view_logs(self, instance):
        """Handle view logs button press"""
        content = BoxLayout(orientation='vertical', spacing='10dp', padding='10dp')
        
        # Get logs from the log capture
        logs_text = log_capture.get_logs()
        if not logs_text.strip():
            logs_text = "No logs available yet."
        
        # Create scrollable text input to display logs
        logs_display = TextInput(
            text=logs_text,
            multiline=True,
            readonly=True,
            size_hint=(1, 0.9),
            font_size='12sp',
            font_name='RobotoMono-Regular.ttf' if os.path.exists('RobotoMono-Regular.ttf') else 'DroidSansMono'
        )
        content.add_widget(logs_display)
        
        # Button box
        button_box = BoxLayout(size_hint=(1, 0.1), spacing='10dp')
        
        popup = Popup(title="Application Logs", content=content, size_hint=(0.95, 0.9))
        
        def refresh_logs(instance):
            """Refresh the log display"""
            logs_display.text = log_capture.get_logs()
        
        def copy_logs(instance):
            """Copy logs to clipboard (if available)"""
            try:
                from kivy.core.clipboard import Clipboard
                Clipboard.copy(log_capture.get_logs())
                # Show brief confirmation
                copy_btn.text = "Copied!"
                Clock.schedule_once(lambda dt: setattr(copy_btn, 'text', 'Copy'), 2)
            except Exception as e:
                print(f"Clipboard error: {e}")
        
        refresh_btn = Button(text="Refresh")
        refresh_btn.bind(on_press=refresh_logs)
        button_box.add_widget(refresh_btn)
        
        copy_btn = Button(text="Copy")
        copy_btn.bind(on_press=copy_logs)
        button_box.add_widget(copy_btn)
        
        close_button = Button(text="Close")
        close_button.bind(on_press=popup.dismiss)
        button_box.add_widget(close_button)
        
        content.add_widget(button_box)
        popup.open()
    
    # File Operations
    
    def _get_save_directory(self):
        """Get the appropriate save directory based on platform"""
        if platform == 'android':
            from android.storage import app_storage_path
            return app_storage_path()
        else:
            return os.path.expanduser("~")
    
    def _autosave(self):
        """Auto-save the current state"""
        try:
            save_dir = self._get_save_directory()
            filepath = os.path.join(save_dir, AUTOSAVE_FILE)
            with open(filepath, 'w') as f:
                json.dump(self.state.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Autosave error: {e}")
    
    def _load_autosave(self):
        """Load the autosaved state if it exists"""
        try:
            save_dir = self._get_save_directory()
            filepath = os.path.join(save_dir, AUTOSAVE_FILE)
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    self.state.from_dict(data)
        except Exception as e:
            print(f"Load autosave error: {e}")
    
    def _save_rhythm(self, filename):
        """Save rhythm to file"""
        try:
            save_dir = self._get_save_directory()
            if not filename.endswith('.json'):
                filename += '.json'
            filepath = os.path.join(save_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(self.state.to_dict(), f, indent=2)
            
            # Show success message
            popup = Popup(
                title="Success",
                content=Label(text=f"Saved to {filename}"),
                size_hint=(0.6, 0.3)
            )
            popup.open()
            Clock.schedule_once(lambda dt: popup.dismiss(), 2)
        except Exception as e:
            popup = Popup(
                title="Error",
                content=Label(text=f"Save failed: {str(e)}"),
                size_hint=(0.6, 0.3)
            )
            popup.open()
    
    def _load_rhythm(self, filename):
        """Load rhythm from file"""
        try:
            save_dir = self._get_save_directory()
            if not filename.endswith('.json'):
                filename += '.json'
            filepath = os.path.join(save_dir, filename)
            
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.state.from_dict(data)
            
            # Update UI
            self.bpm_slider.value = self.state.bpm
            self.volume_slider.value = self.state.master_volume
            self.left_list.refresh()
            self.right_list.refresh()
            
            popup = Popup(
                title="Success",
                content=Label(text=f"Loaded {filename}"),
                size_hint=(0.6, 0.3)
            )
            popup.open()
            Clock.schedule_once(lambda dt: popup.dismiss(), 2)
        except Exception as e:
            popup = Popup(
                title="Error",
                content=Label(text=f"Load failed: {str(e)}"),
                size_hint=(0.6, 0.3)
            )
            popup.open()

# ---------------- Main App ---------------- #

class PolyRhythmMetronomeApp(App):
    """Main Kivy application"""
    
    def build(self):
        """Build and return the root widget"""
        # Set window title (for desktop testing)
        self.title = "PolyRhythm Metronome"
        return MetronomeWidget()
    
    def on_stop(self):
        """Called when the app is closing"""
        # Stop the metronome engine
        root = self.root
        if hasattr(root, 'engine'):
            root.engine.stop()

# ---------------- Entry Point ---------------- #

if __name__ == '__main__':
    PolyRhythmMetronomeApp().run()
