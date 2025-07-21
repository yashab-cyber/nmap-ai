"""
Main scanning widget for the NMAP-AI GUI application.
Provides the primary interface for configuring and running scans.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QComboBox,
    QCheckBox, QProgressBar, QGroupBox, QSpinBox,
    QTabWidget, QSplitter, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QPalette


class ScanWidget(QWidget):
    """Main scanning interface widget."""
    
    # Signals
    scan_started = pyqtSignal(dict)
    scan_completed = pyqtSignal(dict)
    scan_progress = pyqtSignal(int, str)
    scan_error = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.scan_thread = None
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Create tab widget for different scan options
        self.tab_widget = QTabWidget()
        
        # Basic scan tab
        basic_tab = self.create_basic_scan_tab()
        self.tab_widget.addTab(basic_tab, "Basic Scan")
        
        # Advanced scan tab
        advanced_tab = self.create_advanced_scan_tab()
        self.tab_widget.addTab(advanced_tab, "Advanced")
        
        # AI options tab
        ai_tab = self.create_ai_options_tab()
        self.tab_widget.addTab(ai_tab, "AI Options")
        
        layout.addWidget(self.tab_widget)
        
        # Progress section
        progress_frame = self.create_progress_section()
        layout.addWidget(progress_frame)
        
        # Control buttons
        button_layout = self.create_button_layout()
        layout.addLayout(button_layout)
        
    def create_basic_scan_tab(self):
        """Create the basic scan configuration tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Target configuration
        target_group = QGroupBox("Target Configuration")
        target_layout = QGridLayout(target_group)
        
        target_layout.addWidget(QLabel("Targets:"), 0, 0)
        self.target_input = QTextEdit()
        self.target_input.setMaximumHeight(100)
        self.target_input.setPlaceholderText("Enter IP addresses or hostnames, one per line\nExample:\n192.168.1.1\n192.168.1.0/24\ngoogle.com")
        target_layout.addWidget(self.target_input, 0, 1)
        
        target_layout.addWidget(QLabel("Scan Type:"), 1, 0)
        self.scan_type_combo = QComboBox()
        self.scan_type_combo.addItems([
            "TCP SYN Scan (-sS)",
            "TCP Connect Scan (-sT)",
            "UDP Scan (-sU)",
            "Comprehensive Scan (-sS -sV -O)",
            "Quick Scan (-T4 -F)",
            "Intense Scan (-T4 -A -v)"
        ])
        target_layout.addWidget(self.scan_type_combo, 1, 1)
        
        layout.addWidget(target_group)
        
        # Port configuration
        port_group = QGroupBox("Port Configuration")
        port_layout = QGridLayout(port_group)
        
        port_layout.addWidget(QLabel("Port Range:"), 0, 0)
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("e.g., 1-1000, 22,80,443, or leave empty for default")
        port_layout.addWidget(self.port_input, 0, 1)
        
        self.top_ports_check = QCheckBox("Scan top 1000 ports")
        port_layout.addWidget(self.top_ports_check, 1, 0, 1, 2)
        
        layout.addWidget(port_group)
        
        return widget
        
    def create_advanced_scan_tab(self):
        """Create the advanced scan options tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Timing and performance
        timing_group = QGroupBox("Timing & Performance")
        timing_layout = QGridLayout(timing_group)
        
        timing_layout.addWidget(QLabel("Timing Template:"), 0, 0)
        self.timing_combo = QComboBox()
        self.timing_combo.addItems([
            "T0 (Paranoid)", "T1 (Sneaky)", "T2 (Polite)",
            "T3 (Normal)", "T4 (Aggressive)", "T5 (Insane)"
        ])
        self.timing_combo.setCurrentIndex(3)  # T3 Normal
        timing_layout.addWidget(self.timing_combo, 0, 1)
        
        timing_layout.addWidget(QLabel("Max Parallel Hosts:"), 1, 0)
        self.max_hosts_spin = QSpinBox()
        self.max_hosts_spin.setRange(1, 100)
        self.max_hosts_spin.setValue(30)
        timing_layout.addWidget(self.max_hosts_spin, 1, 1)
        
        layout.addWidget(timing_group)
        
        # Detection options
        detection_group = QGroupBox("Detection Options")
        detection_layout = QVBoxLayout(detection_group)
        
        self.os_detection_check = QCheckBox("OS Detection (-O)")
        self.service_detection_check = QCheckBox("Service/Version Detection (-sV)")
        self.script_scan_check = QCheckBox("Script Scan (-sC)")
        self.aggressive_check = QCheckBox("Aggressive Scan (-A)")
        
        detection_layout.addWidget(self.os_detection_check)
        detection_layout.addWidget(self.service_detection_check)
        detection_layout.addWidget(self.script_scan_check)
        detection_layout.addWidget(self.aggressive_check)
        
        layout.addWidget(detection_group)
        
        return widget
        
    def create_ai_options_tab(self):
        """Create the AI-specific options tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # AI features
        ai_group = QGroupBox("AI-Powered Features")
        ai_layout = QVBoxLayout(ai_group)
        
        self.ai_enabled_check = QCheckBox("Enable AI Analysis")
        self.ai_enabled_check.setChecked(True)
        ai_layout.addWidget(self.ai_enabled_check)
        
        self.vulnerability_analysis_check = QCheckBox("AI Vulnerability Analysis")
        self.vulnerability_analysis_check.setChecked(True)
        ai_layout.addWidget(self.vulnerability_analysis_check)
        
        self.smart_script_selection_check = QCheckBox("Smart Script Selection")
        ai_layout.addWidget(self.smart_script_selection_check)
        
        self.anomaly_detection_check = QCheckBox("Anomaly Detection")
        ai_layout.addWidget(self.anomaly_detection_check)
        
        layout.addWidget(ai_group)
        
        # AI model selection
        model_group = QGroupBox("AI Model Configuration")
        model_layout = QGridLayout(model_group)
        
        model_layout.addWidget(QLabel("Vulnerability Model:"), 0, 0)
        self.vuln_model_combo = QComboBox()
        self.vuln_model_combo.addItems(["Default", "Enhanced", "Experimental"])
        model_layout.addWidget(self.vuln_model_combo, 0, 1)
        
        model_layout.addWidget(QLabel("Classification Model:"), 1, 0)
        self.classification_model_combo = QComboBox()
        self.classification_model_combo.addItems(["Standard", "Deep Learning", "Ensemble"])
        model_layout.addWidget(self.classification_model_combo, 1, 1)
        
        layout.addWidget(model_group)
        
        return widget
        
    def create_progress_section(self):
        """Create the progress tracking section."""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(frame)
        
        self.progress_label = QLabel("Ready to scan")
        self.progress_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        return frame
        
    def create_button_layout(self):
        """Create the control button layout."""
        layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Scan")
        self.start_button.clicked.connect(self.start_scan)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
            }
        """)
        
        self.stop_button = QPushButton("Stop Scan")
        self.stop_button.clicked.connect(self.stop_scan)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #dc2626;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #b91c1c;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
            }
        """)
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_form)
        
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.clear_button)
        layout.addStretch()
        
        return layout
        
    def start_scan(self):
        """Start the scanning process."""
        scan_config = self.get_scan_configuration()
        
        if not scan_config['targets']:
            self.status_label.setText("Error: No targets specified")
            self.status_label.setStyleSheet("color: red;")
            return
            
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Initializing scan...")
        
        # Emit scan started signal
        self.scan_started.emit(scan_config)
        
    def stop_scan(self):
        """Stop the current scan."""
        if self.scan_thread and self.scan_thread.isRunning():
            self.scan_thread.terminate()
            
        self.reset_ui_state()
        self.status_label.setText("Scan stopped by user")
        self.status_label.setStyleSheet("color: orange;")
        
    def clear_form(self):
        """Clear all form inputs."""
        self.target_input.clear()
        self.port_input.clear()
        self.scan_type_combo.setCurrentIndex(0)
        self.timing_combo.setCurrentIndex(3)
        
        # Reset checkboxes
        for checkbox in self.findChildren(QCheckBox):
            checkbox.setChecked(False)
            
        self.ai_enabled_check.setChecked(True)
        self.vulnerability_analysis_check.setChecked(True)
        
        self.reset_ui_state()
        
    def get_scan_configuration(self):
        """Get the current scan configuration."""
        targets = [line.strip() for line in self.target_input.toPlainText().split('\n') 
                  if line.strip()]
                  
        config = {
            'targets': targets,
            'scan_type': self.scan_type_combo.currentText(),
            'ports': self.port_input.text().strip(),
            'timing': self.timing_combo.currentText(),
            'os_detection': self.os_detection_check.isChecked(),
            'service_detection': self.service_detection_check.isChecked(),
            'script_scan': self.script_scan_check.isChecked(),
            'aggressive': self.aggressive_check.isChecked(),
            'ai_enabled': self.ai_enabled_check.isChecked(),
            'vulnerability_analysis': self.vulnerability_analysis_check.isChecked(),
            'smart_scripts': self.smart_script_selection_check.isChecked(),
            'anomaly_detection': self.anomaly_detection_check.isChecked(),
            'max_hosts': self.max_hosts_spin.value(),
            'top_ports': self.top_ports_check.isChecked()
        }
        
        return config
        
    def update_progress(self, value, message):
        """Update the progress display."""
        self.progress_bar.setValue(value)
        self.progress_label.setText(f"Progress: {value}%")
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: blue;")
        
    def scan_completed_handler(self, results):
        """Handle scan completion."""
        self.reset_ui_state()
        self.progress_bar.setValue(100)
        self.progress_label.setText("Scan completed successfully")
        self.status_label.setText(f"Found {len(results.get('hosts', []))} hosts")
        self.status_label.setStyleSheet("color: green;")
        
    def scan_error_handler(self, error_message):
        """Handle scan errors."""
        self.reset_ui_state()
        self.progress_label.setText("Scan failed")
        self.status_label.setText(f"Error: {error_message}")
        self.status_label.setStyleSheet("color: red;")
        
    def reset_ui_state(self):
        """Reset UI to initial state."""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
