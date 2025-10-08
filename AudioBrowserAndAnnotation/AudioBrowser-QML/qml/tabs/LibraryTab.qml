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
                        text: fileManager.getCurrentDirectory()
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
                        
                        // Name column header
                        Rectangle {
                            Layout.fillWidth: true
                            height: parent.height
                            color: "transparent"
                            
                            Label {
                                anchors.fill: parent
                                anchors.leftMargin: 4
                                text: "Name " + (sortField === "filename" ? (sortAscending ? "▲" : "▼") : "")
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
                        
                        // Duration column header
                        Rectangle {
                            Layout.preferredWidth: 80
                            height: parent.height
                            color: "transparent"
                            
                            Label {
                                anchors.fill: parent
                                anchors.rightMargin: 4
                                text: "Duration " + (sortField === "duration" ? (sortAscending ? "▲" : "▼") : "")
                                font.pixelSize: Theme.fontSizeSmall
                                font.bold: true
                                color: sortField === "duration" ? Theme.accentPrimary : Theme.textColor
                                horizontalAlignment: Text.AlignRight
                                verticalAlignment: Text.AlignVCenter
                            }
                            
                            MouseArea {
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    if (sortField === "duration") {
                                        sortAscending = !sortAscending
                                    } else {
                                        sortField = "duration"
                                        sortAscending = false  // Default to longest first
                                    }
                                    fileListModel.sortBy(sortField, sortAscending)
                                }
                            }
                        }
                        
                        // Size column header
                        Rectangle {
                            Layout.preferredWidth: 80
                            height: parent.height
                            color: "transparent"
                            
                            Label {
                                anchors.fill: parent
                                anchors.rightMargin: 4
                                text: "Size " + (sortField === "filesize" ? (sortAscending ? "▲" : "▼") : "")
                                font.pixelSize: Theme.fontSizeSmall
                                font.bold: true
                                color: sortField === "filesize" ? Theme.accentPrimary : Theme.textColor
                                horizontalAlignment: Text.AlignRight
                                verticalAlignment: Text.AlignVCenter
                            }
                            
                            MouseArea {
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    if (sortField === "filesize") {
                                        sortAscending = !sortAscending
                                    } else {
                                        sortField = "filesize"
                                        sortAscending = false  // Default to largest first
                                    }
                                    fileListModel.sortBy(sortField, sortAscending)
                                }
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
                            
                            // BPM field (editable)
                            TextField {
                                id: bpmField
                                Layout.preferredWidth: 50
                                text: model.bpm > 0 ? Math.round(model.bpm).toString() : ""
                                placeholderText: "BPM"
                                font.pixelSize: Theme.fontSizeSmall
                                horizontalAlignment: Text.AlignCenter
                                color: Theme.textColor
                                background: Rectangle {
                                    color: bpmField.activeFocus ? Theme.backgroundLight : "transparent"
                                    border.color: bpmField.activeFocus ? Theme.accentPrimary : Theme.borderColor
                                    border.width: 1
                                    radius: 2
                                }
                                validator: IntValidator { bottom: 0; top: 300 }
                                
                                onEditingFinished: {
                                    var bpmValue = parseFloat(text)
                                    if (isNaN(bpmValue) || text === "") {
                                        bpmValue = 0
                                    }
                                    // Get the base filename for the model
                                    var fileName = model.filename
                                    // Extract actual filename from path if needed
                                    var filePath = model.filepath
                                    var pathParts = filePath.split("/")
                                    fileName = pathParts[pathParts.length - 1]
                                    
                                    tempoManager.setBPM(fileName, bpmValue)
                                }
                                
                                // Prevent mouse area from capturing clicks
                                MouseArea {
                                    anchors.fill: parent
                                    onPressed: function(mouse) {
                                        bpmField.forceActiveFocus()
                                        mouse.accepted = false
                                    }
                                }
                            }
                            
                            Label {
                                text: model.filename
                                font.pixelSize: Theme.fontSizeNormal
                                color: Theme.textColor
                                Layout.fillWidth: true
                                elide: Text.ElideMiddle
                            }
                            
                            Label {
                                text: formatDuration(model.duration)
                                font.pixelSize: Theme.fontSizeSmall
                                color: Theme.textSecondary
                                Layout.preferredWidth: 80
                                horizontalAlignment: Text.AlignRight
                            }
                            
                            Label {
                                text: formatFileSize(model.filesize)
                                font.pixelSize: Theme.fontSizeSmall
                                color: Theme.textSecondary
                                Layout.preferredWidth: 80
                                horizontalAlignment: Text.AlignRight
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
                                    // Load file on single left-click so it's ready to view in Annotations tab
                                    audioEngine.loadFile(model.filepath)
                                }
                            }
                            
                            onDoubleClicked: {
                                console.log("Double-clicked file:", model.filepath)
                                audioEngine.loadFile(model.filepath)
                                audioEngine.play()
                                
                                // Auto-switch to Annotations tab if enabled
                                if (autoSwitchCheckbox.checked) {
                                    tabBar.currentIndex = 1  // Switch to Annotations tab
                                }
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
                    text: fileManager.getCurrentDirectory()
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
        
        function onErrorOccurred(errorMessage) {
            console.error("File Manager Error:", errorMessage)
        }
    }
    
    // ========== File Context Menu ==========
    
    FileContextMenu {
        id: contextMenu
        
        onAnnotationRequested: {
            // Switch to Annotations tab
            // This will be triggered from the parent (main.qml)
            console.log("Annotation requested for:", contextMenu.filePath)
        }
        
        onClipRequested: {
            // Switch to Clips tab
            console.log("Clip requested for:", contextMenu.filePath)
        }
        
        onPropertiesRequested: {
            // Show file properties dialog
            propertiesDialog.filePath = contextMenu.filePath
            propertiesDialog.open()
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
                text: fileManager.getFileProperties(propertiesDialog.filePath)
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
