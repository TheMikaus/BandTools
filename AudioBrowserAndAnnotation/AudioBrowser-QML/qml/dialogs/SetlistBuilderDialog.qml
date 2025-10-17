import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import QtQuick.Dialogs
import "../components"
import "../styles"

/**
 * SetlistBuilderDialog Component
 * 
 * Dialog for managing and organizing performance setlists.
 * 
 * Features:
 * - Create/rename/delete setlists
 * - Add songs from any folder to setlists
 * - Reorder songs with move up/down
 * - View song details (name, duration, best take status)
 * - Add performance notes
 * - Validate setlists (missing files, no best takes)
 * - Export setlists to text files
 */
Dialog {
    id: root
    
    // ========== Properties ==========
    
    // References
    property var setlistManager: null
    property var fileManager: null
    
    // Internal state
    property string currentSetlistId: ""
    property var setlistDetails: null
    
    // ========== Dialog Configuration ==========
    
    title: "Setlist Builder"
    modal: false  // Non-modal to allow continued work
    width: 1100
    height: 750
    
    anchors.centerIn: parent
    
    standardButtons: Dialog.Close
    
    // Set background color for better visibility
    background: Rectangle {
        color: Theme.backgroundColor
        border.color: Theme.borderColor
        border.width: 1
        radius: Theme.radiusSmall
    }
    
    // ========== Functions ==========
    
    function refreshSetlists() {
        if (!setlistManager) return
        
        var jsonStr = setlistManager.getAllSetlistsJson()
        var setlists = JSON.parse(jsonStr)
        setlistsModel.clear()
        
        for (var i = 0; i < setlists.length; i++) {
            setlistsModel.append(setlists[i])
        }
    }
    
    function loadSetlistDetails(setlistId) {
        if (!setlistManager || !setlistId) return
        
        currentSetlistId = setlistId
        var jsonStr = setlistManager.getSetlistDetails(setlistId)
        setlistDetails = JSON.parse(jsonStr)
        
        // Update UI
        setlistNameLabel.text = setlistDetails.name || "Unnamed Setlist"
        notesEdit.text = setlistDetails.notes || ""
        
        // Update songs table
        songsModel.clear()
        var totalDuration = 0
        
        for (var i = 0; i < setlistDetails.songs.length; i++) {
            var song = setlistDetails.songs[i]
            songsModel.append(song)
            totalDuration += song.duration_sec
        }
        
        // Update total duration
        totalDurationLabel.text = "Total Duration: " + formatDuration(totalDuration)
    }
    
    function formatDuration(seconds) {
        if (seconds <= 0) return "0:00"
        
        var hours = Math.floor(seconds / 3600)
        var minutes = Math.floor((seconds % 3600) / 60)
        var secs = seconds % 60
        
        if (hours > 0) {
            return hours + ":" + (minutes < 10 ? "0" : "") + minutes + ":" + (secs < 10 ? "0" : "") + secs
        } else {
            return minutes + ":" + (secs < 10 ? "0" : "") + secs
        }
    }
    
    function validateCurrentSetlist() {
        if (!setlistManager || !currentSetlistId) return
        
        var jsonStr = setlistManager.validateSetlist(currentSetlistId)
        var result = JSON.parse(jsonStr)
        
        if (result.error) {
            validationText.text = "Error: " + result.error
            return
        }
        
        var text = "<b>Validation Results:</b><br><br>"
        text += "Total Songs: " + result.total_songs + "<br>"
        text += "Total Duration: " + result.total_duration_formatted + "<br><br>"
        
        if (result.valid) {
            text += "<font color='#4CAF50'><b>✓ Setlist is valid!</b></font><br><br>"
        } else {
            text += "<font color='#f44336'><b>⚠ Issues found:</b></font><br><br>"
        }
        
        if (result.missing_files.length > 0) {
            text += "<font color='#f44336'><b>Missing Files (" + result.missing_files.length + "):</b></font><br>"
            for (var i = 0; i < result.missing_files.length; i++) {
                var missing = result.missing_files[i]
                text += "&nbsp;&nbsp;" + missing.index + ". " + missing.name + " [" + missing.folder + "]<br>"
            }
            text += "<br>"
        }
        
        if (result.no_best_takes.length > 0) {
            text += "<font color='#FFA726'><b>No Best Take (" + result.no_best_takes.length + "):</b></font><br>"
            for (var j = 0; j < result.no_best_takes.length; j++) {
                var noBest = result.no_best_takes[j]
                text += "&nbsp;&nbsp;" + noBest.index + ". " + noBest.name + "<br>"
            }
        }
        
        validationText.text = text
    }
    
    // ========== Content ==========
    
    ColumnLayout {
        anchors.fill: parent
        spacing: Theme.spacingNormal
        
        // Tab bar
        TabBar {
            id: tabBar
            Layout.fillWidth: true
            
            TabButton {
                text: "Manage Setlists"
            }
            
            TabButton {
                text: "Export & Validation"
            }
        }
        
        // Stack layout for tabs
        StackLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: tabBar.currentIndex
            
            // Tab 1: Manage Setlists
            Item {
                RowLayout {
                    anchors.fill: parent
                    spacing: Theme.spacingNormal
                    
                    // Left panel: Setlists list
                    ColumnLayout {
                        Layout.fillHeight: true
                        Layout.preferredWidth: 300
                        spacing: Theme.spacingSmall
                        
                        Label {
                            text: "Your Setlists"
                            font.pixelSize: Theme.fontSizeLarge
                            font.bold: true
                            color: Theme.textPrimary
                        }
                        
                        // Setlists list
                        ScrollView {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            
                            ListView {
                                id: setlistsListView
                                model: ListModel { id: setlistsModel }
                                spacing: 2
                                clip: true
                                
                                delegate: Rectangle {
                                    width: ListView.view.width
                                    height: 60
                                    color: ListView.isCurrentItem ? Theme.highlightColor : Theme.backgroundMedium
                                    radius: Theme.radiusSmall
                                    
                                    MouseArea {
                                        anchors.fill: parent
                                        onClicked: {
                                            setlistsListView.currentIndex = index
                                            loadSetlistDetails(model.id)
                                        }
                                    }
                                    
                                    ColumnLayout {
                                        anchors.fill: parent
                                        anchors.margins: Theme.spacingSmall
                                        spacing: 2
                                        
                                        Label {
                                            text: model.name
                                            font.pixelSize: Theme.fontSizeNormal
                                            font.bold: true
                                            color: Theme.textPrimary
                                            Layout.fillWidth: true
                                            elide: Text.ElideRight
                                        }
                                        
                                        Label {
                                            text: model.songCount + " songs"
                                            font.pixelSize: Theme.fontSizeSmall
                                            color: Theme.textSecondary
                                        }
                                    }
                                }
                            }
                        }
                        
                        // Setlist management buttons
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: Theme.spacingSmall
                            
                            Button {
                                text: "New"
                                Layout.fillWidth: true
                                onClicked: newSetlistDialog.open()
                            }
                            
                            Button {
                                text: "Rename"
                                Layout.fillWidth: true
                                enabled: currentSetlistId !== ""
                                onClicked: {
                                    renameDialog.oldName = setlistNameLabel.text
                                    renameDialog.open()
                                }
                            }
                            
                            Button {
                                text: "Delete"
                                Layout.fillWidth: true
                                enabled: currentSetlistId !== ""
                                onClicked: deleteDialog.open()
                            }
                        }
                    }
                    
                    // Right panel: Setlist details
                    ColumnLayout {
                        Layout.fillHeight: true
                        Layout.fillWidth: true
                        spacing: Theme.spacingSmall
                        
                        Label {
                            id: setlistNameLabel
                            text: "Select a setlist"
                            font.pixelSize: Theme.fontSizeLarge
                            font.bold: true
                            color: Theme.textPrimary
                        }
                        
                        // Songs table
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: Theme.backgroundMedium
                            radius: Theme.radiusSmall
                            
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: Theme.spacingSmall
                                spacing: 0
                                
                                // Table header
                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 30
                                    color: Theme.backgroundDark
                                    
                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.margins: Theme.spacingSmall
                                        spacing: Theme.spacingSmall
                                        
                                        Label {
                                            text: "#"
                                            Layout.preferredWidth: 30
                                            font.bold: true
                                            color: Theme.textPrimary
                                        }
                                        Label {
                                            text: "Song Name"
                                            Layout.fillWidth: true
                                            font.bold: true
                                            color: Theme.textPrimary
                                        }
                                        Label {
                                            text: "Best"
                                            Layout.preferredWidth: 40
                                            font.bold: true
                                            color: Theme.textPrimary
                                        }
                                        Label {
                                            text: "Duration"
                                            Layout.preferredWidth: 70
                                            font.bold: true
                                            color: Theme.textPrimary
                                        }
                                        Label {
                                            text: "Folder"
                                            Layout.preferredWidth: 150
                                            font.bold: true
                                            color: Theme.textPrimary
                                        }
                                    }
                                }
                                
                                // Songs list
                                ScrollView {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    
                                    ListView {
                                        id: songsListView
                                        model: ListModel { id: songsModel }
                                        spacing: 2
                                        clip: true
                                        
                                        delegate: Rectangle {
                                            width: ListView.view.width
                                            height: 40
                                            color: index % 2 === 0 ? Theme.backgroundMedium : Theme.backgroundLight
                                            
                                            RowLayout {
                                                anchors.fill: parent
                                                anchors.margins: Theme.spacingSmall
                                                spacing: Theme.spacingSmall
                                                
                                                Label {
                                                    text: (index + 1) + "."
                                                    Layout.preferredWidth: 30
                                                    color: model.exists ? Theme.textPrimary : "#f44336"
                                                    font.bold: !model.exists
                                                }
                                                Label {
                                                    text: model.provided_name
                                                    Layout.fillWidth: true
                                                    elide: Text.ElideRight
                                                    color: model.exists ? Theme.textPrimary : "#f44336"
                                                }
                                                Label {
                                                    text: model.is_best_take ? "✓" : ""
                                                    Layout.preferredWidth: 40
                                                    color: "#4CAF50"
                                                    font.bold: true
                                                }
                                                Label {
                                                    text: formatDuration(model.duration_sec)
                                                    Layout.preferredWidth: 70
                                                    color: Theme.textSecondary
                                                }
                                                Label {
                                                    text: model.folder
                                                    Layout.preferredWidth: 150
                                                    elide: Text.ElideMiddle
                                                    color: Theme.textSecondary
                                                    font.pixelSize: Theme.fontSizeSmall
                                                }
                                            }
                                            
                                            MouseArea {
                                                anchors.fill: parent
                                                onClicked: songsListView.currentIndex = index
                                            }
                                        }
                                    }
                                }
                            }
                        }
                        
                        // Total duration
                        Label {
                            id: totalDurationLabel
                            text: "Total Duration: 0:00"
                            font.pixelSize: Theme.fontSizeNormal
                            font.bold: true
                            color: Theme.textPrimary
                        }
                        
                        // Song management buttons
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: Theme.spacingSmall
                            
                            Button {
                                text: "Add Current Song"
                                enabled: currentSetlistId !== "" && fileManager
                                onClicked: {
                                    if (fileManager && fileManager.getCurrentDirectory() && fileManager.currentFile) {
                                        var folder = fileManager.getCurrentDirectory().split('/').pop()
                                        var filename = fileManager.currentFile
                                        if (setlistManager.addSong(currentSetlistId, folder, filename)) {
                                            loadSetlistDetails(currentSetlistId)
                                        }
                                    }
                                }
                            }
                            
                            Button {
                                text: "Remove Song"
                                enabled: currentSetlistId !== "" && songsListView.currentIndex >= 0
                                onClicked: {
                                    if (setlistManager.removeSong(currentSetlistId, songsListView.currentIndex)) {
                                        loadSetlistDetails(currentSetlistId)
                                    }
                                }
                            }
                            
                            Button {
                                text: "↑ Move Up"
                                enabled: currentSetlistId !== "" && songsListView.currentIndex > 0
                                onClicked: {
                                    var idx = songsListView.currentIndex
                                    if (setlistManager.moveSong(currentSetlistId, idx, idx - 1)) {
                                        loadSetlistDetails(currentSetlistId)
                                        songsListView.currentIndex = idx - 1
                                    }
                                }
                            }
                            
                            Button {
                                text: "↓ Move Down"
                                enabled: currentSetlistId !== "" && songsListView.currentIndex >= 0 && songsListView.currentIndex < songsModel.count - 1
                                onClicked: {
                                    var idx = songsListView.currentIndex
                                    if (setlistManager.moveSong(currentSetlistId, idx, idx + 1)) {
                                        loadSetlistDetails(currentSetlistId)
                                        songsListView.currentIndex = idx + 1
                                    }
                                }
                            }
                        }
                        
                        // Performance notes
                        Label {
                            text: "Performance Notes:"
                            font.bold: true
                            color: Theme.textPrimary
                        }
                        
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 100
                            color: Theme.backgroundMedium
                            radius: Theme.radiusSmall
                            
                            ScrollView {
                                anchors.fill: parent
                                
                                TextArea {
                                    id: notesEdit
                                    placeholderText: "Add notes about this setlist (key changes, tuning, gear requirements, etc.)"
                                    wrapMode: TextArea.Wrap
                                    color: Theme.textPrimary
                                    background: Rectangle { color: "transparent" }
                                    
                                    onTextChanged: {
                                        if (currentSetlistId) {
                                            setlistManager.updateNotes(currentSetlistId, text)
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            
            // Tab 2: Export & Validation
            Item {
                ColumnLayout {
                    anchors.fill: parent
                    spacing: Theme.spacingNormal
                    
                    Label {
                        text: "Export & Validation"
                        font.pixelSize: Theme.fontSizeLarge
                        font.bold: true
                        color: Theme.textPrimary
                    }
                    
                    // Setlist selection for export
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: Theme.spacingSmall
                        
                        Label {
                            text: "Select Setlist:"
                            color: Theme.textPrimary
                        }
                        
                        ComboBox {
                            id: exportSetlistCombo
                            Layout.fillWidth: true
                            model: setlistsModel
                            textRole: "name"
                            
                            onCurrentIndexChanged: {
                                if (currentIndex >= 0) {
                                    var setlistId = setlistsModel.get(currentIndex).id
                                    loadSetlistDetails(setlistId)
                                }
                            }
                        }
                    }
                    
                    // Validation results
                    Label {
                        text: "Validation Results:"
                        font.bold: true
                        color: Theme.textPrimary
                    }
                    
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 200
                        color: Theme.backgroundMedium
                        radius: Theme.radiusSmall
                        
                        ScrollView {
                            anchors.fill: parent
                            anchors.margins: Theme.spacingSmall
                            
                            Label {
                                id: validationText
                                text: "Click 'Validate' to check the selected setlist"
                                wrapMode: Text.WordWrap
                                color: Theme.textPrimary
                                textFormat: Text.RichText
                            }
                        }
                    }
                    
                    // Export and validation buttons
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: Theme.spacingSmall
                        
                        Button {
                            text: "Validate Setlist"
                            enabled: currentSetlistId !== ""
                            onClicked: validateCurrentSetlist()
                        }
                        
                        Button {
                            text: "Export as Text"
                            enabled: currentSetlistId !== ""
                            onClicked: exportFileDialog.open()
                        }
                        
                        Item { Layout.fillWidth: true }
                    }
                    
                    Item { Layout.fillHeight: true }
                }
            }
        }
    }
    
    // ========== Dialogs ==========
    
    // New setlist dialog
    Dialog {
        id: newSetlistDialog
        title: "New Setlist"
        modal: true
        anchors.centerIn: parent
        standardButtons: Dialog.Ok | Dialog.Cancel
        
        ColumnLayout {
            spacing: Theme.spacingNormal
            
            Label {
                text: "Enter setlist name:"
                color: Theme.textPrimary
            }
            
            TextField {
                id: newSetlistNameField
                Layout.preferredWidth: 300
                placeholderText: "e.g., Summer Tour 2024"
                color: Theme.textPrimary
                
                onAccepted: newSetlistDialog.accept()
            }
        }
        
        onAccepted: {
            if (newSetlistNameField.text.trim() && setlistManager) {
                setlistManager.createSetlist(newSetlistNameField.text.trim())
                refreshSetlists()
                newSetlistNameField.text = ""
            }
        }
        
        onOpened: newSetlistNameField.forceActiveFocus()
    }
    
    // Rename dialog
    Dialog {
        id: renameDialog
        title: "Rename Setlist"
        modal: true
        anchors.centerIn: parent
        standardButtons: Dialog.Ok | Dialog.Cancel
        
        property string oldName: ""
        
        ColumnLayout {
            spacing: Theme.spacingNormal
            
            Label {
                text: "Enter new name:"
                color: Theme.textPrimary
            }
            
            TextField {
                id: renameField
                Layout.preferredWidth: 300
                text: renameDialog.oldName
                color: Theme.textPrimary
                
                onAccepted: renameDialog.accept()
            }
        }
        
        onAccepted: {
            if (renameField.text.trim()) {
                setlistManager.renameSetlist(currentSetlistId, renameField.text.trim())
                refreshSetlists()
                loadSetlistDetails(currentSetlistId)
            }
        }
        
        onOpened: {
            renameField.selectAll()
            renameField.forceActiveFocus()
        }
    }
    
    // Delete confirmation dialog
    Dialog {
        id: deleteDialog
        title: "Delete Setlist"
        modal: true
        anchors.centerIn: parent
        standardButtons: Dialog.Yes | Dialog.No
        
        Label {
            text: "Are you sure you want to delete '" + setlistNameLabel.text + "'?"
            color: Theme.textPrimary
        }
        
        onAccepted: {
            setlistManager.deleteSetlist(currentSetlistId)
            currentSetlistId = ""
            setlistDetails = null
            setlistNameLabel.text = "Select a setlist"
            notesEdit.text = ""
            songsModel.clear()
            totalDurationLabel.text = "Total Duration: 0:00"
            refreshSetlists()
        }
    }
    
    // Export file dialog
    FileDialog {
        id: exportFileDialog
        fileMode: FileDialog.SaveFile
        defaultSuffix: "txt"
        nameFilters: ["Text files (*.txt)"]
        
        onAccepted: {
            var path = selectedFile.toString().replace("file://", "")
            if (setlistManager.exportToText(currentSetlistId, path)) {
                console.log("Setlist exported successfully")
            }
        }
    }
    
    // ========== Initialization ==========
    
    Component.onCompleted: {
        refreshSetlists()
    }
}
