import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import "../components"
import "../styles"

/**
 * PracticeGoalsDialog Component
 * 
 * Dialog for managing and viewing practice goals.
 * 
 * Features:
 * - Create new goals (weekly, monthly, song-specific)
 * - View active goals with progress bars
 * - Track goal completion and deadlines
 * - Delete completed or expired goals
 */
Dialog {
    id: root
    
    // ========== Properties ==========
    
    // References
    property var practiceGoals: null
    property var practiceStatistics: null
    property var fileManager: null
    
    // Internal state
    property var goalsData: null
    property var statsData: null
    
    // ========== Dialog Configuration ==========
    
    title: "Practice Goals"
    modal: false  // Non-modal to allow continued work
    width: 900
    height: 700
    
    anchors.centerIn: parent
    
    standardButtons: Dialog.Close
    
    // ========== Content ==========
    
    ColumnLayout {
        anchors.fill: parent
        spacing: Theme.spacingNormal
        
        // Tab bar for switching between views
        TabBar {
            id: tabBar
            Layout.fillWidth: true
            
            TabButton {
                text: "Active Goals"
            }
            
            TabButton {
                text: "Manage Goals"
            }
        }
        
        // Stack layout for tab content
        StackLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: tabBar.currentIndex
            
            // Tab 1: Active Goals with progress
            Item {
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
                            text: "<b>Note:</b> Progress is calculated from your practice statistics. " +
                                  "Create goals in the 'Manage Goals' tab."
                            font.pixelSize: Theme.fontSizeSmall
                            color: Theme.textSecondary
                            wrapMode: Text.WordWrap
                        }
                    }
                    
                    // Goals list
                    ScrollView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        
                        ListView {
                            id: goalsListView
                            model: ListModel {
                                id: goalsListModel
                            }
                            spacing: Theme.spacingNormal
                            
                            delegate: Rectangle {
                                width: goalsListView.width - Theme.spacingNormal * 2
                                height: goalCard.height
                                color: "transparent"
                                
                                Rectangle {
                                    id: goalCard
                                    anchors.fill: parent
                                    color: Theme.backgroundLight
                                    border.color: Theme.borderColor
                                    border.width: 1
                                    radius: Theme.radiusSmall
                                    
                                    ColumnLayout {
                                        anchors.fill: parent
                                        anchors.margins: Theme.spacingNormal
                                        spacing: Theme.spacingSmall
                                        
                                        // Goal title
                                        Label {
                                            Layout.fillWidth: true
                                            text: model.title
                                            font.pixelSize: Theme.fontSizeNormal
                                            font.bold: true
                                            color: Theme.textPrimary
                                        }
                                        
                                        // Goal dates
                                        Label {
                                            Layout.fillWidth: true
                                            text: model.dates
                                            font.pixelSize: Theme.fontSizeSmall
                                            font.italic: true
                                            color: Theme.textSecondary
                                        }
                                        
                                        // Progress bar
                                        ProgressBar {
                                            Layout.fillWidth: true
                                            value: model.percentage / 100.0
                                            
                                            background: Rectangle {
                                                implicitHeight: 24
                                                color: Theme.backgroundColor
                                                radius: Theme.radiusSmall
                                                border.color: Theme.borderColor
                                                border.width: 1
                                            }
                                            
                                            contentItem: Rectangle {
                                                implicitHeight: 22
                                                radius: Theme.radiusSmall
                                                color: model.status === "complete" ? "#4CAF50" :
                                                       model.status === "expired" ? "#f44336" :
                                                       model.percentage >= 75 ? "#4CAF50" :
                                                       model.percentage >= 50 ? "#FF9800" : "#2196F3"
                                                
                                                Label {
                                                    anchors.centerIn: parent
                                                    text: model.percentage + "% - " + model.message
                                                    font.pixelSize: Theme.fontSizeSmall
                                                    color: "white"
                                                }
                                            }
                                        }
                                        
                                        // Status message
                                        Label {
                                            Layout.fillWidth: true
                                            text: model.statusMessage
                                            font.pixelSize: Theme.fontSizeSmall
                                            color: model.status === "complete" ? "#4CAF50" :
                                                   model.status === "expired" ? "#f44336" : Theme.textSecondary
                                            wrapMode: Text.WordWrap
                                        }
                                        
                                        // Delete button (for expired/completed goals)
                                        StyledButton {
                                            Layout.alignment: Qt.AlignRight
                                            text: "Delete Goal"
                                            destructive: true
                                            visible: model.status === "complete" || model.status === "expired"
                                            onClicked: {
                                                deleteGoal(model.category, model.goalId)
                                            }
                                        }
                                    }
                                }
                            }
                            
                            // Empty state
                            Label {
                                anchors.centerIn: parent
                                visible: goalsListModel.count === 0
                                text: "No active goals. Create one in the 'Manage Goals' tab!"
                                font.pixelSize: Theme.fontSizeNormal
                                color: Theme.textSecondary
                            }
                        }
                    }
                    
                    // Refresh button
                    RowLayout {
                        Layout.fillWidth: true
                        
                        Item {
                            Layout.fillWidth: true
                        }
                        
                        StyledButton {
                            text: "Refresh Progress"
                            info: true
                            onClicked: {
                                refreshGoals()
                            }
                        }
                    }
                }
            }
            
            // Tab 2: Manage Goals (create new goals)
            Item {
                ColumnLayout {
                    anchors.fill: parent
                    spacing: Theme.spacingNormal
                    
                    Label {
                        text: "Create New Goal"
                        font.pixelSize: Theme.fontSizeLarge
                        font.bold: true
                        color: Theme.textPrimary
                    }
                    
                    // Goal type selection
                    GroupBox {
                        Layout.fillWidth: true
                        title: "Goal Type"
                        
                        ColumnLayout {
                            anchors.fill: parent
                            
                            ComboBox {
                                id: goalCategoryCombo
                                Layout.fillWidth: true
                                model: ["Weekly Goal", "Monthly Goal", "Song-Specific Goal"]
                                
                                onCurrentIndexChanged: {
                                    // Update visibility of song name field
                                    songNameRow.visible = (currentIndex === 2)
                                }
                            }
                        }
                    }
                    
                    // Song name (for song-specific goals)
                    RowLayout {
                        id: songNameRow
                        Layout.fillWidth: true
                        visible: false
                        
                        Label {
                            text: "Song Name:"
                            Layout.preferredWidth: 120
                        }
                        
                        TextField {
                            id: songNameField
                            Layout.fillWidth: true
                            placeholderText: "Enter song name..."
                        }
                    }
                    
                    // Goal target type
                    GroupBox {
                        Layout.fillWidth: true
                        title: "Target Type"
                        
                        ColumnLayout {
                            anchors.fill: parent
                            
                            ComboBox {
                                id: targetTypeCombo
                                Layout.fillWidth: true
                                model: goalCategoryCombo.currentIndex === 2 ? 
                                       ["Practice Count", "Best Takes"] :
                                       ["Practice Time (minutes)", "Session Count"]
                            }
                        }
                    }
                    
                    // Target value
                    RowLayout {
                        Layout.fillWidth: true
                        
                        Label {
                            text: "Target Value:"
                            Layout.preferredWidth: 120
                        }
                        
                        SpinBox {
                            id: targetValueSpinBox
                            Layout.fillWidth: true
                            from: 1
                            to: 10000
                            value: 5
                        }
                    }
                    
                    // Date range
                    GroupBox {
                        Layout.fillWidth: true
                        title: "Date Range"
                        
                        GridLayout {
                            anchors.fill: parent
                            columns: 2
                            rowSpacing: Theme.spacingSmall
                            columnSpacing: Theme.spacingNormal
                            
                            Label {
                                text: "Start Date:"
                            }
                            
                            TextField {
                                id: startDateField
                                Layout.fillWidth: true
                                placeholderText: "YYYY-MM-DD"
                                text: Qt.formatDate(new Date(), "yyyy-MM-dd")
                            }
                            
                            Label {
                                text: "End Date:"
                            }
                            
                            TextField {
                                id: endDateField
                                Layout.fillWidth: true
                                placeholderText: "YYYY-MM-DD"
                                text: {
                                    var endDate = new Date()
                                    if (goalCategoryCombo.currentIndex === 0) {
                                        // Weekly: 7 days from now
                                        endDate.setDate(endDate.getDate() + 7)
                                    } else {
                                        // Monthly: 30 days from now
                                        endDate.setDate(endDate.getDate() + 30)
                                    }
                                    return Qt.formatDate(endDate, "yyyy-MM-dd")
                                }
                            }
                        }
                    }
                    
                    // Create button
                    RowLayout {
                        Layout.fillWidth: true
                        
                        Item {
                            Layout.fillWidth: true
                        }
                        
                        StyledButton {
                            text: "Create Goal"
                            primary: true
                            onClicked: {
                                createNewGoal()
                            }
                        }
                    }
                    
                    Item {
                        Layout.fillHeight: true
                    }
                }
            }
        }
    }
    
    // ========== Functions ==========
    
    function refreshGoals() {
        if (!practiceGoals || !practiceStatistics || !fileManager) {
            console.warn("Missing required managers")
            return
        }
        
        // Get root path and set it for both managers
        var rootPath = fileManager.getCurrentDirectory()
        practiceGoals.setRootPath(rootPath)
        practiceStatistics.setRootPath(rootPath)
        
        // Get statistics
        var statsJson = practiceStatistics.generateStatistics()
        statsData = JSON.parse(statsJson)
        
        // Calculate all goals with progress
        var allGoalsJson = practiceGoals.calculateAllGoalsProgress(statsJson)
        var allGoals = JSON.parse(allGoalsJson)
        
        // Update list model
        goalsListModel.clear()
        
        for (var i = 0; i < allGoals.length; i++) {
            var goal = allGoals[i]
            var progress = goal.progress
            
            // Skip expired goals older than 7 days
            if (progress.status === "expired" && progress.days_remaining < -7) {
                continue
            }
            
            // Build title
            var title = ""
            if (goal.category === "song") {
                title = "Song: " + goal.song_name + " - " + goal.type.replace(/_/g, " ")
            } else {
                title = goal.category.charAt(0).toUpperCase() + goal.category.slice(1) + 
                        " Goal - " + goal.type.replace(/_/g, " ")
            }
            
            // Build dates string
            var dates = goal.start_date + " to " + goal.end_date
            
            // Build status message
            var statusMessage = ""
            if (progress.status === "complete") {
                statusMessage = "✅ Goal completed! Great work!"
            } else if (progress.status === "expired") {
                statusMessage = "⚠️ Goal expired (" + Math.abs(progress.days_remaining) + " days ago)"
            } else if (progress.days_remaining <= 3) {
                statusMessage = "⏰ " + progress.days_remaining + " days remaining"
            } else {
                statusMessage = progress.days_remaining + " days remaining"
            }
            
            goalsListModel.append({
                goalId: goal.id,
                category: goal.category,
                title: title,
                dates: dates,
                percentage: progress.percentage,
                message: progress.message,
                status: progress.status,
                statusMessage: statusMessage
            })
        }
    }
    
    function createNewGoal() {
        if (!practiceGoals || !fileManager) {
            console.warn("Missing required managers")
            return
        }
        
        // Get root path
        var rootPath = fileManager.getCurrentDirectory()
        practiceGoals.setRootPath(rootPath)
        
        // Determine category
        var category = ""
        if (goalCategoryCombo.currentIndex === 0) {
            category = "weekly"
        } else if (goalCategoryCombo.currentIndex === 1) {
            category = "monthly"
        } else {
            category = "song"
        }
        
        // Determine goal type
        var goalType = ""
        if (category === "song") {
            if (targetTypeCombo.currentIndex === 0) {
                goalType = "practice_count"
            } else {
                goalType = "best_take"
            }
            
            // Validate song name
            if (songNameField.text.trim() === "") {
                console.warn("Song name is required for song-specific goals")
                return
            }
            
            // Create song goal
            practiceGoals.createSongGoal(
                songNameField.text.trim(),
                goalType,
                targetValueSpinBox.value,
                startDateField.text,
                endDateField.text
            )
        } else {
            if (targetTypeCombo.currentIndex === 0) {
                goalType = "time"
            } else {
                goalType = "session_count"
            }
            
            // Create regular goal
            practiceGoals.createGoal(
                category,
                goalType,
                targetValueSpinBox.value,
                startDateField.text,
                endDateField.text
            )
        }
        
        // Reset form
        targetValueSpinBox.value = 5
        songNameField.text = ""
        
        // Switch to active goals tab and refresh
        tabBar.currentIndex = 0
        refreshGoals()
    }
    
    function deleteGoal(category, goalId) {
        if (!practiceGoals) {
            return
        }
        
        practiceGoals.deleteGoal(category, goalId)
        refreshGoals()
    }
    
    // ========== Lifecycle ==========
    
    onOpened: {
        console.log("PracticeGoalsDialog opened")
        refreshGoals()
    }
    
    Component.onCompleted: {
        console.log("PracticeGoalsDialog created")
    }
}
