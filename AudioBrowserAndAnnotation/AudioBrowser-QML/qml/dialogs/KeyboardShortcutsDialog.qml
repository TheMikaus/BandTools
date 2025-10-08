import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "../styles"

/**
 * KeyboardShortcutsDialog Component
 * 
 * Displays all available keyboard shortcuts in the application.
 * Organized by category for easy reference.
 */
Dialog {
    id: keyboardShortcutsDialog
    title: "Keyboard Shortcuts"
    modal: true
    standardButtons: Dialog.Ok
    
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
    
    ScrollView {
        anchors.fill: parent
        contentWidth: availableWidth
        
        ColumnLayout {
            width: parent.width - 20
            spacing: Theme.spacingLarge
            
            // Title
            Label {
                text: "Keyboard Shortcuts Reference"
                font.pixelSize: Theme.fontSizeTitle
                font.bold: true
                color: Theme.textColor
                Layout.alignment: Qt.AlignHCenter
            }
            
            // Playback Section
            GroupBox {
                Layout.fillWidth: true
                title: "Playback"
                
                background: Rectangle {
                    color: Theme.backgroundLight
                    border.color: Theme.borderColor
                    border.width: 1
                    radius: Theme.radiusSmall
                }
                
                label: Label {
                    text: parent.title
                    font.bold: true
                    font.pixelSize: Theme.fontSizeLarge
                    color: Theme.textColor
                    leftPadding: Theme.spacingSmall
                }
                
                GridLayout {
                    width: parent.width
                    columns: 2
                    rowSpacing: Theme.spacingSmall
                    columnSpacing: Theme.spacingLarge
                    
                    Label { text: "Space"; font.pixelSize: Theme.fontSizeNormal; color: Theme.accentColor; font.bold: true }
                    Label { text: "Play / Pause"; font.pixelSize: Theme.fontSizeNormal; color: Theme.textColor }
                    
                    Label { text: "Escape"; font.pixelSize: Theme.fontSizeNormal; color: Theme.accentColor; font.bold: true }
                    Label { text: "Stop"; font.pixelSize: Theme.fontSizeNormal; color: Theme.textColor }
                    
                    Label { text: "Left Arrow"; font.pixelSize: Theme.fontSizeNormal; color: Theme.accentColor; font.bold: true }
                    Label { text: "Seek backward 5 seconds"; font.pixelSize: Theme.fontSizeNormal; color: Theme.textColor }
                    
                    Label { text: "Right Arrow"; font.pixelSize: Theme.fontSizeNormal; color: Theme.accentColor; font.bold: true }
                    Label { text: "Seek forward 5 seconds"; font.pixelSize: Theme.fontSizeNormal; color: Theme.textColor }
                    
                    Label { text: "+"; font.pixelSize: Theme.fontSizeNormal; color: Theme.accentColor; font.bold: true }
                    Label { text: "Increase volume"; font.pixelSize: Theme.fontSizeNormal; color: Theme.textColor }
                    
                    Label { text: "-"; font.pixelSize: Theme.fontSizeNormal; color: Theme.accentColor; font.bold: true }
                    Label { text: "Decrease volume"; font.pixelSize: Theme.fontSizeNormal; color: Theme.textColor }
                }
            }
            
            // File Operations Section
            GroupBox {
                Layout.fillWidth: true
                title: "File Operations"
                
                background: Rectangle {
                    color: Theme.backgroundLight
                    border.color: Theme.borderColor
                    border.width: 1
                    radius: Theme.radiusSmall
                }
                
                label: Label {
                    text: parent.title
                    font.bold: true
                    font.pixelSize: Theme.fontSizeLarge
                    color: Theme.textColor
                    leftPadding: Theme.spacingSmall
                }
                
                GridLayout {
                    width: parent.width
                    columns: 2
                    rowSpacing: Theme.spacingSmall
                    columnSpacing: Theme.spacingLarge
                    
                    Label { text: "Ctrl+O"; font.pixelSize: Theme.fontSizeNormal; color: Theme.accentColor; font.bold: true }
                    Label { text: "Open folder"; font.pixelSize: Theme.fontSizeNormal; color: Theme.textColor }
                    
                    Label { text: "F5"; font.pixelSize: Theme.fontSizeNormal; color: Theme.accentColor; font.bold: true }
                    Label { text: "Refresh file list"; font.pixelSize: Theme.fontSizeNormal; color: Theme.textColor }
                    
                    Label { text: "Ctrl+Q"; font.pixelSize: Theme.fontSizeNormal; color: Theme.accentColor; font.bold: true }
                    Label { text: "Quit application"; font.pixelSize: Theme.fontSizeNormal; color: Theme.textColor }
                }
            }
            
            // Navigation Section
            GroupBox {
                Layout.fillWidth: true
                title: "Navigation"
                
                background: Rectangle {
                    color: Theme.backgroundLight
                    border.color: Theme.borderColor
                    border.width: 1
                    radius: Theme.radiusSmall
                }
                
                label: Label {
                    text: parent.title
                    font.bold: true
                    font.pixelSize: Theme.fontSizeLarge
                    color: Theme.textColor
                    leftPadding: Theme.spacingSmall
                }
                
                GridLayout {
                    width: parent.width
                    columns: 2
                    rowSpacing: Theme.spacingSmall
                    columnSpacing: Theme.spacingLarge
                    
                    Label { text: "Ctrl+1"; font.pixelSize: Theme.fontSizeNormal; color: Theme.accentColor; font.bold: true }
                    Label { text: "Switch to Library tab"; font.pixelSize: Theme.fontSizeNormal; color: Theme.textColor }
                    
                    Label { text: "Ctrl+2"; font.pixelSize: Theme.fontSizeNormal; color: Theme.accentColor; font.bold: true }
                    Label { text: "Switch to Annotations tab"; font.pixelSize: Theme.fontSizeNormal; color: Theme.textColor }
                    
                    Label { text: "Ctrl+3"; font.pixelSize: Theme.fontSizeNormal; color: Theme.accentColor; font.bold: true }
                    Label { text: "Switch to Clips tab"; font.pixelSize: Theme.fontSizeNormal; color: Theme.textColor }
                    
                    Label { text: "Ctrl+4"; font.pixelSize: Theme.fontSizeNormal; color: Theme.accentColor; font.bold: true }
                    Label { text: "Switch to Folder Notes tab"; font.pixelSize: Theme.fontSizeNormal; color: Theme.textColor }
                    
                    Label { text: "Ctrl+5"; font.pixelSize: Theme.fontSizeNormal; color: Theme.accentColor; font.bold: true }
                    Label { text: "Switch to Fingerprints tab"; font.pixelSize: Theme.fontSizeNormal; color: Theme.textColor }
                }
            }
            
            // Annotations and Clips Section
            GroupBox {
                Layout.fillWidth: true
                title: "Annotations & Clips"
                
                background: Rectangle {
                    color: Theme.backgroundLight
                    border.color: Theme.borderColor
                    border.width: 1
                    radius: Theme.radiusSmall
                }
                
                label: Label {
                    text: parent.title
                    font.bold: true
                    font.pixelSize: Theme.fontSizeLarge
                    color: Theme.textColor
                    leftPadding: Theme.spacingSmall
                }
                
                GridLayout {
                    width: parent.width
                    columns: 2
                    rowSpacing: Theme.spacingSmall
                    columnSpacing: Theme.spacingLarge
                    
                    Label { text: "Ctrl+A"; font.pixelSize: Theme.fontSizeNormal; color: Theme.accentColor; font.bold: true }
                    Label { text: "Add annotation"; font.pixelSize: Theme.fontSizeNormal; color: Theme.textColor }
                    
                    Label { text: "["; font.pixelSize: Theme.fontSizeNormal; color: Theme.accentColor; font.bold: true }
                    Label { text: "Set clip start marker"; font.pixelSize: Theme.fontSizeNormal; color: Theme.textColor }
                    
                    Label { text: "]"; font.pixelSize: Theme.fontSizeNormal; color: Theme.accentColor; font.bold: true }
                    Label { text: "Set clip end marker"; font.pixelSize: Theme.fontSizeNormal; color: Theme.textColor }
                }
            }
            
            // Dialogs Section
            GroupBox {
                Layout.fillWidth: true
                title: "Dialogs & Windows"
                
                background: Rectangle {
                    color: Theme.backgroundLight
                    border.color: Theme.borderColor
                    border.width: 1
                    radius: Theme.radiusSmall
                }
                
                label: Label {
                    text: parent.title
                    font.bold: true
                    font.pixelSize: Theme.fontSizeLarge
                    color: Theme.textColor
                    leftPadding: Theme.spacingSmall
                }
                
                GridLayout {
                    width: parent.width
                    columns: 2
                    rowSpacing: Theme.spacingSmall
                    columnSpacing: Theme.spacingLarge
                    
                    Label { text: "Ctrl+Shift+T"; font.pixelSize: Theme.fontSizeNormal; color: Theme.accentColor; font.bold: true }
                    Label { text: "Open Setlist Builder"; font.pixelSize: Theme.fontSizeNormal; color: Theme.textColor }
                    
                    Label { text: "Ctrl+Shift+S"; font.pixelSize: Theme.fontSizeNormal; color: Theme.accentColor; font.bold: true }
                    Label { text: "Open Practice Statistics"; font.pixelSize: Theme.fontSizeNormal; color: Theme.textColor }
                    
                    Label { text: "Ctrl+Shift+G"; font.pixelSize: Theme.fontSizeNormal; color: Theme.accentColor; font.bold: true }
                    Label { text: "Open Practice Goals"; font.pixelSize: Theme.fontSizeNormal; color: Theme.textColor }
                    
                    Label { text: "Ctrl+,"; font.pixelSize: Theme.fontSizeNormal; color: Theme.accentColor; font.bold: true }
                    Label { text: "Open Preferences"; font.pixelSize: Theme.fontSizeNormal; color: Theme.textColor }
                    
                    Label { text: "F1 or Ctrl+/"; font.pixelSize: Theme.fontSizeNormal; color: Theme.accentColor; font.bold: true }
                    Label { text: "Show this help"; font.pixelSize: Theme.fontSizeNormal; color: Theme.textColor }
                }
            }
            
            // Appearance Section
            GroupBox {
                Layout.fillWidth: true
                title: "Appearance"
                
                background: Rectangle {
                    color: Theme.backgroundLight
                    border.color: Theme.borderColor
                    border.width: 1
                    radius: Theme.radiusSmall
                }
                
                label: Label {
                    text: parent.title
                    font.bold: true
                    font.pixelSize: Theme.fontSizeLarge
                    color: Theme.textColor
                    leftPadding: Theme.spacingSmall
                }
                
                GridLayout {
                    width: parent.width
                    columns: 2
                    rowSpacing: Theme.spacingSmall
                    columnSpacing: Theme.spacingLarge
                    
                    Label { text: "Ctrl+T"; font.pixelSize: Theme.fontSizeNormal; color: Theme.accentColor; font.bold: true }
                    Label { text: "Toggle dark/light theme"; font.pixelSize: Theme.fontSizeNormal; color: Theme.textColor }
                }
            }
            
            // Note
            Label {
                text: "Note: Some shortcuts may be disabled when text input fields have focus to avoid conflicts."
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.textMuted
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
            }
        }
    }
}
