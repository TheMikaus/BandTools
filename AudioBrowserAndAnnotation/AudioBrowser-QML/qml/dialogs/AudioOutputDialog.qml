import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "../components"
import "../styles"

Dialog {
    id: audioOutputDialog
    title: "Audio Output Device"
    modal: true
    width: 500
    height: 400
    anchors.centerIn: parent
    
    background: Rectangle {
        color: Theme.backgroundColor
        border.color: Theme.borderColor
        border.width: 1
        radius: Theme.radiusNormal
    }
    
    ColumnLayout {
        anchors.fill: parent
        spacing: Theme.spacingNormal
        
        Label {
            text: "Select Audio Output Device:"
            font.pixelSize: Theme.fontSizeNormal
            font.bold: true
            color: Theme.textColor
        }
        
        Label {
            text: "Choose the audio output device for playback"
            font.pixelSize: Theme.fontSizeSmall
            color: Theme.textMuted
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }
        
        // Device list
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: Theme.backgroundColor
            border.color: Theme.borderColor
            border.width: 1
            radius: Theme.radiusSmall
            
            ListView {
                id: deviceListView
                anchors.fill: parent
                anchors.margins: 1
                clip: true
                
                model: ListModel {
                    id: deviceListModel
                }
                
                delegate: Rectangle {
                    width: deviceListView.width
                    height: 48
                    color: deviceMouseArea.containsMouse ? Theme.backgroundLight : 
                           (model.isCurrent ? Theme.backgroundMedium : "transparent")
                    
                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: Theme.spacingNormal
                        anchors.rightMargin: Theme.spacingNormal
                        spacing: Theme.spacingNormal
                        
                        // Selection indicator
                        Label {
                            text: model.isCurrent ? "●" : "○"
                            font.pixelSize: Theme.fontSizeLarge
                            color: model.isCurrent ? Theme.accentPrimary : Theme.textMuted
                            Layout.preferredWidth: 24
                        }
                        
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 2
                            
                            Label {
                                text: model.description
                                font.pixelSize: Theme.fontSizeNormal
                                font.bold: model.isCurrent
                                color: Theme.textColor
                                Layout.fillWidth: true
                                elide: Text.ElideRight
                            }
                            
                            Label {
                                text: model.id || "(Default Device)"
                                font.pixelSize: Theme.fontSizeSmall
                                color: Theme.textMuted
                                Layout.fillWidth: true
                                elide: Text.ElideMiddle
                            }
                        }
                    }
                    
                    MouseArea {
                        id: deviceMouseArea
                        anchors.fill: parent
                        hoverEnabled: true
                        
                        onClicked: {
                            // Update selection
                            for (var i = 0; i < deviceListModel.count; i++) {
                                deviceListModel.setProperty(i, "isCurrent", i === index)
                            }
                            selectedDeviceId = model.id
                        }
                    }
                }
                
                ScrollBar.vertical: ScrollBar {
                    policy: ScrollBar.AsNeeded
                }
            }
        }
        
        // Info label
        Label {
            text: "Note: Changes will take effect immediately"
            font.pixelSize: Theme.fontSizeSmall
            font.italic: true
            color: Theme.textMuted
            Layout.fillWidth: true
        }
        
        // Buttons
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacingNormal
            
            Item { Layout.fillWidth: true }
            
            StyledButton {
                text: "Refresh"
                Layout.preferredWidth: 100
                onClicked: refreshDeviceList()
            }
            
            StyledButton {
                text: "Close"
                primary: true
                Layout.preferredWidth: 100
                onClicked: audioOutputDialog.close()
            }
        }
    }
    
    // Track selected device
    property string selectedDeviceId: ""
    
    // Functions
    function refreshDeviceList() {
        deviceListModel.clear()
        
        if (!audioEngine) return
        
        var devices = audioEngine.getAudioOutputDevices()
        var currentDevice = audioEngine.getCurrentAudioOutputDevice()
        
        for (var i = 0; i < devices.length; i++) {
            var device = devices[i]
            deviceListModel.append({
                id: device.id,
                description: device.description,
                isCurrent: device.id === currentDevice
            })
        }
        
        selectedDeviceId = currentDevice
    }
    
    function applyDevice() {
        if (audioEngine && selectedDeviceId !== undefined) {
            audioEngine.setAudioOutputDevice(selectedDeviceId)
            // Save to settings
            if (settingsManager) {
                settingsManager.setAudioOutputDevice(selectedDeviceId)
            }
        }
    }
    
    // Refresh when opened
    onOpened: {
        refreshDeviceList()
    }
    
    // Apply when device selection changes
    onSelectedDeviceIdChanged: {
        if (opened) {
            applyDevice()
        }
    }
    
    // Listen for device changes
    Connections {
        target: audioEngine
        
        function onAudioOutputDevicesChanged() {
            if (audioOutputDialog.opened) {
                refreshDeviceList()
            }
        }
    }
}
