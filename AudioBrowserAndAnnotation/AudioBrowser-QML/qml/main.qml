import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "components"
import "styles"
import "tabs"

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 1200
    height: 800
    title: "AudioBrowser (QML) - Phase 1 Development"
    
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
                
                // Playback controls (placeholder)
                RowLayout {
                    spacing: Theme.spacingSmall
                    
                    StyledButton {
                        text: "⏮"
                        enabled: false
                    }
                    
                    StyledButton {
                        text: audioEngine.isPlaying() ? "⏸" : "▶"
                        primary: true
                        onClicked: audioEngine.togglePlayPause()
                    }
                    
                    StyledButton {
                        text: "⏹"
                        onClicked: audioEngine.stop()
                    }
                    
                    StyledButton {
                        text: "⏭"
                        enabled: false
                    }
                }
                
                Item { width: Theme.spacingNormal }
                
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
                    text: "Phase 1 Development • Theme: " + settingsManager.getTheme()
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
}
