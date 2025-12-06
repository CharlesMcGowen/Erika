#!/usr/bin/env python3
"""
Desktop Icon Creator for Erika
================================

Creates desktop shortcuts/icons for Windows, Linux, and macOS.

Author: Living Archive team
Version: 1.0.0
"""

import sys
import os
import platform
import shutil
from pathlib import Path
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class DesktopIconCreator:
    """Creates desktop icons for different platforms"""
    
    def __init__(self, project_root: Path, icon_path: Path, script_path: Path):
        """
        Initialize desktop icon creator
        
        Args:
            project_root: Root directory of the Erika project
            icon_path: Path to the icon image file
            script_path: Path to the script to run (run_erika.py)
        """
        self.project_root = project_root
        self.icon_path = icon_path
        self.script_path = script_path
        self.system = platform.system()
        
    def create_desktop_icon(self) -> Tuple[bool, str]:
        """
        Create desktop icon for current platform
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if self.system == "Linux":
            return self._create_linux_desktop()
        elif self.system == "Windows":
            return self._create_windows_shortcut()
        elif self.system == "Darwin":  # macOS
            return self._create_macos_app()
        else:
            return False, f"Unsupported platform: {self.system}"
    
    def _create_linux_desktop(self) -> Tuple[bool, str]:
        """Create Linux .desktop file"""
        try:
            messages = []
            
            # Get absolute paths
            icon_abs = self.icon_path.resolve()
            script_abs = self.script_path.resolve()
            python_exe = sys.executable
            
            # Create .desktop file content
            desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Erika
Comment=AI-powered email management system
Exec={python_exe} {script_abs}
Icon={icon_abs}
Terminal=false
Categories=Office;Email;Utility;
StartupNotify=true
"""
            
            # 1. Create on Desktop
            desktop_dir = Path.home() / "Desktop"
            if not desktop_dir.exists():
                # Try XDG desktop directory
                xdg_desktop = os.getenv('XDG_DESKTOP_DIR')
                if xdg_desktop:
                    desktop_dir = Path(xdg_desktop)
                else:
                    # Fallback to ~/Desktop
                    desktop_dir.mkdir(exist_ok=True)
            
            desktop_file = desktop_dir / "Erika.desktop"
            try:
                with open(desktop_file, 'w') as f:
                    f.write(desktop_content)
                os.chmod(desktop_file, 0o755)
                messages.append(f"Desktop: {desktop_file}")
            except Exception as e:
                messages.append(f"Desktop creation failed: {e}")
            
            # 2. Create in applications directory (for app menu)
            applications_dir = Path.home() / ".local" / "share" / "applications"
            applications_dir.mkdir(parents=True, exist_ok=True)
            app_file = applications_dir / "Erika.desktop"
            try:
                with open(app_file, 'w') as f:
                    f.write(desktop_content)
                os.chmod(app_file, 0o755)
                messages.append(f"Applications: {app_file}")
            except Exception as e:
                messages.append(f"Applications creation failed: {e}")
            
            if messages:
                return True, f"✅ Linux desktop icon created:\n   " + "\n   ".join(messages)
            else:
                return False, "❌ Failed to create desktop icon"
            
        except Exception as e:
            return False, f"❌ Failed to create Linux desktop icon: {e}"
    
    def _create_windows_shortcut(self) -> Tuple[bool, str]:
        """Create Windows shortcut (.lnk file)"""
        try:
            # Try using win32com (if available)
            try:
                import win32com.client
                
                desktop = Path.home() / "Desktop"
                shortcut_path = desktop / "Erika.lnk"
                
                python_exe = sys.executable
                script_abs = self.script_path.resolve()
                icon_abs = self.icon_path.resolve()
                
                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(str(shortcut_path))
                shortcut.Targetpath = python_exe
                shortcut.Arguments = f'"{script_abs}"'
                shortcut.WorkingDirectory = str(self.project_root)
                shortcut.IconLocation = str(icon_abs)
                shortcut.save()
                
                return True, f"✅ Windows shortcut created: {shortcut_path}"
                
            except ImportError:
                # Fallback: Create batch file
                return self._create_windows_batch()
                
        except Exception as e:
            return False, f"❌ Failed to create Windows shortcut: {e}"
    
    def _create_windows_batch(self) -> Tuple[bool, str]:
        """Create Windows batch file as fallback"""
        try:
            desktop = Path.home() / "Desktop"
            batch_file = desktop / "Erika.bat"
            
            python_exe = sys.executable
            script_abs = self.script_path.resolve()
            project_abs = self.project_root.resolve()
            
            batch_content = f"""@echo off
cd /d "{project_abs}"
"{python_exe}" "{script_abs}"
pause
"""
            
            with open(batch_file, 'w') as f:
                f.write(batch_content)
            
            return True, f"✅ Windows batch file created: {batch_file}\n   (Install pywin32 for .lnk shortcut: pip install pywin32)"
            
        except Exception as e:
            return False, f"❌ Failed to create Windows batch file: {e}"
    
    def _create_macos_app(self) -> Tuple[bool, str]:
        """Create macOS .app bundle"""
        try:
            applications_dir = Path.home() / "Applications"
            app_bundle = applications_dir / "Erika.app"
            contents_dir = app_bundle / "Contents"
            macos_dir = contents_dir / "MacOS"
            resources_dir = contents_dir / "Resources"
            
            # Create directory structure
            macos_dir.mkdir(parents=True, exist_ok=True)
            resources_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy icon
            icon_dest = resources_dir / "icon.png"
            shutil.copy(self.icon_path, icon_dest)
            
            # Create Info.plist
            python_exe = sys.executable
            script_abs = self.script_path.resolve()
            
            info_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>Erika</string>
    <key>CFBundleIconFile</key>
    <string>icon.png</string>
    <key>CFBundleIdentifier</key>
    <string>com.egollama.erika</string>
    <key>CFBundleName</key>
    <string>Erika</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
</dict>
</plist>
"""
            
            with open(contents_dir / "Info.plist", 'w') as f:
                f.write(info_plist)
            
            # Create launcher script
            launcher_script = f"""#!/bin/bash
cd "{self.project_root}"
"{python_exe}" "{script_abs}"
"""
            
            launcher_path = macos_dir / "Erika"
            with open(launcher_path, 'w') as f:
                f.write(launcher_script)
            
            # Make executable
            os.chmod(launcher_path, 0o755)
            
            return True, f"✅ macOS app bundle created: {app_bundle}\n   (You may need to right-click and select 'Open' the first time)"
            
        except Exception as e:
            return False, f"❌ Failed to create macOS app bundle: {e}"
    
    def remove_desktop_icon(self) -> Tuple[bool, str]:
        """
        Remove desktop icon
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if self.system == "Linux":
                desktop_file = Path.home() / "Desktop" / "Erika.desktop"
                if desktop_file.exists():
                    desktop_file.unlink()
                    return True, "✅ Linux desktop icon removed"
                return False, "Desktop icon not found"
                
            elif self.system == "Windows":
                shortcut = Path.home() / "Desktop" / "Erika.lnk"
                batch = Path.home() / "Desktop" / "Erika.bat"
                removed = []
                if shortcut.exists():
                    shortcut.unlink()
                    removed.append("shortcut")
                if batch.exists():
                    batch.unlink()
                    removed.append("batch file")
                if removed:
                    return True, f"✅ Removed: {', '.join(removed)}"
                return False, "Desktop icon not found"
                
            elif self.system == "Darwin":
                app_bundle = Path.home() / "Applications" / "Erika.app"
                if app_bundle.exists():
                    shutil.rmtree(app_bundle)
                    return True, "✅ macOS app bundle removed"
                return False, "App bundle not found"
                
        except Exception as e:
            return False, f"❌ Failed to remove desktop icon: {e}"

