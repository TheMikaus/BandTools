import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import "../components"
import "../styles"
import "../dialogs"

Item {
    id: libraryTab
    
    // Properties
    property string currentDirectory: ""
    
    // Folder picker dialog
    FileDialog {
        id: folderDialog
        title: "Select Audio Directory"
        fileMode: FileDialog.OpenFile
        currentFolder: "file://" + fileManager.getCurrentDirectory()
        
        onAccepted: {
            var folderPath = selectedFile.toString()
            
            // Remove file:// prefix
            if (folderPath.startsWith("file://")) {
                folderPath = folderPath.substring(7)
            }
            
            // Extract directory from selected file
            var lastSlash = folderPath.lastIndexOf("/")
            if (lastSlash > 0) {
                folderPath = folderPath.substring(0, lastSlash)
            }
            
            fileManager.setCurrentDirectory(folderPath)
            directoryField.text = folderPath
        }
    }
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacingNormal
        spacing: Theme.spacingNormal
        
        // Toolbar
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: Theme.toolbarHeight
            color: Theme.backgroundLight
            radius: Theme.radiusSmall
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: Theme.spacingSmall
                spacing: Theme.spacingNormal
                
                Label {
                    text: "Directory:"
                    font.pixelSize: Theme.fontSizeNormal
                    color: Theme.textColor
                }
                
                TextField {
                    id: directoryField
                    Layout.fillWidth: true
                    placeholderText: "Select a directory..."
                    text: fileManager.getCurrentDirectory()
                    font.pixelSize: Theme.fontSizeNormal
                    background: Rectangle {
                        color: Theme.backgroundColor
                        border.color: Theme.borderColor
                        border.width: 1
                        radius: Theme.radiusSmall
                    }
                    color: Theme.textColor
                    
                    onAccepted: {
                        if (text.length > 0) {
                            fileManager.setCurrentDirectory(text)
                        }
                    }
                }
                
                StyledButton {
                    text: "Browse..."
                    onClicked: {
                        folderDialog.open()
                    }
                }
                
                StyledButton {
                    text: "Refresh"
                    success: true
                    onClicked: {
                        var dir = fileManager.getCurrentDirectory()
                        if (dir.length > 0) {
                            fileManager.discoverAudioFiles(dir)
                        }
                    }
                }
            }
        }
        
        // File list
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: Theme.backgroundColor
            border.color: Theme.borderColor
            border.width: 1
            radius: Theme.radiusSmall
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: Theme.spacingSmall
                spacing: 0
                
                // Header
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: Theme.buttonHeight
                    color: Theme.backgroundLight
                    
                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: Theme.spacingNormal
                        anchors.rightMargin: Theme.spacingNormal
                        spacing: Theme.spacingNormal
                        
                        Label {
                            text: "Files (" + fileListModel.count() + ")"
                            font.pixelSize: Theme.fontSizeMedium
                            font.bold: true
                            color: Theme.textColor
                            Layout.fillWidth: true
                        }
                        
                        TextField {
                            id: filterField
                            Layout.preferredWidth: 200
                            placeholderText: "Filter..."
                            font.pixelSize: Theme.fontSizeNormal
                            background: Rectangle {
                                color: Theme.backgroundColor
                                border.color: Theme.borderColor
                                border.width: 1
                                radius: Theme.radiusSmall
                            }
                            color: Theme.textColor
                        }
                    }
                }
                
                // File ListView
                ListView {
                    id: fileListView
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    
                    model: fileListModel
                    
                    delegate: Rectangle {
                        width: fileListView.width
                        height: 32
                        color: index % 2 === 0 ? Theme.backgroundColor : Theme.backgroundMedium
                        
                        // Hover effect
                        Rectangle {
                            anchors.fill: parent
                            color: Theme.accentPrimary
                            opacity: mouseArea.containsMouse ? 0.1 : 0
                            
                            Behavior on opacity {
                                NumberAnimation { duration: Theme.animationFast }
                            }
                        }
                        
                        // Selection highlight
                        Rectangle {
                            anchors.fill: parent
                            color: Theme.selectionPrimary
                            opacity: fileListView.currentIndex === index ? 0.3 : 0
                        }
                        
                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: Theme.spacingNormal
                            anchors.rightMargin: Theme.spacingNormal
                            spacing: Theme.spacingNormal
                            
                            Label {
                                text: model.filename
                                font.pixelSize: Theme.fontSizeNormal
                                color: Theme.textColor
                                Layout.fillWidth: true
                                elide: Text.ElideMiddle
                            }
                            
                            Label {
                                text: formatFileSize(model.filesize)
                                font.pixelSize: Theme.fontSizeSmall
                                color: Theme.textSecondary
                                Layout.preferredWidth: 80
                                horizontalAlignment: Text.AlignRight
                            }
                        }
                        
                        MouseArea {
                            id: mouseArea
                            anchors.fill: parent
                            hoverEnabled: true
                            
                            onClicked: {
                                fileListView.currentIndex = index
                                console.log("Selected file:", model.filepath)
                            }
                            
                            onDoubleClicked: {
                                console.log("Double-clicked file:", model.filepath)
                                audioEngine.loadFile(model.filepath)
                                audioEngine.play()
                            }
                        }
                    }
                    
                    ScrollBar.vertical: ScrollBar {
                        policy: ScrollBar.AsNeeded
                    }
                }
            }
        }
        
        // Status bar
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: Theme.statusBarHeight
            color: Theme.backgroundLight
            radius: Theme.radiusSmall
            
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: Theme.spacingNormal
                anchors.rightMargin: Theme.spacingNormal
                spacing: Theme.spacingLarge
                
                Label {
                    text: "Ready"
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.textMuted
                }
                
                Item { Layout.fillWidth: true }
                
                Label {
                    text: fileManager.getCurrentDirectory()
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.textMuted
                    elide: Text.ElideMiddle
                }
            }
        }
    }
    
    // Helper function to format file size
    function formatFileSize(bytes) {
        if (bytes < 1024) {
            return bytes + " B"
        } else if (bytes < 1024 * 1024) {
            return (bytes / 1024).toFixed(1) + " KB"
        } else if (bytes < 1024 * 1024 * 1024) {
            return (bytes / (1024 * 1024)).toFixed(1) + " MB"
        } else {
            return (bytes / (1024 * 1024 * 1024)).toFixed(1) + " GB"
        }
    }
    
    // Connections to handle file manager signals
    Connections {
        target: fileManager
        
        function onCurrentDirectoryChanged(directory) {
            directoryField.text = directory
        }
        
        function onErrorOccurred(errorMessage) {
            console.error("File Manager Error:", errorMessage)
        }
    }
}
