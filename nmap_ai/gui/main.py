"""
GUI main module for NMAP-AI
"""

import sys
import os
from typing import Optional

def gui_main(args: Optional[list] = None) -> None:
    """
    Main entry point for GUI application.
    
    Args:
        args: Command line arguments (optional)
    """
    try:
        # Try to import GUI dependencies
        try:
            from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
            from PyQt6.QtCore import Qt
            from PyQt6.QtGui import QPixmap, QIcon
        except ImportError:
            print("GUI dependencies not installed. Please install with: pip install nmap-ai[gui]")
            sys.exit(1)
        
        # Create application
        app = QApplication(args or sys.argv)
        
        # Create main window
        window = QMainWindow()
        window.setWindowTitle("NMAP-AI - AI-Powered Network Scanner")
        window.setGeometry(100, 100, 1200, 800)
        
        # Set window icon if logo exists
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "nmap-ai.png")
        if os.path.exists(logo_path):
            window.setWindowIcon(QIcon(logo_path))
        
        # Create central widget
        central_widget = QWidget()
        window.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Add logo if it exists
        if os.path.exists(logo_path):
            logo_label = QLabel()
            pixmap = QPixmap(logo_path)
            # Scale the logo to a reasonable size
            scaled_pixmap = pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            logo_label.setStyleSheet("padding: 10px;")
            layout.addWidget(logo_label)
        
        # Add welcome message
        welcome_label = QLabel("🚀 NMAP-AI GUI")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px;
            }
        """)
        layout.addWidget(welcome_label)
        
        # Add status message
        status_label = QLabel("GUI interface is under development.\nPlease use the CLI interface for now.")
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #7f8c8d;
                padding: 10px;
            }
        """)
        layout.addWidget(status_label)
        
        # Add CLI instructions
        cli_label = QLabel("To use NMAP-AI from command line:\nnmap-ai --help")
        cli_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cli_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #34495e;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 5px;
                font-family: monospace;
            }
        """)
        layout.addWidget(cli_label)
        
        # Show window
        window.show()
        
        # Run application
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Error launching GUI: {e}")
        print("Please ensure GUI dependencies are installed: pip install nmap-ai[gui]")
        sys.exit(1)


if __name__ == "__main__":
    gui_main()
