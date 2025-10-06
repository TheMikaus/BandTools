pragma Singleton
import QtQuick

/*
  Theme.qml - Singleton for application-wide theming
  
  Provides centralized access to colors, fonts, and sizing constants.
  This singleton can be imported in any QML file and accessed via the Theme identifier.
  
  Usage:
    import "styles"
    
    Rectangle {
        color: Theme.backgroundColor
        
        Label {
            font.pixelSize: Theme.fontSizeLarge
            color: Theme.textColor
        }
    }
*/

QtObject {
    id: theme
    
    // Current theme (light or dark) - connected to ColorManager in main.py
    property string currentTheme: "dark"
    
    // === Dark Theme Colors ===
    readonly property color darkBackground: "#2b2b2b"
    readonly property color darkBackgroundLight: "#3b3b3b"
    readonly property color darkBackgroundMedium: "#353535"
    readonly property color darkBorder: "#505050"
    readonly property color darkTextPrimary: "#ffffff"
    readonly property color darkTextSecondary: "#cccccc"
    readonly property color darkTextMuted: "#999999"
    
    // === Light Theme Colors ===
    readonly property color lightBackground: "#f8f8f8"
    readonly property color lightBackgroundLight: "#ffffff"
    readonly property color lightBackgroundMedium: "#f0f0f0"
    readonly property color lightBorder: "#cccccc"
    readonly property color lightTextPrimary: "#000000"
    readonly property color lightTextSecondary: "#666666"
    readonly property color lightTextMuted: "#999999"
    
    // === Accent Colors (theme-independent) ===
    readonly property color accentPrimary: "#2563eb"
    readonly property color accentSuccess: "#4ade80"
    readonly property color accentDanger: "#ef5350"
    readonly property color accentWarning: "#fbbf24"
    readonly property color accentInfo: "#42a5f5"
    
    // === Waveform Colors ===
    readonly property color waveformLeftChannel: "#58a6ff"
    readonly property color waveformRightChannel: "#ff6b58"
    readonly property color waveformPlayhead: "#ff6666"
    readonly property color waveformSelected: "#ffa500"
    
    // === Active Theme Colors (dynamic based on currentTheme) ===
    readonly property color backgroundColor: currentTheme === "dark" ? darkBackground : lightBackground
    readonly property color backgroundLight: currentTheme === "dark" ? darkBackgroundLight : lightBackgroundLight
    readonly property color backgroundMedium: currentTheme === "dark" ? darkBackgroundMedium : lightBackgroundMedium
    readonly property color borderColor: currentTheme === "dark" ? darkBorder : lightBorder
    readonly property color textColor: currentTheme === "dark" ? darkTextPrimary : lightTextPrimary
    readonly property color textSecondary: currentTheme === "dark" ? darkTextSecondary : lightTextSecondary
    readonly property color textMuted: currentTheme === "dark" ? darkTextMuted : lightTextMuted
    
    // === Typography ===
    readonly property int fontSizeSmall: 11
    readonly property int fontSizeNormal: 12
    readonly property int fontSizeMedium: 14
    readonly property int fontSizeLarge: 18
    readonly property int fontSizeXLarge: 24
    readonly property int fontSizeXXLarge: 32
    
    readonly property string fontFamily: "Segoe UI, Roboto, Arial, sans-serif"
    
    // === Spacing ===
    readonly property int spacingSmall: 5
    readonly property int spacingNormal: 10
    readonly property int spacingMedium: 15
    readonly property int spacingLarge: 20
    readonly property int spacingXLarge: 30
    
    // === Sizes ===
    readonly property int buttonHeight: 32
    readonly property int inputHeight: 28
    readonly property int toolbarHeight: 40
    readonly property int statusBarHeight: 24
    readonly property int panelHeaderHeight: 30
    
    // === Border Radius ===
    readonly property int radiusSmall: 4
    readonly property int radiusNormal: 8
    readonly property int radiusLarge: 12
    
    // === Animations ===
    readonly property int animationFast: 150
    readonly property int animationNormal: 250
    readonly property int animationSlow: 400
    
    // === Functions ===
    
    // Set theme programmatically
    function setTheme(themeName) {
        if (themeName === "light" || themeName === "dark") {
            currentTheme = themeName
        }
    }
    
    // Get color with opacity
    function withOpacity(color, opacity) {
        return Qt.rgba(color.r, color.g, color.b, opacity)
    }
}
