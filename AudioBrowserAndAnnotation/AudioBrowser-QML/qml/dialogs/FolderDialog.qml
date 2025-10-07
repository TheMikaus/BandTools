import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import QtQuick.Dialogs
import "../components"
import "../styles"

/**
 * FolderDialog - Directory selection dialog
 * 
 * A wrapper around FileDialog configured for selecting directories.
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
    title: "Select Audio Directory"
    fileMode: FileDialog.OpenFile  // Will be overridden by selectFolder
    selectFolder: true  // Qt 6 way to select folders
    
    // Handle folder selection
    onAccepted: {
        // Extract directory from selected folder URL
        // When in OpenDirectory mode, selectedFile contains the selected directory
        var folderPath = selectedFile.toString()
        
        // Remove file:// prefix if present
        if (folderPath.startsWith("file://")) {
            folderPath = folderPath.substring(7)
        }
        
        // On Windows, handle the extra slash issue
        // file:///C:/path becomes /C:/path, should be C:/path
        if (folderPath.length > 2 && folderPath.charAt(0) === '/' && folderPath.charAt(2) === ':') {
            folderPath = folderPath.substring(1)
        }
        
        console.log("FolderDialog: Selected folder:", folderPath)
        folderSelected(folderPath)
    }
}
