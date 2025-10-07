import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "../components"
import "../styles"
import "../dialogs"

/**
 * ClipsTab Component
 * 
 * Main tab for audio clip management.
 * 
 * Features:
 * - View all clips in a table
 * - Create, edit, delete clips
 * - Export clips as separate audio files
 * - Visual clip markers on waveform
 * - Clip playback controls
 */
Item {
    id: clipsTab
    
    // ========== Properties ==========
    
    property var clipManager: null
    property var audioEngine: null
    property int selectedClipIndex: -1
    property bool loopClip: false
    
    // Clip marker properties for keyboard shortcuts
    property int clipStartMarker: -1  // -1 means not set
    property int clipEndMarker: -1    // -1 means not set
    
    // ========== Clip Dialog ==========
    
    ClipDialog {
        id: clipDialog
        audioEngine: clipsTab.audioEngine
        clipManager: clipsTab.clipManager
        
        onClipCreated: function(startMs, endMs, name, notes) {
            if (clipManager) {
                clipManager.addClip(startMs, endMs, name, notes);
            }
        }
        
        onClipUpdated: function(index, startMs, endMs, name, notes) {
            if (clipManager) {
                clipManager.updateClip(index, startMs, endMs, name, notes);
            }
        }
    }
    
    // ========== Main Layout ==========
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacingMedium
        spacing: Theme.spacingMedium
        
        // ========== Toolbar ==========
        
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacingNormal
            
            StyledLabel {
                text: "Clips"
                heading: true
            }
            
            // Clip marker status indicator
            Label {
                id: markerStatusLabel
                text: {
                    if (clipStartMarker >= 0 && clipEndMarker >= 0) {
                        return "⏺ Markers: [" + formatTime(clipStartMarker) + " - " + formatTime(clipEndMarker) + "]"
                    } else if (clipStartMarker >= 0) {
                        return "⏺ Start: " + formatTime(clipStartMarker) + " (press ] to set end)"
                    } else if (clipEndMarker >= 0) {
                        return "⏺ End: " + formatTime(clipEndMarker) + " (press [ to set start)"
                    } else {
                        return ""
                    }
                }
                font.pixelSize: Theme.fontSizeSmall
                color: (clipStartMarker >= 0 || clipEndMarker >= 0) ? Theme.accentWarning : Theme.textMuted
                visible: clipStartMarker >= 0 || clipEndMarker >= 0
            }
            
            Item { Layout.fillWidth: true }
            
            StyledButton {
                id: addButton
                text: "➕ Add Clip"
                primary: true
                enabled: audioEngine && audioEngine.getCurrentFile() !== ""
                
                ToolTip.visible: hovered
                ToolTip.text: "Create a new clip from the current audio file"
                
                onClicked: {
                    // Get current playback position for defaults
                    const currentPos = audioEngine ? audioEngine.getPosition() : 0;
                    const duration = audioEngine ? audioEngine.getDuration() : 0;
                    
                    // Default: 5 second clip from current position
                    const start = Math.min(currentPos, duration - 5000);
                    const end = Math.min(currentPos + 5000, duration);
                    
                    clipDialog.openDialog(false, -1, start, end, "", "");
                }
            }
            
            StyledButton {
                id: editButton
                text: "✏ Edit"
                enabled: selectedClipIndex >= 0
                
                ToolTip.visible: hovered
                ToolTip.text: "Edit the selected clip"
                
                onClicked: {
                    if (clipManager && selectedClipIndex >= 0) {
                        const clip = clipManager.getClip(selectedClipIndex);
                        clipDialog.openDialog(
                            true,
                            selectedClipIndex,
                            clip.start_ms,
                            clip.end_ms,
                            clip.name,
                            clip.notes
                        );
                    }
                }
            }
            
            StyledButton {
                id: deleteButton
                text: "🗑 Delete"
                danger: true
                enabled: selectedClipIndex >= 0
                
                ToolTip.visible: hovered
                ToolTip.text: "Delete the selected clip"
                
                onClicked: {
                    deleteConfirmDialog.open();
                }
            }
            
            StyledButton {
                id: playButton
                text: "▶ Play Clip"
                success: true
                enabled: selectedClipIndex >= 0 && audioEngine
                
                ToolTip.visible: hovered
                ToolTip.text: "Play the selected clip region"
                
                onClicked: {
                    if (clipManager && audioEngine && selectedClipIndex >= 0) {
                        const clip = clipManager.getClip(selectedClipIndex);
                        audioEngine.playClip(clip.start_ms, clip.end_ms, loopClip);
                    }
                }
            }
            
            CheckBox {
                id: loopCheckbox
                text: "Loop"
                checked: clipsTab.loopClip
                enabled: selectedClipIndex >= 0
                
                ToolTip.visible: hovered
                ToolTip.text: "Loop clip playback for practice"
                
                contentItem: Text {
                    text: loopCheckbox.text
                    font.pixelSize: Theme.fontSizeNormal
                    color: loopCheckbox.enabled ? Theme.textColor : Theme.textMuted
                    leftPadding: loopCheckbox.indicator.width + loopCheckbox.spacing
                    verticalAlignment: Text.AlignVCenter
                }
                
                onCheckedChanged: {
                    clipsTab.loopClip = checked;
                }
            }
            
            StyledButton {
                id: exportButton
                text: "💾 Export"
                enabled: selectedClipIndex >= 0
                
                ToolTip.visible: hovered
                ToolTip.text: "Export the selected clip as a separate audio file"
                
                onClicked: {
                    if (clipManager && selectedClipIndex >= 0) {
                        clipManager.exportClip(selectedClipIndex, "");
                    }
                }
            }
            
            StyledButton {
                id: clearButton
                text: "Clear All"
                enabled: clipManager && clipManager.getClipCount() > 0
                
                ToolTip.visible: hovered
                ToolTip.text: "Delete all clips for the current file"
                
                onClicked: {
                    clearConfirmDialog.open();
                }
            }
        }
        
        // ========== Clips Table ==========
        
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: Theme.backgroundColor
            border.color: Theme.borderColor
            border.width: 1
            radius: Theme.radiusSmall
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 1
                spacing: 0
                
                // Table header
                Rectangle {
                    Layout.fillWidth: true
                    height: 30
                    color: Theme.backgroundLight
                    
                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: Theme.spacingSmall
                        anchors.rightMargin: Theme.spacingSmall
                        spacing: Theme.spacingSmall
                        
                        StyledLabel {
                            text: "Start"
                            font.bold: true
                            Layout.preferredWidth: 100
                        }
                        
                        StyledLabel {
                            text: "End"
                            font.bold: true
                            Layout.preferredWidth: 100
                        }
                        
                        StyledLabel {
                            text: "Duration"
                            font.bold: true
                            Layout.preferredWidth: 100
                        }
                        
                        StyledLabel {
                            text: "Name"
                            font.bold: true
                            Layout.fillWidth: true
                        }
                    }
                }
                
                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: Theme.borderColor
                }
                
                // Clips list or empty state
                StackLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    currentIndex: clipManager && clipManager.getClipCount() > 0 ? 1 : 0
                    
                    // Empty state
                    Item {
                        ColumnLayout {
                            anchors.centerIn: parent
                            spacing: Theme.spacingLarge
                            
                            StyledLabel {
                                text: "📹 No Clips Yet"
                                heading: true
                                Layout.alignment: Qt.AlignHCenter
                            }
                            
                            StyledLabel {
                                text: "Create clips to extract and export specific sections of your audio.\n\n" +
                                      "1. Set playback position\n" +
                                      "2. Click 'Add Clip' button\n" +
                                      "3. Adjust start/end times\n" +
                                      "4. Export to save as separate file"
                                secondary: true
                                horizontalAlignment: Text.AlignHCenter
                                Layout.alignment: Qt.AlignHCenter
                            }
                        }
                    }
                    
                    // Clips list
                    ScrollView {
                        clip: true
                        
                        ListView {
                            id: clipsListView
                            model: clipManager ? clipManager.getClipCount() : 0
                            spacing: 0
                            
                            delegate: Rectangle {
                                width: clipsListView.width
                                height: 40
                                color: {
                                    if (index === selectedClipIndex) return Theme.selectionColor;
                                    if (mouseArea.containsMouse) return Theme.backgroundLight;
                                    return index % 2 === 0 ? Theme.backgroundColor : Theme.backgroundMedium;
                                }
                                
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.leftMargin: Theme.spacingSmall
                                    anchors.rightMargin: Theme.spacingSmall
                                    spacing: Theme.spacingSmall
                                    
                                    StyledLabel {
                                        text: {
                                            if (!clipManager) return "";
                                            const clip = clipManager.getClip(index);
                                            return formatTime(clip.start_ms);
                                        }
                                        Layout.preferredWidth: 100
                                    }
                                    
                                    StyledLabel {
                                        text: {
                                            if (!clipManager) return "";
                                            const clip = clipManager.getClip(index);
                                            return formatTime(clip.end_ms);
                                        }
                                        Layout.preferredWidth: 100
                                    }
                                    
                                    StyledLabel {
                                        text: {
                                            if (!clipManager) return "";
                                            const clip = clipManager.getClip(index);
                                            return formatTime(clip.duration_ms);
                                        }
                                        secondary: true
                                        Layout.preferredWidth: 100
                                    }
                                    
                                    StyledLabel {
                                        text: {
                                            if (!clipManager) return "";
                                            const clip = clipManager.getClip(index);
                                            return clip.name !== "" ? clip.name : "(Unnamed)";
                                        }
                                        Layout.fillWidth: true
                                    }
                                }
                                
                                MouseArea {
                                    id: mouseArea
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    
                                    onClicked: {
                                        selectedClipIndex = index;
                                        // Seek to clip start
                                        if (audioEngine && clipManager) {
                                            const clip = clipManager.getClip(index);
                                            audioEngine.seek(clip.start_ms);
                                        }
                                    }
                                    
                                    onDoubleClicked: {
                                        selectedClipIndex = index;
                                        editButton.clicked();
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        // ========== Status Bar ==========
        
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacingNormal
            
            StyledLabel {
                text: {
                    if (!clipManager) return "No clip manager";
                    const count = clipManager.getClipCount();
                    return count === 0 ? "No clips" : 
                           count === 1 ? "1 clip" :
                           count + " clips";
                }
                secondary: true
            }
            
            Item { Layout.fillWidth: true }
            
            StyledLabel {
                text: audioEngine && audioEngine.getCurrentFile() !== "" 
                    ? "File loaded" 
                    : "No file selected"
                secondary: true
            }
        }
    }
    
    // ========== Confirmation Dialogs ==========
    
    Dialog {
        id: deleteConfirmDialog
        title: "Delete Clip?"
        modal: true
        anchors.centerIn: parent
        
        standardButtons: Dialog.Yes | Dialog.No
        
        Label {
            text: "Are you sure you want to delete this clip?\nThis action cannot be undone."
            color: Theme.textColor
        }
        
        onAccepted: {
            if (clipManager && selectedClipIndex >= 0) {
                clipManager.deleteClip(selectedClipIndex);
                selectedClipIndex = -1;
            }
        }
    }
    
    Dialog {
        id: clearConfirmDialog
        title: "Clear All Clips?"
        modal: true
        anchors.centerIn: parent
        
        standardButtons: Dialog.Yes | Dialog.No
        
        Label {
            text: "Are you sure you want to delete all clips for this file?\nThis action cannot be undone."
            color: Theme.textColor
        }
        
        onAccepted: {
            if (clipManager) {
                clipManager.clearClips();
                selectedClipIndex = -1;
            }
        }
    }
    
    // ========== Helper Functions ==========
    
    function formatTime(ms) {
        if (ms === undefined || ms === null) return "00:00.000";
        const totalSeconds = Math.floor(ms / 1000);
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        const milliseconds = ms % 1000;
        return minutes.toString().padStart(2, '0') + ":" +
               seconds.toString().padStart(2, '0') + "." +
               milliseconds.toString().padStart(3, '0');
    }
    
    // ========== Clip Marker Functions (for keyboard shortcuts) ==========
    
    function setClipStartMarker() {
        if (!audioEngine) return;
        clipStartMarker = audioEngine.getPosition();
        console.log("Clip start marker set at:", formatTime(clipStartMarker));
        
        // If both markers are set and end is after start, auto-create clip
        if (clipStartMarker >= 0 && clipEndMarker >= 0 && clipEndMarker > clipStartMarker) {
            createClipFromMarkers();
        }
    }
    
    function setClipEndMarker() {
        if (!audioEngine) return;
        clipEndMarker = audioEngine.getPosition();
        console.log("Clip end marker set at:", formatTime(clipEndMarker));
        
        // If both markers are set and end is after start, auto-create clip
        if (clipStartMarker >= 0 && clipEndMarker >= 0 && clipEndMarker > clipStartMarker) {
            createClipFromMarkers();
        }
    }
    
    function createClipFromMarkers() {
        if (clipStartMarker < 0 || clipEndMarker < 0) {
            console.warn("Both markers must be set to create a clip");
            return;
        }
        
        if (clipEndMarker <= clipStartMarker) {
            console.warn("End marker must be after start marker");
            return;
        }
        
        // Open the clip dialog with the marker positions
        clipDialog.openDialog(false, -1, clipStartMarker, clipEndMarker, "", "");
        
        // Reset markers after creating clip
        clipStartMarker = -1;
        clipEndMarker = -1;
    }
    
    function clearClipMarkers() {
        clipStartMarker = -1;
        clipEndMarker = -1;
        console.log("Clip markers cleared");
    }
    
    // ========== Connections ==========
    
    Connections {
        target: clipManager
        
        function onClipsChanged(filePath) {
            // Refresh the list view
            clipsListView.model = clipManager.getClipCount();
        }
        
        function onErrorOccurred(message) {
            console.error("Clip error:", message);
        }
        
        function onExportComplete(outputPath) {
            console.log("Clip exported to:", outputPath);
            // Could show a success notification here
        }
    }
}
