import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "../components"
import "../styles"

/**
 * PracticeStatisticsDialog Component
 * 
 * Modal dialog for displaying practice statistics.
 * 
 * Features:
 * - Display practice session history
 * - Show most/least practiced songs
 * - Display overall summary statistics
 * - Refresh statistics on demand
 * - Non-modal to allow continued work
 */
Dialog {
    id: root
    
    // ========== Properties ==========
    
    // Internal state
    property string currentStatsJson: ""
    property string currentHtml: ""
    
    // ========== Dialog Configuration ==========
    
    title: "Practice Statistics"
    modal: false  // Non-modal to allow continued work
    width: 800
    height: 600
    
    anchors.centerIn: parent
    
    standardButtons: Dialog.Close
    
    // Set background color for better visibility
    background: Rectangle {
        color: Theme.backgroundColor
        border.color: Theme.borderColor
        border.width: 1
        radius: Theme.radiusSmall
    }
    
    // ========== Content ==========
    
    ColumnLayout {
        anchors.fill: parent
        spacing: Theme.spacingNormal
        
        // Information note
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: infoLabel.height + Theme.spacingNormal * 2
            color: Theme.backgroundLight
            radius: Theme.radiusSmall
            
            Label {
                id: infoLabel
                anchors.fill: parent
                anchors.margins: Theme.spacingNormal
                text: "<b>Note:</b> Statistics are calculated from practice folders when this dialog is opened or refreshed. " +
                      "Data is not cached - each refresh analyzes your practice folders in real-time."
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.textSecondary
                wrapMode: Text.WordWrap
            }
        }
        
        // Statistics display area
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: Theme.backgroundColor
            border.color: Theme.borderColor
            border.width: 1
            radius: Theme.radiusSmall
            
            ScrollView {
                anchors.fill: parent
                anchors.margins: 1
                
                TextEdit {
                    id: statsTextEdit
                    readOnly: true
                    textFormat: TextEdit.RichText
                    text: root.currentHtml
                    color: Theme.textColor
                    font.pixelSize: Theme.fontSizeNormal
                    wrapMode: TextEdit.WordWrap
                    selectByMouse: true
                    
                    // Padding
                    padding: Theme.spacingNormal
                }
            }
        }
        
        // Button layout
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacingNormal
            
            StyledButton {
                text: "Refresh Statistics"
                onClicked: {
                    root.refreshStatistics()
                }
            }
            
            Item { Layout.fillWidth: true }
            
            Label {
                id: statusLabel
                text: ""
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.textSecondary
            }
        }
    }
    
    // ========== Functions ==========
    
    function refreshStatistics() {
        if (!practiceStatistics) {
            root.currentHtml = "<h2>Error</h2><p>Practice statistics manager not initialized</p>"
            return
        }
        
        if (!fileManager) {
            root.currentHtml = "<h2>Error</h2><p>File manager not initialized</p>"
            return
        }
        
        // Set root path from file manager
        const rootPath = fileManager.getCurrentDirectory()
        if (!rootPath || rootPath.length === 0) {
            root.currentHtml = "<h2>No Directory Selected</h2><p>Please select a practice folder directory first.</p>"
            statusLabel.text = "No directory selected"
            return
        }
        
        statusLabel.text = "Generating statistics..."
        
        // Set root path and generate statistics
        practiceStatistics.setRootPath(rootPath)
        root.currentStatsJson = practiceStatistics.generateStatistics()
        
        // Format as HTML
        root.currentHtml = practiceStatistics.formatStatisticsAsHtml(root.currentStatsJson)
        
        statusLabel.text = "Statistics updated: " + new Date().toLocaleString()
    }
    
    // ========== Lifecycle ==========
    
    onOpened: {
        // Generate statistics when dialog opens
        refreshStatistics()
    }
    
    Component.onCompleted: {
        console.log("PracticeStatisticsDialog created")
    }
}
