import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "../styles"

/**
 * SyncDialog Component
 * 
 * Google Drive synchronization dialog.
 * Allows users to authenticate, select folders, and sync files.
 */
Dialog {
    id: syncDialog
    title: "Google Drive Sync"
    modal: true
    standardButtons: Dialog.Close
    
    x: (parent.width - width) / 2
    y: (parent.height - height) / 2
    width: 700
    height: 600
    
    background: Rectangle {
        color: Theme.backgroundColor
        border.color: Theme.borderColor
        border.width: 1
        radius: Theme.radiusSmall
    }
    
    // Status properties
    property bool isAuthenticated: false
    property string currentFolder: ""
    property bool isSyncing: false
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacingLarge
        spacing: Theme.spacingLarge
        
        // Title
        Label {
            text: "Google Drive Synchronization"
            font.pixelSize: Theme.fontSizeLarge
            font.bold: true
            color: Theme.textColor
            Layout.fillWidth: true
        }
        
        // Status section
        GroupBox {
            title: "Status"
            Layout.fillWidth: true
            
            background: Rectangle {
                color: Theme.surfaceColor
                border.color: Theme.borderColor
                radius: Theme.radiusSmall
            }
            
            label: Label {
                text: parent.title
                font.bold: true
                font.pixelSize: Theme.fontSizeNormal
                color: Theme.textColor
                leftPadding: Theme.spacingSmall
            }
            
            ColumnLayout {
                width: parent.width
                spacing: Theme.spacingNormal
                
                // Authentication status
                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spacingNormal
                    
                    Label {
                        text: "Authentication:"
                        font.pixelSize: Theme.fontSizeNormal
                        color: Theme.textColor
                    }
                    
                    Label {
                        text: isAuthenticated ? "✓ Authenticated" : "⚠ Not authenticated"
                        font.pixelSize: Theme.fontSizeNormal
                        color: isAuthenticated ? Theme.successColor : Theme.warningColor
                    }
                    
                    Item { Layout.fillWidth: true }
                    
                    Button {
                        text: isAuthenticated ? "Re-authenticate" : "Authenticate"
                        enabled: !isSyncing
                        
                        background: Rectangle {
                            color: parent.enabled ? (parent.pressed ? Theme.accentColorPressed : 
                                   parent.hovered ? Theme.accentColorHover : Theme.accentColor) : Theme.disabledColor
                            radius: Theme.radiusSmall
                        }
                        
                        contentItem: Text {
                            text: parent.text
                            font.pixelSize: Theme.fontSizeNormal
                            color: parent.enabled ? Theme.buttonTextColor : Theme.disabledTextColor
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        
                        onClicked: {
                            if (typeof gdriveSync !== "undefined" && gdriveSync.isAvailable()) {
                                isAuthenticated = gdriveSync.authenticate()
                                if (!isAuthenticated) {
                                    statusLabel.text = "Authentication failed. Check credentials file."
                                    statusLabel.color = Theme.errorColor
                                }
                            } else {
                                statusLabel.text = "Google Drive API not available. Install required packages."
                                statusLabel.color = Theme.errorColor
                            }
                        }
                    }
                }
                
                // Folder selection
                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spacingNormal
                    visible: isAuthenticated
                    
                    Label {
                        text: "Remote Folder:"
                        font.pixelSize: Theme.fontSizeNormal
                        color: Theme.textColor
                    }
                    
                    TextField {
                        id: folderNameField
                        Layout.fillWidth: true
                        placeholderText: "Enter folder name (e.g., BandPracticeSessions)"
                        text: currentFolder
                        enabled: !isSyncing
                        
                        background: Rectangle {
                            color: Theme.backgroundColor
                            border.color: folderNameField.focus ? Theme.accentColor : Theme.borderColor
                            border.width: 1
                            radius: Theme.radiusSmall
                        }
                        
                        color: Theme.textColor
                        font.pixelSize: Theme.fontSizeNormal
                    }
                    
                    Button {
                        text: "Select/Create"
                        enabled: !isSyncing && folderNameField.text.length > 0
                        
                        background: Rectangle {
                            color: parent.enabled ? (parent.pressed ? Theme.accentColorPressed : 
                                   parent.hovered ? Theme.accentColorHover : Theme.accentColor) : Theme.disabledColor
                            radius: Theme.radiusSmall
                        }
                        
                        contentItem: Text {
                            text: parent.text
                            font.pixelSize: Theme.fontSizeNormal
                            color: parent.enabled ? Theme.buttonTextColor : Theme.disabledTextColor
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        
                        onClicked: {
                            if (typeof gdriveSync !== "undefined") {
                                var folderId = gdriveSync.select_remote_folder(folderNameField.text)
                                if (folderId) {
                                    currentFolder = folderNameField.text
                                    statusLabel.text = "Folder selected: " + currentFolder
                                    statusLabel.color = Theme.successColor
                                } else {
                                    statusLabel.text = "Failed to select/create folder"
                                    statusLabel.color = Theme.errorColor
                                }
                            }
                        }
                    }
                }
            }
        }
        
        // Sync operations section
        GroupBox {
            title: "Sync Operations"
            Layout.fillWidth: true
            visible: isAuthenticated && currentFolder.length > 0
            
            background: Rectangle {
                color: Theme.surfaceColor
                border.color: Theme.borderColor
                radius: Theme.radiusSmall
            }
            
            label: Label {
                text: parent.title
                font.bold: true
                font.pixelSize: Theme.fontSizeNormal
                color: Theme.textColor
                leftPadding: Theme.spacingSmall
            }
            
            ColumnLayout {
                width: parent.width
                spacing: Theme.spacingNormal
                
                Label {
                    text: "Choose sync direction:"
                    font.pixelSize: Theme.fontSizeNormal
                    color: Theme.textColor
                    Layout.fillWidth: true
                }
                
                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spacingLarge
                    
                    Button {
                        text: "⬆ Upload Local Changes"
                        Layout.fillWidth: true
                        enabled: !isSyncing
                        
                        background: Rectangle {
                            color: parent.enabled ? (parent.pressed ? Theme.accentColorPressed : 
                                   parent.hovered ? Theme.accentColorHover : Theme.accentColor) : Theme.disabledColor
                            radius: Theme.radiusSmall
                        }
                        
                        contentItem: Text {
                            text: parent.text
                            font.pixelSize: Theme.fontSizeNormal
                            color: parent.enabled ? Theme.buttonTextColor : Theme.disabledTextColor
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        
                        onClicked: {
                            if (typeof gdriveSync !== "undefined" && typeof fileManager !== "undefined") {
                                var currentDir = fileManager.getCurrentFolder()
                                if (currentDir) {
                                    isSyncing = true
                                    statusLabel.text = "Uploading files..."
                                    statusLabel.color = Theme.accentColor
                                    
                                    if (gdriveSync.performSync(currentDir, true)) {
                                        // Success will be reported via signal
                                    } else {
                                        statusLabel.text = "Upload failed"
                                        statusLabel.color = Theme.errorColor
                                        isSyncing = false
                                    }
                                }
                            }
                        }
                    }
                    
                    Button {
                        text: "⬇ Download Remote Changes"
                        Layout.fillWidth: true
                        enabled: !isSyncing
                        
                        background: Rectangle {
                            color: parent.enabled ? (parent.pressed ? Theme.accentColorPressed : 
                                   parent.hovered ? Theme.accentColorHover : Theme.accentColor) : Theme.disabledColor
                            radius: Theme.radiusSmall
                        }
                        
                        contentItem: Text {
                            text: parent.text
                            font.pixelSize: Theme.fontSizeNormal
                            color: parent.enabled ? Theme.buttonTextColor : Theme.disabledTextColor
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        
                        onClicked: {
                            if (typeof gdriveSync !== "undefined" && typeof fileManager !== "undefined") {
                                var currentDir = fileManager.getCurrentFolder()
                                if (currentDir) {
                                    isSyncing = true
                                    statusLabel.text = "Downloading files..."
                                    statusLabel.color = Theme.accentColor
                                    
                                    if (gdriveSync.performSync(currentDir, false)) {
                                        // Success will be reported via signal
                                    } else {
                                        statusLabel.text = "Download failed"
                                        statusLabel.color = Theme.errorColor
                                        isSyncing = false
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        // Progress/Status area
        GroupBox {
            title: "Progress"
            Layout.fillWidth: true
            Layout.fillHeight: true
            visible: isSyncing || statusLabel.text.length > 0
            
            background: Rectangle {
                color: Theme.surfaceColor
                border.color: Theme.borderColor
                radius: Theme.radiusSmall
            }
            
            label: Label {
                text: parent.title
                font.bold: true
                font.pixelSize: Theme.fontSizeNormal
                color: Theme.textColor
                leftPadding: Theme.spacingSmall
            }
            
            ScrollView {
                anchors.fill: parent
                clip: true
                
                TextArea {
                    id: progressLog
                    readOnly: true
                    wrapMode: TextArea.Wrap
                    color: Theme.textColor
                    font.pixelSize: Theme.fontSizeSmall
                    font.family: "monospace"
                    
                    background: Rectangle {
                        color: Theme.backgroundColor
                        border.color: Theme.borderColor
                        radius: Theme.radiusSmall
                    }
                }
            }
        }
        
        // Status label
        Label {
            id: statusLabel
            text: ""
            font.pixelSize: Theme.fontSizeNormal
            color: Theme.textColor
            Layout.fillWidth: true
            wrapMode: Text.Wrap
        }
        
        Item {
            Layout.fillHeight: true
        }
    }
    
    // Connect to backend signals
    Component.onCompleted: {
        if (typeof gdriveSync !== "undefined") {
            // Check if API is available
            if (!gdriveSync.isAvailable()) {
                statusLabel.text = "Google Drive API not available. Please install required packages:\n" +
                                 "pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client"
                statusLabel.color = Theme.warningColor
            }
            
            // Connect signals
            gdriveSync.syncProgress.connect(function(message) {
                progressLog.text += message + "\n"
            })
            
            gdriveSync.syncCompleted.connect(function(success, message, count) {
                isSyncing = false
                statusLabel.text = message
                statusLabel.color = success ? Theme.successColor : Theme.warningColor
                progressLog.text += "\n" + message + "\n"
            })
            
            gdriveSync.syncError.connect(function(message) {
                isSyncing = false
                statusLabel.text = "Error: " + message
                statusLabel.color = Theme.errorColor
                progressLog.text += "ERROR: " + message + "\n"
            })
            
            gdriveSync.authenticationStatusChanged.connect(function(success, message) {
                isAuthenticated = success
                statusLabel.text = message
                statusLabel.color = success ? Theme.successColor : Theme.errorColor
            })
            
            gdriveSync.folderSelected.connect(function(folderId, folderName) {
                currentFolder = folderName
                statusLabel.text = "Folder selected: " + folderName
                statusLabel.color = Theme.successColor
            })
            
            // Check initial authentication state
            isAuthenticated = gdriveSync.isAuthenticated()
        }
    }
}
