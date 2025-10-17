# QML Binding Loop Fix

## Issue
The application was displaying numerous QML binding loop warnings on startup:

```
file:///c:/Work/ToolDev/BandTools/AudioBrowserAndAnnotation/AudioBrowser-QML/qml/main.qml:750:9: QML SetlistBuilderDialog: Binding loop detected for property "setlistManager"
file:///c:/Work/ToolDev/BandTools/AudioBrowserAndAnnotation/AudioBrowser-QML/qml/main.qml:742:9: QML PracticeGoalsDialog: Binding loop detected for property "practiceGoals"
file:///c:/Work/ToolDev/BandTools/AudioBrowserAndAnnotation/AudioBrowser-QML/qml/main.qml:742:9: QML PracticeGoalsDialog: Binding loop detected for property "practiceStatistics"
file:///c:/Work/ToolDev/BandTools/AudioBrowserAndAnnotation/AudioBrowser-QML/qml/main.qml:742:9: QML PracticeGoalsDialog: Binding loop detected for property "fileManager"
file:///c:/Work/ToolDev/BandTools/AudioBrowserAndAnnotation/AudioBrowser-QML/qml/main.qml:735:9: QML PracticeStatisticsDialog: Binding loop detected for property "practiceStatistics"
file:///c:/Work/ToolDev/BandTools/AudioBrowserAndAnnotation/AudioBrowser-QML/qml/main.qml:735:9: QML PracticeStatisticsDialog: Binding loop detected for property "fileManager"
file:///c:/Work/ToolDev/BandTools/AudioBrowserAndAnnotation/AudioBrowser-QML/qml/tabs/LibraryTab.qml:616:5: QML FolderContextMenu: Binding loop detected for property "fingerprintEngine"
file:///c:/Work/ToolDev/BandTools/AudioBrowserAndAnnotation/AudioBrowser-QML/qml/tabs/LibraryTab.qml:616:5: QML FolderContextMenu: Binding loop detected for property "waveformEngine"
file:///c:/Work/ToolDev/BandTools/AudioBrowserAndAnnotation/AudioBrowser-QML/qml/tabs/LibraryTab.qml:616:5: QML FolderContextMenu: Binding loop detected for property "fileManager"
```

## Root Cause

The binding loops were caused by a circular reference pattern:

1. Components/dialogs defined local properties with names matching context properties:
   ```qml
   Dialog {
       property var practiceStatistics: null
       property var fileManager: null
   }
   ```

2. These properties were then bound to context properties in main.qml:
   ```qml
   PracticeStatisticsDialog {
       practiceStatistics: practiceStatistics  // Left side = local property, right side = context property
       fileManager: fileManager
   }
   ```

3. This created a binding loop because QML couldn't determine if `practiceStatistics` on the right side referred to the local property or the context property.

## Solution

The fix involved two steps:

### Step 1: Remove Property Bindings from Instantiation

**main.qml** - Removed property bindings from dialog instantiations:
```diff
 PracticeStatisticsDialog {
     id: practiceStatisticsDialog
-    practiceStatistics: practiceStatistics
-    fileManager: fileManager
 }

 PracticeGoalsDialog {
     id: practiceGoalsDialog
-    practiceGoals: practiceGoals
-    practiceStatistics: practiceStatistics
-    fileManager: fileManager
 }

 SetlistBuilderDialog {
     id: setlistBuilderDialog
-    setlistManager: setlistManager
 }
```

**LibraryTab.qml** - Removed property bindings from component instantiation:
```diff
 FolderContextMenu {
     id: folderContextMenu
-    fingerprintEngine: typeof fingerprintEngine !== 'undefined' ? fingerprintEngine : null
-    waveformEngine: typeof waveformEngine !== 'undefined' ? waveformEngine : null
-    fileManager: typeof fileManager !== 'undefined' ? fileManager : null
 }
```

### Step 2: Remove Local Property Definitions from Components

**PracticeStatisticsDialog.qml**:
```diff
 Dialog {
     // Properties
-    property var practiceStatistics: null
-    property var fileManager: null
     property string currentStatsJson: ""
     property string currentHtml: ""
     
     // Now uses context properties directly
     function refreshStatistics() {
-        if (!root.practiceStatistics) return
+        if (!practiceStatistics) return  // Uses context property
     }
 }
```

**PracticeGoalsDialog.qml**:
```diff
 Dialog {
-    property var practiceGoals: null
-    property var practiceStatistics: null
-    property var fileManager: null
     property var goalsData: null
 }
```

**SetlistBuilderDialog.qml**:
```diff
 Dialog {
-    property var setlistManager: null
-    property var fileManager: null
     property string currentSetlistId: ""
 }
```

**FolderContextMenu.qml**:
```diff
 Menu {
     property string folderPath: ""
     property string folderName: ""
-    property var fingerprintEngine: null
-    property var waveformEngine: null
-    property var fileManager: null
 }
```

## Why This Works

In QML, context properties set via `QQmlContext::setContextProperty()` are globally available throughout the QML document tree. By removing the local property definitions and bindings, we allow components to access these context properties directly without any ambiguity.

The context properties are set in `main.py`:
```python
ctx = engine.rootContext()
ctx.setContextProperty("practiceStatistics", practice_statistics)
ctx.setContextProperty("practiceGoals", practice_goals)
ctx.setContextProperty("setlistManager", setlist_manager)
ctx.setContextProperty("fileManager", file_manager)
ctx.setContextProperty("fingerprintEngine", fingerprint_engine)
ctx.setContextProperty("waveformEngine", waveform_engine)
```

## Files Changed

1. **qml/main.qml** - Removed property bindings for:
   - PracticeStatisticsDialog
   - PracticeGoalsDialog
   - SetlistBuilderDialog

2. **qml/tabs/LibraryTab.qml** - Removed property bindings for:
   - FolderContextMenu

3. **qml/dialogs/PracticeStatisticsDialog.qml** - Removed local property definitions

4. **qml/dialogs/PracticeGoalsDialog.qml** - Removed local property definitions

5. **qml/dialogs/SetlistBuilderDialog.qml** - Removed local property definitions

6. **qml/components/FolderContextMenu.qml** - Removed local property definitions

## Testing

All existing tests pass:
- `test_binding_loop_fixes.py` - ✓ All dialogs pass binding loop checks
- `test_qml_binding_fixes.py` - ✓ All binding loop and signal fixes validated
- `validate_binding_fixes.py` - ✓ Custom validation confirms all fixes in place

## Impact

- **No functional changes** - Components still have full access to all backend managers
- **Performance** - Slight improvement by eliminating binding loop overhead
- **Code clarity** - Clearer that components use global context properties
- **Maintainability** - Less redundant code, easier to understand data flow
