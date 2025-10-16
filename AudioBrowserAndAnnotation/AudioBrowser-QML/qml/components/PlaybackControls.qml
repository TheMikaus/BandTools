import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "../styles"

/**
 * PlaybackControls - Audio playback control panel
 * 
 * Provides play/pause, stop, seek, and volume controls for audio playback.
 * Integrates with AudioEngine backend for full playback control.
 * 
 * Features:
 *   - Play/pause toggle button
 *   - Stop button
 *   - Previous/next buttons (can be enabled/disabled)
 *   - Seek slider with time display
 *   - Volume slider
 * 
 * Usage:
 *   PlaybackControls {
 *       // Will automatically connect to audioEngine context property
 *   }
 */
Item {
    id: root
    
    implicitHeight: Theme.toolbarHeight
    
    RowLayout {
        anchors.fill: parent
        spacing: Theme.spacingNormal
        
        // Playback buttons
        RowLayout {
            spacing: Theme.spacingSmall
            
            StyledButton {
                id: prevButton
                text: "⏮"
                enabled: false
                implicitWidth: 36
                implicitHeight: 32
            }
            
            StyledButton {
                id: playPauseButton
                text: audioEngine.getPlaybackState() === "playing" ? "⏸" : "▶"
                primary: true
                implicitWidth: 40
                implicitHeight: 32
                onClicked: audioEngine.togglePlayPause()
            }
            
            StyledButton {
                id: stopButton
                text: "⏹"
                implicitWidth: 36
                implicitHeight: 32
                onClicked: audioEngine.stop()
            }
            
            StyledButton {
                id: nextButton
                text: "⏭"
                enabled: false
                implicitWidth: 36
                implicitHeight: 32
            }
        }
        
        // Seek slider with time display
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacingSmall
            
            Label {
                id: positionLabel
                text: formatTime(audioEngine.getPosition())
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.textSecondary
                Layout.preferredWidth: 50
                horizontalAlignment: Text.AlignRight
            }
            
            StyledSlider {
                id: seekSlider
                Layout.fillWidth: true
                from: 0
                to: audioEngine.getDuration()
                value: audioEngine.getPosition()
                enabled: audioEngine.getDuration() > 0
                
                onMoved: {
                    audioEngine.seek(value)
                }
            }
            
            Label {
                id: durationLabel
                text: formatTime(audioEngine.getDuration())
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.textSecondary
                Layout.preferredWidth: 50
            }
        }
        
        // Volume control
        RowLayout {
            spacing: Theme.spacingSmall
            
            Label {
                text: "🔊"
                font.pixelSize: Theme.fontSizeMedium
                color: Theme.textSecondary
            }
            
            StyledSlider {
                id: volumeSlider
                from: 0
                to: 100
                value: audioEngine.getVolume()
                implicitWidth: 80
                
                onMoved: {
                    audioEngine.setVolume(value)
                }
            }
            
            Label {
                text: Math.round(volumeSlider.value) + "%"
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.textSecondary
                Layout.preferredWidth: 35
            }
        }
        
        // Channel controls
        RowLayout {
            spacing: Theme.spacingSmall
            
            Rectangle {
                width: 1
                height: parent.height * 0.6
                color: Theme.borderColor
            }
            
            Label {
                text: "Ch:"
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.textSecondary
            }
            
            // Stereo/Mono toggle
            ComboBox {
                id: channelModeCombo
                Layout.preferredWidth: 80
                model: ["Stereo", "Mono", "Left", "Right"]
                currentIndex: 0
                
                background: Rectangle {
                    color: Theme.backgroundColor
                    border.color: Theme.borderColor
                    border.width: 1
                    radius: Theme.radiusSmall
                }
                
                contentItem: Text {
                    text: channelModeCombo.displayText
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.textColor
                    verticalAlignment: Text.AlignVCenter
                    leftPadding: 6
                }
                
                onCurrentTextChanged: {
                    audioEngine.setChannelMode(currentText.toLowerCase())
                }
            }
        }
    }
    
    // Update seek slider when playback position changes
    Connections {
        target: audioEngine
        
        function onPositionChanged(position) {
            if (!seekSlider.pressed) {
                seekSlider.value = position
            }
        }
        
        function onDurationChanged(duration) {
            seekSlider.to = duration
        }
        
        function onVolumeChanged(volume) {
            if (!volumeSlider.pressed) {
                volumeSlider.value = volume
            }
        }
    }
    
    // Timer to update position display
    Timer {
        interval: 100
        running: audioEngine.getPlaybackState() === "playing"
        repeat: true
        onTriggered: {
            positionLabel.text = formatTime(audioEngine.getPosition())
        }
    }
    
    // Helper function to format time in MM:SS format
    function formatTime(milliseconds) {
        if (milliseconds <= 0) return "00:00"
        
        var totalSeconds = Math.floor(milliseconds / 1000)
        var minutes = Math.floor(totalSeconds / 60)
        var seconds = totalSeconds % 60
        
        return String(minutes).padStart(2, '0') + ":" + 
               String(seconds).padStart(2, '0')
    }
}
