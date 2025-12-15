# Supported Email Providers

Erika CLI supports multiple email providers for monitoring and fraud detection.

## Currently Supported Providers

### 1. Gmail (OAuth2) ✅
**Status**: Fully implemented and tested

**Authentication**: OAuth2 via Google Cloud Console

**Setup**:
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create OAuth2 credentials (Desktop app type)
3. Configure in Erika: `python erika_cli.py config --provider gmail`

**Features**:
- Read emails
- Send emails
- Create drafts
- Label management
- Full Gmail API access

**Use Cases**:
- Personal Gmail accounts
- Google Workspace accounts
- Any Gmail-based email

---

### 2. IMAP (Generic Email Servers) ✅
**Status**: Implemented (Alpha)

**Authentication**: Username/password or app password

**Supported Providers**:
- **Yahoo Mail**: `imap.mail.yahoo.com:993`
- **iCloud Mail**: `imap.mail.me.com:993`
- **AOL Mail**: `imap.aol.com:993`
- **Custom IMAP servers**: Any IMAP-compatible server

**Setup**:
```bash
# Yahoo Mail
python erika_cli.py config --provider imap \
  --imap-server imap.mail.yahoo.com \
  --imap-username your@yahoo.com \
  --imap-password YOUR_APP_PASSWORD

# iCloud Mail
python erika_cli.py config --provider imap \
  --imap-server imap.mail.me.com \
  --imap-username your@icloud.com \
  --imap-password YOUR_APP_PASSWORD

# Custom Server
python erika_cli.py config --provider imap \
  --imap-server mail.example.com \
  --imap-username user@example.com \
  --imap-password PASSWORD
```

**Features**:
- Read emails (unread detection)
- Email body extraction
- Header parsing
- Multi-part message handling

**Limitations**:
- Read-only (sending requires SMTP, not yet implemented)
- No thread ID support
- Basic email parsing

**Use Cases**:
- Yahoo Mail accounts
- iCloud Mail accounts
- Corporate IMAP servers
- Custom email infrastructure

---

## Planned Providers (Pro Version)

### 3. Microsoft 365 / Outlook (Planned)
**Status**: Not yet implemented

**Authentication**: OAuth2 via Azure AD

**Features** (Planned):
- Microsoft Graph API integration
- Office 365 email access
- Outlook.com email access
- Enterprise email support

---

### 4. Exchange / EWS (Planned)
**Status**: Not yet implemented

**Authentication**: OAuth2 or Basic Auth

**Features** (Planned):
- Exchange Web Services (EWS)
- On-premises Exchange support
- Enterprise email infrastructure

---

## Provider Comparison

| Provider | Auth Method | Read | Send | Status | Free Tier |
|----------|------------|------|------|--------|-----------|
| Gmail | OAuth2 | ✅ | ✅ | Production | ✅ |
| IMAP | Password | ✅ | ❌ | Alpha | ✅ |
| Office365 | OAuth2 | ❌ | ❌ | Planned | Pro |
| Exchange | OAuth2/Basic | ❌ | ❌ | Planned | Pro |

## Choosing a Provider

### For Personal Use
- **Gmail**: Best choice, full features, OAuth2 security
- **Yahoo/iCloud**: Use IMAP if you don't have Gmail

### For Business Use
- **Gmail/Google Workspace**: Recommended for free tier
- **Office365**: Coming in Pro version
- **Exchange**: Coming in Pro version (on-premises)

### For Custom Infrastructure
- **IMAP**: Works with any IMAP-compatible server
- **Custom SMTP**: Coming soon for sending

## Configuration Examples

### Gmail Setup
```bash
python erika_cli.py config --provider gmail \
  --client-id YOUR_CLIENT_ID \
  --client-secret YOUR_SECRET \
  --test
```

### Yahoo Mail Setup
```bash
python erika_cli.py config --provider imap \
  --imap-server imap.mail.yahoo.com \
  --imap-username your@yahoo.com \
  --imap-password YOUR_APP_PASSWORD \
  --test
```

### iCloud Mail Setup
```bash
python erika_cli.py config --provider imap \
  --imap-server imap.mail.me.com \
  --imap-username your@icloud.com \
  --imap-password YOUR_APP_PASSWORD \
  --test
```

## Security Notes

- **Gmail**: Uses OAuth2 (most secure, no password storage)
- **IMAP**: Requires password/app password (stored securely in database)
- **App Passwords**: Recommended for IMAP (more secure than regular passwords)

## Getting App Passwords

### Yahoo Mail
1. Go to Account Security
2. Generate App Password
3. Use app password instead of regular password

### iCloud Mail
1. Go to Apple ID account
2. Sign-In and Security > App-Specific Passwords
3. Generate password for "Mail"

## Feedback Welcome

We're actively developing support for additional email providers. If you need support for a specific provider, please open an issue on GitHub!
