import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "../components"
import "../dialogs"
import "../styles"

/**
 * FingerprintsTab Component
 * 
 * Main tab for audio fingerprinting and song identification.
 * 
 * Features:
 * - Generate fingerprints for audio files
 * - Match songs across folders
 * - Detect duplicates
 * - Configure fingerprinting algorithm and threshold
 * - View fingerprint coverage information
 */
Item {
    id: fingerprintsTab
    
    // ========== Properties ==========
    
    property var fingerprintEngine: null
    property var fileManager: null
    property var fileListModel: null
    
    // State properties
    property string currentAlgorithm: "spectral"
    property real currentThreshold: 0.7
    property bool isGenerating: false
    property string statusMessage: ""
    
    // ========== Main Layout ==========
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacingMedium
        spacing: Theme.spacingMedium
        
        // ========== Header ==========
        
        StyledLabel {
            text: "Audio Fingerprinting"
            heading: true
        }
        
        // ========== Configuration Section ==========
        
        GroupBox {
            Layout.fillWidth: true
            title: "Configuration"
            
            ColumnLayout {
                anchors.fill: parent
                spacing: Theme.spacingNormal
                
                // Algorithm selection
                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spacingNormal
                    
                    Label {
                        text: "Algorithm:"
                        Layout.preferredWidth: 100
                    }
                    
                    ComboBox {
                        id: algorithmCombo
                        Layout.fillWidth: true
                        model: ListModel {
                            ListElement { text: "Spectral Analysis"; value: "spectral" }
                            ListElement { text: "Lightweight STFT"; value: "lightweight" }
                            ListElement { text: "ChromaPrint-style"; value: "chromaprint" }
                            ListElement { text: "AudFprint-style"; value: "audfprint" }
                        }
                        textRole: "text"
                        
                        Component.onCompleted: {
                            currentIndex = 0
                            if (fingerprintEngine) {
                                fingerprintEngine.setAlgorithm("spectral")
                            }
                        }
                        
                        onActivated: {
                            var alg = model.get(currentIndex).value
                            currentAlgorithm = alg
                            if (fingerprintEngine) {
                                fingerprintEngine.setAlgorithm(alg)
                            }
                        }
                    }
                }
                
                // Threshold slider
                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spacingNormal
                    
                    Label {
                        text: "Match Threshold:"
                        Layout.preferredWidth: 100
                    }
                    
                    Slider {
                        id: thresholdSlider
                        Layout.fillWidth: true
                        from: 0.5
                        to: 0.95
                        value: 0.7
                        stepSize: 0.05
                        
                        onValueChanged: {
                            currentThreshold = value
                            if (fingerprintEngine) {
                                fingerprintEngine.setThreshold(value)
                            }
                        }
                    }
                    
                    Label {
                        text: (thresholdSlider.value * 100).toFixed(0) + "%"
                        Layout.preferredWidth: 50
                    }
                }
            }
        }
        
        // ========== Actions Section ==========
        
        GroupBox {
            Layout.fillWidth: true
            title: "Actions"
            
            ColumnLayout {
                anchors.fill: parent
                spacing: Theme.spacingNormal
                
                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spacingNormal
                    
                    StyledButton {
                        text: "Generate Fingerprints"
                        enabled: !isGenerating && fileManager && fileManager.getCurrentDirectory() !== ""
                        
                        onClicked: {
                            if (fileListModel && fingerprintEngine) {
                                // Get all files from model
                                var files = []
                                for (var i = 0; i < fileListModel.rowCount(); i++) {
                                    var filepath = fileListModel.getFilePath(i)
                                    if (filepath) {
                                        files.push(filepath)
                                    }
                                }
                                
                                if (files.length > 0) {
                                    fingerprintEngine.generateFingerprints(files)
                                } else {
                                    statusMessage = "No files to process"
                                }
                            }
                        }
                    }
                    
                    StyledButton {
                        text: "Cancel"
                        enabled: isGenerating
                        
                        onClicked: {
                            if (fingerprintEngine) {
                                fingerprintEngine.cancelGeneration()
                            }
                        }
                    }
                    
                    StyledButton {
                        text: "Show Info"
                        enabled: fileManager && fileManager.getCurrentDirectory() !== ""
                        
                        onClicked: {
                            if (fingerprintEngine && fileManager) {
                                var info = fingerprintEngine.getFingerprintInfo(fileManager.getCurrentDirectory())
                                var data = JSON.parse(info)
                                
                                if (data.error) {
                                    statusMessage = "Error: " + data.error
                                } else {
                                    var msg = "Total files: " + data.total_files + "\n"
                                    msg += "Algorithm coverage:\n"
                                    for (var alg in data.algorithm_coverage) {
                                        msg += "  " + alg + ": " + data.algorithm_coverage[alg] + "\n"
                                    }
                                    msg += "Excluded files: " + data.excluded_files.length
                                    statusMessage = msg
                                }
                            }
                        }
                    }
                    
                    Item {
                        Layout.fillWidth: true
                    }
                }
            }
        }
        
        // ========== Status Section ==========
        
        GroupBox {
            Layout.fillWidth: true
            Layout.preferredHeight: 150
            title: "Status"
            
            ScrollView {
                anchors.fill: parent
                clip: true
                
                TextArea {
                    id: statusText
                    text: statusMessage
                    readOnly: true
                    wrapMode: TextArea.Wrap
                    selectByMouse: true
                }
            }
        }
        
        // ========== Progress Bar ==========
        
        ProgressBar {
            id: progressBar
            Layout.fillWidth: true
            visible: isGenerating
            from: 0
            to: 100
            value: 0
        }
        
        // Spacer
        Item {
            Layout.fillHeight: true
        }
    }
    
    // ========== Progress Dialog ==========
    
    FingerprintProgressDialog {
        id: progressDialog
        
        onCancelRequested: {
            if (fingerprintEngine) {
                fingerprintEngine.cancelGeneration()
            }
        }
    }
    
    // ========== Connections ==========
    
    Connections {
        target: fingerprintEngine
        
        function onFingerprintGenerationStarted() {
            isGenerating = true
            statusMessage = "Generating fingerprints..."
            progressBar.value = 0
            
            // Show progress dialog
            if (fileListModel) {
                progressDialog.startProgress(fileListModel.rowCount())
            }
        }
        
        function onFingerprintGenerationProgress(current, total, status) {
            progressBar.value = (current / total) * 100
            statusMessage = "Progress: " + current + "/" + total + " - " + status
            
            // Update progress dialog
            progressDialog.updateProgress(current, total, status)
        }
        
        function onFingerprintGenerationFinished(success, message) {
            isGenerating = false
            progressBar.value = 100
            
            if (success) {
                statusMessage = "✓ " + message
            } else {
                statusMessage = "✗ " + message
            }
            
            // Close progress dialog
            progressDialog.finishProgress(success, message)
        }
    }
}
