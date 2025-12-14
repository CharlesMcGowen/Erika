# Erika CLI - Feature Parity with GUI

This document shows how all GUI features are available via CLI commands.

## ✅ Complete Feature Parity

### Installation Wizard → `setup` command
**GUI**: First-run wizard to configure EgoLlama Gateway  
**CLI**: `python erika_cli.py setup [--gateway-url URL] [--test]`

- ✅ Configure gateway URL
- ✅ Test connection
- ✅ Save configuration

### Settings Dialog → `settings` command
**GUI**: Configure server, security, and database settings  
**CLI**: `python erika_cli.py settings [options]`

- ✅ Gateway URL configuration
- ✅ Database URL configuration
- ✅ Phishing detection enable/disable
- ✅ Reverse image search enable/disable
- ✅ AresBridge threat detection enable/disable
- ✅ Auto-mitigation enable/disable
- ✅ Test gateway connection

### Credentials Dialog → `config` command
**GUI**: Configure Gmail OAuth2 credentials  
**CLI**: `python erika_cli.py config [options]`

- ✅ Client ID and Client Secret configuration
- ✅ Test credentials
- ✅ Enable/disable Gmail integration
- ✅ Interactive and non-interactive modes

### Connect Gmail Button → `authenticate` command
**GUI**: Connect to Gmail (opens browser)  
**CLI**: `python erika_cli.py authenticate [--refresh]`

- ✅ OAuth2 authentication
- ✅ Token refresh
- ✅ Browser-based authentication

### Main Window Status → `status` command
**GUI**: Display connection status  
**CLI**: `python erika_cli.py status [--output FORMAT]`

- ✅ Gmail configuration status
- ✅ Gateway URL status
- ✅ Database availability
- ✅ Security feature status
- ✅ Human-readable and JSON output

### Email Operations → `check`, `monitor`, `analyze`, `sort`
**GUI**: Email viewing and analysis (via plugin/Gateway)  
**CLI**: Multiple commands for email operations

- ✅ `check` - One-time email check
- ✅ `monitor` - Continuous monitoring (daemon mode)
- ✅ `analyze` - Fraud analysis on specific emails
- ✅ `sort` - Categorize emails by risk level

## 🎯 Additional CLI-Only Features

- **JSON Output**: All commands support `--output json` for scripting
- **Daemon Mode**: `monitor` command runs continuously
- **Non-Interactive Mode**: All configuration can be done via arguments
- **Batch Operations**: Process multiple emails efficiently

## 📊 Command Mapping

| GUI Feature | CLI Command | Notes |
|------------|-------------|-------|
| Installation Wizard | `setup` | First-time configuration |
| Settings Dialog | `settings` | All settings management |
| Credentials Dialog | `config` | Gmail OAuth2 setup |
| Connect Gmail | `authenticate` | OAuth authentication |
| Status Display | `status` | Configuration status |
| Email Viewing | `check` | One-time email fetch |
| Email Monitoring | `monitor` | Continuous monitoring |
| Fraud Analysis | `analyze` | Deep analysis |
| Email Sorting | `sort` | Risk categorization |

## 🚀 Usage Examples

### Complete Setup (matches GUI workflow)

```bash
# 1. Setup wizard
python erika_cli.py setup --gateway-url http://localhost:8082 --test

# 2. Configure credentials
python erika_cli.py config --client-id ID --client-secret SECRET --test

# 3. Authenticate
python erika_cli.py authenticate

# 4. Check status
python erika_cli.py status

# 5. Start monitoring
python erika_cli.py monitor
```

All GUI features are now available via command line! 🎉
