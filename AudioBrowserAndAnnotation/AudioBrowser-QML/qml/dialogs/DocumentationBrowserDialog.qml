import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../styles"

Dialog {
    id: docBrowserDialog
    title: "Documentation Browser"
    modal: true
    width: 1000
    height: 700
    
    property var documentationManager
    property var allDocuments: []
    property var filteredDocuments: []
    property string currentDocPath: ""
    property string currentDocTitle: ""
    
    Component.onCompleted: {
        loadDocuments()
    }
    
    onOpened: {
        // Reset to first document when opening
        if (filteredDocuments.length > 0) {
            documentList.currentIndex = 0
            loadDocument(0)
        }
        searchField.text = ""
        searchField.forceActiveFocus()
    }
    
    function loadDocuments() {
        if (!documentationManager) {
            console.error("DocumentationManager not set")
            return
        }
        
        allDocuments = documentationManager.getDocuments()
        filteredDocuments = allDocuments
        
        if (filteredDocuments.length > 0) {
            documentList.currentIndex = 0
            loadDocument(0)
        } else {
            documentTitle.text = "No Documentation Found"
            documentContent.text = "Documentation folder not found or empty.\n\n" +
                                  "Please ensure the 'docs' folder exists in the application directory."
        }
    }
    
    function filterDocuments() {
        var query = searchField.text.trim()
        if (query === "") {
            filteredDocuments = allDocuments
        } else {
            filteredDocuments = documentationManager.searchDocuments(query)
        }
        
        // Select first item after filtering
        if (filteredDocuments.length > 0) {
            documentList.currentIndex = 0
            loadDocument(0)
        } else {
            documentTitle.text = "No Results"
            documentContent.text = "No documentation found matching: " + query
        }
    }
    
    function loadDocument(index) {
        if (index < 0 || index >= filteredDocuments.length) return
        
        var doc = filteredDocuments[index]
        currentDocPath = doc.filepath
        currentDocTitle = doc.category + ": " + doc.title
        
        documentTitle.text = currentDocTitle
        
        var content = documentationManager.loadDocument(currentDocPath)
        documentContent.text = content
        
        // Scroll to top
        documentContent.cursorPosition = 0
    }
    
    // Main layout
    RowLayout {
        anchors.fill: parent
        spacing: 10
        
        // Left side: Document list with search
        ColumnLayout {
            Layout.preferredWidth: 300
            Layout.fillHeight: true
            spacing: 10
            
            Label {
                text: "Search:"
                font.bold: true
                color: colorManager ? colorManager.getColor("text") : "black"
            }
            
            TextField {
                id: searchField
                Layout.fillWidth: true
                placeholderText: "Filter documents..."
                color: colorManager ? colorManager.getColor("text") : "black"
                background: Rectangle {
                    color: colorManager ? colorManager.getColor("background") : "white"
                    border.color: colorManager ? colorManager.getColor("border") : "gray"
                    border.width: 1
                    radius: 3
                }
                
                onTextChanged: {
                    filterDocuments()
                }
                
                Keys.onDownPressed: {
                    documentList.forceActiveFocus()
                    if (documentList.currentIndex < documentList.count - 1) {
                        documentList.currentIndex++
                    }
                }
            }
            
            Label {
                text: filteredDocuments.length + " document(s)"
                color: colorManager ? colorManager.getColor("textMuted") : "gray"
                font.pixelSize: 11
            }
            
            ListView {
                id: documentList
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                
                model: filteredDocuments.length
                
                delegate: ItemDelegate {
                    width: ListView.view.width
                    
                    required property int index
                    
                    background: Rectangle {
                        color: {
                            if (parent.ListView.isCurrentItem) {
                                return colorManager ? colorManager.getColor("primary") : "#3498db"
                            } else if (parent.hovered) {
                                return colorManager ? colorManager.getColor("hover") : "#ecf0f1"
                            }
                            return colorManager ? colorManager.getColor("background") : "white"
                        }
                    }
                    
                    contentItem: ColumnLayout {
                        spacing: 2
                        
                        Label {
                            text: filteredDocuments[index].category
                            font.pixelSize: 10
                            font.bold: true
                            color: {
                                if (documentList.currentIndex === index) {
                                    return "white"
                                }
                                return colorManager ? colorManager.getColor("textMuted") : "gray"
                            }
                        }
                        
                        Label {
                            text: filteredDocuments[index].title
                            font.pixelSize: 12
                            color: {
                                if (documentList.currentIndex === index) {
                                    return "white"
                                }
                                return colorManager ? colorManager.getColor("text") : "black"
                            }
                            wrapMode: Text.WordWrap
                            Layout.fillWidth: true
                        }
                    }
                    
                    onClicked: {
                        documentList.currentIndex = index
                        loadDocument(index)
                    }
                }
                
                ScrollBar.vertical: ScrollBar {
                    policy: ScrollBar.AsNeeded
                }
                
                Keys.onUpPressed: {
                    if (currentIndex === 0) {
                        searchField.forceActiveFocus()
                    }
                }
            }
        }
        
        // Right side: Document content viewer
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 10
            
            Label {
                id: documentTitle
                text: "Select a document"
                font.pixelSize: 16
                font.bold: true
                color: colorManager ? colorManager.getColor("text") : "black"
                Layout.fillWidth: true
            }
            
            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                
                TextArea {
                    id: documentContent
                    readOnly: true
                    wrapMode: Text.Wrap
                    selectByMouse: true
                    selectByKeyboard: true
                    color: colorManager ? colorManager.getColor("text") : "black"
                    font.family: "Monospace"
                    font.pixelSize: 12
                    background: Rectangle {
                        color: colorManager ? colorManager.getColor("backgroundAlt") : "#f8f9fa"
                        border.color: colorManager ? colorManager.getColor("border") : "lightgray"
                        border.width: 1
                        radius: 3
                    }
                    
                    // Enable keyboard shortcuts for copy
                    Keys.onPressed: (event) => {
                        if (event.modifiers & Qt.ControlModifier) {
                            if (event.key === Qt.Key_C) {
                                copy()
                                event.accepted = true
                            } else if (event.key === Qt.Key_A) {
                                selectAll()
                                event.accepted = true
                            }
                        }
                    }
                }
            }
            
            // Bottom buttons
            RowLayout {
                Layout.fillWidth: true
                spacing: 10
                
                Label {
                    text: "Tip: Use Ctrl+F in your browser to search within the document"
                    color: colorManager ? colorManager.getColor("textMuted") : "gray"
                    font.pixelSize: 10
                    Layout.fillWidth: true
                }
                
                Button {
                    text: "Close"
                    onClicked: docBrowserDialog.accept()
                    
                    background: Rectangle {
                        color: parent.pressed ? "#2c3e50" : (parent.hovered ? "#34495e" : "#7f8c8d")
                        radius: 3
                    }
                    
                    contentItem: Text {
                        text: parent.text
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                }
            }
        }
    }
}
