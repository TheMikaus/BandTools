import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "../components"
import "../styles"

/**
 * FolderNotesTab Component
 * 
 * Tab for managing folder-level notes.
 * Notes are automatically saved as you type (if auto-save is enabled).
 * 
 * Features:
 * - Rich text editing area
 * - Auto-save indicator
 * - Character and word count
 * - Clear notes button
 * - Manual save button
 */
Item {
    id: folderNotesTab
    
    // ========== Properties ==========
    
    property var folderNotesManager: null
    property bool hasUnsavedChanges: folderNotesManager ? folderNotesManager.isModified() : false
    
    // ========== Connections ==========
    
    Connections {
        target: folderNotesManager
        
        function onNotesLoaded(notes) {
            notesTextArea.text = notes;
            hasUnsavedChanges = false;
        }
        
        function onNotesSaved(path) {
            hasUnsavedChanges = false;
            statusLabel.text = "Saved";
            statusLabel.color = Theme.success;
            
            // Reset status after 2 seconds
            statusTimer.restart();
        }
        
        function onNotesChanged(notes) {
            hasUnsavedChanges = true;
            statusLabel.text = "Modified";
            statusLabel.color = Theme.warning;
        }
        
        function onError(message) {
            statusLabel.text = "Error: " + message;
            statusLabel.color = Theme.danger;
            statusTimer.restart();
        }
    }
    
    // Auto-load notes when folder changes
    Connections {
        target: fileManager
        
        function onCurrentDirectoryChanged(path) {
            if (folderNotesManager) {
                folderNotesManager.loadNotesForFolder(path);
            }
        }
    }
    
    // ========== Timer for Status Messages ==========
    
    Timer {
        id: statusTimer
        interval: 2000
        onTriggered: {
            if (!hasUnsavedChanges) {
                statusLabel.text = "";
            }
        }
    }
    
    // ========== Main Layout ==========
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacingMedium
        spacing: Theme.spacingMedium
        
        // ========== Toolbar ==========
        
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacingNormal
            
            StyledLabel {
                text: "Folder Notes"
                heading: true
            }
            
            // Current folder indicator
            StyledLabel {
                text: folderNotesManager ? 
                      (folderNotesManager.getCurrentFolder() || "(No folder selected)") : 
                      ""
                secondary: true
                Layout.fillWidth: true
                elide: Text.ElideMiddle
            }
            
            Item { Layout.fillWidth: true }
            
            // Auto-save toggle
            CheckBox {
                id: autoSaveCheckbox
                text: "Auto-save"
                checked: folderNotesManager ? folderNotesManager.getAutoSaveEnabled() : true
                onCheckedChanged: {
                    if (folderNotesManager) {
                        folderNotesManager.setAutoSaveEnabled(checked);
                    }
                }
                
                ToolTip.visible: hovered
                ToolTip.text: "Automatically save notes as you type"
            }
            
            // Save button
            StyledButton {
                text: "💾 Save"
                primary: true
                enabled: hasUnsavedChanges && folderNotesManager
                onClicked: {
                    if (folderNotesManager) {
                        folderNotesManager.saveNotes();
                    }
                }
                
                ToolTip.visible: hovered
                ToolTip.text: "Manually save notes to disk"
            }
            
            // Clear button
            StyledButton {
                text: "🗑 Clear"
                danger: true
                enabled: folderNotesManager && folderNotesManager.getNotesLength() > 0
                onClicked: clearConfirmDialog.open()
                
                ToolTip.visible: hovered
                ToolTip.text: "Clear all notes for this folder"
            }
        }
        
        // ========== Status Bar ==========
        
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacingNormal
            
            StyledLabel {
                id: statusLabel
                text: ""
                Layout.fillWidth: true
            }
            
            // Character count
            StyledLabel {
                text: {
                    const chars = folderNotesManager ? folderNotesManager.getNotesLength() : 0;
                    const words = folderNotesManager ? folderNotesManager.getNotesWordCount() : 0;
                    return chars + " characters, " + words + " words";
                }
                secondary: true
            }
        }
        
        // ========== Notes Text Area ==========
        
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            
            TextArea {
                id: notesTextArea
                placeholderText: "Enter notes for this folder...\n\n" +
                                 "You can write anything here:\n" +
                                 "• Practice goals\n" +
                                 "• Song arrangements\n" +
                                 "• Technical notes\n" +
                                 "• Reminders\n" +
                                 "• Whatever helps your workflow!"
                
                wrapMode: TextArea.Wrap
                selectByMouse: true
                
                // Styling
                color: Theme.foregroundColor
                font.pixelSize: Theme.fontSizeNormal
                font.family: "Monospace"
                
                background: Rectangle {
                    color: Theme.backgroundLight
                    border.color: notesTextArea.activeFocus ? Theme.accentPrimary : Theme.borderColor
                    border.width: 1
                    radius: Theme.radiusSmall
                }
                
                // Update notes on text change
                onTextChanged: {
                    if (folderNotesManager && text !== folderNotesManager.getCurrentNotes()) {
                        folderNotesManager.updateNotes(text);
                    }
                }
            }
        }
        
        // ========== Help Text ==========
        
        StyledLabel {
            text: "💡 Tip: Notes are saved per folder. Auto-save is enabled by default."
            secondary: true
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }
    }
    
    // ========== Confirmation Dialog ==========
    
    Dialog {
        id: clearConfirmDialog
        title: "Clear Notes"
        modal: true
        anchors.centerIn: parent
        
        standardButtons: Dialog.Yes | Dialog.No
        
        Label {
            text: "Are you sure you want to clear all notes for this folder?\n\n" +
                  "This action cannot be undone."
            color: Theme.foregroundColor
        }
        
        background: Rectangle {
            color: Theme.backgroundColor
            border.color: Theme.borderColor
            border.width: 1
            radius: Theme.radiusSmall
        }
        
        onAccepted: {
            if (folderNotesManager) {
                folderNotesManager.clearNotes();
            }
        }
    }
}
