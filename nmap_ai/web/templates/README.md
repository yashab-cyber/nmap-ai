# Web Templates Directory

This directory contains Jinja2 templates for the NMAP-AI web interface.

## Template Structure

### Base Templates
- **base.html**: Main layout template with navigation and common elements
- **layout.html**: Standard page layout with header, footer, and sidebar
- **error.html**: Error page templates for various HTTP errors

### Page Templates
- **index.html**: Dashboard/home page template
- **scan.html**: Scanning interface and configuration
- **results.html**: Scan results display and analysis
- **reports.html**: Report generation and viewing
- **settings.html**: Application configuration interface

### Component Templates
- **components/**: Reusable template components
  - **navbar.html**: Navigation bar component
  - **sidebar.html**: Sidebar navigation
  - **footer.html**: Page footer
  - **modals.html**: Modal dialog templates
  - **forms.html**: Common form templates

### API Documentation
- **docs/**: API documentation templates
  - **api_overview.html**: API overview page
  - **endpoints.html**: Endpoint documentation
  - **swagger.html**: Swagger UI integration

## Template Features

### Jinja2 Integration
- Template inheritance and blocks
- Macros for reusable components
- Filters for data formatting
- Context processors for global data

### Bootstrap Integration
- Responsive design components
- Mobile-first layout approach
- Modern UI components
- Cross-browser compatibility

### JavaScript Integration
- AJAX functionality for dynamic updates
- Real-time scan progress updates
- Interactive data visualization
- Form validation and submission

## Usage

Templates are rendered by FastAPI using Jinja2TemplateEngine. They receive context data from the web application routes and render dynamic HTML content for users.
