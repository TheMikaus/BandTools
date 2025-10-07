import QtQuick
import QtQuick.Controls.Basic
import "../styles"

/**
 * AnnotationMarker Component
 * 
 * Displays an annotation marker on the waveform at a specific timestamp.
 * Shows a vertical line with an optional flag and tooltip on hover.
 */
Item {
    id: root
    
    // Properties
    property int timestampMs: 0
    property string text: ""
    property string category: ""
    property bool important: false
    property color markerColor: Theme.accentPrimary
    property int waveformDurationMs: 0
    property int waveformWidth: 0
    
    // Signals
    signal clicked(int timestampMs)
    signal doubleClicked(int timestampMs)
    signal rightClicked(int timestampMs)
    
    // Calculate x position based on timestamp
    property real xPosition: waveformDurationMs > 0 ? 
        (timestampMs / waveformDurationMs) * waveformWidth : 0
    
    x: xPosition
    width: 2  // Marker line width
    height: parent.height
    
    // Marker line
    Rectangle {
        id: markerLine
        anchors.fill: parent
        color: markerColor
        opacity: important ? 1.0 : 0.7
        
        // Subtle shadow for important markers
        Rectangle {
            visible: important
            anchors.fill: parent
            anchors.margins: -1
            color: "transparent"
            border.color: markerColor
            border.width: 1
            opacity: 0.3
            z: -1
        }
    }
    
    // Flag at top (for important markers)
    Rectangle {
        id: flag
        visible: important
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.leftMargin: 2
        width: 16
        height: 16
        color: markerColor
        radius: 2
        
        Label {
            anchors.centerIn: parent
            text: "⭐"
            font.pixelSize: 10
            color: "white"
        }
    }
    
    // Hit area for mouse events
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        anchors.leftMargin: -4  // Expand hit area
        anchors.rightMargin: -4
        hoverEnabled: true
        acceptedButtons: Qt.LeftButton | Qt.RightButton
        
        onClicked: function(mouse) {
            if (mouse.button === Qt.LeftButton) {
                root.clicked(timestampMs)
            } else if (mouse.button === Qt.RightButton) {
                root.rightClicked(timestampMs)
            }
        }
        
        onDoubleClicked: function(mouse) {
            if (mouse.button === Qt.LeftButton) {
                root.doubleClicked(timestampMs)
            }
        }
        
        // Change appearance on hover
        onEntered: {
            markerLine.opacity = 1.0
            markerLine.width = 3
            tooltip.visible = true
        }
        
        onExited: {
            markerLine.opacity = important ? 1.0 : 0.7
            markerLine.width = 2
            tooltip.visible = false
        }
    }
    
    // Tooltip
    Rectangle {
        id: tooltip
        visible: false
        anchors.bottom: parent.top
        anchors.bottomMargin: 5
        anchors.horizontalCenter: parent.horizontalCenter
        width: tooltipContent.width + 16
        height: tooltipContent.height + 12
        color: Theme.backgroundDark
        border.color: markerColor
        border.width: 1
        radius: Theme.radiusSmall
        opacity: 0.95
        z: 100
        
        // Arrow pointing down
        Canvas {
            id: arrow
            anchors.top: parent.bottom
            anchors.horizontalCenter: parent.horizontalCenter
            width: 10
            height: 5
            
            onPaint: {
                var ctx = getContext("2d")
                ctx.clearRect(0, 0, width, height)
                ctx.fillStyle = Theme.backgroundDark
                ctx.beginPath()
                ctx.moveTo(0, 0)
                ctx.lineTo(width / 2, height)
                ctx.lineTo(width, 0)
                ctx.closePath()
                ctx.fill()
            }
        }
        
        Column {
            id: tooltipContent
            anchors.centerIn: parent
            spacing: 4
            
            Label {
                text: formatTime(timestampMs)
                font.pixelSize: Theme.fontSizeSmall
                font.bold: true
                color: markerColor
            }
            
            Label {
                visible: category !== ""
                text: "[" + category + "]"
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.textMuted
            }
            
            Label {
                text: root.text
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.textColor
                wrapMode: Text.WordWrap
                maximumLineCount: 3
                elide: Text.ElideRight
            }
        }
    }
    
    // Helper function to format timestamp
    function formatTime(ms) {
        var totalSeconds = ms / 1000.0
        var minutes = Math.floor(totalSeconds / 60)
        var seconds = Math.floor(totalSeconds % 60)
        var milliseconds = Math.floor((totalSeconds % 1) * 1000)
        
        return String(minutes).padStart(2, '0') + ":" + 
               String(seconds).padStart(2, '0') + "." +
               String(milliseconds).padStart(3, '0')
    }
}
