import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 1200
    height: 800
    title: "AudioBrowser (QML) - Phase 0"
    
    // Color scheme (will be moved to Theme.qml in Phase 1)
    color: "#2b2b2b"
    
    // Main content area
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 20
        
        // Header
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 80
            color: "#3b3b3b"
            radius: 8
            
            ColumnLayout {
                anchors.centerIn: parent
                spacing: 10
                
                Label {
                    text: appViewModel.getMessage()
                    font.pixelSize: 24
                    font.bold: true
                    color: "#ffffff"
                    Layout.alignment: Qt.AlignHCenter
                }
                
                Label {
                    text: "QML Migration Infrastructure Test"
                    font.pixelSize: 14
                    color: "#cccccc"
                    Layout.alignment: Qt.AlignHCenter
                }
            }
        }
        
        // Info panel
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "#353535"
            radius: 8
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 15
                
                Label {
                    text: "✓ Phase 0: Preparation • ⏳ Phase 1: In Progress"
                    font.pixelSize: 18
                    font.bold: true
                    color: "#4ade80"
                }
                
                Label {
                    text: "Status: Backend modules integrated • Current theme: " + settingsManager.getTheme()
                    font.pixelSize: 14
                    color: "#ffffff"
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }
                
                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: "#555555"
                }
                
                Label {
                    text: "Completed:"
                    font.pixelSize: 14
                    font.bold: true
                    color: "#ffffff"
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
                            font.pixelSize: 12
                            color: "#cccccc"
                            leftPadding: 20
                        }
                    }
                }
                
                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: "#555555"
                }
                
                Label {
                    text: "Next: Phase 1 - Core Infrastructure"
                    font.pixelSize: 14
                    font.bold: true
                    color: "#fbbf24"
                }
                
                ColumnLayout {
                    spacing: 8
                    Layout.fillWidth: true
                    
                    Repeater {
                        model: [
                            "• Split audio_browser.py into backend modules",
                            "• Create backend classes (audio, waveform, file managers)",
                            "• Implement tab structure in QML",
                            "• Set up theming system",
                            "• Create reusable QML components"
                        ]
                        
                        Label {
                            text: modelData
                            font.pixelSize: 12
                            color: "#999999"
                            leftPadding: 20
                        }
                    }
                }
                
                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: "#555555"
                }
                
                Label {
                    text: "Backend Integration Test:"
                    font.pixelSize: 14
                    font.bold: true
                    color: "#ffffff"
                }
                
                RowLayout {
                    spacing: 15
                    Layout.fillWidth: true
                    
                    ColumnLayout {
                        spacing: 8
                        Layout.fillWidth: true
                        
                        Label {
                            text: "SettingsManager:"
                            font.pixelSize: 12
                            color: "#cccccc"
                        }
                        
                        Label {
                            text: "  • Theme: " + settingsManager.getTheme()
                            font.pixelSize: 11
                            color: "#999999"
                        }
                        
                        Label {
                            text: "  • Volume: " + settingsManager.getVolume() + "%"
                            font.pixelSize: 11
                            color: "#999999"
                        }
                    }
                    
                    ColumnLayout {
                        spacing: 8
                        Layout.fillWidth: true
                        
                        Label {
                            text: "ColorManager:"
                            font.pixelSize: 12
                            color: "#cccccc"
                        }
                        
                        Label {
                            text: "  • Success: " + colorManager.getSuccessColor()
                            font.pixelSize: 11
                            color: colorManager.getSuccessColor()
                        }
                        
                        Label {
                            text: "  • Danger: " + colorManager.getDangerColor()
                            font.pixelSize: 11
                            color: colorManager.getDangerColor()
                        }
                    }
                }
                
                Item {
                    Layout.fillHeight: true
                }
                
                // Test buttons for backend integration
                RowLayout {
                    spacing: 10
                    Layout.alignment: Qt.AlignHCenter
                    
                    Button {
                        text: "Test Python-QML Communication"
                        
                        onClicked: {
                            appViewModel.setMessage("Communication Test Successful! ✓")
                        }
                    }
                    
                    Button {
                        text: "Toggle Theme (Test)"
                        
                        onClicked: {
                            var currentTheme = settingsManager.getTheme()
                            var newTheme = currentTheme === "dark" ? "light" : "dark"
                            settingsManager.setTheme(newTheme)
                        }
                    }
                }
            }
        }
        
        // Footer
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 40
            color: "#3b3b3b"
            radius: 8
            
            Label {
                anchors.centerIn: parent
                text: "AudioBrowser QML Migration • Phase 0 Complete"
                font.pixelSize: 12
                color: "#888888"
            }
        }
    }
}
