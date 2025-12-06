#!/usr/bin/env python3
"""
Erika Installation Wizard
=========================

First-run setup wizard for configuring EgoLlama Gateway connection.

Author: Living Archive team
Version: 1.0.0
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QGroupBox, QTextEdit, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont
import requests

logger = logging.getLogger(__name__)


class ConnectionTestWorker(QThread):
    """Background worker for testing gateway connection"""
    connection_result = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, gateway_url: str):
        super().__init__()
        self.gateway_url = gateway_url
    
    def run(self):
        """Test connection to gateway"""
        try:
            response = requests.get(
                f"{self.gateway_url}/health",
                timeout=5
            )
            if response.status_code == 200:
                self.connection_result.emit(True, "✅ Connection successful!")
            else:
                self.connection_result.emit(False, f"❌ Server returned status {response.status_code}")
        except requests.exceptions.ConnectionError:
            self.connection_result.emit(False, "❌ Could not connect to server. Check address and port.")
        except requests.exceptions.Timeout:
            self.connection_result.emit(False, "❌ Connection timeout. Server may be unreachable.")
        except Exception as e:
            self.connection_result.emit(False, f"❌ Error: {str(e)}")


class ErikaInstallationWizard(QDialog):
    """Installation wizard for first-time setup"""
    
    # Signal emitted when configuration is saved
    configuration_saved = pyqtSignal(str)  # gateway_url
    
    def __init__(self, parent=None, allow_skip: bool = True, config_path: Path = None):
        super().__init__(parent)
        if config_path is None:
            self.config_path = Path.home() / ".erika" / "config.json"
        else:
            self.config_path = config_path
        self.setWindowTitle("🌿 Erika - Installation Wizard")
        self.setMinimumWidth(700)
        self.setModal(True)
        self.connection_worker = None
        self.allow_skip = allow_skip
        self.setup_ui()
        self.load_existing_config()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Welcome title
        title = QLabel("Welcome to Erika! 🌿")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Let's set up your connection to the EgoLlama server")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #666; font-size: 12pt;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        # Server Configuration Group
        server_group = QGroupBox("EgoLlama Server Configuration")
        server_layout = QVBoxLayout(server_group)
        server_layout.setSpacing(15)
        
        # Instructions
        instructions = QLabel(
            "Enter your EgoLlama server address and port.\n"
            "If your company set up the server, ask them for the address.\n"
            "Example: http://egollama.company.com:8082 or http://192.168.1.100:8082"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #555; padding: 10px;")
        server_layout.addWidget(instructions)
        
        # Server Address
        address_layout = QHBoxLayout()
        address_label = QLabel("Server Address:")
        address_label.setMinimumWidth(120)
        address_layout.addWidget(address_label)
        self.server_address_input = QLineEdit()
        self.server_address_input.setPlaceholderText("http://localhost:8082")
        self.server_address_input.setText("http://localhost:8082")  # Default
        self.server_address_input.textChanged.connect(self.on_address_changed)
        address_layout.addWidget(self.server_address_input, 1)
        server_layout.addLayout(address_layout)
        
        # Connection Status
        self.connection_status = QLabel("Not tested")
        self.connection_status.setStyleSheet("""
            padding: 10px;
            border-radius: 4px;
            background: #f5f5f5;
            color: #666;
        """)
        server_layout.addWidget(self.connection_status)
        
        # Test Connection Button
        test_layout = QHBoxLayout()
        test_layout.addStretch()
        self.test_btn = QPushButton("🔍 Test Connection")
        self.test_btn.setToolTip("Test connection to the EgoLlama server")
        self.test_btn.clicked.connect(self.test_connection)
        test_layout.addWidget(self.test_btn)
        server_layout.addLayout(test_layout)
        
        layout.addWidget(server_group)
        
        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        layout.addWidget(self.progress_bar)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        if self.allow_skip:
            self.skip_btn = QPushButton("Skip for Now")
            self.skip_btn.setToolTip("Skip server setup (you can configure later)")
            self.skip_btn.clicked.connect(self.skip_setup)
            button_layout.addWidget(self.skip_btn)
        
        self.save_btn = QPushButton("✅ Save & Continue")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                padding: 12px 30px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background: #45a049;
            }
            QPushButton:disabled {
                background: #cccccc;
                color: #666666;
            }
        """)
        self.save_btn.setToolTip("Save configuration and continue")
        self.save_btn.clicked.connect(self.save_configuration)
        self.save_btn.setEnabled(False)  # Disabled until connection tested
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
    
    def on_address_changed(self):
        """Handle address input change"""
        self.save_btn.setEnabled(False)
        self.connection_status.setText("Not tested")
        self.connection_status.setStyleSheet("""
            padding: 10px;
            border-radius: 4px;
            background: #f5f5f5;
            color: #666;
        """)
    
    def test_connection(self):
        """Test connection to gateway"""
        address = self.server_address_input.text().strip()
        
        if not address:
            QMessageBox.warning(self, "Missing Address", "Please enter a server address")
            return
        
        # Validate URL format
        if not (address.startswith("http://") or address.startswith("https://")):
            QMessageBox.warning(
                self, 
                "Invalid Address",
                "Server address must start with http:// or https://\n\n"
                "Example: http://localhost:8082"
            )
            return
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.test_btn.setEnabled(False)
        self.connection_status.setText("Testing connection...")
        self.connection_status.setStyleSheet("""
            padding: 10px;
            border-radius: 4px;
            background: #fff3e0;
            color: #f57c00;
        """)
        
        # Test in background thread
        if self.connection_worker and self.connection_worker.isRunning():
            self.connection_worker.terminate()
        
        self.connection_worker = ConnectionTestWorker(address)
        self.connection_worker.connection_result.connect(self.on_connection_test_result)
        self.connection_worker.start()
    
    def on_connection_test_result(self, success: bool, message: str):
        """Handle connection test result"""
        self.progress_bar.setVisible(False)
        self.test_btn.setEnabled(True)
        
        if success:
            self.connection_status.setText(message)
            self.connection_status.setStyleSheet("""
                padding: 10px;
                border-radius: 4px;
                background: #e8f5e9;
                color: #2e7d32;
            """)
            self.save_btn.setEnabled(True)
        else:
            self.connection_status.setText(message)
            self.connection_status.setStyleSheet("""
                padding: 10px;
                border-radius: 4px;
                background: #ffebee;
                color: #c62828;
            """)
            # Allow saving even if test fails (user might want to configure later)
            # But show a warning
            self.save_btn.setEnabled(True)
            QMessageBox.warning(
                self,
                "Connection Test Failed",
                f"{message}\n\n"
                "You can still save the configuration and try connecting later.\n"
                "Make sure the server is running and the address is correct."
            )
    
    def load_existing_config(self):
        """Load existing configuration if available"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    gateway_url = config.get('egollama_gateway_url', '')
                    if gateway_url:
                        self.server_address_input.setText(gateway_url)
            except Exception as e:
                logger.warning(f"Could not load existing config: {e}")
    
    def save_configuration(self):
        """Save configuration to file"""
        address = self.server_address_input.text().strip()
        
        if not address:
            QMessageBox.warning(self, "Missing Address", "Please enter a server address")
            return
        
        # Validate URL format
        if not (address.startswith("http://") or address.startswith("https://")):
            QMessageBox.warning(
                self,
                "Invalid Address",
                "Server address must start with http:// or https://"
            )
            return
        
        # Ensure config directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing config or create new
        config = {}
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
            except Exception:
                pass
        
        # Update gateway URL
        config['egollama_gateway_url'] = address
        config['configured'] = True
        
        # Save config
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Create desktop icon
            self.create_desktop_icon()
            
            QMessageBox.information(
                self,
                "✅ Configuration Saved",
                f"EgoLlama server configured successfully!\n\n"
                f"Server: {address}\n\n"
                f"Desktop icon created!\n\n"
                f"You can change settings later in Settings."
            )
            
            self.configuration_saved.emit(address)
            self.accept()
        except Exception as e:
            QMessageBox.critical(
                self,
                "❌ Error",
                f"Failed to save configuration:\n\n{str(e)}"
            )
    
    def create_desktop_icon(self):
        """Create desktop icon for Erika"""
        try:
            from app.desktop_icon import DesktopIconCreator
            
            # Get project root (parent of app directory)
            project_root = Path(__file__).parent.parent
            icon_path = project_root / "Images" / "icon.png"
            script_path = project_root / "scripts" / "run_erika.py"
            
            if icon_path.exists() and script_path.exists():
                creator = DesktopIconCreator(
                    project_root=project_root,
                    icon_path=icon_path,
                    script_path=script_path
                )
                success, message = creator.create_desktop_icon()
                if success:
                    logger.info(f"Desktop icon created: {message}")
                else:
                    logger.warning(f"Could not create desktop icon: {message}")
            else:
                logger.warning(f"Missing files for desktop icon: icon={icon_path.exists()}, script={script_path.exists()}")
        except Exception as e:
            logger.warning(f"Error creating desktop icon: {e}")
            # Don't fail installation if icon creation fails
    
    def skip_setup(self):
        """Skip setup and use defaults"""
        reply = QMessageBox.question(
            self,
            "Skip Setup?",
            "You can configure the server later in Settings.\n\n"
            "Continue without server connection?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Still create desktop icon even if skipping setup
            self.create_desktop_icon()
            self.configuration_saved.emit("")  # Empty = use defaults
            self.reject()

