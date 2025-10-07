import QtQuick
import QtQuick.Controls.Basic
import "../styles"

/*
  StyledButton - Reusable styled button component
  
  A custom button that follows the application theme and provides
  consistent styling across the application.
  
  Usage:
    StyledButton {
        text: "Click Me"
        onClicked: console.log("Button clicked")
    }
    
    StyledButton {
        text: "Primary Action"
        primary: true
    }
    
    StyledButton {
        text: "Danger Action"
        danger: true
    }
*/

Button {
    id: control
    
    // Custom properties
    property bool primary: false
    property bool danger: false
    property bool success: false
    property bool info: false
    property bool warning: false
    
    // Sizing
    implicitHeight: Theme.buttonHeight
    implicitWidth: Math.max(100, contentItem.implicitWidth + leftPadding + rightPadding)
    
    // Padding
    padding: Theme.spacingNormal
    leftPadding: Theme.spacingMedium
    rightPadding: Theme.spacingMedium
    
    // Content (text)
    contentItem: Text {
        text: control.text
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeNormal
        color: {
            if (!control.enabled) {
                return Theme.textMuted
            }
            if (primary || danger || success || info || warning) {
                return "#ffffff"
            }
            return control.hovered ? Theme.textColor : Theme.textSecondary
        }
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
    
    // Background
    background: Rectangle {
        implicitHeight: Theme.buttonHeight
        color: {
            if (!control.enabled) {
                return Theme.backgroundMedium
            }
            if (control.down) {
                if (primary) return Qt.darker(Theme.accentPrimary, 1.3)
                if (danger) return Qt.darker(Theme.accentDanger, 1.3)
                if (success) return Qt.darker(Theme.accentSuccess, 1.3)
                if (info) return Qt.darker(Theme.accentInfo, 1.3)
                if (warning) return Qt.darker(Theme.accentWarning, 1.3)
                return Qt.darker(Theme.backgroundLight, 1.2)
            }
            if (control.hovered) {
                if (primary) return Qt.lighter(Theme.accentPrimary, 1.1)
                if (danger) return Qt.lighter(Theme.accentDanger, 1.1)
                if (success) return Qt.lighter(Theme.accentSuccess, 1.1)
                if (info) return Qt.lighter(Theme.accentInfo, 1.1)
                if (warning) return Qt.lighter(Theme.accentWarning, 1.1)
                return Theme.backgroundLight
            }
            if (primary) return Theme.accentPrimary
            if (danger) return Theme.accentDanger
            if (success) return Theme.accentSuccess
            if (info) return Theme.accentInfo
            if (warning) return Theme.accentWarning
            return Theme.backgroundLight
        }
        border.color: {
            if (!control.enabled) {
                return Theme.borderColor
            }
            if (control.hovered || control.down) {
                if (primary) return Theme.accentPrimary
                if (danger) return Theme.accentDanger
                if (success) return Theme.accentSuccess
                if (info) return Theme.accentInfo
                if (warning) return Theme.accentWarning
                return Theme.textSecondary
            }
            return Theme.borderColor
        }
        border.width: primary || danger || success || info || warning ? 0 : 1
        radius: Theme.radiusSmall
        
        // Smooth color transitions
        Behavior on color {
            ColorAnimation {
                duration: Theme.animationFast
            }
        }
        
        Behavior on border.color {
            ColorAnimation {
                duration: Theme.animationFast
            }
        }
    }
    
    // Hover handling
    hoverEnabled: true
    
    // Cursor shape (using HoverHandler for proper cursor support)
    HoverHandler {
        cursorShape: control.enabled ? Qt.PointingHandCursor : Qt.ForbiddenCursor
    }
}
