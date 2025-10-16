import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: backupDialog
    title: "Restore from Backup"
    modal: true
    width: 600
    height: 500
    
    // Properties to pass to dialog
    property var backupManager
    property string currentFolder: ""
    property string rootPath: ""
    
    // Internal properties
    property var availableBackups: []
    property string selectedBackupPath: ""
    property string selectedTargetFolder: ""
    property var backupContents: []
    
    Component.onCompleted: {
        if (backupManager && rootPath) {
            loadAvailableBackups()
        }
    }
    
    function loadAvailableBackups() {
        availableBackups = backupManager.discoverBackups(rootPath)
        backupCombo.model = availableBackups
        if (availableBackups.length > 0) {
            backupCombo.currentIndex = 0
            updateBackupContents()
        }
    }
    
    function updateBackupContents() {
        if (backupCombo.currentIndex >= 0 && availableBackups.length > 0) {
            var backup = availableBackups[backupCombo.currentIndex]
            selectedBackupPath = backup.path
            backupContents = backupManager.getBackupContents(backup.path)
            
            // Update target folder combo
            targetFolderCombo.clear()
            targetFolderCombo.append({
                text: "Current folder: " + getRelativePath(currentFolder),
                value: currentFolder
            })
            
            // Add the practice folder from the backup as an option
            var practiceFolderPath = backup.practiceFolder
            if (practiceFolderPath && practiceFolderPath !== currentFolder) {
                targetFolderCombo.append({
                    text: "Original folder: " + getRelativePath(practiceFolderPath),
                    value: practiceFolderPath
                })
            }
            
            // Set default target folder
            targetFolderCombo.currentIndex = 0
            selectedTargetFolder = currentFolder
        }
    }
    
    function getRelativePath(path) {
        if (!path || !rootPath) return path
        if (path.startsWith(rootPath)) {
            var rel = path.substring(rootPath.length)
            if (rel.startsWith("/")) rel = rel.substring(1)
            return rel || "Root"
        }
        return path
    }
    
    function performRestore() {
        if (!selectedBackupPath || !selectedTargetFolder) {
            statusLabel.text = "Please select a backup and target folder"
            statusLabel.color = colorManager ? colorManager.getColor("error") : "#ef5350"
            return
        }
        
        var filesRestored = backupManager.restoreBackup(selectedBackupPath, selectedTargetFolder)
        if (filesRestored > 0) {
            statusLabel.text = `Successfully restored ${filesRestored} file(s)`
            statusLabel.color = colorManager ? colorManager.getColor("success") : "#66bb6a"
            // Close dialog after successful restore
            Qt.callLater(function() {
                backupDialog.accept()
            })
        } else {
            statusLabel.text = "No files were restored"
            statusLabel.color = colorManager ? colorManager.getColor("warning") : "#ffa726"
        }
    }
    
    contentItem: ColumnLayout {
        spacing: 15
        
        // Description
        Label {
            text: "Select a backup to restore and choose the target folder:"
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
            font.pointSize: 10
        }
        
        // Backup selection group
        GroupBox {
            title: "Select Backup"
            Layout.fillWidth: true
            
            ColumnLayout {
                anchors.fill: parent
                spacing: 10
                
                Label {
                    text: "Available backups:"
                    font.bold: true
                }
                
                ComboBox {
                    id: backupCombo
                    Layout.fillWidth: true
                    textRole: "displayName"
                    
                    onCurrentIndexChanged: {
                        updateBackupContents()
                    }
                }
                
                Label {
                    text: `Backup contains ${backupContents.length} file(s):`
                    visible: backupContents.length > 0
                    font.italic: true
                }
                
                ScrollView {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 120
                    visible: backupContents.length > 0
                    
                    ListView {
                        model: backupContents
                        delegate: Label {
                            text: "• " + modelData
                            font.pixelSize: 11
                            leftPadding: 10
                        }
                    }
                }
                
                Label {
                    text: "No files found in this backup"
                    visible: backupContents.length === 0
                    color: colorManager ? colorManager.getColor("text_dim") : "#808080"
                    font.italic: true
                }
            }
        }
        
        // Target folder selection group
        GroupBox {
            title: "Restore To"
            Layout.fillWidth: true
            
            ColumnLayout {
                anchors.fill: parent
                spacing: 10
                
                Label {
                    text: "Target folder:"
                    font.bold: true
                }
                
                ComboBox {
                    id: targetFolderCombo
                    Layout.fillWidth: true
                    textRole: "text"
                    valueRole: "value"
                    
                    model: ListModel {
                        id: targetFolderModel
                    }
                    
                    onCurrentIndexChanged: {
                        if (currentIndex >= 0) {
                            selectedTargetFolder = model.get(currentIndex).value
                        }
                    }
                    
                    function clear() {
                        model.clear()
                    }
                    
                    function append(item) {
                        model.append(item)
                    }
                }
            }
        }
        
        // Status label
        Label {
            id: statusLabel
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
            font.italic: true
            visible: text !== ""
        }
        
        // Warning message
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: warningLayout.implicitHeight + 20
            color: colorManager ? colorManager.getColor("warning_bg") : "#4a3a1f"
            border.color: colorManager ? colorManager.getColor("warning") : "#ffa726"
            border.width: 1
            radius: 4
            
            ColumnLayout {
                id: warningLayout
                anchors.fill: parent
                anchors.margins: 10
                spacing: 5
                
                Label {
                    text: "⚠️ Warning"
                    font.bold: true
                    color: colorManager ? colorManager.getColor("warning") : "#ffa726"
                }
                
                Label {
                    text: "Restoring from backup will overwrite any existing metadata files in the target folder. This action cannot be undone."
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap
                    font.pointSize: 9
                }
            }
        }
    }
    
    footer: DialogButtonBox {
        Button {
            text: "Cancel"
            DialogButtonBox.buttonRole: DialogButtonBox.RejectRole
        }
        Button {
            text: "Restore"
            DialogButtonBox.buttonRole: DialogButtonBox.AcceptRole
            enabled: availableBackups.length > 0 && backupContents.length > 0
        }
        
        onAccepted: performRestore()
        onRejected: backupDialog.reject()
    }
}
