#!/usr/bin/env python3
"""
Erika Gmail Credentials Configuration Dialog
============================================

Qt dialog for configuring Erika's Gmail OAuth2 credentials.

Author: EGO Revolution Team
Version: 1.0.0
"""

import logging
from typing import Optional
from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QMessageBox, QGroupBox, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from .database_service import ErikaDatabaseService

logger = logging.getLogger(__name__)


class ErikaCredentialsDialog(QDialog):
    """Dialog for configuring Erika's Gmail OAuth2 credentials"""
    
    # Signal emitted when credentials are saved
    credentials_saved = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_service = ErikaDatabaseService()
        self.setWindowTitle("🌿 Erika - Gmail API Configuration")
        self.setMinimumWidth(650)
        self.setModal(True)
        self.setup_ui()
        self.load_config()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Gmail OAuth2 Configuration")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Instructions
        instructions_text = QTextEdit()
        instructions_text.setReadOnly(True)
        instructions_text.setMaximumHeight(100)
        instructions_text.setPlainText(
            "Enter your Google Cloud OAuth2 credentials to enable Gmail integration.\n\n"
            "To get these credentials:\n"
            "1. Go to https://console.cloud.google.com\n"
            "2. Create a project or select existing one\n"
            "3. Enable Gmail API in APIs & Services > Library\n"
            "4. Create OAuth2 credentials in APIs & Services > Credentials\n"
            "5. Application type: Desktop app\n"
            "6. Copy the Client ID and Client Secret below"
        )
        instructions_text.setStyleSheet("""
            QTextEdit {
                background: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        layout.addWidget(instructions_text)
        
        # Credentials Group
        credentials_group = QGroupBox("OAuth2 Credentials")
        credentials_layout = QVBoxLayout(credentials_group)
        credentials_layout.setSpacing(15)
        
        # Client ID
        client_id_layout = QHBoxLayout()
        client_id_label = QLabel("Client ID:")
        client_id_label.setMinimumWidth(100)
        client_id_layout.addWidget(client_id_label)
        self.client_id_input = QLineEdit()
        self.client_id_input.setPlaceholderText("xxxxx.apps.googleusercontent.com")
        self.client_id_input.setEchoMode(QLineEdit.EchoMode.Normal)
        client_id_layout.addWidget(self.client_id_input, 1)
        credentials_layout.addLayout(client_id_layout)
        
        # Client Secret
        client_secret_layout = QHBoxLayout()
        client_secret_label = QLabel("Client Secret:")
        client_secret_label.setMinimumWidth(100)
        client_secret_layout.addWidget(client_secret_label)
        self.client_secret_input = QLineEdit()
        self.client_secret_input.setPlaceholderText("Your client secret")
        self.client_secret_input.setEchoMode(QLineEdit.EchoMode.Password)
        client_secret_layout.addWidget(self.client_secret_input, 1)
        credentials_layout.addLayout(client_secret_layout)
        
        # Show/Hide password toggle
        toggle_layout = QHBoxLayout()
        toggle_layout.addStretch()
        self.show_password_cb = QCheckBox("Show Password")
        self.show_password_cb.stateChanged.connect(self.toggle_password_visibility)
        toggle_layout.addWidget(self.show_password_cb)
        credentials_layout.addLayout(toggle_layout)
        
        layout.addWidget(credentials_group)
        
        # Settings Group
        settings_group = QGroupBox("Gmail Settings")
        settings_layout = QVBoxLayout(settings_group)
        
        self.enable_checkbox = QCheckBox("Enable Gmail Integration")
        self.enable_checkbox.setChecked(False)
        self.enable_checkbox.setToolTip("Enable Erika to fetch and process emails from Gmail")
        settings_layout.addWidget(self.enable_checkbox)
        
        layout.addWidget(settings_group)
        
        # Status display
        self.status_label = QLabel()
        self.status_label.setStyleSheet("""
            padding: 10px;
            border-radius: 4px;
            background: #e3f2fd;
            color: #1976d2;
        """)
        self.update_status_text()
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.test_btn = QPushButton("🧪 Test Connection")
        self.test_btn.setToolTip("Validate credentials and test OAuth2 configuration")
        self.test_btn.clicked.connect(self.test_credentials)
        self.test_btn.setEnabled(False)
        button_layout.addWidget(self.test_btn)
        
        self.refresh_token_btn = QPushButton("🔄 Refresh Token")
        self.refresh_token_btn.setToolTip("Generate new Gmail OAuth2 token (opens browser)")
        self.refresh_token_btn.clicked.connect(self.refresh_gmail_token)
        button_layout.addWidget(self.refresh_token_btn)
        
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
            QPushButton:pressed {
                background: #3d8b40;
            }
        """)
        self.save_btn.setToolTip("Save credentials to database")
        self.save_btn.clicked.connect(self.save_credentials)
        button_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background: #f44336;
                color: white;
                padding: 10px 25px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background: #da190b;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Enable test button when both fields filled
        self.client_id_input.textChanged.connect(self.check_inputs)
        self.client_secret_input.textChanged.connect(self.check_inputs)
    
    def check_inputs(self):
        """Enable/disable test button based on input"""
        has_client_id = bool(self.client_id_input.text().strip())
        has_secret = bool(self.client_secret_input.text().strip())
        self.test_btn.setEnabled(has_client_id and has_secret)
    
    def toggle_password_visibility(self, state):
        """Toggle password visibility"""
        if state == Qt.CheckState.Checked:
            self.client_secret_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.client_secret_input.setEchoMode(QLineEdit.EchoMode.Password)
    
    def update_status_text(self):
        """Update status display"""
        config = self.db_service.get_email_config(user_id="default")
        if config and config.get('gmail_client_id'):
            self.status_label.setText("✅ Credentials are configured")
            self.status_label.setStyleSheet("""
                padding: 10px;
                border-radius: 4px;
                background: #e8f5e9;
                color: #2e7d32;
            """)
        else:
            self.status_label.setText("⚠️ No credentials configured")
            self.status_label.setStyleSheet("""
                padding: 10px;
                border-radius: 4px;
                background: #fff3e0;
                color: #f57c00;
            """)
    
    def load_config(self):
        """Load existing configuration"""
        config = self.db_service.get_email_config(user_id="default")
        if config:
            self.client_id_input.setText(config.get('gmail_client_id', ''))
            self.client_secret_input.setText(config.get('gmail_client_secret', ''))
            self.enable_checkbox.setChecked(config.get('gmail_enabled', False))
        self.check_inputs()
        self.update_status_text()
    
    def test_credentials(self):
        """Test the OAuth2 credentials"""
        client_id = self.client_id_input.text().strip()
        client_secret = self.client_secret_input.text().strip()
        
        if not client_id or not client_secret:
            QMessageBox.warning(self, "Missing Credentials", 
                              "Please enter both Client ID and Client Secret")
            return
        
        # Validate format
        if not client_id.endswith('.apps.googleusercontent.com'):
            QMessageBox.warning(self, "Invalid Format",
                              "Client ID should end with '.apps.googleusercontent.com'")
            return
        
        # Try to authenticate
        try:
            from google_auth_oauthlib.flow import InstalledAppFlow
            
            client_config = {
                "installed": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost"]
                }
            }
            
            # Request both readonly (for scanning) and modify (for mitigation)
            SCOPES = [
                'https://www.googleapis.com/auth/gmail.readonly',
                'https://www.googleapis.com/auth/gmail.modify'
            ]
            
            # This will validate the config structure
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            
            QMessageBox.information(
                self, 
                "✅ Test Success",
                "Credentials are valid!\n\n"
                "The configuration is correct. When you enable Gmail integration, "
                "you'll be asked to authenticate with Google in your browser."
            )
            
        except ImportError:
            QMessageBox.warning(
                self,
                "Missing Dependencies",
                "Google OAuth2 libraries not installed.\n\n"
                "Please install: google-auth-oauthlib\n"
                "Command: pip install google-auth-oauthlib"
            )
        except Exception as e:
            logger.error(f"Test credentials error: {e}")
            QMessageBox.critical(
                self, 
                "❌ Test Failed", 
                f"Invalid credentials or configuration:\n\n{str(e)}\n\n"
                "Please verify your Client ID and Client Secret from Google Cloud Console."
            )
    
    def refresh_gmail_token(self):
        """Refresh or generate new Gmail OAuth2 token"""
        client_id = self.client_id_input.text().strip()
        client_secret = self.client_secret_input.text().strip()
        
        if not client_id or not client_secret:
            QMessageBox.warning(
                self, 
                "Missing Credentials",
                "Please enter both Client ID and Client Secret first,\n"
                "then save them before refreshing the token."
            )
            return
        
        try:
            from erika.plugins.email import ErikaGmailService
            
            # Use the library's Gmail service for token generation
            gmail_service = ErikaGmailService(
                user_id="default",
                config={
                    'gmail_client_id': client_id,
                    'gmail_client_secret': client_secret
                }
            )
            
            QMessageBox.information(
                self,
                "🌐 Browser Authentication",
                "Your browser will open for Google authentication.\n\n"
                "Please sign in and authorize Erika to access Gmail."
            )
            
            # Authenticate (this will open browser)
            success = gmail_service.authenticate(
                client_id=client_id,
                client_secret=client_secret
            )
            
            if success:
                QMessageBox.information(
                    self,
                    "✅ Token Generated",
                    "Gmail token saved successfully!\n\n"
                    "Erika will now use this token for Gmail access.\n"
                    "Email processing will start automatically."
                )
            else:
                QMessageBox.critical(
                    self,
                    "❌ Token Generation Failed",
                    "Failed to generate token.\n\n"
                    "Please check your credentials and try again."
                )
            
        except ImportError:
            QMessageBox.warning(
                self,
                "Missing Dependencies",
                "Google OAuth2 libraries not installed.\n\n"
                "Please install: google-auth-oauthlib\n"
                "Command: pip install google-auth-oauthlib"
            )
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            QMessageBox.critical(
                self,
                "❌ Token Generation Failed",
                f"Failed to generate token:\n\n{str(e)}\n\n"
                "Please check your credentials and try again."
            )
    
    def save_credentials(self):
        """Save credentials to database"""
        client_id = self.client_id_input.text().strip()
        client_secret = self.client_secret_input.text().strip()
        
        if not client_id or not client_secret:
            QMessageBox.warning(self, "Missing Credentials",
                              "Please enter both Client ID and Client Secret")
            return
        
        # Validate format
        if not client_id.endswith('.apps.googleusercontent.com'):
            QMessageBox.warning(self, "Invalid Format",
                              "Client ID should end with '.apps.googleusercontent.com'")
            return
        
        # Save to database
        success = self.db_service.update_email_config(
            user_id="default",
            gmail_client_id=client_id,
            gmail_client_secret=client_secret,
            gmail_enabled=self.enable_checkbox.isChecked()
        )
        
        if success:
            QMessageBox.information(
                self, 
                "✅ Success", 
                "Credentials saved successfully!\n\n"
                "Erika can now use Gmail integration when enabled.\n\n"
                "Click '🔄 Refresh Token' to generate authentication token."
            )
            self.credentials_saved.emit()
            self.accept()
        else:
            QMessageBox.critical(
                self, 
                "❌ Error", 
                "Failed to save credentials to database.\n\n"
                "Please check database connection and try again."
            )

