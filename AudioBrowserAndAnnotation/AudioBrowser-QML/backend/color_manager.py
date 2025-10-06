"""
Color Manager for AudioBrowser QML

Manages consistent colors across different machines and display environments.
Extracted and adapted from audio_browser.py ColorManager class.
"""

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, pyqtProperty
from PyQt6.QtGui import QColor
from typing import Dict


class ColorManager(QObject):
    """
    Manages consistent colors across different machines and display environments.
    
    Provides theme-aware color palettes for UI elements, waveforms, and other
    visual components. Colors are standardized for consistent appearance across
    different displays and platforms.
    
    Phase 1: Core Infrastructure
    """
    
    themeChanged = pyqtSignal()
    
    def __init__(self, theme: str = "dark"):
        super().__init__()
        self._color_cache = {}
        self._theme = theme
        
    def _get_theme(self) -> str:
        """Get current theme."""
        return self._theme
    
    def _set_theme(self, theme: str):
        """Set current theme and clear cache."""
        if theme != self._theme:
            self._theme = theme
            self._color_cache.clear()
            self.themeChanged.emit()
    
    # Q_PROPERTY for QML access
    theme = pyqtProperty(str, _get_theme, _set_theme, notify=themeChanged)
    
    @pyqtSlot(str)
    def setTheme(self, theme: str):
        """Set the current theme ('light' or 'dark')."""
        self._set_theme(theme)
    
    @pyqtSlot(result=str)
    def getTheme(self) -> str:
        """Get the current theme."""
        return self._theme
    
    def get_standardized_color(self, base_color: str, purpose: str = "general") -> QColor:
        """
        Get a standardized color that appears consistent across different machines.
        
        Args:
            base_color: Base hex color (e.g., "#58a6ff")
            purpose: Purpose of the color (e.g., "selection", "waveform", "text")
            
        Returns:
            QColor object with standardized properties for consistent appearance
        """
        cache_key = f"{base_color}_{purpose}"
        if cache_key in self._color_cache:
            return self._color_cache[cache_key]
            
        base_qcolor = QColor(base_color)
        if not base_qcolor.isValid():
            base_qcolor = QColor("#808080")  # Fallback gray
            
        # Apply standardization based on purpose
        standardized = self._apply_color_standardization(base_qcolor, purpose)
        self._color_cache[cache_key] = standardized
        return standardized
    
    def _apply_color_standardization(self, color: QColor, purpose: str) -> QColor:
        """Apply standardization rules to ensure consistent appearance across machines."""
        # Convert to HSV for consistent manipulation
        h, s, v, a = color.getHsvF()
        
        # Standardize based on purpose
        if purpose == "selection":
            # Ensure selection colors are vivid and high-contrast
            s = max(0.8, s)  # Ensure high saturation for visibility
            v = max(0.6, min(0.9, v))  # Ensure adequate brightness without being blinding
        elif purpose == "waveform":
            # Waveform colors should be clear but not too bright
            s = max(0.7, min(0.95, s))  # Good saturation for clarity
            v = max(0.5, min(0.8, v))  # Medium brightness for long viewing comfort
        elif purpose == "text":
            # Text colors need good contrast
            if v > 0.5:  # Light colors
                v = max(0.2, v)  # Ensure dark enough for readability
            else:  # Dark colors  
                v = min(0.8, max(0.4, v))  # Ensure light enough for readability
        elif purpose == "ui_accent":
            # UI accent colors (buttons, highlights)
            s = max(0.6, min(0.9, s))  # Strong but not overwhelming
            v = max(0.4, min(0.7, v))  # Medium brightness
        
        # Apply gamma correction for consistent appearance across displays
        # Most displays have gamma around 2.2, so we normalize to that
        v = pow(v, 1.0 / 2.2) if v > 0 else 0
        v = pow(v, 2.2)
        
        return QColor.fromHsvF(h, s, v, a)
    
    @pyqtSlot(result=str)
    def getSelectionColorPrimary(self) -> str:
        """Get primary selection color as hex string."""
        return self.get_standardized_color("#2563eb", "selection").name()
    
    @pyqtSlot(result=str)
    def getSelectionColorActive(self) -> str:
        """Get active selection color as hex string."""
        return self.get_standardized_color("#1d4ed8", "selection").name()
    
    @pyqtSlot(result=str)
    def getSelectionColorInactive(self) -> str:
        """Get inactive selection color as hex string."""
        return self.get_standardized_color("#1e3a8a", "selection").name()
    
    def get_waveform_colors(self) -> Dict[str, QColor]:
        """Get standardized waveform colors."""
        if self._theme == "dark":
            return {
                'background': self.get_standardized_color("#181a1f", "ui_accent"),
                'axis': self.get_standardized_color("#353841", "ui_accent"),
                'left_channel': self.get_standardized_color("#58a6ff", "waveform"),
                'right_channel': self.get_standardized_color("#ff6b58", "waveform"),
                'playhead': self.get_standardized_color("#ff6666", "waveform"),
                'selected': self.get_standardized_color("#ffa500", "selection"),
                'message': self.get_standardized_color("#9aa0a8", "text")
            }
        else:
            return {
                'background': self.get_standardized_color("#101114", "ui_accent"),
                'axis': self.get_standardized_color("#2a2c31", "ui_accent"),
                'left_channel': self.get_standardized_color("#58a6ff", "waveform"),
                'right_channel': self.get_standardized_color("#ff6b58", "waveform"),
                'playhead': self.get_standardized_color("#ff5555", "waveform"),
                'selected': self.get_standardized_color("#ffa500", "selection"),
                'message': self.get_standardized_color("#8a8f98", "text")
            }
    
    @pyqtSlot(result=str)
    def getWaveformBackground(self) -> str:
        """Get waveform background color as hex string."""
        return self.get_waveform_colors()['background'].name()
    
    @pyqtSlot(result=str)
    def getWaveformAxis(self) -> str:
        """Get waveform axis color as hex string."""
        return self.get_waveform_colors()['axis'].name()
    
    @pyqtSlot(result=str)
    def getWaveformLeftChannel(self) -> str:
        """Get waveform left channel color as hex string."""
        return self.get_waveform_colors()['left_channel'].name()
    
    @pyqtSlot(result=str)
    def getWaveformRightChannel(self) -> str:
        """Get waveform right channel color as hex string."""
        return self.get_waveform_colors()['right_channel'].name()
    
    @pyqtSlot(result=str)
    def getWaveformPlayhead(self) -> str:
        """Get waveform playhead color as hex string."""
        return self.get_waveform_colors()['playhead'].name()
    
    def get_ui_colors(self) -> Dict[str, QColor]:
        """Get standardized UI element colors."""
        if self._theme == "dark":
            return {
                'success': self.get_standardized_color("#66bb6a", "ui_accent"),
                'danger': self.get_standardized_color("#ef5350", "ui_accent"),
                'info': self.get_standardized_color("#42a5f5", "ui_accent"),
                'warning': self.get_standardized_color("#ffa726", "ui_accent"),
                'text_secondary': self.get_standardized_color("#b0b0b0", "text"),
                'text_muted': self.get_standardized_color("#808080", "text"),
                'background_light': self.get_standardized_color("#2a2a2a", "ui_accent"),
                'background_medium': self.get_standardized_color("#353535", "ui_accent"),
                'border': self.get_standardized_color("#505050", "ui_accent")
            }
        else:
            return {
                'success': self.get_standardized_color("#4CAF50", "ui_accent"),
                'danger': self.get_standardized_color("#f44336", "ui_accent"),
                'info': self.get_standardized_color("#2196F3", "ui_accent"),
                'warning': self.get_standardized_color("#ff9800", "ui_accent"),
                'text_secondary': self.get_standardized_color("#666666", "text"),
                'text_muted': self.get_standardized_color("#999999", "text"),
                'background_light': self.get_standardized_color("#f8f8f8", "ui_accent"),
                'background_medium': self.get_standardized_color("#f0f0f0", "ui_accent"),
                'border': self.get_standardized_color("#cccccc", "ui_accent")
            }
    
    @pyqtSlot(result=str)
    def getSuccessColor(self) -> str:
        """Get success color as hex string."""
        return self.get_ui_colors()['success'].name()
    
    @pyqtSlot(result=str)
    def getDangerColor(self) -> str:
        """Get danger color as hex string."""
        return self.get_ui_colors()['danger'].name()
    
    @pyqtSlot(result=str)
    def getInfoColor(self) -> str:
        """Get info color as hex string."""
        return self.get_ui_colors()['info'].name()
    
    @pyqtSlot(result=str)
    def getWarningColor(self) -> str:
        """Get warning color as hex string."""
        return self.get_ui_colors()['warning'].name()
    
    @pyqtSlot(result=str)
    def getBackgroundLight(self) -> str:
        """Get light background color as hex string."""
        return self.get_ui_colors()['background_light'].name()
    
    @pyqtSlot(result=str)
    def getBackgroundMedium(self) -> str:
        """Get medium background color as hex string."""
        return self.get_ui_colors()['background_medium'].name()
    
    @pyqtSlot(result=str)
    def getBorderColor(self) -> str:
        """Get border color as hex string."""
        return self.get_ui_colors()['border'].name()
