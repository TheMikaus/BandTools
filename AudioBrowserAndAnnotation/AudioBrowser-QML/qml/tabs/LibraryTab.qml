import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import QtQuick.Dialogs
import "../components"
import "../styles"
import "../dialogs"

Item {
    id: libraryTab
    
    // Properties
    property string currentDirectory: ""
    property string sortField: "filename"
    property bool sortAscending: true
    property bool filterBestTakes: false
    property bool filterPartialTakes: false
    
    // Signals for context menu actions that need to switch tabs
    signal requestAnnotationTab(string filePath)
    signal requestClipsTab(string filePath)
    
    // Functions accessible from outside
    function openFolderDialog() {
        folderDialog.open()
    }
    
    function setDirectoryFromCode(path) {
        directoryField.text = path
        populateFolderTree(path)
    }
    
    // Folder picker dialog
    FolderDialog {
        id: folderDialog
        
        onFolderSelected: function(folder) {
            console.log("Folder selected:", folder)
            fileManager.setCurrentDirectory(folder)
            settingsManager.addRecentFolder(folder, 10)
            directoryField.text = folder
            // Populate folder tree with new root directory
            populateFolderTree(folder)
        }
    }
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacingNormal
        spacing: Theme.spacingNormal
        
        // Toolbar - organized into two rows
        ColumnLayout {
            Layout.fillWidth: true
            spacing: Theme.spacingSmall
            
            // First row: Directory selection
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: Theme.toolbarHeight
                color: Theme.backgroundLight
                radius: Theme.radiusSmall
                
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: Theme.spacingSmall
                    spacing: Theme.spacingNormal
                    
                    Label {
                        text: "Directory:"
                        font.pixelSize: Theme.fontSizeNormal
                        color: Theme.textColor
                    }
                    
                    TextField {
                        id: directoryField
                        Layout.fillWidth: true
                        placeholderText: "Select a directory..."
                        text: fileManager ? fileManager.getCurrentDirectory() : ""
                        font.pixelSize: Theme.fontSizeNormal
                        background: Rectangle {
                            color: Theme.backgroundColor
                            border.color: Theme.borderColor
                            border.width: 1
                            radius: Theme.radiusSmall
                        }
                        color: Theme.textColor
                        
                        onAccepted: {
                            if (text.length > 0) {
                                fileManager.setCurrentDirectory(text)
                            } else {
                                promptForDirectory()
                            }
                        }
                    }
                    
                    StyledButton {
                        text: "Browse..."
                        onClicked: {
                            folderDialog.open()
                        }
                    }
                    
                    StyledButton {
                        text: "Refresh"
                        success: true
                        onClicked: {
                            var dir = fileManager.getCurrentDirectory()
                            if (dir.length > 0) {
                                fileManager.discoverAudioFiles(dir)
                            } else {
                                promptForDirectory()
                            }
                        }
                    }
                }
            }
            
            // Second row: Actions and filters
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: Theme.toolbarHeight
                color: Theme.backgroundLight
                radius: Theme.radiusSmall
                
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: Theme.spacingSmall
                    spacing: Theme.spacingNormal
                    
                    Label {
                        text: "Actions:"
                        font.pixelSize: Theme.fontSizeNormal
                        color: Theme.textColor
                    }
                    
                    // Batch operations buttons
                    StyledButton {
                        text: "Batch Rename"
                        info: true
                        enabled: fileListModel.count() > 0
                        onClicked: {
                            // Get all files from the model
                            var files = []
                            for (var i = 0; i < fileListModel.count(); i++) {
                                var filePath = fileListModel.getFilePath(i)
                                if (filePath) {
                                    files.push(filePath)
                                }
                            }
                            batchRenameDialog.openDialog(files)
                        }
                    }
                    
                    StyledButton {
                        text: "Convert WAV→MP3"
                        warning: true
                        enabled: fileListModel.count() > 0
                        onClicked: {
                            // Get all WAV files from the model
                            var wavFiles = []
                            for (var i = 0; i < fileListModel.count(); i++) {
                                var filePath = fileListModel.getFilePath(i)
                                if (filePath && filePath.toLowerCase().endsWith(".wav")) {
                                    wavFiles.push(filePath)
                                }
                            }
                            if (wavFiles.length === 0) {
                                console.log("No WAV files found")
                                return
                            }
                            batchConvertDialog.openDialog("wav_to_mp3", wavFiles, "")
                        }
                    }
                    
                    // Separator
                    Rectangle {
                        width: 1
                        Layout.fillHeight: true
                        Layout.margins: 4
                        color: Theme.borderColor
                    }
                    
                    Label {
                        text: "Filters:"
                        font.pixelSize: Theme.fontSizeNormal
                        color: Theme.textColor
                    }
                    
                    // Filter: Best Takes
                    StyledButton {
                        text: filterBestTakes ? "★ Best Takes ✓" : "★ Best Takes"
                        info: filterBestTakes
                        onClicked: {
                            filterBestTakes = !filterBestTakes
                            updateFileList()
                        }
                    }
                    
                    // Filter: Partial Takes
                    StyledButton {
                        text: filterPartialTakes ? "◐ Partial Takes ✓" : "◐ Partial Takes"
                        info: filterPartialTakes
                        onClicked: {
                            filterPartialTakes = !filterPartialTakes
                            updateFileList()
                        }
                    }
                    
                    // Separator
                    Rectangle {
                        width: 1
                        Layout.fillHeight: true
                        Layout.margins: 4
                        color: Theme.borderColor
                    }
                    
                    Label {
                        text: "Tools:"
                        font.pixelSize: Theme.fontSizeNormal
                        color: Theme.textColor
                    }
                    
                    // Practice Statistics button
                    StyledButton {
                        text: "📊 Stats"
                        info: true
                        onClicked: {
                            practiceStatisticsDialog.open()
                        }
                    }
                    
                    // Practice Goals button
                    StyledButton {
                        text: "🎯 Goals"
                        info: true
                        onClicked: {
                            practiceGoalsDialog.open()
                        }
                    }
                    
                    // Setlist Builder button
                    StyledButton {
                        text: "🎵 Setlist"
                        info: true
                        onClicked: {
                            setlistBuilderDialog.open()
                        }
                    }
                    
                    // Add spacing at the end
                    Item { Layout.fillWidth: true }
                }
            }
        }
        
        // Split view: Folders on left, Files on right
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: Theme.spacingNormal
            
            // Folders panel (left side)
            Rectangle {
                Layout.preferredWidth: 250
                Layout.fillHeight: true
                color: Theme.backgroundColor
                border.color: Theme.borderColor
                border.width: 1
                radius: Theme.radiusSmall
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: Theme.spacingSmall
                    spacing: 0
                    
                    // Header
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: Theme.buttonHeight
                        color: Theme.backgroundLight
                        
                        Label {
                            anchors.fill: parent
                            anchors.leftMargin: Theme.spacingNormal
                            text: "Folders"
                            font.pixelSize: Theme.fontSizeMedium
                            font.bold: true
                            color: Theme.textColor
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                    
                    // Folder ListView
                    ListView {
                        id: folderListView
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        
                        model: ListModel {
                            id: folderTreeModel
                        }
                        
                        delegate: Rectangle {
                            width: folderListView.width
                            height: 28
                            color: folderMouseArea.containsMouse ? Theme.backgroundLight : 
                                   (model.isSelected ? Theme.backgroundMedium : "transparent")
                            
                            property bool isSelected: false
                            
                            RowLayout {
                                anchors.fill: parent
                                anchors.leftMargin: Theme.spacingSmall + (model.level * 16)
                                anchors.rightMargin: Theme.spacingSmall
                                spacing: 4
                                
                                Label {
                                    text: model.isRoot ? "📁 " + model.name : 
                                          (model.hasAudio ? "📂 " + model.name : "📁 " + model.name)
                                    font.pixelSize: Theme.fontSizeNormal
                                    color: Theme.textColor
                                    Layout.fillWidth: true
                                    elide: Text.ElideMiddle
                                }
                                
                                Label {
                                    text: model.audioCount > 0 ? "(" + model.audioCount + ")" : ""
                                    font.pixelSize: Theme.fontSizeSmall
                                    color: Theme.textSecondary
                                    visible: model.audioCount > 0
                                }
                            }
                            
                            MouseArea {
                                id: folderMouseArea
                                anchors.fill: parent
                                hoverEnabled: true
                                
                                onClicked: {
                                    // Clear previous selection
                                    for (var i = 0; i < folderListView.count; i++) {
                                        folderListView.itemAtIndex(i).isSelected = false
                                    }
                                    // Set new selection
                                    isSelected = true
                                    
                                    // Load files from this folder
                                    console.log("Selected folder:", model.path)
                                    fileManager.discoverAudioFiles(model.path)
                                    
                                    // Load folder notes for this folder
                                    if (folderNotesManager) {
                                        folderNotesManager.loadNotesForFolder(model.path)
                                    }
                                }
                            }
                        }
                        
                        ScrollBar.vertical: ScrollBar {
                            policy: ScrollBar.AsNeeded
                        }
                    }
                }
            }
            
            // Files panel (right side)
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: Theme.backgroundColor
                border.color: Theme.borderColor
                border.width: 1
                radius: Theme.radiusSmall
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: Theme.spacingSmall
                    spacing: 0
                    
                    // Header with column labels
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: Theme.buttonHeight
                        color: Theme.backgroundLight
                        
                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: Theme.spacingNormal
                            anchors.rightMargin: Theme.spacingNormal
                            spacing: Theme.spacingNormal
                            
                            Label {
                                text: "Files (" + fileListModel.count() + ")"
                                font.pixelSize: Theme.fontSizeMedium
                                font.bold: true
                                color: Theme.textColor
                                Layout.fillWidth: true
                            }
                            
                            TextField {
                                id: filterField
                                Layout.preferredWidth: 200
                                placeholderText: "Filter..."
                                font.pixelSize: Theme.fontSizeNormal
                                background: Rectangle {
                                    color: Theme.backgroundColor
                                    border.color: Theme.borderColor
                                    border.width: 1
                                    radius: Theme.radiusSmall
                                }
                                color: Theme.textColor
                            }
                        }
                    }
                
                // Column Headers (clickable for sorting)
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 28
                    color: Theme.backgroundMedium
                    
                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: Theme.spacingNormal
                        anchors.rightMargin: Theme.spacingNormal
                        spacing: Theme.spacingNormal
                        
                        // Indicators column header
                        Rectangle {
                            Layout.preferredWidth: 60
                            height: parent.height
                            color: "transparent"
                            
                            Label {
                                anchors.fill: parent
                                anchors.leftMargin: 4
                                text: "Take"
                                font.pixelSize: Theme.fontSizeSmall
                                font.bold: true
                                color: Theme.textColor
                                verticalAlignment: Text.AlignVCenter
                            }
                        }
                        
                        // File Name column header
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredWidth: 300
                            height: parent.height
                            color: "transparent"
                            
                            Label {
                                anchors.fill: parent
                                anchors.leftMargin: 4
                                text: "File Name " + (sortField === "filename" ? (sortAscending ? "▲" : "▼") : "")
                                font.pixelSize: Theme.fontSizeSmall
                                font.bold: true
                                color: sortField === "filename" ? Theme.accentPrimary : Theme.textColor
                                verticalAlignment: Text.AlignVCenter
                            }
                            
                            MouseArea {
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    if (sortField === "filename") {
                                        sortAscending = !sortAscending
                                    } else {
                                        sortField = "filename"
                                        sortAscending = true
                                    }
                                    fileListModel.sortBy(sortField, sortAscending)
                                }
                            }
                        }
                        
                        // Library Name column header
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredWidth: 200
                            height: parent.height
                            color: "transparent"
                            
                            Label {
                                anchors.fill: parent
                                anchors.leftMargin: 4
                                text: "Library"
                                font.pixelSize: Theme.fontSizeSmall
                                font.bold: true
                                color: Theme.textColor
                                verticalAlignment: Text.AlignVCenter
                            }
                        }
                        
                        // Duration column header
                        Rectangle {
                            Layout.preferredWidth: 80
                            height: parent.height
                            color: "transparent"
                            
                            Label {
                                anchors.fill: parent
                                text: "Duration"
                                font.pixelSize: Theme.fontSizeSmall
                                font.bold: true
                                color: Theme.textColor
                                verticalAlignment: Text.AlignVCenter
                                horizontalAlignment: Text.AlignHCenter
                            }
                        }
                    }
                }
                
                // File ListView
                ListView {
                    id: fileListView
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    
                    model: fileListModel
                    
                    delegate: Rectangle {
                        width: fileListView.width
                        height: 32
                        color: index % 2 === 0 ? Theme.backgroundColor : Theme.backgroundMedium
                        
                        // Hover effect
                        Rectangle {
                            anchors.fill: parent
                            color: Theme.accentPrimary
                            opacity: mouseArea.containsMouse ? 0.1 : 0
                            
                            Behavior on opacity {
                                NumberAnimation { duration: Theme.animationFast }
                            }
                        }
                        
                        // Selection highlight
                        Rectangle {
                            anchors.fill: parent
                            color: Theme.selectionPrimary
                            opacity: fileListView.currentIndex === index ? 0.3 : 0
                        }
                        
                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: Theme.spacingNormal
                            anchors.rightMargin: Theme.spacingNormal
                            spacing: Theme.spacingNormal
                            
                            // Take indicators
                            RowLayout {
                                Layout.preferredWidth: 60
                                spacing: 4
                                
                                BestTakeIndicator {
                                    marked: model.isBestTake || false
                                    onClicked: {
                                        if (model.isBestTake) {
                                            fileManager.unmarkAsBestTake(model.filepath)
                                        } else {
                                            fileManager.markAsBestTake(model.filepath)
                                        }
                                        // Refresh the file list to update indicators
                                        fileManager.discoverAudioFiles(fileManager.getCurrentDirectory())
                                    }
                                }
                                
                                PartialTakeIndicator {
                                    marked: model.isPartialTake || false
                                    onClicked: {
                                        if (model.isPartialTake) {
                                            fileManager.unmarkAsPartialTake(model.filepath)
                                        } else {
                                            fileManager.markAsPartialTake(model.filepath)
                                        }
                                        // Refresh the file list to update indicators
                                        fileManager.discoverAudioFiles(fileManager.getCurrentDirectory())
                                    }
                                }
                            }
                            
                            // File Name with important annotation indicator
                            RowLayout {
                                Layout.fillWidth: true
                                Layout.preferredWidth: 300
                                spacing: 4
                                
                                Label {
                                    text: model.hasImportantAnnotation ? "⭐" : ""
                                    font.pixelSize: Theme.fontSizeNormal
                                    color: Theme.accentWarning
                                    visible: model.hasImportantAnnotation || false
                                }
                                
                                Label {
                                    text: model.filename
                                    font.pixelSize: Theme.fontSizeNormal
                                    color: Theme.textColor
                                    Layout.fillWidth: true
                                    elide: Text.ElideMiddle
                                }
                            }
                            
                            // Library Name (folder name)
                            Label {
                                text: model.libraryName || ""
                                font.pixelSize: Theme.fontSizeSmall
                                color: Theme.textSecondary
                                Layout.fillWidth: true
                                Layout.preferredWidth: 200
                                elide: Text.ElideMiddle
                            }
                            
                            // Duration
                            Label {
                                text: formatDuration(model.duration || 0)
                                font.pixelSize: Theme.fontSizeSmall
                                color: Theme.textSecondary
                                Layout.preferredWidth: 80
                                horizontalAlignment: Text.AlignHCenter
                            }
                        }
                        
                        MouseArea {
                            id: mouseArea
                            anchors.fill: parent
                            hoverEnabled: true
                            acceptedButtons: Qt.LeftButton | Qt.RightButton
                            
                            onClicked: function(mouse) {
                                fileListView.currentIndex = index
                                console.log("Selected file:", model.filepath)
                                
                                // Handle right-click for context menu
                                if (mouse.button === Qt.RightButton) {
                                    contextMenu.filePath = model.filepath
                                    contextMenu.fileName = model.filename
                                    contextMenu.popup()
                                } else {
                                    // Single click: Load and play the file
                                    audioEngine.loadAndPlay(model.filepath)
                                }
                            }
                            
                            onDoubleClicked: {
                                console.log("Double-clicked file:", model.filepath)
                                // Double click: Load, play, and switch to Annotations tab
                                audioEngine.loadAndPlay(model.filepath)
                                tabBar.currentIndex = 1  // Switch to Annotations tab
                            }
                        }
                    }
                    
                    ScrollBar.vertical: ScrollBar {
                        policy: ScrollBar.AsNeeded
                    }
                }
            }  // End of Files panel ColumnLayout
        }  // End of Files panel Rectangle
        }  // End of RowLayout (split view)
        
        // Status bar
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: Theme.statusBarHeight
            color: Theme.backgroundLight
            radius: Theme.radiusSmall
            
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: Theme.spacingNormal
                anchors.rightMargin: Theme.spacingNormal
                spacing: Theme.spacingLarge
                
                Label {
                    text: "Ready"
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.textMuted
                }
                
                Item { Layout.fillWidth: true }
                
                Label {
                    text: fileManager ? fileManager.getCurrentDirectory() : ""
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.textMuted
                    elide: Text.ElideMiddle
                }
            }
        }
    }
    
    // Prompt user to select a directory
    function promptForDirectory() {
        noDirectoryDialog.open()
    }
    
    // Update file list with filters applied
    function updateFileList() {
        var currentDir = fileManager.getCurrentDirectory()
        if (!currentDir || currentDir.length === 0) {
            return
        }
        
        // If no filters, refresh normally
        if (!filterBestTakes && !filterPartialTakes) {
            fileManager.discoverAudioFiles(currentDir)
            return
        }
        
        // Get all files
        var allFiles = fileManager.getDiscoveredFiles()
        var filteredFiles = []
        
        // Apply filters
        for (var i = 0; i < allFiles.length; i++) {
            var filePath = allFiles[i]
            var isBest = fileManager.isBestTake(filePath)
            var isPartial = fileManager.isPartialTake(filePath)
            
            // Include file if it matches any active filter
            if ((filterBestTakes && isBest) || (filterPartialTakes && isPartial)) {
                filteredFiles.push(filePath)
            }
        }
        
        // Update model with filtered files
        fileListModel.setFiles(filteredFiles)
    }
    
    // Helper function to format file size
    function formatFileSize(bytes) {
        if (bytes < 1024) {
            return bytes + " B"
        } else if (bytes < 1024 * 1024) {
            return (bytes / 1024).toFixed(1) + " KB"
        } else if (bytes < 1024 * 1024 * 1024) {
            return (bytes / (1024 * 1024)).toFixed(1) + " MB"
        } else {
            return (bytes / (1024 * 1024 * 1024)).toFixed(1) + " GB"
        }
    }
    
    // Helper function to format duration
    function formatDuration(durationMs) {
        if (durationMs <= 0) {
            return "--:--"
        }
        
        var totalSeconds = Math.floor(durationMs / 1000)
        var hours = Math.floor(totalSeconds / 3600)
        var minutes = Math.floor((totalSeconds % 3600) / 60)
        var seconds = totalSeconds % 60
        
        if (hours > 0) {
            return hours.toString().padStart(2, '0') + ":" + 
                   minutes.toString().padStart(2, '0') + ":" + 
                   seconds.toString().padStart(2, '0')
        } else {
            return minutes.toString().padStart(2, '0') + ":" + 
                   seconds.toString().padStart(2, '0')
        }
    }
    
    // Connections to handle file manager signals
    Connections {
        target: fileManager
        
        function onCurrentDirectoryChanged(directory) {
            directoryField.text = directory
            // Populate folder tree when directory changes
            populateFolderTree(directory)
        }
        
        function onFilesDiscovered(files) {
            // Update the file list model with discovered files
            fileListModel.setFiles(files)
        }
        
        function onErrorOccurred(errorMessage) {
            console.error("File Manager Error:", errorMessage)
        }
    }
    
    // ========== File Context Menu ==========
    
    FileContextMenu {
        id: contextMenu
        
        onAnnotationRequested: {
            // Emit signal to request switching to Annotations tab
            // and load the file if different from current
            if (contextMenu.filePath && audioEngine) {
                if (audioEngine.getCurrentFile() !== contextMenu.filePath) {
                    audioEngine.loadAndPlay(contextMenu.filePath)
                }
            }
            libraryTab.requestAnnotationTab(contextMenu.filePath)
        }
        
        onClipRequested: {
            // Emit signal to request switching to Clips tab
            // and load the file if different from current
            if (contextMenu.filePath && audioEngine) {
                if (audioEngine.getCurrentFile() !== contextMenu.filePath) {
                    audioEngine.loadAndPlay(contextMenu.filePath)
                }
            }
            libraryTab.requestClipsTab(contextMenu.filePath)
        }
        
        onPropertiesRequested: {
            // Show file properties dialog
            propertiesDialog.filePath = contextMenu.filePath
            propertiesDialog.open()
        }
        
        onEditLibraryNameRequested: {
            // Show library name edit dialog
            editLibraryNameDialog.filePath = contextMenu.filePath
            editLibraryNameDialog.fileName = contextMenu.fileName
            editLibraryNameDialog.currentLibraryName = fileManager ? fileManager.getProvidedName(contextMenu.filePath) : ""
            editLibraryNameDialog.open()
        }
    }
    
    // ========== File Properties Dialog ==========
    
    Dialog {
        id: propertiesDialog
        title: "File Properties"
        modal: true
        anchors.centerIn: parent
        width: 400
        
        property string filePath: ""
        
        standardButtons: Dialog.Ok
        
        ColumnLayout {
            width: parent.width
            spacing: Theme.spacingSmall
            
            Label {
                text: fileManager ? fileManager.getFileProperties(propertiesDialog.filePath) : ""
                color: Theme.textColor
                font.pixelSize: Theme.fontSizeNormal
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
            }
        }
        
        background: Rectangle {
            color: Theme.backgroundColor
            border.color: Theme.borderColor
            border.width: 1
            radius: Theme.radiusSmall
        }
    }
    
    // ========== Edit Library Name Dialog ==========
    
    Dialog {
        id: editLibraryNameDialog
        title: "Edit Library Name"
        modal: true
        anchors.centerIn: parent
        width: 450
        
        property string filePath: ""
        property string fileName: ""
        property string currentLibraryName: ""
        
        standardButtons: Dialog.Ok | Dialog.Cancel
        
        ColumnLayout {
            width: parent.width
            spacing: Theme.spacingNormal
            
            Label {
                text: "File: " + editLibraryNameDialog.fileName
                color: Theme.textSecondary
                font.pixelSize: Theme.fontSizeSmall
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
            }
            
            Label {
                text: "Library Name (Song Title):"
                color: Theme.textColor
                font.pixelSize: Theme.fontSizeNormal
            }
            
            TextField {
                id: libraryNameField
                Layout.fillWidth: true
                placeholderText: "Enter library/song name..."
                text: editLibraryNameDialog.currentLibraryName
                font.pixelSize: Theme.fontSizeNormal
                selectByMouse: true
                
                background: Rectangle {
                    color: Theme.backgroundColor
                    border.color: libraryNameField.activeFocus ? Theme.accentPrimary : Theme.borderColor
                    border.width: 1
                    radius: Theme.radiusSmall
                }
                
                color: Theme.textColor
                
                Keys.onReturnPressed: editLibraryNameDialog.accept()
            }
            
            Label {
                text: "Tip: This name will be used to identify the song in your library."
                color: Theme.textMuted
                font.pixelSize: Theme.fontSizeSmall
                font.italic: true
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
            }
        }
        
        onAccepted: {
            if (fileManager && filePath) {
                fileManager.setProvidedName(filePath, libraryNameField.text)
                // Refresh the file list
                var dir = fileManager.getCurrentDirectory()
                if (dir.length > 0) {
                    fileManager.discoverAudioFiles(dir)
                }
            }
        }
        
        onOpened: {
            libraryNameField.forceActiveFocus()
            libraryNameField.selectAll()
        }
        
        background: Rectangle {
            color: Theme.backgroundColor
            border.color: Theme.borderColor
            border.width: 1
            radius: Theme.radiusSmall
        }
    }
    
    // ========== No Directory Dialog ==========
    
    Dialog {
        id: noDirectoryDialog
        title: "No Directory Selected"
        modal: true
        anchors.centerIn: parent
        width: 350
        
        standardButtons: Dialog.Ok | Dialog.Cancel
        
        ColumnLayout {
            width: parent.width
            spacing: Theme.spacingNormal
            
            Label {
                text: "No audio directory has been selected.\n\nWould you like to select a directory now?"
                color: Theme.textColor
                font.pixelSize: Theme.fontSizeNormal
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
            }
        }
        
        onAccepted: {
            folderDialog.open()
        }
        
        background: Rectangle {
            color: Theme.backgroundColor
            border.color: Theme.borderColor
            border.width: 1
            radius: Theme.radiusSmall
        }
    }
    
    // Populate folder tree from root directory
    function populateFolderTree(rootDirectory) {
        if (!rootDirectory || rootDirectory.length === 0) {
            folderTreeModel.clear()
            return
        }
        
        console.log("Populating folder tree for:", rootDirectory)
        
        // Get all directories with audio files
        var directories = fileManager.getDirectoriesWithAudioFiles(rootDirectory)
        
        // Clear the model
        folderTreeModel.clear()
        
        // Add directories to the model
        for (var i = 0; i < directories.length; i++) {
            var dir = directories[i]
            folderTreeModel.append({
                path: dir.path,
                name: dir.name,
                parent: dir.parent,
                hasAudio: dir.hasAudio,
                audioCount: dir.audioCount,
                isRoot: dir.isRoot,
                level: 0  // Will be calculated based on path depth
            })
        }
        
        // Calculate levels for proper indentation
        for (var j = 0; j < folderTreeModel.count; j++) {
            var folder = folderTreeModel.get(j)
            if (folder.isRoot) {
                folder.level = 0
            } else {
                // Count slashes to determine depth
                var pathParts = folder.path.split('/')
                var rootParts = rootDirectory.split('/')
                folder.level = pathParts.length - rootParts.length
            }
        }
    }
    
    // Initialize on component load
    Component.onCompleted: {
        // Check if we have a directory set
        var currentDir = fileManager.getCurrentDirectory()
        if (!currentDir || currentDir.length === 0) {
            // No directory set, prompt user to select one
            promptForDirectory()
        } else {
            // Populate folder tree with current directory
            populateFolderTree(currentDir)
        }
    }
}
