import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import "../styles"

Dialog {
    id: exportDialog
    
    title: "Export Annotations"
    modal: true
    width: 500
    height: 350
    
    property string currentFile: ""
    property int annotationCount: 0
    property var annotationManager: null
    property var fileManager: null
    
    // Update annotation count when dialog opens
    onOpened: {
        if (annotationManager) {
            annotationCount = annotationManager.getAnnotationCount()
            updatePreview()
        }
    }
    
    function updatePreview() {
        let fileName = currentFile ? currentFile.split('/').pop().split('\\').pop() : "untitled"
        let baseName = fileName.replace(/\.[^/.]+$/, "")
        
        let extension = ".txt"
        if (formatComboBox.currentIndex === 1) {
            extension = ".csv"
        } else if (formatComboBox.currentIndex === 2) {
            extension = ".md"
        }
        
        fileNameField.text = baseName + "_annotations" + extension
    }
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 15
        
        // Status section
        GroupBox {
            Layout.fillWidth: true
            title: "Current File"
            
            ColumnLayout {
                anchors.fill: parent
                spacing: 5
                
                Label {
                    text: currentFile ? currentFile.split('/').pop().split('\\').pop() : "No file selected"
                    font.bold: true
                    elide: Text.ElideMiddle
                    Layout.fillWidth: true
                }
                
                Label {
                    text: annotationCount + " annotation" + (annotationCount !== 1 ? "s" : "")
                    color: Theme.textColor
                    opacity: 0.7
                }
            }
        }
        
        // Export format section
        GroupBox {
            Layout.fillWidth: true
            title: "Export Format"
            
            ColumnLayout {
                anchors.fill: parent
                spacing: 10
                
                ComboBox {
                    id: formatComboBox
                    Layout.fillWidth: true
                    
                    model: [
                        "Plain Text (.txt)",
                        "CSV (.csv)",
                        "Markdown (.md)"
                    ]
                    
                    onCurrentIndexChanged: updatePreview()
                }
                
                Label {
                    text: getFormatDescription()
                    font.pixelSize: 11
                    color: Theme.textColor
                    opacity: 0.6
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }
            }
        }
        
        // File name section
        GroupBox {
            Layout.fillWidth: true
            title: "Export File Name"
            
            RowLayout {
                anchors.fill: parent
                spacing: 10
                
                TextField {
                    id: fileNameField
                    Layout.fillWidth: true
                    placeholderText: "filename_annotations.txt"
                    selectByMouse: true
                }
                
                Button {
                    text: "Browse..."
                    onClicked: saveFileDialog.open()
                }
            }
        }
        
        // Spacer
        Item {
            Layout.fillHeight: true
        }
        
        // Button row
        RowLayout {
            Layout.fillWidth: true
            spacing: 10
            
            Item {
                Layout.fillWidth: true
            }
            
            Button {
                text: "Cancel"
                onClicked: exportDialog.reject()
            }
            
            Button {
                text: "Export"
                highlighted: true
                enabled: annotationCount > 0 && fileNameField.text.length > 0
                
                onClicked: {
                    performExport()
                }
            }
        }
    }
    
    // File save dialog
    FileDialog {
        id: saveFileDialog
        fileMode: FileDialog.SaveFile
        currentFolder: fileManager ? fileManager.rootDirectory : ""
        
        nameFilters: {
            if (formatComboBox.currentIndex === 1) {
                return ["CSV files (*.csv)", "All files (*)"]
            } else if (formatComboBox.currentIndex === 2) {
                return ["Markdown files (*.md)", "All files (*)"]
            } else {
                return ["Text files (*.txt)", "All files (*)"]
            }
        }
        
        onAccepted: {
            let path = selectedFile.toString()
            // Remove file:// prefix if present
            if (path.startsWith("file://")) {
                path = path.substring(7)
            }
            fileNameField.text = path
        }
    }
    
    function getFormatDescription() {
        switch (formatComboBox.currentIndex) {
            case 0:
                return "Plain text format with timestamps, categories, and annotation text. Easy to read and share."
            case 1:
                return "Comma-separated values format. Can be opened in spreadsheet applications like Excel."
            case 2:
                return "Markdown format with headers and formatting. Great for documentation and GitHub."
            default:
                return ""
        }
    }
    
    function performExport() {
        if (!annotationManager) {
            console.error("AnnotationManager not available")
            return
        }
        
        if (annotationCount === 0) {
            console.error("No annotations to export")
            return
        }
        
        let fileName = fileNameField.text
        if (!fileName) {
            console.error("No file name specified")
            return
        }
        
        // Determine export format
        let format = "text"
        if (formatComboBox.currentIndex === 1) {
            format = "csv"
        } else if (formatComboBox.currentIndex === 2) {
            format = "markdown"
        }
        
        // Build full path
        let exportPath = fileName
        
        // If it's just a filename (no path), use current directory
        if (!fileName.includes('/') && !fileName.includes('\\')) {
            let currentDir = fileManager ? fileManager.rootDirectory : ""
            if (currentDir) {
                exportPath = currentDir + "/" + fileName
            }
        }
        
        // Perform export
        let success = annotationManager.exportAnnotations(exportPath, format)
        
        if (success) {
            console.log("Annotations exported successfully to:", exportPath)
            exportDialog.accept()
            
            // Show success message
            successDialog.open()
        } else {
            console.error("Failed to export annotations")
        }
    }
    
    // Success dialog
    Dialog {
        id: successDialog
        title: "Export Successful"
        modal: true
        standardButtons: Dialog.Ok
        
        anchors.centerIn: parent
        
        Label {
            text: "Annotations exported successfully!"
        }
    }
}
