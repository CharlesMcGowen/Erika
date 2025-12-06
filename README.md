# EgoLlama Erika - Email Assistant Plugin

Erika is an **AI-powered email assistant plugin** for the EgoLlama Gateway server. It provides secure Gmail OAuth integration, email analysis, and phishing detection.

**Copyright (c) 2024 Living Archive team. All Rights Reserved.**

## 🚀 Quick Start (Plugin Mode)

Erika works as a **plugin** for EgoLlama Gateway. Here's how to get started:

### 1. Install EgoLlama Gateway

First, download and run the [EgoLlama Gateway server](https://github.com/your-org/EgoLlama):

```bash
git clone https://github.com/your-org/EgoLlama.git
cd EgoLlama
pip install -r requirements.txt
python unified_llama_gateway.py
```

### 2. Install Erika Plugin

```bash
git clone https://github.com/your-org/EgoLlama-erika.git
cd EgoLlama-erika
pip install -r requirements.txt
```

### 3. Start Erika Plugin

```bash
python scripts/start_erika_plugin.py
```

Erika will automatically connect to EgoLlama Gateway and register as a plugin. You can then access Erika through the EgoLlama agent interface!

**📖 For detailed installation instructions, see [PLUGIN_INSTALLATION.md](PLUGIN_INSTALLATION.md)**

---

## Features

## Features

- **Gmail OAuth2 Integration**: Secure authentication with Google Gmail API
- **Token Management**: Automatic token refresh and revocation handling
- **Security First**: HTML sanitization, input validation, and secure base64 decoding
- **Framework Agnostic**: Works with any Python web framework
- **Database Support**: Optional SQLAlchemy models for configuration storage

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Get Gmail OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API
4. Create OAuth 2.0 credentials (Desktop app type)
5. Download the credentials JSON file

### 2. Basic Usage

```python
from erika.plugins.email import ErikaGmailService

# Initialize Gmail service
gmail_service = ErikaGmailService(
    user_id="user123",
    config={
        'gmail_client_id': 'your-client-id',
        'gmail_client_secret': 'your-client-secret',
        'gmail_keywords': ['important', 'urgent']
    }
)

# Authenticate (will open browser for first-time OAuth)
gmail_service.authenticate()

# Get unread emails
emails = gmail_service.get_unread_emails(max_results=50, days_back=7)

# Send an email
gmail_service.send_email(
    to="recipient@example.com",
    subject="Hello",
    body="This is a test email"
)
```

### 3. Using with Database

```python
from erika.database import init_db, db_session
from erika.models import ErikaEmailConfig
from erika.api import get_email_config, update_email_config, test_gmail_connection

# Initialize database
init_db()

# Set DATABASE_URL environment variable
# export DATABASE_URL='postgresql://user:password@localhost:5432/erika'

# Get user config
config = get_email_config(user_id="user123")

# Update config
update_email_config(user_id="user123", request_data={
    'gmail_client_id': 'your-client-id',
    'gmail_client_secret': 'your-client-secret',
    'gmail_enabled': True
})

# Test connection
result = test_gmail_connection(user_id="user123")
```

## Security Features

### HTML Sanitization
All HTML email content is automatically sanitized to prevent XSS attacks. The library uses `html_sanitizer` if available, otherwise falls back to HTML escaping.

### Input Validation
- Email addresses are validated using RFC 5322 compliant regex
- Text fields have maximum length limits (subject: 500 chars, body: 100,000 chars)
- Control characters and null bytes are removed
- All inputs are type-checked

### Secure Token Storage
- OAuth tokens are stored in `~/.erika/gmail_token_{user_id}.pickle`
- Token metadata is stored in JSON format for debugging
- Automatic token refresh on expiry
- Token revocation detection and handling

### Base64 Decoding
All base64 decoding operations include error handling to prevent crashes on malformed data.

## EgoLlama Gateway Integration

Erika can connect to an EgoLlama Gateway server for AI-powered email analysis and chat functionality.

### Installation Wizard (Recommended for New Users)

**First time setup is easy!** When you first run Erika, an installation wizard will guide you through connecting to your EgoLlama server:

1. Run `python scripts/run_erika.py`
2. Enter your server address (e.g., `http://egollama.company.com:8082`)
3. Click "Test Connection" to verify
4. Click "Save & Continue"

See [INSTALLATION.md](INSTALLATION.md) for detailed instructions.

### Basic Gateway Usage

```python
from erika.services import ErikaEgoLlamaGateway

# Initialize gateway connection (automatically uses config file or env var)
gateway = ErikaEgoLlamaGateway()  # No URL needed - uses saved config!

# Or specify URL directly
gateway = ErikaEgoLlamaGateway(gateway_url="http://localhost:8082")

# Check if gateway is available
if gateway.is_available():
    # Sync email to gateway
    email_data = {
        'subject': 'Important Meeting',
        'sender': 'colleague@example.com',
        'body': 'Meeting scheduled for tomorrow...'
    }
    result = gateway.sync_email(email_data)
    
    # Analyze email with AI
    analysis = gateway.analyze_email(email_data)
    print(f"Analysis: {analysis['analysis']}")
    
    # Chat with Erika
    response = gateway.chat("What emails need my attention?")
    print(f"Erika: {response['response']}")
```

### Gateway Features

- **Email Syncing**: Sync emails to gateway for processing and training
- **AI Analysis**: Analyze emails using Erika's AI model
- **Chat Interface**: Chat with Erika about your emails
- **Model Training**: Trigger model training with your email data
- **Model Status**: Check status of Erika's model in the gateway

## API Reference

### ErikaGmailService

#### Methods

- `authenticate(client_id=None, client_secret=None) -> bool`
  - Authenticate with Gmail API using OAuth2
  - Returns True on success, raises GmailAuthenticationError on failure

- `get_unread_emails(max_results=50, days_back=7) -> List[Dict]`
  - Get unread emails from the last N days
  - Returns list of email dictionaries with sanitized content

- `send_email(to, subject, body, thread_id=None) -> bool`
  - Send email via Gmail API
  - Validates all inputs before sending

- `create_draft(to, subject, body, thread_id=None) -> bool`
  - Create email draft via Gmail API
  - Validates all inputs before creating

### OAuthTokenManager

#### Methods

- `save_token(creds) -> bool`
  - Save OAuth2 credentials with metadata

- `load_token() -> Optional[Credentials]`
  - Load token with automatic refresh
  - Raises Exception if token is revoked

- `detect_revocation(api_error) -> bool`
  - Detect if API error indicates token revocation

### ErikaEgoLlamaGateway

#### Methods

- `is_available() -> bool`
  - Check if gateway is currently reachable

- `sync_email(email_data) -> Optional[Dict]`
  - Sync email to gateway for processing
  - Returns gateway response or None

- `batch_sync_emails(emails) -> Dict`
  - Batch sync multiple emails
  - Returns summary with success/failure counts

- `analyze_email(email_data, model="erika-email-classifier") -> Optional[Dict]`
  - Analyze email using AI model
  - Returns analysis results

- `chat(message, conversation_history=None) -> Optional[Dict]`
  - Chat with Erika via gateway
  - Returns chat response

- `get_model_status() -> Optional[Dict]`
  - Get status of Erika's model in gateway

- `train_model(training_config=None) -> Optional[Dict]`
  - Trigger model training in gateway

## Configuration

### Environment Variables

- `DATABASE_URL`: PostgreSQL connection string (optional, for database features)
- `ERIKA_DATABASE_URL`: Alternative database URL variable

### Token Storage

OAuth tokens are stored in:
- `~/.erika/gmail_token_{user_id}.pickle` - Token file (Google library format)
- `~/.erika/gmail_token_{user_id}_metadata.json` - Token metadata

## Requirements

- Python 3.7+
- google-api-python-client
- google-auth-httplib2
- google-auth-oauthlib
- sqlalchemy (for database features)
- psycopg2-binary (for PostgreSQL, if using database)
- html-sanitizer (optional, for advanced HTML sanitization)

## Security Considerations

1. **Never commit OAuth credentials** to version control
2. **Encrypt client_secret** in production (not implemented in this library)
3. **Use environment variables** or secure secret management for credentials
4. **Limit API scopes** to minimum required permissions
5. **Monitor token usage** and revoke if compromised

## License

**Commercial License** - Copyright (c) 2024 Living Archive team. All Rights Reserved.

This software is licensed for personal, non-commercial use only. Commercial use, 
redistribution, or integration into commercial products requires a commercial license 
from Living Archive team.

See LICENSE file for full terms and conditions.

## Contributing

Contributions are welcome! Please ensure all code includes:
- Input validation
- Error handling
- Security considerations
- Documentation

## Support

For issues and questions, please open an issue on GitHub.

