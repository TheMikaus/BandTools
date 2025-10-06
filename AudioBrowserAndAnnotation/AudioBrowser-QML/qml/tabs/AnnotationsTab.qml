import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"
import "../styles"

/**
 * AnnotationsTab
 * 
 * Phase 2: Waveform visualization and annotation management
 */
Item {
    id: root
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacingNormal
        spacing: Theme.spacingNormal
        
        // Toolbar
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: Theme.toolbarHeight
            color: Theme.backgroundLight
            radius: Theme.radiusSmall
            
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: Theme.spacingNormal
                anchors.rightMargin: Theme.spacingNormal
                spacing: Theme.spacingNormal
                
                Label {
                    text: "Waveform Display"
                    font.pixelSize: Theme.fontSizeNormal
                    font.bold: true
                    color: Theme.textColor
                }
                
                Item { Layout.fillWidth: true }
                
                // Zoom controls
                Label {
                    text: "Zoom:"
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.textMuted
                }
                
                StyledButton {
                    text: "−"
                    Layout.preferredWidth: 32
                    enabled: waveformDisplay.zoomLevel > 1.0
                    onClicked: waveformDisplay.zoomOut()
                }
                
                Label {
                    text: Math.round(waveformDisplay.zoomLevel * 100) + "%"
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.textColor
                    Layout.preferredWidth: 50
                    horizontalAlignment: Text.AlignHCenter
                }
                
                StyledButton {
                    text: "+"
                    Layout.preferredWidth: 32
                    enabled: waveformDisplay.zoomLevel < 10.0
                    onClicked: waveformDisplay.zoomIn()
                }
                
                StyledButton {
                    text: "Reset"
                    Layout.preferredWidth: 60
                    enabled: waveformDisplay.zoomLevel !== 1.0
                    onClicked: waveformDisplay.resetZoom()
                }
                
                Rectangle {
                    width: 1
                    height: parent.height * 0.6
                    color: Theme.borderColor
                    Layout.alignment: Qt.AlignVCenter
                }
                
                StyledButton {
                    text: "Generate"
                    primary: true
                    enabled: audioEngine.getCurrentFile() !== ""
                    onClicked: {
                        waveformDisplay.generateWaveform()
                    }
                }
                
                Label {
                    text: audioEngine.getCurrentFile() !== "" ? 
                          "Current: " + fileManager.getFileName(audioEngine.getCurrentFile()) :
                          "No file selected"
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.textMuted
                }
            }
        }
        
        // Waveform display
        WaveformDisplay {
            id: waveformDisplay
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumHeight: 200
            autoGenerate: true
        }
        
        // Annotation controls (placeholder for future implementation)
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 150
            color: Theme.backgroundLight
            radius: Theme.radiusSmall
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: Theme.spacingNormal
                spacing: Theme.spacingSmall
                
                Label {
                    text: "Annotation Controls"
                    font.pixelSize: Theme.fontSizeNormal
                    font.bold: true
                    color: Theme.textColor
                }
                
                Label {
                    text: "Annotation table and editing features will be added in the next phase"
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.textMuted
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }
                
                RowLayout {
                    spacing: Theme.spacingNormal
                    
                    StyledButton {
                        text: "Add Annotation"
                        enabled: false
                        Layout.preferredWidth: 120
                    }
                    
                    StyledButton {
                        text: "Edit"
                        enabled: false
                        Layout.preferredWidth: 80
                    }
                    
                    StyledButton {
                        text: "Delete"
                        danger: true
                        enabled: false
                        Layout.preferredWidth: 80
                    }
                }
            }
        }
    }
    
    // Update waveform when audio file changes
    Connections {
        target: audioEngine
        
        function onCurrentFileChanged(path) {
            if (path !== "") {
                waveformDisplay.setFilePath(path)
            }
        }
    }
}
