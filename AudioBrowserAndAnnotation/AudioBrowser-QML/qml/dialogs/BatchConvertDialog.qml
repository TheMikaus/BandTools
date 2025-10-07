import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "../components"
import "../styles"

/**
 * BatchConvertDialog Component
 * 
 * Modal dialog for batch audio format conversion.
 * 
 * Features:
 * - WAV to MP3 conversion
 * - Stereo to mono conversion
 * - Volume boost export
 * - Bitrate selection
 * - Option to delete originals
 */
Dialog {
    id: root
    
    // ========== Properties ==========
    
    property var fileList: []  // List of file paths to convert
    property string operationType: "wav_to_mp3"  // "wav_to_mp3", "to_mono", "volume_boost"
    property string currentFilePath: ""  // For single file operations
    
    // References
    property var batchOperations: null
    
    // ========== Signals ==========
    
    signal conversionCompleted()
    
    // ========== Dialog Configuration ==========
    
    title: {
        if (operationType === "wav_to_mp3") return "Convert WAV to MP3"
        if (operationType === "to_mono") return "Convert to Mono"
        if (operationType === "volume_boost") return "Export with Volume Boost"
        return "Batch Convert"
    }
    
    modal: true
    width: 600
    height: operationType === "wav_to_mp3" ? 450 : 400
    
    anchors.centerIn: parent
    
    standardButtons: Dialog.Ok | Dialog.Cancel
    
    // ========== Helper Functions ==========
    
    function openDialog(operation, files, currentFile) {
        operationType = operation
        fileList = files || []
        currentFilePath = currentFile || ""
        
        // Reset fields
        bitrateCombo.currentIndex = 1  // 192k default
        deleteOriginalsCheck.checked = true
        leftChannelCheck.checked = true
        rightChannelCheck.checked = true
        boostSlider.value = 3.0
        
        errorLabel.text = ""
        
        // Check dependencies
        if (!batchOperations) {
            errorLabel.text = "Batch operations not available"
            return
        }
        
        if (!batchOperations.isPydubAvailable()) {
            errorLabel.text = "pydub library not installed. Please install: pip install pydub"
            return
        }
        
        if (!batchOperations.isFfmpegAvailable()) {
            errorLabel.text = "FFmpeg not found. Please install FFmpeg."
            return
        }
        
        // Validate files
        if (operationType === "wav_to_mp3" && fileList.length === 0) {
            errorLabel.text = "No WAV files selected"
            return
        }
        
        if ((operationType === "to_mono" || operationType === "volume_boost") && !currentFilePath) {
            errorLabel.text = "No file selected"
            return
        }
        
        open()
    }
    
    function executeConversion() {
        if (!batchOperations) return
        
        // Close dialog
        close()
        
        // Execute operation
        if (operationType === "wav_to_mp3") {
            var bitrates = ["128k", "192k", "256k", "320k"]
            var bitrate = bitrates[bitrateCombo.currentIndex]
            batchOperations.convertWavToMp3(fileList, bitrate, deleteOriginalsCheck.checked)
        } else if (operationType === "to_mono") {
            batchOperations.convertToMono(currentFilePath, leftChannelCheck.checked, rightChannelCheck.checked)
        } else if (operationType === "volume_boost") {
            batchOperations.exportWithVolumeBoost(currentFilePath, boostSlider.value)
        }
        
        // Emit signal
        conversionCompleted()
    }
    
    // ========== Dialog Actions ==========
    
    onAccepted: {
        executeConversion()
    }
    
    // ========== Content ==========
    
    contentItem: ColumnLayout {
        spacing: Theme.spacingMedium
        
        // WAV to MP3 options
        GroupBox {
            visible: operationType === "wav_to_mp3"
            title: "Conversion Settings"
            Layout.fillWidth: true
            
            background: Rectangle {
                color: Theme.backgroundLight
                border.color: Theme.borderColor
                radius: Theme.radiusSmall
            }
            
            ColumnLayout {
                anchors.fill: parent
                spacing: Theme.spacingMedium
                
                Label {
                    text: "Converting " + fileList.length + " WAV file(s) to MP3"
                    font.bold: true
                }
                
                // Bitrate selection
                RowLayout {
                    spacing: Theme.spacingMedium
                    
                    Label {
                        text: "MP3 Bitrate:"
                        Layout.preferredWidth: 100
                    }
                    
                    ComboBox {
                        id: bitrateCombo
                        model: ["128 kbps", "192 kbps", "256 kbps", "320 kbps"]
                        currentIndex: 1  // 192k default
                        Layout.preferredWidth: 150
                        
                        background: Rectangle {
                            color: Theme.backgroundWhite
                            border.color: bitrateCombo.activeFocus ? Theme.primary : Theme.borderColor
                            radius: Theme.radiusSmall
                        }
                    }
                    
                    Item { Layout.fillWidth: true }
                }
                
                // Delete originals option
                CheckBox {
                    id: deleteOriginalsCheck
                    text: "Delete original WAV files after conversion"
                    checked: true
                    
                    indicator: Rectangle {
                        width: 20
                        height: 20
                        x: deleteOriginalsCheck.leftPadding
                        y: parent.height / 2 - height / 2
                        radius: 3
                        border.color: Theme.borderColor
                        color: Theme.backgroundWhite
                        
                        Rectangle {
                            width: 12
                            height: 12
                            anchors.centerIn: parent
                            radius: 2
                            color: Theme.primary
                            visible: deleteOriginalsCheck.checked
                        }
                    }
                }
                
                Label {
                    text: "⚠ Warning: Original files will be permanently deleted"
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.danger
                    visible: deleteOriginalsCheck.checked
                }
            }
        }
        
        // Mono conversion options
        GroupBox {
            visible: operationType === "to_mono"
            title: "Channel Selection"
            Layout.fillWidth: true
            
            background: Rectangle {
                color: Theme.backgroundLight
                border.color: Theme.borderColor
                radius: Theme.radiusSmall
            }
            
            ColumnLayout {
                anchors.fill: parent
                spacing: Theme.spacingMedium
                
                Label {
                    text: "Converting stereo file to mono"
                    font.bold: true
                }
                
                Label {
                    text: "Select which channels to include:"
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.textSecondary
                }
                
                CheckBox {
                    id: leftChannelCheck
                    text: "Include Left Channel"
                    checked: true
                    
                    indicator: Rectangle {
                        width: 20
                        height: 20
                        x: leftChannelCheck.leftPadding
                        y: parent.height / 2 - height / 2
                        radius: 3
                        border.color: Theme.borderColor
                        color: Theme.backgroundWhite
                        
                        Rectangle {
                            width: 12
                            height: 12
                            anchors.centerIn: parent
                            radius: 2
                            color: Theme.primary
                            visible: leftChannelCheck.checked
                        }
                    }
                }
                
                CheckBox {
                    id: rightChannelCheck
                    text: "Include Right Channel"
                    checked: true
                    
                    indicator: Rectangle {
                        width: 20
                        height: 20
                        x: rightChannelCheck.leftPadding
                        y: parent.height / 2 - height / 2
                        radius: 3
                        border.color: Theme.borderColor
                        color: Theme.backgroundWhite
                        
                        Rectangle {
                            width: 12
                            height: 12
                            anchors.centerIn: parent
                            radius: 2
                            color: Theme.primary
                            visible: rightChannelCheck.checked
                        }
                    }
                }
                
                Label {
                    text: "• Original stereo file will be backed up to .backup folder\n• New mono version will replace the original"
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.textSecondary
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }
            }
        }
        
        // Volume boost options
        GroupBox {
            visible: operationType === "volume_boost"
            title: "Volume Boost Settings"
            Layout.fillWidth: true
            
            background: Rectangle {
                color: Theme.backgroundLight
                border.color: Theme.borderColor
                radius: Theme.radiusSmall
            }
            
            ColumnLayout {
                anchors.fill: parent
                spacing: Theme.spacingMedium
                
                Label {
                    text: "Boost volume and export"
                    font.bold: true
                }
                
                RowLayout {
                    spacing: Theme.spacingMedium
                    
                    Label {
                        text: "Boost:"
                        Layout.preferredWidth: 60
                    }
                    
                    Slider {
                        id: boostSlider
                        from: 0.0
                        to: 10.0
                        value: 3.0
                        stepSize: 0.5
                        Layout.fillWidth: true
                        
                        background: Rectangle {
                            x: boostSlider.leftPadding
                            y: boostSlider.topPadding + boostSlider.availableHeight / 2 - height / 2
                            width: boostSlider.availableWidth
                            height: 4
                            radius: 2
                            color: Theme.backgroundMedium
                            
                            Rectangle {
                                width: boostSlider.visualPosition * parent.width
                                height: parent.height
                                color: Theme.primary
                                radius: 2
                            }
                        }
                        
                        handle: Rectangle {
                            x: boostSlider.leftPadding + boostSlider.visualPosition * (boostSlider.availableWidth - width)
                            y: boostSlider.topPadding + boostSlider.availableHeight / 2 - height / 2
                            width: 18
                            height: 18
                            radius: 9
                            color: boostSlider.pressed ? Theme.primaryDark : Theme.primary
                            border.color: Theme.backgroundWhite
                            border.width: 2
                        }
                    }
                    
                    Label {
                        text: "+" + boostSlider.value.toFixed(1) + " dB"
                        font.bold: true
                        Layout.preferredWidth: 70
                    }
                }
                
                Label {
                    text: "A new file with '_boosted' suffix will be created"
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.textSecondary
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
        
        // Info section
        Rectangle {
            Layout.fillWidth: true
            height: 60
            color: Theme.backgroundLight
            radius: Theme.radiusSmall
            border.color: Theme.borderColor
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: Theme.spacingMedium
                spacing: Theme.spacingMedium
                
                Label {
                    text: "ℹ"
                    font.pixelSize: 24
                    color: Theme.info
                }
                
                Label {
                    text: {
                        if (operationType === "wav_to_mp3")
                            return "This operation may take several minutes depending on file size and count."
                        if (operationType === "to_mono")
                            return "The conversion will create a backup before replacing the original file."
                        if (operationType === "volume_boost")
                            return "Use this to create a louder version of your audio file."
                        return ""
                    }
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                    font.pixelSize: Theme.fontSizeSmall
                }
            }
        }
    }
}
