#!/usr/bin/env python3
"""
Test Installation Wizard
========================

Simple script to test the installation wizard in a clean test environment.

Usage:
    python scripts/test_wizard.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set test directory for clean testing
TEST_DIR = project_root / "test_run"
TEST_CONFIG_DIR = TEST_DIR / ".erika"
TEST_CONFIG_FILE = TEST_CONFIG_DIR / "config.json"

def setup_test_environment():
    """Setup test environment with isolated config directory"""
    # Create test directory structure
    TEST_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Backup original config path if it exists
    original_config = Path.home() / ".erika" / "config.json"
    backup_config = TEST_DIR / "original_config_backup.json"
    
    if original_config.exists() and not backup_config.exists():
        import shutil
        shutil.copy(original_config, backup_config)
        print(f"  ℹ️  Backed up original config to: {backup_config}")
    
    # Patch config_manager to use test directory
    import app.config_manager
    original_init = app.config_manager.ErikaConfigManager.__init__
    
    def test_init(self):
        """Modified __init__ to use test directory"""
        self.config_path = TEST_CONFIG_FILE
        self._config = None
        self._load_config()
    
    app.config_manager.ErikaConfigManager.__init__ = test_init
    
    print(f"✅ Test environment setup:")
    print(f"   Test directory: {TEST_DIR}")
    print(f"   Config will be saved to: {TEST_CONFIG_FILE}")
    print()
    
    # Setup desktop icon
    setup_desktop_icon()

def setup_desktop_icon():
    """Setup desktop icon for the application"""
    try:
        from app.desktop_icon import DesktopIconCreator
        
        icon_path = project_root / "Images" / "icon.png"
        script_path = project_root / "scripts" / "run_erika.py"
        
        if not icon_path.exists():
            print(f"  ⚠️  Icon not found: {icon_path}")
            print("     Skipping desktop icon creation")
            return
        
        if not script_path.exists():
            print(f"  ⚠️  Script not found: {script_path}")
            print("     Skipping desktop icon creation")
            return
        
        creator = DesktopIconCreator(
            project_root=project_root,
            icon_path=icon_path,
            script_path=script_path
        )
        
        success, message = creator.create_desktop_icon()
        if success:
            print(f"  {message}")
        else:
            print(f"  {message}")
            print("     (This is optional - you can still run Erika from command line)")
        print()
        
    except ImportError as e:
        print(f"  ⚠️  Could not import desktop icon creator: {e}")
        print("     Skipping desktop icon creation")
        print()
    except Exception as e:
        print(f"  ⚠️  Error setting up desktop icon: {e}")
        print("     Skipping desktop icon creation")
        print()

def cleanup_test_environment():
    """Cleanup test environment"""
    print()
    print("="*60)
    print("🧹 CLEANUP")
    print("="*60)
    print()
    
    if TEST_CONFIG_FILE.exists():
        print(f"Test config file exists: {TEST_CONFIG_FILE}")
        response = input("Delete test config? (y/N): ").strip().lower()
        if response == 'y':
            TEST_CONFIG_FILE.unlink()
            print("  ✅ Test config deleted")
        else:
            print("  ℹ️  Test config kept")
            print(f"     Location: {TEST_CONFIG_FILE}")
    
    # Restore original config if backed up
    backup_config = TEST_DIR / "original_config_backup.json"
    if backup_config.exists():
        print(f"\nOriginal config backup exists: {backup_config}")
        print("  ℹ️  Backup kept for safety")
    
    # Ask about desktop icon
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
            print(f"\nDesktop icon was created during setup")
            response = input("Remove desktop icon? (y/N): ").strip().lower()
            if response == 'y':
                success, message = creator.remove_desktop_icon()
                print(f"  {message}")
    except Exception:
        pass  # Ignore errors during cleanup
    
    print()
    print("Test directory contents:")
    if TEST_DIR.exists():
        for item in TEST_DIR.iterdir():
            print(f"  - {item.name}")

def main():
    """Test the installation wizard"""
    print("="*60)
    print("🌿 ERIKA INSTALLATION WIZARD TEST")
    print("="*60)
    print()
    
    # Setup test environment
    print("Setting up test environment...")
    setup_test_environment()
    
    # Check display
    display = os.getenv('DISPLAY')
    if not display:
        print("⚠️  No DISPLAY environment variable detected")
        print("   The wizard requires a GUI environment to display")
        print("   If you're using SSH, enable X11 forwarding:")
        print("     ssh -X user@host")
        print()
        print("   The wizard code is ready and will work when run")
        print("   on a system with a display.")
        print()
        cleanup_test_environment()
        return 1
    
    print(f"✅ DISPLAY={display}")
    print()
    
    # Test imports
    print("Testing imports...")
    try:
        from PyQt6.QtWidgets import QApplication
        print("  ✅ PyQt6.QtWidgets")
    except ImportError as e:
        print(f"  ❌ PyQt6.QtWidgets: {e}")
        print("\nPlease install PyQt6: pip install PyQt6")
        cleanup_test_environment()
        return 1
    
    try:
        from app.installation_wizard import ErikaInstallationWizard
        print("  ✅ Installation wizard")
    except ImportError as e:
        print(f"  ❌ Installation wizard: {e}")
        import traceback
        traceback.print_exc()
        cleanup_test_environment()
        return 1
    
    try:
        import requests
        print("  ✅ requests")
    except ImportError as e:
        print(f"  ❌ requests: {e}")
        print("\nPlease install requests: pip install requests")
        cleanup_test_environment()
        return 1
    
    print()
    print("✅ All imports successful!")
    print()
    
    # Create application
    print("Creating QApplication...")
    try:
        app = QApplication(sys.argv)
        print("  ✅ QApplication created")
    except Exception as e:
        print(f"  ❌ Failed to create QApplication: {e}")
        cleanup_test_environment()
        return 1
    
    # Create wizard with test config path
    print("Creating installation wizard...")
    try:
        wizard = ErikaInstallationWizard(allow_skip=True, config_path=TEST_CONFIG_FILE)
        print("  ✅ Wizard created")
    except Exception as e:
        print(f"  ❌ Failed to create wizard: {e}")
        import traceback
        traceback.print_exc()
        cleanup_test_environment()
        return 1
    
    print()
    print("="*60)
    print("🌿 INSTALLATION WIZARD")
    print("="*60)
    print()
    print("The wizard window should now be visible!")
    print()
    print("Instructions:")
    print("  1. Enter your EgoLlama server address")
    print("     Example: http://localhost:8082")
    print("     Example: http://egollama.company.com:8082")
    print()
    print("  2. Click '🔍 Test Connection' to verify")
    print()
    print("  3. Click '✅ Save & Continue' to save")
    print("     Or click 'Skip for Now' to configure later")
    print()
    print("="*60)
    print()
    
    # Show wizard
    result = wizard.exec()
    
    if result == wizard.DialogCode.Accepted:
        print()
        print("✅ Configuration saved successfully!")
        print()
        # Check what was saved
        from app.config_manager import ErikaConfigManager
        config = ErikaConfigManager()
        gateway_url = config.get_gateway_url()
        print(f"Gateway URL: {gateway_url}")
        print(f"Config file: {config.config_path}")
        print()
        print("="*60)
        print("📋 TEST RESULTS")
        print("="*60)
        print()
        print("✅ Wizard test completed successfully!")
        print(f"   Config saved to: {TEST_CONFIG_FILE}")
        print()
        if TEST_CONFIG_FILE.exists():
            import json
            with open(TEST_CONFIG_FILE, 'r') as f:
                saved_config = json.load(f)
            print("Saved configuration:")
            for key, value in saved_config.items():
                print(f"   {key}: {value}")
        print()
    else:
        print()
        print("⚠️  Wizard cancelled or skipped")
        print()
    
    # Cleanup
    cleanup_test_environment()
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        cleanup_test_environment()
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        cleanup_test_environment()
        sys.exit(1)
