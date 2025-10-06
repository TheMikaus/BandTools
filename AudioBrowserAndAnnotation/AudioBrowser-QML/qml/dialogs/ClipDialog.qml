import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"
import "../styles"

/**
 * ClipDialog Component
 * 
 * Modal dialog for creating and editing audio clips.
 * 
 * Features:
 * - Create new clip or edit existing
 * - Start/end time input with validation
 * - "Use Current" buttons to use playback position
 * - Name and notes fields
 * - Duration calculation and display
 * - Validation before accepting
 */
Dialog {
    id: root
    
    // ========== Properties ==========
    
    // Mode
    property bool isEditMode: false
    property int clipIndex: -1
    
    // Clip data
    property int startMs: 0
    property int endMs: 0
    property string clipName: ""
    property string clipNotes: ""
    
    // References
    property var audioEngine: null
    property var clipManager: null
    
    // ========== Signals ==========
    
    signal clipCreated(int startMs, int endMs, string name, string notes)
    signal clipUpdated(int index, int startMs, int endMs, string name, string notes)
    
    // ========== Dialog Configuration ==========
    
    title: isEditMode ? "Edit Clip" : "New Clip"
    modal: true
    width: 500
    height: 450
    
    anchors.centerIn: parent
    
    standardButtons: Dialog.Ok | Dialog.Cancel
    
    // ========== Helper Functions ==========
    
    // Format time as MM:SS.mmm
    function formatTime(ms) {
        const totalSeconds = Math.floor(ms / 1000);
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        const milliseconds = ms % 1000;
        return minutes.toString().padStart(2, '0') + ":" +
               seconds.toString().padStart(2, '0') + "." +
               milliseconds.toString().padStart(3, '0');
    }
    
    // Parse time string (MM:SS or MM:SS.mmm) to milliseconds
    function parseTime(timeStr) {
        const parts = timeStr.split(':');
        if (parts.length !== 2) return -1;
        
        const minutes = parseInt(parts[0]);
        if (isNaN(minutes) || minutes < 0) return -1;
        
        const secondParts = parts[1].split('.');
        const seconds = parseInt(secondParts[0]);
        if (isNaN(seconds) || seconds < 0 || seconds >= 60) return -1;
        
        let milliseconds = 0;
        if (secondParts.length > 1) {
            milliseconds = parseInt(secondParts[1].padEnd(3, '0'));
            if (isNaN(milliseconds)) milliseconds = 0;
        }
        
        return (minutes * 60 + seconds) * 1000 + milliseconds;
    }
    
    // Validate inputs
    function validate() {
        const start = parseTime(startField.text);
        const end = parseTime(endField.text);
        
        if (start < 0) {
            errorLabel.text = "Invalid start time format. Use MM:SS or MM:SS.mmm";
            return false;
        }
        
        if (end < 0) {
            errorLabel.text = "Invalid end time format. Use MM:SS or MM:SS.mmm";
            return false;
        }
        
        if (start >= end) {
            errorLabel.text = "Start time must be before end time";
            return false;
        }
        
        errorLabel.text = "";
        return true;
    }
    
    // Initialize dialog with values
    function openDialog(editMode, index, start, end, name, notes) {
        isEditMode = editMode;
        clipIndex = index;
        startMs = start;
        endMs = end;
        clipName = name;
        clipNotes = notes;
        
        // Set field values
        startField.text = formatTime(startMs);
        endField.text = formatTime(endMs);
        nameField.text = clipName;
        notesField.text = clipNotes;
        
        errorLabel.text = "";
        
        open();
    }
    
    // ========== Content ==========
    
    contentItem: ColumnLayout {
        spacing: Theme.spacingMedium
        
        // Time inputs
        GroupBox {
            title: "Clip Boundaries"
            Layout.fillWidth: true
            
            background: Rectangle {
                color: Theme.backgroundLight
                border.color: Theme.borderColor
                radius: Theme.radiusSmall
            }
            
            ColumnLayout {
                anchors.fill: parent
                spacing: Theme.spacingNormal
                
                // Start time
                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spacingNormal
                    
                    StyledLabel {
                        text: "Start:"
                        Layout.preferredWidth: 60
                    }
                    
                    StyledTextField {
                        id: startField
                        Layout.fillWidth: true
                        placeholderText: "MM:SS.mmm"
                        
                        onTextChanged: {
                            if (text !== "") {
                                const parsed = parseTime(text);
                                if (parsed >= 0) {
                                    startMs = parsed;
                                    updateDuration();
                                }
                            }
                        }
                    }
                    
                    StyledButton {
                        text: "Current"
                        onClicked: {
                            if (audioEngine) {
                                const currentPos = audioEngine.getPosition();
                                startMs = currentPos;
                                startField.text = formatTime(currentPos);
                                updateDuration();
                            }
                        }
                    }
                }
                
                // End time
                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spacingNormal
                    
                    StyledLabel {
                        text: "End:"
                        Layout.preferredWidth: 60
                    }
                    
                    StyledTextField {
                        id: endField
                        Layout.fillWidth: true
                        placeholderText: "MM:SS.mmm"
                        
                        onTextChanged: {
                            if (text !== "") {
                                const parsed = parseTime(text);
                                if (parsed >= 0) {
                                    endMs = parsed;
                                    updateDuration();
                                }
                            }
                        }
                    }
                    
                    StyledButton {
                        text: "Current"
                        onClicked: {
                            if (audioEngine) {
                                const currentPos = audioEngine.getPosition();
                                endMs = currentPos;
                                endField.text = formatTime(currentPos);
                                updateDuration();
                            }
                        }
                    }
                }
                
                // Duration display
                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spacingNormal
                    
                    StyledLabel {
                        text: "Duration:"
                        Layout.preferredWidth: 60
                    }
                    
                    StyledLabel {
                        id: durationLabel
                        text: formatTime(Math.max(0, endMs - startMs))
                        secondary: true
                    }
                }
            }
        }
        
        // Name input
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacingNormal
            
            StyledLabel {
                text: "Name:"
                Layout.preferredWidth: 80
            }
            
            StyledTextField {
                id: nameField
                Layout.fillWidth: true
                placeholderText: "Clip name (optional)"
            }
        }
        
        // Notes input
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: Theme.spacingSmall
            
            StyledLabel {
                text: "Notes:"
            }
            
            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.preferredHeight: 120
                
                TextArea {
                    id: notesField
                    placeholderText: "Additional notes (optional)"
                    wrapMode: TextEdit.Wrap
                    
                    background: Rectangle {
                        color: Theme.backgroundColor
                        border.color: notesField.activeFocus ? Theme.accentPrimary : Theme.borderColor
                        border.width: 1
                        radius: Theme.radiusSmall
                    }
                    
                    color: Theme.textColor
                    font.pixelSize: Theme.fontSizeNormal
                }
            }
        }
        
        // Error message
        StyledLabel {
            id: errorLabel
            Layout.fillWidth: true
            danger: true
            visible: text !== ""
            wrapMode: Text.WordWrap
        }
    }
    
    // ========== Dialog Actions ==========
    
    onAccepted: {
        if (!validate()) {
            // Reopen dialog to show error
            open();
            return;
        }
        
        const start = parseTime(startField.text);
        const end = parseTime(endField.text);
        const name = nameField.text;
        const notes = notesField.text;
        
        if (isEditMode) {
            clipUpdated(clipIndex, start, end, name, notes);
        } else {
            clipCreated(start, end, name, notes);
        }
    }
    
    // ========== Helper Functions ==========
    
    function updateDuration() {
        durationLabel.text = formatTime(Math.max(0, endMs - startMs));
    }
}
