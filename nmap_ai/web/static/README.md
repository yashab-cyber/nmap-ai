# Web Static Files Directory

This directory contains static assets for the NMAP-AI web interface including CSS, JavaScript, images, and other client-side resources.

## Directory Structure

```
static/
├── css/              # Stylesheets
│   ├── main.css     # Main application styles
│   ├── bootstrap/   # Bootstrap framework
│   └── themes/      # Color themes
├── js/              # JavaScript files
│   ├── app.js       # Main application logic
│   ├── scan.js      # Scanning functionality
│   ├── charts.js    # Data visualization
│   └── utils.js     # Utility functions
├── img/             # Images and icons
│   ├── logo/        # Application logos
│   ├── icons/       # UI icons
│   └── backgrounds/ # Background images
├── fonts/           # Web fonts
├── vendor/          # Third-party libraries
│   ├── jquery/      # jQuery library
│   ├── bootstrap/   # Bootstrap components
│   ├── chartjs/     # Chart.js for visualization
│   └── fontawesome/ # Font Awesome icons
└── manifest.json    # Web app manifest
```

## Technologies Used

### CSS Framework
- **Bootstrap 5**: Responsive design framework
- **Custom CSS**: Application-specific styling
- **CSS Grid/Flexbox**: Modern layout techniques
- **CSS Variables**: Theme customization

### JavaScript Libraries
- **Vanilla JavaScript**: Core application logic
- **Chart.js**: Data visualization and charting
- **WebSocket API**: Real-time communication
- **Fetch API**: HTTP requests to backend

### Icons and Images
- **Font Awesome**: Icon library
- **Custom Icons**: Application-specific icons
- **SVG Graphics**: Scalable vector graphics
- **Optimized Images**: Compressed web-optimized images

## Features

### Real-time Updates
- Live scan progress tracking
- Dynamic result updates
- WebSocket integration
- Responsive UI updates

### Data Visualization
- Interactive charts and graphs
- Network topology visualization
- Vulnerability trend analysis
- Export capabilities

### Responsive Design
- Mobile-first approach
- Cross-device compatibility
- Adaptive layouts
- Touch-friendly interfaces

## Performance Optimization

- Minified CSS and JavaScript
- Image optimization
- Lazy loading implementation
- CDN-ready asset structure
