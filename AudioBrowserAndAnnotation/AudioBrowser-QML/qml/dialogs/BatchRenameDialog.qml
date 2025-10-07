import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "../components"
import "../styles"

/**
 * BatchRenameDialog Component
 * 
 * Modal dialog for batch renaming audio files.
 * 
 * Features:
 * - Pattern input for naming
 * - Preview of rename operations
 * - List of files to be renamed
 * - Success/error status
 */
Dialog {
    id: root
    
    // ========== Properties ==========
    
    property var fileList: []  // List of file paths to rename
    property string namePattern: ""  // Optional name pattern
    
    // References
    property var batchOperations: null
    property var fileManager: null
    
    // ========== Signals ==========
    
    signal renameCompleted()
    
    // ========== Dialog Configuration ==========
    
    title: "Batch Rename Files"
    modal: true
    width: 700
    height: 600
    
    anchors.centerIn: parent
    
    standardButtons: Dialog.Ok | Dialog.Cancel
    
    // ========== Helper Functions ==========
    
    function openDialog(files) {
        fileList = files
        namePattern = ""
        patternField.text = ""
        
        if (fileList.length === 0) {
            errorLabel.text = "No files selected for rename"
            return
        }
        
        // Update preview
        updatePreview()
        
        errorLabel.text = ""
        open()
    }
    
    function updatePreview() {
        if (!batchOperations) return
        
        previewModel.clear()
        
        var preview = batchOperations.previewBatchRename(fileList, patternField.text)
        
        for (var i = 0; i < preview.length; i++) {
            var item = preview[i]
            previewModel.append({
                oldName: item.oldName,
                newName: item.newName,
                status: item.status
            })
        }
    }
    
    function executeRename() {
        if (!batchOperations || fileList.length === 0) return
        
        // Close dialog
        close()
        
        // Execute batch rename
        batchOperations.executeBatchRename(fileList, patternField.text)
        
        // Emit signal
        renameCompleted()
    }
    
    // ========== Dialog Actions ==========
    
    onAccepted: {
        executeRename()
    }
    
    // ========== Content ==========
    
    contentItem: ColumnLayout {
        spacing: Theme.spacingMedium
        
        // Instructions
        Label {
            text: "Rename " + fileList.length + " file(s) with pattern:"
            font.bold: true
            Layout.fillWidth: true
        }
        
        // Pattern input
        GroupBox {
            title: "Rename Pattern"
            Layout.fillWidth: true
            
            background: Rectangle {
                color: Theme.backgroundLight
                border.color: Theme.borderColor
                radius: Theme.radiusSmall
            }
            
            ColumnLayout {
                anchors.fill: parent
                spacing: Theme.spacingSmall
                
                Label {
                    text: "Leave empty to use current filenames, or enter a pattern for all files:"
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.textSecondary
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }
                
                TextField {
                    id: patternField
                    placeholderText: "e.g., 'song_name' (will become 01_song_name, 02_song_name, etc.)"
                    Layout.fillWidth: true
                    
                    background: Rectangle {
                        color: Theme.backgroundWhite
                        border.color: patternField.activeFocus ? Theme.primary : Theme.borderColor
                        radius: Theme.radiusSmall
                    }
                    
                    onTextChanged: {
                        updatePreview()
                    }
                }
                
                Label {
                    text: "Files will be numbered sequentially (01_, 02_, etc.)"
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.textSecondary
                    Layout.fillWidth: true
                }
            }
        }
        
        // Preview section
        GroupBox {
            title: "Preview"
            Layout.fillWidth: true
            Layout.fillHeight: true
            
            background: Rectangle {
                color: Theme.backgroundLight
                border.color: Theme.borderColor
                radius: Theme.radiusSmall
            }
            
            ColumnLayout {
                anchors.fill: parent
                spacing: 0
                
                // Header
                Rectangle {
                    Layout.fillWidth: true
                    height: 30
                    color: Theme.backgroundMedium
                    
                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 5
                        spacing: 10
                        
                        Label {
                            text: "Current Name"
                            font.bold: true
                            Layout.preferredWidth: parent.width * 0.45
                        }
                        
                        Label {
                            text: "→"
                            font.bold: true
                            Layout.preferredWidth: 20
                        }
                        
                        Label {
                            text: "New Name"
                            font.bold: true
                            Layout.fillWidth: true
                        }
                    }
                }
                
                // List view
                ListView {
                    id: previewList
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    
                    ScrollBar.vertical: ScrollBar {
                        policy: ScrollBar.AlwaysOn
                    }
                    
                    model: ListModel {
                        id: previewModel
                    }
                    
                    delegate: Rectangle {
                        width: previewList.width - 20
                        height: 35
                        color: index % 2 === 0 ? Theme.backgroundWhite : Theme.backgroundLight
                        
                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 5
                            spacing: 10
                            
                            Label {
                                text: model.oldName
                                Layout.preferredWidth: parent.width * 0.45
                                elide: Text.ElideMiddle
                                color: Theme.textPrimary
                            }
                            
                            Label {
                                text: "→"
                                Layout.preferredWidth: 20
                                color: Theme.textSecondary
                            }
                            
                            Label {
                                text: model.newName
                                Layout.fillWidth: true
                                elide: Text.ElideMiddle
                                color: model.status === "ok" ? Theme.success : Theme.warning
                                font.bold: model.oldName !== model.newName
                            }
                        }
                    }
                }
            }
        }
        
        // Error label
        Label {
            id: errorLabel
            text: ""
            color: Theme.danger
            visible: text.length > 0
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }
        
        // Help text
        Label {
            text: "Note: Files are numbered based on creation time, oldest first."
            font.pixelSize: Theme.fontSizeSmall
            font.italic: true
            color: Theme.textSecondary
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }
    }
}
