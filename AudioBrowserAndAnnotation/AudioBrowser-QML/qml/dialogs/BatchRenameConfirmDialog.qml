import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "../components"
import "../styles"

/**
 * BatchRenameConfirmDialog Component
 * 
 * Confirmation dialog showing preview of batch rename operations.
 * 
 * Features:
 * - Shows preview of up to 25 renames
 * - Displays count of additional files
 * - Yes/No confirmation buttons
 * - Scrollable preview list
 */
Dialog {
    id: root
    
    // ========== Properties ==========
    
    property var renamePreview: []  // List of {oldName, newName} objects
    
    // ========== Signals ==========
    
    signal confirmed()
    signal cancelled()
    
    // ========== Dialog Configuration ==========
    
    title: "Confirm Batch Rename"
    modal: true
    width: 650
    height: 500
    
    anchors.centerIn: parent
    
    standardButtons: Dialog.Yes | Dialog.No
    
    // ========== Helper Functions ==========
    
    function openDialog(preview) {
        renamePreview = preview
        updatePreviewList()
        open()
    }
    
    function updatePreviewList() {
        previewModel.clear()
        
        var maxDisplay = 25
        var displayCount = Math.min(renamePreview.length, maxDisplay)
        
        for (var i = 0; i < displayCount; i++) {
            var item = renamePreview[i]
            previewModel.append({
                oldName: item.oldName,
                newName: item.newName
            })
        }
    }
    
    // ========== Dialog Actions ==========
    
    onAccepted: {
        confirmed()
    }
    
    onRejected: {
        cancelled()
    }
    
    // ========== Content ==========
    
    contentItem: ColumnLayout {
        spacing: 15
        
        // Header label
        Label {
            text: renamePreview.length === 1 
                ? "Rename 1 file as follows?"
                : "Rename " + renamePreview.length + " files as follows?"
            font.pixelSize: 14
            font.bold: true
            Layout.fillWidth: true
        }
        
        // Preview list
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "transparent"
            border.color: Theme.borderColor
            border.width: 1
            radius: 4
            
            ScrollView {
                anchors.fill: parent
                anchors.margins: 1
                clip: true
                
                ListView {
                    id: previewListView
                    model: previewModel
                    spacing: 2
                    
                    delegate: Rectangle {
                        width: previewListView.width
                        height: 35
                        color: index % 2 === 0 ? Theme.backgroundColor : Theme.alternateBackgroundColor
                        
                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 5
                            spacing: 10
                            
                            Label {
                                text: model.oldName
                                font.pixelSize: 12
                                Layout.fillWidth: true
                                elide: Text.ElideMiddle
                            }
                            
                            Label {
                                text: "→"
                                font.pixelSize: 14
                                font.bold: true
                                color: Theme.accentColor
                            }
                            
                            Label {
                                text: model.newName
                                font.pixelSize: 12
                                font.bold: true
                                Layout.fillWidth: true
                                elide: Text.ElideMiddle
                            }
                        }
                    }
                }
            }
        }
        
        // "And X more" label if needed
        Label {
            visible: renamePreview.length > 25
            text: "… and " + (renamePreview.length - 25) + " more"
            font.pixelSize: 12
            font.italic: true
            color: Theme.secondaryTextColor
            Layout.fillWidth: true
            horizontalAlignment: Text.AlignCenter
        }
        
        // Info label
        Label {
            text: "Files will be renamed in place. This operation cannot be undone."
            font.pixelSize: 11
            color: Theme.warningColor
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }
    }
    
    // ========== Data Model ==========
    
    ListModel {
        id: previewModel
    }
}
