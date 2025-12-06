# Gateway Restart Instructions

## Current Situation

✅ **Plugin router code is working!** The new gateway successfully loads:
```
INFO ✅ Plugin Management API router registered
```

❌ **Old gateway process (PID 8964) is blocking port 8082**

## Solution: Stop Old Process

The old gateway process is running as **root**, so you need elevated permissions to stop it.

### Option 1: Using sudo (Recommended)

```bash
sudo kill -9 8964
```

Then start the new gateway:
```bash
cd /mnt/webapps-nvme/EgoLlama
python3 unified_llama_gateway.py
```

### Option 2: If running in screen/tmux

If the gateway is running in a screen or tmux session:

```bash
# Find the session
screen -ls
# or
tmux ls

# Attach to it
screen -r <session-name>
# or
tmux attach -t <session-name>

# Stop with Ctrl+C, then restart
python3 unified_llama_gateway.py
```

### Option 3: If running as systemd service

```bash
# Check if it's a service
systemctl list-units | grep -i egollama
systemctl list-units | grep -i gateway

# If found, restart it
sudo systemctl restart <service-name>
```

## Verification

After restarting, verify the plugin endpoints work:

```bash
# 1. Check gateway health
curl http://localhost:8082/health

# 2. Test plugin endpoint
curl http://localhost:8082/api/plugins/list
# Expected: {"success": true, "plugins": [], "count": 0}

# 3. Run full test suite
cd /media/ego/328010BE80108A8D1/github_public/EgoLlama-erika
python3 scripts/test_plugin_api.py
```

## Expected Results

After restart, you should see:
- ✅ Gateway starts successfully
- ✅ Plugin router loads: "✅ Plugin Management API router registered"
- ✅ Plugin endpoints available at `/api/plugins/*`
- ✅ Test suite passes

## Quick Test Command

Once restarted, test immediately:
```bash
curl http://localhost:8082/api/plugins/list && echo ""
```

If you see `{"success": true, "plugins": [], "count": 0}`, the plugin system is working!

