import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"
import "../styles"

Item {
    id: annotationsTab
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacingLarge
        spacing: Theme.spacingLarge
        
        Label {
            text: "Annotations Tab"
            font.pixelSize: Theme.fontSizeXLarge
            font.bold: true
            color: Theme.textColor
            Layout.alignment: Qt.AlignHCenter
        }
        
        Label {
            text: "This tab will contain:"
            font.pixelSize: Theme.fontSizeMedium
            color: Theme.textSecondary
            Layout.alignment: Qt.AlignHCenter
        }
        
        ColumnLayout {
            spacing: Theme.spacingSmall
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignHCenter
            
            Repeater {
                model: [
                    "• Waveform display with markers",
                    "• Annotation table with timestamp navigation",
                    "• Annotation categories and importance marking",
                    "• Multi-user annotation support",
                    "• Playback controls integrated with waveform"
                ]
                
                Label {
                    text: modelData
                    font.pixelSize: Theme.fontSizeNormal
                    color: Theme.textMuted
                    leftPadding: Theme.spacingXLarge
                }
            }
        }
        
        Item { Layout.fillHeight: true }
        
        Label {
            text: "Coming in Phase 2"
            font.pixelSize: Theme.fontSizeMedium
            font.italic: true
            color: Theme.accentWarning
            Layout.alignment: Qt.AlignHCenter
        }
    }
}
