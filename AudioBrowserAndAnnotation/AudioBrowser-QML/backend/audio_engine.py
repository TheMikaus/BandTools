#!/usr/bin/env python3
"""
Audio Engine Backend Module

Handles audio playback functionality for the AudioBrowser QML application.
Provides QML-accessible audio playback controls and state management.
"""

import logging
from pathlib import Path
from typing import Optional, List
from PyQt6.QtCore import QObject, QUrl, pyqtSignal, pyqtSlot, QTimer
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QAudioDevice, QMediaDevices


# Set up module logger
logger = logging.getLogger(__name__)


class AudioEngine(QObject):
    """
    Audio playback engine for the AudioBrowser application.
    
    Provides audio playback control, position tracking, and state management
    with signals for QML integration.
    """
    
    # Signals for state changes
    playbackStateChanged = pyqtSignal(str)  # "playing", "paused", "stopped"
    positionChanged = pyqtSignal(int)  # Position in milliseconds
    durationChanged = pyqtSignal(int)  # Duration in milliseconds
    volumeChanged = pyqtSignal(int)  # Volume 0-100
    currentFileChanged = pyqtSignal(str)  # Current file path
    errorOccurred = pyqtSignal(str)  # Error message
    mediaStatusChanged = pyqtSignal(str)  # Media status
    playbackSpeedChanged = pyqtSignal(float)  # Playback speed multiplier
    channelModeChanged = pyqtSignal(str)  # "stereo", "left", "right", "mono"
    audioOutputDevicesChanged = pyqtSignal()  # Audio output devices changed
    
    def __init__(self, parent=None):
        """Initialize the audio engine."""
        super().__init__(parent)
        
        # Create media player and audio output
        self._player = QMediaPlayer()
        self._audio_output = QAudioOutput()
        self._player.setAudioOutput(self._audio_output)
        
        # State tracking
        self._current_file: Optional[Path] = None
        self._volume = 100
        self._playback_speed = 1.0
        self._autoplay_pending = False  # Flag to track if we should play after loading
        
        # Channel control state
        self._channel_mode = "stereo"  # "stereo", "left", "right", "mono"
        self._left_muted = False
        self._right_muted = False
        
        # Clip playback state
        self._clip_start: Optional[int] = None
        self._clip_end: Optional[int] = None
        self._clip_loop = False
        
        # Connect player signals
        self._player.playbackStateChanged.connect(self._on_playback_state_changed)
        self._player.positionChanged.connect(self._on_position_changed)
        self._player.durationChanged.connect(self._on_duration_changed)
        self._player.errorOccurred.connect(self._on_error_occurred)
        self._player.mediaStatusChanged.connect(self._on_media_status_changed)
        
        # Connect to audio device changes
        QMediaDevices.audioOutputsChanged.connect(self._on_audio_outputs_changed)
        
        # Set initial volume
        self._audio_output.setVolume(self._volume / 100.0)
    
    # ========== QML-accessible methods ==========
    
    @pyqtSlot(str)
    def loadFile(self, file_path: str) -> None:
        """
        Load an audio file for playback.
        
        Args:
            file_path: Path to the audio file
        """
        try:
            logger.info(f"Loading audio file: {file_path}")
            path = Path(file_path)
            if not path.exists():
                error_msg = f"File not found: {file_path}"
                logger.error(error_msg)
                self.errorOccurred.emit(error_msg)
                return
            
            self._current_file = path
            self._autoplay_pending = False  # Reset autoplay flag when explicitly loading
            self._player.setSource(QUrl.fromLocalFile(str(path)))
            self.currentFileChanged.emit(str(path))
            logger.debug(f"Audio file loaded successfully: {path.name}")
            
        except Exception as e:
            error_msg = f"Error loading file: {e}"
            logger.error(error_msg, exc_info=True)
            self.errorOccurred.emit(error_msg)
    
    @pyqtSlot(str)
    def loadAndPlay(self, file_path: str) -> None:
        """
        Load an audio file and automatically play when ready.
        
        Args:
            file_path: Path to the audio file
        """
        try:
            logger.info(f"Loading and playing audio file: {file_path}")
            path = Path(file_path)
            if not path.exists():
                error_msg = f"File not found: {file_path}"
                logger.error(error_msg)
                self.errorOccurred.emit(error_msg)
                return
            
            self._current_file = path
            self._autoplay_pending = True  # Set flag to play when loaded
            self._player.setSource(QUrl.fromLocalFile(str(path)))
            self.currentFileChanged.emit(str(path))
            logger.debug(f"Audio file loaded with autoplay: {path.name}")
            
        except Exception as e:
            error_msg = f"Error loading file: {e}"
            logger.error(error_msg, exc_info=True)
            self.errorOccurred.emit(error_msg)
            self._autoplay_pending = False
    
    @pyqtSlot()
    def play(self) -> None:
        """Start or resume playback."""
        if self._current_file is None:
            error_msg = "No file loaded"
            logger.warning(error_msg)
            self.errorOccurred.emit(error_msg)
            return
        
        logger.debug(f"Starting playback: {self._current_file.name}")
        self._player.play()
    
    @pyqtSlot()
    def pause(self) -> None:
        """Pause playback."""
        logger.debug("Pausing playback")
        self._player.pause()
    
    @pyqtSlot()
    def stop(self) -> None:
        """Stop playback and reset position to beginning."""
        logger.debug("Stopping playback")
        self._player.stop()
    
    @pyqtSlot()
    def togglePlayPause(self) -> None:
        """Toggle between play and pause states."""
        if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.pause()
        else:
            self.play()
    
    @pyqtSlot(int)
    def seek(self, position_ms: int) -> None:
        """
        Seek to a specific position in the audio file.
        
        Args:
            position_ms: Position in milliseconds
        """
        self._player.setPosition(position_ms)
    
    @pyqtSlot(int)
    def seekForward(self, delta_ms: int) -> None:
        """
        Seek forward by delta_ms milliseconds.
        
        Args:
            delta_ms: Number of milliseconds to skip forward
        """
        current_pos = self._player.position()
        duration = self._player.duration()
        new_pos = min(current_pos + delta_ms, duration)
        self._player.setPosition(new_pos)
    
    @pyqtSlot(int)
    def seekBackward(self, delta_ms: int) -> None:
        """
        Seek backward by delta_ms milliseconds.
        
        Args:
            delta_ms: Number of milliseconds to skip backward
        """
        current_pos = self._player.position()
        new_pos = max(current_pos - delta_ms, 0)
        self._player.setPosition(new_pos)
    
    @pyqtSlot(int, int, bool)
    def playClip(self, start_ms: int, end_ms: int, loop: bool = False) -> None:
        """
        Play a specific clip/region of the audio file.
        
        Args:
            start_ms: Start position in milliseconds
            end_ms: End position in milliseconds
            loop: Whether to loop the clip playback
        """
        # Store clip boundaries
        self._clip_start = start_ms
        self._clip_end = end_ms
        self._clip_loop = loop
        
        # Seek to start and play
        self._player.setPosition(start_ms)
        self.play()
    
    @pyqtSlot()
    def stopClip(self) -> None:
        """Stop clip playback and clear clip boundaries."""
        self._clip_start = None
        self._clip_end = None
        self._clip_loop = False
    
    @pyqtSlot(int)
    def setVolume(self, volume: int) -> None:
        """
        Set the playback volume.
        
        Args:
            volume: Volume level (0-100)
        """
        volume = max(0, min(100, volume))  # Clamp to 0-100
        self._volume = volume
        self._audio_output.setVolume(volume / 100.0)
        self.volumeChanged.emit(volume)
    
    @pyqtSlot(float)
    def setPlaybackSpeed(self, speed: float) -> None:
        """
        Set the playback speed multiplier.
        
        Args:
            speed: Speed multiplier (e.g., 0.5 = half speed, 2.0 = double speed)
        """
        speed = max(0.1, min(4.0, speed))  # Clamp to reasonable range
        self._playback_speed = speed
        self._player.setPlaybackRate(speed)
        self.playbackSpeedChanged.emit(speed)
    
    @pyqtSlot(result=str)
    def getPlaybackState(self) -> str:
        """
        Get the current playback state.
        
        Returns:
            One of: "playing", "paused", "stopped"
        """
        state = self._player.playbackState()
        if state == QMediaPlayer.PlaybackState.PlayingState:
            return "playing"
        elif state == QMediaPlayer.PlaybackState.PausedState:
            return "paused"
        else:
            return "stopped"
    
    @pyqtSlot(result=int)
    def getPosition(self) -> int:
        """
        Get the current playback position.
        
        Returns:
            Position in milliseconds
        """
        return self._player.position()
    
    @pyqtSlot(result=int)
    def getDuration(self) -> int:
        """
        Get the duration of the current audio file.
        
        Returns:
            Duration in milliseconds
        """
        return self._player.duration()
    
    @pyqtSlot(result=int)
    def getVolume(self) -> int:
        """
        Get the current volume level.
        
        Returns:
            Volume (0-100)
        """
        return self._volume
    
    @pyqtSlot(result=float)
    def getPlaybackSpeed(self) -> float:
        """
        Get the current playback speed.
        
        Returns:
            Speed multiplier
        """
        return self._playback_speed
    
    @pyqtSlot(result=str)
    def getCurrentFile(self) -> str:
        """
        Get the path of the currently loaded file.
        
        Returns:
            File path or empty string if no file loaded
        """
        return str(self._current_file) if self._current_file else ""
    
    @pyqtSlot(result=bool)
    def isPlaying(self) -> bool:
        """
        Check if audio is currently playing.
        
        Returns:
            True if playing, False otherwise
        """
        return self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState
    
    # ========== Internal signal handlers ==========
    
    def _on_playback_state_changed(self, state: QMediaPlayer.PlaybackState) -> None:
        """Handle playback state changes from the media player."""
        if state == QMediaPlayer.PlaybackState.PlayingState:
            state_str = "playing"
        elif state == QMediaPlayer.PlaybackState.PausedState:
            state_str = "paused"
        else:
            state_str = "stopped"
        
        self.playbackStateChanged.emit(state_str)
    
    def _on_position_changed(self, position: int) -> None:
        """Handle position changes from the media player."""
        self.positionChanged.emit(position)
        
        # Handle clip boundaries
        if self._clip_end is not None and position >= self._clip_end:
            if self._clip_loop and self._clip_start is not None:
                # Loop back to start
                self._player.setPosition(self._clip_start)
            else:
                # Stop at clip end
                self.stop()
                self.stopClip()
    
    def _on_duration_changed(self, duration: int) -> None:
        """Handle duration changes from the media player."""
        self.durationChanged.emit(duration)
    
    def _on_error_occurred(self, error: QMediaPlayer.Error, error_string: str) -> None:
        """Handle errors from the media player."""
        self.errorOccurred.emit(f"Media error: {error_string}")
    
    def _on_media_status_changed(self, status: QMediaPlayer.MediaStatus) -> None:
        """Handle media status changes from the media player."""
        status_map = {
            QMediaPlayer.MediaStatus.NoMedia: "no_media",
            QMediaPlayer.MediaStatus.LoadingMedia: "loading",
            QMediaPlayer.MediaStatus.LoadedMedia: "loaded",
            QMediaPlayer.MediaStatus.StalledMedia: "stalled",
            QMediaPlayer.MediaStatus.BufferingMedia: "buffering",
            QMediaPlayer.MediaStatus.BufferedMedia: "buffered",
            QMediaPlayer.MediaStatus.EndOfMedia: "end_of_media",
            QMediaPlayer.MediaStatus.InvalidMedia: "invalid",
        }
        status_str = status_map.get(status, "unknown")
        self.mediaStatusChanged.emit(status_str)
        
        # Auto-play when media is loaded if requested
        if status == QMediaPlayer.MediaStatus.LoadedMedia and self._autoplay_pending:
            self._autoplay_pending = False
            self.play()
    
    # ========== Channel control methods ==========
    
    @pyqtSlot(str)
    def setChannelMode(self, mode: str) -> None:
        """
        Set the channel playback mode.
        
        Args:
            mode: One of "stereo", "left", "right", "mono"
        """
        valid_modes = ["stereo", "left", "right", "mono"]
        if mode not in valid_modes:
            self.errorOccurred.emit(f"Invalid channel mode: {mode}")
            return
        
        self._channel_mode = mode
        self.channelModeChanged.emit(mode)
        
        # Note: QMediaPlayer doesn't support per-channel muting directly
        # This setting is used primarily for audio conversion
    
    @pyqtSlot(result=str)
    def getChannelMode(self) -> str:
        """
        Get the current channel playback mode.
        
        Returns:
            Current channel mode
        """
        return self._channel_mode
    
    @pyqtSlot(bool)
    def setLeftChannelMuted(self, muted: bool) -> None:
        """
        Mute or unmute the left channel.
        
        Args:
            muted: True to mute, False to unmute
        """
        self._left_muted = muted
        # Update channel mode based on mute states
        if self._left_muted and self._right_muted:
            self.setChannelMode("mono")  # Both muted, use mono
        elif self._left_muted:
            self.setChannelMode("right")  # Left muted, use right only
        elif self._right_muted:
            self.setChannelMode("left")  # Right muted, use left only
        else:
            self.setChannelMode("stereo")  # Neither muted, use stereo
    
    @pyqtSlot(result=bool)
    def isLeftChannelMuted(self) -> bool:
        """Check if left channel is muted."""
        return self._left_muted
    
    @pyqtSlot(bool)
    def setRightChannelMuted(self, muted: bool) -> None:
        """
        Mute or unmute the right channel.
        
        Args:
            muted: True to mute, False to unmute
        """
        self._right_muted = muted
        # Update channel mode based on mute states
        if self._left_muted and self._right_muted:
            self.setChannelMode("mono")  # Both muted, use mono
        elif self._left_muted:
            self.setChannelMode("right")  # Left muted, use right only
        elif self._right_muted:
            self.setChannelMode("left")  # Right muted, use left only
        else:
            self.setChannelMode("stereo")  # Neither muted, use stereo
    
    @pyqtSlot(result=bool)
    def isRightChannelMuted(self) -> bool:
        """Check if right channel is muted."""
        return self._right_muted
    
    # ========== Audio Output Device Management ==========
    
    @pyqtSlot(result=list)
    def getAudioOutputDevices(self) -> List[dict]:
        """
        Get list of available audio output devices.
        
        Returns:
            List of dictionaries with device information (id, description)
        """
        devices = []
        for device in QMediaDevices.audioOutputs():
            devices.append({
                "id": device.id().data().decode('utf-8') if device.id() else "",
                "description": device.description()
            })
        return devices
    
    @pyqtSlot(result=str)
    def getCurrentAudioOutputDevice(self) -> str:
        """
        Get the currently selected audio output device ID.
        
        Returns:
            Device ID string, or empty string for default device
        """
        device = self._audio_output.device()
        if device.id():
            return device.id().data().decode('utf-8')
        return ""
    
    @pyqtSlot(str)
    def setAudioOutputDevice(self, device_id: str) -> None:
        """
        Set the audio output device.
        
        Args:
            device_id: Device ID string, or empty string for default device
        """
        try:
            # Find the device with matching ID
            selected_device = None
            if device_id:
                for device in QMediaDevices.audioOutputs():
                    if device.id() and device.id().data().decode('utf-8') == device_id:
                        selected_device = device
                        break
            else:
                # Use default device
                selected_device = QMediaDevices.defaultAudioOutput()
            
            if selected_device:
                # Save current volume
                current_volume = self._audio_output.volume()
                
                # Create new audio output with selected device
                self._audio_output = QAudioOutput(selected_device)
                self._audio_output.setVolume(current_volume)
                self._player.setAudioOutput(self._audio_output)
                
                logger.info(f"Audio output device changed to: {selected_device.description()}")
            else:
                logger.warning(f"Audio output device not found: {device_id}")
                
        except Exception as e:
            error_msg = f"Error setting audio output device: {e}"
            logger.error(error_msg, exc_info=True)
            self.errorOccurred.emit(error_msg)
    
    def _on_audio_outputs_changed(self) -> None:
        """Handle audio output devices list change."""
        logger.info("Audio output devices changed")
        self.audioOutputDevicesChanged.emit()
    
    # ========== Public properties for direct access ==========
    
    @property
    def player(self) -> QMediaPlayer:
        """Get the underlying QMediaPlayer instance."""
        return self._player
    
    @property
    def audio_output(self) -> QAudioOutput:
        """Get the underlying QAudioOutput instance."""
        return self._audio_output
