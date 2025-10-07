import QtQuick
import QtQuick.Controls.Basic
import "../styles"

/**
 * ClipMarker Component
 * 
 * Visual representation of an audio clip on the waveform.
 * Shows start and end boundaries with a highlighted region between them.
 * 
 * Features:
 * - Start and end boundary markers
 * - Highlighted region between markers
 * - Interactive tooltips on hover
 * - Click to select clip
 * - Double-click to edit clip
 * - Theme-aware styling
 */
Item {
    id: root
    
    // ========== Properties ==========
    
    // Clip data
    property int startMs: 0
    property int endMs: 0
    property string clipName: ""
    property string clipNotes: ""
    property int clipIndex: 0
    
    // Waveform reference for positioning
    property real waveformWidth: 0
    property int waveformDuration: 0  // Duration in milliseconds
    
    // Visual properties
    property color regionColor: Theme.accentWarning
    property real regionOpacity: 0.2
    property color markerColor: Theme.accentWarning
    property int markerWidth: 3
    
    // Interaction state
    property bool isSelected: false
    property bool isHovered: false
    
    // ========== Signals ==========
    
    signal clicked(int index)
    signal doubleClicked(int index)
    signal startDragged(int index, int newStartMs)
    signal endDragged(int index, int newEndMs)
    
    // ========== Computed Properties ==========
    
    // Position calculations
    readonly property real startX: waveformDuration > 0 
        ? (startMs / waveformDuration) * waveformWidth 
        : 0
    readonly property real endX: waveformDuration > 0 
        ? (endMs / waveformDuration) * waveformWidth 
        : 0
    readonly property real regionWidth: endX - startX
    
    // Format timestamp as MM:SS.mmm
    function formatTime(ms) {
        const totalSeconds = Math.floor(ms / 1000);
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        const milliseconds = ms % 1000;
        return minutes.toString().padStart(2, '0') + ":" +
               seconds.toString().padStart(2, '0') + "." +
               milliseconds.toString().padStart(3, '0');
    }
    
    // ========== Visual Elements ==========
    
    // Highlighted region between markers
    Rectangle {
        id: clipRegion
        x: startX
        width: regionWidth
        height: parent.height
        color: regionColor
        opacity: isSelected ? regionOpacity + 0.1 : regionOpacity
        
        Behavior on opacity {
            NumberAnimation { duration: Theme.durationFast }
        }
        
        // Region mouse area for selection
        MouseArea {
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            
            onEntered: isHovered = true
            onExited: isHovered = false
            onClicked: root.clicked(clipIndex)
            onDoubleClicked: root.doubleClicked(clipIndex)
        }
        
        // Clip name label (visible when region is wide enough)
        Label {
            anchors.centerIn: parent
            text: clipName
            font.pixelSize: Theme.fontSizeSmall
            font.bold: true
            color: Theme.textColor
            visible: parent.width > 60 && clipName !== ""
            opacity: 0.8
            
            background: Rectangle {
                color: Theme.backgroundColor
                opacity: 0.7
                radius: 3
            }
            
            padding: 4
        }
    }
    
    // Start marker
    Item {
        id: startMarker
        x: startX - markerWidth / 2
        width: markerWidth * 3  // Wider hit area
        height: parent.height
        
        // Marker line
        Rectangle {
            anchors.horizontalCenter: parent.horizontalCenter
            width: markerWidth
            height: parent.height
            color: markerColor
            opacity: isSelected || startMouseArea.containsMouse ? 1.0 : 0.8
            
            Behavior on opacity {
                NumberAnimation { duration: Theme.durationFast }
            }
        }
        
        // Start label flag
        Rectangle {
            anchors.top: parent.top
            anchors.horizontalCenter: parent.horizontalCenter
            width: 30
            height: 18
            color: markerColor
            radius: 3
            
            Label {
                anchors.centerIn: parent
                text: "["
                font.pixelSize: Theme.fontSizeSmall
                font.bold: true
                color: "white"
            }
        }
        
        // Mouse area for interaction
        MouseArea {
            id: startMouseArea
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.SizeHorCursor
            
            onEntered: isHovered = true
            onExited: isHovered = false
            
            // Tooltip
            ToolTip {
                visible: startMouseArea.containsMouse
                text: "Start: " + formatTime(startMs) + 
                      (clipName !== "" ? "\nClip: " + clipName : "")
                delay: 500
            }
        }
    }
    
    // End marker
    Item {
        id: endMarker
        x: endX - markerWidth / 2
        width: markerWidth * 3  // Wider hit area
        height: parent.height
        
        // Marker line
        Rectangle {
            anchors.horizontalCenter: parent.horizontalCenter
            width: markerWidth
            height: parent.height
            color: markerColor
            opacity: isSelected || endMouseArea.containsMouse ? 1.0 : 0.8
            
            Behavior on opacity {
                NumberAnimation { duration: Theme.durationFast }
            }
        }
        
        // End label flag
        Rectangle {
            anchors.top: parent.top
            anchors.horizontalCenter: parent.horizontalCenter
            width: 30
            height: 18
            color: markerColor
            radius: 3
            
            Label {
                anchors.centerIn: parent
                text: "]"
                font.pixelSize: Theme.fontSizeSmall
                font.bold: true
                color: "white"
            }
        }
        
        // Mouse area for interaction
        MouseArea {
            id: endMouseArea
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.SizeHorCursor
            
            onEntered: isHovered = true
            onExited: isHovered = false
            
            // Tooltip
            ToolTip {
                visible: endMouseArea.containsMouse
                text: "End: " + formatTime(endMs) +
                      "\nDuration: " + formatTime(endMs - startMs) +
                      (clipName !== "" ? "\nClip: " + clipName : "")
                delay: 500
            }
        }
    }
    
    // Selection indicator border (when selected)
    Rectangle {
        x: startX
        width: regionWidth
        height: parent.height
        color: "transparent"
        border.color: markerColor
        border.width: isSelected ? 2 : 0
        opacity: 0.6
        visible: isSelected
    }
}
