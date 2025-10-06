import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"
import "../styles"

/**
 * AnnotationDialog
 * 
 * Dialog for creating and editing annotations.
 * Allows user to set timestamp, text, category, importance, and color.
 */
Dialog {
    id: root
    
    title: editMode ? "Edit Annotation" : "Add Annotation"
    modal: true
    standardButtons: Dialog.Ok | Dialog.Cancel
    
    width: 500
    height: 400
    
    // Properties
    property bool editMode: false
    property int annotationIndex: -1
    property int timestampMs: 0
    property string annotationText: ""
    property string annotationCategory: ""
    property bool annotationImportant: false
    property string annotationColor: "#3498db"
    
    // Signals
    signal annotationAccepted(int timestampMs, string text, string category, 
                            bool important, string color)
    signal annotationUpdated(int index, int timestampMs, string text, 
                            string category, bool important, string color)
    
    // Reset to defaults
    function resetDialog() {
        editMode = false
        annotationIndex = -1
        timestampMs = 0
        annotationText = ""
        annotationCategory = ""
        annotationImportant = false
        annotationColor = "#3498db"
        
        updateFields()
    }
    
    // Load annotation for editing
    function loadAnnotation(index, timestamp, text, category, important, color) {
        editMode = true
        annotationIndex = index
        timestampMs = timestamp
        annotationText = text
        annotationCategory = category
        annotationImportant = important
        annotationColor = color || "#3498db"
        
        updateFields()
    }
    
    // Update UI fields from properties
    function updateFields() {
        timestampField.text = formatTime(timestampMs)
        textField.text = annotationText
        categoryCombo.currentIndex = categoryCombo.find(annotationCategory)
        importantCheck.checked = annotationImportant
        colorCombo.currentIndex = getColorIndex(annotationColor)
    }
    
    // Format timestamp as MM:SS.mmm
    function formatTime(ms) {
        var totalSeconds = ms / 1000.0
        var minutes = Math.floor(totalSeconds / 60)
        var seconds = Math.floor(totalSeconds % 60)
        var milliseconds = Math.floor((totalSeconds % 1) * 1000)
        
        return String(minutes).padStart(2, '0') + ":" + 
               String(seconds).padStart(2, '0') + "." +
               String(milliseconds).padStart(3, '0')
    }
    
    // Parse time string to milliseconds
    function parseTime(timeStr) {
        var parts = timeStr.split(":")
        if (parts.length !== 2) return 0
        
        var minutes = parseInt(parts[0]) || 0
        var secParts = parts[1].split(".")
        var seconds = parseInt(secParts[0]) || 0
        var milliseconds = parseInt(secParts[1]) || 0
        
        return (minutes * 60 + seconds) * 1000 + milliseconds
    }
    
    // Get color index from hex value
    function getColorIndex(hexColor) {
        var colors = ["#3498db", "#e74c3c", "#2ecc71", "#f39c12", 
                     "#9b59b6", "#1abc9c", "#34495e"]
        return Math.max(0, colors.indexOf(hexColor))
    }
    
    // Content
    ColumnLayout {
        anchors.fill: parent
        spacing: Theme.spacingNormal
        
        // Timestamp
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacingNormal
            
            Label {
                text: "Time:"
                font.pixelSize: Theme.fontSizeNormal
                color: Theme.textColor
                Layout.preferredWidth: 80
            }
            
            StyledTextField {
                id: timestampField
                Layout.fillWidth: true
                placeholderText: "MM:SS.mmm"
                
                onTextChanged: {
                    timestampMs = parseTime(text)
                }
            }
            
            StyledButton {
                text: "Current"
                Layout.preferredWidth: 80
                onClicked: {
                    timestampMs = audioEngine.getPosition()
                    timestampField.text = formatTime(timestampMs)
                }
            }
        }
        
        // Category
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacingNormal
            
            Label {
                text: "Category:"
                font.pixelSize: Theme.fontSizeNormal
                color: Theme.textColor
                Layout.preferredWidth: 80
            }
            
            ComboBox {
                id: categoryCombo
                Layout.fillWidth: true
                model: ["", "timing", "energy", "harmony", "dynamics", "notes"]
                
                background: Rectangle {
                    color: Theme.backgroundLight
                    border.color: Theme.borderColor
                    border.width: 1
                    radius: Theme.radiusSmall
                }
                
                contentItem: Text {
                    text: categoryCombo.displayText
                    color: Theme.textColor
                    font.pixelSize: Theme.fontSizeNormal
                    verticalAlignment: Text.AlignVCenter
                    leftPadding: 10
                }
                
                onCurrentTextChanged: {
                    annotationCategory = currentText
                }
            }
        }
        
        // Text
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacingNormal
            
            Label {
                text: "Text:"
                font.pixelSize: Theme.fontSizeNormal
                color: Theme.textColor
                Layout.preferredWidth: 80
                Layout.alignment: Qt.AlignTop
                Layout.topMargin: 8
            }
            
            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.minimumHeight: 100
                
                TextArea {
                    id: textField
                    wrapMode: TextArea.Wrap
                    placeholderText: "Enter annotation text..."
                    
                    background: Rectangle {
                        color: Theme.backgroundLight
                        border.color: Theme.borderColor
                        border.width: 1
                        radius: Theme.radiusSmall
                    }
                    
                    color: Theme.textColor
                    font.pixelSize: Theme.fontSizeNormal
                    
                    onTextChanged: {
                        annotationText = text
                    }
                }
            }
        }
        
        // Color
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacingNormal
            
            Label {
                text: "Color:"
                font.pixelSize: Theme.fontSizeNormal
                color: Theme.textColor
                Layout.preferredWidth: 80
            }
            
            ComboBox {
                id: colorCombo
                Layout.fillWidth: true
                model: [
                    {name: "Blue", value: "#3498db"},
                    {name: "Red", value: "#e74c3c"},
                    {name: "Green", value: "#2ecc71"},
                    {name: "Orange", value: "#f39c12"},
                    {name: "Purple", value: "#9b59b6"},
                    {name: "Teal", value: "#1abc9c"},
                    {name: "Gray", value: "#34495e"}
                ]
                textRole: "name"
                
                background: Rectangle {
                    color: Theme.backgroundLight
                    border.color: Theme.borderColor
                    border.width: 1
                    radius: Theme.radiusSmall
                }
                
                contentItem: RowLayout {
                    spacing: 8
                    
                    Rectangle {
                        width: 20
                        height: 20
                        color: colorCombo.model[colorCombo.currentIndex].value
                        radius: 3
                    }
                    
                    Text {
                        text: colorCombo.displayText
                        color: Theme.textColor
                        font.pixelSize: Theme.fontSizeNormal
                        verticalAlignment: Text.AlignVCenter
                    }
                }
                
                delegate: ItemDelegate {
                    width: colorCombo.width
                    
                    contentItem: RowLayout {
                        spacing: 8
                        
                        Rectangle {
                            width: 20
                            height: 20
                            color: modelData.value
                            radius: 3
                        }
                        
                        Text {
                            text: modelData.name
                            color: Theme.textColor
                            font.pixelSize: Theme.fontSizeNormal
                        }
                    }
                    
                    background: Rectangle {
                        color: highlighted ? Theme.backgroundLight : "transparent"
                    }
                }
                
                onCurrentIndexChanged: {
                    if (currentIndex >= 0 && currentIndex < model.length) {
                        annotationColor = model[currentIndex].value
                    }
                }
            }
        }
        
        // Important flag
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacingNormal
            
            Label {
                text: "Important:"
                font.pixelSize: Theme.fontSizeNormal
                color: Theme.textColor
                Layout.preferredWidth: 80
            }
            
            CheckBox {
                id: importantCheck
                text: "Mark as important"
                
                indicator: Rectangle {
                    implicitWidth: 20
                    implicitHeight: 20
                    x: importantCheck.leftPadding
                    y: parent.height / 2 - height / 2
                    radius: 3
                    border.color: Theme.borderColor
                    border.width: 1
                    color: importantCheck.checked ? Theme.accentPrimary : Theme.backgroundLight
                    
                    Label {
                        visible: importantCheck.checked
                        anchors.centerIn: parent
                        text: "✓"
                        color: "white"
                        font.pixelSize: 14
                    }
                }
                
                contentItem: Text {
                    text: importantCheck.text
                    font.pixelSize: Theme.fontSizeNormal
                    color: Theme.textColor
                    leftPadding: importantCheck.indicator.width + 8
                    verticalAlignment: Text.AlignVCenter
                }
                
                onCheckedChanged: {
                    annotationImportant = checked
                }
            }
        }
    }
    
    // Handle button clicks
    onAccepted: {
        if (editMode) {
            annotationUpdated(annotationIndex, timestampMs, annotationText,
                            annotationCategory, annotationImportant, annotationColor)
        } else {
            annotationAccepted(timestampMs, annotationText, annotationCategory,
                             annotationImportant, annotationColor)
        }
    }
}
