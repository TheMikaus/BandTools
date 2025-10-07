import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "../components"
import "../styles"

/**
 * ProgressDialog Component
 * 
 * Modal dialog for showing progress of long-running operations.
 * 
 * Features:
 * - Progress bar
 * - Status text
 * - Current file indicator
 * - Cancel button
 * - Results summary
 */
Dialog {
    id: root
    
    // ========== Properties ==========
    
    property string operationName: "Processing"
    property int currentProgress: 0
    property int totalProgress: 100
    property string currentFile: ""
    property bool canCancel: true
    property bool showResults: false
    property string resultsMessage: ""
    
    // References
    property var batchOperations: null
    
    // ========== Signals ==========
    
    signal cancelRequested()
    
    // ========== Dialog Configuration ==========
    
    title: operationName
    modal: true
    closePolicy: canCancel ? Dialog.CloseOnEscape : Dialog.NoAutoClose
    width: 500
    height: 250
    
    anchors.centerIn: parent
    
    standardButtons: {
        if (showResults)
            return Dialog.Close
        if (canCancel)
            return Dialog.Cancel
        return Dialog.NoButton
    }
    
    // ========== Helper Functions ==========
    
    function openDialog(operation) {
        operationName = operation
        currentProgress = 0
        totalProgress = 100
        currentFile = ""
        showResults = false
        resultsMessage = ""
        canCancel = true
        
        open()
    }
    
    function updateProgress(done, total, filename) {
        currentProgress = done
        totalProgress = total
        currentFile = filename
    }
    
    function showResult(success, message) {
        showResults = true
        resultsMessage = message
        canCancel = false
    }
    
    // ========== Dialog Actions ==========
    
    onRejected: {
        // Cancel button clicked
        if (canCancel) {
            cancelRequested()
            if (batchOperations) {
                batchOperations.cancelCurrentOperation()
            }
        }
    }
    
    // ========== Content ==========
    
    contentItem: ColumnLayout {
        spacing: Theme.spacingLarge
        
        // Status message
        Label {
            text: showResults ? resultsMessage : (operationName + "...")
            font.pixelSize: Theme.fontSizeMedium
            font.bold: true
            Layout.fillWidth: true
            horizontalAlignment: Text.AlignHCenter
        }
        
        // Progress section (visible when not showing results)
        ColumnLayout {
            visible: !showResults
            spacing: Theme.spacingMedium
            Layout.fillWidth: true
            
            // Current file
            Label {
                text: currentFile ? ("Processing: " + currentFile) : "Preparing..."
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.textSecondary
                Layout.fillWidth: true
                elide: Text.ElideMiddle
                horizontalAlignment: Text.AlignHCenter
            }
            
            // Progress bar
            ProgressBar {
                id: progressBar
                from: 0
                to: totalProgress
                value: currentProgress
                Layout.fillWidth: true
                Layout.preferredHeight: 25
                
                background: Rectangle {
                    implicitWidth: 200
                    implicitHeight: 25
                    color: Theme.backgroundLight
                    radius: Theme.radiusSmall
                    border.color: Theme.borderColor
                }
                
                contentItem: Item {
                    implicitWidth: 200
                    implicitHeight: 23
                    
                    Rectangle {
                        width: progressBar.visualPosition * parent.width
                        height: parent.height
                        radius: Theme.radiusSmall
                        color: Theme.primary
                    }
                    
                    // Progress text overlay
                    Label {
                        anchors.centerIn: parent
                        text: {
                            if (totalProgress > 0) {
                                var percent = Math.round((currentProgress / totalProgress) * 100)
                                return currentProgress + " / " + totalProgress + " (" + percent + "%)"
                            }
                            return "Starting..."
                        }
                        color: progressBar.visualPosition > 0.5 ? Theme.backgroundWhite : Theme.textPrimary
                        font.pixelSize: Theme.fontSizeSmall
                        font.bold: true
                    }
                }
            }
            
            // Status label
            Label {
                text: canCancel ? "Click Cancel to stop" : "Please wait..."
                font.pixelSize: Theme.fontSizeSmall
                font.italic: true
                color: Theme.textSecondary
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
            }
        }
        
        // Results section (visible when showing results)
        Rectangle {
            visible: showResults
            Layout.fillWidth: true
            Layout.preferredHeight: 80
            color: Theme.backgroundLight
            radius: Theme.radiusSmall
            border.color: Theme.borderColor
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: Theme.spacingMedium
                spacing: Theme.spacingMedium
                
                Label {
                    text: resultsMessage.indexOf("error") >= 0 || resultsMessage.indexOf("failed") >= 0 ? "⚠" : "✓"
                    font.pixelSize: 32
                    color: resultsMessage.indexOf("error") >= 0 || resultsMessage.indexOf("failed") >= 0 ? Theme.danger : Theme.success
                }
                
                Label {
                    text: resultsMessage
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }
            }
        }
        
        // Spacer
        Item {
            Layout.fillHeight: true
        }
    }
}
