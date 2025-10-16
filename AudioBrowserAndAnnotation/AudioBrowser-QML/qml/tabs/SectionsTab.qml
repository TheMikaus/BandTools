import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "../components"
import "../styles"
import "../dialogs"

/**
 * SectionsTab Component
 * 
 * Main tab for managing song sections.
 * 
 * Features:
 * - View all sections in a table
 * - Create, edit, delete sections
 * - Auto-detect sections using fingerprints
 * - Common section labels (Verse, Chorus, Bridge, etc.)
 */
Item {
    id: sectionsTab
    
    // Properties
    property int selectedSectionIndex: -1
    
    // Dialog for adding/editing sections
    Dialog {
        id: sectionDialog
        title: sectionDialog.editMode ? "Edit Section" : "Add Section"
        modal: true
        anchors.centerIn: parent
        width: 400
        
        property bool editMode: false
        property int editIndex: -1
        
        ColumnLayout {
            anchors.fill: parent
            spacing: Theme.spacingNormal
            
            // Start time
            RowLayout {
                Layout.fillWidth: true
                spacing: Theme.spacingNormal
                
                Label {
                    text: "Start Time:"
                    font.pixelSize: Theme.fontSizeNormal
                    color: Theme.textColor
                    Layout.preferredWidth: 100
                }
                
                TextField {
                    id: startTimeField
                    Layout.fillWidth: true
                    placeholderText: "mm:ss"
                    font.pixelSize: Theme.fontSizeNormal
                    
                    background: Rectangle {
                        color: Theme.backgroundColor
                        border.color: Theme.borderColor
                        border.width: 1
                        radius: Theme.radiusSmall
                    }
                    color: Theme.textColor
                }
                
                StyledButton {
                    text: "Current"
                    onClicked: {
                        var pos = audioEngine.getPosition()
                        startTimeField.text = formatTime(pos)
                    }
                }
            }
            
            // End time
            RowLayout {
                Layout.fillWidth: true
                spacing: Theme.spacingNormal
                
                Label {
                    text: "End Time:"
                    font.pixelSize: Theme.fontSizeNormal
                    color: Theme.textColor
                    Layout.preferredWidth: 100
                }
                
                TextField {
                    id: endTimeField
                    Layout.fillWidth: true
                    placeholderText: "mm:ss"
                    font.pixelSize: Theme.fontSizeNormal
                    
                    background: Rectangle {
                        color: Theme.backgroundColor
                        border.color: Theme.borderColor
                        border.width: 1
                        radius: Theme.radiusSmall
                    }
                    color: Theme.textColor
                }
                
                StyledButton {
                    text: "Current"
                    onClicked: {
                        var pos = audioEngine.getPosition()
                        endTimeField.text = formatTime(pos)
                    }
                }
            }
            
            // Label (with common labels dropdown)
            RowLayout {
                Layout.fillWidth: true
                spacing: Theme.spacingNormal
                
                Label {
                    text: "Label:"
                    font.pixelSize: Theme.fontSizeNormal
                    color: Theme.textColor
                    Layout.preferredWidth: 100
                }
                
                ComboBox {
                    id: labelCombo
                    Layout.fillWidth: true
                    editable: true
                    model: sectionManager.getCommonLabels()
                    
                    background: Rectangle {
                        color: Theme.backgroundColor
                        border.color: Theme.borderColor
                        border.width: 1
                        radius: Theme.radiusSmall
                    }
                    
                    contentItem: TextField {
                        text: labelCombo.editText
                        font.pixelSize: Theme.fontSizeNormal
                        color: Theme.textColor
                        background: Rectangle {
                            color: "transparent"
                        }
                    }
                }
            }
            
            // Notes
            RowLayout {
                Layout.fillWidth: true
                spacing: Theme.spacingNormal
                
                Label {
                    text: "Notes:"
                    font.pixelSize: Theme.fontSizeNormal
                    color: Theme.textColor
                    Layout.preferredWidth: 100
                    Layout.alignment: Qt.AlignTop
                }
                
                TextArea {
                    id: notesField
                    Layout.fillWidth: true
                    Layout.preferredHeight: 80
                    placeholderText: "Optional notes..."
                    font.pixelSize: Theme.fontSizeNormal
                    wrapMode: TextEdit.Wrap
                    
                    background: Rectangle {
                        color: Theme.backgroundColor
                        border.color: Theme.borderColor
                        border.width: 1
                        radius: Theme.radiusSmall
                    }
                    color: Theme.textColor
                }
            }
            
            // Buttons
            RowLayout {
                Layout.fillWidth: true
                spacing: Theme.spacingNormal
                
                Item { Layout.fillWidth: true }
                
                StyledButton {
                    text: "Cancel"
                    onClicked: sectionDialog.close()
                }
                
                StyledButton {
                    text: sectionDialog.editMode ? "Update" : "Add"
                    primary: true
                    onClicked: {
                        var startMs = parseTimeToMs(startTimeField.text)
                        var endMs = parseTimeToMs(endTimeField.text)
                        var label = labelCombo.editText.trim()
                        var notes = notesField.text.trim()
                        
                        if (sectionDialog.editMode) {
                            sectionManager.updateSection(sectionDialog.editIndex, startMs, endMs, label, notes)
                        } else {
                            sectionManager.addSection(startMs, endMs, label, notes)
                        }
                        
                        sectionDialog.close()
                    }
                }
            }
        }
        
        onOpened: {
            if (!editMode) {
                startTimeField.text = ""
                endTimeField.text = ""
                labelCombo.editText = ""
                notesField.text = ""
            }
        }
    }
    
    // Main layout
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacingMedium
        spacing: Theme.spacingMedium
        
        // Toolbar
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacingNormal
            
            StyledLabel {
                text: "Sections (" + sectionManager.getSectionCount() + ")"
                heading: true
            }
            
            Item { Layout.fillWidth: true }
            
            StyledButton {
                text: "Auto-Detect"
                info: true
                enabled: audioEngine.getCurrentFile() !== ""
                onClicked: {
                    sectionManager.autoDetectSections()
                }
                
                ToolTip.visible: hovered
                ToolTip.text: "Auto-detect sections using fingerprint matching"
            }
            
            StyledButton {
                text: "➕ Add Section"
                primary: true
                enabled: audioEngine.getCurrentFile() !== ""
                
                onClicked: {
                    sectionDialog.editMode = false
                    sectionDialog.open()
                }
            }
            
            StyledButton {
                text: "Edit"
                enabled: selectedSectionIndex >= 0
                
                onClicked: {
                    var section = sectionManager.getSectionAt(selectedSectionIndex)
                    if (section) {
                        sectionDialog.editMode = true
                        sectionDialog.editIndex = selectedSectionIndex
                        startTimeField.text = formatTime(section.start_ms)
                        endTimeField.text = formatTime(section.end_ms)
                        labelCombo.editText = section.label
                        notesField.text = section.notes
                        sectionDialog.open()
                    }
                }
            }
            
            StyledButton {
                text: "Delete"
                danger: true
                enabled: selectedSectionIndex >= 0
                
                onClicked: {
                    sectionManager.deleteSection(selectedSectionIndex)
                    selectedSectionIndex = -1
                }
            }
        }
        
        // Sections table
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: Theme.backgroundColor
            border.color: Theme.borderColor
            border.width: 1
            radius: Theme.radiusSmall
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: Theme.spacingSmall
                spacing: 0
                
                // Column headers
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 28
                    color: Theme.backgroundMedium
                    
                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: Theme.spacingNormal
                        anchors.rightMargin: Theme.spacingNormal
                        spacing: Theme.spacingNormal
                        
                        Label {
                            text: "Start"
                            font.pixelSize: Theme.fontSizeSmall
                            font.bold: true
                            color: Theme.textColor
                            Layout.preferredWidth: 80
                        }
                        
                        Label {
                            text: "End"
                            font.pixelSize: Theme.fontSizeSmall
                            font.bold: true
                            color: Theme.textColor
                            Layout.preferredWidth: 80
                        }
                        
                        Label {
                            text: "Label"
                            font.pixelSize: Theme.fontSizeSmall
                            font.bold: true
                            color: Theme.textColor
                            Layout.preferredWidth: 120
                        }
                        
                        Label {
                            text: "Notes"
                            font.pixelSize: Theme.fontSizeSmall
                            font.bold: true
                            color: Theme.textColor
                            Layout.fillWidth: true
                        }
                    }
                }
                
                // Sections list
                ListView {
                    id: sectionsListView
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    
                    model: ListModel {
                        id: sectionsModel
                    }
                    
                    delegate: Rectangle {
                        width: sectionsListView.width
                        height: 32
                        color: index % 2 === 0 ? Theme.backgroundColor : Theme.backgroundMedium
                        
                        // Hover effect
                        Rectangle {
                            anchors.fill: parent
                            color: Theme.accentPrimary
                            opacity: mouseArea.containsMouse ? 0.1 : 0
                            
                            Behavior on opacity {
                                NumberAnimation { duration: Theme.animationFast }
                            }
                        }
                        
                        // Selection highlight
                        Rectangle {
                            anchors.fill: parent
                            color: Theme.selectionPrimary
                            opacity: selectedSectionIndex === index ? 0.3 : 0
                        }
                        
                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: Theme.spacingNormal
                            anchors.rightMargin: Theme.spacingNormal
                            spacing: Theme.spacingNormal
                            
                            Label {
                                text: formatTime(model.start_ms)
                                font.pixelSize: Theme.fontSizeSmall
                                color: Theme.textColor
                                Layout.preferredWidth: 80
                            }
                            
                            Label {
                                text: formatTime(model.end_ms)
                                font.pixelSize: Theme.fontSizeSmall
                                color: Theme.textColor
                                Layout.preferredWidth: 80
                            }
                            
                            Label {
                                text: model.label
                                font.pixelSize: Theme.fontSizeNormal
                                font.bold: true
                                color: Theme.textColor
                                Layout.preferredWidth: 120
                            }
                            
                            Label {
                                text: model.notes
                                font.pixelSize: Theme.fontSizeSmall
                                color: Theme.textSecondary
                                Layout.fillWidth: true
                                elide: Text.ElideRight
                            }
                        }
                        
                        MouseArea {
                            id: mouseArea
                            anchors.fill: parent
                            hoverEnabled: true
                            
                            onClicked: {
                                selectedSectionIndex = index
                            }
                            
                            onDoubleClicked: {
                                // Jump to section start
                                audioEngine.setPosition(model.start_ms)
                                if (audioEngine.getPlaybackState() !== "playing") {
                                    audioEngine.play()
                                }
                            }
                        }
                    }
                    
                    ScrollBar.vertical: ScrollBar {
                        policy: ScrollBar.AsNeeded
                    }
                }
            }
        }
        
        // Status message
        Label {
            text: audioEngine.getCurrentFile() !== "" ? 
                  "Current file: " + fileManager.getFileName(audioEngine.getCurrentFile()) :
                  "No file selected - select a file to manage sections"
            font.pixelSize: Theme.fontSizeSmall
            color: Theme.textMuted
            Layout.fillWidth: true
        }
    }
    
    // Helper functions
    function formatTime(ms) {
        var totalSeconds = Math.floor(ms / 1000)
        var minutes = Math.floor(totalSeconds / 60)
        var seconds = totalSeconds % 60
        return minutes + ":" + (seconds < 10 ? "0" : "") + seconds
    }
    
    function parseTimeToMs(timeStr) {
        var parts = timeStr.split(":")
        if (parts.length !== 2) return 0
        
        var minutes = parseInt(parts[0]) || 0
        var seconds = parseInt(parts[1]) || 0
        return (minutes * 60 + seconds) * 1000
    }
    
    function refreshSections() {
        var sections = sectionManager.getSections()
        sectionsModel.clear()
        
        for (var i = 0; i < sections.length; i++) {
            sectionsModel.append(sections[i])
        }
    }
    
    // Connections
    Connections {
        target: sectionManager
        
        function onSectionsChanged() {
            refreshSections()
        }
        
        function onCurrentFileChanged() {
            refreshSections()
            selectedSectionIndex = -1
        }
    }
    
    Connections {
        target: audioEngine
        
        function onCurrentFileChanged(filePath) {
            if (filePath) {
                sectionManager.setCurrentFile(filePath)
                refreshSections()
            }
        }
    }
    
    // Initialize
    Component.onCompleted: {
        if (audioEngine.getCurrentFile() !== "") {
            sectionManager.setCurrentFile(audioEngine.getCurrentFile())
            refreshSections()
        }
    }
}
