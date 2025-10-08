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

# ---------------- Constants ---------------- #

SAMPLE_RATE = 44100
BASE_AMP = 0.22
DEFAULT_ACCENT_FACTOR = 1.6
FLASH_DURATION = 0.12  # seconds
AUTOSAVE_FILE = "metronome_autosave.json"

# BPM presets for quick access
BPM_PRESETS = [60, 80, 100, 120, 140, 160, 180, 200]

# Subdivision options (notes per beat)
SUBDIV_OPTIONS = ["1", "2", "4", "8", "16"]

# Drum sound options
DRUM_CHOICES = ["kick", "snare", "hihat", "crash", "tom", "ride"]

# Sound mode options
SOUND_MODES = ["tone", "drum"]

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
        """Generate kick drum sound"""
        sr = self.sample_rate
        dur = 0.25
        n = int(sr * dur)
        t = np.arange(n, dtype=np.float32) / sr
        
        # Frequency sweep from 120Hz to 50Hz
        f0, f1 = 120.0, 50.0
        k = np.log(f1 / f0) / dur
        phase = 2 * np.pi * (f0 * (np.expm1(k * t) / k))
        
        tone = np.sin(phase).astype(np.float32)
        env = np.exp(-t / 0.15).astype(np.float32)
        click = np.exp(-t / 0.01)
        
        return (0.9 * tone * env + 0.05 * click).astype(np.float32)
    
    def _make_snare(self):
        """Generate snare drum sound"""
        sr = self.sample_rate
        dur = 0.3
        n = int(sr * dur)
        t = np.arange(n, dtype=np.float32) / sr
        
        noise = np.random.uniform(-1, 1, size=n).astype(np.float32)
        env_n = np.exp(-t / 0.12).astype(np.float32)
        body = np.sin(2 * np.pi * 190 * t).astype(np.float32) * np.exp(-t / 0.1)
        
        return (0.8 * noise * env_n + 0.25 * body).astype(np.float32)
    
    def _make_hihat(self):
        """Generate hi-hat sound"""
        sr = self.sample_rate
        dur = 0.08
        n = int(sr * dur)
        t = np.arange(n, dtype=np.float32) / sr
        
        noise = np.random.uniform(-1, 1, size=n).astype(np.float32)
        env = np.exp(-t / 0.03).astype(np.float32)
        
        return (noise * env).astype(np.float32)
    
    def _make_crash(self):
        """Generate crash cymbal sound"""
        sr = self.sample_rate
        dur = 1.2
        n = int(sr * dur)
        t = np.arange(n, dtype=np.float32) / sr
        
        noise = np.random.uniform(-1, 1, size=n).astype(np.float32)
        env = np.exp(-t / 0.6).astype(np.float32)
        
        return (0.6 * noise * env).astype(np.float32)
    
    def _make_tom(self):
        """Generate tom drum sound"""
        sr = self.sample_rate
        dur = 0.4
        n = int(sr * dur)
        t = np.arange(n, dtype=np.float32) / sr
        
        tone = np.sin(2 * np.pi * 160.0 * t).astype(np.float32)
        env = np.exp(-t / 0.25).astype(np.float32)
        
        return (tone * env).astype(np.float32)
    
    def _make_ride(self):
        """Generate ride cymbal sound"""
        sr = self.sample_rate
        dur = 0.9
        n = int(sr * dur)
        t = np.arange(n, dtype=np.float32) / sr
        
        ping = np.sin(2 * np.pi * 900 * t).astype(np.float32) * np.exp(-t / 0.4)
        noise = np.random.uniform(-1, 1, size=n).astype(np.float32) * np.exp(-t / 0.8) * 0.2
        
        return (0.8 * ping + noise).astype(np.float32)

# ---------------- Rhythm State (Data Model) ---------------- #

def new_uid():
    """Generate unique ID for layers"""
    return uuid.uuid4().hex


def make_layer(subdiv=4, freq=880.0, vol=1.0, mute=False, mode="tone", drum="snare", color="#9CA3AF", uid=None):
    """Create a layer dictionary"""
    return {
        "uid": uid or new_uid(),
        "subdiv": int(subdiv),
        "freq": float(freq),
        "vol": float(vol),
        "mute": bool(mute),
        "mode": mode,
        "drum": drum,
        "color": color
    }


class RhythmState:
    """Stores the current rhythm configuration with multiple layers per ear"""
    
    def __init__(self):
        self.bpm = 120.0
        self.beats_per_measure = 4
        self.accent_factor = DEFAULT_ACCENT_FACTOR
        self.flash_enabled = False
        
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
            
            def normalize(x):
                x = dict(x)
                x.setdefault("mode", "tone")
                x.setdefault("drum", "snare")
                x.setdefault("color", "#9CA3AF")
                x.setdefault("uid", new_uid())
                return x
            
            self.left = [make_layer(**normalize(x)) for x in data.get("left", [])]
            self.right = [make_layer(**normalize(x)) for x in data.get("right", [])]
            
            # Ensure at least one layer per ear
            if not self.left:
                self.left.append(make_layer(subdiv=4, freq=880.0, vol=1.0, color="#3B82F6"))
            if not self.right:
                self.right.append(make_layer(subdiv=4, freq=440.0, vol=1.0, color="#EF4444"))

# ---------------- Metronome Engine ---------------- #

class SimpleMetronomeEngine:
    """Audio engine for Android with multiple layers and drum support"""
    
    def __init__(self, rhythm_state, on_beat_callback=None):
        self.state = rhythm_state
        self.on_beat_callback = on_beat_callback
        self.tone_gen = ToneGenerator()
        self.drum_synth = DrumSynth()
        
        self.running = False
        self.thread = None
        self._lock = threading.RLock()
        
    def start(self):
        """Start the metronome"""
        if self.running:
            return
        
        with self.state._lock:
            if not self.state.left and not self.state.right:
                print("No layers to play")
                return
        
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
    
    def _get_audio_data(self, layer):
        """Get audio data for a layer based on its mode"""
        mode = layer.get("mode", "tone")
        
        if mode == "drum":
            drum_name = layer.get("drum", "snare")
            return self.drum_synth.get(drum_name)
        else:  # tone mode
            freq = float(layer.get("freq", 880.0))
            return self.tone_gen.generate_beep(freq, duration_ms=50)
    
    def _run(self):
        """Main metronome loop with multiple layers"""
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
        
        start_time = time.time()
        left_next_times = [0.0] * len(left_layers)
        right_next_times = [0.0] * len(right_layers)
        
        while self.running:
            current_time = time.time() - start_time
            
            # Check left layers
            for i, layer in enumerate(left_layers):
                if not layer.get("mute", False) and current_time >= left_next_times[i]:
                    if self.on_beat_callback:
                        uid = layer.get("uid")
                        color = layer.get("color", "#3B82F6")
                        Clock.schedule_once(lambda dt, u=uid, c=color: self.on_beat_callback('left', u, c), 0)
                    left_next_times[i] += left_intervals[i]
            
            # Check right layers
            for i, layer in enumerate(right_layers):
                if not layer.get("mute", False) and current_time >= right_next_times[i]:
                    if self.on_beat_callback:
                        uid = layer.get("uid")
                        color = layer.get("color", "#EF4444")
                        Clock.schedule_once(lambda dt, u=uid, c=color: self.on_beat_callback('right', u, c), 0)
                    right_next_times[i] += right_intervals[i]
            
            # Small sleep to avoid busy waiting
            time.sleep(0.001)

# ---------------- UI Components ---------------- #

class LayerWidget(BoxLayout):
    """Widget for displaying and controlling a single layer"""
    
    def __init__(self, layer, side, on_change=None, on_delete=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = '120dp'
        self.padding = '5dp'
        self.spacing = '5dp'
        
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
            Color(r, g, b, 0.3)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)
        
        self._build_ui()
    
    def _update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos
    
    def _build_ui(self):
        # Top row: Mode, Subdiv, Mute, Delete
        top_row = BoxLayout(size_hint_y=0.4, spacing='5dp')
        
        # Mode selector
        mode_label = Label(text="Mode:", size_hint_x=0.2, font_size='14sp')
        top_row.add_widget(mode_label)
        
        self.mode_spinner = Spinner(
            text=self.layer.get("mode", "tone"),
            values=SOUND_MODES,
            size_hint_x=0.3,
            font_size='14sp'
        )
        self.mode_spinner.bind(text=self._on_mode_change)
        top_row.add_widget(self.mode_spinner)
        
        # Subdivision
        subdiv_label = Label(text="÷", size_hint_x=0.1, font_size='14sp')
        top_row.add_widget(subdiv_label)
        
        self.subdiv_spinner = Spinner(
            text=str(self.layer.get("subdiv", 4)),
            values=SUBDIV_OPTIONS,
            size_hint_x=0.2,
            font_size='14sp'
        )
        self.subdiv_spinner.bind(text=self._on_subdiv_change)
        top_row.add_widget(self.subdiv_spinner)
        
        # Mute button
        self.mute_button = ToggleButton(
            text="MUTE",
            size_hint_x=0.3,
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
        
        # Middle row: Frequency or Drum selector
        self.middle_row = BoxLayout(size_hint_y=0.3, spacing='5dp')
        self._build_middle_row()
        self.add_widget(self.middle_row)
        
        # Bottom row: Volume
        bottom_row = BoxLayout(size_hint_y=0.3, spacing='5dp')
        vol_label = Label(text="Vol:", size_hint_x=0.2, font_size='14sp')
        bottom_row.add_widget(vol_label)
        
        self.vol_slider = Slider(
            min=0.0,
            max=1.5,
            value=self.layer.get("vol", 1.0),
            size_hint_x=0.8
        )
        self.vol_slider.bind(value=self._on_vol_change)
        bottom_row.add_widget(self.vol_slider)
        
        self.add_widget(bottom_row)
    
    def _build_middle_row(self):
        self.middle_row.clear_widgets()
        
        mode = self.layer.get("mode", "tone")
        
        if mode == "tone":
            freq_label = Label(text="Freq (Hz):", size_hint_x=0.3, font_size='14sp')
            self.middle_row.add_widget(freq_label)
            
            self.freq_input = TextInput(
                text=str(int(self.layer.get("freq", 880))),
                multiline=False,
                input_filter='int',
                size_hint_x=0.7,
                font_size='14sp'
            )
            self.freq_input.bind(text=self._on_freq_change)
            self.middle_row.add_widget(self.freq_input)
        else:  # drum mode
            drum_label = Label(text="Drum:", size_hint_x=0.3, font_size='14sp')
            self.middle_row.add_widget(drum_label)
            
            self.drum_spinner = Spinner(
                text=self.layer.get("drum", "snare"),
                values=DRUM_CHOICES,
                size_hint_x=0.7,
                font_size='14sp'
            )
            self.drum_spinner.bind(text=self._on_drum_change)
            self.middle_row.add_widget(self.drum_spinner)
    
    def _on_mode_change(self, spinner, value):
        self.layer["mode"] = value
        self._build_middle_row()
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
    
    def _on_vol_change(self, slider, value):
        self.layer["vol"] = value
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
        
        # Scroll view for layers
        self.scroll = ScrollView(size_hint=(1, 1))
        self.layers_container = BoxLayout(orientation='vertical', size_hint_y=None, spacing='5dp')
        self.layers_container.bind(minimum_height=self.layers_container.setter('height'))
        self.scroll.add_widget(self.layers_container)
        self.add_widget(self.scroll)
        
        self.refresh()
    
    def refresh(self):
        self.layers_container.clear_widgets()
        
        layers = self.state.left if self.side == "left" else self.state.right
        
        for layer in layers:
            layer_widget = LayerWidget(
                layer,
                self.side,
                on_change=self._notify_change,
                on_delete=self._on_delete_layer
            )
            self.layers_container.add_widget(layer_widget)
    
    def _on_add_layer(self, button):
        layers = self.state.left if self.side == "left" else self.state.right
        color = "#3B82F6" if self.side == "left" else "#EF4444"
        new_layer = make_layer(subdiv=4, freq=880.0 if self.side == "left" else 440.0, vol=1.0, color=color)
        layers.append(new_layer)
        self.refresh()
        self._notify_change()
    
    def _on_delete_layer(self, layer):
        layers = self.state.left if self.side == "left" else self.state.right
        if len(layers) > 1:  # Keep at least one layer
            if layer in layers:
                layers.remove(layer)
                self.refresh()
                self._notify_change()
    
    def _notify_change(self):
        if self.on_change:
            self.on_change()


class MetronomeWidget(BoxLayout):
    """Main metronome control widget"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = '10dp'
        self.spacing = '10dp'
        
        # Initialize state and engine
        self.state = RhythmState()
        self.engine = SimpleMetronomeEngine(self.state, on_beat_callback=self.on_beat)
        
        # Load autosave if exists
        self._load_autosave()
        
        # Build UI
        self._build_ui()
        
        # Bind to window size changes for orientation support
        Window.bind(on_resize=self.on_window_resize)
    
    def on_window_resize(self, window, width, height):
        """Handle orientation changes"""
        # Rebuild UI for new orientation if needed
        pass
    
    def _build_ui(self):
        """Build the user interface"""
        
        # Title and BPM
        header = self._build_header()
        self.add_widget(header)
        
        # Layer lists (side by side or stacked based on orientation)
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
        header = BoxLayout(orientation='vertical', size_hint_y=None, height='120dp', spacing='5dp')
        
        # Title
        title = Label(text="PolyRhythm Metronome", font_size='24sp', bold=True, size_hint_y=0.3)
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
        
        # BPM presets
        preset_grid = GridLayout(cols=4, size_hint_y=0.4, spacing='5dp')
        for bpm in BPM_PRESETS:
            btn = Button(text=str(bpm), font_size='14sp')
            btn.bind(on_press=lambda x, b=bpm: self.set_bpm(b))
            preset_grid.add_widget(btn)
        
        header.add_widget(preset_grid)
        
        return header
    
    def _build_controls(self):
        """Build play/stop and file operation controls"""
        controls = BoxLayout(orientation='vertical', size_hint_y=None, height='80dp', spacing='5dp')
        
        # Play/Stop button
        self.play_button = Button(
            text="PLAY",
            font_size='20sp',
            size_hint_y=0.5,
            background_color=(0.2, 0.8, 0.2, 1)
        )
        self.play_button.bind(on_press=self.on_play_stop)
        controls.add_widget(self.play_button)
        
        # Save/Load buttons
        file_box = BoxLayout(size_hint_y=0.5, spacing='5dp')
        
        save_btn = Button(text="SAVE", font_size='16sp')
        save_btn.bind(on_press=self.on_save)
        file_box.add_widget(save_btn)
        
        load_btn = Button(text="LOAD", font_size='16sp')
        load_btn.bind(on_press=self.on_load)
        file_box.add_widget(load_btn)
        
        new_btn = Button(text="NEW", font_size='16sp')
        new_btn.bind(on_press=self.on_new)
        file_box.add_widget(new_btn)
        
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
        """Called when a beat occurs"""
        # Could flash the layer that triggered the beat
        pass
    
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
