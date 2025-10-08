import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import QtQuick.Dialogs
import "../styles"

/**
 * ExportBestTakesDialog Component
 * 
 * Dialog for exporting all Best Take files as a package.
 * Supports ZIP archive and folder export with optional format conversion.
 */
Dialog {
    id: exportDialog
    title: "Export Best Takes Package"
    modal: true
    standardButtons: Dialog.Ok | Dialog.Cancel
    
    x: (parent.width - width) / 2
    y: (parent.height - height) / 2
    width: 550
    height: 450
    
    background: Rectangle {
        color: Theme.backgroundColor
        border.color: Theme.borderColor
        border.width: 1
        radius: Theme.radiusSmall
    }
    
    // Properties
    property int bestTakesCount: 0
    property string destinationPath: ""
    property string exportFormat: "folder"  // "folder" or "zip"
    property bool convertToMP3: false
    property bool includeMetadata: true
    
    // Update count when dialog opens
    onAboutToShow: {
        bestTakesCount = fileManager.getBestTakesCount()
        updateInfo()
    }
    
    // Handle OK button
    onAccepted: {
        performExport()
    }
    
    function updateInfo() {
        var info = "Found " + bestTakesCount + " file(s) marked as Best Take"
        if (bestTakesCount === 0) {
            info += "\n\nPlease mark files as Best Take before exporting."
        }
        infoLabel.text = info
    }
    
    function performExport() {
        if (bestTakesCount === 0) {
            console.log("No best takes to export")
            return
        }
        
        if (destinationPath === "") {
            console.log("No destination path selected")
            return
        }
        
        // Get list of best takes
        var bestTakes = fileManager.getBestTakes()
        console.log("Exporting " + bestTakes.length + " best takes to:", destinationPath)
        console.log("Export format:", exportFormat)
        console.log("Convert to MP3:", convertToMP3)
        console.log("Include metadata:", includeMetadata)
        
        // TODO: Implement actual export via batch operations or new export manager
        // For now, we'll show a progress dialog
        progressDialog.open()
        progressDialog.performExport(bestTakes, destinationPath, exportFormat, convertToMP3, includeMetadata)
    }
    
    ScrollView {
        anchors.fill: parent
        contentWidth: availableWidth
        
        ColumnLayout {
            width: parent.width - 20
            spacing: Theme.spacingLarge
            
            // Info Section
            Label {
                id: infoLabel
                text: "Loading..."
                font.pixelSize: Theme.fontSizeNormal
                color: Theme.textColor
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
            }
            
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 1
                color: Theme.borderColor
            }
            
            // Export Format Section
            GroupBox {
                Layout.fillWidth: true
                title: "Export Format"
                
                background: Rectangle {
                    color: Theme.backgroundLight
                    border.color: Theme.borderColor
                    border.width: 1
                    radius: Theme.radiusSmall
                }
                
                label: Label {
                    text: parent.title
                    font.bold: true
                    font.pixelSize: Theme.fontSizeLarge
                    color: Theme.textColor
                    leftPadding: Theme.spacingSmall
                }
                
                ColumnLayout {
                    width: parent.width
                    spacing: Theme.spacingNormal
                    
                    RadioButton {
                        id: folderRadio
                        text: "Export to Folder"
                        checked: exportFormat === "folder"
                        
                        onCheckedChanged: {
                            if (checked) {
                                exportFormat = "folder"
                            }
                        }
                        
                        contentItem: Text {
                            text: parent.text
                            font.pixelSize: Theme.fontSizeNormal
                            color: Theme.textColor
                            leftPadding: parent.indicator.width + Theme.spacingSmall
                            verticalAlignment: Text.AlignVCenter
                        }
                        
                        indicator: Rectangle {
                            implicitWidth: 20
                            implicitHeight: 20
                            radius: 10
                            border.color: Theme.borderColor
                            border.width: 1
                            color: "transparent"
                            
                            Rectangle {
                                anchors.centerIn: parent
                                width: 12
                                height: 12
                                radius: 6
                                color: Theme.accentColor
                                visible: folderRadio.checked
                            }
                        }
                    }
                    
                    RadioButton {
                        id: zipRadio
                        text: "Export to ZIP Archive"
                        checked: exportFormat === "zip"
                        
                        onCheckedChanged: {
                            if (checked) {
                                exportFormat = "zip"
                            }
                        }
                        
                        contentItem: Text {
                            text: parent.text
                            font.pixelSize: Theme.fontSizeNormal
                            color: Theme.textColor
                            leftPadding: parent.indicator.width + Theme.spacingSmall
                            verticalAlignment: Text.AlignVCenter
                        }
                        
                        indicator: Rectangle {
                            implicitWidth: 20
                            implicitHeight: 20
                            radius: 10
                            border.color: Theme.borderColor
                            border.width: 1
                            color: "transparent"
                            
                            Rectangle {
                                anchors.centerIn: parent
                                width: 12
                                height: 12
                                radius: 6
                                color: Theme.accentColor
                                visible: zipRadio.checked
                            }
                        }
                    }
                }
            }
            
            // Export Options Section
            GroupBox {
                Layout.fillWidth: true
                title: "Export Options"
                
                background: Rectangle {
                    color: Theme.backgroundLight
                    border.color: Theme.borderColor
                    border.width: 1
                    radius: Theme.radiusSmall
                }
                
                label: Label {
                    text: parent.title
                    font.bold: true
                    font.pixelSize: Theme.fontSizeLarge
                    color: Theme.textColor
                    leftPadding: Theme.spacingSmall
                }
                
                ColumnLayout {
                    width: parent.width
                    spacing: Theme.spacingNormal
                    
                    CheckBox {
                        id: convertCheck
                        text: "Convert to MP3"
                        checked: convertToMP3
                        
                        onCheckedChanged: {
                            convertToMP3 = checked
                        }
                        
                        contentItem: Text {
                            text: parent.text
                            font.pixelSize: Theme.fontSizeNormal
                            color: Theme.textColor
                            leftPadding: parent.indicator.width + Theme.spacingSmall
                            verticalAlignment: Text.AlignVCenter
                        }
                        
                        indicator: Rectangle {
                            implicitWidth: 20
                            implicitHeight: 20
                            radius: 3
                            border.color: Theme.borderColor
                            border.width: 1
                            color: convertCheck.checked ? Theme.accentColor : Theme.backgroundColor
                            
                            Text {
                                anchors.centerIn: parent
                                text: "✓"
                                font.pixelSize: Theme.fontSizeNormal
                                color: Theme.textColor
                                visible: convertCheck.checked
                            }
                        }
                    }
                    
                    CheckBox {
                        id: metadataCheck
                        text: "Include Metadata Files"
                        checked: includeMetadata
                        
                        onCheckedChanged: {
                            includeMetadata = checked
                        }
                        
                        contentItem: Text {
                            text: parent.text
                            font.pixelSize: Theme.fontSizeNormal
                            color: Theme.textColor
                            leftPadding: parent.indicator.width + Theme.spacingSmall
                            verticalAlignment: Text.AlignVCenter
                        }
                        
                        indicator: Rectangle {
                            implicitWidth: 20
                            implicitHeight: 20
                            radius: 3
                            border.color: Theme.borderColor
                            border.width: 1
                            color: metadataCheck.checked ? Theme.accentColor : Theme.backgroundColor
                            
                            Text {
                                anchors.centerIn: parent
                                text: "✓"
                                font.pixelSize: Theme.fontSizeNormal
                                color: Theme.textColor
                                visible: metadataCheck.checked
                            }
                        }
                    }
                    
                    Label {
                        text: "Metadata includes: annotations, tempo, clip definitions"
                        font.pixelSize: Theme.fontSizeSmall
                        color: Theme.textMuted
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                    }
                }
            }
            
            // Destination Section
            GroupBox {
                Layout.fillWidth: true
                title: "Destination"
                
                background: Rectangle {
                    color: Theme.backgroundLight
                    border.color: Theme.borderColor
                    border.width: 1
                    radius: Theme.radiusSmall
                }
                
                label: Label {
                    text: parent.title
                    font.bold: true
                    font.pixelSize: Theme.fontSizeLarge
                    color: Theme.textColor
                    leftPadding: Theme.spacingSmall
                }
                
                RowLayout {
                    width: parent.width
                    spacing: Theme.spacingNormal
                    
                    TextField {
                        id: pathField
                        Layout.fillWidth: true
                        placeholderText: "Select destination folder..."
                        text: destinationPath
                        readOnly: true
                        
                        background: Rectangle {
                            color: Theme.backgroundColor
                            border.color: Theme.borderColor
                            border.width: 1
                            radius: Theme.radiusSmall
                        }
                        
                        color: Theme.textColor
                    }
                    
                    Button {
                        text: "Browse..."
                        
                        onClicked: {
                            folderDialog.open()
                        }
                        
                        contentItem: Text {
                            text: parent.text
                            font.pixelSize: Theme.fontSizeNormal
                            color: Theme.textColor
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        
                        background: Rectangle {
                            color: parent.down ? Theme.backgroundLight : Theme.backgroundColor
                            border.color: Theme.borderColor
                            border.width: 1
                            radius: Theme.radiusSmall
                        }
                    }
                }
            }
        }
    }
    
    // Folder selection dialog
    FolderDialog {
        id: folderDialog
        title: "Select Destination Folder"
        
        onAccepted: {
            var path = selectedFolder.toString()
            // Remove file:// prefix
            if (path.startsWith("file://")) {
                path = path.substring(7)
            }
            destinationPath = path
        }
    }
    
    // Progress dialog (placeholder - actual implementation would use a proper worker)
    Dialog {
        id: progressDialog
        title: "Exporting Best Takes"
        modal: true
        closePolicy: Popup.NoAutoClose
        
        x: (parent.width - width) / 2
        y: (parent.height - height) / 2
        width: 400
        height: 200
        
        background: Rectangle {
            color: Theme.backgroundColor
            border.color: Theme.borderColor
            border.width: 1
            radius: Theme.radiusSmall
        }
        
        property int currentFile: 0
        property int totalFiles: 0
        
        function performExport(files, dest, format, convert, metadata) {
            totalFiles = files.length
            currentFile = 0
            progressBar.value = 0
            statusLabel.text = "Preparing export..."
            
            // TODO: Implement actual export via worker thread
            // For now, just simulate progress
            exportTimer.start()
        }
        
        ColumnLayout {
            anchors.fill: parent
            spacing: Theme.spacingLarge
            
            Label {
                id: statusLabel
                text: "Exporting files..."
                font.pixelSize: Theme.fontSizeNormal
                color: Theme.textColor
                Layout.fillWidth: true
            }
            
            ProgressBar {
                id: progressBar
                Layout.fillWidth: true
                from: 0
                to: 100
                value: 0
                
                background: Rectangle {
                    color: Theme.backgroundLight
                    border.color: Theme.borderColor
                    border.width: 1
                    radius: Theme.radiusSmall
                }
                
                contentItem: Item {
                    Rectangle {
                        width: progressBar.visualPosition * parent.width
                        height: parent.height
                        color: Theme.accentColor
                        radius: Theme.radiusSmall
                    }
                }
            }
            
            Label {
                id: progressLabel
                text: "0 / 0 files"
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.textMuted
                Layout.fillWidth: true
            }
            
            Button {
                text: "Cancel"
                Layout.alignment: Qt.AlignRight
                
                onClicked: {
                    exportTimer.stop()
                    progressDialog.close()
                }
                
                contentItem: Text {
                    text: parent.text
                    font.pixelSize: Theme.fontSizeNormal
                    color: Theme.textColor
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                
                background: Rectangle {
                    color: parent.down ? Theme.backgroundLight : Theme.backgroundColor
                    border.color: Theme.borderColor
                    border.width: 1
                    radius: Theme.radiusSmall
                }
            }
        }
        
        // Simulate export progress (TODO: replace with real worker)
        Timer {
            id: exportTimer
            interval: 200
            repeat: true
            
            onTriggered: {
                progressDialog.currentFile++
                var progress = (progressDialog.currentFile / progressDialog.totalFiles) * 100
                progressBar.value = progress
                progressLabel.text = progressDialog.currentFile + " / " + progressDialog.totalFiles + " files"
                statusLabel.text = "Exporting file " + progressDialog.currentFile + "..."
                
                if (progressDialog.currentFile >= progressDialog.totalFiles) {
                    exportTimer.stop()
                    statusLabel.text = "Export complete!"
                    progressBar.value = 100
                    
                    // Close dialog after 1 second
                    Qt.callLater(function() {
                        closeTimer.start()
                    })
                }
            }
        }
        
        Timer {
            id: closeTimer
            interval: 1000
            repeat: false
            onTriggered: progressDialog.close()
        }
    }
}
