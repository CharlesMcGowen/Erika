# AresBridge Integration

## Overview

AresBridge is a threat detection and mitigation system integrated into Erika's email processing pipeline. It provides multi-factor threat scoring and automatic Gmail API mitigation.

## Features

### Threat Scoring (0.0-1.0)

AresBridge calculates threat scores using three factors:

1. **Footprint Risk (40% weight)**
   - Domain age analysis
   - Online presence/source count
   - New domains (< 90 days, 0 sources) = 40% risk
   - Low footprint (< 3 sources, < 180 days) = 20% risk

2. **Domain Mismatch Risk (30% weight)**
   - Detects professional claims with personal email domains
   - Example: "Recruiter" using @gmail.com instead of company domain
   - Uses keyword detection for professional roles

3. **Content Risk (30% weight)**
   - Uses phishing detection risk score
   - LLM-based content analysis
   - Weighted contribution to final score

### Mitigation Actions

Based on threat score:

- **Score >= 0.8**: `MARK_AS_PHISHING`
  - Adds labels: `SPAM`, `PHISHING_DETECTED_BY_ERIKA`
  - Removes from `INBOX`

- **Score >= 0.5**: `FLAG`
  - Flags for user review
  - No automatic action

- **Score < 0.5**: `NONE`
  - No action taken

## Configuration

### Settings Dialog

Access via: **Settings → Security Settings → AresBridge Threat Detection**

Options:
- **Enable AresBridge Threat Detection**: Master switch
- **Auto-Mitigate High-Threat Emails**: Automatically apply mitigation when score >= 0.8

### Database Configuration

Stored in `ErikaEmailConfig`:
- `enable_ares_bridge` (Boolean, default: False)
- `auto_mitigate_threats` (Boolean, default: False)
- `threat_mitigation_threshold` (Integer, default: 80 = 0.8)

### Email Analysis Storage

Stored in `ErikaEmailAnalysis`:
- `threat_score` (Float, 0.0-1.0)
- `threat_analysis` (JSON): Full breakdown
- `mitigation_applied` (JSON): Mitigation action results

## Integration Flow

```
Email arrives
    ↓
Gmail API fetch
    ↓
Extract email data
    ↓
Phishing detection (if enabled)
    ↓
AresBridge analysis (if enabled)
    ├─> FootprintAnalyzer.get_footprint_data()
    ├─> AresBridge.calculate_threat_score()
    └─> If auto-mitigate enabled and score >= 0.8:
        └─> AresBridge.request_client_mitigation()
            └─> Gmail API: messages().modify()
    ↓
Store results in database
    ↓
Return email data with threat analysis
```

## Security Considerations

### OAuth Token Management

- AresBridge requires `gmail.modify` scope for mitigation
- Tokens are managed securely via `OAuthTokenManager`
- No sensitive data stored in metadata JSON

### Auto-Mitigation Warning

⚠️ **Use auto-mitigation with caution:**
- May mark legitimate emails as spam
- False positives can occur
- Recommended: Start with manual review, enable auto-mitigation after validation

## API Reference

### AresBridge

```python
from erika.services import AresBridge

ares = AresBridge(client_config={})

# Calculate threat score
threat_analysis = ares.calculate_threat_score(
    email_analysis={
        'id': 'email_id',
        'sender': 'sender@example.com',
        'subject': 'Email subject',
        'body': 'Email body'
    },
    footprint_data={
        'domain': 'example.com',
        'source_count': 10,
        'age_days': 730
    },
    content_risk_score=0.5
)

# Apply mitigation
result = ares.request_client_mitigation(
    email_client_id='gmail_message_id',
    mitigation_action='MARK_AS_PHISHING',
    creds=oauth_credentials
)
```

### FootprintAnalyzer

```python
from erika.services import FootprintAnalyzer

analyzer = FootprintAnalyzer()
footprint = analyzer.get_footprint_data('sender@example.com')
# Returns: {'domain': 'example.com', 'source_count': 10, 'age_days': 730, 'reputation': 'established'}
```

## Testing

Test AresBridge integration:

```python
python3 -c "
from erika.services import AresBridge, FootprintAnalyzer
ares = AresBridge()
footprint = FootprintAnalyzer()
print('✅ AresBridge ready')
"
```

## Future Enhancements

- WHOIS API integration for accurate domain age
- Search engine APIs for source count
- Reputation service integration
- Machine learning model for content risk
- Customizable threat thresholds per user

