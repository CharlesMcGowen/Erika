#!/usr/bin/env python3
"""
Run Erika Standalone Application
=================================

Entry point for running the Erika standalone Qt application.

Usage:
    python scripts/run_erika.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set environment variables if needed
if not os.getenv('DATABASE_URL'):
    # Default to local PostgreSQL
    os.environ.setdefault('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/ego')

if __name__ == "__main__":
    try:
        from PyQt6.QtWidgets import QApplication
        from app.config_manager import ErikaConfigManager
        from app.installation_wizard import ErikaInstallationWizard
        
        app = QApplication(sys.argv)
        
        # Check if first run and show installation wizard
        config_manager = ErikaConfigManager()
        gateway_url = None
        is_first_run = not config_manager.is_configured()
        
        if is_first_run:
            # Show installation wizard
            wizard = ErikaInstallationWizard(allow_skip=True)
            if wizard.exec() == wizard.DialogCode.Accepted:
                # Wizard was accepted (config saved)
                gateway_url = config_manager.get_gateway_url()
            else:
                # Wizard was skipped or cancelled
                gateway_url = config_manager.get_gateway_url()
        else:
            # Already configured, use saved URL
            gateway_url = config_manager.get_gateway_url()
        
        # Create desktop icon if it doesn't exist (even if already configured)
        # This ensures the icon is created even if user skipped wizard
        try:
            from app.desktop_icon import DesktopIconCreator
            icon_path = project_root / "Images" / "icon.png"
            script_path = project_root / "scripts" / "run_erika.py"
            
            if icon_path.exists() and script_path.exists():
                creator = DesktopIconCreator(
                    project_root=project_root,
                    icon_path=icon_path,
                    script_path=script_path
                )
                # Check if icon already exists, if not create it
                success, message = creator.create_desktop_icon()
                if success:
                    print(f"✅ Desktop icon: {message}")
        except Exception as e:
            # Don't fail app startup if icon creation fails
            print(f"⚠️  Could not create desktop icon: {e}")
        
        # Set environment variable for gateway URL (so it's available to the app)
        if gateway_url:
            os.environ['EGOLLAMA_GATEWAY_URL'] = gateway_url
        
        # Now import and start the main app
        from app.main import ErikaStandaloneApp
        
        window = ErikaStandaloneApp(embedded_mode=False)
        window.show()
        sys.exit(app.exec())
    except ImportError as e:
        print(f"Error: Missing dependencies. Please install: pip install -r requirements.txt")
        print(f"Details: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting Erika: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

