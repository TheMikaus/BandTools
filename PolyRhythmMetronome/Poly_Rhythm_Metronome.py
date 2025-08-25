
#!/usr/bin/env python3
"""
Stereo Subdivision Metronome — Multi-Layer per Ear (Streaming backend + WAV layers + color flash)
- Multiple layers per ear with subdivision, frequency/volume/mute, and COLOR.
- Each layer can be a synthesized TONE or a WAV FILE (mixed together if they overlap).
- Global ACCENT FACTOR controls the loudness of beat 1 relative to other beats (applies to all layers).
- Optional visual FLASH on hits using per-layer colors (default OFF).
- Move layers between ears; mute with checkbox.
- Beat 1 accent per measure.
- Playback via a low-latency audio callback using sounddevice (preferred).
  Falls back to simpleaudio if sounddevice is unavailable.
- Audio runs on a separate thread from the UI.
- Save/Load rhythm presets (JSON) + autosave on change.
- Export stereo WAV for a user-defined duration.
- Auto-installs numpy and sounddevice/simpleaudio if missing.

Run:
    python stereo_metronome_stream.py
"""

import sys, subprocess, importlib, traceback, struct
import json, os, time, threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, colorchooser
import wave
from collections import deque
from dataclasses import dataclass, field

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
BLIP_MS = 55
FADE_MS = 5
BASE_AMP = 0.22           # base loudness used in amp calculation
DEFAULT_ACCENT_FACTOR = 1.6  # beat 1 multiplier (user adjustable)
TOL = 1e-4      # seconds tolerance for event alignment
TOL_SAMPLES = 2 # samples tolerance for measure boundary detection
TOL_SAVE = 1e-6 # for offline render
FLASH_MS = 120  # visual flash duration


# --------------- Timing / Subdivision Helpers -------------- #

def notes_per_beat_from_input(n: int) -> float:
    """
    Interpret subdivision:
    - Powers of two => standard note denominators (4=quarters, 8=eighths, 16=sixteenths...):
        4 -> 1 per beat, 8 -> 2 per beat, 16 -> 4 per beat, etc.
    - Other positive integers => tuplets-per-beat (3=triplets, 5=quintuplets...)
    """
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


# -------------------- Tone/WAV Cache / DSP --------------------- #

class ToneCache:
    """Cache unit blip tones by frequency to avoid re-generating every hit."""
    def __init__(self, sample_rate=SAMPLE_RATE, blip_ms=BLIP_MS, fade_ms=FADE_MS):
        self.sample_rate = sample_rate
        self.blip_ms = blip_ms
        self.fade_ms = fade_ms
        self._cache = {}  # freq -> np.ndarray mono float32

    def get(self, freq: float):
        key = round(float(freq), 6)
        if key in self._cache:
            return self._cache[key]
        # Generate mono unit-amplitude with short fade
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
    """
    Cache mono float32 arrays for WAV paths.
    Supports PCM 8/16/32 and float32 WAV. Resamples to SAMPLE_RATE if needed.
    """
    def __init__(self, sample_rate=SAMPLE_RATE):
        self.sample_rate = sample_rate
        self._cache = {}  # path -> np.ndarray mono float32

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
        import numpy as np
        if sampwidth == 1:
            # 8-bit unsigned
            data = np.frombuffer(raw, dtype=np.uint8).astype(np.float32)
            data = (data - 128.0) / 128.0
        elif sampwidth == 2:
            data = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        elif sampwidth == 4:
            # Could be int32 or float32; wave doesn't tell, assume int32 PCM if it looks like that, otherwise float32
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
        import numpy as np
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


def float_to_int16(stereo):
    import numpy as np
    stereo = np.clip(stereo, -1.0, 1.0)
    return (stereo * 32767.0).astype(np.int16)


# ---------------------- Data Structures -------------------- #

def make_layer(subdiv=4, freq=880.0, vol=1.0, mute=False, mode="tone", wav_path="", color="#9CA3AF"):
    return {"subdiv": int(subdiv), "freq": float(freq), "vol": float(vol), "mute": bool(mute),
            "mode": mode, "wav_path": wav_path, "color": color}


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
            self.left = [make_layer(**x) for x in d.get("left", [])]
            self.right = [make_layer(**x) for x in d.get("right", [])]


# ------------------------ Streaming Engine --------------------- #

class StreamEngine:
    """
    Preferred backend using sounddevice stream callback for stable playback.
    Freezes the configuration at start() for deterministic timing.
    """
    def __init__(self, rhythm_state: RhythmState, ui_after_callable, event_notify):
        self.rhythm = rhythm_state
        self.ui_after = ui_after_callable
        self.stream = None
        self.running = False
        self.tones = ToneCache()
        self.waves = WaveCache()
        self._lock = threading.RLock()

        # event notify: function(side, layer_index, color)
        self.event_notify = event_notify

        # Scheduling state (set on start)
        self.left_layers = []
        self.right_layers = []
        self.L_intervals = []
        self.R_intervals = []
        self.L_next = []
        self.R_next = []
        self.measure_samples = 0
        self.sample_counter = 0  # running sample position

        # Active blips: dict with 'data' (mono array), 'idx', 'amp', 'channel'
        self.active = []

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

    def start(self):
        if self.running:
            return
        # Freeze configuration
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
            next_times = [0.0 for _ in layers]  # seconds
            return intervals, next_times

        self.L_intervals, self.L_next = mk_side(self.left_layers)
        self.R_intervals, self.R_next = mk_side(self.right_layers)
        self.sample_counter = 0
        self.active.clear()

        if sd is not None:
            try:
                self.stream = sd.OutputStream(
                    samplerate=SAMPLE_RATE,
                    channels=2,
                    dtype='float32',
                    callback=self._callback,
                    blocksize=0,
                )
                self.stream.start()
                self.running = True
                return
            except Exception as e:
                self._notify_error(f"sounddevice stream failed ({e}). Falling back to simpleaudio.")
                self.stream = None

        # Fallback to simpleaudio loop
        if sa is None:
            try:
                globals()['sa'] = ensure_pkg("simpleaudio")
            except ImportError:
                self._notify_error("Neither 'sounddevice' nor 'simpleaudio' are available.")
                return
        self.running = True
        threading.Thread(target=self._sa_loop, name="SA-Loop", daemon=True).start()

    def stop(self):
        self.running = False
        if self.stream is not None:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None
        with self._lock:
            self.active.clear()

    # ---- Calculate amplitude and choose source data for a layer hit ----
    def _amp_and_source(self, lay, accent: bool):
        amp = BASE_AMP * float(lay["vol"]) * (self.accent_factor if accent else 1.0)
        if lay.get("mode", "tone") == "file" and lay.get("wav_path"):
            try:
                data = self.waves.get(lay["wav_path"])
                return amp, data
            except Exception as e:
                pass
        freq = float(lay.get("freq", 880.0))
        data = self.tones.get(freq)
        return amp, data

    # ---- sounddevice callback ----
    def _callback(self, outdata, frames, time_info, status):
        import numpy as np
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
                                color = lay.get("color", "#9CA3AF")
                                self.event_notify("L" if channel == 0 else "R", i, color)
                        next_times[i] = t_sec + iv

            schedule_side(self.left_layers, self.L_intervals, self.L_next, 0)
            schedule_side(self.right_layers, self.R_intervals, self.R_next, 1)

            new_active = []
            for blip in self.active:
                data = blip["data"]
                ch = blip["channel"]
                amp = blip["amp"]
                idx = blip["idx"]
                remain = data.shape[0] - idx
                if remain <= 0:
                    continue
                n = min(remain, frames)
                block[:n, ch] += amp * data[idx:idx+n]
                blip["idx"] += n
                if blip["idx"] < data.shape[0]:
                    new_active.append(blip)
            self.active = new_active

            outdata[:] = block
            self.sample_counter += frames

        except Exception as e:
            with open("metronome_log.txt", "a", encoding="utf-8") as f:
                f.write("=== Exception in sounddevice callback ===\n")
                traceback.print_exc(file=f)
            outdata[:] = 0
            raise

    # ---- simpleaudio fallback loop ----
    def _sa_loop(self):
        import numpy as np, time
        try:
            sr = SAMPLE_RATE
            handles = deque(maxlen=512)
            start = time.perf_counter()

            while self.running:
                candidates = []
                if self.L_next: candidates.append(min(self.L_next))
                if self.R_next: candidates.append(min(self.R_next))
                if not candidates:
                    time.sleep(0.01)
                    continue
                next_t = min(candidates)

                left_events = []
                right_events = []

                for i, t_ev in enumerate(self.L_next):
                    if abs(t_ev - next_t) < TOL:
                        lay = self.left_layers[i]
                        if not lay.get("mute", False):
                            ev_sample = int(round(t_ev * sr))
                            accent = False
                            if self.measure_samples > 0:
                                r = ev_sample % self.measure_samples
                                accent = (r <= TOL_SAMPLES or (self.measure_samples - r) <= TOL_SAMPLES)
                            amp, data = self._amp_and_source(lay, accent)
                            left_events.append((amp, data, i))
                        self.L_next[i] = t_ev + self.L_intervals[i]

                for i, t_ev in enumerate(self.R_next):
                    if abs(t_ev - next_t) < TOL:
                        lay = self.right_layers[i]
                        if not lay.get("mute", False):
                            ev_sample = int(round(t_ev * sr))
                            accent = False
                            if self.measure_samples > 0:
                                r = ev_sample % self.measure_samples
                                accent = (r <= TOL_SAMPLES or (self.measure_samples - r) <= TOL_SAMPLES)
                            amp, data = self._amp_and_source(lay, accent)
                            right_events.append((amp, data, i))
                        self.R_next[i] = t_ev + self.R_intervals[i]

                target = start + next_t
                while True:
                    now = time.perf_counter()
                    dt = target - now
                    if dt <= 0: break
                    time.sleep(min(0.001, dt))

                max_len = 0
                for amp, data, _ in left_events + right_events:
                    max_len = max(max_len, data.shape[0])
                if max_len == 0:
                    time.sleep(0.0005)
                    continue

                frame = np.zeros((max_len, 2), dtype=np.float32)
                for amp, data, idx in left_events:
                    L = min(max_len, data.shape[0])
                    frame[:L, 0] += amp * data[:L]
                    if self.flash_enabled and self.event_notify is not None:
                        color = self.left_layers[idx].get("color", "#9CA3AF")
                        self.event_notify("L", idx, color)
                for amp, data, idx in right_events:
                    L = min(max_len, data.shape[0])
                    frame[:L, 1] += amp * data[:L]
                    if self.flash_enabled and self.event_notify is not None:
                        color = self.right_layers[idx].get("color", "#9CA3AF")
                        self.event_notify("R", idx, color)

                int16 = float_to_int16(frame)
                try:
                    h = sa.play_buffer(int16, 2, 2, sr)
                except TypeError:
                    h = sa.play_buffer(int16.tobytes(), 2, 2, sr)
                handles.append(h)

                time.sleep(0.0005)
        except Exception as e:
            with open("metronome_log.txt", "a", encoding="utf-8") as f:
                f.write("=== Exception in simpleaudio loop ===\n")
                traceback.print_exc(file=f)
            self._notify_error(str(e))
        finally:
            self.running = False


# -------------------- Render to WAV (offline) -------------------- #

def render_to_wav(path: str, state: RhythmState, duration_sec: float):
    import numpy as np
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
        if lay.get("mode", "tone") == "file" and lay.get("wav_path"):
            try:
                data = wave_cache.get(lay["wav_path"])
                return amp, data
            except Exception:
                pass
        freq = float(lay.get("freq", 880.0))
        data = tone_cache.get(freq)
        return amp, data

    t = 0.0
    while True:
        candidates = []
        if L_next:
            candidates.append(min(L_next))
        if R_next:
            candidates.append(min(R_next))
        if not candidates:
            break
        t = min(candidates)
        if t >= duration_sec:
            break

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
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(int16.tobytes())


# ----------------------------- UI ----------------------------- #

AUTOSAVE_FILE = "metronome_autosave.json"

class ScrollList(ttk.Frame):
    """
    Scrollable list of layer rows with flashing capability.
    """
    def __init__(self, master, title):
        super().__init__(master, padding=(6,6))
        ttk.Label(self, text=title, font=("Segoe UI", 10, "bold")).pack(anchor="w")

        self.canvas = tk.Canvas(self, height=240, highlightthickness=0)
        self.inner = ttk.Frame(self.canvas)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.create_window((0,0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.rows = []  # [{"frame": tk.Frame, "label": ttk.Label, "index": i, "base_bg": str}, ...]
        self.selected_index = None

    def clear(self):
        for row in self.rows:
            row["frame"].destroy()
        self.rows.clear()
        self.selected_index = None

    def rebuild(self, layers, on_toggle_mute, on_delete, on_select, on_pick_color):
        self.clear()
        for idx, layer in enumerate(layers):
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

            text = f"{layer.get('mode','tone').upper()}  subdiv={layer['subdiv']}  "
            if layer.get("mode","tone") == "tone":
                text += f"freq={layer['freq']}Hz  "
            else:
                p = layer.get("wav_path","")
                text += f"wav={os.path.basename(p) if p else '(none)'}  "
            text += f"vol={layer['vol']:.2f}"
            lbl = ttk.Label(fr, text=text, background=base_bg)
            lbl.pack(side="left", padx=6)

            def make_select(i):
                return lambda e=None: on_select(i)
            lbl.bind("<Button-1>", make_select(idx))
            fr.bind("<Button-1>", make_select(idx))

            del_btn = ttk.Button(fr, text="Delete", width=7, command=lambda i=idx: on_delete(i))
            del_btn.pack(side="right")

            self.rows.append({"frame": fr, "label": lbl, "index": idx, "base_bg": base_bg, "swatch": swatch})

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

    def flash(self, index, color, duration_ms=FLASH_MS):
        if index is None or not (0 <= index < len(self.rows)):
            return
        row = self.rows[index]
        orig = row["frame"]["bg"]
        row["frame"].configure(bg=color)
        row["label"].configure(background=color)
        row["frame"].after(duration_ms, lambda: (row["frame"].configure(bg=orig),
                                                 row["label"].configure(background=orig)))


class App(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=10)
        master.title("Stereo Subdivision Metronome — Multi-Layer (Streaming + WAV + Colors)")
        master.protocol("WM_DELETE_WINDOW", self.on_close)

        self.state = RhythmState()
        self.flash_queue = deque()
        self.engine = StreamEngine(self.state, ui_after_callable=lambda cb: self.after(0, cb),
                                   event_notify=self._enqueue_flash)

        self._load_autosave_if_exists()

        # ---------- Top Controls ----------
        top = ttk.Frame(self)
        top.grid(row=0, column=0, sticky="ew")
        for c in range(15):
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

        ttk.Label(top, text="Freq (Hz):").grid(row=1, column=4, sticky="e")
        self.var_freq = tk.StringVar(value="880")
        self.entry_freq = ttk.Entry(top, textvariable=self.var_freq, width=8)
        self.entry_freq.grid(row=1, column=5, sticky="w")

        ttk.Label(top, text="WAV:").grid(row=1, column=6, sticky="e")
        self.var_wav = tk.StringVar(value="")
        self.entry_wav = ttk.Entry(top, textvariable=self.var_wav, width=22, state="disabled")
        self.entry_wav.grid(row=1, column=7, sticky="ew")
        ttk.Button(top, text="Browse…", command=self._browse_wav).grid(row=1, column=8, sticky="w")

        ttk.Label(top, text="Volume (0..1):").grid(row=1, column=9, sticky="e")
        self.var_vol = tk.StringVar(value="1.0")
        ttk.Entry(top, textvariable=self.var_vol, width=7).grid(row=1, column=10, sticky="w")

        ttk.Label(top, text="Color:").grid(row=1, column=11, sticky="e")
        self.var_color = tk.StringVar(value="#9CA3AF")
        self.color_btn = ttk.Button(top, text="Pick", command=self._pick_new_color)
        self.color_btn.grid(row=1, column=12, sticky="w")

        ttk.Button(top, text="Add to Left", command=self.add_to_left).grid(row=1, column=13, sticky="ew", padx=(8,2))
        ttk.Button(top, text="Add to Right", command=self.add_to_right).grid(row=1, column=14, sticky="ew", padx=(2,0))

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
    def _enqueue_flash(self, side, index, color):
        self.flash_queue.append((side, index, color))

    def _drain_flash_queue(self):
        if self.state.flash_enabled:
            while self.flash_queue:
                side, index, color = self.flash_queue.popleft()
                if side == "L":
                    self.left_list.flash(index, color, FLASH_MS)
                else:
                    self.right_list.flash(index, color, FLASH_MS)
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
        else:
            self.entry_freq.configure(state="disabled")
            self.entry_wav.configure(state="normal")

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
                if which_side == "L" and 0 <= index < len(self.state.left):
                    self.state.left[index]["color"] = c[1]
                if which_side == "R" and 0 <= index < len(self.state.right):
                    self.state.right[index]["color"] = c[1]
            self.refresh_lists()
            self._autosave()

    def _get_new_layer_vals(self):
        try:
            subdiv = int(self.var_subdiv.get())
            vol = float(self.var_vol.get())
            if vol < 0: vol = 0.0
            if vol > 1: vol = 1.0
            mode = self.var_mode.get()
            freq = float(self.var_freq.get()) if mode == "tone" else 0.0
            wav_path = self.var_wav.get() if mode == "file" else ""
            color = self.var_color.get()
            _ = interval_seconds(float(self.var_bpm.get()), subdiv)
            if mode == "file" and not wav_path:
                raise ValueError("Please choose a WAV file (or switch to Tone).")
            return subdiv, vol, mode, freq, wav_path, color
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
        return True

    def refresh_lists(self):
        def L_toggle_mute(i, val):
            with self.state._lock:
                if 0 <= i < len(self.state.left):
                    self.state.left[i]["mute"] = bool(val)
            self._autosave()

        def L_delete(i):
            with self.state._lock:
                if 0 <= i < len(self.state.left):
                    del self.state.left[i]
            self.left_list.selected_index = None
            self.refresh_lists()
            self._autosave()

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

        def R_delete(i):
            with self.state._lock:
                if 0 <= i < len(self.state.right):
                    del self.state.right[i]
            self.right_list.selected_index = None
            self.refresh_lists()
            self._autosave()

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
        subdiv, vol, mode, freq, wav_path, color = vals
        with self.state._lock:
            self.state.left.append(make_layer(subdiv=subdiv, freq=freq, vol=vol, mute=False,
                                              mode=mode, wav_path=wav_path, color=color))
        self.refresh_lists()
        self._autosave()

    def add_to_right(self):
        if not self._update_global_from_inputs():
            return
        vals = self._get_new_layer_vals()
        if not vals: return
        subdiv, vol, mode, freq, wav_path, color = vals
        with self.state._lock:
            self.state.right.append(make_layer(subdiv=subdiv, freq=freq, vol=vol, mute=False,
                                               mode=mode, wav_path=wav_path, color=color))
        self.refresh_lists()
        self._autosave()

    def move_left_to_right(self):
        with self.state._lock:
            idx = self.left_list.selected_index
            if idx is None or not (0 <= idx < len(self.state.left)):
                messagebox.showinfo("Move", "Select a Left layer first.")
                return
            lay = self.state.left.pop(idx)
            self.state.right.append(lay)
        self.refresh_lists()
        self._autosave()

    def move_right_to_left(self):
        with self.state._lock:
            idx = self.right_list.selected_index
            if idx is None or not (0 <= idx < len(self.state.right)):
                messagebox.showinfo("Move", "Select a Right layer first.")
                return
            lay = self.state.right.pop(idx)
            self.state.left.append(lay)
        self.refresh_lists()
        self._autosave()

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
            if s is None:
                return
            duration = float(s)
        except Exception:
            return
        if not duration or duration <= 0:
            return
        path = filedialog.asksaveasfilename(
            title="Save Stereo WAV",
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav")]
        )
        if not path:
            return
        try:
            render_to_wav(path, self.state, duration)
        except Exception as e:
            messagebox.showerror("Save Error", str(e))
            return
        messagebox.showinfo("Saved", f"WAV saved to:\n{path}")

    def on_save_rhythm(self):
        if not self._update_global_from_inputs():
            return
        path = filedialog.asksaveasfilename(
            title="Save Rhythm",
            defaultextension=".json",
            filetypes=[("JSON files","*.json")]
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.state.to_dict(), f, indent=2)
        except Exception as e:
            messagebox.showerror("Save Error", str(e))
            return
        messagebox.showinfo("Saved", f"Rhythm saved to:\n{path}")

    def on_load_rhythm(self):
        path = filedialog.askopenfilename(
            title="Load Rhythm",
            filetypes=[("JSON files","*.json")]
        )
        if not path:
            return
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
        except Exception as e:
            messagebox.showerror("Load Error", str(e))

    def on_new(self):
        with self.state._lock:
            self.state.left.clear()
            self.state.right.clear()
        self.refresh_lists()
        self._autosave()

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
