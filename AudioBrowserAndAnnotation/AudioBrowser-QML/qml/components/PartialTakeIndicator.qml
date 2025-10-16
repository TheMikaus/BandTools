import QtQuick
import QtQuick.Controls.Basic
import "../styles"

/**
 * PartialTakeIndicator Component
 * 
 * Visual indicator showing "Partial Take" status with a half-filled star icon.
 * 
 * Properties:
 * - marked: Whether this file is marked as a partial take
 * - enabled: Whether the indicator is interactive
 * 
 * Signals:
 * - clicked(): Emitted when the indicator is clicked
 */
Item {
    id: partialTakeIndicator
    
    // ========== Properties ==========
    
    property bool marked: false
    property bool enabled: true
    
    // ========== Sizing ==========
    
    implicitWidth: 24
    implicitHeight: 24
    
    // ========== Signals ==========
    
    signal clicked()
    
    // ========== Visual Components ==========
    
    // Half-filled star icon (blue/gray depending on marked status)
    Canvas {
        id: starCanvas
        anchors.fill: parent
        visible: partialTakeIndicator.marked  // Only show when marked
        
        onPaint: {
            var ctx = getContext("2d");
            ctx.clearRect(0, 0, width, height);
            
            // Calculate star points
            var centerX = width / 2;
            var centerY = height / 2;
            var outerRadius = Math.min(width, height) / 2 - 2;
            var innerRadius = outerRadius * 0.4;
            var spikes = 5;
            
            // Draw star outline first
            ctx.beginPath();
            for (var i = 0; i < spikes * 2; i++) {
                var radius = (i % 2 === 0) ? outerRadius : innerRadius;
                var angle = (i * Math.PI) / spikes - Math.PI / 2;
                var x = centerX + Math.cos(angle) * radius;
                var y = centerY + Math.sin(angle) * radius;
                
                if (i === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            }
            ctx.closePath();
            
            // Fill with light color first
            ctx.fillStyle = "#E0E0E0";
            ctx.fill();
            
            // Save context state
            ctx.save();
            
            // Clip to left half
            ctx.beginPath();
            ctx.rect(0, 0, width / 2, height);
            ctx.clip();
            
            // Draw star again for left half with different color
            ctx.beginPath();
            for (var j = 0; j < spikes * 2; j++) {
                var radius2 = (j % 2 === 0) ? outerRadius : innerRadius;
                var angle2 = (j * Math.PI) / spikes - Math.PI / 2;
                var x2 = centerX + Math.cos(angle2) * radius2;
                var y2 = centerY + Math.sin(angle2) * radius2;
                
                if (j === 0) {
                    ctx.moveTo(x2, y2);
                } else {
                    ctx.lineTo(x2, y2);
                }
            }
            ctx.closePath();
            
            // Blue gradient for left half
            var gradient = ctx.createLinearGradient(0, 0, 0, height);
            gradient.addColorStop(0, "#4A90E2");  // Light blue
            gradient.addColorStop(1, "#2E5C8A");  // Dark blue
            ctx.fillStyle = gradient;
            ctx.fill();
            
            // Restore context
            ctx.restore();
            
            // Draw border
            ctx.beginPath();
            for (var k = 0; k < spikes * 2; k++) {
                var radius3 = (k % 2 === 0) ? outerRadius : innerRadius;
                var angle3 = (k * Math.PI) / spikes - Math.PI / 2;
                var x3 = centerX + Math.cos(angle3) * radius3;
                var y3 = centerY + Math.sin(angle3) * radius3;
                
                if (k === 0) {
                    ctx.moveTo(x3, y3);
                } else {
                    ctx.lineTo(x3, y3);
                }
            }
            ctx.closePath();
            ctx.strokeStyle = "#2E5C8A";
            ctx.lineWidth = 1;
            ctx.stroke();
        }
    }
    
    // Subtle outline when unmarked
    Canvas {
        id: outlineCanvas
        anchors.fill: parent
        visible: !partialTakeIndicator.marked && mouseArea.containsMouse  // Only show on hover when unmarked
        
        onPaint: {
            var ctx = getContext("2d");
            ctx.clearRect(0, 0, width, height);
            
            // Calculate star points
            var centerX = width / 2;
            var centerY = height / 2;
            var outerRadius = Math.min(width, height) / 2 - 2;
            var innerRadius = outerRadius * 0.4;
            var spikes = 5;
            
            // Draw star outline only
            ctx.beginPath();
            for (var i = 0; i < spikes * 2; i++) {
                var radius = (i % 2 === 0) ? outerRadius : innerRadius;
                var angle = (i * Math.PI) / spikes - Math.PI / 2;
                var x = centerX + Math.cos(angle) * radius;
                var y = centerY + Math.sin(angle) * radius;
                
                if (i === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            }
            ctx.closePath();
            
            // Draw half-fill indication with dashed line
            ctx.moveTo(centerX, 0);
            ctx.lineTo(centerX, height);
            
            // Light gray dashed outline
            ctx.strokeStyle = Theme.borderColor;
            ctx.lineWidth = 1;
            ctx.setLineDash([2, 2]);
            ctx.stroke();
        }
    }
    
    // Tooltip
    ToolTip {
        visible: mouseArea.containsMouse
        text: partialTakeIndicator.marked ? "Partial Take (click to unmark)" : "Mark as Partial Take"
        delay: 500
    }
    
    // Mouse area for interaction
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: partialTakeIndicator.enabled
        cursorShape: partialTakeIndicator.enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
        enabled: partialTakeIndicator.enabled
        
        onClicked: {
            if (partialTakeIndicator.enabled) {
                partialTakeIndicator.clicked();
            }
        }
        
        onEntered: {
            if (partialTakeIndicator.enabled) {
                starCanvas.opacity = 0.8;
                outlineCanvas.requestPaint();
            }
        }
        
        onExited: {
            starCanvas.opacity = 1.0;
            outlineCanvas.requestPaint();
        }
    }
    
    // Redraw canvas when marked status changes
    onMarkedChanged: {
        starCanvas.requestPaint();
        outlineCanvas.requestPaint();
    }
    
    Component.onCompleted: {
        starCanvas.requestPaint();
        outlineCanvas.requestPaint();
    }
}
