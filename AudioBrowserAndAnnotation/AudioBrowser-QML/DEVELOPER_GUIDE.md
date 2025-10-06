# AudioBrowser QML - Developer Guide

Quick reference for developing with the QML-based AudioBrowser application.

---

## Project Structure

```
AudioBrowser-QML/
├── main.py                          # Application entry point
├── backend/                         # Python backend modules
│   ├── settings_manager.py         # Settings (QSettings wrapper)
│   ├── color_manager.py            # Theme and colors
│   ├── audio_engine.py             # Audio playback
│   ├── file_manager.py             # File operations
│   └── models.py                   # QML data models
├── qml/                             # QML UI definitions
│   ├── main.qml                    # Main window
│   ├── styles/                     # Theme styling
│   │   ├── Theme.qml               # Theme singleton
│   │   └── qmldir                  # Singleton registration
│   ├── components/                 # Reusable components
│   │   ├── StyledButton.qml
│   │   ├── StyledLabel.qml
│   │   └── StyledTextField.qml
│   └── tabs/                       # Tab views
│       ├── LibraryTab.qml
│       ├── AnnotationsTab.qml
│       └── ClipsTab.qml
├── test_backend.py                 # Backend test script
├── README.md                       # Project documentation
├── PHASE_1_SUMMARY.md             # Phase 1 summary
└── DEVELOPER_GUIDE.md             # This file
```

---

## Running the Application

### Prerequisites
- Python 3.8+
- PyQt6 (auto-installed on first run)

### Launch
```bash
cd AudioBrowser-QML
python3 main.py
```

### Testing
```bash
python3 test_backend.py
```

---

## Backend Development

### Creating a Backend Module

1. **Create module file** in `backend/` directory
2. **Inherit from QObject**
3. **Define signals** for state changes
4. **Add pyqtSlot methods** for QML access
5. **Expose via context property** in main.py

**Template**:
```python
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

class MyModule(QObject):
    # Signals
    dataChanged = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = ""
    
    @pyqtSlot(result=str)
    def getData(self) -> str:
        return self._data
    
    @pyqtSlot(str)
    def setData(self, data: str):
        self._data = data
        self.dataChanged.emit(data)
```

### Exposing to QML

In `main.py`:
```python
my_module = MyModule()
engine.rootContext().setContextProperty("myModule", my_module)
```

### Signal Connections

```python
# Python to Python
module1.dataChanged.connect(module2.updateData)

# QML to Python (in QML)
Connections {
    target: myModule
    function onDataChanged(data) {
        console.log("Data changed:", data)
    }
}
```

---

## QML Development

### Using the Theme Singleton

Always import and use the Theme singleton for consistent styling:

```qml
import "../styles"

Rectangle {
    color: Theme.backgroundColor
    radius: Theme.radiusNormal
    
    Label {
        font.pixelSize: Theme.fontSizeLarge
        color: Theme.textColor
    }
}
```

### Creating a Styled Component

1. **Create file** in `qml/components/`
2. **Import Theme** singleton
3. **Extend base component**
4. **Add variant properties**
5. **Use Theme constants**

**Template**:
```qml
import QtQuick
import QtQuick.Controls
import "../styles"

Button {
    id: myButton
    
    // Variants
    property bool variant1: false
    
    // Styling
    font.pixelSize: Theme.fontSizeNormal
    
    background: Rectangle {
        color: variant1 ? Theme.accentPrimary : Theme.backgroundLight
        radius: Theme.radiusSmall
        
        Behavior on color {
            ColorAnimation { duration: Theme.animationFast }
        }
    }
    
    contentItem: Text {
        text: myButton.text
        color: Theme.textColor
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
}
```

### Creating a Tab View

1. **Create file** in `qml/tabs/`
2. **Use Item as root**
3. **Import components and styles**
4. **Layout with ColumnLayout or similar**

**Template**:
```qml
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"
import "../styles"

Item {
    id: myTab
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacingNormal
        spacing: Theme.spacingNormal
        
        // Tab content here
    }
}
```

### Accessing Backend Modules

Backend modules are available as context properties:

```qml
// Settings
var theme = settingsManager.getTheme()
settingsManager.setTheme("dark")

// Colors
var color = colorManager.getSuccessColor()

// Audio
audioEngine.loadFile("/path/to/file.wav")
audioEngine.play()

// File Manager
fileManager.setCurrentDirectory("/path/to/music")
var files = fileManager.getDiscoveredFiles()

// Models
ListView {
    model: fileListModel
    delegate: Text { text: model.filename }
}
```

---

## Common Patterns

### Loading and Playing Audio

```qml
Button {
    text: "Play"
    onClicked: {
        audioEngine.loadFile(filepath)
        audioEngine.play()
    }
}
```

### Updating File List

```qml
Button {
    text: "Refresh"
    onClicked: {
        var dir = fileManager.getCurrentDirectory()
        fileManager.discoverAudioFiles(dir)
        // fileListModel updates automatically via signal
    }
}
```

### Theme Switching

```qml
Button {
    text: "Toggle Theme"
    onClicked: {
        var current = settingsManager.getTheme()
        var newTheme = current === "dark" ? "light" : "dark"
        settingsManager.setTheme(newTheme)
        Theme.setTheme(newTheme)
    }
}
```

### Handling Backend Signals

```qml
Connections {
    target: audioEngine
    
    function onPlaybackStateChanged(state) {
        console.log("Playback state:", state)
        if (state === "playing") {
            playButton.text = "⏸"
        } else {
            playButton.text = "▶"
        }
    }
}
```

---

## Styling Guidelines

### Colors

Use Theme singleton, never hardcode colors:
```qml
// ✓ Good
color: Theme.textColor

// ✗ Bad
color: "#ffffff"
```

### Spacing

Use Theme spacing constants:
```qml
// ✓ Good
anchors.margins: Theme.spacingNormal

// ✗ Bad
anchors.margins: 10
```

### Font Sizes

Use Theme font size constants:
```qml
// ✓ Good
font.pixelSize: Theme.fontSizeLarge

// ✗ Bad
font.pixelSize: 18
```

### Animations

Use Theme animation durations:
```qml
Behavior on opacity {
    NumberAnimation { duration: Theme.animationFast }
}
```

---

## Data Models

### FileListModel

**Roles**:
- `filepath` - Full file path
- `filename` - File name with extension
- `basename` - File name without extension
- `filesize` - File size in bytes
- `duration` - Duration in milliseconds (0 if not set)
- `extension` - File extension

**Methods**:
```qml
fileListModel.setFiles(filePaths)
fileListModel.clear()
var path = fileListModel.getFilePath(index)
var count = fileListModel.count()
var index = fileListModel.findFileIndex(filepath)
```

### AnnotationsModel

**Roles**:
- `timestamp` - Timestamp in milliseconds
- `category` - Annotation category
- `text` - Annotation text
- `important` - Boolean importance flag
- `color` - Annotation color

**Methods**:
```qml
annotationsModel.setAnnotations(annotationsList)
annotationsModel.clear()
var count = annotationsModel.count()
```

---

## Testing

### Backend Tests

Run the test script:
```bash
python3 test_backend.py
```

Tests:
- Python syntax validation
- QML file existence
- Module imports (if PyQt6 available)

### Manual Testing

1. **Launch application**
2. **Set directory** in Library tab
3. **Browse files** in list view
4. **Double-click** to play audio
5. **Test playback controls** in toolbar
6. **Switch theme** with button
7. **Check tabs** (Library, Annotations, Clips)

---

## Debugging

### Print Debug Info

**Python**:
```python
print(f"Debug: {variable}")
import logging
logging.info("Info message")
```

**QML**:
```qml
console.log("Debug:", variable)
console.error("Error:", errorMessage)
```

### Check Context Properties

In QML:
```qml
Component.onCompleted: {
    console.log("Settings Manager:", settingsManager)
    console.log("Audio Engine:", audioEngine)
}
```

### Backend Errors

Watch the terminal for Python errors and QML warnings.

---

## Performance Tips

1. **Minimize QML updates**: Batch model updates
2. **Use ListView**: For large file lists
3. **Lazy loading**: Load data only when needed
4. **Cache results**: Cache file metadata
5. **Async operations**: Use signals for long operations

---

## Adding a New Feature

### Example: Add a "Play All" Button

1. **Add backend method** (if needed):
```python
# In file_manager.py
@pyqtSlot(result=list)
def getAllAudioFiles(self) -> List[str]:
    return [str(f) for f in self._discovered_files]
```

2. **Add UI component**:
```qml
// In LibraryTab.qml
StyledButton {
    text: "Play All"
    onClicked: {
        var files = fileManager.getAllAudioFiles()
        // Implement playlist logic
    }
}
```

3. **Test** the feature
4. **Document** in appropriate files

---

## Resources

- [Qt QML Documentation](https://doc.qt.io/qt-6/qmlapplications.html)
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [QML Best Practices](https://doc.qt.io/qt-6/qml-codingconventions.html)
- [Qt Quick Controls](https://doc.qt.io/qt-6/qtquickcontrols-index.html)

---

## Getting Help

1. Check existing components for examples
2. Review backend module implementations
3. Consult Qt documentation
4. Test with `test_backend.py`
5. Check terminal output for errors

---

## Contributing

When adding new code:

1. Follow existing patterns
2. Use Theme singleton for styling
3. Add pyqtSlot decorators for QML methods
4. Emit signals for state changes
5. Test your changes
6. Update documentation

---

## Quick Reference

### Backend Modules

| Module | Purpose | Key Methods |
|--------|---------|-------------|
| SettingsManager | Settings | getTheme(), setTheme(), getVolume() |
| ColorManager | Colors | getSuccessColor(), setTheme() |
| AudioEngine | Playback | play(), pause(), stop(), loadFile() |
| FileManager | Files | setCurrentDirectory(), discoverAudioFiles() |
| FileListModel | File List | setFiles(), getFilePath() |
| AnnotationsModel | Annotations | setAnnotations(), clear() |

### QML Components

| Component | Purpose | Variants |
|-----------|---------|----------|
| StyledButton | Button | primary, danger, success |
| StyledLabel | Label | heading, secondary, muted, success, danger, warning |
| StyledTextField | Input | error |

### Theme Constants

| Category | Examples |
|----------|----------|
| Colors | backgroundColor, textColor, accentPrimary |
| Fonts | fontSizeSmall, fontSizeNormal, fontSizeLarge |
| Spacing | spacingSmall, spacingNormal, spacingLarge |
| Sizing | buttonHeight, toolbarHeight, statusBarHeight |
| Radius | radiusSmall, radiusNormal, radiusLarge |
| Animation | animationFast, animationNormal, animationSlow |
