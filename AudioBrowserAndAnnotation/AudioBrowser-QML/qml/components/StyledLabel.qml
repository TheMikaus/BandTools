import QtQuick
import QtQuick.Controls.Basic
import "../styles"

Label {
    id: styledLabel
    
    // Variants
    property bool heading: false
    property bool secondary: false
    property bool muted: false
    property bool success: false
    property bool danger: false
    property bool warning: false
    
    // Styling
    font.pixelSize: heading ? Theme.fontSizeLarge : Theme.fontSizeNormal
    font.bold: heading
    
    color: {
        if (success) return Theme.accentSuccess
        if (danger) return Theme.accentDanger
        if (warning) return Theme.accentWarning
        if (muted) return Theme.textMuted
        if (secondary) return Theme.textSecondary
        return Theme.textColor
    }
}
