#!/usr/bin/env python3
"""
PolyRhythmMetronome - Android Version
A simplified touch-optimized metronome for Android devices (Kindle Fire HD 10)

Simplified features for mobile:
- Single layer per ear (vs. multi-layer in desktop)
- Touch-optimized large buttons and sliders
- Simplified sound options: Tone only (no WAV/Drum)
- BPM control with preset buttons and slider
- Save/Load rhythm patterns
- Visual feedback with color flashing
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
    from kivy.uix.button import Button
    from kivy.uix.label import Label
    from kivy.uix.slider import Slider
    from kivy.uix.togglebutton import ToggleButton
    from kivy.uix.spinner import Spinner
    from kivy.uix.popup import Popup
    from kivy.uix.textinput import TextInput
    from kivy.uix.filechooser import FileChooserListView
    from kivy.clock import Clock
    from kivy.core.audio import SoundLoader
    from kivy.graphics import Color, Rectangle
    from kivy.properties import NumericProperty, StringProperty, BooleanProperty
    from kivy.utils import platform
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

# ---------------- Rhythm State (Data Model) ---------------- #

def new_uid():
    """Generate unique ID for layers"""
    return uuid.uuid4().hex

class RhythmState:
    """Stores the current rhythm configuration"""
    
    def __init__(self):
        self.bpm = 120.0
        self.beats_per_measure = 4
        self.accent_factor = DEFAULT_ACCENT_FACTOR
        
        # Simplified: single layer per ear
        self.left_subdiv = 4  # Quarter notes
        self.left_freq = 880.0  # Hz
        self.left_vol = 1.0
        self.left_mute = False
        self.left_color = "#3B82F6"  # Blue
        
        self.right_subdiv = 4
        self.right_freq = 440.0  # Hz
        self.right_vol = 1.0
        self.right_mute = False
        self.right_color = "#EF4444"  # Red
        
        self._lock = threading.RLock()
    
    def to_dict(self):
        """Serialize to dictionary for saving"""
        with self._lock:
            return {
                "bpm": self.bpm,
                "beats_per_measure": self.beats_per_measure,
                "accent_factor": self.accent_factor,
                "left": {
                    "subdiv": self.left_subdiv,
                    "freq": self.left_freq,
                    "vol": self.left_vol,
                    "mute": self.left_mute,
                    "color": self.left_color
                },
                "right": {
                    "subdiv": self.right_subdiv,
                    "freq": self.right_freq,
                    "vol": self.right_vol,
                    "mute": self.right_mute,
                    "color": self.right_color
                }
            }
    
    def from_dict(self, data):
        """Load from dictionary"""
        with self._lock:
            self.bpm = float(data.get("bpm", 120.0))
            self.beats_per_measure = int(data.get("beats_per_measure", 4))
            self.accent_factor = float(data.get("accent_factor", DEFAULT_ACCENT_FACTOR))
            
            left = data.get("left", {})
            self.left_subdiv = int(left.get("subdiv", 4))
            self.left_freq = float(left.get("freq", 880.0))
            self.left_vol = float(left.get("vol", 1.0))
            self.left_mute = bool(left.get("mute", False))
            self.left_color = left.get("color", "#3B82F6")
            
            right = data.get("right", {})
            self.right_subdiv = int(right.get("subdiv", 4))
            self.right_freq = float(right.get("freq", 440.0))
            self.right_vol = float(right.get("vol", 1.0))
            self.right_mute = bool(right.get("mute", False))
            self.right_color = right.get("color", "#EF4444")

# ---------------- Metronome Engine ---------------- #

class SimpleMetronomeEngine:
    """Simplified audio engine for Android"""
    
    def __init__(self, rhythm_state, on_beat_callback=None):
        self.state = rhythm_state
        self.on_beat_callback = on_beat_callback
        self.tone_gen = ToneGenerator()
        
        self.running = False
        self.thread = None
        self._lock = threading.RLock()
        
        # Sound objects
        self.left_sound = None
        self.right_sound = None
    
    def _prepare_sounds(self):
        """Pre-generate the tone sounds"""
        # Generate left and right tones
        left_data = self.tone_gen.generate_beep(self.state.left_freq, duration_ms=50)
        right_data = self.tone_gen.generate_beep(self.state.right_freq, duration_ms=50)
        
        # In a real implementation, we'd convert these to audio files that Kivy can play
        # For now, we'll use placeholders
        # TODO: Save as temporary WAV files and load with SoundLoader
        
    def start(self):
        """Start the metronome"""
        if self.running:
            return
        
        self.running = True
        self._prepare_sounds()
        
        # Start the metronome thread
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop the metronome"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None
    
    def _run(self):
        """Main metronome loop"""
        with self.state._lock:
            bpm = self.state.bpm
            left_interval = 60.0 / (bpm * (self.state.left_subdiv / 4.0))
            right_interval = 60.0 / (bpm * (self.state.right_subdiv / 4.0))
        
        start_time = time.time()
        left_next = 0.0
        right_next = 0.0
        
        while self.running:
            current_time = time.time() - start_time
            
            # Check if it's time for left beat
            if current_time >= left_next and not self.state.left_mute:
                if self.on_beat_callback:
                    Clock.schedule_once(lambda dt: self.on_beat_callback('left'), 0)
                left_next += left_interval
            
            # Check if it's time for right beat
            if current_time >= right_next and not self.state.right_mute:
                if self.on_beat_callback:
                    Clock.schedule_once(lambda dt: self.on_beat_callback('right'), 0)
                right_next += right_interval
            
            # Small sleep to avoid busy waiting
            time.sleep(0.001)

# ---------------- UI Components ---------------- #

class MetronomeWidget(BoxLayout):
    """Main metronome control widget"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 15
        
        # Initialize state and engine
        self.state = RhythmState()
        self.engine = SimpleMetronomeEngine(self.state, on_beat_callback=self.on_beat)
        
        # Load autosave if exists
        self._load_autosave()
        
        # Build UI
        self._build_ui()
    
    def _build_ui(self):
        """Build the user interface"""
        
        # Title
        title = Label(
            text="PolyRhythm Metronome",
            size_hint=(1, 0.08),
            font_size='24sp',
            bold=True
        )
        self.add_widget(title)
        
        # BPM Control Section
        bpm_section = self._build_bpm_section()
        self.add_widget(bpm_section)
        
        # Left/Right Layer Controls
        layers_section = self._build_layers_section()
        self.add_widget(layers_section)
        
        # Play/Stop and Save/Load buttons
        controls_section = self._build_controls_section()
        self.add_widget(controls_section)
    
    def _build_bpm_section(self):
        """Build BPM control section"""
        section = BoxLayout(orientation='vertical', size_hint=(1, 0.25), spacing=10)
        
        # BPM Label and Value
        bpm_label_box = BoxLayout(size_hint=(1, 0.3))
        bpm_label_box.add_widget(Label(text="BPM:", font_size='20sp', size_hint=(0.3, 1)))
        self.bpm_value_label = Label(
            text=str(int(self.state.bpm)),
            font_size='28sp',
            bold=True,
            size_hint=(0.7, 1)
        )
        bpm_label_box.add_widget(self.bpm_value_label)
        section.add_widget(bpm_label_box)
        
        # BPM Slider
        self.bpm_slider = Slider(
            min=40,
            max=240,
            value=self.state.bpm,
            step=1,
            size_hint=(1, 0.3)
        )
        self.bpm_slider.bind(value=self.on_bpm_change)
        section.add_widget(self.bpm_slider)
        
        # BPM Preset Buttons
        preset_grid = GridLayout(cols=4, size_hint=(1, 0.4), spacing=5)
        for bpm in BPM_PRESETS:
            btn = Button(
                text=str(bpm),
                font_size='16sp',
                on_press=lambda x, b=bpm: self.set_bpm(b)
            )
            preset_grid.add_widget(btn)
        section.add_widget(preset_grid)
        
        return section
    
    def _build_layers_section(self):
        """Build left/right layer control section"""
        section = BoxLayout(orientation='horizontal', size_hint=(1, 0.45), spacing=10)
        
        # Left ear controls
        left_box = self._build_layer_controls("LEFT", "left")
        section.add_widget(left_box)
        
        # Right ear controls
        right_box = self._build_layer_controls("RIGHT", "right")
        section.add_widget(right_box)
        
        return section
    
    def _build_layer_controls(self, title, side):
        """Build controls for one layer (left or right)"""
        box = BoxLayout(orientation='vertical', size_hint=(0.5, 1), spacing=5)
        
        # Set background color
        with box.canvas.before:
            if side == "left":
                Color(0.23, 0.51, 0.96, 0.2)  # Light blue
            else:
                Color(0.94, 0.27, 0.27, 0.2)  # Light red
            self.bg_rect = Rectangle(size=box.size, pos=box.pos)
            box.bind(size=self._update_rect, pos=self._update_rect)
        
        # Title and Mute button
        header = BoxLayout(size_hint=(1, 0.15))
        header.add_widget(Label(text=title, font_size='18sp', bold=True, size_hint=(0.6, 1)))
        
        mute_btn = ToggleButton(
            text="MUTE",
            size_hint=(0.4, 1),
            font_size='14sp'
        )
        if side == "left":
            mute_btn.state = 'down' if self.state.left_mute else 'normal'
            mute_btn.bind(state=self.on_left_mute)
            self.left_mute_btn = mute_btn
        else:
            mute_btn.state = 'down' if self.state.right_mute else 'normal'
            mute_btn.bind(state=self.on_right_mute)
            self.right_mute_btn = mute_btn
        
        header.add_widget(mute_btn)
        box.add_widget(header)
        
        # Subdivision control
        subdiv_box = BoxLayout(size_hint=(1, 0.15))
        subdiv_box.add_widget(Label(text="Subdiv:", font_size='14sp', size_hint=(0.4, 1)))
        
        spinner = Spinner(
            text=str(getattr(self.state, f"{side}_subdiv")),
            values=SUBDIV_OPTIONS,
            size_hint=(0.6, 1),
            font_size='14sp'
        )
        if side == "left":
            spinner.bind(text=self.on_left_subdiv)
        else:
            spinner.bind(text=self.on_right_subdiv)
        subdiv_box.add_widget(spinner)
        box.add_widget(subdiv_box)
        
        # Frequency control
        freq_box = BoxLayout(size_hint=(1, 0.15))
        freq_box.add_widget(Label(text="Freq (Hz):", font_size='14sp', size_hint=(0.5, 1)))
        
        freq_input = TextInput(
            text=str(int(getattr(self.state, f"{side}_freq"))),
            multiline=False,
            input_filter='int',
            size_hint=(0.5, 1),
            font_size='14sp'
        )
        if side == "left":
            freq_input.bind(text=self.on_left_freq)
        else:
            freq_input.bind(text=self.on_right_freq)
        freq_box.add_widget(freq_input)
        box.add_widget(freq_box)
        
        # Volume control
        vol_box = BoxLayout(orientation='vertical', size_hint=(1, 0.25))
        vol_box.add_widget(Label(text="Volume", font_size='14sp', size_hint=(1, 0.4)))
        
        vol_slider = Slider(
            min=0.0,
            max=1.5,
            value=getattr(self.state, f"{side}_vol"),
            step=0.1,
            size_hint=(1, 0.6)
        )
        if side == "left":
            vol_slider.bind(value=self.on_left_vol)
        else:
            vol_slider.bind(value=self.on_right_vol)
        vol_box.add_widget(vol_slider)
        box.add_widget(vol_box)
        
        # Visual indicator (for beat flashing)
        indicator = Label(
            text="",
            size_hint=(1, 0.3),
            font_size='48sp'
        )
        if side == "left":
            self.left_indicator = indicator
        else:
            self.right_indicator = indicator
        box.add_widget(indicator)
        
        return box
    
    def _update_rect(self, instance, value):
        """Update background rectangle when size/position changes"""
        if hasattr(instance, 'canvas'):
            instance.canvas.before.clear()
            with instance.canvas.before:
                if hasattr(self, 'state'):
                    # Determine color based on side
                    # This is a simple implementation - in practice you'd track which side
                    Color(0.2, 0.2, 0.2, 0.1)
                rect = Rectangle(size=instance.size, pos=instance.pos)
    
    def _build_controls_section(self):
        """Build play/stop and file operation controls"""
        section = BoxLayout(orientation='vertical', size_hint=(1, 0.22), spacing=10)
        
        # Play/Stop button
        self.play_button = Button(
            text="PLAY",
            font_size='24sp',
            size_hint=(1, 0.5),
            background_color=(0.2, 0.8, 0.2, 1)
        )
        self.play_button.bind(on_press=self.on_play_stop)
        section.add_widget(self.play_button)
        
        # Save/Load buttons
        file_box = BoxLayout(size_hint=(1, 0.5), spacing=10)
        
        save_btn = Button(text="SAVE", font_size='18sp')
        save_btn.bind(on_press=self.on_save)
        file_box.add_widget(save_btn)
        
        load_btn = Button(text="LOAD", font_size='18sp')
        load_btn.bind(on_press=self.on_load)
        file_box.add_widget(load_btn)
        
        section.add_widget(file_box)
        
        return section
    
    # Event Handlers
    
    def on_bpm_change(self, instance, value):
        """Handle BPM slider change"""
        self.state.bpm = value
        self.bpm_value_label.text = str(int(value))
        self._autosave()
    
    def set_bpm(self, bpm):
        """Set BPM to a specific value"""
        self.bpm_slider.value = bpm
    
    def on_left_mute(self, instance, value):
        """Handle left mute toggle"""
        self.state.left_mute = (value == 'down')
        self._autosave()
    
    def on_right_mute(self, instance, value):
        """Handle right mute toggle"""
        self.state.right_mute = (value == 'down')
        self._autosave()
    
    def on_left_subdiv(self, instance, value):
        """Handle left subdivision change"""
        try:
            self.state.left_subdiv = int(value)
            self._autosave()
        except ValueError:
            pass
    
    def on_right_subdiv(self, instance, value):
        """Handle right subdivision change"""
        try:
            self.state.right_subdiv = int(value)
            self._autosave()
        except ValueError:
            pass
    
    def on_left_freq(self, instance, value):
        """Handle left frequency change"""
        try:
            if value:
                self.state.left_freq = float(value)
                self._autosave()
        except ValueError:
            pass
    
    def on_right_freq(self, instance, value):
        """Handle right frequency change"""
        try:
            if value:
                self.state.right_freq = float(value)
                self._autosave()
        except ValueError:
            pass
    
    def on_left_vol(self, instance, value):
        """Handle left volume change"""
        self.state.left_vol = value
        self._autosave()
    
    def on_right_vol(self, instance, value):
        """Handle right volume change"""
        self.state.right_vol = value
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
    
    def on_beat(self, side):
        """Called when a beat occurs - flash the visual indicator"""
        if side == 'left':
            self.left_indicator.text = "●"
            Clock.schedule_once(lambda dt: setattr(self.left_indicator, 'text', ''), FLASH_DURATION)
        else:
            self.right_indicator.text = "●"
            Clock.schedule_once(lambda dt: setattr(self.right_indicator, 'text', ''), FLASH_DURATION)
    
    def on_save(self, instance):
        """Handle save button press"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        filename_input = TextInput(
            text="my_rhythm.json",
            multiline=False,
            size_hint=(1, 0.3)
        )
        content.add_widget(Label(text="Enter filename:", size_hint=(1, 0.3)))
        content.add_widget(filename_input)
        
        button_box = BoxLayout(size_hint=(1, 0.4), spacing=10)
        
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
        # Simple file chooser - in a real app, use FileChooser
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        filename_input = TextInput(
            text="my_rhythm.json",
            multiline=False,
            size_hint=(1, 0.3)
        )
        content.add_widget(Label(text="Enter filename:", size_hint=(1, 0.3)))
        content.add_widget(filename_input)
        
        button_box = BoxLayout(size_hint=(1, 0.4), spacing=10)
        
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
            
            # Update UI to reflect loaded values
            self.bpm_slider.value = self.state.bpm
            # Note: Other UI elements will need to be updated too
            # This is simplified for the example
            
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
