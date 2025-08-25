#!/usr/bin/env python3
"""
Stereo Subdivision Metronome — Live Updates + DrumSynth + Stable Flashing (UID)
- Live updates while playing.
- Per layer: Tone, WAV, or Drum (kick/snare/hihat/crash/tom/ride).
- Per-layer color and optional flashing (OFF by default).
- Global accent factor for beat 1.
- Multi-layers per ear with mute, move L<->R.
- Streaming audio via sounddevice; simpleaudio fallback.
- Save/Load presets + autosave; Export stereo WAV; audio on a separate thread.
- Flashing uses stable per-layer UIDs so UI refreshes (like color changes) never break flashes.
- In-place color updates avoid unnecessary list rebuilds.

Run:
    python Poly_Rhythm_Metronome.py
"""

import sys, subprocess, importlib, traceback, math, time, uuid
import json, os, threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, colorchooser
import wave
from collections import deque

# -------------- Auto-install missing packages -------------- #

def ensure_pkg(pkg_name: str, import_name: str = None):
    mod_name = import_name or pkg_name
    try:
        return importlib.import_module(mod_name)
    except ImportError as first_err:
        try:
            print(f"[setup] Installing '{pkg_name}' ...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg_name])
            return importlib.import_module(mod_name)
        except Exception as install_err:
            print(f"[setup] Failed to auto-install '{pkg_name}'. Error:\n{install_err}")
            raise first_err

np = ensure_pkg("numpy")

# Prefer sounddevice; simpleaudio as fallback
try:
    sd = ensure_pkg("sounddevice")
except ImportError:
    sd = None

try:
    sa = ensure_pkg("simpleaudio")
except ImportError:
    sa = None


# --------------------- Audio Constants --------------------- #

SAMPLE_RATE = 44100
BASE_AMP = 0.22
DEFAULT_ACCENT_FACTOR = 1.6
TOL = 1e-4
TOL_SAMPLES = 2
TOL_SAVE = 1e-6
FLASH_MS = 120


# --------------- Timing / Subdivision Helpers -------------- #

def notes_per_beat_from_input(n: int) -> float:
    if n in (1, 2, 4, 8, 16, 32, 64):
        return n / 4.0
    if n > 0:
        return float(n)
    raise ValueError("Subdivision must be a positive integer.")

def interval_seconds(bpm: float, subdiv: int) -> float:
    if bpm <= 0:
        raise ValueError("BPM must be > 0.")
    beat_len = 60.0 / bpm
    per_beat = notes_per_beat_from_input(subdiv)
    return beat_len / per_beat

def measure_seconds(bpm: float, beats_per_measure: int) -> float:
    if beats_per_measure <= 0:
        raise ValueError("Beats per measure must be > 0.")
    return (60.0 / bpm) * float(beats_per_measure)


# -------------------- Tone/WAV/DRUM Cache / DSP --------------------- #

class ToneCache:
    def __init__(self, sample_rate=SAMPLE_RATE, blip_ms=55, fade_ms=5):
        self.sample_rate = sample_rate
        self.blip_ms = blip_ms
        self.fade_ms = fade_ms
        self._cache = {}
    def get(self, freq: float):
        key = round(float(freq), 6)
        if key in self._cache:
            return self._cache[key]
        n = int(self.sample_rate * (self.blip_ms / 1000.0))
        t = np.arange(n, dtype=np.float32) / self.sample_rate
        tone = np.sin(2 * np.pi * key * t).astype(np.float32)
        fade_n = max(1, int(self.sample_rate * (min(self.fade_ms, self.blip_ms/2) / 1000.0)))
        env = np.ones(n, dtype=np.float32)
        env[:fade_n] = np.linspace(0.0, 1.0, fade_n, dtype=np.float32)
        env[-fade_n:] = np.linspace(1.0, 0.0, fade_n, dtype=np.float32)
        mono = tone * env
        self._cache[key] = mono
        return mono

class WaveCache:
    def __init__(self, sample_rate=SAMPLE_RATE):
        self.sample_rate = sample_rate
        self._cache = {}
    def get(self, path: str):
        if not path:
            return None
        key = os.path.abspath(path)
        if key in self._cache:
            return self._cache[key]
        if not os.path.exists(key):
            raise FileNotFoundError(f"WAV not found: {key}")
        data, sr = self._read_wav_any(key)
        if sr != self.sample_rate:
            data = self._resample_linear(data, sr, self.sample_rate)
        self._cache[key] = data.astype(np.float32, copy=False)
        return self._cache[key]
    @staticmethod
    def _read_wav_any(path):
        with wave.open(path, 'rb') as wf:
            n_channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            framerate = wf.getframerate()
            n_frames = wf.getnframes()
            raw = wf.readframes(n_frames)
        if sampwidth == 1:
            data = np.frombuffer(raw, dtype=np.uint8).astype(np.float32); data = (data - 128.0) / 128.0
        elif sampwidth == 2:
            data = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        elif sampwidth == 4:
            arr = np.frombuffer(raw, dtype=np.int32)
            if np.max(np.abs(arr)) < 1e6:
                data = np.frombuffer(raw, dtype=np.float32)
            else:
                data = arr.astype(np.float32) / 2147483648.0
        else:
            raise ValueError("Only 8/16/32-bit or float32 WAV supported.")
        if n_channels > 1:
            data = data.reshape(-1, n_channels).mean(axis=1)
        return data.astype(np.float32, copy=False), framerate
    @staticmethod
    def _resample_linear(x, sr_from, sr_to):
        if sr_from == sr_to:
            return x
        if len(x) == 0:
            return x
        duration = len(x) / float(sr_from)
        new_len = int(round(duration * sr_to))
        if new_len <= 1:
            return np.zeros(1, dtype=np.float32)
        xp = np.linspace(0.0, 1.0, num=len(x), dtype=np.float32)
        fp = x.astype(np.float32, copy=False)
        xnew = np.linspace(0.0, 1.0, num=new_len, dtype=np.float32)
        return np.interp(xnew, xp, fp).astype(np.float32)

class DrumSynth:
    def __init__(self, sample_rate=SAMPLE_RATE):
        self.sample_rate = sample_rate
        self._cache = {}
    def get(self, name: str):
        key = (name or "").lower()
        if key in self._cache:
            return self._cache[key]
        fn = getattr(self, f"_make_{key}", None)
        if not fn:
            data = self._make_snare()
        else:
            data = fn()
        self._cache[key] = data
        return data
    def _make_kick(self):
        sr = self.sample_rate; dur = 0.25
        n = int(sr*dur); t = np.arange(n, dtype=np.float32)/sr
        f0, f1 = 120.0, 50.0; k = np.log(f1/f0)/dur
        phase = 2*np.pi*(f0*(np.expm1(k*t)/k))
        tone = np.sin(phase).astype(np.float32)
        env = np.exp(-t/0.15).astype(np.float32)
        click = np.exp(-t/0.01)
        y = 0.9*tone*env + 0.05*click
        return y.astype(np.float32)
    def _make_snare(self):
        sr = self.sample_rate; dur = 0.3
        n = int(sr*dur); t = np.arange(n, dtype=np.float32)/sr
        noise = np.random.uniform(-1,1,size=n).astype(np.float32)
        env_n = np.exp(-t/0.12).astype(np.float32)
        body = np.sin(2*np.pi*190*t).astype(np.float32)*np.exp(-t/0.1)
        y = 0.8*noise*env_n + 0.25*body
        return y.astype(np.float32)
    def _make_hihat(self):
        sr = self.sample_rate; dur = 0.08
        n = int(sr*dur); t = np.arange(n, dtype=np.float32)/sr
        noise = np.random.uniform(-1,1,size=n).astype(np.float32)
        env = np.exp(-t/0.03).astype(np.float32)
        y = noise*env
        return y.astype(np.float32)
    def _make_crash(self):
        sr = self.sample_rate; dur = 1.2
        n = int(sr*dur); t = np.arange(n, dtype=np.float32)/sr
        noise = np.random.uniform(-1,1,size=n).astype(np.float32)
        env = np.exp(-t/0.6).astype(np.float32)
        y = 0.6*noise*env
        return y.astype(np.float32)
    def _make_tom(self):
        sr = self.sample_rate; dur = 0.4
        n = int(sr*dur); t = np.arange(n, dtype=np.float32)/sr
        freq = 160.0
        tone = np.sin(2*np.pi*freq*t).astype(np.float32)
        env = np.exp(-t/0.25).astype(np.float32)
        y = tone*env
        return y.astype(np.float32)
    def _make_ride(self):
        sr = self.sample_rate; dur = 0.9
        n = int(sr*dur); t = np.arange(n, dtype=np.float32)/sr
        ping = np.sin(2*np.pi*900*t).astype(np.float32)*np.exp(-t/0.4)
        noise = np.random.uniform(-1,1,size=n).astype(np.float32)*np.exp(-t/0.8)*0.2
        y = 0.8*ping + noise
        return y.astype(np.float32)

def float_to_int16(stereo: np.ndarray) -> np.ndarray:
    stereo = np.clip(stereo, -1.0, 1.0)
    return (stereo * 32767.0).astype(np.int16)


# ---------------------- Data Structures -------------------- #

def new_uid():
    return uuid.uuid4().hex

def make_layer(subdiv=4, freq=880.0, vol=1.0, mute=False, mode="tone", wav_path="", drum="snare", color="#9CA3AF", uid=None):
    return {"uid": uid or new_uid(),
            "subdiv": int(subdiv), "freq": float(freq), "vol": float(vol), "mute": bool(mute),
            "mode": mode, "wav_path": wav_path, "drum": drum, "color": color}


class RhythmState:
    def __init__(self):
        self.bpm = 120.0
        self.beats_per_measure = 4
        self.accent_factor = DEFAULT_ACCENT_FACTOR  # global
        self.left = []   # list of layers
        self.right = []  # list of layers
        self.flash_enabled = False
        self._lock = threading.RLock()

    def to_dict(self):
        with self._lock:
            return {
                "bpm": self.bpm,
                "beats_per_measure": self.beats_per_measure,
                "accent_factor": self.accent_factor,
                "flash_enabled": self.flash_enabled,
                "left": self.left,
                "right": self.right,
            }

    def from_dict(self, d):
        with self._lock:
            self.bpm = float(d.get("bpm", 120.0))
            self.beats_per_measure = int(d.get("beats_per_measure", 4))
            self.accent_factor = float(d.get("accent_factor", DEFAULT_ACCENT_FACTOR))
            self.flash_enabled = bool(d.get("flash_enabled", False))
            def normalize(x):
                x = dict(x)
                x.setdefault("mode", "tone")
                x.setdefault("wav_path", "")
                x.setdefault("drum", "snare")
                x.setdefault("color", "#9CA3AF")
                x.setdefault("uid", new_uid())
                return x
            self.left = [make_layer(**normalize(x)) for x in d.get("left", [])]
            self.right = [make_layer(**normalize(x)) for x in d.get("right", [])]


# ------------------------ Streaming Engine --------------------- #

class StreamEngine:
    """
    Streaming backend with simpleaudio fallback.
    Live updates supported via update_live_from_state().
    Flashes are routed by stable layer UID rather than index.
    """
    def __init__(self, rhythm_state: RhythmState, ui_after_callable, event_notify):
        self.rhythm = rhythm_state
        self.ui_after = ui_after_callable
        self.event_notify = event_notify  # function(side, uid, color)

        self.stream = None
        self.running = False
        self.tones = ToneCache()
        self.waves = WaveCache()
        self.drums = DrumSynth()
        self._lock = threading.RLock()

        # Schedule state
        self.left_layers = []
        self.right_layers = []
        self.L_intervals = []
        self.R_intervals = []
        self.L_next = []
        self.R_next = []
        self.measure_samples = 0
        self.sample_counter = 0
        self.accent_factor = DEFAULT_ACCENT_FACTOR
        self.flash_enabled = False

        self.active = []

        self._sa_start_time = None

    def _notify_error(self, msg: str):
        def cb():
            try:
                messagebox.showerror("Audio Error", msg)
            except Exception:
                print("Audio Error:", msg, file=sys.stderr)
        try:
            self.ui_after(cb)
        except Exception:
            print("Audio Error:", msg, file=sys.stderr)

    def is_playing(self):
        return self.running

    def update_live_from_state(self):
        if not self.is_playing():
            return
        with self.rhythm._lock:
            bpm = float(self.rhythm.bpm)
            beats_per_measure = int(self.rhythm.beats_per_measure)
            self.accent_factor = float(self.rhythm.accent_factor)
            self.flash_enabled = bool(self.rhythm.flash_enabled)
            new_left = [dict(x) for x in self.rhythm.left]
            new_right = [dict(x) for x in self.rhythm.right]
        if self.stream is not None:
            t_cur = self.sample_counter / float(SAMPLE_RATE)
        else:
            if self._sa_start_time is None:
                t_cur = 0.0
            else:
                t_cur = time.perf_counter() - self._sa_start_time

        meas_len = measure_seconds(bpm, beats_per_measure)
        with self._lock:
            def recalc(layers):
                intervals = [interval_seconds(bpm, lay["subdiv"]) for lay in layers]
                next_times = []
                for iv in intervals:
                    if iv <= 0: iv = 1e9
                    k = math.ceil((t_cur - 1e-9)/iv)
                    if k < 0: k = 0
                    next_times.append(k * iv)
                return layers, intervals, next_times
            self.left_layers, self.L_intervals, self.L_next = recalc(new_left)
            self.right_layers, self.R_intervals, self.R_next = recalc(new_right)
            self.measure_samples = int(round(meas_len * SAMPLE_RATE)) if meas_len > 0 else 0

    def start(self):
        if self.running:
            return
        with self.rhythm._lock:
            bpm = float(self.rhythm.bpm)
            beats_per_measure = int(self.rhythm.beats_per_measure)
            self.accent_factor = float(self.rhythm.accent_factor)
            self.flash_enabled = bool(self.rhythm.flash_enabled)
            self.left_layers = [dict(x) for x in self.rhythm.left]
            self.right_layers = [dict(x) for x in self.rhythm.right]
        if not self.left_layers and not self.right_layers:
            self._notify_error("No layers added. Add layers to Left or Right and try Play.")
            return
        self.measure_samples = int(round(measure_seconds(bpm, beats_per_measure) * SAMPLE_RATE))

        def mk_side(layers):
            intervals = [interval_seconds(bpm, lay["subdiv"]) for lay in layers]
            next_times = [0.0 for _ in layers]
            return intervals, next_times

        self.L_intervals, self.L_next = mk_side(self.left_layers)
        self.R_intervals, self.R_next = mk_side(self.right_layers)
        self.sample_counter = 0
        self.active.clear()

        if sd is not None:
            try:
                self.stream = sd.OutputStream(
                    samplerate=SAMPLE_RATE, channels=2, dtype='float32',
                    callback=self._callback, blocksize=0
                )
                self.stream.start()
                self.running = True
                return
            except Exception as e:
                self._notify_error(f"sounddevice stream failed ({e}). Falling back to simpleaudio.")
                self.stream = None

        if sa is None:
            try:
                globals()['sa'] = ensure_pkg("simpleaudio")
            except ImportError:
                self._notify_error("Neither 'sounddevice' nor 'simpleaudio' are available.")
                return
        self.running = True
        self._sa_start_time = time.perf_counter()
        threading.Thread(target=self._sa_loop, name="SA-Loop", daemon=True).start()

    def stop(self):
        self.running = False
        if self.stream is not None:
            try:
                self.stream.stop(); self.stream.close()
            except Exception:
                pass
            self.stream = None
        with self._lock:
            self.active.clear()

    def _amp_and_source(self, lay, accent: bool):
        amp = BASE_AMP * float(lay["vol"]) * (self.accent_factor if accent else 1.0)
        mode = lay.get("mode", "tone")
        if mode == "file" and lay.get("wav_path"):
            try:
                return amp, self.waves.get(lay["wav_path"])
            except Exception:
                pass
        if mode == "drum":
            return amp, self.drums.get(lay.get("drum","snare"))
        freq = float(lay.get("freq", 880.0))
        return amp, self.tones.get(freq)

    def _callback(self, outdata, frames, time_info, status):
        try:
            block = np.zeros((frames, 2), dtype=np.float32)
            sr = SAMPLE_RATE
            t0 = self.sample_counter
            t1 = t0 + frames

            def schedule_side(layers, intervals, next_times, channel):
                for i, lay in enumerate(layers):
                    if lay.get("mute", False):
                        continue
                    iv = intervals[i]
                    while True:
                        t_sec = next_times[i]
                        ev_sample = int(round(t_sec * sr))
                        if ev_sample >= t1:
                            break
                        if ev_sample >= t0:
                            accent = False
                            if self.measure_samples > 0:
                                r = ev_sample % self.measure_samples
                                accent = (r <= TOL_SAMPLES or (self.measure_samples - r) <= TOL_SAMPLES)
                            amp, data = self._amp_and_source(lay, accent)
                            self.active.append({"data": data, "idx": 0, "amp": amp, "channel": channel})
                            if self.flash_enabled and self.event_notify is not None:
                                self.event_notify("L" if channel == 0 else "R", lay.get("uid"), lay.get("color","#9CA3AF"))
                        next_times[i] = t_sec + iv

            with self._lock:
                L_layers, R_layers = self.left_layers, self.right_layers
                L_intv, R_intv = self.L_intervals, self.R_intervals
                L_next, R_next = self.L_next, self.R_next

            schedule_side(L_layers, L_intv, L_next, 0)
            schedule_side(R_layers, R_intv, R_next, 1)

            new_active = []
            for blip in self.active:
                data = blip["data"]; ch = blip["channel"]; amp = blip["amp"]; idx = blip["idx"]
                remain = data.shape[0] - idx
                if remain <= 0: continue
                n = min(remain, frames)
                block[:n, ch] += amp * data[idx:idx+n]
                blip["idx"] += n
                if blip["idx"] < data.shape[0]:
                    new_active.append(blip)
            self.active = new_active

            outdata[:] = block
            self.sample_counter += frames

        except Exception:
            # Don't crash the app if the audio callback hiccups
            with open("metronome_log.txt", "a", encoding="utf-8") as f:
                f.write("=== Exception in sounddevice callback ===\n")
                traceback.print_exc(file=f)
            outdata[:] = 0
            return

    def _sa_loop(self):
        try:
            sr = SAMPLE_RATE
            handles = deque(maxlen=512)
            start = self._sa_start_time or time.perf_counter()

            while self.running:
                with self._lock:
                    candidates = []
                    if self.L_next: candidates.append(min(self.L_next))
                    if self.R_next: candidates.append(min(self.R_next))
                    if not candidates:
                        time.sleep(0.01); continue
                    next_t = min(candidates)

                    left_events = []
                    right_events = []

                    for i, t_ev in enumerate(self.L_next):
                        if abs(t_ev - next_t) < TOL:
                            if i < len(self.left_layers):
                                lay = self.left_layers[i]
                                if not lay.get("mute", False):
                                    ev_sample = int(round(t_ev * sr))
                                    accent = False
                                    if self.measure_samples > 0:
                                        r = ev_sample % self.measure_samples
                                        accent = (r <= TOL_SAMPLES or (self.measure_samples - r) <= TOL_SAMPLES)
                                    amp, data = self._amp_and_source(lay, accent)
                                    left_events.append((amp, data, lay.get("uid"), lay.get("color","#9CA3AF")))
                            self.L_next[i] = t_ev + self.L_intervals[i]

                    for i, t_ev in enumerate(self.R_next):
                        if abs(t_ev - next_t) < TOL:
                            if i < len(self.right_layers):
                                lay = self.right_layers[i]
                                if not lay.get("mute", False):
                                    ev_sample = int(round(t_ev * sr))
                                    accent = False
                                    if self.measure_samples > 0:
                                        r = ev_sample % self.measure_samples
                                        accent = (r <= TOL_SAMPLES or (self.measure_samples - r) <= TOL_SAMPLES)
                                    amp, data = self._amp_and_source(lay, accent)
                                    right_events.append((amp, data, lay.get("uid"), lay.get("color","#9CA3AF")))
                            self.R_next[i] = t_ev + self.R_intervals[i]

                target = start + next_t
                while True:
                    now = time.perf_counter()
                    dt = target - now
                    if dt <= 0: break
                    time.sleep(min(0.001, dt))

                max_len = 0
                for amp, data, *_ in left_events + right_events:
                    max_len = max(max_len, data.shape[0])
                if max_len == 0:
                    time.sleep(0.0005); continue

                frame = np.zeros((max_len, 2), dtype=np.float32)
                for amp, data, uid, color in left_events:
                    L = min(max_len, data.shape[0])
                    frame[:L, 0] += amp * data[:L]
                    if self.flash_enabled and self.event_notify is not None:
                        self.event_notify("L", uid, color)
                for amp, data, uid, color in right_events:
                    L = min(max_len, data.shape[0])
                    frame[:L, 1] += amp * data[:L]
                    if self.flash_enabled and self.event_notify is not None:
                        self.event_notify("R", uid, color)

                int16 = float_to_int16(frame)
                try:
                    h = sa.play_buffer(int16, 2, 2, sr)
                except TypeError:
                    h = sa.play_buffer(int16.tobytes(), 2, 2, sr)
                handles.append(h)

                time.sleep(0.0005)
        except Exception:
            with open("metronome_log.txt", "a", encoding="utf-8") as f:
                f.write("=== Exception in simpleaudio loop ===\n")
                traceback.print_exc(file=f)
            self._notify_error("Audio engine stopped due to an error.")
        finally:
            self.running = False


# -------------------- Render to WAV (offline) -------------------- #

def render_to_wav(path: str, state: RhythmState, duration_sec: float):
    if duration_sec <= 0:
        raise ValueError("Duration must be > 0.")
    with state._lock:
        bpm = float(state.bpm)
        beats_per_measure = int(state.beats_per_measure)
        accent_factor = float(state.accent_factor)
        left_layers = [dict(x) for x in state.left]
        right_layers = [dict(x) for x in state.right]

    meas_len = measure_seconds(bpm, beats_per_measure)
    meas_samples = int(round(meas_len * SAMPLE_RATE)) if meas_len > 0 else 0

    def make_side(layers):
        intervals = [interval_seconds(bpm, lay["subdiv"]) for lay in layers]
        next_times = [0.0 for _ in layers]
        return intervals, next_times

    L_intervals, L_next = make_side(left_layers)
    R_intervals, R_next = make_side(right_layers)

    total_samples = int(SAMPLE_RATE * duration_sec)
    stereo = np.zeros((total_samples, 2), dtype=np.float32)
    tone_cache = ToneCache()
    wave_cache = WaveCache()
    drum = DrumSynth()

    def add_data(start_idx, data, amp, ch):
        if start_idx >= total_samples:
            return
        end_idx = min(total_samples, start_idx + data.shape[0])
        L = end_idx - start_idx
        if L <= 0:
            return
        stereo[start_idx:end_idx, ch] += amp * data[:L]

    def amp_and_source(lay, ev_sample):
        accent = False
        if meas_samples > 0:
            r = ev_sample % meas_samples
            accent = (r <= TOL_SAMPLES or (meas_samples - r) <= TOL_SAMPLES)
        amp = BASE_AMP * float(lay["vol"]) * (accent_factor if accent else 1.0)
        mode = lay.get("mode","tone")
        if mode == "file" and lay.get("wav_path"):
            try:
                data = wave_cache.get(lay["wav_path"]); return amp, data
            except Exception:
                pass
        if mode == "drum":
            return amp, drum.get(lay.get("drum","snare"))
        freq = float(lay.get("freq", 880.0))
        return amp, tone_cache.get(freq)

    t = 0.0
    while True:
        candidates = []
        if L_next: candidates.append(min(L_next))
        if R_next: candidates.append(min(R_next))
        if not candidates: break
        t = min(candidates)
        if t >= duration_sec: break
        ev_sample = int(round(t * SAMPLE_RATE))

        for i, tn in enumerate(L_next):
            if abs(tn - t) < TOL_SAVE:
                lay = left_layers[i]
                if not lay.get("mute", False):
                    amp, data = amp_and_source(lay, ev_sample)
                    add_data(ev_sample, data, amp, 0)
                L_next[i] += L_intervals[i]
        for i, tn in enumerate(R_next):
            if abs(tn - t) < TOL_SAVE:
                lay = right_layers[i]
                if not lay.get("mute", False):
                    amp, data = amp_and_source(lay, ev_sample)
                    add_data(ev_sample, data, amp, 1)
                R_next[i] += R_intervals[i]

    int16 = float_to_int16(stereo)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SAMPLE_RATE)
        wf.writeframes(int16.tobytes())


# ----------------------------- UI ----------------------------- #

AUTOSAVE_FILE = "metronome_autosave.json"
DRUM_CHOICES = ["kick","snare","hihat","crash","tom","ride"]

class ScrollList(ttk.Frame):
    def __init__(self, master, title):
        super().__init__(master, padding=(6,6))
        ttk.Label(self, text=title, font=("Segoe UI", 10, "bold")).pack(anchor="w")

        self.canvas = tk.Canvas(self, height=260, highlightthickness=0)
        self.inner = ttk.Frame(self.canvas)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.create_window((0,0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.rows = []          # list of {frame,label,swatch,index,base_bg,uid}
        self.uid_to_row = {}    # uid -> row dict
        self.selected_index = None

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
            base_bg = "#ffffff"
            fr = tk.Frame(self.inner, padx=2, pady=2, bg=base_bg, highlightthickness=1, highlightbackground="#e5e7eb")
            fr.pack(fill="x", expand=True, pady=2)

            mute_var = tk.BooleanVar(value=bool(layer.get("mute", False)))
            cb = ttk.Checkbutton(fr, variable=mute_var, command=lambda i=idx, v=mute_var: on_toggle_mute(i, v.get()))
            cb.pack(side="left")

            color = layer.get("color", "#9CA3AF")
            swatch = tk.Canvas(fr, width=16, height=16, bg=color, highlightthickness=1, highlightbackground="#ccc")
            swatch.pack(side="left", padx=4)
            swatch.bind("<Button-1>", lambda e, i=idx: on_pick_color(i))

            mode = layer.get("mode","tone").upper()
            text = f"{mode}  subdiv={layer['subdiv']}  "
            if layer.get("mode","tone") == "tone":
                text += f"freq={layer['freq']}Hz  "
            elif layer.get("mode") == "file":
                p = layer.get("wav_path","")
                text += f"wav={os.path.basename(p) if p else '(none)'}  "
            else:
                text += f"drum={layer.get('drum','snare')}  "
            text += f"vol={layer['vol']:.2f}"
            lbl = ttk.Label(fr, text=text, background=base_bg)
            lbl.pack(side="left", padx=6)

            def make_select(i):
                return lambda e=None: on_select(i)
            lbl.bind("<Button-1>", make_select(idx))
            fr.bind("<Button-1>", make_select(idx))

            del_btn = ttk.Button(fr, text="Delete", width=7, command=lambda i=idx: on_delete(i))
            del_btn.pack(side="right")

            row = {"frame": fr, "label": lbl, "swatch": swatch, "index": idx, "base_bg": base_bg, "uid": uid}
            self.rows.append(row)
            self.uid_to_row[uid] = row

    def highlight(self, index):
        for i, row in enumerate(self.rows):
            row["frame"].configure(bg=row["base_bg"])
            row["label"].configure(background=row["base_bg"])
        if index is not None and 0 <= index < len(self.rows):
            self.rows[index]["frame"].configure(bg="#dbeafe")
            self.rows[index]["label"].configure(background="#dbeafe")
            self.selected_index = index
        else:
            self.selected_index = None

    def flash_uid(self, uid, color, duration_ms=FLASH_MS):
        row = self.uid_to_row.get(uid)
        if not row:
            return
        orig = row["frame"]["bg"]
        row["frame"].configure(bg=color)
        row["label"].configure(background=color)
        row["frame"].after(duration_ms, lambda: (row["frame"].configure(bg=orig),
                                                 row["label"].configure(background=orig)))

    def set_color_uid(self, uid, color):
        row = self.uid_to_row.get(uid)
        if not row:
            return
        row["swatch"].configure(bg=color)

class App(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=10)
        master.title("Stereo Subdivision Metronome — Live + Drums (UID flashing)")
        master.protocol("WM_DELETE_WINDOW", self.on_close)

        self.state = RhythmState()
        self.flash_queue = deque()
        self.engine = StreamEngine(self.state, ui_after_callable=lambda cb: self.after(0, cb),
                                   event_notify=self._enqueue_flash)

        self._load_autosave_if_exists()

        # ---------- Top Controls ----------
        top = ttk.Frame(self)
        top.grid(row=0, column=0, sticky="ew")
        for c in range(20):
            top.columnconfigure(c, weight=1)

        ttk.Label(top, text="BPM:").grid(row=0, column=0, sticky="e", padx=4, pady=4)
        self.var_bpm = tk.StringVar(value=str(self.state.bpm))
        ttk.Entry(top, textvariable=self.var_bpm, width=7).grid(row=0, column=1, sticky="w")

        ttk.Label(top, text="Beats/Measure:").grid(row=0, column=2, sticky="e", padx=(8,4))
        self.var_bpmmeasure = tk.StringVar(value=str(self.state.beats_per_measure))
        ttk.Entry(top, textvariable=self.var_bpmmeasure, width=7).grid(row=0, column=3, sticky="w")

        ttk.Label(top, text="Accent factor (beat 1):").grid(row=0, column=4, sticky="e", padx=(8,4))
        self.var_accent = tk.StringVar(value=str(self.state.accent_factor))
        ttk.Entry(top, textvariable=self.var_accent, width=7).grid(row=0, column=5, sticky="w")

        self.var_flash_enabled = tk.BooleanVar(value=self.state.flash_enabled)
        ttk.Checkbutton(top, text="Enable color flash", variable=self.var_flash_enabled,
                        command=self._update_global_from_inputs).grid(row=0, column=6, columnspan=2, sticky="w", padx=(8,0))

        # New layer inputs
        ttk.Label(top, text="Subdivision:").grid(row=1, column=0, sticky="e", padx=4, pady=4)
        self.var_subdiv = tk.StringVar(value="4")
        ttk.Entry(top, textvariable=self.var_subdiv, width=7).grid(row=1, column=1, sticky="w")

        self.var_mode = tk.StringVar(value="tone")
        ttk.Radiobutton(top, text="Tone", variable=self.var_mode, value="tone", command=self._on_mode_change).grid(row=1, column=2, sticky="w")
        ttk.Radiobutton(top, text="WAV", variable=self.var_mode, value="file", command=self._on_mode_change).grid(row=1, column=3, sticky="w")
        ttk.Radiobutton(top, text="Drum", variable=self.var_mode, value="drum", command=self._on_mode_change).grid(row=1, column=4, sticky="w")

        ttk.Label(top, text="Freq (Hz):").grid(row=1, column=5, sticky="e")
        self.var_freq = tk.StringVar(value="880")
        self.entry_freq = ttk.Entry(top, textvariable=self.var_freq, width=8)
        self.entry_freq.grid(row=1, column=6, sticky="w")

        ttk.Label(top, text="WAV:").grid(row=1, column=7, sticky="e")
        self.var_wav = tk.StringVar(value="")
        self.entry_wav = ttk.Entry(top, textvariable=self.var_wav, width=22, state="disabled")
        self.entry_wav.grid(row=1, column=8, sticky="ew")
        ttk.Button(top, text="Browse…", command=self._browse_wav).grid(row=1, column=9, sticky="w")

        ttk.Label(top, text="Drum:").grid(row=1, column=10, sticky="e")
        self.var_drum = tk.StringVar(value="snare")
        self.combo_drum = ttk.Combobox(top, textvariable=self.var_drum, values=["kick","snare","hihat","crash","tom","ride"], state="disabled", width=10)
        self.combo_drum.grid(row=1, column=11, sticky="w")

        ttk.Label(top, text="Volume (0..1):").grid(row=1, column=12, sticky="e")
        self.var_vol = tk.StringVar(value="1.0")
        ttk.Entry(top, textvariable=self.var_vol, width=7).grid(row=1, column=13, sticky="w")

        ttk.Label(top, text="Color:").grid(row=1, column=14, sticky="e")
        self.var_color = tk.StringVar(value="#9CA3AF")
        self.color_btn = ttk.Button(top, text="Pick", command=self._pick_new_color)
        self.color_btn.grid(row=1, column=15, sticky="w")

        ttk.Button(top, text="Add to Left", command=self.add_to_left).grid(row=1, column=16, sticky="ew", padx=(8,2))
        ttk.Button(top, text="Add to Right", command=self.add_to_right).grid(row=1, column=17, sticky="ew", padx=(2,0))

        # ---------- Middle: Lists & Move Buttons ----------
        middle = ttk.Frame(self)
        middle.grid(row=1, column=0, sticky="nsew", pady=(8,0))
        self.rowconfigure(1, weight=1)
        middle.columnconfigure(0, weight=1)
        middle.columnconfigure(1, weight=0)
        middle.columnconfigure(2, weight=1)

        self.left_list = ScrollList(middle, "Left Ear Layers")
        self.left_list.grid(row=0, column=0, sticky="nsew", padx=(0,8))

        move_box = ttk.Frame(middle, padding=10)
        move_box.grid(row=0, column=1, sticky="ns")
        ttk.Button(move_box, text="→ Move →", command=self.move_left_to_right).pack(pady=6)
        ttk.Button(move_box, text="← Move ←", command=self.move_right_to_left).pack(pady=6)

        self.right_list = ScrollList(middle, "Right Ear Layers")
        self.right_list.grid(row=0, column=2, sticky="nsew", padx=(8,0))

        # ---------- Bottom: Transport & File Ops ----------
        bottom = ttk.Frame(self)
        bottom.grid(row=2, column=0, sticky="ew", pady=(10,0))
        for c in range(6):
            bottom.columnconfigure(c, weight=1)

        ttk.Button(bottom, text="Play", command=self.on_play).grid(row=0, column=0, sticky="ew", padx=2)
        ttk.Button(bottom, text="Stop", command=self.on_stop).grid(row=0, column=1, sticky="ew", padx=2)
        ttk.Button(bottom, text="Save WAV…", command=self.on_save_wav).grid(row=0, column=2, sticky="ew", padx=2)
        ttk.Button(bottom, text="Save Rhythm…", command=self.on_save_rhythm).grid(row=0, column=3, sticky="ew", padx=2)
        ttk.Button(bottom, text="Load Rhythm…", command=self.on_load_rhythm).grid(row=0, column=4, sticky="ew", padx=2)
        ttk.Button(bottom, text="New (Clear)", command=self.on_new).grid(row=0, column=5, sticky="ew", padx=2)

        self.pack(fill="both", expand=True)
        self.refresh_lists()  # initial render

        self.after(30, self._drain_flash_queue)

    # ---------- Flash queue ----------
    def _enqueue_flash(self, side, uid, color):
        self.flash_queue.append((side, uid, color))

    def _drain_flash_queue(self):
        while self.flash_queue:
            side, uid, color = self.flash_queue.popleft()
            if self.state.flash_enabled:
                if side == "L":
                    self.left_list.flash_uid(uid, color, FLASH_MS)
                else:
                    self.right_list.flash_uid(uid, color, FLASH_MS)
        self.after(30, self._drain_flash_queue)

    # ---------- Autosave ----------
    def _autosave(self):
        try:
            with open(AUTOSAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.state.to_dict(), f, indent=2)
        except Exception as e:
            print("Autosave failed:", e, file=sys.stderr)

    def _load_autosave_if_exists(self):
        if os.path.exists(AUTOSAVE_FILE):
            try:
                with open(AUTOSAVE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.state.from_dict(data)
            except Exception as e:
                print("Failed to load autosave:", e, file=sys.stderr)

    # ---------- Helpers ----------
    def _on_mode_change(self):
        mode = self.var_mode.get()
        if mode == "tone":
            self.entry_freq.configure(state="normal")
            self.entry_wav.configure(state="disabled")
            self.combo_drum.configure(state="disabled")
        elif mode == "file":
            self.entry_freq.configure(state="disabled")
            self.entry_wav.configure(state="normal")
            self.combo_drum.configure(state="disabled")
        else:
            self.entry_freq.configure(state="disabled")
            self.entry_wav.configure(state="disabled")
            self.combo_drum.configure(state="readonly")

    def _browse_wav(self):
        path = filedialog.askopenfilename(title="Choose WAV file",
                                          filetypes=[("WAV files","*.wav")])
        if path:
            self.var_wav.set(path)

    def _pick_new_color(self):
        c = colorchooser.askcolor(title="Choose Color", initialcolor=self.var_color.get())
        if c and c[1]:
            self.var_color.set(c[1])

    def _pick_color_in_list(self, which_side, index):
        c = colorchooser.askcolor(title="Choose Color")
        if c and c[1]:
            with self.state._lock:
                target = self.state.left if which_side == "L" else self.state.right
                if 0 <= index < len(target):
                    target[index]["color"] = c[1]
                    uid = target[index]["uid"]
            if which_side == "L":
                self.left_list.set_color_uid(uid, c[1])
            else:
                self.right_list.set_color_uid(uid, c[1])
            self._autosave()
            self.engine.update_live_from_state()

    def _get_new_layer_vals(self):
        try:
            subdiv = int(self.var_subdiv.get())
            vol = float(self.var_vol.get())
            if vol < 0: vol = 0.0
            if vol > 1: vol = 1.0
            mode = self.var_mode.get()
            if mode == "tone":
                freq = float(self.var_freq.get()); wav_path = ""; drum = "snare"
            elif mode == "file":
                wav_path = self.var_wav.get()
                if not wav_path: raise ValueError("Please choose a WAV file (or use Tone/Drum).")
                freq = 0.0; drum = "snare"
            else:
                drum = self.var_drum.get() or "snare"
                freq = 0.0; wav_path = ""
            color = self.var_color.get()
            _ = interval_seconds(float(self.var_bpm.get()), subdiv)
            return subdiv, vol, mode, freq, wav_path, drum, color
        except Exception as e:
            messagebox.showerror("Invalid Layer", str(e))
            return None

    def _update_global_from_inputs(self):
        try:
            self.state.bpm = float(self.var_bpm.get())
            self.state.beats_per_measure = int(self.var_bpmmeasure.get())
            self.state.accent_factor = float(self.var_accent.get())
            self.state.flash_enabled = bool(self.var_flash_enabled.get())
            _ = measure_seconds(self.state.bpm, self.state.beats_per_measure)
        except Exception as e:
            messagebox.showerror("Invalid Settings", str(e))
            return False
        self._autosave()
        self.engine.update_live_from_state()
        return True

    def refresh_lists(self):
        def L_toggle_mute(i, val):
            with self.state._lock:
                if 0 <= i < len(self.state.left):
                    self.state.left[i]["mute"] = bool(val)
            self._autosave()
            self.engine.update_live_from_state()

        def L_delete(i):
            with self.state._lock:
                if 0 <= i < len(self.state.left):
                    del self.state.left[i]
            self.left_list.selected_index = None
            self.refresh_lists()
            self._autosave()
            self.engine.update_live_from_state()

        def L_select(i):
            self.left_list.highlight(i)
            self.right_list.highlight(None)

        def L_pick_color(i):
            self._pick_color_in_list("L", i)

        def R_toggle_mute(i, val):
            with self.state._lock:
                if 0 <= i < len(self.state.right):
                    self.state.right[i]["mute"] = bool(val)
            self._autosave()
            self.engine.update_live_from_state()

        def R_delete(i):
            with self.state._lock:
                if 0 <= i < len(self.state.right):
                    del self.state.right[i]
            self.right_list.selected_index = None
            self.refresh_lists()
            self._autosave()
            self.engine.update_live_from_state()

        def R_select(i):
            self.right_list.highlight(i)
            self.left_list.highlight(None)

        def R_pick_color(i):
            self._pick_color_in_list("R", i)

        with self.state._lock:
            left_layers = list(self.state.left)
            right_layers = list(self.state.right)

        self.left_list.rebuild(left_layers, L_toggle_mute, L_delete, L_select, L_pick_color)
        self.right_list.rebuild(right_layers, R_toggle_mute, R_delete, R_select, R_pick_color)

    # ---------- UI Actions ----------
    def add_to_left(self):
        if not self._update_global_from_inputs():
            return
        vals = self._get_new_layer_vals()
        if not vals: return
        subdiv, vol, mode, freq, wav_path, drum, color = vals
        with self.state._lock:
            self.state.left.append(make_layer(subdiv=subdiv, freq=freq, vol=vol, mute=False,
                                              mode=mode, wav_path=wav_path, drum=drum, color=color))
        self.refresh_lists()
        self._autosave()
        self.engine.update_live_from_state()

    def add_to_right(self):
        if not self._update_global_from_inputs():
            return
        vals = self._get_new_layer_vals()
        if not vals: return
        subdiv, vol, mode, freq, wav_path, drum, color = vals
        with self.state._lock:
            self.state.right.append(make_layer(subdiv=subdiv, freq=freq, vol=vol, mute=False,
                                               mode=mode, wav_path=wav_path, drum=drum, color=color))
        self.refresh_lists()
        self._autosave()
        self.engine.update_live_from_state()

    def move_left_to_right(self):
        with self.state._lock:
            idx = self.left_list.selected_index
            if idx is None or not (0 <= idx < len(self.state.left)):
                messagebox.showinfo("Move", "Select a Left layer first."); return
            lay = self.state.left.pop(idx)
            self.state.right.append(lay)
        self.refresh_lists()
        self._autosave()
        self.engine.update_live_from_state()

    def move_right_to_left(self):
        with self.state._lock:
            idx = self.right_list.selected_index
            if idx is None or not (0 <= idx < len(self.state.right)):
                messagebox.showinfo("Move", "Select a Right layer first."); return
            lay = self.state.right.pop(idx)
            self.state.left.append(lay)
        self.refresh_lists()
        self._autosave()
        self.engine.update_live_from_state()

    def on_play(self):
        if not self._update_global_from_inputs():
            return
        self.engine.start()

    def on_stop(self):
        self.engine.stop()

    def on_save_wav(self):
        if not self._update_global_from_inputs():
            return
        try:
            s = simpledialog.askstring("WAV Duration", "Duration in seconds:", initialvalue="30")
            if s is None: return
            duration = float(s)
        except Exception:
            return
        if not duration or duration <= 0: return
        path = filedialog.asksaveasfilename(title="Save Stereo WAV", defaultextension=".wav",
                                            filetypes=[("WAV files", "*.wav")])
        if not path: return
        try:
            render_to_wav(path, self.state, duration)
        except Exception as e:
            messagebox.showerror("Save Error", str(e)); return
        messagebox.showinfo("Saved", f"WAV saved to:\n{path}")

    def on_save_rhythm(self):
        if not self._update_global_from_inputs():
            return
        path = filedialog.asksaveasfilename(title="Save Rhythm", defaultextension=".json",
                                            filetypes=[("JSON files","*.json")])
        if not path: return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.state.to_dict(), f, indent=2)
        except Exception as e:
            messagebox.showerror("Save Error", str(e)); return
        messagebox.showinfo("Saved", f"Rhythm saved to:\n{path}")

    def on_load_rhythm(self):
        path = filedialog.askopenfilename(title="Load Rhythm", filetypes=[("JSON files","*.json")])
        if not path: return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.state.from_dict(data)
            self.var_bpm.set(str(self.state.bpm))
            self.var_bpmmeasure.set(str(self.state.beats_per_measure))
            self.var_accent.set(str(self.state.accent_factor))
            self.var_flash_enabled.set(bool(self.state.flash_enabled))
            self.refresh_lists()
            self._autosave()
            self.engine.update_live_from_state()
        except Exception as e:
            messagebox.showerror("Load Error", str(e))

    def on_new(self):
        with self.state._lock:
            self.state.left.clear()
            self.state.right.clear()
        self.refresh_lists()
        self._autosave()
        self.engine.update_live_from_state()

    def on_close(self):
        self.on_stop()
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    try:
        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")
        elif "clam" in style.theme_names():
            style.theme_use("clam")
    except Exception:
        pass
    App(root)
    root.mainloop()
