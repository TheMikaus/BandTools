#!/usr/bin/env python3
"""
Audio Engine Backend Module

Handles audio playback functionality for the AudioBrowser QML application.
Provides QML-accessible audio playback controls and state management.
"""

from pathlib import Path
from typing import Optional
from PyQt6.QtCore import QObject, QUrl, pyqtSignal, pyqtSlot, QTimer
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput


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
        
        # Connect player signals
        self._player.playbackStateChanged.connect(self._on_playback_state_changed)
        self._player.positionChanged.connect(self._on_position_changed)
        self._player.durationChanged.connect(self._on_duration_changed)
        self._player.errorOccurred.connect(self._on_error_occurred)
        self._player.mediaStatusChanged.connect(self._on_media_status_changed)
        
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
            path = Path(file_path)
            if not path.exists():
                self.errorOccurred.emit(f"File not found: {file_path}")
                return
            
            self._current_file = path
            self._player.setSource(QUrl.fromLocalFile(str(path)))
            self.currentFileChanged.emit(str(path))
            
        except Exception as e:
            self.errorOccurred.emit(f"Error loading file: {e}")
    
    @pyqtSlot()
    def play(self) -> None:
        """Start or resume playback."""
        if self._current_file is None:
            self.errorOccurred.emit("No file loaded")
            return
        
        self._player.play()
    
    @pyqtSlot()
    def pause(self) -> None:
        """Pause playback."""
        self._player.pause()
    
    @pyqtSlot()
    def stop(self) -> None:
        """Stop playback and reset position to beginning."""
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
    
    # ========== Public properties for direct access ==========
    
    @property
    def player(self) -> QMediaPlayer:
        """Get the underlying QMediaPlayer instance."""
        return self._player
    
    @property
    def audio_output(self) -> QAudioOutput:
        """Get the underlying QAudioOutput instance."""
        return self._audio_output
