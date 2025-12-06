# Phishing Detection Controls

## User Control

**Erika's reverse image search phishing detection is AUTOMATIC but USER-CONTROLLED.**

### Default Behavior

- ✅ **Enabled by default** - Phishing detection runs automatically on all emails
- ✅ **Non-blocking** - If detection fails, email processing continues
- ✅ **User can disable** - Can be turned off in Settings

### How to Control

#### Enable/Disable Phishing Detection

1. **Open Settings**:
   - Menu: Settings → Server Settings
   - Or: Settings → Security Settings (new tab)

2. **Security Tab**:
   - ☑️ **Enable Phishing Detection** - Master switch for phishing detection
   - ☑️ **Enable Reverse Image Search** - Enable/disable Google reverse search

3. **Save Settings**:
   - Click "💾 Save"
   - Settings are saved to database

### Settings Explained

#### "Enable Phishing Detection"
- **ON**: Erika automatically checks all emails for phishing
- **OFF**: Phishing detection is completely disabled
- **Default**: ON

#### "Enable Reverse Image Search"
- **ON**: Uses Google reverse image search to verify profile photos
- **OFF**: Phishing detection runs but without image verification
- **Default**: ON
- **Requires**: Selenium, Chrome browser, internet connection

### When Detection Runs

Phishing detection runs automatically when:
1. ✅ Emails are fetched from Gmail
2. ✅ Email processing happens
3. ✅ Phishing detection is enabled in settings

### What Happens

1. **Email arrives** → Erika processes it
2. **If phishing detection enabled** → Extracts images
3. **If images found** → Finds profile photo
4. **If reverse search enabled** → Performs Google search
5. **Results analyzed** → Risk score calculated
6. **Email tagged** → `is_phishing` and `phishing_risk_score` added to email data

### Email Data Structure

After processing, emails include:
```python
{
    'id': '...',
    'subject': '...',
    'sender': '...',
    'body': '...',
    # Phishing detection results (if enabled)
    'is_phishing': False,  # True if risk_score >= 0.7
    'phishing_risk_score': 0.85,  # 0.0-1.0
    'phishing_analysis': {
        'is_phishing': True,
        'risk_score': 0.85,
        'confidence': 0.9,
        'indicators': [...],
        'recommendations': [...]
    }
}
```

### Performance Considerations

- **Time**: Reverse image search takes ~5-10 seconds per email
- **Rate Limiting**: Google may rate-limit automated searches
- **Privacy**: Images are uploaded to Google servers
- **Non-blocking**: Detection failures don't stop email processing

### Recommended Settings

**For Most Users**:
- ✅ Enable Phishing Detection: ON
- ✅ Enable Reverse Image Search: ON

**For Privacy-Conscious Users**:
- ✅ Enable Phishing Detection: ON
- ❌ Enable Reverse Image Search: OFF (no images sent to Google)

**For Performance**:
- ❌ Enable Phishing Detection: OFF (skip all checks)

### Disabling Detection

To completely disable:
1. Settings → Security Settings
2. Uncheck "Enable Phishing Detection"
3. Save

Emails will still be processed normally, just without phishing checks.

### Re-enabling

To re-enable:
1. Settings → Security Settings
2. Check "Enable Phishing Detection"
3. Check "Enable Reverse Image Search" (if desired)
4. Save

Detection will resume on new emails.

## Technical Details

### Configuration Storage

Settings are stored in:
- Database: `erika_email_config` table
- Fields: `phishing_detection_enabled`, `reverse_image_search_enabled`
- Default: Both `True`

### Integration Points

1. **Email Processing**: `gmail_service.py` → `_get_email_details()` → `_check_phishing()`
2. **Settings UI**: `settings_dialog.py` → Security tab
3. **Database**: `models.py` → `ErikaEmailConfig` model

### Error Handling

- Detection errors are logged but don't fail email processing
- Missing dependencies (Selenium) are handled gracefully
- Network errors don't block email fetching

