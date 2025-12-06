# Erika Plugin Installation Guide

Erika is designed to work as a **plugin** for the EgoLlama Gateway server. This guide will walk you through installing and setting up Erika as a plugin.

## Architecture Overview

```
┌─────────────────────────────────────┐
│   EgoLlama Server (GitHub Repo)     │
│   - Main FastAPI Gateway            │
│   - Port 8082                       │
│   - Plugin registration system      │
└──────────────┬──────────────────────┘
               │
               │ Plugin Registration
               │
┌──────────────▼──────────────────────┐
│   Erika Plugin (This Repo)          │
│   - Email service                    │
│   - Gmail OAuth                      │
│   - Connects to EgoLlama Gateway    │
└─────────────────────────────────────┘
```

## Prerequisites

1. **EgoLlama Gateway Server** - Download and run from the [EgoLlama GitHub repository](https://github.com/your-org/EgoLlama)
2. **Python 3.8+** - Required for both EgoLlama and Erika
3. **PostgreSQL** (optional) - For storing email configurations and analysis results
4. **Gmail OAuth Credentials** - Your own Google Cloud OAuth credentials

## Installation Steps

### Step 1: Install EgoLlama Gateway

First, download and set up the EgoLlama Gateway server:

```bash
# Clone EgoLlama repository
git clone https://github.com/your-org/EgoLlama.git
cd EgoLlama

# Install dependencies
pip install -r requirements.txt

# Start EgoLlama Gateway
python unified_llama_gateway.py
# Or use the provided start script
./start_gateway.sh
```

The gateway should be running at `http://localhost:8082`.

### Step 2: Install Erika Plugin

```bash
# Clone Erika repository
git clone https://github.com/your-org/EgoLlama-erika.git
cd EgoLlama-erika

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Erika

Erika can be configured via:
1. **Environment variables** (recommended)
2. **Config file** (`~/.erika/config.json`)

#### Option A: Environment Variables

```bash
export EGOLLAMA_GATEWAY_URL="http://localhost:8082"
export DATABASE_URL="postgresql://user:password@localhost:5432/erika"
```

#### Option B: Config File

Create `~/.erika/config.json`:

```json
{
  "egollama_gateway_url": "http://localhost:8082",
  "database_url": "postgresql://user:password@localhost:5432/erika"
}
```

### Step 4: Start Erika Plugin

```bash
# Start Erika plugin service
python scripts/start_erika_plugin.py

# Or with custom gateway URL
python scripts/start_erika_plugin.py --gateway-url http://localhost:8082
```

You should see:
```
🌿 Starting Erika Plugin Service
   Gateway URL: http://localhost:8082
   Standalone mode: False
🔌 Connecting to EgoLlama Gateway...
✅ Erika plugin registered successfully!

📧 Erika is now available as an agent in EgoLlama Gateway
   Access Erika endpoints at: http://localhost:8082/api/erika

🔄 Starting keep-alive loop...
   Press Ctrl+C to stop
```

### Step 5: Verify Plugin Registration

Check that Erika is registered:

```bash
# List all plugins
curl http://localhost:8082/api/plugins/list

# Get Erika plugin info
curl http://localhost:8082/api/plugins/erika
```

### Step 6: Set Up Gmail OAuth

1. **Get Gmail OAuth Credentials:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing
   - Enable Gmail API
   - Create OAuth 2.0 credentials (Desktop app type)
   - Download credentials

2. **Connect Gmail via API:**
   ```bash
   curl -X POST http://localhost:8082/api/erika/gmail/connect \
     -H "Content-Type: application/json" \
     -d '{
       "client_id": "your-client-id",
       "client_secret": "your-client-secret",
       "user_id": "default"
     }'
   ```

3. **Complete OAuth Flow:**
   - The first time you connect, you'll need to complete the OAuth flow
   - Follow the instructions in the response to authorize access

## Usage

### Access Erika Endpoints

Once registered, Erika endpoints are available at:
- `http://localhost:8082/api/erika/health` - Health check
- `http://localhost:8082/api/erika/emails` - Get emails
- `http://localhost:8082/api/erika/gmail/status` - Gmail connection status
- `http://localhost:8082/api/erika/stats` - Statistics

### Example: Get Emails

```bash
curl http://localhost:8082/api/erika/emails?max_results=10&days_back=7
```

### Example: Check Gmail Status

```bash
curl http://localhost:8082/api/erika/gmail/status
```

## Standalone Mode (Testing)

For testing without EgoLlama Gateway:

```bash
python scripts/start_erika_plugin.py --standalone
```

This runs Erika as a standalone FastAPI server on port 8000:
- `http://localhost:8000/api/erika/health`
- `http://localhost:8000/api/erika/emails`
- etc.

## Troubleshooting

### Plugin Registration Fails

**Error:** `Cannot connect to EgoLlama Gateway`

**Solution:**
1. Make sure EgoLlama Gateway is running
2. Check the gateway URL: `curl http://localhost:8082/health`
3. Verify firewall/network settings

### Gmail Authentication Fails

**Error:** `Gmail authentication failed`

**Solution:**
1. Verify OAuth credentials are correct
2. Check that Gmail API is enabled in Google Cloud Console
3. Ensure OAuth consent screen is configured
4. Complete OAuth flow manually if needed

### Database Connection Issues

**Error:** `Database connection failed`

**Solution:**
1. Verify PostgreSQL is running
2. Check `DATABASE_URL` environment variable
3. Ensure database exists and user has permissions
4. Erika can run without database (with limited features)

## Advanced Configuration

### Keep-Alive Interval

Adjust the keep-alive check interval:

```bash
python scripts/start_erika_plugin.py --keep-alive-interval 30
```

### Custom Gateway URL

```bash
python scripts/start_erika_plugin.py --gateway-url http://192.168.1.100:8082
```

## Plugin Architecture

### How It Works

1. **Erika Plugin Service** starts and connects to EgoLlama Gateway
2. **Registration** - Erika registers itself via `/api/plugins/register`
3. **Router Inclusion** - EgoLlama Gateway includes Erika's router
4. **Keep-Alive** - Erika maintains connection with periodic health checks
5. **Reconnection** - Automatic reconnection if gateway connection is lost

### Plugin Components

- **`erika/plugin/erika_plugin.py`** - Main plugin class
- **`erika/plugin/erika_router.py`** - FastAPI router with endpoints
- **`erika/plugin/plugin_client.py`** - Client for gateway communication
- **`scripts/start_erika_plugin.py`** - Plugin service launcher

## Next Steps

- Set up Gmail OAuth credentials
- Configure email keywords and filters
- Enable phishing detection features
- Set up AresBridge threat scoring

See the main [README.md](README.md) for more details on Erika's features.

