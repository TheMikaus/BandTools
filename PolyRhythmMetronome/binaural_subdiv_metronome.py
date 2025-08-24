#!/usr/bin/env python3
"""
Stereo Subdivision Metronome
- Left and right ears can use different note subdivisions.
- Beat 1 of each measure is accented.
- Play runs audio on a separate thread from the UI.
- Save creates a stereo WAV for a user-defined duration.
- Will auto-install numpy and simpleaudio if missing.

Run:
    python binaural_subdiv_metronome.py
"""

import sys, subprocess, importlib
import threading
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import wave

# ---------- Auto-install missing packages ---------- #

def ensure_pkg(pkg_name: str, import_name: str = None):
    """
    Try importing a package; if missing, install via pip and import again.
    Returns the imported module on success, or raises the original ImportError.
    """
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

# numpy is required for the app to run at all
np = ensure_pkg("numpy")

# simpleaudio is optional until playback; we'll try to ensure it now but handle failure gracefully
try:
    sa = ensure_pkg("simpleaudio")
except ImportError:
    sa = None


# ---------------- Audio/Synthesis Helpers ---------------- #

SAMPLE_RATE = 44100
BASE_AMP = 0.22      # normal note loudness
ACCENT_AMP = 0.36    # slightly louder for beat 1
BLIP_MS = 55         # blip duration in milliseconds
FADE_MS = 5          # attack/release fade to avoid clicks

LEFT_FREQ = 880.0    # left-ear blip frequency (A5-ish)
RIGHT_FREQ = 1320.0  # right-ear blip frequency (E6-ish)


def _unit_tone(freq: float, dur_ms: int, sr: int = SAMPLE_RATE):
    """Generate a mono unit-amplitude tone with a short fade in/out."""
    n = int(sr * (dur_ms / 1000.0))
    t = np.arange(n, dtype=np.float32) / sr
    tone = np.sin(2 * np.pi * freq * t).astype(np.float32)

    # Linear fade in/out
    fade_n = max(1, int(sr * (min(FADE_MS, dur_ms / 2) / 1000.0)))
    env = np.ones(n, dtype=np.float32)
    env[:fade_n] = np.linspace(0.0, 1.0, fade_n, dtype=np.float32)
    env[-fade_n:] = np.linspace(1.0, 0.0, fade_n, dtype=np.float32)

    return tone * env  # unit amplitude (scale later)


UNIT_LEFT = _unit_tone(LEFT_FREQ, BLIP_MS)   # mono unit wave
UNIT_RIGHT = _unit_tone(RIGHT_FREQ, BLIP_MS) # mono unit wave


def _make_stereo_frame(left_amp: float, right_amp: float):
    """
    Build a short stereo frame for a blip event by scaling the precomputed unit tones.
    Returns float32 array shape (N, 2).
    """
    n = max(len(UNIT_LEFT), len(UNIT_RIGHT))
    l = np.zeros(n, dtype=np.float32)
    r = np.zeros(n, dtype=np.float32)

    # Add scaled unit tones (if amp is zero that side is silent)
    if left_amp != 0.0:
        if len(UNIT_LEFT) == n:
            l += left_amp * UNIT_LEFT
        else:
            l[:len(UNIT_LEFT)] += left_amp * UNIT_LEFT
    if right_amp != 0.0:
        if len(UNIT_RIGHT) == n:
            r += right_amp * UNIT_RIGHT
        else:
            r[:len(UNIT_RIGHT)] += right_amp * UNIT_RIGHT

    return np.stack([l, r], axis=1)  # (n, 2)


def _float_to_int16(stereo):
    """Clip to [-1, 1] and convert to int16 interleaved stereo."""
    stereo = np.clip(stereo, -1.0, 1.0)
    return (stereo * 32767.0).astype(np.int16)


# ------------- Subdivision / Timing Math ----------------- #

def notes_per_beat_from_input(n: int) -> float:
    """
    Interprets the user's subdivision input.
    - Powers of two are treated as note denominators (whole=1, half=2, quarter=4, eighth=8, etc.):
        e.g., 4 -> 1 per beat (quarter), 8 -> 2 per beat (eighth), 16 -> 4 per beat (sixteenth)
    - Other integers (3, 5, 7, 10, 12...) are treated as tuplets per beat:
        e.g., 3 -> triplets, 5 -> quintuplets, 12 -> 12-tuplets (often 16th-note triplets)
    """
    if n in (1, 2, 4, 8, 16, 32, 64):
        return n / 4.0
    elif n > 0:
        return float(n)
    else:
        raise ValueError("Subdivision must be a positive integer.")


def interval_seconds(bpm: float, subdiv: int) -> float:
    """Time between blips for a given BPM and subdivision scheme (seconds)."""
    if bpm <= 0:
        raise ValueError("BPM must be > 0.")
    beat_len = 60.0 / bpm
    per_beat = notes_per_beat_from_input(subdiv)
    return beat_len / per_beat


def measure_seconds(bpm: float, beats_per_measure: int) -> float:
    if beats_per_measure <= 0:
        raise ValueError("Beats per measure must be > 0.")
    return (60.0 / bpm) * float(beats_per_measure)


# ----------------- Playback Thread ---------------------- #

class MetronomePlayer:
    def __init__(self, get_params_callable):
        """
        get_params_callable() should return a dict with:
        {
          'bpm': float, 'left_subdiv': int, 'right_subdiv': int,
          'beats_per_measure': int
        }
        """
        self._get_params = get_params_callable
        self._thread = None
        self._stop_flag = threading.Event()

    def is_playing(self):
        return self._thread is not None and self._thread.is_alive()

    def stop(self):
        if self._thread and self._thread.is_alive():
            self._stop_flag.set()
            self._thread.join(timeout=1.0)
        self._thread = None
        self._stop_flag.clear()

    def start(self):
        global sa
        if sa is None:
            # Try one more time to install simpleaudio now that the UI is up
            try:
                sa = ensure_pkg("simpleaudio")
            except ImportError:
                messagebox.showerror(
                    "Audio Error",
                    "The 'simpleaudio' package is not available and could not be auto-installed.\n\n"
                    "Please install it manually:\n\npip install simpleaudio"
                )
                return
        if self.is_playing():
            return
        self._stop_flag.clear()
        self._thread = threading.Thread(target=self._run, name="MetronomeAudioThread", daemon=True)
        self._thread.start()

    def _run(self):
        try:
            params = self._get_params()
            bpm = float(params['bpm'])
            l_sub = int(params['left_subdiv'])
            r_sub = int(params['right_subdiv'])
            bpm_measure = int(params['beats_per_measure'])

            left_iv = interval_seconds(bpm, l_sub)
            right_iv = interval_seconds(bpm, r_sub)
            meas_len = measure_seconds(bpm, bpm_measure)

            # schedule
            t0 = time.perf_counter()
            next_left = 0.0
            next_right = 0.0
            tol = 1e-4  # time-match tolerance for coincident events & measure boundary

            while not self._stop_flag.is_set():
                # pick next event time and which sides fire
                next_t = min(next_left, next_right)
                left_now = abs(next_left - next_t) < tol
                right_now = abs(next_right - next_t) < tol

                # Accent if this event falls on (or extremely near) a measure boundary
                # Using modulo tolerance for floating point drift.
                on_measure_boundary = (abs((next_t % meas_len)) < tol) or (abs((meas_len - (next_t % meas_len)) % meas_len) < tol)

                l_amp = (ACCENT_AMP if on_measure_boundary and left_now else BASE_AMP) if left_now else 0.0
                r_amp = (ACCENT_AMP if on_measure_boundary and right_now else BASE_AMP) if right_now else 0.0

                # Sleep until it's time for the event
                target_time = t0 + next_t
                while True:
                    now = time.perf_counter()
                    dt = target_time - now
                    if dt <= 0:
                        break
                    # sleep in small increments to improve timing (still not sample-accurate)
                    time.sleep(min(0.001, dt))

                # Build and play the stereo frame (one combined blip if both sides fire)
                frame = _make_stereo_frame(l_amp, r_amp)
                int16 = _float_to_int16(frame)
                # Interleaved bytes: channels=2, bytes_per_sample=2
                sa.play_buffer(int16.tobytes(), 2, 2, SAMPLE_RATE)

                # Advance whichever side(s) fired
                if left_now:
                    next_left += left_iv
                if right_now:
                    next_right += right_iv

                # Guard against runaway drift if one side lags far behind for some reason
                # (Shouldn't normally happen. This ensures forward progress.)
                max_ahead = 10.0  # seconds
                base_t = min(next_left, next_right)
                if next_left - base_t > max_ahead:
                    next_left = base_t + left_iv
                if next_right - base_t > max_ahead:
                    next_right = base_t + right_iv

        except Exception as e:
            # Surface any error to the UI thread safely
            def show_err():
                messagebox.showerror("Playback Error", str(e))
            try:
                root.after(0, show_err)
            except Exception:
                pass


# -------------------- Save to WAV ----------------------- #

def render_to_wav(path: str, bpm: float, left_subdiv: int, right_subdiv: int, beats_per_measure: int, duration_sec: float):
    if duration_sec <= 0:
        raise ValueError("Duration must be > 0 seconds.")

    left_iv = interval_seconds(bpm, left_subdiv)
    right_iv = interval_seconds(bpm, right_subdiv)
    meas_len = measure_seconds(bpm, beats_per_measure)
    tol = 1e-6

    total_samples = int(SAMPLE_RATE * duration_sec)
    stereo = np.zeros((total_samples, 2), dtype=np.float32)

    def add_frame(start_s: float, left_amp: float, right_amp: float):
        start_idx = int(round(start_s * SAMPLE_RATE))
        if start_idx >= total_samples:
            return
        frame = _make_stereo_frame(left_amp, right_amp)
        end_idx = min(total_samples, start_idx + frame.shape[0])
        # Add (mix), respecting end boundary
        length = end_idx - start_idx
        if length > 0:
            stereo[start_idx:end_idx, :] += frame[:length, :]

    # Schedule events
    tL = 0.0
    tR = 0.0
    while True:
        t = min(tL, tR)
        if t >= duration_sec:
            break
        Lnow = abs(tL - t) < tol
        Rnow = abs(tR - t) < tol
        on_measure_boundary = (abs((t % meas_len)) < tol) or (abs((meas_len - (t % meas_len)) % meas_len) < tol)
        l_amp = (ACCENT_AMP if on_measure_boundary and Lnow else BASE_AMP) if Lnow else 0.0
        r_amp = (ACCENT_AMP if on_measure_boundary and Rnow else BASE_AMP) if Rnow else 0.0
        add_frame(t, l_amp, r_amp)
        if Lnow: tL += left_iv
        if Rnow: tR += right_iv

    # Clip and write
    int16 = _float_to_int16(stereo)
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(int16.tobytes())


# ------------------------ UI ---------------------------- #

class App(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=12)
        master.title("Stereo Subdivision Metronome")
        master.protocol("WM_DELETE_WINDOW", self.on_close)

        # Vars
        self.var_bpm = tk.StringVar(value="120")
        self.var_left = tk.StringVar(value="4")
        self.var_right = tk.StringVar(value="4")
        self.var_beats_per_measure = tk.StringVar(value="4")
        self.var_save_seconds = tk.StringVar(value="30")

        # Layout
        grid = ttk.Frame(self)
        grid.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        r = 0
        ttk.Label(grid, text="BPM:").grid(row=r, column=0, sticky="e", padx=4, pady=4)
        ttk.Entry(grid, textvariable=self.var_bpm, width=8).grid(row=r, column=1, sticky="w")

        ttk.Label(grid, text="Beats / Measure:").grid(row=r, column=2, sticky="e", padx=12)
        ttk.Entry(grid, textvariable=self.var_beats_per_measure, width=8).grid(row=r, column=3, sticky="w")
        r += 1

        ttk.Label(grid, text="Left Subdivision:").grid(row=r, column=0, sticky="e", padx=4, pady=4)
        ttk.Entry(grid, textvariable=self.var_left, width=8).grid(row=r, column=1, sticky="w")
        ttk.Label(grid, text="(e.g., 4=quarters, 8=eighths, 16=sixteenths, 3=triplets)").grid(row=r, column=2, columnspan=2, sticky="w")
        r += 1

        ttk.Label(grid, text="Right Subdivision:").grid(row=r, column=0, sticky="e", padx=4, pady=4)
        ttk.Entry(grid, textvariable=self.var_right, width=8).grid(row=r, column=1, sticky="w")
        r += 1

        # Buttons
        btns = ttk.Frame(self)
        btns.grid(row=1, column=0, pady=(12, 0), sticky="ew")
        btns.columnconfigure(0, weight=1)
        btns.columnconfigure(1, weight=1)
        btns.columnconfigure(2, weight=1)

        self.btn_play = ttk.Button(btns, text="Play", command=self.on_play)
        self.btn_stop = ttk.Button(btns, text="Stop", command=self.on_stop)
        self.btn_save = ttk.Button(btns, text="Save WAV…", command=self.on_save)

        self.btn_play.grid(row=0, column=0, padx=4, sticky="ew")
        self.btn_stop.grid(row=0, column=1, padx=4, sticky="ew")
        self.btn_save.grid(row=0, column=2, padx=4, sticky="ew")

        # Save options
        save_opts = ttk.Frame(self)
        save_opts.grid(row=2, column=0, pady=(10,0), sticky="ew")
        ttk.Label(save_opts, text="WAV Duration (sec):").grid(row=0, column=0, sticky="e")
        ttk.Entry(save_opts, textvariable=self.var_save_seconds, width=8).grid(row=0, column=1, sticky="w")
        ttk.Label(save_opts, text="(stereo, accented beat 1)").grid(row=0, column=2, sticky="w", padx=8)

        self.pack(fill="both", expand=True)

        # Player
        self.player = MetronomePlayer(self._collect_params)

    def _collect_params(self):
        # Validate & collect from UI
        bpm = float(self.var_bpm.get())
        left_subdiv = int(self.var_left.get())
        right_subdiv = int(self.var_right.get())
        beats_per_measure = int(self.var_beats_per_measure.get())

        # Validate by computing intervals (will raise if invalid)
        _ = interval_seconds(bpm, left_subdiv)
        _ = interval_seconds(bpm, right_subdiv)
        _ = measure_seconds(bpm, beats_per_measure)

        return {
            'bpm': bpm,
            'left_subdiv': left_subdiv,
            'right_subdiv': right_subdiv,
            'beats_per_measure': beats_per_measure,
        }

    def on_play(self):
        try:
            _ = self._collect_params()  # validation pass
        except Exception as e:
            messagebox.showerror("Invalid Input", str(e))
            return
        self.player.start()

    def on_stop(self):
        self.player.stop()

    def on_save(self):
        try:
            params = self._collect_params()
            duration = float(self.var_save_seconds.get())
        except Exception as e:
            messagebox.showerror("Invalid Input", str(e))
            return

        path = filedialog.asksaveasfilename(
            title="Save Stereo WAV",
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav")]
        )
        if not path:
            return

        # Render and save
        try:
            render_to_wav(path,
                          bpm=params['bpm'],
                          left_subdiv=params['left_subdiv'],
                          right_subdiv=params['right_subdiv'],
                          beats_per_measure=params['beats_per_measure'],
                          duration_sec=duration)
        except Exception as e:
            messagebox.showerror("Save Error", str(e))
            return

        messagebox.showinfo("Saved", f"WAV saved to:\n{path}")

    def on_close(self):
        self.on_stop()
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    # Native-like theming if available
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
