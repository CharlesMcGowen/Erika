# Erika Plugin Architecture

## Overview

Erika is designed as a **plugin** for the EgoLlama Gateway server. This document explains the architecture and how Erika integrates with EgoLlama.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│              EgoLlama Gateway Server                     │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Plugin Registry (/api/plugins)                   │  │
│  │  - Register plugins                                │  │
│  │  - List plugins                                    │  │
│  │  - Plugin info                                     │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Dynamic Router Inclusion                         │  │
│  │  - Includes plugin routers at runtime             │  │
│  │  - Supports external plugin URLs                 │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                        ▲
                        │ Plugin Registration
                        │ (HTTP POST /api/plugins/register)
                        │
┌───────────────────────┴───────────────────────────────┐
│              Erika Plugin Service                       │
│  ┌──────────────────────────────────────────────────┐  │
│  │  ErikaPluginClient                                │  │
│  │  - Connects to EgoLlama Gateway                   │  │
│  │  - Registers plugin metadata                      │  │
│  │  - Keep-alive loop                                │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  ErikaRouter (FastAPI)                           │  │
│  │  - /api/erika/emails                             │  │
│  │  - /api/erika/gmail/connect                      │  │
│  │  - /api/erika/stats                              │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Erika Services                                   │  │
│  │  - Gmail OAuth                                    │  │
│  │  - Email analysis                                 │  │
│  │  - Phishing detection                             │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Components

### 1. EgoLlama Gateway Plugin System

**Location:** `/mnt/webapps-nvme/EgoLlama/api/plugins/`

**Files:**
- `plugin_registry.py` - Plugin registration and management
- `__init__.py` - Package exports

**Key Features:**
- Plugin registration endpoint (`/api/plugins/register`)
- Plugin listing (`/api/plugins/list`)
- Dynamic router inclusion
- Plugin metadata storage

### 2. Erika Plugin

**Location:** `/media/ego/328010BE80108A8D1/github_public/EgoLlama-erika/erika/plugin/`

**Files:**
- `erika_plugin.py` - Main plugin class
- `erika_router.py` - FastAPI router with endpoints
- `plugin_client.py` - Client for gateway communication
- `__init__.py` - Package exports

**Key Features:**
- FastAPI router with email endpoints
- Gateway connection and registration
- Keep-alive mechanism
- Automatic reconnection

### 3. Plugin Service Launcher

**Location:** `/media/ego/328010BE80108A8D1/github_public/EgoLlama-erika/scripts/start_erika_plugin.py`

**Features:**
- Connects to EgoLlama Gateway
- Registers Erika plugin
- Maintains connection
- Standalone mode for testing

## Registration Flow

1. **Erika Plugin Service Starts**
   ```bash
   python scripts/start_erika_plugin.py
   ```

2. **Connect to Gateway**
   - Checks gateway health: `GET /health`
   - Verifies connection

3. **Register Plugin**
   - Sends registration: `POST /api/plugins/register`
   - Includes metadata:
     - Plugin name, version, description
     - Endpoint list
     - Capabilities

4. **Router Inclusion** (if Erika installed locally)
   - EgoLlama Gateway includes Erika's router
   - Endpoints available at `/api/erika/*`

5. **Keep-Alive Loop**
   - Periodic health checks
   - Automatic reconnection on failure
   - Re-registration if needed

## Plugin Endpoints

Once registered, Erika endpoints are available:

- `GET /api/erika/health` - Health check
- `GET /api/erika/emails` - Get emails
- `GET /api/erika/emails/{email_id}` - Get email details
- `POST /api/erika/emails/analyze` - Analyze email
- `POST /api/erika/gmail/connect` - Connect Gmail
- `GET /api/erika/gmail/status` - Gmail status
- `POST /api/erika/gmail/disconnect` - Disconnect Gmail
- `GET /api/erika/stats` - Statistics

## Two Integration Modes

### Mode 1: Local Router Inclusion (Recommended)

**How it works:**
- Erika is installed as a Python package in EgoLlama
- Erika's router is included directly in EgoLlama Gateway
- No separate server needed
- Fastest performance

**Setup:**
```bash
# In EgoLlama directory
pip install -e /path/to/EgoLlama-erika

# Erika router automatically included
```

### Mode 2: External Plugin Service

**How it works:**
- Erika runs as separate service
- Registers with EgoLlama via HTTP
- EgoLlama can proxy requests to Erika
- More flexible deployment

**Setup:**
```bash
# Start Erika plugin service
cd EgoLlama-erika
python scripts/start_erika_plugin.py
```

## Configuration

### Environment Variables

```bash
export EGOLLAMA_GATEWAY_URL="http://localhost:8082"
export DATABASE_URL="postgresql://user:pass@localhost:5432/erika"
```

### Config File

`~/.erika/config.json`:
```json
{
  "egollama_gateway_url": "http://localhost:8082",
  "database_url": "postgresql://user:pass@localhost:5432/erika"
}
```

## User Flow

1. **User downloads EgoLlama** → Runs gateway server
2. **User downloads Erika** → Installs plugin
3. **User runs Erika plugin service** → Connects to gateway
4. **User sets up Gmail OAuth** → Their own credentials
5. **User interacts with Erika** → Via EgoLlama agent interface

## Benefits

✅ **Separation of Concerns** - Erika is independent  
✅ **Modular** - Easy to add more plugins  
✅ **User Control** - Users manage their own OAuth  
✅ **Scalable** - Multiple plugins can register  
✅ **Clean Architecture** - Server handles routing, plugins provide features

## Future Enhancements

- Plugin discovery system
- Plugin versioning
- Plugin dependencies
- Plugin marketplace
- Automatic plugin updates

