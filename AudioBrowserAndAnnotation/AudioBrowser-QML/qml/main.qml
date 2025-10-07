import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "components"
import "styles"
import "tabs"
import "dialogs"

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 1200
    height: 800
    title: "AudioBrowser (QML) - Phase 7 (Additional Features - 55% Complete)"
    
    // Use theme for background color
    color: Theme.backgroundColor
    
    // Main content area with tabs
    ColumnLayout {
        anchors.fill: parent
        spacing: 0
        
        // Toolbar
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: Theme.toolbarHeight
            color: Theme.backgroundLight
            
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: Theme.spacingNormal
                anchors.rightMargin: Theme.spacingNormal
                spacing: Theme.spacingLarge
                
                Label {
                    text: "AudioBrowser QML"
                    font.pixelSize: Theme.fontSizeLarge
                    font.bold: true
                    color: Theme.textColor
                }
                
                Item { Layout.fillWidth: true }
                
                // Playback controls
                PlaybackControls {
                    Layout.fillWidth: true
                    Layout.preferredHeight: Theme.toolbarHeight
                }
                
                Item { width: Theme.spacingSmall }
                
                // Theme toggle
                StyledButton {
                    text: "Theme"
                    success: true
                    onClicked: {
                        var currentTheme = settingsManager.getTheme()
                        var newTheme = currentTheme === "dark" ? "light" : "dark"
                        settingsManager.setTheme(newTheme)
                        Theme.setTheme(newTheme)
                    }
                }
            }
        }
        
        // Tab bar
        TabBar {
            id: tabBar
            Layout.fillWidth: true
            background: Rectangle {
                color: Theme.backgroundLight
            }
            
            TabButton {
                text: "Library"
                font.pixelSize: Theme.fontSizeNormal
                
                background: Rectangle {
                    color: tabBar.currentIndex === 0 ? Theme.backgroundColor : Theme.backgroundLight
                }
                
                contentItem: Text {
                    text: parent.text
                    font: parent.font
                    color: tabBar.currentIndex === 0 ? Theme.textColor : Theme.textSecondary
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
            
            TabButton {
                text: "Annotations"
                font.pixelSize: Theme.fontSizeNormal
                
                background: Rectangle {
                    color: tabBar.currentIndex === 1 ? Theme.backgroundColor : Theme.backgroundLight
                }
                
                contentItem: Text {
                    text: parent.text
                    font: parent.font
                    color: tabBar.currentIndex === 1 ? Theme.textColor : Theme.textSecondary
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
            
            TabButton {
                text: "Clips"
                font.pixelSize: Theme.fontSizeNormal
                
                background: Rectangle {
                    color: tabBar.currentIndex === 2 ? Theme.backgroundColor : Theme.backgroundLight
                }
                
                contentItem: Text {
                    text: parent.text
                    font: parent.font
                    color: tabBar.currentIndex === 2 ? Theme.textColor : Theme.textSecondary
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
            
            TabButton {
                text: "Folder Notes"
                font.pixelSize: Theme.fontSizeNormal
                
                background: Rectangle {
                    color: tabBar.currentIndex === 3 ? Theme.backgroundColor : Theme.backgroundLight
                }
                
                contentItem: Text {
                    text: parent.text
                    font: parent.font
                    color: tabBar.currentIndex === 3 ? Theme.textColor : Theme.textSecondary
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
        }
        
        // Tab content
        StackLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: tabBar.currentIndex
            
            LibraryTab {
                id: libraryTab
            }
            
            AnnotationsTab {
                id: annotationsTab
            }
            
            ClipsTab {
                id: clipsTab
            }
            
            FolderNotesTab {
                id: folderNotesTab
            }
        }
        
        // Batch operations dialogs
        BatchRenameDialog {
            id: batchRenameDialog
            batchOperations: batchOperations
            fileManager: fileManager
            
            onRenameCompleted: {
                // Refresh file list after rename
                var dir = fileManager.getCurrentDirectory()
                if (dir.length > 0) {
                    fileManager.discoverAudioFiles(dir)
                }
                progressDialog.showResult(true, "Rename operation completed successfully")
            }
        }
        
        BatchConvertDialog {
            id: batchConvertDialog
            batchOperations: batchOperations
            
            onConversionCompleted: {
                // Refresh file list after conversion
                var dir = fileManager.getCurrentDirectory()
                if (dir.length > 0) {
                    fileManager.discoverAudioFiles(dir)
                }
            }
        }
        
        ProgressDialog {
            id: progressDialog
            batchOperations: batchOperations
        }
        
        // Practice Statistics Dialog
        PracticeStatisticsDialog {
            id: practiceStatisticsDialog
            practiceStatistics: practiceStatistics
            fileManager: fileManager
        }
        
        // Status bar
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: Theme.statusBarHeight
            color: Theme.backgroundLight
            
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: Theme.spacingNormal
                anchors.rightMargin: Theme.spacingNormal
                spacing: Theme.spacingLarge
                
                Label {
                    text: audioEngine.getPlaybackState() === "playing" ? "Playing" : "Ready"
                    font.pixelSize: Theme.fontSizeSmall
                    color: audioEngine.getPlaybackState() === "playing" ? Theme.accentSuccess : Theme.textMuted
                }
                
                Label {
                    text: audioEngine.getCurrentFile() ? "File: " + fileManager.getFileName(audioEngine.getCurrentFile()) : ""
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.textMuted
                    elide: Text.ElideMiddle
                    Layout.fillWidth: true
                }
                
                Label {
                    text: "Phase 7 (Additional Features) • Theme: " + settingsManager.getTheme()
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.textMuted
                }
            }
        }
    }
    
    // Update status bar when playback state changes
    Connections {
        target: audioEngine
        
        function onPlaybackStateChanged(state) {
            // Force status bar to update
            mainWindow.update()
        }
    }
    
    // Keyboard shortcuts
    Shortcut {
        sequence: "Space"
        // Only activate if no text input has focus
        enabled: !mainWindow.activeFocusItem || 
                 mainWindow.activeFocusItem.toString().indexOf("TextField") === -1 &&
                 mainWindow.activeFocusItem.toString().indexOf("TextArea") === -1 &&
                 mainWindow.activeFocusItem.toString().indexOf("TextEdit") === -1
        onActivated: audioEngine.togglePlayPause()
    }
    
    Shortcut {
        sequence: "Escape"
        onActivated: audioEngine.stop()
    }
    
    Shortcut {
        sequence: "Ctrl+T"
        onActivated: {
            var currentTheme = settingsManager.getTheme()
            var newTheme = currentTheme === "dark" ? "light" : "dark"
            settingsManager.setTheme(newTheme)
            Theme.setTheme(newTheme)
        }
    }
    
    Shortcut {
        sequence: "Ctrl+1"
        onActivated: tabBar.currentIndex = 0
    }
    
    Shortcut {
        sequence: "Ctrl+2"
        onActivated: tabBar.currentIndex = 1
    }
    
    Shortcut {
        sequence: "Ctrl+3"
        onActivated: tabBar.currentIndex = 2
    }
    
    Shortcut {
        sequence: "Ctrl+4"
        onActivated: tabBar.currentIndex = 3
    }
    
    Shortcut {
        sequence: "+"
        onActivated: {
            var vol = audioEngine.getVolume()
            audioEngine.setVolume(Math.min(100, vol + 5))
        }
    }
    
    Shortcut {
        sequence: "-"
        onActivated: {
            var vol = audioEngine.getVolume()
            audioEngine.setVolume(Math.max(0, vol - 5))
        }
    }
    
    // Navigation shortcuts
    Shortcut {
        sequence: "Left"
        onActivated: audioEngine.seekBackward(5000)  // 5 seconds back
    }
    
    Shortcut {
        sequence: "Right"
        onActivated: audioEngine.seekForward(5000)  // 5 seconds forward
    }
    
    // Annotation shortcuts
    Shortcut {
        sequence: "Ctrl+A"
        // Only activate if not in text input
        enabled: !mainWindow.activeFocusItem || 
                 mainWindow.activeFocusItem.toString().indexOf("TextField") === -1 &&
                 mainWindow.activeFocusItem.toString().indexOf("TextArea") === -1 &&
                 mainWindow.activeFocusItem.toString().indexOf("TextEdit") === -1
        onActivated: {
            if (audioEngine.getCurrentFile() !== "") {
                annotationsTab.openAddDialog()
            }
        }
    }
    
    // Clip marker shortcuts
    Shortcut {
        sequence: "["
        // Only activate if not in text input
        enabled: !mainWindow.activeFocusItem || 
                 mainWindow.activeFocusItem.toString().indexOf("TextField") === -1 &&
                 mainWindow.activeFocusItem.toString().indexOf("TextArea") === -1 &&
                 mainWindow.activeFocusItem.toString().indexOf("TextEdit") === -1
        onActivated: {
            if (audioEngine.getCurrentFile() !== "") {
                clipsTab.setClipStartMarker()
            }
        }
    }
    
    Shortcut {
        sequence: "]"
        // Only activate if not in text input
        enabled: !mainWindow.activeFocusItem || 
                 mainWindow.activeFocusItem.toString().indexOf("TextField") === -1 &&
                 mainWindow.activeFocusItem.toString().indexOf("TextArea") === -1 &&
                 mainWindow.activeFocusItem.toString().indexOf("TextEdit") === -1
        onActivated: {
            if (audioEngine.getCurrentFile() !== "") {
                clipsTab.setClipEndMarker()
            }
        }
    }
    
    // Batch operations signal connections
    Connections {
        target: batchOperations
        
        function onOperationStarted(operationName) {
            progressDialog.openDialog(operationName)
        }
        
        function onOperationProgress(done, total, currentFile) {
            progressDialog.updateProgress(done, total, currentFile)
        }
        
        function onOperationFinished(success, message) {
            progressDialog.showResult(success, message)
        }
        
        function onErrorOccurred(errorMessage) {
            progressDialog.showResult(false, "Error: " + errorMessage)
        }
    }
}
