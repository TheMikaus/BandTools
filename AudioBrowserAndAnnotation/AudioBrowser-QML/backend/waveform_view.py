#!/usr/bin/env python3
"""
Waveform View Backend Module

QQuickPaintedItem implementation for waveform rendering in QML.
Provides custom painting for waveform visualization with position tracking.
"""

from typing import Optional, List
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, pyqtProperty, QPointF, Qt
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtQuick import QQuickPaintedItem


class WaveformView(QQuickPaintedItem):
    """
    Custom QML item for rendering audio waveforms.
    
    Provides waveform visualization with playback position tracking,
    click-to-seek functionality, and theme-aware colors.
    """
    
    # Signals
    seekRequested = pyqtSignal(int)  # Position in milliseconds
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Waveform data
        self._peaks: List[List[float]] = []
        self._duration_ms: int = 0
        
        # Playback state
        self._position_ms: int = 0
        
        # Tempo/BPM for markers
        self._bpm: float = 0.0
        
        # Colors (default dark theme)
        self._background_color = QColor("#1e1e1e")
        self._waveform_color = QColor("#4a9eff")
        self._playhead_color = QColor("#ff4444")
        self._axis_color = QColor("#3e3e3e")
        self._tempo_marker_color = QColor("#666666")
        
        # Enable mouse tracking for click-to-seek
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
        
        # Request repaint when size changes
        self.widthChanged.connect(self.update)
        self.heightChanged.connect(self.update)
    
    # ========== Properties for QML ==========
    
    def _get_peaks(self) -> List[List[float]]:
        return self._peaks
    
    def _set_peaks(self, peaks: List[List[float]]) -> None:
        if peaks != self._peaks:
            self._peaks = peaks if peaks else []
            self.update()
    
    peaks = pyqtProperty(list, _get_peaks, _set_peaks)
    
    def _get_duration_ms(self) -> int:
        return self._duration_ms
    
    def _set_duration_ms(self, duration: int) -> None:
        if duration != self._duration_ms:
            self._duration_ms = int(duration)
            self.update()
    
    durationMs = pyqtProperty(int, _get_duration_ms, _set_duration_ms)
    
    def _get_position_ms(self) -> int:
        return self._position_ms
    
    def _set_position_ms(self, position: int) -> None:
        if position != self._position_ms:
            self._position_ms = int(position)
            self.update()
    
    positionMs = pyqtProperty(int, _get_position_ms, _set_position_ms)
    
    def _get_background_color(self) -> QColor:
        return self._background_color
    
    def _set_background_color(self, color: QColor) -> None:
        self._background_color = color
        self.update()
    
    backgroundColor = pyqtProperty(QColor, _get_background_color, _set_background_color)
    
    def _get_waveform_color(self) -> QColor:
        return self._waveform_color
    
    def _set_waveform_color(self, color: QColor) -> None:
        self._waveform_color = color
        self.update()
    
    waveformColor = pyqtProperty(QColor, _get_waveform_color, _set_waveform_color)
    
    def _get_playhead_color(self) -> QColor:
        return self._playhead_color
    
    def _set_playhead_color(self, color: QColor) -> None:
        self._playhead_color = color
        self.update()
    
    playheadColor = pyqtProperty(QColor, _get_playhead_color, _set_playhead_color)
    
    def _get_axis_color(self) -> QColor:
        return self._axis_color
    
    def _set_axis_color(self, color: QColor) -> None:
        self._axis_color = color
        self.update()
    
    axisColor = pyqtProperty(QColor, _get_axis_color, _set_axis_color)
    
    def _get_bpm(self) -> float:
        return self._bpm
    
    def _set_bpm(self, bpm: float) -> None:
        if bpm != self._bpm:
            self._bpm = float(bpm) if bpm > 0 else 0.0
            self.update()
    
    bpm = pyqtProperty(float, _get_bpm, _set_bpm)
    
    def _get_tempo_marker_color(self) -> QColor:
        return self._tempo_marker_color
    
    def _set_tempo_marker_color(self, color: QColor) -> None:
        self._tempo_marker_color = color
        self.update()
    
    tempoMarkerColor = pyqtProperty(QColor, _get_tempo_marker_color, _set_tempo_marker_color)
    
    # ========== Painting ==========
    
    def paint(self, painter: QPainter) -> None:
        """Paint the waveform."""
        width = int(self.width())
        height = int(self.height())
        
        if width <= 0 or height <= 0:
            return
        
        # Fill background
        painter.fillRect(0, 0, width, height, self._background_color)
        
        # Draw center axis
        mid_y = height / 2
        painter.setPen(QPen(self._axis_color, 1))
        painter.drawLine(0, int(mid_y), width, int(mid_y))
        
        # Draw tempo markers if BPM is set
        if self._bpm > 0 and self._duration_ms > 0:
            self._paint_tempo_markers(painter, width, height)
        
        # Draw waveform if data available
        if self._peaks and len(self._peaks) > 0:
            self._paint_waveform(painter, width, height, mid_y)
        
        # Draw playhead if position is set
        if self._duration_ms > 0 and self._position_ms >= 0:
            self._paint_playhead(painter, width, height)
    
    def _paint_waveform(self, painter: QPainter, width: int, height: int, mid_y: float) -> None:
        """Paint the waveform peaks."""
        num_peaks = len(self._peaks)
        if num_peaks == 0:
            return
        
        # Calculate scale
        x_scale = width / num_peaks
        y_scale = (height / 2) * 0.9  # 90% of half-height for some padding
        
        # Draw waveform
        painter.setPen(QPen(self._waveform_color, 1))
        
        for i, peak in enumerate(self._peaks):
            if len(peak) < 2:
                continue
            
            min_val, max_val = peak[0], peak[1]
            
            x = int(i * x_scale)
            y_min = int(mid_y - (max_val * y_scale))
            y_max = int(mid_y - (min_val * y_scale))
            
            # Draw vertical line for this peak
            if y_max > y_min:
                painter.drawLine(x, y_min, x, y_max)
            else:
                # Single point
                painter.drawPoint(x, y_min)
    
    def _paint_playhead(self, painter: QPainter, width: int, height: int) -> None:
        """Paint the playback position indicator."""
        if self._duration_ms <= 0:
            return
        
        # Calculate playhead position
        progress = self._position_ms / self._duration_ms
        x = int(progress * width)
        
        # Draw playhead line
        painter.setPen(QPen(self._playhead_color, 2))
        painter.drawLine(x, 0, x, height)
    
    def _paint_tempo_markers(self, painter: QPainter, width: int, height: int) -> None:
        """Paint tempo/measure markers based on BPM."""
        if self._bpm <= 0 or self._duration_ms <= 0:
            return
        
        # Calculate measure duration in milliseconds (assuming 4/4 time signature)
        # 1 beat = 60,000ms / BPM
        # 1 measure (4 beats) = 4 * (60,000 / BPM) = 240,000 / BPM
        measure_duration_ms = 240000.0 / self._bpm
        
        # Calculate number of measures
        num_measures = int(self._duration_ms / measure_duration_ms)
        
        # Limit to 1000 measures for performance
        if num_measures > 1000:
            return
        
        # Draw measure markers
        pen = QPen(self._tempo_marker_color, 1, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        
        for i in range(1, num_measures + 1):
            measure_time_ms = i * measure_duration_ms
            if measure_time_ms > self._duration_ms:
                break
            
            # Calculate x position
            progress = measure_time_ms / self._duration_ms
            x = int(progress * width)
            
            # Draw vertical dashed line
            painter.drawLine(x, 0, x, height)
            
            # Draw measure number every 4 measures
            if i % 4 == 0:
                painter.setPen(QPen(self._tempo_marker_color, 1))
                painter.drawText(x + 2, 12, f"M{i}")
                pen = QPen(self._tempo_marker_color, 1, Qt.PenStyle.DashLine)
                painter.setPen(pen)
    
    # ========== Mouse interaction ==========
    
    def mousePressEvent(self, event) -> None:
        """Handle mouse press for click-to-seek."""
        if self._duration_ms > 0:
            # Calculate position from click
            progress = event.pos().x() / self.width()
            position_ms = int(progress * self._duration_ms)
            
            # Clamp to valid range
            position_ms = max(0, min(position_ms, self._duration_ms))
            
            # Emit seek request
            self.seekRequested.emit(position_ms)
        
        super().mousePressEvent(event)
