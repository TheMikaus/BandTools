import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "../styles"

/**
 * NowPlayingPanel - Persistent playback status panel
 * 
 * Displays current playback information with compact controls and mini-waveform.
 * Features:
 *   - Collapsible with toggle button
 *   - Current file display
 *   - Mini waveform with playback position
 *   - Compact playback controls
 *   - Quick annotation entry field
 *   - State persistence
 */
Rectangle {
    id: root
    
    // Properties
    implicitHeight: collapsed ? collapsedHeight : expandedHeight
    Layout.fillWidth: true
    Layout.preferredHeight: implicitHeight
    
    color: Theme.backgroundLight
    border.color: Theme.borderColor
    border.width: 1
    
    // Sizing
    readonly property int collapsedHeight: 30
    readonly property int expandedHeight: 180
    
    // State
    property bool collapsed: false
    
    // Signals
    signal annotationRequested(string text)
    
    // Smooth height animation
    Behavior on implicitHeight {
        NumberAnimation {
            duration: 200
            easing.type: Easing.InOutQuad
        }
    }
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacingSmall
        spacing: Theme.spacingSmall
        
        // Header with collapse button
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacingSmall
            
            Button {
                id: collapseButton
                text: collapsed ? "▶" : "▼"
                implicitWidth: 20
                implicitHeight: 20
                
                ToolTip.visible: hovered
                ToolTip.text: collapsed ? "Expand Now Playing Panel" : "Collapse Now Playing Panel"
                
                onClicked: {
                    collapsed = !collapsed
                    settingsManager.setNowPlayingCollapsed(collapsed)
                }
                
                background: Rectangle {
                    color: parent.hovered ? Theme.backgroundDark : "transparent"
                    radius: 2
                }
                
                contentItem: Text {
                    text: parent.text
                    color: Theme.textPrimary
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
            
            Label {
                text: "Now Playing"
                font.pixelSize: Theme.fontSizeMedium
                font.bold: true
                color: Theme.textPrimary
            }
            
            Item {
                Layout.fillWidth: true
            }
        }
        
        // Content (collapsible)
        ColumnLayout {
            id: content
            Layout.fillWidth: true
            spacing: Theme.spacingSmall
            visible: !collapsed
            opacity: collapsed ? 0 : 1
            
            Behavior on opacity {
                NumberAnimation {
                    duration: 200
                    easing.type: Easing.InOutQuad
                }
            }
            
            // Current file display
            Label {
                id: fileLabel
                text: (audioEngine && audioEngine.getCurrentFile() && fileManager) ? "♪ " + fileManager.getFileName(audioEngine.getCurrentFile()) : "No file loaded"
                font.pixelSize: Theme.fontSizeSmall
                font.italic: !(audioEngine && audioEngine.getCurrentFile())
                color: Theme.textSecondary
                Layout.fillWidth: true
                elide: Text.ElideMiddle
            }
            
            // Mini waveform
            MiniWaveformWidget {
                id: miniWaveform
                Layout.fillWidth: true
                Layout.preferredHeight: 50
                filePath: audioEngine ? audioEngine.getCurrentFile() : ""
                positionMs: 0  // Updated via onPositionChanged signal
            }
            
            // Compact playback controls
            RowLayout {
                Layout.fillWidth: true
                spacing: Theme.spacingSmall
                
                StyledButton {
                    id: playButton
                    text: (audioEngine && audioEngine.getPlaybackState() === "playing") ? "⏸" : "▶"
                    primary: true
                    implicitWidth: 32
                    implicitHeight: 32
                    enabled: audioEngine && audioEngine.getCurrentFile() !== ""
                    onClicked: {
                        if (audioEngine) {
                            audioEngine.togglePlayPause()
                        }
                    }
                    
                    ToolTip.visible: hovered
                    ToolTip.text: "Play/Pause (Space)"
                }
                
                Label {
                    id: timeLabel
                    text: audioEngine ? (formatTime(audioEngine.getPosition()) + " / " + formatTime(audioEngine.getDuration())) : "0:00 / 0:00"
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.textSecondary
                    Layout.preferredWidth: 90
                }
                
                Item {
                    Layout.fillWidth: true
                }
            }
            
            // Quick annotation entry
            RowLayout {
                Layout.fillWidth: true
                spacing: Theme.spacingSmall
                
                StyledTextField {
                    id: annotationInput
                    Layout.fillWidth: true
                    placeholderText: "Type note + Enter to annotate at current position"
                    enabled: audioEngine && audioEngine.getCurrentFile() !== ""
                    
                    onAccepted: {
                        if (text.trim().length > 0) {
                            root.annotationRequested(text.trim())
                            text = ""
                        }
                    }
                }
                
                StyledButton {
                    text: "Add Note"
                    implicitWidth: 80
                    implicitHeight: 28
                    enabled: audioEngine && audioEngine.getCurrentFile() !== "" && annotationInput.text.trim().length > 0
                    
                    ToolTip.visible: hovered
                    ToolTip.text: "Add annotation at current playback position"
                    
                    onClicked: {
                        if (annotationInput.text.trim().length > 0) {
                            root.annotationRequested(annotationInput.text.trim())
                            annotationInput.text = ""
                        }
                    }
                }
            }
        }
    }
    
    // Update time display when playback is active
    Timer {
        id: updateTimer
        interval: 100
        running: audioEngine && audioEngine.getPlaybackState() === "playing" && !collapsed
        repeat: true
        onTriggered: {
            if (audioEngine) {
                timeLabel.text = formatTime(audioEngine.getPosition()) + " / " + formatTime(audioEngine.getDuration())
            }
        }
    }
    
    // Connections to audio engine
    Connections {
        target: audioEngine
        
        function onCurrentFileChanged(filePath) {
            // Update file label
            if (filePath && filePath.length > 0) {
                fileLabel.text = "♪ " + fileManager.getFileName(filePath)
            } else {
                fileLabel.text = "No file loaded"
                miniWaveform.clear()
            }
        }
        
        function onPlaybackStateChanged(state) {
            // Update play button icon
            playButton.text = state === "playing" ? "⏸" : "▶"
        }
        
        function onDurationChanged(duration) {
            timeLabel.text = formatTime(audioEngine.getPosition()) + " / " + formatTime(duration)
        }
        
        function onPositionChanged(position) {
            // Update mini waveform playback position
            miniWaveform.positionMs = position
        }
    }
    
    // Restore collapsed state on startup
    Component.onCompleted: {
        collapsed = settingsManager.getNowPlayingCollapsed()
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
