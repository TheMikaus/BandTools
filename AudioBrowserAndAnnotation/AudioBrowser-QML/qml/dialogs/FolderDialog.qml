import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import QtQuick.Dialogs
import "../components"
import "../styles"

/**
 * FolderDialog - Directory selection dialog
 * 
 * A simple dialog wrapper around the FileDialog for selecting directories.
 * Provides a consistent interface for directory selection across the app.
 * 
 * Signals:
 *   - folderSelected(string folder): Emitted when a folder is selected
 * 
 * Usage:
 *   FolderDialog {
 *       id: folderDialog
 *       onFolderSelected: function(folder) {
 *           console.log("Selected:", folder)
 *       }
 *   }
 *   
 *   Button {
 *       onClicked: folderDialog.open()
 *   }
 */
FileDialog {
    id: dialog
    
    // Signals
    signal folderSelected(string folder)
    
    // Dialog configuration
    title: "Select Directory"
    fileMode: FileDialog.SaveFile  // Workaround: use SaveFile mode to get directory picker
    
    // Custom current folder property for convenience
    property string currentFolder: ""
    
    // Handle folder selection
    onAccepted: {
        // Extract directory from selected file URL
        var folderPath = selectedFile.toString()
        
        // Remove file:// prefix if present
        if (folderPath.startsWith("file://")) {
            folderPath = folderPath.substring(7)
        }
        
        // Get parent directory
        var lastSlash = folderPath.lastIndexOf("/")
        if (lastSlash > 0) {
            folderPath = folderPath.substring(0, lastSlash)
        }
        
        folderSelected(folderPath)
    }
}
