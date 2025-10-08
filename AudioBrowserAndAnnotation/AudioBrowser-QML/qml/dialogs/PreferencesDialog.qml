import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "../styles"

/**
 * PreferencesDialog Component
 * 
 * Application preferences and settings dialog.
 * Provides access to all configurable application settings.
 */
Dialog {
    id: preferencesDialog
    title: "Preferences"
    modal: true
    standardButtons: Dialog.Ok | Dialog.Cancel | Dialog.Apply | Dialog.RestoreDefaults
    
    x: (parent.width - width) / 2
    y: (parent.height - height) / 2
    width: 600
    height: 500
    
    background: Rectangle {
        color: Theme.backgroundColor
        border.color: Theme.borderColor
        border.width: 1
        radius: Theme.radiusSmall
    }
    
    // Temporary storage for settings (applied on OK/Apply)
    property int tempUndoLimit: 100
    property int tempParallelWorkers: 4
    property bool tempAutoWaveforms: false
    property bool tempAutoFingerprints: false
    property int tempDefaultZoomLevel: 1
    property string tempWaveformQuality: "medium"
    
    // Load settings when dialog opens
    onAboutToShow: {
        loadSettings()
    }
    
    // Handle button clicks
    onAccepted: {
        applySettings()
    }
    
    onApplied: {
        applySettings()
    }
    
    onReset: {
        restoreDefaults()
    }
    
    function loadSettings() {
        tempUndoLimit = settingsManager.getUndoLimit()
        tempParallelWorkers = 4  // TODO: Add to SettingsManager
        tempAutoWaveforms = settingsManager.getAutoWaveforms()
        tempAutoFingerprints = settingsManager.getAutoFingerprints()
        tempDefaultZoomLevel = 1  // TODO: Add to SettingsManager
        tempWaveformQuality = "medium"  // TODO: Add to SettingsManager
        
        // Update UI controls
        undoLimitSlider.value = tempUndoLimit
        parallelWorkersSlider.value = tempParallelWorkers
        autoWaveformsCheck.checked = tempAutoWaveforms
        autoFingerprintsCheck.checked = tempAutoFingerprints
        defaultZoomSlider.value = tempDefaultZoomLevel
        waveformQualityCombo.currentIndex = waveformQualityCombo.indexOfValue(tempWaveformQuality)
    }
    
    function applySettings() {
        settingsManager.setUndoLimit(tempUndoLimit)
        // TODO: Add parallel workers to settings manager
        settingsManager.setAutoWaveforms(tempAutoWaveforms)
        settingsManager.setAutoFingerprints(tempAutoFingerprints)
        // TODO: Add default zoom and waveform quality to settings manager
        
        console.log("Settings applied:", tempUndoLimit, tempAutoWaveforms, tempAutoFingerprints)
    }
    
    function restoreDefaults() {
        tempUndoLimit = 100
        tempParallelWorkers = 4
        tempAutoWaveforms = false
        tempAutoFingerprints = false
        tempDefaultZoomLevel = 1
        tempWaveformQuality = "medium"
        loadSettings()
    }
    
    ScrollView {
        anchors.fill: parent
        contentWidth: availableWidth
        
        ColumnLayout {
            width: parent.width - 20
            spacing: Theme.spacingLarge
            
            // General Settings Section
            GroupBox {
                Layout.fillWidth: true
                title: "General Settings"
                
                background: Rectangle {
                    color: Theme.backgroundLight
                    border.color: Theme.borderColor
                    border.width: 1
                    radius: Theme.radiusSmall
                }
                
                label: Label {
                    text: parent.title
                    font.bold: true
                    font.pixelSize: Theme.fontSizeLarge
                    color: Theme.textColor
                    leftPadding: Theme.spacingSmall
                }
                
                ColumnLayout {
                    width: parent.width
                    spacing: Theme.spacingNormal
                    
                    // Undo Limit
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: Theme.spacingNormal
                        
                        Label {
                            text: "Undo Limit:"
                            font.pixelSize: Theme.fontSizeNormal
                            color: Theme.textColor
                            Layout.preferredWidth: 150
                        }
                        
                        Slider {
                            id: undoLimitSlider
                            Layout.fillWidth: true
                            from: 10
                            to: 1000
                            stepSize: 10
                            value: tempUndoLimit
                            
                            onValueChanged: {
                                tempUndoLimit = Math.round(value)
                            }
                            
                            background: Rectangle {
                                x: undoLimitSlider.leftPadding
                                y: undoLimitSlider.topPadding + undoLimitSlider.availableHeight / 2 - height / 2
                                width: undoLimitSlider.availableWidth
                                height: 4
                                radius: 2
                                color: Theme.borderColor
                                
                                Rectangle {
                                    width: undoLimitSlider.visualPosition * parent.width
                                    height: parent.height
                                    color: Theme.accentColor
                                    radius: 2
                                }
                            }
                            
                            handle: Rectangle {
                                x: undoLimitSlider.leftPadding + undoLimitSlider.visualPosition * (undoLimitSlider.availableWidth - width)
                                y: undoLimitSlider.topPadding + undoLimitSlider.availableHeight / 2 - height / 2
                                implicitWidth: 20
                                implicitHeight: 20
                                radius: 10
                                color: undoLimitSlider.pressed ? Theme.accentColorDark : Theme.accentColor
                            }
                        }
                        
                        Label {
                            text: tempUndoLimit.toString()
                            font.pixelSize: Theme.fontSizeNormal
                            color: Theme.textColor
                            Layout.preferredWidth: 50
                        }
                    }
                    
                    // Parallel Workers
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: Theme.spacingNormal
                        
                        Label {
                            text: "Parallel Workers:"
                            font.pixelSize: Theme.fontSizeNormal
                            color: Theme.textColor
                            Layout.preferredWidth: 150
                        }
                        
                        Slider {
                            id: parallelWorkersSlider
                            Layout.fillWidth: true
                            from: 0
                            to: 16
                            stepSize: 1
                            value: tempParallelWorkers
                            
                            onValueChanged: {
                                tempParallelWorkers = Math.round(value)
                            }
                            
                            background: Rectangle {
                                x: parallelWorkersSlider.leftPadding
                                y: parallelWorkersSlider.topPadding + parallelWorkersSlider.availableHeight / 2 - height / 2
                                width: parallelWorkersSlider.availableWidth
                                height: 4
                                radius: 2
                                color: Theme.borderColor
                                
                                Rectangle {
                                    width: parallelWorkersSlider.visualPosition * parent.width
                                    height: parent.height
                                    color: Theme.accentColor
                                    radius: 2
                                }
                            }
                            
                            handle: Rectangle {
                                x: parallelWorkersSlider.leftPadding + parallelWorkersSlider.visualPosition * (parallelWorkersSlider.availableWidth - width)
                                y: parallelWorkersSlider.topPadding + parallelWorkersSlider.availableHeight / 2 - height / 2
                                implicitWidth: 20
                                implicitHeight: 20
                                radius: 10
                                color: parallelWorkersSlider.pressed ? Theme.accentColorDark : Theme.accentColor
                            }
                        }
                        
                        Label {
                            text: tempParallelWorkers === 0 ? "Auto" : tempParallelWorkers.toString()
                            font.pixelSize: Theme.fontSizeNormal
                            color: Theme.textColor
                            Layout.preferredWidth: 50
                        }
                    }
                }
            }
            
            // Auto-Generation Settings Section
            GroupBox {
                Layout.fillWidth: true
                title: "Auto-Generation Settings"
                
                background: Rectangle {
                    color: Theme.backgroundLight
                    border.color: Theme.borderColor
                    border.width: 1
                    radius: Theme.radiusSmall
                }
                
                label: Label {
                    text: parent.title
                    font.bold: true
                    font.pixelSize: Theme.fontSizeLarge
                    color: Theme.textColor
                    leftPadding: Theme.spacingSmall
                }
                
                ColumnLayout {
                    width: parent.width
                    spacing: Theme.spacingNormal
                    
                    CheckBox {
                        id: autoWaveformsCheck
                        text: "Auto-generate Waveforms"
                        checked: tempAutoWaveforms
                        
                        onCheckedChanged: {
                            tempAutoWaveforms = checked
                        }
                        
                        contentItem: Text {
                            text: parent.text
                            font.pixelSize: Theme.fontSizeNormal
                            color: Theme.textColor
                            leftPadding: parent.indicator.width + Theme.spacingSmall
                            verticalAlignment: Text.AlignVCenter
                        }
                        
                        indicator: Rectangle {
                            implicitWidth: 20
                            implicitHeight: 20
                            radius: 3
                            border.color: Theme.borderColor
                            border.width: 1
                            color: autoWaveformsCheck.checked ? Theme.accentColor : Theme.backgroundColor
                            
                            Text {
                                anchors.centerIn: parent
                                text: "✓"
                                font.pixelSize: Theme.fontSizeNormal
                                color: Theme.textColor
                                visible: autoWaveformsCheck.checked
                            }
                        }
                    }
                    
                    CheckBox {
                        id: autoFingerprintsCheck
                        text: "Auto-generate Fingerprints"
                        checked: tempAutoFingerprints
                        
                        onCheckedChanged: {
                            tempAutoFingerprints = checked
                        }
                        
                        contentItem: Text {
                            text: parent.text
                            font.pixelSize: Theme.fontSizeNormal
                            color: Theme.textColor
                            leftPadding: parent.indicator.width + Theme.spacingSmall
                            verticalAlignment: Text.AlignVCenter
                        }
                        
                        indicator: Rectangle {
                            implicitWidth: 20
                            implicitHeight: 20
                            radius: 3
                            border.color: Theme.borderColor
                            border.width: 1
                            color: autoFingerprintsCheck.checked ? Theme.accentColor : Theme.backgroundColor
                            
                            Text {
                                anchors.centerIn: parent
                                text: "✓"
                                font.pixelSize: Theme.fontSizeNormal
                                color: Theme.textColor
                                visible: autoFingerprintsCheck.checked
                            }
                        }
                    }
                    
                    Label {
                        text: "Note: Auto-generation may slow down folder loading for large directories."
                        font.pixelSize: Theme.fontSizeSmall
                        color: Theme.textMuted
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                    }
                }
            }
            
            // Display Settings Section
            GroupBox {
                Layout.fillWidth: true
                title: "Display Settings"
                
                background: Rectangle {
                    color: Theme.backgroundLight
                    border.color: Theme.borderColor
                    border.width: 1
                    radius: Theme.radiusSmall
                }
                
                label: Label {
                    text: parent.title
                    font.bold: true
                    font.pixelSize: Theme.fontSizeLarge
                    color: Theme.textColor
                    leftPadding: Theme.spacingSmall
                }
                
                ColumnLayout {
                    width: parent.width
                    spacing: Theme.spacingNormal
                    
                    // Default Zoom Level
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: Theme.spacingNormal
                        
                        Label {
                            text: "Default Zoom Level:"
                            font.pixelSize: Theme.fontSizeNormal
                            color: Theme.textColor
                            Layout.preferredWidth: 150
                        }
                        
                        Slider {
                            id: defaultZoomSlider
                            Layout.fillWidth: true
                            from: 1
                            to: 10
                            stepSize: 1
                            value: tempDefaultZoomLevel
                            
                            onValueChanged: {
                                tempDefaultZoomLevel = Math.round(value)
                            }
                            
                            background: Rectangle {
                                x: defaultZoomSlider.leftPadding
                                y: defaultZoomSlider.topPadding + defaultZoomSlider.availableHeight / 2 - height / 2
                                width: defaultZoomSlider.availableWidth
                                height: 4
                                radius: 2
                                color: Theme.borderColor
                                
                                Rectangle {
                                    width: defaultZoomSlider.visualPosition * parent.width
                                    height: parent.height
                                    color: Theme.accentColor
                                    radius: 2
                                }
                            }
                            
                            handle: Rectangle {
                                x: defaultZoomSlider.leftPadding + defaultZoomSlider.visualPosition * (defaultZoomSlider.availableWidth - width)
                                y: defaultZoomSlider.topPadding + defaultZoomSlider.availableHeight / 2 - height / 2
                                implicitWidth: 20
                                implicitHeight: 20
                                radius: 10
                                color: defaultZoomSlider.pressed ? Theme.accentColorDark : Theme.accentColor
                            }
                        }
                        
                        Label {
                            text: tempDefaultZoomLevel.toString() + "×"
                            font.pixelSize: Theme.fontSizeNormal
                            color: Theme.textColor
                            Layout.preferredWidth: 50
                        }
                    }
                    
                    // Waveform Rendering Quality
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: Theme.spacingNormal
                        
                        Label {
                            text: "Waveform Quality:"
                            font.pixelSize: Theme.fontSizeNormal
                            color: Theme.textColor
                            Layout.preferredWidth: 150
                        }
                        
                        ComboBox {
                            id: waveformQualityCombo
                            Layout.fillWidth: true
                            
                            model: [
                                { text: "Low (Faster)", value: "low" },
                                { text: "Medium (Balanced)", value: "medium" },
                                { text: "High (Better Quality)", value: "high" }
                            ]
                            
                            textRole: "text"
                            valueRole: "value"
                            
                            onActivated: {
                                tempWaveformQuality = currentValue
                            }
                            
                            delegate: ItemDelegate {
                                width: waveformQualityCombo.width
                                
                                contentItem: Text {
                                    text: modelData.text
                                    font.pixelSize: Theme.fontSizeNormal
                                    color: Theme.textColor
                                    verticalAlignment: Text.AlignVCenter
                                }
                                
                                background: Rectangle {
                                    color: parent.hovered ? Theme.backgroundLight : Theme.backgroundColor
                                }
                            }
                            
                            contentItem: Text {
                                leftPadding: Theme.spacingSmall
                                text: waveformQualityCombo.displayText
                                font.pixelSize: Theme.fontSizeNormal
                                color: Theme.textColor
                                verticalAlignment: Text.AlignVCenter
                            }
                            
                            background: Rectangle {
                                color: Theme.backgroundColor
                                border.color: Theme.borderColor
                                border.width: 1
                                radius: Theme.radiusSmall
                            }
                        }
                    }
                }
            }
        }
    }
}
