import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "components"
import "styles"

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 1200
    height: 800
    title: "AudioBrowser (QML) - Phase 1 Progress"
    
    // Use theme for background color
    color: Theme.backgroundColor
    
    // Main content area
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 20
        
        // Header
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 80
            color: Theme.backgroundLight
            radius: Theme.radiusNormal
            
            ColumnLayout {
                anchors.centerIn: parent
                spacing: 10
                
                Label {
                    text: appViewModel.getMessage()
                    font.pixelSize: Theme.fontSizeXLarge
                    font.bold: true
                    color: Theme.textColor
                    Layout.alignment: Qt.AlignHCenter
                }
                
                Label {
                    text: "QML Migration - Backend Integration"
                    font.pixelSize: Theme.fontSizeMedium
                    color: Theme.textSecondary
                    Layout.alignment: Qt.AlignHCenter
                }
            }
        }
        
        // Info panel
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: Theme.backgroundMedium
            radius: Theme.radiusNormal
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 15
                
                Label {
                    text: "✓ Phase 0: Preparation • ⏳ Phase 1: In Progress"
                    font.pixelSize: Theme.fontSizeLarge
                    font.bold: true
                    color: Theme.accentSuccess
                }
                
                Label {
                    text: "Status: Backend modules integrated • Current theme: " + settingsManager.getTheme()
                    font.pixelSize: Theme.fontSizeMedium
                    color: Theme.textColor
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }
                
                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: Theme.borderColor
                }
                
                Label {
                    text: "Completed:"
                    font.pixelSize: Theme.fontSizeMedium
                    font.bold: true
                    color: Theme.textColor
                }
                
                ColumnLayout {
                    spacing: 8
                    Layout.fillWidth: true
                    
                    Repeater {
                        model: [
                            "✓ Project directory structure created",
                            "✓ main.py entry point implemented",
                            "✓ PyQt6.QtQuick dependencies configured",
                            "✓ QML main window rendering",
                            "✓ Python-QML communication established",
                            "✓ SettingsManager backend module created",
                            "✓ ColorManager backend module created",
                            "✓ Backend managers exposed to QML"
                        ]
                        
                        Label {
                            text: modelData
                            font.pixelSize: Theme.fontSizeNormal
                            color: Theme.textSecondary
                            leftPadding: Theme.spacingLarge
                        }
                    }
                }
                
                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: Theme.borderColor
                }
                
                Label {
                    text: "Next Steps:"
                    font.pixelSize: Theme.fontSizeMedium
                    font.bold: true
                    color: Theme.accentWarning
                }
                
                ColumnLayout {
                    spacing: 8
                    Layout.fillWidth: true
                    
                    Repeater {
                        model: [
                            "• Extract audio_engine from audio_browser.py",
                            "• Extract file_manager from audio_browser.py",
                            "• Implement QML tab structure (Library, Annotations, Clips)",
                            "• Create more reusable QML components",
                            "• Implement file list model"
                        ]
                        
                        Label {
                            text: modelData
                            font.pixelSize: Theme.fontSizeNormal
                            color: Theme.textMuted
                            leftPadding: Theme.spacingLarge
                        }
                    }
                }
                
                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: Theme.borderColor
                }
                
                Label {
                    text: "Backend Integration Test:"
                    font.pixelSize: Theme.fontSizeMedium
                    font.bold: true
                    color: Theme.textColor
                }
                
                RowLayout {
                    spacing: 15
                    Layout.fillWidth: true
                    
                    ColumnLayout {
                        spacing: 8
                        Layout.fillWidth: true
                        
                        Label {
                            text: "SettingsManager:"
                            font.pixelSize: Theme.fontSizeNormal
                            color: Theme.textSecondary
                        }
                        
                        Label {
                            text: "  • Theme: " + settingsManager.getTheme()
                            font.pixelSize: Theme.fontSizeSmall
                            color: Theme.textMuted
                        }
                        
                        Label {
                            text: "  • Volume: " + settingsManager.getVolume() + "%"
                            font.pixelSize: Theme.fontSizeSmall
                            color: Theme.textMuted
                        }
                    }
                    
                    ColumnLayout {
                        spacing: 8
                        Layout.fillWidth: true
                        
                        Label {
                            text: "ColorManager:"
                            font.pixelSize: Theme.fontSizeNormal
                            color: Theme.textSecondary
                        }
                        
                        Label {
                            text: "  • Success: " + colorManager.getSuccessColor()
                            font.pixelSize: Theme.fontSizeSmall
                            color: colorManager.getSuccessColor()
                        }
                        
                        Label {
                            text: "  • Danger: " + colorManager.getDangerColor()
                            font.pixelSize: Theme.fontSizeSmall
                            color: colorManager.getDangerColor()
                        }
                    }
                }
                
                Item {
                    Layout.fillHeight: true
                }
                
                // Test buttons for backend integration
                RowLayout {
                    spacing: Theme.spacingNormal
                    Layout.alignment: Qt.AlignHCenter
                    
                    StyledButton {
                        text: "Test Communication"
                        primary: true
                        
                        onClicked: {
                            appViewModel.setMessage("Communication Test Successful! ✓")
                        }
                    }
                    
                    StyledButton {
                        text: "Toggle Theme"
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
        }
        
        // Footer
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: Theme.statusBarHeight
            color: Theme.backgroundLight
            radius: Theme.radiusNormal
            
            Label {
                anchors.centerIn: parent
                text: "AudioBrowser QML Migration • Phase 0 Complete • Phase 1 In Progress"
                font.pixelSize: Theme.fontSizeNormal
                color: Theme.textMuted
            }
        }
    }
}
