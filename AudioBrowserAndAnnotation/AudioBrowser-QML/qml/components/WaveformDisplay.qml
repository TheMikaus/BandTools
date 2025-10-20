import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import AudioBrowser 1.0
import "../styles"
import "../components"

/**
 * WaveformDisplay Component
 * 
 * Displays audio waveform with playback position tracking and click-to-seek functionality.
 * Integrates with AudioEngine and WaveformEngine for seamless playback control.
 */
Rectangle {
    id: root
    
    color: Theme.backgroundColor
    border.color: Theme.borderColor
    border.width: 1
    radius: Theme.radiusSmall
    
    // Properties
    property string filePath: ""
    property bool autoGenerate: true
    property real bpm: 0.0  // Tempo in BPM for measure markers
    
    // State indicators
    property bool isLoading: false
    property bool hasWaveform: false
    property string errorMessage: ""
    
    // Zoom control
    property real zoomLevel: 1.0  // 1.0 = normal, 2.0 = 2x zoom, etc.
    
    // Handle filePath changes
    onFilePathChanged: {
        setFilePath(filePath)
    }
    
    // Waveform view
    Flickable {
        id: flickable
        anchors.fill: parent
        anchors.margins: 1
        contentWidth: waveform.width
        contentHeight: waveform.height
        clip: true
        
        ScrollBar.horizontal: ScrollBar {
            policy: zoomLevel > 1.0 ? ScrollBar.AlwaysOn : ScrollBar.AsNeeded
        }
        
        // Container for waveform and markers
        Item {
            width: Math.max(flickable.width, flickable.width * zoomLevel)
            height: flickable.height
            
            WaveformView {
                id: waveform
                anchors.fill: parent
                
                // Colors from theme
                backgroundColor: Theme.backgroundColor
                waveformColor: Theme.accentPrimary
                playheadColor: Theme.accentDanger
                axisColor: Theme.backgroundLight
                tempoMarkerColor: Theme.textMuted
                
                // Bind playback position
                positionMs: audioEngine.getPosition()
                
                // Bind BPM for tempo markers
                bpm: root.bpm
                
                // Handle seek requests
                onSeekRequested: function(positionMs) {
                    audioEngine.seek(positionMs)
                }
            }
            
            // Annotation markers layer
            Repeater {
                id: markersRepeater
                model: annotationManager ? annotationManager.getAnnotations() : []
                
                AnnotationMarker {
                    timestampMs: modelData.timestamp_ms || 0
                    text: modelData.text || ""
                    category: modelData.category || ""
                    important: modelData.important || false
                    markerColor: modelData.color || Theme.accentPrimary
                    waveformDurationMs: waveform.durationMs
                    waveformWidth: waveform.width
                    
                    onClicked: function(timestamp) {
                        audioEngine.seek(timestamp)
                    }
                    
                    onDoubleClicked: function(timestamp) {
                        // Signal to edit this annotation
                        root.annotationDoubleClicked(modelData)
                    }
                    
                    onRightClicked: function(timestamp) {
                        // Could show context menu
                    }
                }
            }
            
            // Clip markers layer
            Repeater {
                id: clipMarkersRepeater
                model: clipManager ? clipManager.getClipCount() : 0
                
                ClipMarker {
                    startMs: {
                        if (!clipManager) return 0;
                        const clip = clipManager.getClip(index);
                        return clip.start_ms || 0;
                    }
                    endMs: {
                        if (!clipManager) return 0;
                        const clip = clipManager.getClip(index);
                        return clip.end_ms || 0;
                    }
                    clipName: {
                        if (!clipManager) return "";
                        const clip = clipManager.getClip(index);
                        return clip.name || "";
                    }
                    clipNotes: {
                        if (!clipManager) return "";
                        const clip = clipManager.getClip(index);
                        return clip.notes || "";
                    }
                    clipIndex: index
                    waveformWidth: waveform.width
                    waveformDuration: waveform.durationMs
                    
                    onClicked: function(clipIndex) {
                        // Signal to select this clip
                        root.clipClicked(clipIndex);
                    }
                    
                    onDoubleClicked: function(clipIndex) {
                        // Signal to edit this clip
                        root.clipDoubleClicked(clipIndex);
                    }
                }
            }
        }
    }
    
    // Signals for annotation and clip interaction
    signal annotationDoubleClicked(var annotationData)
    signal clipClicked(int clipIndex)
    signal clipDoubleClicked(int clipIndex)
    
    // Loading indicator
    Rectangle {
        anchors.centerIn: parent
        width: loadingColumn.width + Theme.spacingLarge * 2
        height: loadingColumn.height + Theme.spacingLarge * 2
        color: Theme.backgroundLight
        radius: Theme.radiusNormal
        visible: isLoading && !hasWaveform
        
        ColumnLayout {
            id: loadingColumn
            anchors.centerIn: parent
            spacing: Theme.spacingNormal
            
            BusyIndicator {
                Layout.alignment: Qt.AlignHCenter
                running: isLoading
            }
            
            Label {
                text: "Generating waveform..."
                color: Theme.textColor
                font.pixelSize: Theme.fontSizeNormal
                Layout.alignment: Qt.AlignHCenter
            }
            
            ProgressBar {
                id: progressBar
                Layout.preferredWidth: 200
                Layout.alignment: Qt.AlignHCenter
                from: 0
                to: 100
                value: 0
            }
        }
    }
    
    // Error display
    Rectangle {
        anchors.centerIn: parent
        width: errorColumn.width + Theme.spacingLarge * 2
        height: errorColumn.height + Theme.spacingLarge * 2
        color: Theme.backgroundLight
        radius: Theme.radiusNormal
        visible: errorMessage !== "" && !isLoading
        
        ColumnLayout {
            id: errorColumn
            anchors.centerIn: parent
            spacing: Theme.spacingNormal
            
            Label {
                text: "⚠"
                color: Theme.accentDanger
                font.pixelSize: 32
                Layout.alignment: Qt.AlignHCenter
            }
            
            Label {
                text: "Error generating waveform"
                color: Theme.textColor
                font.pixelSize: Theme.fontSizeNormal
                font.bold: true
                Layout.alignment: Qt.AlignHCenter
            }
            
            Label {
                text: errorMessage
                color: Theme.textMuted
                font.pixelSize: Theme.fontSizeSmall
                Layout.alignment: Qt.AlignHCenter
                wrapMode: Text.WordWrap
                Layout.maximumWidth: 300
            }
        }
    }
    
    // Empty state
    Rectangle {
        anchors.centerIn: parent
        width: emptyColumn.width + Theme.spacingLarge * 2
        height: emptyColumn.height + Theme.spacingLarge * 2
        color: Theme.backgroundLight
        radius: Theme.radiusNormal
        visible: !isLoading && !hasWaveform && errorMessage === "" && filePath === ""
        
        ColumnLayout {
            id: emptyColumn
            anchors.centerIn: parent
            spacing: Theme.spacingNormal
            
            Label {
                text: "📊"
                color: Theme.textMuted
                font.pixelSize: 48
                Layout.alignment: Qt.AlignHCenter
            }
            
            Label {
                text: "No audio file selected"
                color: Theme.textMuted
                font.pixelSize: Theme.fontSizeNormal
                Layout.alignment: Qt.AlignHCenter
            }
            
            Label {
                text: "Select an audio file to view its waveform"
                color: Theme.textMuted
                font.pixelSize: Theme.fontSizeSmall
                Layout.alignment: Qt.AlignHCenter
            }
        }
    }
    
    // Connections to waveform engine
    Connections {
        target: waveformEngine
        
        function onWaveformReady(path) {
            if (path === filePath) {
                loadWaveformData()
                isLoading = false
                hasWaveform = true
                errorMessage = ""
            }
        }
        
        function onWaveformProgress(path, current, total) {
            if (path === filePath) {
                progressBar.value = (current / total) * 100
            }
        }
        
        function onWaveformError(path, error) {
            if (path === filePath) {
                isLoading = false
                hasWaveform = false
                errorMessage = error
            }
        }
    }
    
    // Connections to audio engine
    Connections {
        target: audioEngine
        
        function onPositionChanged(position) {
            waveform.positionMs = position
        }
        
        function onCurrentFileChanged(path) {
            if (autoGenerate && path !== "" && path === filePath) {
                generateWaveform()
            }
        }
    }
    
    // Timer to regularly update playback position
    Timer {
        id: positionUpdateTimer
        interval: 50  // Update every 50ms for smooth animation
        running: audioEngine && audioEngine.isPlaying()
        repeat: true
        
        onTriggered: {
            if (audioEngine) {
                waveform.positionMs = audioEngine.getPosition()
            }
        }
    }
    
    // Functions
    function setFilePath(path) {
        filePath = path
        errorMessage = ""
        
        if (path === "") {
            hasWaveform = false
            waveform.peaks = []
            waveform.durationMs = 0
            return
        }
        
        // Check if waveform is already cached
        if (waveformEngine.isWaveformReady(path)) {
            loadWaveformData()
            hasWaveform = true
            isLoading = false
        } else if (autoGenerate) {
            generateWaveform()
        }
    }
    
    function generateWaveform() {
        if (filePath === "") {
            return
        }
        
        isLoading = true
        hasWaveform = false
        errorMessage = ""
        progressBar.value = 0
        
        waveformEngine.generateWaveform(filePath)
    }
    
    function loadWaveformData() {
        if (filePath === "") {
            return
        }
        
        var peaks = waveformEngine.getWaveformData(filePath)
        var duration = waveformEngine.getWaveformDuration(filePath)
        
        waveform.peaks = peaks
        waveform.durationMs = duration
        
        // Set audio file path for spectrogram computation
        waveform.setAudioFile(filePath)
        
        hasWaveform = peaks.length > 0
    }
    
    function cancelGeneration() {
        if (isLoading && filePath !== "") {
            waveformEngine.cancelWaveform(filePath)
            isLoading = false
        }
    }
    
    function zoomIn() {
        zoomLevel = Math.min(zoomLevel * 1.5, 10.0)
    }
    
    function zoomOut() {
        zoomLevel = Math.max(zoomLevel / 1.5, 1.0)
    }
    
    function resetZoom() {
        zoomLevel = 1.0
    }
    
    function setSpectrogramMode(enabled) {
        waveform.showSpectrogram = enabled
        // Set audio file path for spectrogram computation
        if (enabled && filePath !== "") {
            waveform.setAudioFile(filePath)
        }
    }
    
    // Listen for clip changes to update markers
    Connections {
        target: clipManager
        
        function onClipsChanged(filePath) {
            // Refresh clip markers by updating the model
            clipMarkersRepeater.model = clipManager.getClipCount();
        }
    }
}
