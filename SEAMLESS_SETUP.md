# Seamless Setup System for Erika

## Overview

Erika now includes a **seamless installation system** that makes it easy for non-technical users to connect to the EgoLlama server, even if they don't know about Docker or servers.

## How It Works

### 1. First Run Detection

When a user runs Erika for the first time:
- The app checks if configuration exists in `~/.erika/config.json`
- If no config exists, the **Installation Wizard** automatically appears
- User-friendly interface guides them through setup

### 2. Installation Wizard Features

**Welcome Screen**:
- Friendly welcome message
- Clear instructions
- No technical jargon

**Server Configuration**:
- Simple text field for server address
- Default value: `http://localhost:8082`
- Examples shown: `http://egollama.company.com:8082`

**Connection Testing**:
- "🔍 Test Connection" button
- Real-time connection test in background thread
- Visual feedback:
  - ✅ Green = Success
  - ❌ Red = Failed (with error message)
- Progress bar during testing

**Flexible Options**:
- "Skip for Now" - Can configure later
- "Save & Continue" - Saves and starts app
- Settings can be changed anytime

### 3. Configuration Storage

**Location**: `~/.erika/config.json`

**Format**:
```json
{
  "egollama_gateway_url": "http://egollama.company.com:8082",
  "configured": true,
  "database_url": "postgresql://user:pass@localhost:5432/erika"
}
```

**Priority Order**:
1. Environment variable `EGOLLAMA_GATEWAY_URL` (highest priority)
2. Config file `~/.erika/config.json`
3. Default: `http://localhost:8082`

### 4. Settings Dialog

Users can reconfigure anytime:
- **Menu**: Settings → Server Settings
- Same friendly interface as wizard
- Test connection before saving
- Database settings also available

### 5. Automatic Integration

The gateway service automatically uses saved configuration:
```python
# No URL needed - uses config automatically!
gateway = ErikaEgoLlamaGateway()
```

## User Experience Flow

### First-Time User

1. **Downloads Erika**
2. **Runs**: `python scripts/run_erika.py`
3. **Wizard appears automatically**
4. **Enters server address** (gets from IT or uses default)
5. **Clicks "Test Connection"** → ✅ Success!
6. **Clicks "Save & Continue"**
7. **Erika starts** with server connected

**Total time**: ~30 seconds
**Technical knowledge required**: None!

### Returning User

1. **Runs**: `python scripts/run_erika.py`
2. **Erika starts immediately** (uses saved config)
3. **No wizard** (already configured)

### Changing Settings

1. **Opens**: Settings → Server Settings
2. **Changes address** if needed
3. **Tests connection**
4. **Saves**

## Technical Implementation

### Components

1. **`app/config_manager.py`**
   - Manages configuration file
   - Handles priority (env var → config → default)
   - Provides getter/setter methods

2. **`app/installation_wizard.py`**
   - Qt dialog for first-time setup
   - Connection testing with background worker
   - User-friendly UI

3. **`app/settings_dialog.py`**
   - Settings dialog for reconfiguration
   - Tabbed interface (Server, Database)
   - Connection testing

4. **`erika/services/egollama_gateway.py`**
   - Updated to use config manager automatically
   - No URL parameter needed if config exists

5. **`scripts/run_erika.py`**
   - Checks for first run
   - Shows wizard if needed
   - Sets environment variable for app

## Benefits

### For End Users

✅ **No technical knowledge needed**
- No Docker knowledge required
- No server configuration knowledge needed
- Just enter the address IT gives you

✅ **Visual feedback**
- See connection status immediately
- Clear error messages if something's wrong

✅ **Flexible**
- Can skip and configure later
- Can change settings anytime
- Works offline (saves locally)

### For IT Administrators

✅ **Easy deployment**
- Just provide server address to users
- No complex setup scripts
- Users configure themselves

✅ **Centralized server**
- All users connect to same server
- Easy to update server address
- Can pre-configure if needed

✅ **Troubleshooting**
- Users can test connection themselves
- Clear error messages
- Config file is human-readable

## Example Scenarios

### Scenario 1: Company Deployment

**IT Admin**:
1. Sets up EgoLlama Gateway at `http://egollama.company.com:8082`
2. Tells users: "Use this address: `http://egollama.company.com:8082`"

**End User**:
1. Runs Erika
2. Wizard appears
3. Enters: `http://egollama.company.com:8082`
4. Clicks "Test Connection" → ✅
5. Clicks "Save & Continue"
6. Done!

### Scenario 2: Local Development

**Developer**:
1. Runs EgoLlama Gateway locally on port 8082
2. Runs Erika
3. Wizard appears
4. Uses default: `http://localhost:8082`
5. Clicks "Test Connection" → ✅
6. Clicks "Save & Continue"
7. Done!

### Scenario 3: Network Issues

**User**:
1. Enters server address
2. Clicks "Test Connection" → ❌ "Could not connect"
3. Checks with IT: "Is the server running?"
4. IT fixes server
5. User clicks "Test Connection" again → ✅
6. Saves

## Future Enhancements

Potential improvements:
- **Auto-discovery**: Detect server on local network
- **Server list**: Pre-configured list of common servers
- **Connection profiles**: Save multiple server configurations
- **Advanced settings**: Timeout, retry count, etc.
- **Diagnostics**: Detailed connection diagnostics

## Testing

To test the installation system:

1. **Delete config** (simulate first run):
   ```bash
   rm ~/.erika/config.json
   ```

2. **Run Erika**:
   ```bash
   python scripts/run_erika.py
   ```

3. **Wizard should appear**

4. **Test connection** with a real server or mock server

5. **Save and verify** config file was created

## Conclusion

The seamless setup system makes Erika accessible to everyone, regardless of technical expertise. Users can get started in seconds, and IT administrators can deploy it easily across their organization.

