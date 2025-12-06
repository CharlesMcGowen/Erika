# Desktop Icon Setup

Erika can create desktop shortcuts/icons for easy access on Windows, Linux, and macOS.

## Automatic Setup

The installation wizard (`test_wizard.py`) automatically creates a desktop icon when you run it:

```bash
python scripts/test_wizard.py
```

The icon will be created on your desktop with the Erika logo.

## Manual Setup

You can also create the desktop icon manually:

```python
from pathlib import Path
from app.desktop_icon import DesktopIconCreator

project_root = Path(__file__).parent
icon_path = project_root / "Images" / "icon.png"
script_path = project_root / "scripts" / "run_erika.py"

creator = DesktopIconCreator(
    project_root=project_root,
    icon_path=icon_path,
    script_path=script_path
)

success, message = creator.create_desktop_icon()
print(message)
```

## Platform-Specific Details

### Linux

Creates a `.desktop` file in `~/Desktop/`:
- File: `Erika.desktop`
- Uses the icon from `Images/icon.png`
- Launches: `python scripts/run_erika.py`
- Category: Office, Email, Utility

**Requirements**: None (works out of the box)

### Windows

Creates a `.lnk` shortcut file in `%USERPROFILE%\Desktop\`:
- File: `Erika.lnk`
- Uses the icon from `Images/icon.png`
- Launches: `python scripts/run_erika.py`

**Requirements**: 
- `pywin32` package for `.lnk` files (recommended)
- Falls back to `.bat` file if `pywin32` not available

**Install pywin32**:
```bash
pip install pywin32
```

### macOS

Creates an `.app` bundle in `~/Applications/`:
- Bundle: `Erika.app`
- Includes icon in Resources folder
- Launches: `python scripts/run_erika.py`

**Requirements**: None (works out of the box)

**Note**: On macOS, you may need to right-click the app and select "Open" the first time, as macOS may block unsigned applications.

## Removing Desktop Icons

To remove the desktop icon:

```python
from app.desktop_icon import DesktopIconCreator

creator = DesktopIconCreator(...)
success, message = creator.remove_desktop_icon()
print(message)
```

Or manually:
- **Linux**: Delete `~/Desktop/Erika.desktop`
- **Windows**: Delete `%USERPROFILE%\Desktop\Erika.lnk` or `Erika.bat`
- **macOS**: Delete `~/Applications/Erika.app`

## Icon File

The icon is located at:
- `Images/icon.png`

This is a PNG image file that will be used for the desktop icon on all platforms.

## Troubleshooting

### Linux: Icon doesn't appear
- Make sure the `.desktop` file is executable: `chmod +x ~/Desktop/Erika.desktop`
- Some desktop environments may require the file to be in `~/.local/share/applications/` instead

### Windows: Shortcut doesn't work
- Install `pywin32`: `pip install pywin32`
- Or use the `.bat` file that was created as fallback

### macOS: App won't open
- Right-click the app and select "Open" (first time only)
- Or go to System Preferences → Security & Privacy → Allow apps from unidentified developers

### Icon not showing
- Make sure `Images/icon.png` exists
- Verify the icon file is a valid PNG image
- Some systems may cache icons - try refreshing the desktop

