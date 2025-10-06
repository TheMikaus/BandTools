import QtQuick
import QtQuick.Controls
import "../styles"

/**
 * FileContextMenu Component
 * 
 * Right-click context menu for file operations.
 * 
 * Properties:
 * - filePath: Path to the file
 * - fileName: Name of the file
 * - audioEngine: Reference to audio engine
 * - annotationManager: Reference to annotation manager
 * - clipManager: Reference to clip manager
 * 
 * Actions:
 * - Play file
 * - Add annotation at current position
 * - Create clip from current position
 * - Show in file explorer
 * - Copy file path
 * - File properties
 */
Menu {
    id: fileContextMenu
    
    // ========== Properties ==========
    
    property string filePath: ""
    property string fileName: ""
    property var audioEngine: null
    property var annotationManager: null
    property var clipManager: null
    property var fileManager: null
    
    // ========== Styling ==========
    
    background: Rectangle {
        implicitWidth: 220
        color: Theme.backgroundColor
        border.color: Theme.borderColor
        border.width: 1
        radius: Theme.radiusSmall
    }
    
    // ========== Menu Items ==========
    
    MenuItem {
        text: "▶ Play"
        enabled: filePath !== ""
        
        background: Rectangle {
            implicitWidth: 200
            implicitHeight: 30
            color: parent.hovered ? Theme.backgroundLight : "transparent"
        }
        
        contentItem: Text {
            text: parent.text
            font.pixelSize: Theme.fontSizeNormal
            color: parent.enabled ? Theme.foregroundColor : Theme.textMuted
            leftPadding: 10
            verticalAlignment: Text.AlignVCenter
        }
        
        onTriggered: {
            if (audioEngine && filePath) {
                audioEngine.loadFile(filePath);
                audioEngine.play();
            }
        }
    }
    
    MenuSeparator {
        background: Rectangle {
            implicitHeight: 1
            color: Theme.borderColor
        }
    }
    
    MenuItem {
        text: "📝 Add Annotation..."
        enabled: filePath !== ""
        
        background: Rectangle {
            implicitWidth: 200
            implicitHeight: 30
            color: parent.hovered ? Theme.backgroundLight : "transparent"
        }
        
        contentItem: Text {
            text: parent.text
            font.pixelSize: Theme.fontSizeNormal
            color: parent.enabled ? Theme.foregroundColor : Theme.textMuted
            leftPadding: 10
            verticalAlignment: Text.AlignVCenter
        }
        
        onTriggered: {
            // Switch to Annotations tab
            // This will be handled by the caller
            fileContextMenu.annotationRequested();
        }
    }
    
    MenuItem {
        text: "✂ Create Clip..."
        enabled: filePath !== ""
        
        background: Rectangle {
            implicitWidth: 200
            implicitHeight: 30
            color: parent.hovered ? Theme.backgroundLight : "transparent"
        }
        
        contentItem: Text {
            text: parent.text
            font.pixelSize: Theme.fontSizeNormal
            color: parent.enabled ? Theme.foregroundColor : Theme.textMuted
            leftPadding: 10
            verticalAlignment: Text.AlignVCenter
        }
        
        onTriggered: {
            // Switch to Clips tab
            // This will be handled by the caller
            fileContextMenu.clipRequested();
        }
    }
    
    MenuSeparator {
        background: Rectangle {
            implicitHeight: 1
            color: Theme.borderColor
        }
    }
    
    MenuItem {
        text: "📁 Show in Explorer"
        enabled: filePath !== ""
        
        background: Rectangle {
            implicitWidth: 200
            implicitHeight: 30
            color: parent.hovered ? Theme.backgroundLight : "transparent"
        }
        
        contentItem: Text {
            text: parent.text
            font.pixelSize: Theme.fontSizeNormal
            color: parent.enabled ? Theme.foregroundColor : Theme.textMuted
            leftPadding: 10
            verticalAlignment: Text.AlignVCenter
        }
        
        onTriggered: {
            if (fileManager && filePath) {
                fileManager.openInFileManager(filePath);
            }
        }
    }
    
    MenuItem {
        text: "📋 Copy Path"
        enabled: filePath !== ""
        
        background: Rectangle {
            implicitWidth: 200
            implicitHeight: 30
            color: parent.hovered ? Theme.backgroundLight : "transparent"
        }
        
        contentItem: Text {
            text: parent.text
            font.pixelSize: Theme.fontSizeNormal
            color: parent.enabled ? Theme.foregroundColor : Theme.textMuted
            leftPadding: 10
            verticalAlignment: Text.AlignVCenter
        }
        
        onTriggered: {
            if (filePath) {
                // Copy to clipboard
                fileContextMenu.copyToClipboard(filePath);
            }
        }
    }
    
    MenuSeparator {
        background: Rectangle {
            implicitHeight: 1
            color: Theme.borderColor
        }
    }
    
    MenuItem {
        text: "ℹ Properties"
        enabled: filePath !== ""
        
        background: Rectangle {
            implicitWidth: 200
            implicitHeight: 30
            color: parent.hovered ? Theme.backgroundLight : "transparent"
        }
        
        contentItem: Text {
            text: parent.text
            font.pixelSize: Theme.fontSizeNormal
            color: parent.enabled ? Theme.foregroundColor : Theme.textMuted
            leftPadding: 10
            verticalAlignment: Text.AlignVCenter
        }
        
        onTriggered: {
            fileContextMenu.propertiesRequested();
        }
    }
    
    // ========== Signals ==========
    
    signal annotationRequested()
    signal clipRequested()
    signal propertiesRequested()
    
    // ========== Helper Functions ==========
    
    function copyToClipboard(text) {
        // Use a temporary TextEdit to copy text
        var tempTextEdit = Qt.createQmlObject(
            'import QtQuick; TextEdit { visible: false }',
            fileContextMenu
        );
        tempTextEdit.text = text;
        tempTextEdit.selectAll();
        tempTextEdit.copy();
        tempTextEdit.destroy();
    }
}
