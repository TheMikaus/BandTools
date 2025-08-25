#!/usr/bin/env python3
"""
Stereo Subdivision Metronome — Multi-Layer per Ear (Streaming backend)
- Multiple layers per ear with subdivision, frequency, volume, mute.
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

import sys, subprocess, importlib, traceback
import json, os, time, threading, math
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
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
BLIP_MS = 55
FADE_MS = 5
BASE_AMP = 0.22
ACCENT_AMP = 0.36
TOL = 1e-4      # seconds tolerance for event alignment
TOL_SAMPLES = 2 # samples tolerance for measure boundary detection
TOL_SAVE = 1e-6 # for offline render


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


# -------------------- Tone Cache / DSP --------------------- #

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


def float_to_int16(stereo: np.ndarray) -> np.ndarray:
    stereo = np.clip(stereo, -1.0, 1.0)
    return (stereo * 32767.0).astype(np.int16)


# ---------------------- Data Structures -------------------- #

def make_layer(subdiv=4, freq=880.0, vol=1.0, mute=False):
    return {"subdiv": int(subdiv), "freq": float(freq), "vol": float(vol), "mute": bool(mute)}


class RhythmState:
    def __init__(self):
        self.bpm = 120.0
        self.beats_per_measure = 4
        self.left = []   # list of layers
        self.right = []  # list of layers
        self._lock = threading.RLock()

    def to_dict(self):
        with self._lock:
            return {
                "bpm": self.bpm,
                "beats_per_measure": self.beats_per_measure,
                "left": self.left,
                "right": self.right,
            }

    def from_dict(self, d):
        with self._lock:
            self.bpm = float(d.get("bpm", 120.0))
            self.beats_per_measure = int(d.get("beats_per_measure", 4))
            self.left = [make_layer(**x) for x in d.get("left", [])]
            self.right = [make_layer(**x) for x in d.get("right", [])]


# ------------------------ Streaming Engine --------------------- #

class StreamEngine:
    """
    Preferred backend using sounddevice stream callback for stable playback.
    Freezes the configuration at start() for deterministic timing.
    """
    def __init__(self, rhythm_state: RhythmState, ui_after_callable):
        self.rhythm = rhythm_state
        self.ui_after = ui_after_callable
        self.stream = None
        self.running = False
        self.tones = ToneCache()
        self._lock = threading.RLock()

        # Scheduling state (set on start)
        self.left_layers = []
        self.right_layers = []
        self.L_intervals = []
        self.R_intervals = []
        self.L_next = []
        self.R_next = []
        self.measure_samples = 0
        self.sample_counter = 0  # running sample position

        # Active blips: each is dict with 'data' (mono tone), 'idx', 'amp', 'channel' (0=L,1=R)
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
                    blocksize=0,  # let the system choose
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

    # ---- sounddevice callback ----
    def _callback(self, outdata, frames, time_info, status):
        try:
            block = np.zeros((frames, 2), dtype=np.float32)
            sr = SAMPLE_RATE
            t0 = self.sample_counter
            t1 = t0 + frames

            # Schedule any events that fall within this block
            def schedule_side(layers, intervals, next_times, channel):
                for i, lay in enumerate(layers):
                    if lay.get("mute", False):  # skip muted
                        continue
                    iv = intervals[i]
                    iv_samples = iv * sr
                    # Pull events into this block
                    while True:
                        t_sec = next_times[i]
                        ev_sample = int(round(t_sec * sr))
                        if ev_sample >= t1:
                            break
                        if ev_sample >= t0:
                            # Accent on measure boundary
                            accent = False
                            if self.measure_samples > 0:
                                r = ev_sample % self.measure_samples
                                accent = (r <= TOL_SAMPLES or (self.measure_samples - r) <= TOL_SAMPLES)
                            amp = (ACCENT_AMP if accent else BASE_AMP) * float(lay["vol"])
                            freq = float(lay["freq"])
                            tone = self.tones.get(freq)
                            # Add to active
                            self.active.append({
                                "data": tone,
                                "idx": 0,
                                "amp": amp,
                                "channel": channel
                            })
                        next_times[i] = t_sec + iv

            schedule_side(self.left_layers, self.L_intervals, self.L_next, 0)
            schedule_side(self.right_layers, self.R_intervals, self.R_next, 1)

            # Mix active blips into block
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
            # Log and stop the stream gracefully instead of killing the app
            with open("metronome_log.txt", "a", encoding="utf-8") as f:
                f.write("=== Exception in sounddevice callback ===\n")
                traceback.print_exc(file=f)
            outdata[:] = 0
            raise

    # ---- simpleaudio fallback loop (less robust than streaming, but OK) ----
    def _sa_loop(self):
        try:
            tones = self.tones
            sr = SAMPLE_RATE
            handles = deque(maxlen=512)

            # convert times to seconds; keep base time
            start = time.perf_counter()

            while self.running:
                # Determine next event time across all layers
                candidates = []
                if self.L_next: candidates.append(min(self.L_next))
                if self.R_next: candidates.append(min(self.R_next))
                if not candidates:
                    time.sleep(0.01)
                    continue
                next_t = min(candidates)

                # Prepare events
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
                            amp = (ACCENT_AMP if accent else BASE_AMP) * float(lay["vol"])
                            left_events.append((float(lay["freq"]), amp))
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
                            amp = (ACCENT_AMP if accent else BASE_AMP) * float(lay["vol"])
                            right_events.append((float(lay["freq"]), amp))
                        self.R_next[i] = t_ev + self.R_intervals[i]

                # Sleep until wall-clock target
                target = start + next_t
                while True:
                    now = time.perf_counter()
                    dt = target - now
                    if dt <= 0: break
                    time.sleep(min(0.001, dt))

                # Build one combined stereo frame
                n = int(sr * (BLIP_MS / 1000.0))
                frame = np.zeros((n, 2), dtype=np.float32)
                for freq, amp in left_events:
                    tone = tones.get(freq)
                    L = min(n, len(tone))
                    frame[:L, 0] += amp * tone[:L]
                for freq, amp in right_events:
                    tone = tones.get(freq)
                    L = min(n, len(tone))
                    frame[:L, 1] += amp * tone[:L]

                int16 = float_to_int16(frame)
                try:
                    h = sa.play_buffer(int16, 2, 2, sr)  # pass numpy array if supported
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
    if duration_sec <= 0:
        raise ValueError("Duration must be > 0.")
    with state._lock:
        bpm = float(state.bpm)
        beats_per_measure = int(state.beats_per_measure)
        left_layers = [dict(x) for x in state.left]
        right_layers = [dict(x) for x in state.right]

    meas_len = measure_seconds(bpm, beats_per_measure)

    def make_side(layers):
        intervals = [interval_seconds(bpm, lay["subdiv"]) for lay in layers]
        next_times = [0.0 for _ in layers]
        return intervals, next_times

    L_intervals, L_next = make_side(left_layers)
    R_intervals, R_next = make_side(right_layers)

    total_samples = int(SAMPLE_RATE * duration_sec)
    stereo = np.zeros((total_samples, 2), dtype=np.float32)
    tone_cache = ToneCache()

    def add_events_at(time_s, left_events, right_events):
        start_idx = int(round(time_s * SAMPLE_RATE))
        if start_idx >= total_samples:
            return
        n = int(SAMPLE_RATE * (BLIP_MS / 1000.0))
        end_idx = min(total_samples, start_idx + n)
        length = end_idx - start_idx
        if length <= 0:
            return
        # Mix
        for freq, amp in left_events:
            tone = tone_cache.get(freq)
            L = min(length, len(tone))
            stereo[start_idx:start_idx+L, 0] += amp * tone[:L]
        for freq, amp in right_events:
            tone = tone_cache.get(freq)
            L = min(length, len(tone))
            stereo[start_idx:start_idx+L, 1] += amp * tone[:L]

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

        left_events = []
        right_events = []

        for i, tn in enumerate(L_next):
            if abs(tn - t) < TOL_SAVE:
                lay = left_layers[i]
                if not lay.get("mute", False):
                    # accent?
                    ev_samp = int(round(t * SAMPLE_RATE))
                    accent = False
                    meas_samples = int(round(meas_len * SAMPLE_RATE)) if meas_len > 0 else 0
                    if meas_samples > 0:
                        r = ev_samp % meas_samples
                        accent = (r <= TOL_SAMPLES or (meas_samples - r) <= TOL_SAMPLES)
                    amp = (ACCENT_AMP if accent else BASE_AMP) * float(lay["vol"])
                    left_events.append((float(lay["freq"]), amp))
                L_next[i] += L_intervals[i]
        for i, tn in enumerate(R_next):
            if abs(tn - t) < TOL_SAVE:
                lay = right_layers[i]
                if not lay.get("mute", False):
                    ev_samp = int(round(t * SAMPLE_RATE))
                    accent = False
                    meas_samples = int(round(meas_len * SAMPLE_RATE)) if meas_len > 0 else 0
                    if meas_samples > 0:
                        r = ev_samp % meas_samples
                        accent = (r <= TOL_SAMPLES or (meas_samples - r) <= TOL_SAMPLES)
                    amp = (ACCENT_AMP if accent else BASE_AMP) * float(lay["vol"])
                    right_events.append((float(lay["freq"]), amp))
                R_next[i] += R_intervals[i]

        if left_events or right_events:
            add_events_at(t, left_events, right_events)

    # write wav
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
    Scrollable list of layer rows with:
      [checkbox mute]  text  (Select)
      [Delete]
    Supports selecting a single row by click to enable moving between lists.
    """
    def __init__(self, master, title):
        super().__init__(master, padding=(6,6))
        ttk.Label(self, text=title, font=("Segoe UI", 10, "bold")).pack(anchor="w")

        self.canvas = tk.Canvas(self, height=220, highlightthickness=0)
        self.inner = ttk.Frame(self.canvas)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.create_window((0,0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # State
        self.rows = []  # list of dicts: {"frame":..., "mute_var":..., "index": int}
        self.selected_index = None

        # keyboard scroll
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, e):
        if self.winfo_ismapped():
            self.canvas.yview_scroll(int(-1*(e.delta/120)), "units")

    def clear(self):
        for row in self.rows:
            row["frame"].destroy()
        self.rows.clear()
        self.selected_index = None

    def rebuild(self, layers, on_toggle_mute, on_delete, on_select):
        self.clear()
        for idx, layer in enumerate(layers):
            fr = ttk.Frame(self.inner, padding=(2,2))
            fr.pack(fill="x", expand=True, pady=2)

            mute_var = tk.BooleanVar(value=bool(layer.get("mute", False)))
            cb = ttk.Checkbutton(fr, variable=mute_var, command=lambda i=idx, v=mute_var: on_toggle_mute(i, v.get()))
            cb.pack(side="left")

            text = f"subdiv={layer['subdiv']}  freq={layer['freq']}Hz  vol={layer['vol']:.2f}"
            lbl = ttk.Label(fr, text=text)
            lbl.pack(side="left", padx=6)
            # click to select
            def make_select(i):
                return lambda e=None: on_select(i)
            lbl.bind("<Button-1>", make_select(idx))
            fr.bind("<Button-1>", make_select(idx))

            del_btn = ttk.Button(fr, text="Delete", width=7, command=lambda i=idx: on_delete(i))
            del_btn.pack(side="right")

            self.rows.append({"frame": fr, "mute_var": mute_var, "index": idx})

    def highlight(self, index):
        # un-highlight
        for i, row in enumerate(self.rows):
            for w in (row["frame"],):
                w.configure(style="")
        # highlight
        if index is not None and 0 <= index < len(self.rows):
            self.rows[index]["frame"].configure(style="SelectedRow.TFrame")
            self.selected_index = index
        else:
            self.selected_index = None


class App(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=10)
        master.title("Stereo Subdivision Metronome — Multi-Layer (Streaming)")
        master.protocol("WM_DELETE_WINDOW", self.on_close)

        # styles
        style = ttk.Style()
        style.configure("SelectedRow.TFrame", background="#dbeafe")  # light blue

        # State & engine
        self.state = RhythmState()
        self.engine = StreamEngine(self.state, ui_after_callable=lambda cb: self.after(0, cb))
        self._load_autosave_if_exists()

        # ---------- Top Controls ----------
        top = ttk.Frame(self)
        top.grid(row=0, column=0, sticky="ew")
        for c in range(8):
            top.columnconfigure(c, weight=1)

        ttk.Label(top, text="BPM:").grid(row=0, column=0, sticky="e", padx=4, pady=4)
        self.var_bpm = tk.StringVar(value=str(self.state.bpm))
        ttk.Entry(top, textvariable=self.var_bpm, width=7).grid(row=0, column=1, sticky="w")

        ttk.Label(top, text="Beats/Measure:").grid(row=0, column=2, sticky="e", padx=(8,4))
        self.var_bpmmeasure = tk.StringVar(value=str(self.state.beats_per_measure))
        ttk.Entry(top, textvariable=self.var_bpmmeasure, width=7).grid(row=0, column=3, sticky="w")

        # New layer inputs
        ttk.Label(top, text="Subdivision:").grid(row=1, column=0, sticky="e", padx=4, pady=4)
        self.var_subdiv = tk.StringVar(value="4")
        ttk.Entry(top, textvariable=self.var_subdiv, width=7).grid(row=1, column=1, sticky="w")

        ttk.Label(top, text="Frequency (Hz):").grid(row=1, column=2, sticky="e")
        self.var_freq = tk.StringVar(value="880")
        ttk.Entry(top, textvariable=self.var_freq, width=7).grid(row=1, column=3, sticky="w")

        ttk.Label(top, text="Volume (0..1):").grid(row=1, column=4, sticky="e")
        self.var_vol = tk.StringVar(value="1.0")
        ttk.Entry(top, textvariable=self.var_vol, width=7).grid(row=1, column=5, sticky="w")

        ttk.Button(top, text="Add to Left", command=self.add_to_left).grid(row=1, column=6, sticky="ew", padx=(8,2))
        ttk.Button(top, text="Add to Right", command=self.add_to_right).grid(row=1, column=7, sticky="ew", padx=(2,0))

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
    def _get_new_layer_vals(self):
        try:
            subdiv = int(self.var_subdiv.get())
            freq = float(self.var_freq.get())
            vol = float(self.var_vol.get())
            if vol < 0: vol = 0.0
            if vol > 1: vol = 1.0
            # Validate timing math early
            _ = interval_seconds(float(self.var_bpm.get()), subdiv)
            return subdiv, freq, vol
        except Exception as e:
            messagebox.showerror("Invalid Layer", str(e))
            return None

    def _update_global_from_inputs(self):
        try:
            self.state.bpm = float(self.var_bpm.get())
            self.state.beats_per_measure = int(self.var_bpmmeasure.get())
            # Validate
            _ = measure_seconds(self.state.bpm, self.state.beats_per_measure)
        except Exception as e:
            messagebox.showerror("Invalid Settings", str(e))
            return False
        self._autosave()
        return True

    def refresh_lists(self):
        # Handlers for left
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

        # Handlers for right
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

        # Rebuild UI lists
        with self.state._lock:
            left_layers = list(self.state.left)
            right_layers = list(self.state.right)

        self.left_list.rebuild(left_layers, L_toggle_mute, L_delete, L_select)
        self.right_list.rebuild(right_layers, R_toggle_mute, R_delete, R_select)

    # ---------- UI Actions ----------
    def add_to_left(self):
        if not self._update_global_from_inputs():
            return
        vals = self._get_new_layer_vals()
        if not vals: return
        subdiv, freq, vol = vals
        with self.state._lock:
            self.state.left.append(make_layer(subdiv=subdiv, freq=freq, vol=vol, mute=False))
        self.refresh_lists()
        self._autosave()

    def add_to_right(self):
        if not self._update_global_from_inputs():
            return
        vals = self._get_new_layer_vals()
        if not vals: return
        subdiv, freq, vol = vals
        with self.state._lock:
            self.state.right.append(make_layer(subdiv=subdiv, freq=freq, vol=vol, mute=False))
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
    # Theme
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
