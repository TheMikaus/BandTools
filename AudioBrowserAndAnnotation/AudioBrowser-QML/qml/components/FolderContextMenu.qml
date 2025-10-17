import QtQuick
import QtQuick.Controls.Basic
import "../styles"

/**
 * FolderContextMenu Component
 * 
 * Right-click context menu for folder operations.
 * 
 * Properties:
 * - folderPath: Path to the folder
 * - folderName: Name of the folder
 * - fingerprintEngine: Reference to fingerprint engine
 * - waveformEngine: Reference to waveform engine
 * - fileManager: Reference to file manager
 * 
 * Actions:
 * - Generate Fingerprint
 * - Mark as reference folder
 * - Mark as ignore fingerprints
 * - Generate waveforms
 */
Menu {
    id: folderContextMenu
    
    // ========== Properties ==========
    
    property string folderPath: ""
    property string folderName: ""
    property var fingerprintEngine: null
    property var waveformEngine: null
    property var fileManager: null
    
    // ========== Styling ==========
    
    background: Rectangle {
        implicitWidth: 240
        color: Theme.backgroundColor
        border.color: Theme.borderColor
        border.width: 1
        radius: Theme.radiusSmall
    }
    
    // ========== Menu Items ==========
    
    MenuItem {
        text: "🔍 Generate Fingerprints"
        enabled: folderPath !== ""
        
        background: Rectangle {
            implicitWidth: 220
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
            folderContextMenu.generateFingerprintsRequested();
        }
    }
    
    MenuSeparator {
        background: Rectangle {
            implicitHeight: 1
            color: Theme.borderColor
        }
    }
    
    MenuItem {
        text: fingerprintEngine && fingerprintEngine.isFolderReference(folderPath) ? 
              "⭐ Unmark Reference Folder" : "⭐ Mark as Reference Folder"
        enabled: folderPath !== ""
        
        background: Rectangle {
            implicitWidth: 220
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
            if (fingerprintEngine && folderPath) {
                fingerprintEngine.toggleFolderReference(folderPath);
            }
        }
    }
    
    MenuItem {
        text: fingerprintEngine && fingerprintEngine.isFolderIgnored(folderPath) ?
              "🚫 Unmark Ignore Fingerprints" : "🚫 Mark as Ignore Fingerprints"
        enabled: folderPath !== ""
        
        background: Rectangle {
            implicitWidth: 220
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
            if (fingerprintEngine && folderPath) {
                fingerprintEngine.toggleFolderIgnore(folderPath);
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
        text: "📊 Generate Waveforms"
        enabled: folderPath !== ""
        
        background: Rectangle {
            implicitWidth: 220
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
            folderContextMenu.generateWaveformsRequested();
        }
    }
    
    // ========== Signals ==========
    
    signal generateFingerprintsRequested()
    signal generateWaveformsRequested()
}
