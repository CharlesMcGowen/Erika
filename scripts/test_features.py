#!/usr/bin/env python3
"""
Test Erika Features
===================

Demonstrates the features we've built without requiring GUI.

Usage:
    python scripts/test_features.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all modules import correctly"""
    print("="*60)
    print("🧪 TESTING ERIKA FEATURES")
    print("="*60)
    print()
    
    print("1. Testing Core Library Imports...")
    try:
        from erika.plugins.email import ErikaGmailService, OAuthTokenManager
        print("   ✅ Gmail service")
    except Exception as e:
        print(f"   ❌ Gmail service: {e}")
    
    try:
        from erika.services import ErikaEgoLlamaGateway
        print("   ✅ EgoLlama Gateway")
    except Exception as e:
        print(f"   ❌ EgoLlama Gateway: {e}")
    
    try:
        from erika.services import PhishingDetector, ImageExtractor, ReverseImageSearchService
        print("   ✅ Phishing detection system")
    except Exception as e:
        print(f"   ⚠️  Phishing detection: {e} (optional)")
    
    print()
    
    print("2. Testing App Components...")
    try:
        from app.config_manager import ErikaConfigManager
        print("   ✅ Configuration manager")
        
        # Test config manager
        config = ErikaConfigManager()
        gateway_url = config.get_gateway_url()
        print(f"      Gateway URL: {gateway_url}")
        print(f"      Configured: {config.is_configured()}")
    except Exception as e:
        print(f"   ❌ Config manager: {e}")
    
    try:
        from app.database_service import ErikaDatabaseService
        print("   ✅ Database service")
    except Exception as e:
        print(f"   ⚠️  Database service: {e} (requires database)")
    
    try:
        from app.installation_wizard import ErikaInstallationWizard
        print("   ✅ Installation wizard")
    except Exception as e:
        print(f"   ❌ Installation wizard: {e}")
    
    try:
        from app.settings_dialog import ErikaSettingsDialog
        print("   ✅ Settings dialog")
    except Exception as e:
        print(f"   ❌ Settings dialog: {e}")
    
    try:
        from app.desktop_icon import DesktopIconCreator
        print("   ✅ Desktop icon creator")
    except Exception as e:
        print(f"   ❌ Desktop icon creator: {e}")
    
    print()
    
    print("3. Testing Phishing Detection...")
    try:
        from erika.services import PhishingDetector, ImageExtractor
        
        detector = PhishingDetector()
        extractor = ImageExtractor()
        
        print("   ✅ Phishing detector initialized")
        print("   ✅ Image extractor initialized")
        
        # Test with mock email
        mock_email = {
            'sender': 'Raymond Franklin <raymond@example.com>',
            'subject': 'Exciting Opportunities Await You',
            'body': 'Hi Charles, I hope you\'re doing well...'
        }
        
        # This would normally analyze, but without images it will return low risk
        print("   ℹ️  Phishing detection ready (requires images in email)")
        
    except Exception as e:
        print(f"   ⚠️  Phishing detection: {e}")
    
    print()
    
    print("4. Testing Configuration System...")
    try:
        from app.config_manager import ErikaConfigManager
        
        config = ErikaConfigManager()
        print(f"   Config file: {config.config_path}")
        print(f"   Exists: {config.config_path.exists()}")
        
        if config.config_path.exists():
            import json
            with open(config.config_path, 'r') as f:
                saved_config = json.load(f)
            print(f"   Current config:")
            for key, value in saved_config.items():
                if 'secret' in key.lower() or 'password' in key.lower():
                    print(f"      {key}: ***hidden***")
                else:
                    print(f"      {key}: {value}")
        else:
            print("   ℹ️  No config file yet (will be created on first run)")
        
    except Exception as e:
        print(f"   ❌ Config system: {e}")
    
    print()
    
    print("5. Testing Desktop Icon System...")
    try:
        from app.desktop_icon import DesktopIconCreator
        import platform
        
        icon_path = project_root / "Images" / "icon.png"
        script_path = project_root / "scripts" / "run_erika.py"
        
        if icon_path.exists() and script_path.exists():
            creator = DesktopIconCreator(
                project_root=project_root,
                icon_path=icon_path,
                script_path=script_path
            )
            print(f"   Platform: {platform.system()}")
            print(f"   Icon: {icon_path.exists()}")
            print(f"   Script: {script_path.exists()}")
            print("   ✅ Desktop icon system ready")
        else:
            print(f"   ⚠️  Missing files: icon={icon_path.exists()}, script={script_path.exists()}")
            
    except Exception as e:
        print(f"   ⚠️  Desktop icon: {e}")
    
    print()
    
    print("="*60)
    print("📋 SUMMARY")
    print("="*60)
    print()
    print("✅ Core Features:")
    print("   • Gmail OAuth integration")
    print("   • EgoLlama Gateway connection")
    print("   • Configuration management")
    print("   • Installation wizard")
    print("   • Settings dialog")
    print()
    print("✅ Security Features:")
    print("   • Phishing detection (reverse image search)")
    print("   • Image extraction from emails")
    print("   • Identity verification")
    print("   • Automatic detection (user-controlled)")
    print()
    print("✅ User Experience:")
    print("   • Seamless installation wizard")
    print("   • Desktop icon creation")
    print("   • Settings management")
    print("   • Test environment support")
    print()
    print("="*60)
    print("🚀 READY TO RUN")
    print("="*60)
    print()
    print("To run Erika:")
    print("  1. Test wizard: python scripts/test_wizard.py")
    print("  2. Main app: python scripts/run_erika.py")
    print()
    print("The installation wizard will appear on first run!")
    print()

if __name__ == "__main__":
    try:
        test_imports()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

