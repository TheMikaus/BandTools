import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "../styles"

/**
 * AboutDialog Component
 * 
 * Displays information about the AudioBrowser QML application.
 * Shows version, features, and development info.
 */
Dialog {
    id: aboutDialog
    title: "About AudioBrowser QML"
    modal: true
    standardButtons: Dialog.Ok
    
    x: (parent.width - width) / 2
    y: (parent.height - height) / 2
    width: 500
    height: 400
    
    background: Rectangle {
        color: Theme.backgroundColor
        border.color: Theme.borderColor
        border.width: 1
        radius: Theme.radiusSmall
    }
    
    ColumnLayout {
        anchors.fill: parent
        spacing: Theme.spacingNormal
        
        // Title
        Label {
            text: "AudioBrowser QML"
            font.pixelSize: Theme.fontSizeTitle
            font.bold: true
            color: Theme.textColor
            Layout.alignment: Qt.AlignHCenter
        }
        
        // Version info
        Label {
            text: "Version 0.7.0 (Phase 7)"
            font.pixelSize: Theme.fontSizeLarge
            color: Theme.textSecondary
            Layout.alignment: Qt.AlignHCenter
        }
        
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 1
            color: Theme.borderColor
        }
        
        // Description
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            
            TextArea {
                readOnly: true
                textFormat: TextEdit.PlainText
                wrapMode: TextEdit.Wrap
                color: Theme.textColor
                background: Rectangle {
                    color: "transparent"
                }
                
                text: "AudioBrowser QML is a modern audio file management and annotation tool built with Qt Quick.\n\n" +
                      "Features:\n" +
                      "• Audio playback with waveform visualization\n" +
                      "• Annotation system with categories\n" +
                      "• Clip management and export\n" +
                      "• Best/Partial take indicators\n" +
                      "• Practice statistics and goals\n" +
                      "• Setlist builder\n" +
                      "• Tempo/BPM tracking\n" +
                      "• Spectrogram overlay\n" +
                      "• Audio fingerprinting\n" +
                      "• Batch operations (rename, convert)\n" +
                      "• Recent folders menu\n" +
                      "• Dark and light themes\n\n" +
                      "Developed with AI assistance (GitHub Copilot)\n" +
                      "Part of the BandTools project\n\n" +
                      "© 2025 BandTools"
            }
        }
    }
}
