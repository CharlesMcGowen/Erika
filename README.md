# Erika CLI - Email Monitoring and Fraud Detection

**Command-line interface for Erika email assistant** - Monitor email servers, detect fraud, sort emails, and configure settings all from the command line. No GUI required!

**Copyright (c) 2024 Living Archive team. All Rights Reserved.**

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# First-time setup
python erika_cli.py setup --gateway-url http://localhost:8082

# Configure Gmail credentials
python erika_cli.py config --client-id YOUR_CLIENT_ID --client-secret YOUR_SECRET

# Authenticate with Gmail
python erika_cli.py authenticate

# Check emails
python erika_cli.py check

# Monitor emails continuously
python erika_cli.py monitor --interval 300
```

## 📋 Features

All GUI features available via command line:

- ✅ **Email Monitoring** - Continuous monitoring with daemon mode
- ✅ **Fraud Detection** - Phishing detection and threat analysis
- ✅ **Email Sorting** - Automatic categorization by risk level
- ✅ **Configuration** - Full settings management via CLI
- ✅ **Gmail Integration** - OAuth2 authentication and email access
- ✅ **Gateway Integration** - EgoLlama Gateway server connection
- ✅ **Security Settings** - Phishing detection, reverse image search, AresBridge

## 📖 Commands

### Setup & Configuration

#### `setup` - First-time setup wizard
Configure EgoLlama Gateway connection (matches Installation Wizard).

```bash
# Interactive setup
python erika_cli.py setup

# Non-interactive setup
python erika_cli.py setup --gateway-url http://localhost:8082 --test
```

#### `config` - Configure email provider credentials
Set up email provider credentials (Gmail OAuth2 or IMAP).

**Gmail (OAuth2):**
```bash
# Interactive mode
python erika_cli.py config --provider gmail

# Non-interactive mode
python erika_cli.py config --provider gmail --client-id YOUR_ID --client-secret YOUR_SECRET --test

# Enable/disable
python erika_cli.py config --provider gmail --enable
```

**IMAP (Yahoo, iCloud, custom servers):**
```bash
# Interactive mode
python erika_cli.py config --provider imap

# Non-interactive mode
python erika_cli.py config --provider imap --imap-server imap.mail.yahoo.com --imap-username user@yahoo.com --imap-password PASSWORD --test
```

#### `settings` - Configure Erika settings
Manage all settings (matches Settings Dialog).

```bash
# Configure gateway URL
python erika_cli.py settings --gateway-url http://localhost:8082 --test-gateway

# Configure database
python erika_cli.py settings --database-url postgresql://user:pass@localhost:5432/erika

# Security settings
python erika_cli.py settings --phishing-enabled true --reverse-search-enabled true
python erika_cli.py settings --ares-enabled true --auto-mitigate false
```

#### `authenticate` - Authenticate with Gmail
Connect to Gmail (opens browser for OAuth).

```bash
# Authenticate (first time or refresh)
python erika_cli.py authenticate

# Force token refresh
python erika_cli.py authenticate --refresh
```

#### `status` - Show Erika status
Display current configuration status (matches Main Window status).

```bash
# Human-readable format
python erika_cli.py status

# JSON format
python erika_cli.py status --output json
```

### Email Operations

#### `check` - Check for unread emails
One-time email check.

```bash
# Default (50 emails, last 7 days)
python erika_cli.py check

# Custom parameters
python erika_cli.py check --max-results 100 --days-back 14

# JSON output
python erika_cli.py check --output json
```

#### `monitor` - Monitor emails continuously
Daemon mode for continuous email monitoring.

```bash
# Default (check every 5 minutes)
python erika_cli.py monitor

# Custom interval (check every 1 minute)
python erika_cli.py monitor --interval 60

# JSON output
python erika_cli.py monitor --output json
```

#### `analyze` - Analyze email for fraud
Deep fraud analysis on a specific email.

```bash
# Analyze by email ID
python erika_cli.py analyze EMAIL_ID

# JSON output
python erika_cli.py analyze EMAIL_ID --output json
```

#### `sort` - Sort emails into categories
Categorize emails by risk level and importance.

```bash
# Human-readable format
python erika_cli.py sort

# JSON output
python erika_cli.py sort --output json
```

## 🔧 Configuration

### Email Providers

Erika CLI supports multiple email providers:
- **Gmail** (OAuth2) - Full features, recommended
- **IMAP** (Yahoo, iCloud, custom servers) - Read-only, Alpha

See [EMAIL_PROVIDERS.md](EMAIL_PROVIDERS.md) for detailed provider information.

### Configuration Files

Erika CLI stores configuration in:
- `~/.erika/config.json` - Gateway URL, database URL
- Database (via `app/database_service.py`) - Email provider credentials, security settings

### Environment Variables

- `EGOLLAMA_GATEWAY_URL` - Override gateway URL
- `DATABASE_URL` - Override database connection string

## 🛡️ Security Features

### Phishing Detection
- Reverse image search for profile photo verification
- Identity mismatch detection
- Suspicious pattern analysis

### AresBridge Threat Detection
- Multi-factor risk scoring:
  - **Footprint Risk (40%)**: Domain age and online presence
  - **Domain Mismatch (30%)**: Professional claims vs personal domains
  - **Content Risk (30%)**: Email content analysis

### Auto-Mitigation
- Automatically mark high-threat emails (score >= 0.8) as SPAM/PHISHING
- Configurable via `settings --auto-mitigate`

## 📊 Output Formats

All commands support two output formats:

- `human` (default) - Human-readable text output
- `json` - JSON format for scripting and automation

Example:
```bash
# Human-readable
python erika_cli.py check

# JSON (for scripts)
python erika_cli.py check --output json | jq '.[] | select(.is_phishing)'
```

## 🔄 Workflow Examples

### Complete Setup Workflow

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup gateway connection
python erika_cli.py setup --gateway-url http://egollama.company.com:8082 --test

# 3. Configure Gmail credentials
python erika_cli.py config --client-id YOUR_ID --client-secret YOUR_SECRET --test

# 4. Authenticate with Gmail (opens browser)
python erika_cli.py authenticate

# 5. Check status
python erika_cli.py status

# 6. Start monitoring
python erika_cli.py monitor --interval 300
```

### Fraud Detection Workflow

```bash
# 1. Check for new emails
python erika_cli.py check --max-results 50

# 2. Sort emails by risk
python erika_cli.py sort

# 3. Analyze suspicious email
python erika_cli.py analyze EMAIL_ID

# 4. Monitor continuously for fraud
python erika_cli.py monitor --interval 60
```

## 📝 Requirements

- Python 3.7+
- google-api-python-client
- google-auth-httplib2
- google-auth-oauthlib
- sqlalchemy (for database features)
- requests (for gateway communication)

See `requirements.txt` for complete list.

## 🔐 Security Considerations

1. **Never commit OAuth credentials** to version control
2. **Use environment variables** or secure secret management for credentials
3. **Limit API scopes** to minimum required permissions
4. **Monitor token usage** and revoke if compromised
5. **Review auto-mitigation settings** before enabling

## 📄 License

**Business Source License 1.1** - Copyright (c) 2024 Living Archive team. All Rights Reserved.

This software is licensed under the Business Source License 1.1. You may use this 
software for any purpose, EXCEPT for operating a competing email security, fraud 
detection, or phishing prevention service.

After 4 years from the initial release date, this software will be licensed under 
the MIT License.

**For Erika Pro SaaS** (unlimited features, hosted, supported), see: https://erika.pro

See LICENSE file for full terms and conditions.

## 🤝 Contributing

Contributions are welcome! Please ensure all code includes:
- Input validation
- Error handling
- Security considerations
- Documentation

## 📞 Support

For issues and questions, please open an issue on GitHub.

## 🔗 Related Projects

- **LivingArchive-erika-pro** - Full GUI version with QtPy interface
- **EgoLlama Gateway** - AI-powered email analysis server
