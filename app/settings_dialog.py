#!/usr/bin/env python3
"""
Erika Settings Dialog
=====================

Settings dialog for configuring Erika's server connection and other options.

Author: EGO Revolution Team
Version: 1.0.0
"""

import logging
from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QGroupBox, QTabWidget, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from .config_manager import ErikaConfigManager
from .installation_wizard import ErikaInstallationWizard

logger = logging.getLogger(__name__)


class ErikaSettingsDialog(QDialog):
    """Settings dialog for Erika configuration"""
    
    # Signal emitted when settings are saved
    settings_saved = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = ErikaConfigManager()
        self.setWindowTitle("🌿 Erika - Settings")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self.setModal(True)
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Erika Settings")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Tabs for different settings sections
        self.tabs = QTabWidget()
        
        # Server Settings Tab
        server_tab = self.create_server_settings_tab()
        self.tabs.addTab(server_tab, "🔌 Server")
        
        # Security Settings Tab
        security_tab = self.create_security_settings_tab()
        self.tabs.addTab(security_tab, "🛡️ Security")
        
        # Database Settings Tab (optional)
        database_tab = self.create_database_settings_tab()
        self.tabs.addTab(database_tab, "💾 Database")
        
        layout.addWidget(self.tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.save_btn = QPushButton("💾 Save")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                padding: 10px 25px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #45a049;
            }
        """)
        self.save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
    
    def create_server_settings_tab(self) -> QWidget:
        """Create server settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Instructions
        instructions = QLabel(
            "Configure your connection to the EgoLlama Gateway server.\n"
            "This server provides AI-powered email analysis and chat features."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #555; padding: 10px;")
        layout.addWidget(instructions)
        
        # Server Address
        address_layout = QHBoxLayout()
        address_label = QLabel("Server Address:")
        address_label.setMinimumWidth(120)
        address_layout.addWidget(address_label)
        self.server_address_input = QLineEdit()
        self.server_address_input.setPlaceholderText("http://localhost:8082")
        address_layout.addWidget(self.server_address_input, 1)
        layout.addLayout(address_layout)
        
        # Test Connection Button
        test_layout = QHBoxLayout()
        test_layout.addStretch()
        self.test_server_btn = QPushButton("🔍 Test Connection")
        self.test_server_btn.clicked.connect(self.test_server_connection)
        test_layout.addWidget(self.test_server_btn)
        layout.addLayout(test_layout)
        
        # Connection Status
        self.server_status_label = QLabel("Not tested")
        self.server_status_label.setStyleSheet("""
            padding: 10px;
            border-radius: 4px;
            background: #f5f5f5;
            color: #666;
        """)
        layout.addWidget(self.server_status_label)
        
        layout.addStretch()
        
        return widget
    
    def create_database_settings_tab(self) -> QWidget:
        """Create database settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Instructions
        instructions = QLabel(
            "Configure database connection (optional).\n"
            "If not set, Erika will use default PostgreSQL settings."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #555; padding: 10px;")
        layout.addWidget(instructions)
        
        # Database URL
        db_layout = QHBoxLayout()
        db_label = QLabel("Database URL:")
        db_label.setMinimumWidth(120)
        db_layout.addWidget(db_label)
        self.database_url_input = QLineEdit()
        self.database_url_input.setPlaceholderText("postgresql://user:password@localhost:5432/erika")
        db_layout.addWidget(self.database_url_input, 1)
        layout.addLayout(db_layout)
        
        layout.addStretch()
        
        return widget
    
    def create_security_settings_tab(self) -> QWidget:
        """Create security settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Instructions
        instructions = QLabel(
            "Configure security features including phishing detection.\n"
            "Reverse image search helps detect phishing emails by verifying profile photos."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #555; padding: 10px;")
        layout.addWidget(instructions)
        
        # Phishing Detection
        phishing_group = QGroupBox("Phishing Detection")
        phishing_layout = QVBoxLayout(phishing_group)
        
        self.phishing_enabled_cb = QCheckBox("Enable Phishing Detection")
        self.phishing_enabled_cb.setChecked(True)
        self.phishing_enabled_cb.setToolTip(
            "Automatically check emails for phishing using reverse image search"
        )
        phishing_layout.addWidget(self.phishing_enabled_cb)
        
        # Reverse Image Search
        self.reverse_search_enabled_cb = QCheckBox("Enable Reverse Image Search")
        self.reverse_search_enabled_cb.setChecked(True)
        self.reverse_search_enabled_cb.setToolTip(
            "Use Google reverse image search to verify profile photos\n"
            "Requires: selenium, webdriver-manager, Chrome browser"
        )
        phishing_layout.addWidget(self.reverse_search_enabled_cb)
        
        # Info about requirements
        info_label = QLabel(
            "Note: Reverse image search requires:\n"
            "• Selenium (pip install selenium)\n"
            "• Chrome browser installed\n"
            "• Internet connection"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-size: 9pt; padding: 10px;")
        phishing_layout.addWidget(info_label)
        
        layout.addWidget(phishing_group)
        
        # AresBridge Threat Detection Group
        ares_group = QGroupBox("AresBridge Threat Detection")
        ares_layout = QVBoxLayout(ares_group)
        ares_layout.setSpacing(15)
        
        # Enable AresBridge
        self.ares_enabled_cb = QCheckBox("Enable AresBridge Threat Detection")
        self.ares_enabled_cb.setChecked(False)
        self.ares_enabled_cb.setToolTip(
            "Multi-factor threat scoring:\n"
            "• Footprint analysis (domain age, source count)\n"
            "• Domain mismatch detection\n"
            "• Content risk analysis"
        )
        ares_layout.addWidget(self.ares_enabled_cb)
        
        # Auto-mitigation
        self.auto_mitigate_cb = QCheckBox("Auto-Mitigate High-Threat Emails")
        self.auto_mitigate_cb.setChecked(False)
        self.auto_mitigate_cb.setToolTip(
            "Automatically mark emails as SPAM/PHISHING when threat score >= 0.8\n"
            "⚠️  Use with caution - may mark legitimate emails"
        )
        ares_layout.addWidget(self.auto_mitigate_cb)
        
        # Info about AresBridge
        ares_info = QLabel(
            "AresBridge provides advanced threat detection:\n"
            "• Footprint Risk (40%): Domain age and online presence\n"
            "• Domain Mismatch (30%): Professional claims vs personal domains\n"
            "• Content Risk (30%): Email content analysis\n\n"
            "Threat Score >= 0.8: Mark as PHISHING\n"
            "Threat Score >= 0.5: Flag for review"
        )
        ares_info.setWordWrap(True)
        ares_info.setStyleSheet("color: #666; font-size: 9pt; padding: 10px;")
        ares_layout.addWidget(ares_info)
        
        layout.addWidget(ares_group)
        
        layout.addStretch()
        
        return widget
    
    def load_settings(self):
        """Load current settings"""
        # Load gateway URL
        gateway_url = self.config_manager.get_gateway_url()
        self.server_address_input.setText(gateway_url)
        
        # Load database URL
        database_url = self.config_manager.get_database_url()
        if database_url:
            self.database_url_input.setText(database_url)
        
        # Load security settings from database
        try:
            from app.database_service import ErikaDatabaseService
            db_service = ErikaDatabaseService()
            config = db_service.get_email_config(user_id="default")
            if config:
                self.phishing_enabled_cb.setChecked(
                    config.get('phishing_detection_enabled', True)
                )
                self.reverse_search_enabled_cb.setChecked(
                    config.get('reverse_image_search_enabled', True)
                )
                self.ares_enabled_cb.setChecked(
                    config.get('enable_ares_bridge', False)
                )
                self.auto_mitigate_cb.setChecked(
                    config.get('auto_mitigate_threats', False)
                )
        except Exception as e:
            logger.debug(f"Could not load security settings: {e}")
            # Use defaults
            self.phishing_enabled_cb.setChecked(True)
            self.reverse_search_enabled_cb.setChecked(True)
    
    def test_server_connection(self):
        """Test connection to server"""
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
        
        # Test connection (simple synchronous test)
        try:
            import requests
            response = requests.get(f"{address}/health", timeout=5)
            if response.status_code == 200:
                self.server_status_label.setText("✅ Connection successful!")
                self.server_status_label.setStyleSheet("""
                    padding: 10px;
                    border-radius: 4px;
                    background: #e8f5e9;
                    color: #2e7d32;
                """)
            else:
                self.server_status_label.setText(f"❌ Server returned status {response.status_code}")
                self.server_status_label.setStyleSheet("""
                    padding: 10px;
                    border-radius: 4px;
                    background: #ffebee;
                    color: #c62828;
                """)
        except requests.exceptions.ConnectionError:
            self.server_status_label.setText("❌ Could not connect to server")
            self.server_status_label.setStyleSheet("""
                padding: 10px;
                border-radius: 4px;
                background: #ffebee;
                color: #c62828;
            """)
        except Exception as e:
            self.server_status_label.setText(f"❌ Error: {str(e)}")
            self.server_status_label.setStyleSheet("""
                padding: 10px;
                border-radius: 4px;
                background: #ffebee;
                color: #c62828;
            """)
    
    def save_settings(self):
        """Save settings"""
        # Save gateway URL
        gateway_url = self.server_address_input.text().strip()
        if gateway_url:
            try:
                self.config_manager.set_gateway_url(gateway_url)
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to save server settings: {str(e)}"
                )
                return
        
        # Save database URL
        database_url = self.database_url_input.text().strip()
        if database_url:
            try:
                self.config_manager.set_database_url(database_url)
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to save database settings: {str(e)}"
                )
                return
        
        # Save security settings to database
        try:
            from app.database_service import ErikaDatabaseService
            db_service = ErikaDatabaseService()
            db_service.update_email_config(
                user_id="default",
                phishing_detection_enabled=self.phishing_enabled_cb.isChecked(),
                reverse_image_search_enabled=self.reverse_search_enabled_cb.isChecked(),
                enable_ares_bridge=self.ares_enabled_cb.isChecked(),
                auto_mitigate_threats=self.auto_mitigate_cb.isChecked()
            )
        except Exception as e:
            logger.warning(f"Could not save security settings: {e}")
            # Continue - not critical
        
        QMessageBox.information(
            self,
            "✅ Settings Saved",
            "Settings have been saved successfully!"
        )
        
        self.settings_saved.emit()
        self.accept()

