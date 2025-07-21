# GUI Widgets Directory

This directory contains custom GUI widgets and components for the NMAP-AI graphical interface.

## Widget Categories

### Core Widgets
- **ScanWidget**: Main scanning interface components
- **ResultWidget**: Scan result display widgets
- **ConfigWidget**: Configuration management widgets
- **LogWidget**: Logging and status display widgets

### Advanced Widgets
- **NetworkMapWidget**: Visual network topology display
- **VulnerabilityWidget**: Vulnerability analysis display
- **ChartWidget**: Data visualization components
- **ProgressWidget**: Scanning progress indicators

### Utility Widgets
- **FileDialogWidget**: File selection dialogs
- **FilterWidget**: Result filtering components
- **ExportWidget**: Data export interfaces
- **SettingsWidget**: Application settings panels

## Technology Stack

- **PyQt6**: Primary GUI framework
- **Custom Styles**: Application-specific styling
- **Signal/Slot System**: Event handling architecture
- **Thread Safety**: Widgets designed for multi-threaded operation

## Widget Structure

Each widget follows the standard PyQt6 pattern:
- Initialization and setup
- Signal/slot connections
- Event handlers
- Data binding methods
- Cleanup and resource management

## Usage

Widgets are imported and used by the main GUI application. They provide reusable components for building the user interface.
