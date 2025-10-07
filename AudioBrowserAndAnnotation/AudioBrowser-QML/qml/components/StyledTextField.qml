import QtQuick
import QtQuick.Controls.Basic
import "../styles"

TextField {
    id: styledTextField
    
    // Variants
    property bool error: false
    
    font.pixelSize: Theme.fontSizeNormal
    color: Theme.textColor
    placeholderTextColor: Theme.textMuted
    
    background: Rectangle {
        color: Theme.backgroundColor
        border.color: {
            if (error) return Theme.accentDanger
            if (styledTextField.activeFocus) return Theme.accentPrimary
            return Theme.borderColor
        }
        border.width: 1
        radius: Theme.radiusSmall
        
        Behavior on border.color {
            ColorAnimation { duration: Theme.animationFast }
        }
    }
    
    // Padding
    leftPadding: Theme.spacingSmall
    rightPadding: Theme.spacingSmall
    topPadding: Theme.spacingSmall
    bottomPadding: Theme.spacingSmall
}
