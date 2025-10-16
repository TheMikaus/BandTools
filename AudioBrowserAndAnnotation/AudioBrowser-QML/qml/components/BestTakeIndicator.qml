import QtQuick
import QtQuick.Controls.Basic
import "../styles"

/**
 * BestTakeIndicator Component
 * 
 * Visual indicator showing "Best Take" status with a gold star icon.
 * 
 * Properties:
 * - marked: Whether this file is marked as a best take
 * - enabled: Whether the indicator is interactive
 * 
 * Signals:
 * - clicked(): Emitted when the indicator is clicked
 */
Item {
    id: bestTakeIndicator
    
    // ========== Properties ==========
    
    property bool marked: false
    property bool enabled: true
    
    // ========== Sizing ==========
    
    implicitWidth: 24
    implicitHeight: 24
    
    // ========== Signals ==========
    
    signal clicked()
    
    // ========== Visual Components ==========
    
    // Star icon (gold/gray depending on marked status)
    Canvas {
        id: starCanvas
        anchors.fill: parent
        visible: bestTakeIndicator.marked  // Only show when marked
        
        onPaint: {
            var ctx = getContext("2d");
            ctx.clearRect(0, 0, width, height);
            
            // Calculate star points
            var centerX = width / 2;
            var centerY = height / 2;
            var outerRadius = Math.min(width, height) / 2 - 2;
            var innerRadius = outerRadius * 0.4;
            var spikes = 5;
            
            // Gold gradient for marked
            var gradient = ctx.createLinearGradient(0, 0, 0, height);
            gradient.addColorStop(0, "#FFD700");  // Gold
            gradient.addColorStop(1, "#FFA500");  // Orange
            ctx.fillStyle = gradient;
            
            // Draw star
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
            ctx.fill();
            
            // Draw border
            ctx.strokeStyle = "#B8860B";
            ctx.lineWidth = 1;
            ctx.stroke();
        }
    }
    
    // Subtle outline when unmarked
    Canvas {
        id: outlineCanvas
        anchors.fill: parent
        visible: !bestTakeIndicator.marked && mouseArea.containsMouse  // Only show on hover when unmarked
        
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
            
            // Light gray dotted outline
            ctx.strokeStyle = Theme.borderColor;
            ctx.lineWidth = 1;
            ctx.setLineDash([2, 2]);
            ctx.stroke();
        }
    }
    
    // Tooltip
    ToolTip {
        visible: mouseArea.containsMouse
        text: bestTakeIndicator.marked ? "Best Take (click to unmark)" : "Mark as Best Take"
        delay: 500
    }
    
    // Mouse area for interaction
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: bestTakeIndicator.enabled
        cursorShape: bestTakeIndicator.enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
        enabled: bestTakeIndicator.enabled
        
        onClicked: {
            if (bestTakeIndicator.enabled) {
                bestTakeIndicator.clicked();
            }
        }
        
        onEntered: {
            if (bestTakeIndicator.enabled) {
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
