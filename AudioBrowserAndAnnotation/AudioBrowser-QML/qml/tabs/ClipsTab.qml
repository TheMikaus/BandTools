import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"
import "../styles"

Item {
    id: clipsTab
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacingLarge
        spacing: Theme.spacingLarge
        
        Label {
            text: "Clips Tab"
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
                    "• Audio clip management",
                    "• Clip creation and editing",
                    "• Clip playback and export",
                    "• Loop markers visualization",
                    "• Clip metadata and organization"
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
            text: "Coming in Phase 3"
            font.pixelSize: Theme.fontSizeMedium
            font.italic: true
            color: Theme.accentWarning
            Layout.alignment: Qt.AlignHCenter
        }
    }
}
