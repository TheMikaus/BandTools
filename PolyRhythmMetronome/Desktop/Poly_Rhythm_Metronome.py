#!/usr/bin/env python3
"""
Stereo Subdivision Metronome — Compact UI + Live Updates + DrumSynth + Stable Flashing (UID)
- Compact top controls (stacked), small footprint.
- List boxes now have higher contrast: bordered container, light canvas background,
  alternating row stripes, stronger selection highlight.
- Multi-layers per ear with mute, move L<->R, per-layer color (flash optional, OFF by default).
- Modes per layer: Tone (freq), WAV file, or Drum (kick/snare/hihat/crash/tom/ride).
- Global accent factor for beat 1, adjustable.
- Real-time audio updates for add/remove/mute and global edits.
- Export stereo WAV; Save/Load rhythms (+ autosave).
- Streaming via sounddevice; simpleaudio fallback. Audio runs on its own thread.
"""

import sys, subprocess, importlib, traceback, math, time, uuid
import json, os, threading, wave
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, colorchooser
from collections import deque

# ---------------- Auto-install missing packages ---------------- #

def ensure_pkg(pkg_name: str, import_name: str = None):
    mod_name = import_name or pkg_name
    try:
        return importlib.import_module(mod_name)
    except ImportError as first_err:
        if getattr(sys, "frozen", False):
            # In frozen builds (PyInstaller, etc.), dependencies are already bundled
            raise first_err
        try:
            print(f"[setup] Installing '{pkg_name}' ...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg_name])
            return importlib.import_module(mod_name)
        except Exception as install_err:
            print(f"[setup] Failed to auto-install '{pkg_name}'. Error:\n{install_err}")
            raise first_err

np = ensure_pkg("numpy")
try: sd = ensure_pkg("sounddevice")
except ImportError: sd = None
try: sa = ensure_pkg("simpleaudio")
except ImportError: sa = None
try: pydub = ensure_pkg("pydub")
except ImportError: pydub = None

# ---------------- Constants ---------------- #

SAMPLE_RATE = 44100
BASE_AMP = 0.22
DEFAULT_ACCENT_FACTOR = 1.6
TOL = 1e-4
TOL_SAMPLES = 2
TOL_SAVE = 1e-6
FLASH_MS = 120

# ---------------- Helpers: timing ---------------- #

def notes_per_beat_from_input(n: int) -> float:
    if n in (1, 2, 4, 8, 16, 32, 64): return n/4.0
    if n > 0: return float(n)
    raise ValueError("Subdivision must be a positive integer.")

def interval_seconds(bpm: float, subdiv: int) -> float:
    if bpm <= 0: raise ValueError("BPM must be > 0.")
    return (60.0/bpm) / notes_per_beat_from_input(subdiv)

def measure_seconds(bpm: float, beats_per_measure: int) -> float:
    if beats_per_measure <= 0: raise ValueError("Beats per measure must be > 0.")
    return (60.0 / bpm) * float(beats_per_measure)

# ---------------- Audio sources ---------------- #

class ToneCache:
    def __init__(self, sr=SAMPLE_RATE, blip_ms=55, fade_ms=5):
        self.sr, self.blip_ms, self.fade_ms, self._c = sr, blip_ms, fade_ms, {}
    def get(self, freq: float):
        key = round(float(freq), 6)
        if key in self._c: return self._c[key]
        n = int(self.sr * (self.blip_ms/1000.0))
        t = np.arange(n, dtype=np.float32) / self.sr
        tone = np.sin(2*np.pi*key*t).astype(np.float32)
        fade_n = max(1, int(self.sr * (min(self.fade_ms, self.blip_ms/2)/1000.0)))
        env = np.ones(n, dtype=np.float32)
        env[:fade_n] = np.linspace(0.0, 1.0, fade_n, dtype=np.float32)
        env[-fade_n:] = np.linspace(1.0, 0.0, fade_n, dtype=np.float32)
        mono = tone * env
        self._c[key] = mono
        return mono

class WaveCache:
    def __init__(self, sr=SAMPLE_RATE): self.sr, self._c = sr, {}
    def get(self, path: str):
        if not path: return None
        key = os.path.abspath(path)
        if key in self._c: return self._c[key]
        if not os.path.exists(key): raise FileNotFoundError(f"Audio file not found: {key}")
        # Check if it's an MP3 file
        if key.lower().endswith('.mp3'):
            data, sr = self._read_mp3(key)
        else:
            data, sr = self._read_wav_any(key)
        if sr != self.sr: data = self._resample_linear(data, sr, self.sr)
        self._c[key] = data.astype(np.float32, copy=False); return self._c[key]
    @staticmethod
    def _read_mp3(path):
        """Read MP3 file using pydub"""
        if pydub is None:
            raise ImportError("pydub is required for MP3 support. Install with: pip install pydub")
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_mp3(path)
            # Convert to mono
            if audio.channels > 1:
                audio = audio.set_channels(1)
            # Get raw data
            samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
            # Normalize based on sample width
            if audio.sample_width == 1:
                samples = (samples - 128.0) / 128.0
            elif audio.sample_width == 2:
                samples = samples / 32768.0
            elif audio.sample_width == 4:
                samples = samples / 2147483648.0
            return samples, audio.frame_rate
        except Exception as e:
            raise RuntimeError(f"Failed to read MP3 file {path}: {e}")
    @staticmethod
    def _read_wav_any(path):
        with wave.open(path, 'rb') as wf:
            ch = wf.getnchannels(); sw = wf.getsampwidth(); fr = wf.getframerate(); nf = wf.getnframes()
            raw = wf.readframes(nf)
        if sw == 1:
            data = np.frombuffer(raw, dtype=np.uint8).astype(np.float32); data = (data-128.0)/128.0
        elif sw == 2:
            data = np.frombuffer(raw, dtype=np.int16).astype(np.float32)/32768.0
        elif sw == 4:
            arr = np.frombuffer(raw, dtype=np.int32)
            data = np.frombuffer(raw, dtype=np.float32) if np.max(np.abs(arr)) < 1e6 else arr.astype(np.float32)/2147483648.0
        else:
            raise ValueError("Only 8/16/32-bit or float32 WAV supported.")
        if ch > 1: data = data.reshape(-1, ch).mean(axis=1)
        return data.astype(np.float32, copy=False), fr
    @staticmethod
    def _resample_linear(x, sr_from, sr_to):
        if sr_from == sr_to or len(x) == 0: return x
        dur = len(x)/float(sr_from); new_len = int(round(dur*sr_to))
        if new_len <= 1: return np.zeros(1, dtype=np.float32)
        xp = np.linspace(0.0,1.0,len(x),dtype=np.float32); xnew = np.linspace(0.0,1.0,new_len,dtype=np.float32)
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
                # Check if corresponding _1 exists (shouldn't happen if _1 was processed first)
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

class DrumSynth:
    def __init__(self, sr=SAMPLE_RATE): self.sr, self._c = sr, {}
    def get(self, name: str):
        key = (name or "").lower()
        if key in self._c: return self._c[key]
        fn = getattr(self, f"_make_{key}", None); data = fn() if fn else self._make_snare()
        self._c[key] = data; return data
    def _make_kick(self):
        sr=self.sr; dur=0.25; n=int(sr*dur); t=np.arange(n,dtype=np.float32)/sr
        f0,f1=120.0,50.0; k=np.log(f1/f0)/dur; phase=2*np.pi*(f0*(np.expm1(k*t)/k))
        tone=np.sin(phase).astype(np.float32); env=np.exp(-t/0.15).astype(np.float32); click=np.exp(-t/0.01)
        return (0.9*tone*env+0.05*click).astype(np.float32)
    def _make_snare(self):
        sr=self.sr; dur=0.3; n=int(sr*dur); t=np.arange(n,dtype=np.float32)/sr
        noise=np.random.uniform(-1,1,size=n).astype(np.float32); env_n=np.exp(-t/0.12).astype(np.float32)
        body=np.sin(2*np.pi*190*t).astype(np.float32)*np.exp(-t/0.1); return (0.8*noise*env_n+0.25*body).astype(np.float32)
    def _make_hihat(self):
        sr=self.sr; dur=0.08; n=int(sr*dur); t=np.arange(n,dtype=np.float32)/sr
        noise=np.random.uniform(-1,1,size=n).astype(np.float32); env=np.exp(-t/0.03).astype(np.float32)
        return (noise*env).astype(np.float32)
    def _make_crash(self):
        sr=self.sr; dur=1.2; n=int(sr*dur); t=np.arange(n,dtype=np.float32)/sr
        noise=np.random.uniform(-1,1,size=n).astype(np.float32); env=np.exp(-t/0.6).astype(np.float32)
        return (0.6*noise*env).astype(np.float32)
    def _make_tom(self):
        sr=self.sr; dur=0.4; n=int(sr*dur); t=np.arange(n,dtype=np.float32)/sr
        tone=np.sin(2*np.pi*160.0*t).astype(np.float32); env=np.exp(-t/0.25).astype(np.float32)
        return (tone*env).astype(np.float32)
    def _make_ride(self):
        sr=self.sr; dur=0.9; n=int(sr*dur); t=np.arange(n,dtype=np.float32)/sr
        ping=np.sin(2*np.pi*900*t).astype(np.float32)*np.exp(-t/0.4); noise=np.random.uniform(-1,1,size=n).astype(np.float32)*np.exp(-t/0.8)*0.2
        return (0.8*ping+noise).astype(np.float32)

def float_to_int16(stereo: np.ndarray) -> np.ndarray:
    stereo = np.clip(stereo, -1.0, 1.0); return (stereo * 32767.0).astype(np.int16)

def tanh_soft_clip(x: np.ndarray) -> np.ndarray:
    """Soft clip audio using tanh to prevent harsh digital clipping"""
    a = 2.0
    return np.tanh(a * x) / np.tanh(a)

# ---------------- Lock-free Ring Buffer ---------------- #

class FloatRingBuffer:
    """Lock-free-ish single-producer single-consumer ring buffer for float mono frames"""
    def __init__(self, capacity_frames: int):
        self.buf = np.zeros(capacity_frames, dtype=np.float32)
        self.capacity = capacity_frames
        # Use separate read/write indices (volatile in nature due to GIL)
        self._read_idx = 0
        self._write_idx = 0
    
    def push(self, src: np.ndarray) -> int:
        """Push frames into buffer, returns number of frames actually written"""
        frames = len(src)
        space = self.free_space()
        n = min(frames, space)
        if n <= 0:
            return 0
        
        w = self._write_idx
        # Handle wrap-around
        first_chunk = min(n, self.capacity - w)
        self.buf[w:w + first_chunk] = src[:first_chunk]
        if n > first_chunk:
            self.buf[0:n - first_chunk] = src[first_chunk:n]
        
        self._write_idx = (w + n) % self.capacity
        return n
    
    def pop(self, dst: np.ndarray, frames: int) -> int:
        """Pop frames from buffer into dst, returns number of frames actually read"""
        avail = self.available()
        n = min(frames, avail)
        
        r = self._read_idx
        # Handle wrap-around
        first_chunk = min(n, self.capacity - r)
        dst[:first_chunk] = self.buf[r:r + first_chunk]
        if n > first_chunk:
            dst[first_chunk:n] = self.buf[0:n - first_chunk]
        
        # Pad with zeros if we don't have enough data
        if n < frames:
            dst[n:frames] = 0.0
        
        self._read_idx = (r + n) % self.capacity
        return n
    
    def available(self) -> int:
        """Number of frames available to read"""
        return (self._write_idx - self._read_idx + self.capacity) % self.capacity
    
    def free_space(self) -> int:
        """Number of frames available to write"""
        return self.capacity - 1 - self.available()

# ---------------- Data model ---------------- #

def new_uid(): return uuid.uuid4().hex

def random_dark_color():
    """Generate a random dark color suitable for inactive layer background"""
    import random
    # Generate RGB values in the range 40-120 to ensure dark but visible colors
    r = random.randint(40, 120)
    g = random.randint(40, 120)
    b = random.randint(40, 120)
    return f"#{r:02x}{g:02x}{b:02x}"

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

def make_layer(subdiv=4, freq=880.0, vol=1.0, mute=False, mode="tone", wav_path="", drum="snare", mp3_tick="", color="#9CA3AF", flash_color=None, uid=None):
    # Auto-generate flash_color if not provided
    if flash_color is None:
        flash_color = brighten_color(color)
    return {"uid": uid or new_uid(),
            "subdiv": int(subdiv), "freq": float(freq), "vol": float(vol), "mute": bool(mute),
            "mode": mode, "wav_path": wav_path, "drum": drum, "mp3_tick": mp3_tick, "color": color, "flash_color": flash_color}

class RhythmState:
    def __init__(self):
        self.bpm = 120.0; self.beats_per_measure = 4; self.accent_factor = DEFAULT_ACCENT_FACTOR
        self.left=[]; self.right=[]; self.flash_enabled=False; self._lock=threading.RLock()
    def to_dict(self):
        with self._lock:
            return {"bpm": self.bpm, "beats_per_measure": self.beats_per_measure, "accent_factor": self.accent_factor,
                    "flash_enabled": self.flash_enabled, "left": self.left, "right": self.right}
    def from_dict(self, d):
        with self._lock:
            self.bpm=float(d.get("bpm",120.0)); self.beats_per_measure=int(d.get("beats_per_measure",4))
            self.accent_factor=float(d.get("accent_factor",DEFAULT_ACCENT_FACTOR)); self.flash_enabled=bool(d.get("flash_enabled",False))
            def normalize(x):
                x=dict(x); x.setdefault("mode","tone"); x.setdefault("wav_path",""); x.setdefault("drum","snare")
                x.setdefault("mp3_tick",""); x.setdefault("color","#9CA3AF"); x.setdefault("uid", new_uid())
                # Set flash_color if not present
                if "flash_color" not in x:
                    x["flash_color"] = brighten_color(x["color"])
                return x
            self.left=[make_layer(**normalize(x)) for x in d.get("left",[])]
            self.right=[make_layer(**normalize(x)) for x in d.get("right",[])]

# ---------------- Audio engine (streaming) ---------------- #

class StreamEngine:
    def __init__(self, rhythm_state, ui_after_callable, event_notify):
        self.rhythm=rhythm_state; self.ui_after=ui_after_callable; self.event_notify=event_notify
        self.stream=None
        self.running=False
        self.tones=ToneCache(); self.waves=WaveCache(); self.drums=DrumSynth(); self.mp3_ticks=Mp3TickCache()
        self._lock=threading.RLock()
        self.left_layers=[]; self.right_layers=[]; self.L_intervals=[]; self.R_intervals=[]; self.L_next=[]; self.R_next=[]
        self.measure_samples=0; self.sample_counter=0; self.accent_factor=DEFAULT_ACCENT_FACTOR; self.flash_enabled=False
        self.active=[]; self._sa_start_time=None
    def _log_exception(self, context_msg: str):
        """Log exception with timestamp and context information."""
        try:
            with open("metronome_log.txt", "a", encoding="utf-8") as f:
                f.write("\n" + "="*70 + "\n")
                f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
                f.write(f"Context: {context_msg}\n")
                f.write(f"Running: {self.running}\n")
                f.write(f"Left layers: {len(self.left_layers)} (muted: {sum(1 for l in self.left_layers if l.get('mute', False))})\n")
                f.write(f"Right layers: {len(self.right_layers)} (muted: {sum(1 for l in self.right_layers if l.get('mute', False))})\n")
                f.write(f"Active sounds: {len(self.active)}\n")
                f.write("-"*70 + "\n")
                traceback.print_exc(file=f)
                f.write("="*70 + "\n")
        except Exception:
            # Fallback if logging fails
            print(f"Failed to write to log: {context_msg}", file=sys.stderr)
            traceback.print_exc()
    
    def _notify_error(self, msg:str):
        def cb():
            try: messagebox.showerror("Audio Error", msg)
            except Exception: print("Audio Error:", msg, file=sys.stderr)
        try: self.ui_after(cb)
        except Exception: print("Audio Error:", msg, file=sys.stderr)
    def is_playing(self): return self.running
    def update_live_from_state(self):
        if not self.is_playing(): return
        with self.rhythm._lock:
            bpm=float(self.rhythm.bpm); beats=int(self.rhythm.beats_per_measure)
            self.accent_factor=float(self.rhythm.accent_factor); self.flash_enabled=bool(self.rhythm.flash_enabled)
            new_left=[dict(x) for x in self.rhythm.left]; new_right=[dict(x) for x in self.rhythm.right]
        t_cur = self.sample_counter/float(SAMPLE_RATE) if self.stream is not None else (0.0 if self._sa_start_time is None else time.perf_counter()-self._sa_start_time)
        meas_len=measure_seconds(bpm, beats)
        with self._lock:
            def recalc(layers):
                intervals=[interval_seconds(bpm, lay["subdiv"]) for lay in layers]
                next_times=[]
                for iv in intervals:
                    if iv<=0: iv=1e9
                    k=math.ceil((t_cur-1e-9)/iv); k=0 if k<0 else k
                    next_times.append(k*iv)
                return layers, intervals, next_times
            self.left_layers,self.L_intervals,self.L_next = recalc(new_left)
            self.right_layers,self.R_intervals,self.R_next = recalc(new_right)
            self.measure_samples=int(round(measure_seconds(bpm, beats)*SAMPLE_RATE)) if meas_len>0 else 0
        # Pre-load any new audio files that were added during playback
        self._preload_audio_files()
    def _preload_audio_files(self):
        """Pre-load all wave/mp3 files into cache before starting playback.
        This prevents disk I/O delays during audio callbacks that cause timing issues."""
        for lay in self.left_layers + self.right_layers:
            mode = lay.get("mode", "tone")
            try:
                if mode == "mp3_tick" and lay.get("mp3_tick"):
                    # Pre-load both accent and non-accent versions
                    self.mp3_ticks.get(lay["mp3_tick"], is_accent=True)
                    self.mp3_ticks.get(lay["mp3_tick"], is_accent=False)
                elif mode == "file" and lay.get("wav_path"):
                    # Pre-load wav file
                    self.waves.get(lay["wav_path"])
            except Exception as e:
                # Log but don't fail - the error will be caught during playback
                print(f"Warning: Failed to preload audio for layer: {e}", file=sys.stderr)
    
    def start(self):
        if self.running: return
        with self.rhythm._lock:
            bpm=float(self.rhythm.bpm); beats=int(self.rhythm.beats_per_measure)
            self.accent_factor=float(self.rhythm.accent_factor); self.flash_enabled=bool(self.rhythm.flash_enabled)
            self.left_layers=[dict(x) for x in self.rhythm.left]; self.right_layers=[dict(x) for x in self.rhythm.right]
        if not self.left_layers and not self.right_layers:
            self._notify_error("No layers added. Add layers to Left or Right and try Play."); return
        self.measure_samples=int(round(measure_seconds(bpm, beats)*SAMPLE_RATE))
        def mk_side(layers): intervals=[interval_seconds(bpm, lay["subdiv"]) for lay in layers]; return intervals,[0.0 for _ in layers]
        self.L_intervals,self.L_next = mk_side(self.left_layers); self.R_intervals,self.R_next = mk_side(self.right_layers)
        self.sample_counter=0; self.active.clear()
        # Pre-load all audio files to prevent timing issues on first play
        self._preload_audio_files()
        if sd is not None:
            try:
                self.stream=sd.OutputStream(samplerate=SAMPLE_RATE, channels=2, dtype='float32', callback=self._callback, blocksize=0)
                self.stream.start(); self.running=True; return
            except Exception as e:
                self._notify_error(f"sounddevice stream failed ({e}). Falling back to simpleaudio."); self.stream=None
        if sa is None:
            try: globals()['sa']=ensure_pkg("simpleaudio")
            except ImportError: self._notify_error("Neither 'sounddevice' nor 'simpleaudio' are available."); return
        self.running=True; self._sa_start_time=time.perf_counter()
        threading.Thread(target=self._sa_loop, name="SA-Loop", daemon=True).start()
    def stop(self):
        self.running=False
        if self.stream is not None:
            try: self.stream.stop(); self.stream.close()
            except Exception: pass
            self.stream=None
        with self._lock: self.active.clear()
    def _amp_and_source(self, lay, accent: bool):
        amp = BASE_AMP * float(lay["vol"]) * (self.accent_factor if accent else 1.0)
        mode = lay.get("mode","tone")
        if mode=="mp3_tick" and lay.get("mp3_tick"):
            try: 
                data = self.mp3_ticks.get(lay["mp3_tick"], is_accent=accent)
                if data is not None:
                    return amp, data
            except Exception: pass
        if mode=="file" and lay.get("wav_path"):
            try: return amp, self.waves.get(lay["wav_path"])
            except Exception: pass
        if mode=="drum": return amp, self.drums.get(lay.get("drum","snare"))
        return amp, self.tones.get(float(lay.get("freq",880.0)))
    def _callback(self, outdata, frames, time_info, status):
        try:
            block = np.zeros((frames,2), dtype=np.float32); sr=SAMPLE_RATE; t0=self.sample_counter; t1=t0+frames
            def schedule_side(layers, intervals, next_times, channel):
                for i, lay in enumerate(layers):
                    if lay.get("mute",False): continue
                    iv=intervals[i]
                    while True:
                        t_sec=next_times[i]; ev_sample=int(round(t_sec*sr))
                        if ev_sample>=t1: break
                        if ev_sample>=t0:
                            accent=False
                            if self.measure_samples>0:
                                r=ev_sample%self.measure_samples; accent = (r<=TOL_SAMPLES or (self.measure_samples-r)<=TOL_SAMPLES)
                            amp,data=self._amp_and_source(lay, accent)
                            self.active.append({"data":data,"idx":0,"amp":amp,"channel":channel})
                            if self.flash_enabled and self.event_notify is not None:
                                self.event_notify("L" if channel==0 else "R", lay.get("uid"), lay.get("flash_color", lay.get("color","#9CA3AF")))
                        next_times[i]=t_sec+iv
            with self._lock:
                L_layers,R_layers = self.left_layers, self.right_layers
                L_intv,R_intv     = self.L_intervals, self.R_intervals
                L_next,R_next     = self.L_next, self.R_next
            schedule_side(L_layers, L_intv, L_next, 0)
            schedule_side(R_layers, R_intv, R_next, 1)
            new_active=[]
            for blip in self.active:
                data, ch, amp, idx = blip["data"], blip["channel"], blip["amp"], blip["idx"]
                remain=data.shape[0]-idx
                if remain<=0: continue
                n=min(remain, frames); block[:n, ch]+=amp*data[idx:idx+n]; blip["idx"]+=n
                if blip["idx"]<data.shape[0]: new_active.append(blip)
            # Apply soft clipping to prevent harsh digital clipping from mixing
            block[:, 0] = tanh_soft_clip(block[:, 0])
            block[:, 1] = tanh_soft_clip(block[:, 1])
            self.active=new_active; outdata[:]=block; self.sample_counter+=frames
        except Exception:
            self._log_exception("Exception in sounddevice callback")
            outdata[:]=0; return
    def _sa_loop(self):
        try:
            sr=SAMPLE_RATE; handles=deque(maxlen=512); start=self._sa_start_time or time.perf_counter()
            while self.running:
                with self._lock:
                    candidates=[]; 
                    if self.L_next: candidates.append(min(self.L_next))
                    if self.R_next: candidates.append(min(self.R_next))
                    if not candidates: time.sleep(0.01); continue
                    next_t=min(candidates); left_events=[]; right_events=[]
                    for i,t_ev in enumerate(self.L_next):
                        if abs(t_ev-next_t)<TOL:
                            if i<len(self.left_layers):
                                lay=self.left_layers[i]
                                if not lay.get("mute",False):
                                    ev_sample=int(round(t_ev*sr)); accent=False
                                    if self.measure_samples>0:
                                        r=ev_sample%self.measure_samples; accent=(r<=TOL_SAMPLES or (self.measure_samples-r)<=TOL_SAMPLES)
                                    amp,data=self._amp_and_source(lay, accent)
                                    left_events.append((amp,data,lay.get("uid"),lay.get("flash_color", lay.get("color","#9CA3AF"))))
                            self.L_next[i]=t_ev+self.L_intervals[i]
                    for i,t_ev in enumerate(self.R_next):
                        if abs(t_ev-next_t)<TOL:
                            if i<len(self.right_layers):
                                lay=self.right_layers[i]
                                if not lay.get("mute",False):
                                    ev_sample=int(round(t_ev*sr)); accent=False
                                    if self.measure_samples>0:
                                        r=ev_sample%self.measure_samples; accent=(r<=TOL_SAMPLES or (self.measure_samples-r)<=TOL_SAMPLES)
                                    amp,data=self._amp_and_source(lay, accent)
                                    right_events.append((amp,data,lay.get("uid"),lay.get("flash_color", lay.get("color","#9CA3AF"))))
                            self.R_next[i]=t_ev+self.R_intervals[i]
                target=start+next_t
                while True:
                    now=time.perf_counter(); dt=target-now
                    if dt<=0: break
                    time.sleep(min(0.001, dt))
                max_len=0
                for amp,data,*_ in left_events+right_events: max_len=max(max_len, data.shape[0])
                if max_len==0: time.sleep(0.0005); continue
                frame=np.zeros((max_len,2), dtype=np.float32)
                for amp,data,uid,flash_color in left_events:
                    L=min(max_len, data.shape[0]); frame[:L,0]+=amp*data[:L]
                    if self.flash_enabled and self.event_notify is not None: self.event_notify("L", uid, flash_color)
                for amp,data,uid,flash_color in right_events:
                    L=min(max_len, data.shape[0]); frame[:L,1]+=amp*data[:L]
                    if self.flash_enabled and self.event_notify is not None: self.event_notify("R", uid, flash_color)
                # Apply soft clipping to prevent harsh digital clipping from mixing
                frame[:, 0] = tanh_soft_clip(frame[:, 0])
                frame[:, 1] = tanh_soft_clip(frame[:, 1])
                int16=(frame*32767.0).astype(np.int16)
                try: h=sa.play_buffer(int16,2,2,sr)
                except TypeError: h=sa.play_buffer(int16.tobytes(),2,2,sr)
                handles.append(h); time.sleep(0.0005)
        except Exception:
            self._log_exception("Exception in simpleaudio loop")
            self._notify_error("Audio engine stopped due to an error.")
        finally:
            self.running=False

# ---------------- Offline render ---------------- #

def render_to_wav(path: str, state: RhythmState, duration_sec: float):
    if duration_sec<=0: raise ValueError("Duration must be > 0.")
    with state._lock:
        bpm=float(state.bpm); beats=int(state.beats_per_measure); accent=float(state.accent_factor)
        left_layers=[dict(x) for x in state.left]; right_layers=[dict(x) for x in state.right]
    meas_len=measure_seconds(bpm, beats); meas_samples=int(round(meas_len*SAMPLE_RATE)) if meas_len>0 else 0
    def make_side(layers): intervals=[interval_seconds(bpm, lay["subdiv"]) for lay in layers]; return intervals,[0.0 for _ in layers]
    L_intv,L_next = make_side(left_layers); R_intv,R_next = make_side(right_layers)
    total=int(SAMPLE_RATE*duration_sec); stereo=np.zeros((total,2),dtype=np.float32)
    tone_cache=ToneCache(); wave_cache=WaveCache(); drum=DrumSynth(); mp3_ticks=Mp3TickCache()
    def add_data(start_idx,data,amp,ch):
        if start_idx>=total: return
        end_idx=min(total,start_idx+data.shape[0]); L=end_idx-start_idx
        if L<=0: return
        stereo[start_idx:end_idx, ch]+=amp*data[:L]
    def amp_src(lay, ev_sample):
        accent_now=False
        if meas_samples>0:
            r=ev_sample%meas_samples; accent_now=(r<=TOL_SAMPLES or (meas_samples-r)<=TOL_SAMPLES)
        amp=BASE_AMP*float(lay["vol"])*(accent if accent_now else 1.0)
        mode=lay.get("mode","tone")
        if mode=="mp3_tick" and lay.get("mp3_tick"):
            try: 
                data = mp3_ticks.get(lay["mp3_tick"], is_accent=accent_now)
                if data is not None:
                    return amp, data
            except Exception: pass
        if mode=="file" and lay.get("wav_path"):
            try: return amp, wave_cache.get(lay["wav_path"])
            except Exception: pass
        if mode=="drum": return amp, drum.get(lay.get("drum","snare"))
        return amp, tone_cache.get(float(lay.get("freq",880.0)))
    t=0.0
    while True:
        candidates=[]; 
        if L_next: candidates.append(min(L_next))
        if R_next: candidates.append(min(R_next))
        if not candidates: break
        t=min(candidates)
        if t>=duration_sec: break
        ev_sample=int(round(t*SAMPLE_RATE))
        for i,tn in enumerate(L_next):
            if abs(tn-t)<TOL_SAVE:
                lay=left_layers[i]
                if not lay.get("mute",False):
                    amp,data=amp_src(lay, ev_sample); add_data(ev_sample,data,amp,0)
                L_next[i]+=L_intv[i]
        for i,tn in enumerate(R_next):
            if abs(tn-t)<TOL_SAVE:
                lay=right_layers[i]
                if not lay.get("mute",False):
                    amp,data=amp_src(lay, ev_sample); add_data(ev_sample,data,amp,1)
                R_next[i]+=R_intv[i]
    int16=(np.clip(stereo,-1.0,1.0)*32767.0).astype(np.int16)
    with wave.open(path,"wb") as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SAMPLE_RATE); wf.writeframes(int16.tobytes())

# ---------------- UI ---------------- #

AUTOSAVE_FILE="metronome_autosave.json"
DRUM_CHOICES=["kick","snare","hihat","crash","tom","ride"]

def get_mp3_tick_choices():
    """Get list of available MP3 ticks from the ticks folder"""
    mp3_cache = Mp3TickCache()
    return mp3_cache.get_available_ticks()

class ScrollList(ttk.Frame):
    """
    Higher-contrast, listbox-like container:
      - Visible border around the list
      - Light canvas background
      - Alternating row stripes
      - Stronger selection color
    """
    def __init__(self, master, title, width_px=320):
        super().__init__(master, padding=(6,6))
        ttk.Label(self, text=title, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0,4))

        # Outer box (bordered) for list area
        self.outer = tk.Frame(self, bg="#cbd5e1", bd=1, relief="solid", highlightthickness=0)
        self.outer.pack(fill="both", expand=True)

        # Canvas + inner frame
        self.canvas = tk.Canvas(self.outer, height=260, width=width_px, highlightthickness=0, bg="#f8fafc")
        self.inner = ttk.Frame(self.canvas)
        self.scrollbar = ttk.Scrollbar(self.outer, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.create_window((0,0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.rows = []          # list of {frame,label,swatch,index,base_bg,uid}
        self.uid_to_row = {}    # uid -> row dict
        self.selected_index = None
        self.wraplength = int(width_px - 40)

        # Row palette
        self.row_even = "#f1f5f9"  # light slate-50
        self.row_odd  = "#e5e7eb"  # gray-200
        self.row_border = "#cbd5e1"  # slate-300
        self.row_selected = "#93c5fd"  # blue-300 (higher contrast than blue-100)

    def clear(self):
        for row in self.rows:
            row["frame"].destroy()
        self.rows.clear()
        self.uid_to_row.clear()
        self.selected_index = None

    def rebuild(self, layers, on_toggle_mute, on_delete, on_select, on_pick_color):
        self.clear()
        for idx, layer in enumerate(layers):
            uid = layer.get("uid")
            base_bg = self.row_even if (idx % 2 == 0) else self.row_odd
            fr = tk.Frame(self.inner, padx=3, pady=3, bg=base_bg,
                          highlightthickness=1, highlightbackground=self.row_border, bd=0)
            fr.pack(fill="x", expand=True, pady=2)

            mute_var = tk.BooleanVar(value=bool(layer.get("mute", False)))
            cb = ttk.Checkbutton(fr, variable=mute_var, command=lambda i=idx, v=mute_var: on_toggle_mute(i, v.get()))
            cb.pack(side="left")

            color = layer.get("color", "#9CA3AF")
            swatch = tk.Canvas(fr, width=14, height=14, bg=color, highlightthickness=1, highlightbackground="#64748b")
            swatch.pack(side="left", padx=4)
            swatch.bind("<Button-1>", lambda e, i=idx: on_pick_color(i))

            mode = layer.get("mode","tone").upper()
            parts = [mode, f"÷{layer['subdiv']}"]
            if layer.get("mode","tone") == "tone":
                parts.append(f"{int(layer['freq'])}Hz")
            elif layer.get("mode") == "file":
                p = layer.get("wav_path","")
                parts.append(os.path.basename(p) if p else "(wav)")
            elif layer.get("mode") == "mp3_tick":
                parts.append(layer.get("mp3_tick",""))
            else:
                parts.append(layer.get("drum","snare"))
            parts.append(f"vol {layer['vol']:.2f}")
            text = " • ".join(parts)
            lbl = ttk.Label(fr, text=text, background=base_bg, wraplength=self.wraplength, justify="left")
            lbl.pack(side="left", padx=6, fill="x", expand=True)

            def make_select(i):
                return lambda e=None: on_select(i)
            lbl.bind("<Button-1>", make_select(idx))
            fr.bind("<Button-1>", make_select(idx))

            del_btn = ttk.Button(fr, text="Del", width=4, command=lambda i=idx: on_delete(i))
            del_btn.pack(side="right")

            row = {"frame": fr, "label": lbl, "swatch": swatch, "index": idx, "base_bg": base_bg, "uid": uid}
            self.rows.append(row)
            self.uid_to_row[uid] = row

    def highlight(self, index):
        for row in self.rows:
            row["frame"].configure(bg=row["base_bg"])
            row["label"].configure(background=row["base_bg"])
        if index is not None and 0 <= index < len(self.rows):
            self.rows[index]["frame"].configure(bg=self.row_selected)
            self.rows[index]["label"].configure(background=self.row_selected)
            self.selected_index = index
        else:
            self.selected_index = None

    def flash_uid(self, uid, flash_color, duration_ms=FLASH_MS):
        row = self.uid_to_row.get(uid)
        if not row: return
        orig = row["base_bg"]
        row["frame"].configure(bg=flash_color); row["label"].configure(background=flash_color)
        row["frame"].after(duration_ms, lambda: (row["frame"].configure(bg=orig),
                                                 row["label"].configure(background=orig)))

    def set_color_uid(self, uid, color):
        row = self.uid_to_row.get(uid)
        if not row: return
        row["swatch"].configure(bg=color)

class App(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=10)
        master.title("Stereo Subdivision Metronome — Compact")
        master.protocol("WM_DELETE_WINDOW", self.on_close)
        try:
            master.minsize(720, 560)
            master.geometry("820x640")
        except Exception:
            pass

        self.state=RhythmState(); self.flash_queue=deque()
        self.engine=StreamEngine(self.state, ui_after_callable=lambda cb:self.after(0,cb),
                                 event_notify=self._enqueue_flash)
        self._load_autosave_if_exists()

        # ---------- Top: compact globals ----------
        top=ttk.Frame(self); top.grid(row=0,column=0,sticky="ew")
        for c in range(8): top.columnconfigure(c, weight=1)

        ttk.Label(top,text="BPM").grid(row=0,column=0,sticky="e",padx=4,pady=4)
        self.var_bpm=tk.StringVar(value=str(self.state.bpm))
        ttk.Entry(top,textvariable=self.var_bpm,width=6).grid(row=0,column=1,sticky="w")

        ttk.Label(top,text="Beats").grid(row=0,column=2,sticky="e",padx=(8,4))
        self.var_bpmmeasure=tk.StringVar(value=str(self.state.beats_per_measure))
        ttk.Entry(top,textvariable=self.var_bpmmeasure,width=5).grid(row=0,column=3,sticky="w")

        ttk.Label(top,text="Accent ×").grid(row=0,column=4,sticky="e",padx=(8,4))
        self.var_accent=tk.StringVar(value=str(self.state.accent_factor))
        ttk.Entry(top,textvariable=self.var_accent,width=6).grid(row=0,column=5,sticky="w")

        self.var_flash_enabled=tk.BooleanVar(value=self.state.flash_enabled)
        ttk.Checkbutton(top,text="Flash",variable=self.var_flash_enabled,
                        command=self._update_global_from_inputs).grid(row=0,column=6,sticky="w",padx=(8,0))

        # ---------- New Layer (stacked rows, fewer columns) ----------
        newlay=ttk.LabelFrame(self, text="New Layer")
        newlay.grid(row=1,column=0,sticky="ew",pady=(6,4))
        for c in range(8): newlay.columnconfigure(c, weight=1)

        ttk.Label(newlay,text="Subdiv").grid(row=0,column=0,sticky="e",padx=4,pady=4)
        self.var_subdiv=tk.StringVar(value="4")
        ttk.Entry(newlay,textvariable=self.var_subdiv,width=6).grid(row=0,column=1,sticky="w")

        ttk.Label(newlay,text="Vol").grid(row=0,column=2,sticky="e")
        self.var_vol=tk.StringVar(value="1.0")
        ttk.Entry(newlay,textvariable=self.var_vol,width=6).grid(row=0,column=3,sticky="w")

        self.var_mode=tk.StringVar(value="tone")
        mode_box=ttk.Frame(newlay); mode_box.grid(row=0,column=4,columnspan=2,sticky="w")
        ttk.Radiobutton(mode_box,text="Tone",variable=self.var_mode,value="tone",command=self._on_mode_change).pack(side="left")
        ttk.Radiobutton(mode_box,text="WAV",variable=self.var_mode,value="file",command=self._on_mode_change).pack(side="left")
        ttk.Radiobutton(mode_box,text="Drum",variable=self.var_mode,value="drum",command=self._on_mode_change).pack(side="left")
        ttk.Radiobutton(mode_box,text="MP3",variable=self.var_mode,value="mp3_tick",command=self._on_mode_change).pack(side="left")

        ttk.Label(newlay,text="Color").grid(row=0,column=6,sticky="e")
        self.var_color=tk.StringVar(value=random_dark_color())
        ttk.Button(newlay,text="Pick",command=self._pick_new_color,width=5).grid(row=0,column=7,sticky="w")

        # Row 1: mode-specific
        ttk.Label(newlay,text="Freq (Hz)").grid(row=1,column=0,sticky="e",padx=4,pady=4)
        self.var_freq=tk.StringVar(value="880")
        self.entry_freq=ttk.Entry(newlay,textvariable=self.var_freq,width=8); self.entry_freq.grid(row=1,column=1,sticky="w")

        ttk.Label(newlay,text="WAV").grid(row=1,column=2,sticky="e")
        self.var_wav=tk.StringVar(value="")
        self.entry_wav=ttk.Entry(newlay,textvariable=self.var_wav,width=18,state="disabled"); self.entry_wav.grid(row=1,column=3,sticky="w")
        ttk.Button(newlay,text="Browse",command=self._browse_wav,width=7).grid(row=1,column=4,sticky="w")

        ttk.Label(newlay,text="Drum").grid(row=1,column=5,sticky="e")
        self.var_drum=tk.StringVar(value="snare")
        self.combo_drum=ttk.Combobox(newlay,textvariable=self.var_drum,values=DRUM_CHOICES,state="disabled",width=10)
        self.combo_drum.grid(row=1,column=6,sticky="w")
        
        ttk.Label(newlay,text="MP3 Tick").grid(row=1,column=7,sticky="e",padx=(8,0))
        self.var_mp3_tick=tk.StringVar(value="")
        mp3_choices = get_mp3_tick_choices()
        self.combo_mp3_tick=ttk.Combobox(newlay,textvariable=self.var_mp3_tick,values=mp3_choices,state="disabled",width=12)
        self.combo_mp3_tick.grid(row=1,column=8,sticky="w")
        if mp3_choices:
            self.var_mp3_tick.set(mp3_choices[0])

        # Row 2: add buttons
        add_box=ttk.Frame(newlay); add_box.grid(row=2,column=0,columnspan=8,sticky="ew",pady=(4,2))
        add_box.columnconfigure(0,weight=1); add_box.columnconfigure(1,weight=1)
        ttk.Button(add_box,text="Add to Left",command=self.add_to_left).grid(row=0,column=0,sticky="ew",padx=(0,4))
        ttk.Button(add_box,text="Add to Right",command=self.add_to_right).grid(row=0,column=1,sticky="ew",padx=(4,0))

        # ---------- Middle: lists ----------
        middle=ttk.Frame(self); middle.grid(row=2,column=0,sticky="nsew",pady=(6,0))
        self.rowconfigure(2,weight=1); middle.columnconfigure(0,weight=1); middle.columnconfigure(1,weight=0); middle.columnconfigure(2,weight=1)
        self.left_list=ScrollList(middle,"Left Ear Layers", width_px=320); self.left_list.grid(row=0,column=0,sticky="nsew",padx=(0,6))
        move_box=ttk.Frame(middle,padding=6); move_box.grid(row=0,column=1,sticky="ns")
        ttk.Button(move_box,text="→",width=4,command=self.move_left_to_right).pack(pady=6)
        ttk.Button(move_box,text="←",width=4,command=self.move_right_to_left).pack(pady=6)
        self.right_list=ScrollList(middle,"Right Ear Layers", width_px=320); self.right_list.grid(row=0,column=2,sticky="nsew",padx=(6,0))

        # ---------- Bottom: transport ----------
        bottom=ttk.Frame(self); bottom.grid(row=3,column=0,sticky="ew",pady=(8,0))
        for c in range(6): bottom.columnconfigure(c,weight=1)
        ttk.Button(bottom,text="Play",command=self.on_play).grid(row=0,column=0,sticky="ew",padx=2)
        ttk.Button(bottom,text="Stop",command=self.on_stop).grid(row=0,column=1,sticky="ew",padx=2)
        ttk.Button(bottom,text="Save WAV…",command=self.on_save_wav).grid(row=0,column=2,sticky="ew",padx=2)
        ttk.Button(bottom,text="Save Rhythm…",command=self.on_save_rhythm).grid(row=0,column=3,sticky="ew",padx=2)
        ttk.Button(bottom,text="Load Rhythm…",command=self.on_load_rhythm).grid(row=0,column=4,sticky="ew",padx=2)
        ttk.Button(bottom,text="New (Clear)",command=self.on_new).grid(row=0,column=5,sticky="ew",padx=2)

        self.pack(fill="both",expand=True)
        self.refresh_lists()
        self.after(30,self._drain_flash_queue)

    # --- Flash queue ---
    def _enqueue_flash(self, side, uid, flash_color): self.flash_queue.append((side,uid,flash_color))
    def _drain_flash_queue(self):
        while self.flash_queue:
            side,uid,flash_color=self.flash_queue.popleft()
            if self.state.flash_enabled:
                (self.left_list.flash_uid if side=="L" else self.right_list.flash_uid)(uid,flash_color,FLASH_MS)
        self.after(30,self._drain_flash_queue)

    # --- Autosave ---
    def _autosave(self):
        try:
            with open(AUTOSAVE_FILE,"w",encoding="utf-8") as f: json.dump(self.state.to_dict(), f, indent=2)
        except Exception as e: print("Autosave failed:", e, file=sys.stderr)
    def _load_autosave_if_exists(self):
        if os.path.exists(AUTOSAVE_FILE):
            try:
                with open(AUTOSAVE_FILE,"r",encoding="utf-8") as f: self.state.from_dict(json.load(f))
            except Exception as e: print("Failed to load autosave:", e, file=sys.stderr)

    # --- UI helpers ---
    def _on_mode_change(self):
        m=self.var_mode.get()
        if m=="tone":
            self.entry_freq.configure(state="normal"); self.entry_wav.configure(state="disabled"); self.combo_drum.configure(state="disabled"); self.combo_mp3_tick.configure(state="disabled")
        elif m=="file":
            self.entry_freq.configure(state="disabled"); self.entry_wav.configure(state="normal"); self.combo_drum.configure(state="disabled"); self.combo_mp3_tick.configure(state="disabled")
        elif m=="drum":
            self.entry_freq.configure(state="disabled"); self.entry_wav.configure(state="disabled"); self.combo_drum.configure(state="readonly"); self.combo_mp3_tick.configure(state="disabled")
        elif m=="mp3_tick":
            self.entry_freq.configure(state="disabled"); self.entry_wav.configure(state="disabled"); self.combo_drum.configure(state="disabled"); self.combo_mp3_tick.configure(state="readonly")
    def _browse_wav(self):
        p=filedialog.askopenfilename(title="Choose WAV file", filetypes=[("WAV files","*.wav")])
        if p: self.var_wav.set(p)
    def _pick_new_color(self):
        c=colorchooser.askcolor(title="Choose Color", initialcolor=self.var_color.get())
        if c and c[1]: self.var_color.set(c[1])
    def _pick_color_in_list(self, side, index):
        c=colorchooser.askcolor(title="Choose Color")
        if c and c[1]:
            with self.state._lock:
                target=self.state.left if side=="L" else self.state.right
                if 0<=index<len(target):
                    target[index]["color"]=c[1]; uid=target[index]["uid"]
            (self.left_list.set_color_uid if side=="L" else self.right_list.set_color_uid)(uid, c[1])
            self._autosave(); self.engine.update_live_from_state()

    def _get_new_layer_vals(self):
        try:
            subdiv=int(self.var_subdiv.get()); vol=float(self.var_vol.get()); vol=0.0 if vol<0 else (1.0 if vol>1 else vol)
            mode=self.var_mode.get()
            if mode=="tone": freq=float(self.var_freq.get()); wav_path=""; drum="snare"; mp3_tick=""
            elif mode=="file":
                wav_path=self.var_wav.get(); 
                if not wav_path: raise ValueError("Please choose a WAV file (or use Tone/Drum/MP3).")
                freq=0.0; drum="snare"; mp3_tick=""
            elif mode=="drum": drum=self.var_drum.get() or "snare"; freq=0.0; wav_path=""; mp3_tick=""
            elif mode=="mp3_tick": 
                mp3_tick=self.var_mp3_tick.get() or ""
                if not mp3_tick: raise ValueError("Please select an MP3 tick sound.")
                freq=0.0; wav_path=""; drum="snare"
            else: freq=0.0; wav_path=""; drum="snare"; mp3_tick=""
            color=self.var_color.get(); _=interval_seconds(float(self.var_bpm.get()), subdiv)
            return subdiv, vol, mode, freq, wav_path, drum, mp3_tick, color
        except Exception as e:
            messagebox.showerror("Invalid Layer", str(e)); return None

    def _update_global_from_inputs(self):
        try:
            self.state.bpm=float(self.var_bpm.get()); self.state.beats_per_measure=int(self.var_bpmmeasure.get())
            self.state.accent_factor=float(self.var_accent.get()); self.state.flash_enabled=bool(self.var_flash_enabled.get())
            _=measure_seconds(self.state.bpm, self.state.beats_per_measure)
        except Exception as e:
            messagebox.showerror("Invalid Settings", str(e)); return False
        self._autosave(); self.engine.update_live_from_state(); return True

    def refresh_lists(self):
        def L_toggle_mute(i,val):
            with self.state._lock:
                if 0<=i<len(self.state.left): self.state.left[i]["mute"]=bool(val)
            self._autosave(); self.engine.update_live_from_state()
        def L_delete(i):
            with self.state._lock:
                if 0<=i<len(self.state.left): del self.state.left[i]
            self.left_list.selected_index=None; self.refresh_lists(); self._autosave(); self.engine.update_live_from_state()
        def L_select(i): self.left_list.highlight(i); self.right_list.highlight(None)
        def L_pick_color(i): self._pick_color_in_list("L", i)
        def R_toggle_mute(i,val):
            with self.state._lock:
                if 0<=i<len(self.state.right): self.state.right[i]["mute"]=bool(val)
            self._autosave(); self.engine.update_live_from_state()
        def R_delete(i):
            with self.state._lock:
                if 0<=i<len(self.state.right): del self.state.right[i]
            self.right_list.selected_index=None; self.refresh_lists(); self._autosave(); self.engine.update_live_from_state()
        def R_select(i): self.right_list.highlight(i); self.left_list.highlight(None)
        def R_pick_color(i): self._pick_color_in_list("R", i)

        with self.state._lock:
            L=list(self.state.left); R=list(self.state.right)
        self.left_list.rebuild(L, L_toggle_mute, L_delete, L_select, L_pick_color)
        self.right_list.rebuild(R, R_toggle_mute, R_delete, R_select, R_pick_color)

    # --- Actions ---
    def add_to_left(self):
        if not self._update_global_from_inputs(): return
        vals=self._get_new_layer_vals(); 
        if not vals: return
        subdiv, vol, mode, freq, wav_path, drum, mp3_tick, color=vals
        with self.state._lock:
            self.state.left.append(make_layer(subdiv=subdiv,freq=freq,vol=vol,mute=False,mode=mode,wav_path=wav_path,drum=drum,mp3_tick=mp3_tick,color=color))
        # Randomize color for next layer
        self.var_color.set(random_dark_color())
        self.refresh_lists(); self._autosave(); self.engine.update_live_from_state()
    def add_to_right(self):
        if not self._update_global_from_inputs(): return
        vals=self._get_new_layer_vals(); 
        if not vals: return
        subdiv, vol, mode, freq, wav_path, drum, mp3_tick, color=vals
        with self.state._lock:
            self.state.right.append(make_layer(subdiv=subdiv,freq=freq,vol=vol,mute=False,mode=mode,wav_path=wav_path,drum=drum,mp3_tick=mp3_tick,color=color))
        # Randomize color for next layer
        self.var_color.set(random_dark_color())
        self.refresh_lists(); self._autosave(); self.engine.update_live_from_state()
    def move_left_to_right(self):
        with self.state._lock:
            idx=self.left_list.selected_index
            if idx is None or not (0<=idx<len(self.state.left)): messagebox.showinfo("Move","Select a Left layer first."); return
            lay=self.state.left.pop(idx); self.state.right.append(lay)
        self.refresh_lists(); self._autosave(); self.engine.update_live_from_state()
    def move_right_to_left(self):
        with self.state._lock:
            idx=self.right_list.selected_index
            if idx is None or not (0<=idx<len(self.state.right)): messagebox.showinfo("Move","Select a Right layer first."); return
            lay=self.state.right.pop(idx); self.state.left.append(lay)
        self.refresh_lists(); self._autosave(); self.engine.update_live_from_state()

    def on_play(self):
        if not self._update_global_from_inputs(): return
        self.engine.start()
    def on_stop(self): self.engine.stop()

    def on_save_wav(self):
        if not self._update_global_from_inputs(): return
        try:
            s=simpledialog.askstring("WAV Duration","Duration in seconds:",initialvalue="30")
            if s is None: return
            duration=float(s)
        except Exception: return
        if not duration or duration<=0: return
        path=filedialog.asksaveasfilename(title="Save Stereo WAV", defaultextension=".wav", filetypes=[("WAV files","*.wav")])
        if not path: return
        try: render_to_wav(path, self.state, duration)
        except Exception as e: messagebox.showerror("Save Error", str(e)); return
        messagebox.showinfo("Saved", f"WAV saved to:\n{path}")

    def on_save_rhythm(self):
        if not self._update_global_from_inputs(): return
        path=filedialog.asksaveasfilename(title="Save Rhythm", defaultextension=".json", filetypes=[("JSON files","*.json")])
        if not path: return
        try:
            with open(path,"w",encoding="utf-8") as f: json.dump(self.state.to_dict(), f, indent=2)
        except Exception as e: messagebox.showerror("Save Error", str(e)); return
        messagebox.showinfo("Saved", f"Rhythm saved to:\n{path}")

    def on_load_rhythm(self):
        path=filedialog.askopenfilename(title="Load Rhythm", filetypes=[("JSON files","*.json")])
        if not path: return
        try:
            with open(path,"r",encoding="utf-8") as f: data=json.load(f)
            self.state.from_dict(data)
            self.var_bpm.set(str(self.state.bpm)); self.var_bpmmeasure.set(str(self.state.beats_per_measure))
            self.var_accent.set(str(self.state.accent_factor)); self.var_flash_enabled.set(bool(self.state.flash_enabled))
            self.refresh_lists(); self._autosave(); self.engine.update_live_from_state()
        except Exception as e: messagebox.showerror("Load Error", str(e))

    def on_new(self):
        with self.state._lock:
            self.state.left.clear(); self.state.right.clear()
        self.refresh_lists(); self._autosave(); self.engine.update_live_from_state()

    def on_close(self): self.on_stop(); self.master.destroy()

if __name__=="__main__":
    root=tk.Tk()
    try:
        style=ttk.Style()
        if "vista" in style.theme_names(): style.theme_use("vista")
        elif "clam" in style.theme_names(): style.theme_use("clam")
    except Exception: pass
    App(root)
    root.mainloop()
