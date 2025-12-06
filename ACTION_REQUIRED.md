# Action Required: Gateway Restart

## Current Situation

The EgoLlama Gateway is running with an **old version** that doesn't include the plugin router code.

**Process Details:**
- PID: 8964
- Started: December 4, 2024
- Status: Running (holding port 8082)
- Issue: Doesn't have plugin router code

## Problem

The gateway process cannot be killed via normal means (requires root/sudo permissions). The plugin router code exists and works correctly, but the running gateway instance doesn't have it loaded.

## Solution Options

### Option 1: Manual Restart (Recommended)

You'll need to manually restart the gateway:

```bash
# 1. Stop the current gateway
# If running in a terminal/screen/tmux:
#   - Press Ctrl+C
#   - Or: screen -r / tmux attach, then Ctrl+C

# If running as a service:
sudo systemctl stop egollama-gateway
# or
sudo service egollama-gateway stop

# 2. Start the gateway
cd /mnt/webapps-nvme/EgoLlama
python3 unified_llama_gateway.py
```

### Option 2: Use Different Port (Temporary Testing)

For testing purposes, you could run a new gateway instance on a different port:

```bash
# Edit unified_llama_gateway.py to use port 8083
# Or use uvicorn directly:
cd /mnt/webapps-nvme/EgoLlama
uvicorn unified_llama_gateway:app --host 0.0.0.0 --port 8083

# Then test with:
export EGOLLAMA_GATEWAY_URL="http://localhost:8083"
python3 scripts/test_plugin_api.py
```

### Option 3: Check if Running as Service

The gateway might be running as a systemd service:

```bash
# Check if service exists
systemctl list-units | grep -i egollama
systemctl list-units | grep -i llama
systemctl list-units | grep -i gateway

# If found, restart it:
sudo systemctl restart <service-name>
```

## Verification

After restart, verify the plugin router is loaded:

```bash
# 1. Check gateway health
curl http://localhost:8082/health

# 2. Test plugin endpoint
curl http://localhost:8082/api/plugins/list

# 3. Run full test suite
cd /media/ego/328010BE80108A8D1/github_public/EgoLlama-erika
python3 scripts/test_plugin_api.py
```

## Expected Results

After restart, you should see:
- ✅ `GET /api/plugins/list` returns 200 with empty list `{"success": true, "plugins": [], "count": 0}`
- ✅ `POST /api/plugins/register` accepts plugin registration
- ✅ Plugin endpoints appear in `/docs` OpenAPI documentation

## Code Status

✅ **All plugin code is correct and ready**
- Router imports successfully
- All endpoints defined correctly
- Integration code in place

The only issue is the running gateway instance needs to be restarted to load the new code.

