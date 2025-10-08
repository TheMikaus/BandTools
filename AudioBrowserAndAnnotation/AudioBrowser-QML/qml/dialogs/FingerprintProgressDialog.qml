import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "../components"
import "../styles"

/**
 * FingerprintProgressDialog Component
 * 
 * Progress dialog for audio fingerprint generation.
 * 
 * Features:
 * - Progress bar showing completion
 * - Current file being processed
 * - Cancel button
 * - Auto-close on completion
 */
Dialog {
    id: root
    
    // ========== Properties ==========
    
    property int currentFile: 0
    property int totalFiles: 0
    property string currentFilename: ""
    property bool isProcessing: false
    
    // ========== Signals ==========
    
    signal cancelRequested()
    
    // ========== Dialog Configuration ==========
    
    title: "Generating Fingerprints"
    modal: true
    width: 550
    height: 200
    
    anchors.centerIn: parent
    
    closePolicy: Popup.NoAutoClose
    
    standardButtons: Dialog.Cancel
    
    // ========== Helper Functions ==========
    
    function startProgress(total) {
        totalFiles = total
        currentFile = 0
        currentFilename = "Preparing..."
        isProcessing = true
        progressBar.value = 0
        open()
    }
    
    function updateProgress(current, total, filename) {
        currentFile = current
        totalFiles = total
        currentFilename = filename
        
        if (total > 0) {
            progressBar.value = current / total
        }
    }
    
    function finishProgress(success, message) {
        isProcessing = false
        
        if (success) {
            // Show completion briefly then close
            currentFilename = message || "Completed"
            progressBar.value = 1.0
            
            // Auto-close after 1 second
            closeTimer.start()
        } else {
            // Show error and allow user to close
            currentFilename = message || "Error occurred"
            progressBar.value = 0
        }
    }
    
    // ========== Dialog Actions ==========
    
    onRejected: {
        if (isProcessing) {
            cancelRequested()
        }
        close()
    }
    
    // ========== Content ==========
    
    contentItem: ColumnLayout {
        spacing: 15
        
        // Status label
        Label {
            id: statusLabel
            text: currentFile > 0 
                ? "Processing file " + currentFile + " of " + totalFiles + "..."
                : "Preparing fingerprint generation..."
            font.pixelSize: 13
            Layout.fillWidth: true
        }
        
        // Progress bar
        ProgressBar {
            id: progressBar
            from: 0
            to: 1.0
            value: 0
            Layout.fillWidth: true
            Layout.preferredHeight: 25
            
            background: Rectangle {
                implicitWidth: 200
                implicitHeight: 25
                color: Theme.inputBackgroundColor
                border.color: Theme.borderColor
                border.width: 1
                radius: 4
            }
            
            contentItem: Item {
                implicitWidth: 200
                implicitHeight: 24
                
                Rectangle {
                    width: progressBar.visualPosition * parent.width
                    height: parent.height
                    radius: 4
                    color: Theme.accentColor
                }
            }
        }
        
        // Current file label
        Label {
            id: filenameLabel
            text: currentFilename
            font.pixelSize: 12
            color: Theme.secondaryTextColor
            elide: Text.ElideMiddle
            Layout.fillWidth: true
            Layout.maximumWidth: parent.width
        }
        
        // Spacer
        Item {
            Layout.fillHeight: true
        }
    }
    
    // ========== Auto-close Timer ==========
    
    Timer {
        id: closeTimer
        interval: 1000
        running: false
        repeat: false
        onTriggered: {
            root.close()
        }
    }
}
