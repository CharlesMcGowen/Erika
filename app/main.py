#!/usr/bin/env python3
"""
Erika Standalone Application
============================

Main Qt application window for the standalone Erika email assistant.

Author: Living Archive team
Version: 1.0.0
"""

import sys
import logging
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QMenuBar, QMenu, QStatusBar, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QIcon, QAction

from .config_manager import ErikaConfigManager
from .settings_dialog import ErikaSettingsDialog
from .database_service import ErikaDatabaseService
from .credentials_dialog import ErikaCredentialsDialog

logger = logging.getLogger(__name__)


class ErikaStandaloneApp(QMainWindow):
    """Main application window for standalone Erika"""
    
    def __init__(self, embedded_mode: bool = False, parent=None):
        super().__init__(parent)
        self.embedded_mode = embedded_mode
        self.config_manager = ErikaConfigManager()
        self.database_service = None
        
        self.setWindowTitle("🌿 Erika - AI Email Assistant")
        self.setMinimumSize(1000, 700)
        
        # Setup UI
        self.setup_menu_bar()
        self.setup_ui()
        self.setup_status_bar()
        
        # Initialize database service
        try:
            self.database_service = ErikaDatabaseService()
        except Exception as e:
            logger.warning(f"Could not initialize database service: {e}")
            self.statusBar().showMessage("⚠️  Database not available", 5000)
    
    def setup_menu_bar(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        settings_action = QAction("&Settings...", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Gmail menu
        gmail_menu = menubar.addMenu("&Gmail")
        
        connect_action = QAction("&Connect Gmail...", self)
        connect_action.triggered.connect(self.connect_gmail)
        gmail_menu.addAction(connect_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About Erika", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_ui(self):
        """Setup main UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Welcome title
        title = QLabel("🌿 Welcome to Erika!")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Your AI-Powered Email Assistant")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #666; font-size: 14pt;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(30)
        
        # Status section
        status_group = QVBoxLayout()
        
        # Gmail connection status
        self.gmail_status_label = QLabel("Gmail: Not connected")
        self.gmail_status_label.setStyleSheet("""
            padding: 15px;
            border-radius: 5px;
            background: #f5f5f5;
            font-size: 12pt;
        """)
        status_group.addWidget(self.gmail_status_label)
        
        # Server connection status
        gateway_url = self.config_manager.get_gateway_url()
        if gateway_url:
            server_status = f"EgoLlama Server: {gateway_url}"
            status_color = "#e8f5e9"
        else:
            server_status = "EgoLlama Server: Not configured"
            status_color = "#fff3e0"
        
        self.server_status_label = QLabel(server_status)
        self.server_status_label.setStyleSheet(f"""
            padding: 15px;
            border-radius: 5px;
            background: {status_color};
            font-size: 12pt;
        """)
        status_group.addWidget(self.server_status_label)
        
        layout.addLayout(status_group)
        
        layout.addStretch()
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Connect Gmail button
        self.connect_btn = QPushButton("📧 Connect Gmail")
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background: #4285f4;
                color: white;
                padding: 15px 30px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12pt;
            }
            QPushButton:hover {
                background: #357ae8;
            }
        """)
        self.connect_btn.clicked.connect(self.connect_gmail)
        button_layout.addWidget(self.connect_btn)
        
        # Settings button
        settings_btn = QPushButton("⚙️ Settings")
        settings_btn.setStyleSheet("""
            QPushButton {
                background: #34a853;
                color: white;
                padding: 15px 30px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12pt;
            }
            QPushButton:hover {
                background: #2d8f47;
            }
        """)
        settings_btn.clicked.connect(self.show_settings)
        button_layout.addWidget(settings_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        layout.addStretch()
    
    def setup_status_bar(self):
        """Setup status bar"""
        self.statusBar().showMessage("Ready")
    
    def connect_gmail(self):
        """Open Gmail connection dialog"""
        try:
            dialog = ErikaCredentialsDialog(self)
            if dialog.exec() == dialog.DialogCode.Accepted:
                self.gmail_status_label.setText("Gmail: Connected ✅")
                self.gmail_status_label.setStyleSheet("""
                    padding: 15px;
                    border-radius: 5px;
                    background: #e8f5e9;
                    font-size: 12pt;
                """)
                self.statusBar().showMessage("Gmail connected successfully", 3000)
        except Exception as e:
            logger.error(f"Error connecting Gmail: {e}")
            QMessageBox.critical(
                self,
                "Connection Error",
                f"Failed to connect Gmail:\n\n{str(e)}"
            )
    
    def show_settings(self):
        """Show settings dialog"""
        try:
            dialog = ErikaSettingsDialog(self)
            if dialog.exec() == dialog.DialogCode.Accepted:
                # Update server status if changed
                gateway_url = self.config_manager.get_gateway_url()
                if gateway_url:
                    self.server_status_label.setText(f"EgoLlama Server: {gateway_url}")
                    self.server_status_label.setStyleSheet("""
                        padding: 15px;
                        border-radius: 5px;
                        background: #e8f5e9;
                        font-size: 12pt;
                    """)
                self.statusBar().showMessage("Settings saved", 3000)
        except Exception as e:
            logger.error(f"Error showing settings: {e}")
            QMessageBox.critical(
                self,
                "Settings Error",
                f"Failed to open settings:\n\n{str(e)}"
            )
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Erika",
            "<h2>🌿 Erika</h2>"
            "<p><b>AI-Powered Email Assistant</b></p>"
            "<p>Version 1.0.0</p>"
            "<p>Erika helps you manage your emails with AI-powered analysis, "
            "phishing detection, and intelligent insights.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Gmail OAuth integration</li>"
            "<li>AI-powered email analysis</li>"
            "<li>Phishing detection with reverse image search</li>"
            "<li>Seamless server configuration</li>"
            "</ul>"
            "<p>© 2024 Living Archive team</p>"
        )
    
    def closeEvent(self, event):
        """Handle window close event"""
        event.accept()

