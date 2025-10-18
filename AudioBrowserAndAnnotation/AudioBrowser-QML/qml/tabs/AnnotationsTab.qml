import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "../components"
import "../dialogs"
import "../styles"

/**
 * AnnotationsTab
 * 
 * Phase 2: Waveform visualization and annotation management
 */
Item {
    id: annotationsTab
    
    // Signals for cross-tab interactions
    signal requestClipEdit(int clipIndex)
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacingNormal
        spacing: Theme.spacingNormal
        
        // Waveform display
        WaveformDisplay {
            id: waveformDisplay
            Layout.fillWidth: true
            Layout.preferredHeight: 150
            Layout.minimumHeight: 100
            
            filePath: audioEngine ? audioEngine.getCurrentFile() : ""
            autoGenerate: true
            
            onAnnotationDoubleClicked: function(annotationData) {
                // Edit annotation when double-clicked on waveform marker
                var index = annotationManager.findAnnotationIndex(annotationData.timestamp_ms)
                if (index >= 0) {
                    openEditDialog(index)
                }
            }
            
            onClipClicked: function(clipIndex) {
                // When a clip marker is clicked, seek to clip start
                if (clipManager && clipIndex >= 0) {
                    var clip = clipManager.getClip(clipIndex)
                    if (clip && audioEngine) {
                        audioEngine.seek(clip.start_ms)
                    }
                }
            }
            
            onClipDoubleClicked: function(clipIndex) {
                // When a clip marker is double-clicked, switch to Clips tab and select/edit that clip
                if (clipManager && clipIndex >= 0) {
                    // Signal to main window to switch tabs
                    // This will be handled by adding a signal to this tab
                    annotationsTab.requestClipEdit(clipIndex)
                }
            }
        }
        
        // Annotation table and controls
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumHeight: 200
            color: Theme.backgroundLight
            radius: Theme.radiusSmall
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: Theme.spacingNormal
                spacing: Theme.spacingSmall
                
                // Header with controls
                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spacingNormal
                    
                    Label {
                        text: "Annotations (" + annotationManager.getAnnotationCount() + ")"
                        font.pixelSize: Theme.fontSizeNormal
                        font.bold: true
                        color: Theme.textColor
                    }
                    
                    Item { Layout.fillWidth: true }
                    
                    StyledButton {
                        text: "Add"
                        primary: true
                        enabled: audioEngine && audioEngine.getCurrentFile() !== ""
                        Layout.preferredWidth: 80
                        onClicked: openAddDialog()
                    }
                    
                    StyledButton {
                        text: "Edit"
                        enabled: annotationsTable.selectedRow >= 0
                        Layout.preferredWidth: 80
                        onClicked: openEditDialog(annotationsTable.selectedRow)
                    }
                    
                    StyledButton {
                        text: "Delete"
                        danger: true
                        enabled: annotationsTable.selectedRow >= 0
                        Layout.preferredWidth: 80
                        onClicked: deleteAnnotation(annotationsTable.selectedRow)
                    }
                    
                    StyledButton {
                        text: "Clear All"
                        enabled: annotationManager.getAnnotationCount() > 0
                        Layout.preferredWidth: 80
                        onClicked: clearAllDialog.open()
                    }
                    
                    StyledButton {
                        text: "Export..."
                        success: true
                        enabled: annotationManager.getAnnotationCount() > 0
                        Layout.preferredWidth: 80
                        onClicked: exportAnnotationsDialog.open()
                    }
                }
                
                // Filter and display options
                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spacingNormal
                    
                    Label {
                        text: "Filter:"
                        font.pixelSize: Theme.fontSizeSmall
                        color: Theme.textMuted
                    }
                    
                    ComboBox {
                        id: categoryFilter
                        Layout.preferredWidth: 120
                        model: ["All", "timing", "energy", "harmony", "dynamics", "notes"]
                        
                        background: Rectangle {
                            color: Theme.backgroundColor
                            border.color: Theme.borderColor
                            border.width: 1
                            radius: Theme.radiusSmall
                        }
                        
                        contentItem: Text {
                            text: categoryFilter.displayText
                            color: Theme.textColor
                            font.pixelSize: Theme.fontSizeSmall
                            verticalAlignment: Text.AlignVCenter
                            leftPadding: 8
                        }
                        
                        onCurrentTextChanged: {
                            refreshAnnotations()
                        }
                    }
                    
                    Label {
                        text: "User: All Users"
                        font.pixelSize: Theme.fontSizeSmall
                        color: Theme.textMuted
                    }
                    
                    CheckBox {
                        id: showImportantOnly
                        text: "Important only"
                        
                        indicator: Rectangle {
                            implicitWidth: 16
                            implicitHeight: 16
                            x: showImportantOnly.leftPadding
                            y: parent.height / 2 - height / 2
                            radius: 2
                            border.color: Theme.borderColor
                            border.width: 1
                            color: showImportantOnly.checked ? Theme.accentPrimary : Theme.backgroundColor
                            
                            Label {
                                visible: showImportantOnly.checked
                                anchors.centerIn: parent
                                text: "✓"
                                color: "white"
                                font.pixelSize: 12
                            }
                        }
                        
                        contentItem: Text {
                            text: showImportantOnly.text
                            font.pixelSize: Theme.fontSizeSmall
                            color: Theme.textColor
                            leftPadding: showImportantOnly.indicator.width + 6
                            verticalAlignment: Text.AlignVCenter
                        }
                        
                        onCheckedChanged: {
                            refreshAnnotations()
                        }
                    }
                    
                    Item { Layout.fillWidth: true }
                }
                
                // Annotation Set Controls
                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spacingNormal
                    
                    Label {
                        text: "Annotation Set:"
                        font.pixelSize: Theme.fontSizeSmall
                        color: Theme.textMuted
                    }
                    
                    ComboBox {
                        id: annotationSetCombo
                        Layout.preferredWidth: 180
                        
                        model: {
                            var sets = annotationManager.getAnnotationSets()
                            return sets.map(function(set) { return set.name })
                        }
                        
                        background: Rectangle {
                            color: Theme.backgroundColor
                            border.color: Theme.borderColor
                            border.width: 1
                            radius: Theme.radiusSmall
                        }
                        
                        contentItem: Text {
                            text: annotationSetCombo.displayText
                            color: Theme.textColor
                            font.pixelSize: Theme.fontSizeSmall
                            verticalAlignment: Text.AlignVCenter
                            leftPadding: 8
                        }
                        
                        onCurrentIndexChanged: {
                            if (currentIndex >= 0) {
                                var sets = annotationManager.getAnnotationSets()
                                if (currentIndex < sets.length) {
                                    annotationManager.setCurrentSetId(sets[currentIndex].id)
                                }
                            }
                        }
                        
                        Component.onCompleted: {
                            updateSetCombo()
                        }
                    }
                    
                    StyledButton {
                        text: "Add Set"
                        Layout.preferredWidth: 80
                        onClicked: newSetDialog.open()
                    }
                    
                    StyledButton {
                        text: "Rename"
                        Layout.preferredWidth: 80
                        enabled: annotationManager.getAnnotationSets().length > 0
                        onClicked: renameSetDialog.open()
                    }
                    
                    StyledButton {
                        text: "Delete"
                        danger: true
                        Layout.preferredWidth: 80
                        enabled: annotationManager.getAnnotationSets().length > 1
                        onClicked: deleteSetDialog.open()
                    }
                    
                    CheckBox {
                        id: showAllSetsCheckbox
                        text: "Show all visible sets in table"
                        checked: annotationManager.getShowAllSets()
                        
                        indicator: Rectangle {
                            implicitWidth: 16
                            implicitHeight: 16
                            x: showAllSetsCheckbox.leftPadding
                            y: parent.height / 2 - height / 2
                            radius: 2
                            border.color: Theme.borderColor
                            border.width: 1
                            color: showAllSetsCheckbox.checked ? Theme.accentPrimary : Theme.backgroundColor
                            
                            Label {
                                visible: showAllSetsCheckbox.checked
                                anchors.centerIn: parent
                                text: "✓"
                                color: "white"
                                font.pixelSize: 12
                            }
                        }
                        
                        contentItem: Text {
                            text: showAllSetsCheckbox.text
                            font.pixelSize: Theme.fontSizeSmall
                            color: Theme.textColor
                            leftPadding: showAllSetsCheckbox.indicator.width + 6
                            verticalAlignment: Text.AlignVCenter
                        }
                        
                        onCheckedChanged: {
                            annotationManager.setShowAllSets(checked)
                            refreshAnnotations()
                        }
                    }
                    
                    Item { Layout.fillWidth: true }
                }
                
                // Annotation table
                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: Theme.backgroundColor
                    border.color: Theme.borderColor
                    border.width: 1
                    radius: Theme.radiusSmall
                    
                    TableView {
                        id: annotationsTable
                        anchors.fill: parent
                        anchors.margins: 1
                        clip: true
                        
                        model: annotationsModel
                        
                        property int selectedRow: -1
                        
                        // Column widths
                        columnWidthProvider: function(column) {
                            switch(column) {
                                case 0: return 100  // Time
                                case 1: return 100  // Category
                                case 2: return width - 330  // Text (fill remaining)
                                case 3: return 100  // User
                                case 4: return 80   // Important
                                default: return 100
                            }
                        }
                        
                        delegate: Rectangle {
                            implicitHeight: 32
                            color: annotationsTable.selectedRow === row ? 
                                   Theme.backgroundLight : 
                                   (row % 2 === 0 ? Theme.backgroundColor : Theme.backgroundLight)
                            
                            Text {
                                anchors.fill: parent
                                anchors.leftMargin: 8
                                anchors.rightMargin: 8
                                text: display || ""
                                color: Theme.textColor
                                font.pixelSize: Theme.fontSizeSmall
                                verticalAlignment: Text.AlignVCenter
                                elide: Text.ElideRight
                            }
                            
                            MouseArea {
                                anchors.fill: parent
                                onClicked: {
                                    annotationsTable.selectedRow = row
                                    // Seek to annotation time
                                    var annotations = annotationManager.getAnnotations()
                                    if (row < annotations.length) {
                                        audioEngine.seek(annotations[row].timestamp_ms)
                                    }
                                }
                                onDoubleClicked: {
                                    annotationsTable.selectedRow = row
                                    openEditDialog(row)
                                }
                            }
                        }
                    }
                    
                    // Empty state
                    Label {
                        visible: annotationManager.getAnnotationCount() === 0
                        anchors.centerIn: parent
                        text: "No annotations yet\nClick 'Add' or double-click on waveform to create"
                        font.pixelSize: Theme.fontSizeNormal
                        color: Theme.textMuted
                        horizontalAlignment: Text.AlignHCenter
                    }
                }
            }
        }
    }
    
    // Annotation dialog
    AnnotationDialog {
        id: annotationDialog
        anchors.centerIn: Overlay.overlay
        
        onAnnotationAccepted: function(timestampMs, text, category, important, color) {
            annotationManager.addAnnotation(timestampMs, text, category, important, color)
            refreshAnnotations()
        }
        
        onAnnotationUpdated: function(index, timestampMs, text, category, important, color) {
            annotationManager.updateAnnotation(index, timestampMs, text, category, important, color)
            refreshAnnotations()
        }
    }
    
    // Clear all confirmation dialog
    Dialog {
        id: clearAllDialog
        title: "Clear All Annotations"
        modal: true
        standardButtons: Dialog.Yes | Dialog.No
        anchors.centerIn: Overlay.overlay
        
        Label {
            text: "Are you sure you want to delete all annotations?\nThis action cannot be undone."
            color: Theme.textColor
            wrapMode: Text.WordWrap
        }
        
        onAccepted: {
            annotationManager.clearAnnotations()
            refreshAnnotations()
        }
    }
    
    // Update waveform when audio file changes
    Connections {
        target: audioEngine
        
        function onCurrentFileChanged(path) {
            if (path !== "") {
                // TODO: Re-enable when WaveformDisplay is added to this tab
                // waveformDisplay.setFilePath(path)
                annotationManager.setCurrentFile(path)
                updateUserFilter()  // Update user list when file changes
                refreshAnnotations()
                
                // Set BPM for tempo markers
                var fileName = fileManager.getFileName(path)
                var bpm = tempoManager.getBPM(fileName)
                // TODO: Re-enable when WaveformDisplay is added to this tab
                // waveformDisplay.bpm = bpm
            }
        }
    }
    
    // Update when annotation sets change
    Connections {
        target: annotationManager
        
        function onAnnotationSetsChanged() {
            updateSetCombo()
        }
        
        function onCurrentSetChanged(setId) {
            updateSetCombo()
            refreshAnnotations()
        }
        
        function onShowAllSetsChanged(showAll) {
            showAllSetsCheckbox.checked = showAll
            refreshAnnotations()
        }
    }
    
    // Update when annotations change
    Connections {
        target: annotationManager
        
        function onAnnotationsChanged(path) {
            if (path === audioEngine.getCurrentFile()) {
                updateUserFilter()  // Update user list when annotations change
                refreshAnnotations()
            }
        }
    }
    
    // Update when tempo changes
    Connections {
        target: tempoManager
        
        function onTempoDataChanged() {
            // Update BPM for current file
            var currentPath = audioEngine.getCurrentFile()
            if (currentPath !== "") {
                var fileName = fileManager.getFileName(currentPath)
                var bpm = tempoManager.getBPM(fileName)
                // TODO: Re-enable when WaveformDisplay is added to this tab
                // waveformDisplay.bpm = bpm
            }
        }
    }
    
    // ========== Annotation Set Dialogs ==========
    
    // New Set Dialog
    Dialog {
        id: newSetDialog
        title: "Add Annotation Set"
        modal: true
        anchors.centerIn: parent
        width: 400
        
        background: Rectangle {
            color: Theme.backgroundColor
            border.color: Theme.borderColor
            border.width: 1
            radius: Theme.radiusNormal
        }
        
        ColumnLayout {
            anchors.fill: parent
            spacing: Theme.spacingNormal
            
            Label {
                text: "Set Name:"
                font.pixelSize: Theme.fontSizeNormal
                color: Theme.textColor
            }
            
            StyledTextField {
                id: newSetNameField
                Layout.fillWidth: true
                placeholderText: "Enter set name..."
                text: settingsManager ? settingsManager.getCurrentUser() : ""
            }
            
            RowLayout {
                Layout.fillWidth: true
                spacing: Theme.spacingNormal
                
                Item { Layout.fillWidth: true }
                
                StyledButton {
                    text: "Cancel"
                    Layout.preferredWidth: 100
                    onClicked: newSetDialog.close()
                }
                
                StyledButton {
                    text: "Create"
                    primary: true
                    Layout.preferredWidth: 100
                    enabled: newSetNameField.text.trim().length > 0
                    onClicked: {
                        var setName = newSetNameField.text.trim()
                        if (setName.length > 0) {
                            annotationManager.addAnnotationSet(setName, "")
                            updateSetCombo()
                            newSetDialog.close()
                        }
                    }
                }
            }
        }
    }
    
    // Rename Set Dialog
    Dialog {
        id: renameSetDialog
        title: "Rename Annotation Set"
        modal: true
        anchors.centerIn: parent
        width: 400
        
        background: Rectangle {
            color: Theme.backgroundColor
            border.color: Theme.borderColor
            border.width: 1
            radius: Theme.radiusNormal
        }
        
        ColumnLayout {
            anchors.fill: parent
            spacing: Theme.spacingNormal
            
            Label {
                text: "New Name:"
                font.pixelSize: Theme.fontSizeNormal
                color: Theme.textColor
            }
            
            StyledTextField {
                id: renameSetNameField
                Layout.fillWidth: true
                placeholderText: "Enter new name..."
                text: {
                    var currentId = annotationManager.getCurrentSetId()
                    var sets = annotationManager.getAnnotationSets()
                    for (var i = 0; i < sets.length; i++) {
                        if (sets[i].id === currentId) {
                            return sets[i].name
                        }
                    }
                    return ""
                }
            }
            
            RowLayout {
                Layout.fillWidth: true
                spacing: Theme.spacingNormal
                
                Item { Layout.fillWidth: true }
                
                StyledButton {
                    text: "Cancel"
                    Layout.preferredWidth: 100
                    onClicked: renameSetDialog.close()
                }
                
                StyledButton {
                    text: "Rename"
                    primary: true
                    Layout.preferredWidth: 100
                    enabled: renameSetNameField.text.trim().length > 0
                    onClicked: {
                        var newName = renameSetNameField.text.trim()
                        if (newName.length > 0) {
                            var currentId = annotationManager.getCurrentSetId()
                            annotationManager.renameAnnotationSet(currentId, newName)
                            updateSetCombo()
                            renameSetDialog.close()
                        }
                    }
                }
            }
        }
    }
    
    // Delete Set Dialog
    Dialog {
        id: deleteSetDialog
        title: "Delete Annotation Set"
        modal: true
        anchors.centerIn: parent
        width: 500
        
        background: Rectangle {
            color: Theme.backgroundColor
            border.color: Theme.borderColor
            border.width: 1
            radius: Theme.radiusNormal
        }
        
        ColumnLayout {
            anchors.fill: parent
            spacing: Theme.spacingNormal
            
            Label {
                text: {
                    var currentId = annotationManager.getCurrentSetId()
                    var sets = annotationManager.getAnnotationSets()
                    for (var i = 0; i < sets.length; i++) {
                        if (sets[i].id === currentId) {
                            return "Delete set '" + sets[i].name + "'? This removes its annotations permanently."
                        }
                    }
                    return "Delete this annotation set?"
                }
                font.pixelSize: Theme.fontSizeNormal
                color: Theme.textColor
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
            }
            
            RowLayout {
                Layout.fillWidth: true
                spacing: Theme.spacingNormal
                
                Item { Layout.fillWidth: true }
                
                StyledButton {
                    text: "Cancel"
                    Layout.preferredWidth: 100
                    onClicked: deleteSetDialog.close()
                }
                
                StyledButton {
                    text: "Delete"
                    danger: true
                    Layout.preferredWidth: 100
                    onClicked: {
                        var currentId = annotationManager.getCurrentSetId()
                        if (annotationManager.deleteAnnotationSet(currentId)) {
                            updateSetCombo()
                            refreshAnnotations()
                        }
                        deleteSetDialog.close()
                    }
                }
            }
        }
    }
    
    // Helper functions
    function updateSetCombo() {
        // Update combo box model
        var sets = annotationManager.getAnnotationSets()
        var setNames = sets.map(function(set) { return set.name })
        annotationSetCombo.model = setNames
        
        // Set current index to match current set
        var currentId = annotationManager.getCurrentSetId()
        for (var i = 0; i < sets.length; i++) {
            if (sets[i].id === currentId) {
                annotationSetCombo.currentIndex = i
                break
            }
        }
    }
    
    function openAddDialog() {
        annotationDialog.resetDialog()
        annotationDialog.timestampMs = audioEngine.getPosition()
        annotationDialog.updateFields()
        annotationDialog.open()
    }
    
    function openEditDialog(index) {
        if (index < 0) return
        
        var annotation = annotationManager.getAnnotation(index)
        if (annotation && annotation.timestamp_ms !== undefined) {
            annotationDialog.loadAnnotation(
                index,
                annotation.timestamp_ms,
                annotation.text,
                annotation.category || "",
                annotation.important || false,
                annotation.color || "#3498db"
            )
            annotationDialog.open()
        }
    }
    
    function deleteAnnotation(index) {
        if (index >= 0) {
            annotationManager.deleteAnnotation(index)
            annotationsTable.selectedRow = -1
        }
    }
    
    function refreshAnnotations() {
        // Get all annotations (no user filtering - always show all users)
        var annotations = annotationManager.getAnnotations()
        
        // Apply filters
        if (showImportantOnly.checked) {
            // Filter important from current set
            annotations = annotations.filter(function(a) { return a.important })
        }
        
        if (categoryFilter.currentText !== "All") {
            // Filter by category from current set
            annotations = annotations.filter(function(a) { return a.category === categoryFilter.currentText })
        }
        
        annotationsModel.setAnnotations(annotations)
    }
    
    function updateUserFilter() {
        // No-op: User filtering is not currently implemented
        // All users are always shown (see line 753 comment)
        // This function exists to prevent ReferenceError when called
    }
    
    // Initialize
    Component.onCompleted: {
        if (audioEngine.getCurrentFile() !== "") {
            annotationManager.setCurrentFile(audioEngine.getCurrentFile())
            refreshAnnotations()
        }
    }
}
