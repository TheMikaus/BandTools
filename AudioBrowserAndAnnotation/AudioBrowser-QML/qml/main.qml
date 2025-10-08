import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import QtQuick.Window
import "components"
import "styles"
import "tabs"
import "dialogs"

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 1200
    height: 800
    title: "AudioBrowser (QML) - Phase 7 (Additional Features - 55% Complete)"
    
    // Use theme for background color
    color: Theme.backgroundColor
    
    // Save window geometry on close
    onClosing: {
        saveWindowGeometry()
    }
    
    // Restore window geometry on startup
    Component.onCompleted: {
        restoreWindowGeometry()
    }
    
    // Functions for workspace layout management
    function saveWindowGeometry() {
        // Save window position and size
        settingsManager.setGeometry(JSON.stringify({
            x: mainWindow.x,
            y: mainWindow.y,
            width: mainWindow.width,
            height: mainWindow.height
        }))
        console.log("Window geometry saved")
    }
    
    function restoreWindowGeometry() {
        try {
            var geometryStr = settingsManager.getGeometry()
            if (geometryStr) {
                var geometry = JSON.parse(geometryStr)
                if (geometry.width && geometry.height) {
                    mainWindow.width = geometry.width
                    mainWindow.height = geometry.height
                }
                if (geometry.x !== undefined && geometry.y !== undefined) {
                    mainWindow.x = geometry.x
                    mainWindow.y = geometry.y
                }
                console.log("Window geometry restored")
            }
        } catch (e) {
            console.log("Could not restore window geometry:", e)
        }
    }
    
    function resetToDefaultLayout() {
        mainWindow.width = 1200
        mainWindow.height = 800
        // Center window on screen
        var screen = mainWindow.screen
        if (screen) {
            mainWindow.x = (screen.width - mainWindow.width) / 2
            mainWindow.y = (screen.height - mainWindow.height) / 2
        }
        saveWindowGeometry()
        console.log("Layout reset to defaults")
    }
    
    // Menu Bar
    menuBar: MenuBar {
        Menu {
            title: "&File"
            
            MenuItem {
                text: "Open Folder..."
                onTriggered: {
                    libraryTab.openFolderDialog()
                }
            }
            
            Menu {
                id: recentFoldersMenu
                title: "Recent Folders"
                
                // Dynamically populated
                Instantiator {
                    model: settingsManager.getRecentFolders()
                    delegate: MenuItem {
                        text: modelData
                        onTriggered: {
                            fileManager.setCurrentDirectory(modelData)
                            libraryTab.setDirectoryFromCode(modelData)
                        }
                    }
                    onObjectAdded: function(index, object) {
                        recentFoldersMenu.insertItem(index, object)
                    }
                    onObjectRemoved: function(index, object) {
                        recentFoldersMenu.removeItem(object)
                    }
                }
                
                MenuSeparator {
                    visible: settingsManager.getRecentFolders().length > 0
                }
                
                MenuItem {
                    text: "Clear Recent Folders"
                    enabled: settingsManager.getRecentFolders().length > 0
                    onTriggered: {
                        settingsManager.clearRecentFolders()
                        recentFoldersMenu.update()
                    }
                }
            }
            
            MenuSeparator {}
            
            MenuItem {
                text: "Export Best Takes Package..."
                onTriggered: {
                    exportBestTakesDialog.open()
                }
            }
            
            MenuSeparator {}
            
            MenuItem {
                text: "Exit"
                onTriggered: Qt.quit()
            }
        }
        
        Menu {
            title: "&View"
            
            MenuItem {
                text: "Toggle Now Playing Panel"
                checkable: true
                checked: !nowPlayingPanel.collapsed
                onTriggered: {
                    nowPlayingPanel.collapsed = !nowPlayingPanel.collapsed
                    settingsManager.setNowPlayingCollapsed(nowPlayingPanel.collapsed)
                }
            }
            
            MenuSeparator {}
            
            MenuItem {
                text: "Save Layout"
                onTriggered: {
                    mainWindow.saveWindowGeometry()
                    // Show confirmation
                    console.log("Layout saved")
                }
            }
            
            MenuItem {
                text: "Reset Layout to Default"
                onTriggered: {
                    mainWindow.resetToDefaultLayout()
                }
            }
        }
        
        Menu {
            title: "&Edit"
            
            MenuItem {
                text: "Preferences..."
                onTriggered: {
                    preferencesDialog.open()
                }
            }
            
            MenuItem {
                text: "Auto-Generation Settings..."
                onTriggered: {
                    autoGenDialog.open()
                }
            }
            
            MenuSeparator {}
            
            MenuItem {
                text: "Restore from Backup..."
                onTriggered: {
                    backupDialog.open()
                }
            }
        }
        
        Menu {
            title: "&Help"
            
            MenuItem {
                text: "Documentation Browser..."
                onTriggered: {
                    documentationBrowserDialog.open()
                }
            }
            
            MenuItem {
                text: "Keyboard Shortcuts"
                onTriggered: {
                    keyboardShortcutsDialog.open()
                }
            }
            
            MenuSeparator {}
            
            MenuItem {
                text: "About"
                onTriggered: {
                    aboutDialog.open()
                }
            }
        }
        
        background: Rectangle {
            color: Theme.backgroundLight
        }
    }
    
    // Main content area with tabs
    ColumnLayout {
        anchors.fill: parent
        spacing: 0
        
        // Toolbar
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: Theme.toolbarHeight
            color: Theme.backgroundLight
            
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: Theme.spacingNormal
                anchors.rightMargin: Theme.spacingNormal
                spacing: Theme.spacingLarge
                
                Label {
                    text: "AudioBrowser QML"
                    font.pixelSize: Theme.fontSizeLarge
                    font.bold: true
                    color: Theme.textColor
                }
                
                Item { Layout.fillWidth: true }
                
                // Playback controls
                PlaybackControls {
                    Layout.fillWidth: true
                    Layout.preferredHeight: Theme.toolbarHeight
                }
                
                Item { width: Theme.spacingSmall }
                
                // Auto-switch checkbox
                CheckBox {
                    id: autoSwitchCheckbox
                    text: "Auto-switch to Annotations"
                    checked: settingsManager.getAutoSwitchAnnotations()
                    
                    indicator: Rectangle {
                        implicitWidth: 16
                        implicitHeight: 16
                        x: autoSwitchCheckbox.leftPadding
                        y: parent.height / 2 - height / 2
                        radius: 2
                        border.color: Theme.borderColor
                        border.width: 1
                        color: autoSwitchCheckbox.checked ? Theme.accentPrimary : Theme.backgroundColor
                        
                        Label {
                            visible: autoSwitchCheckbox.checked
                            anchors.centerIn: parent
                            text: "✓"
                            color: "white"
                            font.pixelSize: 12
                        }
                    }
                    
                    contentItem: Text {
                        text: autoSwitchCheckbox.text
                        font.pixelSize: Theme.fontSizeSmall
                        color: Theme.textColor
                        leftPadding: autoSwitchCheckbox.indicator.width + 6
                        verticalAlignment: Text.AlignVCenter
                    }
                    
                    onCheckedChanged: {
                        settingsManager.setAutoSwitchAnnotations(checked)
                    }
                    
                    ToolTip.visible: hovered
                    ToolTip.text: "Automatically switch to Annotations tab when selecting a file"
                    ToolTip.delay: 500
                }
                
                Item { width: Theme.spacingSmall }
                
                // Theme toggle
                StyledButton {
                    text: "Theme"
                    success: true
                    onClicked: {
                        var currentTheme = settingsManager.getTheme()
                        var newTheme = currentTheme === "dark" ? "light" : "dark"
                        settingsManager.setTheme(newTheme)
                        Theme.setTheme(newTheme)
                    }
                }
            }
        }
        
        // Tab bar
        TabBar {
            id: tabBar
            Layout.fillWidth: true
            background: Rectangle {
                color: Theme.backgroundLight
            }
            
            TabButton {
                text: "Library"
                font.pixelSize: Theme.fontSizeNormal
                
                background: Rectangle {
                    color: tabBar.currentIndex === 0 ? Theme.backgroundColor : Theme.backgroundLight
                }
                
                contentItem: Text {
                    text: parent.text
                    font: parent.font
                    color: tabBar.currentIndex === 0 ? Theme.textColor : Theme.textSecondary
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
            
            TabButton {
                text: "Annotations"
                font.pixelSize: Theme.fontSizeNormal
                
                background: Rectangle {
                    color: tabBar.currentIndex === 1 ? Theme.backgroundColor : Theme.backgroundLight
                }
                
                contentItem: Text {
                    text: parent.text
                    font: parent.font
                    color: tabBar.currentIndex === 1 ? Theme.textColor : Theme.textSecondary
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
            
            TabButton {
                text: "Clips"
                font.pixelSize: Theme.fontSizeNormal
                
                background: Rectangle {
                    color: tabBar.currentIndex === 2 ? Theme.backgroundColor : Theme.backgroundLight
                }
                
                contentItem: Text {
                    text: parent.text
                    font: parent.font
                    color: tabBar.currentIndex === 2 ? Theme.textColor : Theme.textSecondary
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
            
            TabButton {
                text: "Folder Notes"
                font.pixelSize: Theme.fontSizeNormal
                
                background: Rectangle {
                    color: tabBar.currentIndex === 3 ? Theme.backgroundColor : Theme.backgroundLight
                }
                
                contentItem: Text {
                    text: parent.text
                    font: parent.font
                    color: tabBar.currentIndex === 3 ? Theme.textColor : Theme.textSecondary
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
            
            TabButton {
                text: "Fingerprints"
                font.pixelSize: Theme.fontSizeNormal
                
                background: Rectangle {
                    color: tabBar.currentIndex === 4 ? Theme.backgroundColor : Theme.backgroundLight
                }
                
                contentItem: Text {
                    text: parent.text
                    font: parent.font
                    color: tabBar.currentIndex === 4 ? Theme.textColor : Theme.textSecondary
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
        }
        
        // Tab content
        StackLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: tabBar.currentIndex
            
            LibraryTab {
                id: libraryTab
            }
            
            AnnotationsTab {
                id: annotationsTab
            }
            
            ClipsTab {
                id: clipsTab
            }
            
            FolderNotesTab {
                id: folderNotesTab
            }
            
            FingerprintsTab {
                id: fingerprintsTab
            }
        }
        
        // Now Playing Panel
        NowPlayingPanel {
            id: nowPlayingPanel
            
            onAnnotationRequested: function(text) {
                // Add annotation at current playback position
                if (audioEngine.getCurrentFile()) {
                    var timestamp = audioEngine.getPosition()
                    annotationManager.addAnnotation(timestamp, text, "General", false)
                    // Switch to annotations tab if auto-switch is enabled
                    if (settingsManager.getAutoSwitchAnnotations()) {
                        tabBar.currentIndex = 1
                    }
                }
            }
        }
        
        // Batch operations dialogs
        BatchRenameDialog {
            id: batchRenameDialog
            
            onRenameCompleted: {
                // Refresh file list after rename
                var dir = fileManager.getCurrentDirectory()
                if (dir.length > 0) {
                    fileManager.discoverAudioFiles(dir)
                }
                progressDialog.showResult(true, "Rename operation completed successfully")
            }
        }
        
        BatchConvertDialog {
            id: batchConvertDialog
            
            onConversionCompleted: {
                // Refresh file list after conversion
                var dir = fileManager.getCurrentDirectory()
                if (dir.length > 0) {
                    fileManager.discoverAudioFiles(dir)
                }
            }
        }
        
        ProgressDialog {
            id: progressDialog
        }
        
        // Practice Statistics Dialog
        PracticeStatisticsDialog {
            id: practiceStatisticsDialog
        }
        
        // Practice Goals Dialog
        PracticeGoalsDialog {
            id: practiceGoalsDialog
        }
        
        // Setlist Builder Dialog
        SetlistBuilderDialog {
            id: setlistBuilderDialog
        }
        
        // Export Annotations Dialog
        ExportAnnotationsDialog {
            id: exportAnnotationsDialog
            currentFile: audioEngine.currentFile
        }
        
        // About Dialog
        AboutDialog {
            id: aboutDialog
        }
        
        // Preferences Dialog
        PreferencesDialog {
            id: preferencesDialog
        }
        
        // Keyboard Shortcuts Dialog
        KeyboardShortcutsDialog {
            id: keyboardShortcutsDialog
        }
        
        // Documentation Browser Dialog
        DocumentationBrowserDialog {
            id: documentationBrowserDialog
            documentationManager: documentationManager
        }
        
        // Auto-Generation Settings Dialog
        AutoGenerationSettingsDialog {
            id: autoGenDialog
            settingsManager: settingsManager
        }
        
        // Backup Selection Dialog
        BackupSelectionDialog {
            id: backupDialog
            backupManager: backupManager
            currentFolder: fileManager.currentDirectory
            rootPath: fileManager.currentDirectory
        }
        
        ExportBestTakesDialog {
            id: exportBestTakesDialog
        }
        
        // Status bar
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: Theme.statusBarHeight
            color: Theme.backgroundLight
            
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: Theme.spacingNormal
                anchors.rightMargin: Theme.spacingNormal
                spacing: Theme.spacingLarge
                
                Label {
                    text: audioEngine.getPlaybackState() === "playing" ? "Playing" : "Ready"
                    font.pixelSize: Theme.fontSizeSmall
                    color: audioEngine.getPlaybackState() === "playing" ? Theme.accentSuccess : Theme.textMuted
                }
                
                Label {
                    text: audioEngine.getCurrentFile() ? "File: " + fileManager.getFileName(audioEngine.getCurrentFile()) : ""
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.textMuted
                    elide: Text.ElideMiddle
                    Layout.fillWidth: true
                }
                
                Label {
                    text: "Phase 7 (Additional Features) • Theme: " + settingsManager.getTheme()
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.textMuted
                }
            }
        }
    }
    
    // Update status bar when playback state changes
    Connections {
        target: audioEngine
        
        function onPlaybackStateChanged(state) {
            // Force status bar to update
            mainWindow.update()
        }
    }
    
    // Keyboard shortcuts
    Shortcut {
        sequence: "Space"
        // Only activate if no text input has focus
        enabled: !mainWindow.activeFocusItem || 
                 mainWindow.activeFocusItem.toString().indexOf("TextField") === -1 &&
                 mainWindow.activeFocusItem.toString().indexOf("TextArea") === -1 &&
                 mainWindow.activeFocusItem.toString().indexOf("TextEdit") === -1
        onActivated: audioEngine.togglePlayPause()
    }
    
    Shortcut {
        sequence: "Escape"
        onActivated: audioEngine.stop()
    }
    
    Shortcut {
        sequence: "Ctrl+T"
        onActivated: {
            var currentTheme = settingsManager.getTheme()
            var newTheme = currentTheme === "dark" ? "light" : "dark"
            settingsManager.setTheme(newTheme)
            Theme.setTheme(newTheme)
        }
    }
    
    Shortcut {
        sequence: "Ctrl+1"
        onActivated: tabBar.currentIndex = 0
    }
    
    Shortcut {
        sequence: "Ctrl+2"
        onActivated: tabBar.currentIndex = 1
    }
    
    Shortcut {
        sequence: "Ctrl+3"
        onActivated: tabBar.currentIndex = 2
    }
    
    Shortcut {
        sequence: "Ctrl+4"
        onActivated: tabBar.currentIndex = 3
    }
    
    Shortcut {
        sequence: "+"
        onActivated: {
            var vol = audioEngine.getVolume()
            audioEngine.setVolume(Math.min(100, vol + 5))
        }
    }
    
    Shortcut {
        sequence: "-"
        onActivated: {
            var vol = audioEngine.getVolume()
            audioEngine.setVolume(Math.max(0, vol - 5))
        }
    }
    
    // Navigation shortcuts
    Shortcut {
        sequence: "Left"
        onActivated: audioEngine.seekBackward(5000)  // 5 seconds back
    }
    
    Shortcut {
        sequence: "Right"
        onActivated: audioEngine.seekForward(5000)  // 5 seconds forward
    }
    
    // Annotation shortcuts
    Shortcut {
        sequence: "Ctrl+A"
        // Only activate if not in text input
        enabled: !mainWindow.activeFocusItem || 
                 mainWindow.activeFocusItem.toString().indexOf("TextField") === -1 &&
                 mainWindow.activeFocusItem.toString().indexOf("TextArea") === -1 &&
                 mainWindow.activeFocusItem.toString().indexOf("TextEdit") === -1
        onActivated: {
            if (audioEngine.getCurrentFile() !== "") {
                annotationsTab.openAddDialog()
            }
        }
    }
    
    // Clip marker shortcuts
    Shortcut {
        sequence: "["
        // Only activate if not in text input
        enabled: !mainWindow.activeFocusItem || 
                 mainWindow.activeFocusItem.toString().indexOf("TextField") === -1 &&
                 mainWindow.activeFocusItem.toString().indexOf("TextArea") === -1 &&
                 mainWindow.activeFocusItem.toString().indexOf("TextEdit") === -1
        onActivated: {
            if (audioEngine.getCurrentFile() !== "") {
                clipsTab.setClipStartMarker()
            }
        }
    }
    
    Shortcut {
        sequence: "]"
        // Only activate if not in text input
        enabled: !mainWindow.activeFocusItem || 
                 mainWindow.activeFocusItem.toString().indexOf("TextField") === -1 &&
                 mainWindow.activeFocusItem.toString().indexOf("TextArea") === -1 &&
                 mainWindow.activeFocusItem.toString().indexOf("TextEdit") === -1
        onActivated: {
            if (audioEngine.getCurrentFile() !== "") {
                clipsTab.setClipEndMarker()
            }
        }
    }
    
    // Additional keyboard shortcuts for feature parity (Issue #12)
    
    // Dialog shortcuts
    Shortcut {
        sequence: "Ctrl+Shift+T"
        onActivated: setlistBuilderDialog.open()
    }
    
    Shortcut {
        sequence: "Ctrl+Shift+S"
        onActivated: practiceStatisticsDialog.open()
    }
    
    Shortcut {
        sequence: "Ctrl+Shift+G"
        onActivated: practiceGoalsDialog.open()
    }
    
    Shortcut {
        sequence: "Ctrl+,"
        onActivated: preferencesDialog.open()
    }
    
    Shortcut {
        sequence: "Ctrl+/"
        onActivated: keyboardShortcutsDialog.open()
    }
    
    Shortcut {
        sequence: "F1"
        onActivated: keyboardShortcutsDialog.open()
    }
    
    // File operations
    Shortcut {
        sequence: "Ctrl+O"
        onActivated: libraryTab.openFolderDialog()
    }
    
    Shortcut {
        sequence: "F5"
        onActivated: {
            var dir = fileManager.getCurrentDirectory()
            if (dir.length > 0) {
                fileManager.discoverAudioFiles(dir)
            }
        }
    }
    
    Shortcut {
        sequence: "Ctrl+Q"
        onActivated: Qt.quit()
    }
    
    // Tab switching with Ctrl+5 for Fingerprints tab
    Shortcut {
        sequence: "Ctrl+5"
        onActivated: tabBar.currentIndex = 4
    }
    
    // Workspace layout shortcuts
    Shortcut {
        sequence: "Ctrl+Shift+L"
        onActivated: mainWindow.saveWindowGeometry()
    }
    
    Shortcut {
        sequence: "Ctrl+Shift+R"
        onActivated: mainWindow.resetToDefaultLayout()
    }
    
    // Documentation browser shortcut
    Shortcut {
        sequence: "Ctrl+Shift+H"
        onActivated: documentationBrowserDialog.open()
    }
    
    // Batch operations signal connections
    Connections {
        target: batchOperations
        
        function onOperationStarted(operationName) {
            progressDialog.openDialog(operationName)
        }
        
        function onOperationProgress(done, total, currentFile) {
            progressDialog.updateProgress(done, total, currentFile)
        }
        
        function onOperationFinished(success, message) {
            progressDialog.showResult(success, message)
        }
        
        function onErrorOccurred(errorMessage) {
            progressDialog.showResult(false, "Error: " + errorMessage)
        }
    }
}
