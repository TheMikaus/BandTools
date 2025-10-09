import QtQuick
import QtQuick.Controls.Basic
import AudioBrowser 1.0
import "../styles"

/**
 * MiniWaveformWidget - Compact waveform display for Now Playing panel
 * 
 * Displays a simplified waveform with playback position indicator.
 * Used in the Now Playing panel for at-a-glance playback monitoring.
 */
Rectangle {
    id: root
    
    // Properties
    implicitHeight: 50
    implicitWidth: 200
    
    color: Theme.backgroundColor
    border.color: Theme.borderColor
    border.width: 1
    radius: Theme.radiusSmall
    
    // Waveform data
    property string filePath: ""
    property int positionMs: 0
    property int durationMs: 0
    
    // Mini waveform view
    WaveformView {
        id: miniWaveform
        anchors.fill: parent
        anchors.margins: 1
        
        // Colors from theme
        backgroundColor: Theme.backgroundColor
        waveformColor: Theme.accentPrimary
        playheadColor: Theme.accentDanger
        axisColor: Theme.backgroundLight
        
        // Bind playback position
        positionMs: root.positionMs
        
        // No interaction for mini waveform
        enabled: false
    }
    
    // Load waveform when file changes
    onFilePathChanged: {
        if (filePath && filePath.length > 0) {
            waveformEngine.generateWaveform(filePath)
        } else {
            // Clear the waveform display
            miniWaveform.clearWaveform()
            root.durationMs = 0
        }
    }
    
    // Update waveform view when data is available
    Connections {
        target: waveformEngine
        
        function onWaveformReady(path) {
            // Only update if this is for our file
            if (path === filePath) {
                var peaks = waveformEngine.getWaveformData(path)
                var duration = waveformEngine.getWaveformDuration(path)
                miniWaveform.setWaveformData(peaks, duration)
                root.durationMs = duration
            }
        }
    }
    
    // Function to clear the waveform
    function clear() {
        filePath = ""
        positionMs = 0
        durationMs = 0
        miniWaveform.clearWaveform()
    }
}
