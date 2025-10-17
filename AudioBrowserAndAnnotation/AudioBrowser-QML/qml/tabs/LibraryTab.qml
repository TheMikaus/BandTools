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
    property var batchRenameDialogRef: null
    property var batchConvertDialogRef: null
    
    // Signals for context menu actions that need to switch tabs
    signal requestAnnotationTab(string filePath)
    signal requestClipsTab(string filePath)
    signal switchToAnnotationsTab()
    signal requestFingerprintsTab()
    
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
        anchors.margins: Theme.spacingSmall
        spacing: Theme.spacingSmall
        
        // Compact toolbar - single row with essential controls
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: Theme.toolbarHeight
            color: Theme.backgroundLight
            radius: Theme.radiusSmall
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: Theme.spacingSmall
                spacing: Theme.spacingSmall
                
                StyledButton {
                    text: "📁"
                    onClicked: {
                        folderDialog.open()
                    }
                    ToolTip.visible: hovered
                    ToolTip.text: "Browse for folder"
                    ToolTip.delay: 500
                }
                
                StyledButton {
                    text: "🔄"
                    success: true
                    onClicked: {
                        var dir = fileManager.getCurrentDirectory()
                        if (dir.length > 0) {
                            fileManager.discoverAudioFiles(dir)
                        } else {
                            promptForDirectory()
                        }
                    }
                    ToolTip.visible: hovered
                    ToolTip.text: "Refresh"
                    ToolTip.delay: 500
                }
                
                Item { Layout.fillWidth: true }
                
                // More menu button
                StyledButton {
                    text: "⋮"
                    onClicked: moreMenu.popup()
                    ToolTip.visible: hovered
                    ToolTip.text: "More options"
                    ToolTip.delay: 500
                    
                    Menu {
                        id: moreMenu
                        
                        property int fileCount: 0
                        
                        onAboutToShow: {
                            // Update file count when menu is about to show
                            fileCount = fileListModel ? fileListModel.count() : 0
                        }
                        
                        MenuItem {
                            text: "Batch Rename"
                            enabled: moreMenu.fileCount > 0
                            onTriggered: {
                                if (!fileListModel || !batchRenameDialogRef) return
                                var files = []
                                for (var i = 0; i < fileListModel.count(); i++) {
                                    var filePath = fileListModel.getFilePath(i)
                                    if (filePath) {
                                        files.push(filePath)
                                    }
                                }
                                batchRenameDialogRef.openDialog(files)
                            }
                        }
                        
                        MenuItem {
                            text: "Convert WAV→MP3"
                            enabled: moreMenu.fileCount > 0
                            onTriggered: {
                                if (!fileListModel || !batchConvertDialogRef) return
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
                                batchConvertDialogRef.openDialog("wav_to_mp3", wavFiles, "")
                            }
                        }
                        
                        MenuSeparator {}
                        
                        MenuItem {
                            text: filterBestTakes ? "★ Best Takes ✓" : "★ Best Takes"
                            checkable: true
                            checked: filterBestTakes
                            onTriggered: {
                                filterBestTakes = !filterBestTakes
                                updateFileList()
                            }
                        }
                        
                        MenuItem {
                            text: filterPartialTakes ? "◐ Partial Takes ✓" : "◐ Partial Takes"
                            checkable: true
                            checked: filterPartialTakes
                            onTriggered: {
                                filterPartialTakes = !filterPartialTakes
                                updateFileList()
                            }
                        }
                        
                        MenuSeparator {}
                        
                        MenuItem {
                            text: "📊 Practice Stats"
                            onTriggered: practiceStatisticsDialog.open()
                        }
                        
                        MenuItem {
                            text: "🎯 Practice Goals"
                            onTriggered: practiceGoalsDialog.open()
                        }
                        
                        MenuItem {
                            text: "🎵 Setlist Builder"
                            onTriggered: setlistBuilderDialog.open()
                        }
                    }
                }
            }
        }
        
        // Compact split view: Folders on top, Files on bottom (vertical stacking for side panel)
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: Theme.spacingSmall
            
            // Folders panel (top, compact)
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 150
                Layout.minimumHeight: 100
                color: Theme.backgroundColor
                border.color: Theme.borderColor
                border.width: 1
                radius: Theme.radiusSmall
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: Theme.spacingSmall
                    spacing: 0
                    
                    // Compact header
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 24
                        color: Theme.backgroundLight
                        
                        Label {
                            anchors.fill: parent
                            anchors.leftMargin: Theme.spacingSmall
                            text: "Folders"
                            font.pixelSize: Theme.fontSizeSmall
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
                            height: 24
                            color: folderMouseArea.containsMouse ? Theme.backgroundLight : 
                                   (model.isSelected ? Theme.backgroundMedium : "transparent")
                            
                            property bool isSelected: false
                            
                            RowLayout {
                                anchors.fill: parent
                                anchors.leftMargin: Theme.spacingSmall + (model.level * 12)
                                anchors.rightMargin: Theme.spacingSmall
                                spacing: 2
                                
                                Label {
                                    text: model.isRoot ? "📁" : (model.hasAudio ? "📂" : "📁")
                                    font.pixelSize: Theme.fontSizeSmall
                                }
                                
                                Label {
                                    text: model.name
                                    font.pixelSize: Theme.fontSizeSmall
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
                                acceptedButtons: Qt.LeftButton | Qt.RightButton
                                
                                onClicked: function(mouse) {
                                    // Handle right-click for context menu
                                    if (mouse.button === Qt.RightButton) {
                                        folderContextMenu.folderPath = model.path
                                        folderContextMenu.folderName = model.name
                                        folderContextMenu.popup()
                                    } else {
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
                        }
                        
                        ScrollBar.vertical: ScrollBar {
                            policy: ScrollBar.AsNeeded
                        }
                    }
                }
            }
            
            // Files panel (bottom)
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
                    
                    // Compact header with file count
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 24
                        color: Theme.backgroundLight
                        
                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: Theme.spacingSmall
                            anchors.rightMargin: Theme.spacingSmall
                            spacing: Theme.spacingSmall
                            
                            Label {
                                text: "Files (" + (fileListModel ? fileListModel.count() : 0) + ")"
                                font.pixelSize: Theme.fontSizeSmall
                                font.bold: true
                                color: Theme.textColor
                                Layout.fillWidth: true
                            }
                        }
                    }
                
                // File ListView (compact, no column headers for space saving)
                ListView {
                    id: fileListView
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    
                    model: fileListModel
                    
                    delegate: Rectangle {
                        width: fileListView.width
                        height: 28
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
                            anchors.leftMargin: Theme.spacingSmall
                            anchors.rightMargin: Theme.spacingSmall
                            spacing: 4
                            
                            // Compact take indicators
                            BestTakeIndicator {
                                marked: model.isBestTake || false
                                Layout.preferredWidth: 16
                                Layout.preferredHeight: 16
                                onClicked: {
                                    if (model.isBestTake) {
                                        fileManager.unmarkAsBestTake(model.filepath)
                                    } else {
                                        fileManager.markAsBestTake(model.filepath)
                                    }
                                    fileManager.discoverAudioFiles(fileManager.getCurrentDirectory())
                                }
                            }
                            
                            PartialTakeIndicator {
                                marked: model.isPartialTake || false
                                Layout.preferredWidth: 16
                                Layout.preferredHeight: 16
                                onClicked: {
                                    if (model.isPartialTake) {
                                        fileManager.unmarkAsPartialTake(model.filepath)
                                    } else {
                                        fileManager.markAsPartialTake(model.filepath)
                                    }
                                    fileManager.discoverAudioFiles(fileManager.getCurrentDirectory())
                                }
                            }
                            
                            // File name (compact, with important indicator)
                            Label {
                                text: (model.hasImportantAnnotation ? "⭐ " : "") + model.filename
                                font.pixelSize: Theme.fontSizeSmall
                                color: Theme.textColor
                                Layout.fillWidth: true
                                elide: Text.ElideMiddle
                            }
                            
                            // Duration (compact)
                            Label {
                                text: formatDuration(model.duration || 0)
                                font.pixelSize: Theme.fontSizeSmall
                                color: Theme.textSecondary
                                Layout.preferredWidth: 50
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
                                    
                                    // Auto-switch to Annotations tab if enabled
                                    if (settingsManager && settingsManager.getAutoSwitchAnnotations()) {
                                        libraryTab.switchToAnnotationsTab()
                                    }
                                }
                            }
                            
                            onDoubleClicked: {
                                console.log("Double-clicked file:", model.filepath)
                                // Double click: Load, play, and switch to Annotations tab
                                audioEngine.loadAndPlay(model.filepath)
                                libraryTab.switchToAnnotationsTab()
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
    
    FolderContextMenu {
        id: folderContextMenu
        
        onGenerateFingerprintsRequested: {
            if (folderContextMenu.folderPath && fileManager && fingerprintEngine) {
                // Get all audio files in this folder
                var files = fileManager.discoverAudioFilesRecursive(folderContextMenu.folderPath)
                if (files && files.length > 0) {
                    console.log("Generating fingerprints for", files.length, "files in", folderContextMenu.folderPath)
                    fingerprintEngine.generateFingerprints(files)
                    // Switch to Fingerprints tab
                    // This will be handled by the parent component
                    libraryTab.requestFingerprintsTab()
                } else {
                    console.log("No audio files found in folder:", folderContextMenu.folderPath)
                }
            }
        }
        
        onGenerateWaveformsRequested: {
            if (folderContextMenu.folderPath && fileManager && waveformEngine) {
                // Get all audio files in this folder
                var files = fileManager.discoverAudioFilesRecursive(folderContextMenu.folderPath)
                if (files && files.length > 0) {
                    console.log("Generating waveforms for", files.length, "files in", folderContextMenu.folderPath)
                    // Generate waveforms for all files in background
                    for (var i = 0; i < files.length; i++) {
                        waveformEngine.generateWaveform(files[i])
                    }
                } else {
                    console.log("No audio files found in folder:", folderContextMenu.folderPath)
                }
            }
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
