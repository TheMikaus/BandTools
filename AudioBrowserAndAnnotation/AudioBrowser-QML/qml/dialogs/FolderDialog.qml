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
 * NOTE: Qt Quick Dialogs FileDialog in Qt6 doesn't have a native folder selection mode.
 * This implementation asks users to navigate to a folder and select any file in it,
 * then uses the parent directory of that file.
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
FolderDialog {
    id: dialog
    
    // Signals
    signal folderSelected(string folder)
    
    // Dialog configuration
    title: "Navigate to Audio Directory"
    
    // Handle folder selection
    onAccepted: {
        var folderPath = ""
        
        // No file selected, use current folder
        folderPath = currentFolder.toString()
        
        // Remove file:// prefix if present
        if (folderPath.startsWith("file://")) {
            folderPath = folderPath.substring(7)
        }
        
        // On Windows, handle the extra slash issue
        if (folderPath.length > 2 && folderPath.charAt(0) === '/' && folderPath.charAt(2) === ':') {
            folderPath = folderPath.substring(1)
        }
        
        console.log("FolderDialog: Selected folder:", folderPath)
        folderSelected(folderPath)
    }
}
