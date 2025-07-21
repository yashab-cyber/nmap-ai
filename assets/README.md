# Assets Directory

This directory contains static assets used by NMAP-AI including images, icons, themes, and other resources.

## Structure

- `images/` - Screenshots, diagrams, and documentation images
- `icons/` - Application icons and UI elements  
- `themes/` - GUI themes and styling resources
- `fonts/` - Custom fonts for GUI applications
- `templates/` - Report templates and layouts
- `logos/` - Project logos and branding materials

## Contents

### Images
- Application screenshots for documentation
- Architecture diagrams and flowcharts
- Network topology visualizations
- Tutorial step-by-step images

### Icons
- Application icon files (.ico, .png, .svg)
- Menu and toolbar icons
- Status indicator icons
- File type association icons

### Themes
- Dark and light theme resources
- Custom color schemes
- GUI styling templates
- CSS files for web interface

### Templates
- HTML report templates
- PDF report layouts
- Email notification templates
- Configuration file templates

## Usage in Application

### GUI Themes
The GUI application can use custom themes by placing theme files in `themes/`:

```python
# Load custom theme
from nmap_ai.gui.theme import ThemeManager

theme_manager = ThemeManager()
theme_manager.load_theme('themes/dark_theme.json')
```

### Report Templates
Custom report templates can be used for generating professional reports:

```python
from nmap_ai.core.reports import ReportGenerator

generator = ReportGenerator()
generator.load_template('templates/professional_report.html')
report = generator.generate(scan_results)
```

### Icons in GUI
Application icons are automatically loaded from the icons directory:

```python
# Icons are referenced by name
icon_path = 'assets/icons/scan_icon.png'
```

## File Formats

### Supported Image Formats
- PNG (preferred for icons and screenshots)
- SVG (preferred for scalable graphics)
- JPG (for photographs and complex images)
- ICO (for Windows application icons)

### Theme Files
- JSON for theme configuration
- CSS for web interface styling
- QSS for Qt application styling

### Template Files
- HTML for web-based reports
- Jinja2 templates for dynamic content
- CSS for styling templates

## Adding New Assets

### Guidelines
1. Use descriptive filenames
2. Optimize file sizes for distribution
3. Include multiple resolutions for icons
4. Use consistent naming conventions
5. Document any licensing requirements

### Icon Guidelines
- Provide multiple sizes: 16x16, 32x32, 64x64, 128x128
- Use PNG format with transparency
- Keep designs simple and recognizable
- Follow platform-specific design guidelines

### Image Guidelines  
- Use PNG for screenshots and diagrams
- Optimize file sizes without quality loss
- Include alt text descriptions in documentation
- Use consistent styling and colors

## Licensing

All assets should be:
- Original creations
- Licensed under compatible terms
- Properly attributed if using third-party content
- Documented in ATTRIBUTION.md if required

## Attribution

Some assets may be derived from or inspired by:
- Nmap project icons and imagery
- Open source security tool interfaces
- Community contributions

See ATTRIBUTION.md for detailed licensing information.

## Building Assets

### Icon Generation
```bash
# Generate icon set from SVG
python scripts/generate_icons.py assets/logos/logo.svg

# Optimize PNG files
python scripts/optimize_images.py assets/images/
```

### Theme Development
```bash
# Validate theme files
python scripts/validate_themes.py assets/themes/

# Preview themes
python scripts/theme_preview.py assets/themes/custom_theme.json
```

## Distribution

Assets are automatically included in distribution packages:
- Essential icons and themes in all packages
- Full asset library in source distributions
- Compressed assets in binary distributions

## Platform Considerations

### Windows
- ICO files for application icons
- High DPI awareness for images
- Windows-specific themes

### macOS  
- ICNS files for application bundles
- Retina display optimizations
- macOS-specific styling

### Linux
- SVG icons for scalability
- Theme integration with desktop environments
- Standard icon naming conventions
