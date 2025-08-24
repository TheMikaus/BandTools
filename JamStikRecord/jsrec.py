import threading
import time
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Combobox
from tkinter import font as tkfont
from collections import deque, defaultdict

import mido
from music21 import (
    stream, note, chord, duration, meter, tempo,
    instrument, clef, layout, metadata, pitch as m21pitch, tie as m21tie
)

# Optional audio click for metronome
try:
    import pygame
    HAVE_PYGAME = True
except Exception:
    HAVE_PYGAME = False

# -------------------- Helpers / Config --------------------

STANDARD_QL = [4.0, 3.0, 2.0, 1.5, 1.0, 0.75, 0.5, 0.25, 0.125, 0.0625]

# 4/4 bar for metronome behavior and visual gap compression
BEATS_PER_BAR = 4

# Subdivision mapping (how many columns per quarter note)
SUBDIVISION_FACTORS = {
    "Quarter": 1,
    "Eighth": 2,
    "Sixteenth": 4,
    "32nd": 8,
    "64th": 16,
}

# Rough max characters before Notepad @ 12pt wraps (safe default).
MAX_TAB_LINE_CHARS = 90


def quantize_quarter_length(ql: float) -> float:
    return min(STANDARD_QL, key=lambda x: abs(x - ql))


def parse_tuning_cell(text: str) -> int:
    t = text.strip()
    if not t:
        raise ValueError("Empty tuning cell")
    try:
        return int(t)
    except ValueError:
        pass
    p = m21pitch.Pitch(t)
    return p.midi


def cell2(fret: int) -> str:
    """
    Format a fret number into a 2-character cell for the ASCII tab grid.
    - Single-digit: '3-' (no leading space)
    - Two-digit: '12'
    - Negative:  '-1'
    """
    s = str(fret)
    if len(s) == 1:
        return s + "-"
    elif len(s) == 2:
        return s
    else:
        return s[-2:]


class JSRecApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Jamstik Real-Time Tab & MusicXML Recorder (MPE strict)")

        # Device
        self.device_name = self.find_jamstik()
        self.input_port = None

        # State & settings
        self.bpm = tk.StringVar(value="120")
        self.capo_val = tk.StringVar(value="0")
        self.metronome_on = tk.BooleanVar(value=True)
        self.is_recording = False

        # Advance visually only when notes arrive (default: True)
        self.advance_on_notes = tk.BooleanVar(value=True)

        # Some Jamstik profiles map Channel 2 to HIGH E; others to LOW E.
        self.ch2_is_highE = tk.BooleanVar(value=True)

        # Subdivision selection
        self.subdivision = tk.StringVar(value="Quarter")  # Quarter, Eighth, Sixteenth, 32nd, 64th

        # Chord same-column threshold controls
        self.auto_threshold = tk.BooleanVar(value=True)   # default: Auto from subdivision
        self.threshold_ms = tk.StringVar(value="")        # filled by auto updater at startup

        # Tuning entries (1..6; 1=high E)
        default_tunings = ["E4", "B3", "G3", "D3", "A2", "E2"]
        self.tuning_vars = [tk.StringVar(value=default_tunings[i]) for i in range(6)]

        # Visual tab buffer: per string deque of last 20 columns (columns are subdivision units)
        self.columns_window = 20
        self.tab_cols = {s: deque(["--"] * self.columns_window, maxlen=self.columns_window) for s in range(1, 7)}

        # Full recording tab buffer (persists entire take)
        self.full_tab_cols = {s: [] for s in range(1, 7)}
        # Timestamps (seconds from session start) for each full-tab column
        self.full_col_times = []  # one timestamp per column index

        # String number labels & tab labels (monospace for alignment)
        self.string_num_labels = {}
        self.tab_labels = {}
        self.monofont = tkfont.Font(family="Courier New", size=11)

        # Active strings in the current visual column
        self.highlight_strings = set()

        # Recording note events for XML
        self.active_starts = {}   # key: (note, channel) -> (start_time, velocity)
        self.recorded = []        # list of (msg, timestamp) for the current recording

        # Metronome audio (optional)
        self.blip_sound = None
        if HAVE_PYGAME:
            try:
                pygame.mixer.init()
                self.blip_sound = pygame.mixer.Sound("blip.wav")
            except Exception:
                self.blip_sound = None

        # Metronome indicator
        self.metro_indicator = None

        # Timing anchors for visuals & export
        self._session_start = time.time()
        self._last_visual_column_ts = None  # timestamp of last placed column (visual)
        self._beat_counter = 0              # quarter-note count for metronome

        # Quantization grid used for export (quarter lengths)
        self._export_grid_ql = 1.0  # default = quarter
        self._export_first_onset_sec = None

        # Thread controls
        self.running = True
        self.beat_thread = None
        self.midi_thread = None

        # Build UI
        self.build_ui()
        self._update_auto_threshold()  # initialize ms field

        # Start background threads
        self.open_port_if_available()
        self.start_threads()

        # Initial render
        self.render_tab()
        self.update_string_number_labels()

        # On close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # React to BPM/Subdivision changes to refresh auto threshold
        self.bpm.trace_add("write", lambda *args: self._update_auto_threshold())
        self.subdivision.trace_add("write", lambda *args: self._update_auto_threshold())
        self.auto_threshold.trace_add("write", lambda *args: self._update_auto_threshold())

    # ---------- Device discovery ----------
    def find_jamstik(self):
        for name in mido.get_input_names():
            if "jamstik" in name.lower():
                return name
        return None

    def open_port_if_available(self):
        if self.device_name:
            try:
                self.input_port = mido.open_input(self.device_name)
                self.status_var.set(f"Jamstik Found: {self.device_name}")
            except Exception as e:
                self.status_var.set(f"Found Jamstik but failed to open: {e}")
                self.input_port = None
        else:
            self.status_var.set("Jamstik Not Found")

    # ---------- UI ----------
    def build_ui(self):
        top = tk.Frame(self.root)
        top.pack(padx=10, pady=10, fill="x")

        # Status
        self.status_var = tk.StringVar(value="(checking...)")
        tk.Label(top, textvariable=self.status_var, fg="green").grid(row=0, column=0, columnspan=20, sticky="w")

        # MPE mapping toggle
        tk.Checkbutton(
            top,
            text="MPE: Ch.2 = High E (uncheck if Ch.2 = Low E)",
            variable=self.ch2_is_highE
        ).grid(row=1, column=0, columnspan=20, sticky="w", pady=(4, 6))

        # BPM, Capo, Subdivision, Metronome (checkbox), Advance-on-notes, Record
        tk.Label(top, text="BPM:").grid(row=2, column=0, sticky="e")
        tk.Entry(top, width=6, textvariable=self.bpm).grid(row=2, column=1, sticky="w", padx=(4, 10))

        tk.Label(top, text="Capo:").grid(row=2, column=2, sticky="e")
        self.capo_combo = Combobox(top, width=5, textvariable=self.capo_val, values=[str(i) for i in range(0, 13)], state="readonly")
        self.capo_combo.grid(row=2, column=3, sticky="w", padx=(4, 10))

        tk.Label(top, text="Subdivision:").grid(row=2, column=4, sticky="e")
        self.subdiv_combo = Combobox(
            top, width=10, textvariable=self.subdivision,
            values=list(SUBDIVISION_FACTORS.keys()), state="readonly"
        )
        self.subdiv_combo.grid(row=2, column=5, sticky="w", padx=(4, 10))

        # Metronome checkbox + indicator
        tk.Checkbutton(top, text="Metronome", variable=self.metronome_on).grid(row=2, column=6, sticky="w")
        self.metro_indicator = tk.Label(top, text="●", fg="grey")
        self.metro_indicator.grid(row=2, column=7, sticky="w", padx=(6, 4))

        # Advance-on-notes-only checkbox (default True)
        tk.Checkbutton(top, text="Advance on notes only", variable=self.advance_on_notes).grid(row=2, column=8, sticky="w", padx=(10, 0))

        # Chord same-column threshold
        tk.Checkbutton(top, text="Auto chord threshold", variable=self.auto_threshold).grid(row=2, column=9, sticky="w", padx=(10, 0))
        tk.Label(top, text="Threshold (ms):").grid(row=2, column=10, sticky="e")
        tk.Entry(top, width=7, textvariable=self.threshold_ms).grid(row=2, column=11, sticky="w", padx=(4, 10))

        # Record/Stop button
        self.rec_btn = tk.Button(top, text="Record", command=self.toggle_recording)
        self.rec_btn.grid(row=2, column=19, sticky="e")

        # Header row for string grid
        hdr = tk.Frame(self.root)
        hdr.pack(padx=10, pady=(6, 0), fill="x")
        tk.Label(hdr, text="Str", width=4, anchor="w").grid(row=0, column=0, sticky="w")
        tk.Label(hdr, text="Tuning", width=8, anchor="w").grid(row=0, column=1, sticky="w")
        tk.Label(hdr, text="Tab (last 20 columns)", anchor="w").grid(row=0, column=2, sticky="w")

        # Per-string grid
        self.str_frame = tk.Frame(self.root)
        self.str_frame.pack(padx=10, pady=(2, 10), fill="x")

        for s in range(1, 7):
            row = s - 1
            num_lbl = tk.Label(self.str_frame, text=" 1 ", width=4, anchor="w", font=self.monofont)
            num_lbl.grid(row=row, column=0, sticky="w")
            self.string_num_labels[s] = num_lbl

            tk.Entry(self.str_frame, width=8, textvariable=self.tuning_vars[s - 1]).grid(row=row, column=1, sticky="w", padx=(0, 10))

            lbl = tk.Label(self.str_frame, text="", font=("Courier New", 12), anchor="w", justify="left")
            lbl.grid(row=row, column=2, sticky="w")
            self.tab_labels[s] = lbl

        # Bottom controls
        bottom = tk.Frame(self.root)
        bottom.pack(padx=10, pady=(0, 10), fill="x")
        self.clear_btn = tk.Button(bottom, text="Clear Tab", command=self.clear_tab)
        self.clear_btn.pack(side="left")
        self.refresh_btn = tk.Button(bottom, text="Re-open Jamstik", command=self.reopen_device)
        self.refresh_btn.pack(side="right")

    # ---------- Threads ----------
    def start_threads(self):
        # Metronome clock (quarters) and (optionally) time-driven visual advance
        self.beat_thread = threading.Thread(target=self.clock_loop, daemon=True)
        self.beat_thread.start()

        # MIDI listener thread
        self.midi_thread = threading.Thread(target=self.midi_loop, daemon=True)
        self.midi_thread.start()

    def _current_q_len(self) -> float:
        try:
            bpm_val = max(1.0, float(self.bpm.get()))
        except Exception:
            bpm_val = 120.0
        return 60.0 / bpm_val

    def _current_step_len(self) -> float:
        factor = SUBDIVISION_FACTORS.get(self.subdivision.get(), 1)
        return self._current_q_len() / factor

    def _update_auto_threshold(self):
        if self.auto_threshold.get():
            ms = int(round(self._current_step_len() * 1000.0))
            self.threshold_ms.set(str(ms))

    def _get_same_column_threshold_sec(self) -> float:
        if self.auto_threshold.get():
            return self._current_step_len()
        try:
            ms = max(0.0, float(self.threshold_ms.get()))
        except Exception:
            ms = self._current_step_len() * 1000.0
        return ms / 1000.0

    def clock_loop(self):
        next_sub_time = time.time()
        next_q_time = time.time()
        while self.running:
            q_len = self._current_q_len()
            step_len = self._current_step_len()
            now = time.time()

            # Quarter-note metronome (always runs for visuals/audio)
            if now >= next_q_time:
                self._beat_counter += 1
                if self.metronome_on.get():
                    self.root.after(0, lambda: self.metro_indicator.config(fg="red"))
                    if HAVE_PYGAME and self.blip_sound is not None:
                        try:
                            is_downbeat = ((self._beat_counter - 1) % BEATS_PER_BAR == 0)
                            vol = 1.0 if is_downbeat else 0.75
                            self.blip_sound.set_volume(vol)
                            self.blip_sound.play()
                        except Exception:
                            pass
                    self.root.after(100, lambda: self.metro_indicator.config(fg="grey"))
                next_q_time += q_len

            if not self.advance_on_notes.get():
                if now >= next_sub_time:
                    self._append_columns(1, timestamp=now - self._session_start)
                    self.highlight_strings.clear()
                    self.update_string_number_labels()
                    self.root.after(0, self.render_tab)
                    next_sub_time += step_len

            time.sleep(0.005)

    def midi_loop(self):
        self._session_start = time.time()
        while self.running:
            if self.input_port is None:
                time.sleep(0.05)
                continue
            try:
                for msg in self.input_port.iter_pending():
                    if msg.type in ("note_on", "note_off"):
                        ts = time.time() - self._session_start

                        if self.is_recording:
                            self.recorded.append((msg.copy(), ts))
                            key = (msg.note, getattr(msg, "channel", 0))
                            if msg.type == "note_on" and msg.velocity > 0:
                                self.active_starts[key] = (ts, msg.velocity)
                                if self._export_first_onset_sec is None:
                                    self._export_first_onset_sec = ts
                            elif (msg.type == "note_off") or (msg.type == "note_on" and msg.velocity == 0):
                                if key in self.active_starts:
                                    self.active_starts.pop(key, None)

                        if msg.type == "note_on" and msg.velocity > 0:
                            self.place_note_in_tab(msg, ts)

                time.sleep(0.003)
            except Exception:
                time.sleep(0.05)

    # ---------- Mapping / display helpers ----------
    def _norm_member_ch(self, ch):
        if ch is None:
            return None
        if 1 <= ch <= 6:
            return ch
        if 0 <= ch <= 5:
            return ch + 1
        return None

    def get_mpe_map(self):
        if self.ch2_is_highE.get():
            return {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6}
        else:
            return {1: 6, 2: 5, 3: 4, 4: 3, 5: 2, 6: 1}

    def get_open_string_midis(self):
        opens = {}
        for s in range(1, 7):
            txt = self.tuning_vars[s - 1].get()
            opens[s] = parse_tuning_cell(txt)
        return opens

    def update_string_number_labels(self):
        for s in range(1, 7):
            txt = f"-{s}-" if s in self.highlight_strings else f" {s} "
            self.string_num_labels[s].config(text=txt, font=self.monofont)

    # ----- Column append helpers (updates both visual window and full buffer) -----
    def _append_columns(self, n: int, timestamp: float):
        for _ in range(n):
            for s in range(1, 7):
                self.tab_cols[s].append("--")
                self.full_tab_cols[s].append("--")
            self.full_col_times.append(timestamp)

    def _note_driven_gap_and_new_column(self, note_ts: float):
        if self._last_visual_column_ts is None:
            self._append_columns(1, timestamp=note_ts)  # starter gap
            self._append_columns(1, timestamp=note_ts)  # first note column
            self._last_visual_column_ts = note_ts
            self.highlight_strings.clear()
            self.update_string_number_labels()
            return

        if (note_ts - self._last_visual_column_ts) <= self._get_same_column_threshold_sec():
            return

        elapsed_beats = (note_ts - self._last_visual_column_ts) / self._current_q_len()
        gap_cols = 1 if elapsed_beats < BEATS_PER_BAR else 3

        self._append_columns(gap_cols + 1, timestamp=note_ts)
        self._last_visual_column_ts = note_ts

        self.highlight_strings.clear()
        self.update_string_number_labels()

    def place_note_in_tab(self, msg, ts_now: float):
        ch_raw = getattr(msg, "channel", None)
        norm = self._norm_member_ch(ch_raw)
        if norm is None:
            return

        string = self.get_mpe_map().get(norm, None)
        if not string:
            return

        if self.advance_on_notes.get():
            self._note_driven_gap_and_new_column(ts_now)

        opens = self.get_open_string_midis()
        try:
            capo = int(self.capo_val.get())
        except Exception:
            capo = 0

        fret = msg.note - (opens[string] + capo)
        self.tab_cols[string][-1] = cell2(fret)
        if self.full_tab_cols[string]:
            self.full_tab_cols[string][-1] = cell2(fret)

        if string not in self.highlight_strings:
            self.highlight_strings.add(string)
            self.update_string_number_labels()

        self.root.after(0, self.render_tab)

    def render_tab(self):
        for s in range(1, 7):
            row = "".join(self.tab_cols[s])
            self.tab_labels[s].config(text=f"{s}|{row}")

    def clear_tab(self):
        for s in range(1, 7):
            self.tab_cols[s].clear()
            self.tab_cols[s].extend(["--"] * self.columns_window)
        self.highlight_strings.clear()
        self.update_string_number_labels()
        self.render_tab()

    def reopen_device(self):
        if self.input_port is not None:
            try:
                self.input_port.close()
            except Exception:
                pass
        self.device_name = self.find_jamstik()
        self.open_port_if_available()

    # ---------- Record / Stop & Save ----------
    def toggle_recording(self):
        if not self.is_recording:
            self.is_recording = True
            self.rec_btn.config(text="Stop")
            self.recorded.clear()
            self.active_starts.clear()
            self.status_var.set("Recording… (press Stop to save)")
            self._session_start = time.time()
            self._last_visual_column_ts = None
            self._beat_counter = 0
            for s in range(1, 7):
                self.full_tab_cols[s].clear()
            self.full_col_times.clear()
            factor = SUBDIVISION_FACTORS.get(self.subdivision.get(), 1)
            self._export_grid_ql = 1.0 / float(factor)
            self._export_first_onset_sec = None
        else:
            self.is_recording = False
            self.rec_btn.config(text="Record")
            self.status_var.set("Stopped. Saving…")
            self.save_outputs()
            self.status_var.set("Ready")

    # ---------- Save: MusicXML + Tab Text ----------
    def save_outputs(self):
        if not self.recorded:
            messagebox.showinfo("Save", "No events recorded.")
            return

        fp = filedialog.asksaveasfilename(
            defaultextension=".musicxml",
            filetypes=[("MusicXML", "*.musicxml"), ("XML", "*.xml")],
            initialfile="jamstik_take.musicxml",
            title="Save MusicXML (tab text will also be saved)"
        )
        if not fp:
            return
        base, _ = os.path.splitext(fp)
        xml_fp = base + ".musicxml"
        txt_fp = base + ".txt"

        try:
            self._write_musicxml_gp_safe_tied(xml_fp)
        except Exception as e:
            messagebox.showerror("MusicXML Save Error", str(e))
            return

        try:
            self._write_tab_txt_wrapped(txt_fp)
        except Exception as e:
            messagebox.showerror("Tab Save Error", str(e))
            return

        messagebox.showinfo("Saved", f"Saved:\n{xml_fp}\n{txt_fp}")

    def _bar_index_for_time(self, sec_from_start: float) -> int:
        """Zero-based bar index from first onset using 4/4 and BPM."""
        if self._export_first_onset_sec is None:
            return 0
        beats = max(0.0, (sec_from_start - self._export_first_onset_sec) / self._current_q_len())
        return int(beats // BEATS_PER_BAR)

    def _write_tab_txt_wrapped(self, filepath: str):
        """
        Build ASCII tab grouped by bar (from recorded time).
        Starts a new 6-line block whenever adding another bar would exceed MAX_TAB_LINE_CHARS.
        """
        if not self.full_col_times:
            lines = [f"{s}|" for s in range(1, 7)]
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            return

        # Group columns into bars by timestamp
        bars = []  # list of dict string->str (concatenated cells)
        for col_idx, col_ts in enumerate(self.full_col_times):
            bar_idx = self._bar_index_for_time(col_ts)
            while len(bars) <= bar_idx:
                bars.append({s: "" for s in range(1, 7)})
            for s in range(1, 7):
                bars[bar_idx][s] += self.full_tab_cols[s][col_idx]

        # Emit blocks of bars, wrapping to avoid Notepad line wrap
        out_lines = []
        cur_block = {s: f"{s}|" for s in range(1, 7)}
        cur_len = {s: len(cur_block[s]) for s in range(1, 7)}

        for bar in bars:
            bar_len = len(bar[1]) if bar else 0
            would_exceed = any(cur_len[s] + bar_len > MAX_TAB_LINE_CHARS for s in range(1, 7))
            if would_exceed and any(cur_len[s] > len(f"{s}|") for s in range(1, 7)):
                for s in range(1, 7):
                    out_lines.append(cur_block[s])
                out_lines.append("")  # blank line between blocks
                cur_block = {s: f"{s}|" for s in range(1, 7)}
                cur_len = {s: len(cur_block[s]) for s in range(1, 7)}

            for s in range(1, 7):
                cur_block[s] += bar[s]
                cur_len[s] += bar_len

        for s in range(1, 7):
            out_lines.append(cur_block[s])

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(out_lines))

    # ---------- MUSICXML (GP-safe measure-based with ties) ----------
    def _write_musicxml_gp_safe_tied(self, filepath: str):
        """
        GP7-friendly MusicXML with proper quantized durations and ties across barlines.
          - 4/4 measures, one voice.
          - Onsets & durations quantized to the chosen subdivision (nearest).
          - Notes that extend past a bar are split and tied (start/continue/stop).
        """
        opens = self.get_open_string_midis()
        try:
            capo = int(self.capo_val.get())
        except Exception:
            capo = 0

        q_len = self._current_q_len()
        grid = float(self._export_grid_ql)  # quarter-length step captured at record start
        first_onset_sec = self._export_first_onset_sec
        if first_onset_sec is None:
            raise RuntimeError("No note-on events captured.")

        # Build finished notes (pairs)
        starts = {}
        finished = []  # (onset_sec, midi, dur_sec, vel, string, fret)
        mpe_map = self.get_mpe_map()

        for msg, ts in self.recorded:
            if msg.type == "note_on" and msg.velocity > 0:
                starts[(msg.note, getattr(msg, "channel", 0))] = (ts, msg.velocity)
            elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                key = (msg.note, getattr(msg, "channel", 0))
                if key in starts:
                    t0, vel = starts.pop(key)
                    dur_sec = max(0.001, ts - t0)

                    norm = self._norm_member_ch(key[1])
                    string = mpe_map.get(norm, None)
                    if string is None:
                        continue

                    fret = msg.note - (opens[string] + capo)
                    finished.append((t0, msg.note, dur_sec, vel, string, fret))

        if not finished:
            raise RuntimeError("No completed notes to save.")

        # Quantize onsets & durations to grid (nearest), then split across barlines into segments
        # events_by_bar_offset[(bar_idx, offset_in_bar)] = list of (midi, seg_ql, vel, string, fret, tieFlag)
        events_by_bar_offset = defaultdict(list)

        def round_to_grid(x, step):
            if step <= 0:
                return round(x, 6)
            return round(round(x / step) * step, 6)

        def split_into_bar_segments(onset_total_ql, dur_ql):
            """Return list of (bar_idx, offset_in_bar, seg_len_ql) splitting across bars."""
            segs = []
            remaining = dur_ql
            cur = onset_total_ql
            while remaining > 1e-6:
                bar_idx = int(cur // 4.0)
                off_in_bar = round(cur - bar_idx * 4.0, 6)
                rem_in_bar = 4.0 - off_in_bar
                seg = min(remaining, rem_in_bar)
                segs.append((bar_idx, off_in_bar, round(seg, 6)))
                cur += seg
                remaining -= seg
            return segs

        for t0, midi_val, dur_sec, vel, string, fret in finished:
            onset_ql = (t0 - first_onset_sec) / q_len
            onset_ql_q = round_to_grid(onset_ql, grid)
            raw_dur_ql = max(grid if grid > 0 else 0.0625, dur_sec / q_len)
            dur_ql_q = round_to_grid(raw_dur_ql, grid)

            # ensure at least one grid step
            if grid > 0 and dur_ql_q < grid:
                dur_ql_q = grid

            segments = split_into_bar_segments(onset_ql_q, dur_ql_q)
            # tie flags
            if len(segments) == 1:
                flags = [None]
            else:
                flags = ['start'] + (['continue'] * (len(segments) - 2)) + ['stop']

            for (seg, flag) in zip(segments, flags):
                bar_idx, off_in_bar, seg_len = seg
                events_by_bar_offset[(bar_idx, off_in_bar)].append(
                    (midi_val, seg_len, vel, string, fret, flag)
                )

        # Build Part with 4/4 measures
        part = stream.Part(id="Guitar")
        part.insert(0, instrument.Guitar())
        part.insert(0, clef.TabClef())
        part.insert(0, layout.StaffLayout(staffLines=6))
        try:
            bpm_val = max(1.0, float(self.bpm.get()))
        except Exception:
            bpm_val = 120.0
        part.insert(0.0, tempo.MetronomeMark(number=bpm_val))
        part.insert(0.0, meter.TimeSignature("4/4"))
        part.insert(0.0, metadata.Metadata(title="Jamstik Session"))

        # Determine bar range
        max_bar_idx = 0
        if events_by_bar_offset:
            max_bar_idx = max(b for (b, off) in events_by_bar_offset.keys())

        # Create measures sequentially, placing events at offsets and filling any leading/trailing real silence with rests
        for bar_idx in range(0, max_bar_idx + 1):
            m = stream.Measure(number=bar_idx + 1)
            time_in_bar = 0.0

            # get offsets in this bar
            offs = sorted(off for (b, off) in events_by_bar_offset.keys() if b == bar_idx)

            for off in offs:
                # leading rest if needed
                gap = round(off - time_in_bar, 6)
                if gap > 0.0:
                    r = note.Rest()
                    r.duration = duration.Duration(gap)
                    m.append(r)
                    time_in_bar += gap

                # collect notes at this offset
                items = events_by_bar_offset[(bar_idx, off)]
                # Build a chord of individual Notes (each can carry its own tie)
                chord_notes = []
                for midi_val, seg_len, vel, string, fret, tie_flag in items:
                    n = note.Note()
                    n.pitch.midi = midi_val
                    n.duration = duration.Duration(seg_len)
                    n.volume.velocity = int(max(1, min(127, vel)))
                    n.lyric = str(fret)  # hint for tab importers

                    if tie_flag in ('start', 'continue', 'stop'):
                        n.tie = m21tie.Tie(tie_flag)

                    chord_notes.append(n)

                if len(chord_notes) == 1:
                    m.append(chord_notes[0])
                    time_in_bar += float(chord_notes[0].duration.quarterLength)
                else:
                    ch = chord.Chord(chord_notes)
                    m.append(ch)
                    time_in_bar += float(ch.duration.quarterLength)

            # Trailing rest to fill bar to exactly 4.0 ql (only if needed)
            if time_in_bar < 4.0:
                pad = round(4.0 - time_in_bar, 6)
                if pad > 0:
                    r = note.Rest()
                    r.duration = duration.Duration(pad)
                    m.append(r)

            part.append(m)

        score = stream.Score(id="Score")
        score.append(part)
        score.write("musicxml", fp=filepath)

    # ---------- Shutdown ----------
    def on_close(self):
        self.running = False
        try:
            if self.input_port is not None:
                self.input_port.close()
        except Exception:
            pass
        self.root.after(200, self.root.destroy)


if __name__ == "__main__":
    root = tk.Tk()
    app = JSRecApp(root)
    root.mainloop()
