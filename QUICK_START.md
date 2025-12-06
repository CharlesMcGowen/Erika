# Quick Start - Running the Installation Wizard

## Run the Installation Wizard

The installation wizard can be run in several ways:

### Method 1: Run the Test Script (Recommended)

```bash
cd /media/ego/328010BE80108A8D1/github_public/EgoLlama-erika
python3 scripts/test_wizard.py
```

This will:
- Check all dependencies
- Verify imports
- Show the wizard window
- Guide you through setup

### Method 2: Run via Main App (First Run)

```bash
cd /media/ego/328010BE80108A8D1/github_public/EgoLlama-erika
python3 scripts/run_erika.py
```

If this is your first time running Erika, the wizard will appear automatically.

### Method 3: Run Wizard Directly

```bash
cd /media/ego/328010BE80108A8D1/github_public/EgoLlama-erika
python3 << 'EOF'
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from PyQt6.QtWidgets import QApplication
from app.installation_wizard import ErikaInstallationWizard

app = QApplication(sys.argv)
wizard = ErikaInstallationWizard(allow_skip=True)
wizard.show()
wizard.exec()
EOF
```

## What You'll See

1. **Welcome Screen**
   - "Welcome to Erika! 🌿"
   - Instructions for setting up the server connection

2. **Server Address Field**
   - Default: `http://localhost:8082`
   - Enter your EgoLlama server address here

3. **Test Connection Button**
   - Click to verify the server is reachable
   - Shows ✅ (green) if successful
   - Shows ❌ (red) with error message if failed

4. **Buttons**
   - **Skip for Now**: Skip setup and configure later
   - **Save & Continue**: Save configuration and continue

## Example Server Addresses

- **Local development**: `http://localhost:8082`
- **Company server**: `http://egollama.company.com:8082`
- **IP address**: `http://192.168.1.100:8082`
- **Custom port**: `http://server.com:9000`

## After Setup

Once you save the configuration:
- Settings are saved to `~/.erika/config.json`
- Erika will use this server automatically
- You can change it later in Settings → Server Settings

## Troubleshooting

**Wizard doesn't appear**:
- Make sure you have a display/GUI environment
- If using SSH, enable X11 forwarding: `ssh -X user@host`
- Check that PyQt6 is installed: `pip install PyQt6`

**"Could not connect" error**:
- Verify the server address is correct
- Check that the server is running
- Verify network connectivity
- You can still save and try later

**Import errors**:
- Install dependencies: `pip install -r requirements.txt`
- Make sure you're in the project directory

## Next Steps

After configuring the server:
1. Configure Gmail credentials (Settings → Configure Gmail)
2. Fetch emails from Gmail
3. Start using Erika's AI features!

