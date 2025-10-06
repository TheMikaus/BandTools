import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"
import "../dialogs"
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
            Layout.preferredHeight: 250
            Layout.minimumHeight: 200
            autoGenerate: true
            
            onAnnotationDoubleClicked: function(annotationData) {
                var index = annotationsTable.currentRow
                if (index >= 0) {
                    openEditDialog(index)
                }
            }
        }
        
        // Annotation table and controls
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumHeight: 200
            color: Theme.backgroundLight
            radius: Theme.radiusSmall
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: Theme.spacingNormal
                spacing: Theme.spacingSmall
                
                // Header with controls
                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spacingNormal
                    
                    Label {
                        text: "Annotations (" + annotationManager.getAnnotationCount() + ")"
                        font.pixelSize: Theme.fontSizeNormal
                        font.bold: true
                        color: Theme.textColor
                    }
                    
                    Item { Layout.fillWidth: true }
                    
                    StyledButton {
                        text: "Add"
                        primary: true
                        enabled: audioEngine.getCurrentFile() !== ""
                        Layout.preferredWidth: 80
                        onClicked: openAddDialog()
                    }
                    
                    StyledButton {
                        text: "Edit"
                        enabled: annotationsTable.currentRow >= 0
                        Layout.preferredWidth: 80
                        onClicked: openEditDialog(annotationsTable.currentRow)
                    }
                    
                    StyledButton {
                        text: "Delete"
                        danger: true
                        enabled: annotationsTable.currentRow >= 0
                        Layout.preferredWidth: 80
                        onClicked: deleteAnnotation(annotationsTable.currentRow)
                    }
                    
                    StyledButton {
                        text: "Clear All"
                        enabled: annotationManager.getAnnotationCount() > 0
                        Layout.preferredWidth: 80
                        onClicked: clearAllDialog.open()
                    }
                }
                
                // Annotation table
                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: Theme.backgroundColor
                    border.color: Theme.borderColor
                    border.width: 1
                    radius: Theme.radiusSmall
                    
                    TableView {
                        id: annotationsTable
                        anchors.fill: parent
                        anchors.margins: 1
                        clip: true
                        
                        model: annotationsModel
                        
                        property int currentRow: -1
                        
                        // Column widths
                        columnWidthProvider: function(column) {
                            switch(column) {
                                case 0: return 100  // Time
                                case 1: return 100  // Category
                                case 2: return width - 250  // Text (fill remaining)
                                case 3: return 80   // Important
                                default: return 100
                            }
                        }
                        
                        delegate: Rectangle {
                            implicitHeight: 32
                            color: annotationsTable.currentRow === row ? 
                                   Theme.backgroundLight : 
                                   (row % 2 === 0 ? Theme.backgroundColor : Theme.backgroundLight)
                            
                            Text {
                                anchors.fill: parent
                                anchors.leftMargin: 8
                                anchors.rightMargin: 8
                                text: display || ""
                                color: Theme.textColor
                                font.pixelSize: Theme.fontSizeSmall
                                verticalAlignment: Text.AlignVCenter
                                elide: Text.ElideRight
                            }
                            
                            MouseArea {
                                anchors.fill: parent
                                onClicked: {
                                    annotationsTable.currentRow = row
                                    // Seek to annotation time
                                    var annotations = annotationManager.getAnnotations()
                                    if (row < annotations.length) {
                                        audioEngine.seek(annotations[row].timestamp_ms)
                                    }
                                }
                                onDoubleClicked: {
                                    annotationsTable.currentRow = row
                                    openEditDialog(row)
                                }
                            }
                        }
                    }
                    
                    // Empty state
                    Label {
                        visible: annotationManager.getAnnotationCount() === 0
                        anchors.centerIn: parent
                        text: "No annotations yet\nClick 'Add' or double-click on waveform to create"
                        font.pixelSize: Theme.fontSizeNormal
                        color: Theme.textMuted
                        horizontalAlignment: Text.AlignHCenter
                    }
                }
            }
        }
    }
    
    // Annotation dialog
    AnnotationDialog {
        id: annotationDialog
        anchors.centerIn: Overlay.overlay
        
        onAnnotationAccepted: function(timestampMs, text, category, important, color) {
            annotationManager.addAnnotation(timestampMs, text, category, important, color)
            refreshAnnotations()
        }
        
        onAnnotationUpdated: function(index, timestampMs, text, category, important, color) {
            annotationManager.updateAnnotation(index, timestampMs, text, category, important, color)
            refreshAnnotations()
        }
    }
    
    // Clear all confirmation dialog
    Dialog {
        id: clearAllDialog
        title: "Clear All Annotations"
        modal: true
        standardButtons: Dialog.Yes | Dialog.No
        anchors.centerIn: Overlay.overlay
        
        Label {
            text: "Are you sure you want to delete all annotations?\nThis action cannot be undone."
            color: Theme.textColor
            wrapMode: Text.WordWrap
        }
        
        onAccepted: {
            annotationManager.clearAnnotations()
            refreshAnnotations()
        }
    }
    
    // Update waveform when audio file changes
    Connections {
        target: audioEngine
        
        function onCurrentFileChanged(path) {
            if (path !== "") {
                waveformDisplay.setFilePath(path)
                annotationManager.setCurrentFile(path)
                refreshAnnotations()
            }
        }
    }
    
    // Update when annotations change
    Connections {
        target: annotationManager
        
        function onAnnotationsChanged(path) {
            if (path === audioEngine.getCurrentFile()) {
                refreshAnnotations()
            }
        }
    }
    
    // Helper functions
    function openAddDialog() {
        annotationDialog.reset()
        annotationDialog.timestampMs = audioEngine.getPosition()
        annotationDialog.updateFields()
        annotationDialog.open()
    }
    
    function openEditDialog(index) {
        if (index < 0) return
        
        var annotation = annotationManager.getAnnotation(index)
        if (annotation && annotation.timestamp_ms !== undefined) {
            annotationDialog.loadAnnotation(
                index,
                annotation.timestamp_ms,
                annotation.text,
                annotation.category || "",
                annotation.important || false,
                annotation.color || "#3498db"
            )
            annotationDialog.open()
        }
    }
    
    function deleteAnnotation(index) {
        if (index >= 0) {
            annotationManager.deleteAnnotation(index)
            annotationsTable.currentRow = -1
        }
    }
    
    function refreshAnnotations() {
        var annotations = annotationManager.getAnnotations()
        annotationsModel.setAnnotations(annotations)
        waveformDisplay.update()  // Force waveform to redraw markers
    }
    
    // Initialize
    Component.onCompleted: {
        if (audioEngine.getCurrentFile() !== "") {
            annotationManager.setCurrentFile(audioEngine.getCurrentFile())
            refreshAnnotations()
        }
    }
}
