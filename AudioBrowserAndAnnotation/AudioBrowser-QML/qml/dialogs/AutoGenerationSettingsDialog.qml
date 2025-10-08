import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: autoGenDialog
    title: "Auto-Generation Settings"
    modal: true
    width: 550
    height: 550
    
    // Properties to pass to dialog
    property var settingsManager
    
    // Current settings
    property bool autoGenWaveforms: false
    property bool autoGenFingerprints: false
    property string autoGenTiming: "folder_selection"
    property bool paginationEnabled: true
    property int paginationChunkSize: 500
    property int parallelWorkers: 0
    
    Component.onCompleted: {
        loadCurrentSettings()
    }
    
    function loadCurrentSettings() {
        if (settingsManager) {
            autoGenWaveforms = settingsManager.getSetting("auto_gen_waveforms", false)
            autoGenFingerprints = settingsManager.getSetting("auto_gen_fingerprints", false)
            autoGenTiming = settingsManager.getSetting("auto_gen_timing", "folder_selection")
            paginationEnabled = settingsManager.getSetting("pagination_enabled", true)
            paginationChunkSize = settingsManager.getSetting("pagination_chunk_size", 500)
            parallelWorkers = settingsManager.getSetting("parallel_workers", 0)
            
            // Update UI
            waveformsCheckbox.checked = autoGenWaveforms
            fingerprintsCheckbox.checked = autoGenFingerprints
            timingCombo.currentIndex = autoGenTiming === "boot" ? 0 : 1
            paginationCheckbox.checked = paginationEnabled
            chunkSizeSpinBox.value = paginationChunkSize
            workersSpinBox.value = parallelWorkers
        }
    }
    
    function saveSettings() {
        if (!settingsManager) return
        
        autoGenWaveforms = waveformsCheckbox.checked
        autoGenFingerprints = fingerprintsCheckbox.checked
        autoGenTiming = timingCombo.currentValue
        paginationEnabled = paginationCheckbox.checked
        paginationChunkSize = chunkSizeSpinBox.value
        parallelWorkers = workersSpinBox.value
        
        settingsManager.setSetting("auto_gen_waveforms", autoGenWaveforms)
        settingsManager.setSetting("auto_gen_fingerprints", autoGenFingerprints)
        settingsManager.setSetting("auto_gen_timing", autoGenTiming)
        settingsManager.setSetting("pagination_enabled", paginationEnabled)
        settingsManager.setSetting("pagination_chunk_size", paginationChunkSize)
        settingsManager.setSetting("parallel_workers", parallelWorkers)
        
        autoGenDialog.accept()
    }
    
    contentItem: ScrollView {
        clip: true
        
        ColumnLayout {
            width: autoGenDialog.availableWidth
            spacing: 15
            
            // Description
            Label {
                text: "Configure automatic generation settings for the entire band practice folder."
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                font.pointSize: 10
            }
            
            // Auto-generation settings group
            GroupBox {
                title: "Auto-Generation Settings"
                Layout.fillWidth: true
                
                ColumnLayout {
                    anchors.fill: parent
                    spacing: 12
                    
                    // Auto-generate waveforms checkbox
                    CheckBox {
                        id: waveformsCheckbox
                        text: "Auto-generate waveform images"
                        ToolTip.visible: hovered
                        ToolTip.text: "Automatically generate waveform visualizations for audio files"
                    }
                    
                    // Auto-generate fingerprints checkbox
                    CheckBox {
                        id: fingerprintsCheckbox
                        text: "Auto-generate audio fingerprints"
                        ToolTip.visible: hovered
                        ToolTip.text: "Automatically generate audio fingerprints for song matching and duplicate detection"
                    }
                    
                    // Timing selection
                    RowLayout {
                        spacing: 10
                        
                        Label {
                            text: "Auto-generate:"
                            font.bold: true
                        }
                        
                        ComboBox {
                            id: timingCombo
                            Layout.fillWidth: true
                            
                            model: [
                                { text: "On application startup", value: "boot" },
                                { text: "When clicking into folder", value: "folder_selection" }
                            ]
                            
                            textRole: "text"
                            valueRole: "value"
                            
                            ToolTip.visible: hovered
                            ToolTip.text: "When to automatically start generation of waveforms and fingerprints"
                        }
                    }
                    
                    Label {
                        text: "Note: Auto-generation runs in the background and won't block the UI"
                        Layout.fillWidth: true
                        wrapMode: Text.WordWrap
                        font.pointSize: 9
                        font.italic: true
                        color: colorManager.getColor("text_dim")
                    }
                }
            }
            
            // Performance settings group
            GroupBox {
                title: "Performance Settings"
                Layout.fillWidth: true
                
                ColumnLayout {
                    anchors.fill: parent
                    spacing: 12
                    
                    // Pagination settings
                    ColumnLayout {
                        spacing: 8
                        Layout.fillWidth: true
                        
                        CheckBox {
                            id: paginationCheckbox
                            text: "Enable pagination for large libraries"
                            ToolTip.visible: hovered
                            ToolTip.text: "Automatically load files in chunks for libraries with 500+ files"
                        }
                        
                        RowLayout {
                            spacing: 10
                            enabled: paginationCheckbox.checked
                            Layout.leftMargin: 30
                            
                            Label {
                                text: "Files per page:"
                            }
                            
                            SpinBox {
                                id: chunkSizeSpinBox
                                from: 50
                                to: 1000
                                stepSize: 50
                                value: 500
                                editable: true
                                
                                ToolTip.visible: hovered
                                ToolTip.text: "Number of files to display at once (applies to large libraries)"
                            }
                            
                            Item { Layout.fillWidth: true }
                        }
                        
                        Label {
                            text: "Note: QML version uses efficient list virtualization, so pagination is optional"
                            Layout.fillWidth: true
                            Layout.leftMargin: 30
                            wrapMode: Text.WordWrap
                            font.pointSize: 8
                            font.italic: true
                            color: colorManager.getColor("text_dim")
                            visible: !paginationCheckbox.checked
                        }
                    }
                    
                    Rectangle {
                        Layout.fillWidth: true
                        height: 1
                        color: colorManager.getColor("border")
                    }
                    
                    // Parallel workers setting
                    ColumnLayout {
                        spacing: 8
                        Layout.fillWidth: true
                        
                        Label {
                            text: "Background Processing"
                            font.bold: true
                        }
                        
                        RowLayout {
                            spacing: 10
                            
                            Label {
                                text: "Parallel workers:"
                            }
                            
                            SpinBox {
                                id: workersSpinBox
                                from: 0
                                to: 16
                                value: 0
                                editable: true
                                
                                textFromValue: function(value) {
                                    return value === 0 ? "Auto" : value.toString()
                                }
                                
                                valueFromText: function(text) {
                                    return text === "Auto" ? 0 : parseInt(text)
                                }
                                
                                ToolTip.visible: hovered
                                ToolTip.text: "Number of parallel workers for generation (0 = auto-detect based on CPU cores)"
                            }
                            
                            Item { Layout.fillWidth: true }
                        }
                        
                        Label {
                            text: workersSpinBox.value === 0 
                                ? "Auto mode will use optimal number of workers based on your CPU"
                                : `Using ${workersSpinBox.value} worker thread(s) for background tasks`
                            Layout.fillWidth: true
                            Layout.leftMargin: 30
                            wrapMode: Text.WordWrap
                            font.pointSize: 8
                            font.italic: true
                            color: colorManager.getColor("text_dim")
                        }
                    }
                }
            }
            
            // Info note
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: infoLayout.implicitHeight + 20
                color: colorManager.getColor("info_bg")
                border.color: colorManager.getColor("accent")
                border.width: 1
                radius: 4
                
                ColumnLayout {
                    id: infoLayout
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 5
                    
                    Label {
                        text: "ℹ️ Recommendations"
                        font.bold: true
                        color: colorManager.getColor("accent")
                    }
                    
                    Label {
                        text: "• Enable waveform auto-generation for better visual feedback\n" +
                              "• Enable fingerprint auto-generation if you need song matching\n" +
                              "• Use 'folder_selection' timing for better performance on startup\n" +
                              "• Keep parallel workers on 'Auto' unless you experience issues"
                        Layout.fillWidth: true
                        wrapMode: Text.WordWrap
                        font.pointSize: 9
                    }
                }
            }
            
            Item {
                Layout.fillHeight: true
            }
        }
    }
    
    footer: DialogButtonBox {
        Button {
            text: "Cancel"
            DialogButtonBox.buttonRole: DialogButtonBox.RejectRole
        }
        Button {
            text: "Save"
            DialogButtonBox.buttonRole: DialogButtonBox.AcceptRole
        }
        
        onAccepted: saveSettings()
        onRejected: autoGenDialog.reject()
    }
}
