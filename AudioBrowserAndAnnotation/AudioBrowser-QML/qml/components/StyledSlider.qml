import QtQuick
import QtQuick.Controls
import "../styles"

/**
 * StyledSlider - Themed slider component with consistent styling
 * 
 * A reusable slider that follows the application theme with smooth
 * interactions and visual feedback.
 * 
 * Properties:
 *   - value: Current slider value (0.0 to 1.0 by default)
 *   - from/to: Range values
 *   - stepSize: Step increment
 *   - enabled: Enable/disable state
 * 
 * Usage:
 *   StyledSlider {
 *       from: 0
 *       to: 100
 *       value: 50
 *       onValueChanged: console.log("Value:", value)
 *   }
 */
Slider {
    id: control
    
    // Visual properties
    implicitWidth: 200
    implicitHeight: Theme.inputHeight
    
    // Custom handle
    handle: Rectangle {
        x: control.leftPadding + control.visualPosition * (control.availableWidth - width)
        y: control.topPadding + control.availableHeight / 2 - height / 2
        implicitWidth: 16
        implicitHeight: 16
        radius: 8
        color: control.pressed ? Theme.accentPrimaryLight : Theme.accentPrimary
        border.color: control.enabled ? Theme.accentPrimary : Theme.borderColor
        border.width: 1
        
        // Smooth animations
        Behavior on color {
            ColorAnimation { duration: Theme.animationFast }
        }
        
        // Scale effect when hovered or pressed
        scale: control.pressed ? 1.1 : (control.hovered ? 1.05 : 1.0)
        
        Behavior on scale {
            NumberAnimation { duration: Theme.animationFast }
        }
    }
    
    // Custom background track
    background: Rectangle {
        x: control.leftPadding
        y: control.topPadding + control.availableHeight / 2 - height / 2
        implicitWidth: 200
        implicitHeight: 4
        width: control.availableWidth
        height: implicitHeight
        radius: 2
        color: Theme.backgroundMedium
        
        // Filled portion of track
        Rectangle {
            width: control.visualPosition * parent.width
            height: parent.height
            color: control.enabled ? Theme.accentPrimary : Theme.borderColor
            radius: 2
            
            Behavior on color {
                ColorAnimation { duration: Theme.animationFast }
            }
        }
    }
    
    // Cursor changes on hover
    MouseArea {
        anchors.fill: parent
        acceptedButtons: Qt.NoButton
        cursorShape: control.enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
    }
}
