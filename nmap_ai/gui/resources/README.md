# GUI Resources Directory

This directory contains static resources and assets for the NMAP-AI graphical user interface.

## Resource Types

### Icons and Images
- **Application Icons**: Main application icon in various sizes
- **Action Icons**: Icons for buttons, menu items, and toolbars
- **Status Icons**: Icons indicating scan status, results, and alerts
- **Network Icons**: Icons representing different network devices and services

### Stylesheets
- **Main Stylesheet**: Primary application styling (CSS/QSS)
- **Theme Files**: Light and dark theme configurations
- **Custom Styles**: Component-specific styling overrides

### UI Files
- **Designer Files**: Qt Designer .ui files for complex dialogs
- **Template Files**: UI template definitions
- **Layout Files**: Predefined layout configurations

### Fonts and Typography
- **Custom Fonts**: Application-specific font files
- **Icon Fonts**: Font-based icon sets
- **Typography Configs**: Font size and style definitions

## File Organization

```
resources/
├── icons/
│   ├── app/          # Application icons
│   ├── actions/      # Action icons
│   └── status/       # Status indicators
├── styles/
│   ├── main.qss      # Main stylesheet
│   └── themes/       # Theme files
├── ui/
│   └── dialogs/      # UI definition files
└── fonts/            # Font files
```

## Resource Loading

Resources are loaded by the GUI application using Qt's resource system. They are embedded into the application during build time for optimal performance.

## Formats Supported

- **Images**: PNG, SVG, ICO, JPG
- **Stylesheets**: QSS, CSS
- **Fonts**: TTF, OTF
- **UI Files**: .ui (Qt Designer format)
