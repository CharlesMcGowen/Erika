# Erika Installation Guide

## Quick Start for New Users

Erika now includes an **Installation Wizard** that makes setup seamless, even if you don't know about Docker or servers!

### First Time Setup

1. **Run Erika**:
   ```bash
   python scripts/run_erika.py
   ```

2. **Installation Wizard appears automatically**:
   - If this is your first time running Erika, a welcome wizard will appear
   - Enter your EgoLlama server address (ask your IT department if you don't know it)
   - Example addresses:
     - `http://localhost:8082` (if server is on your computer)
     - `http://egollama.company.com:8082` (company server)
     - `http://192.168.1.100:8082` (local network server)

3. **Test Connection**:
   - Click "🔍 Test Connection" to verify the server is reachable
   - You'll see ✅ if successful, or ❌ with an error message

4. **Save & Continue**:
   - Click "✅ Save & Continue" to save your settings
   - Erika will remember this configuration for future use

5. **Skip Option**:
   - You can click "Skip for Now" if you want to configure later
   - Access settings anytime from the Settings menu

### Changing Settings Later

1. **Open Settings**:
   - In the Erika app, go to **Settings → Server Settings**
   - Or use the menu: **Settings → Server Settings**

2. **Update Server Address**:
   - Change the server address if needed
   - Click "🔍 Test Connection" to verify
   - Click "💾 Save" to save changes

### Configuration Storage

Your settings are saved in:
- **Location**: `~/.erika/config.json`
- **Format**: JSON file (human-readable)
- **Security**: Stored locally on your computer

Example config file:
```json
{
  "egollama_gateway_url": "http://egollama.company.com:8082",
  "configured": true
}
```

### Environment Variables (Advanced)

If you prefer environment variables, you can still use:
```bash
export EGOLLAMA_GATEWAY_URL="http://egollama.company.com:8082"
```

The priority order is:
1. Environment variable `EGOLLAMA_GATEWAY_URL`
2. Config file `~/.erika/config.json`
3. Default: `http://localhost:8082`

### Troubleshooting

**"Could not connect to server"**:
- Check if the server address is correct
- Verify the server is running
- Check your network connection
- Ask your IT department for the correct address

**"Server returned status 404"**:
- The server might not have the `/health` endpoint
- Try the address anyway - Erika will work if the server is correct

**Settings not saving**:
- Check file permissions on `~/.erika/` directory
- Make sure you have write access to your home directory

### For IT Administrators

If you're setting up Erika for multiple users:

1. **Provide Server Address**:
   - Give users the EgoLlama Gateway URL
   - Example: `http://egollama.company.com:8082`

2. **Network Requirements**:
   - Users need network access to the Gateway server
   - Port 8082 (or your configured port) must be accessible

3. **Health Endpoint**:
   - Gateway should have `/health` endpoint for connection testing
   - Returns HTTP 200 if healthy

4. **Bulk Configuration** (Optional):
   - You can pre-create config files for users
   - Place `config.json` in `~/.erika/` for each user

### Next Steps

After installation:
1. Configure Gmail credentials (Settings → Configure Gmail)
2. Fetch emails from Gmail
3. Start using Erika's AI-powered email management!

For more information, see the main [README.md](README.md).

