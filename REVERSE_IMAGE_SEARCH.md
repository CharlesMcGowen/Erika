# Reverse Image Search for Phishing Detection

Erika now includes reverse image search capability to detect phishing emails by verifying profile photos.

## How It Works

1. **Extract Images**: Erika extracts images from incoming emails
2. **Find Profile Photo**: Identifies the most likely profile photo (square aspect ratio, reasonable size)
3. **Google Reverse Search**: Performs Google Lens reverse image search
4. **Identity Verification**: Compares claimed identity with search results
5. **Risk Assessment**: Generates risk score based on mismatches

## Example Detection

**Email Claims:**
- Sender: "Raymond Franklin"
- Role: Recruiter/Headhunter
- Company: Career Services

**Google Search Results:**
- Image found on Facebook as "Mr Robert" (Real Estate Agent)
- Image found on law firm websites
- Image found on multiple unrelated domains

**Result:** 🚨 HIGH RISK - Profile photo doesn't match claimed identity

## Usage

### Basic Usage

```python
from erika.services import PhishingDetector, ImageExtractor

# Initialize
detector = PhishingDetector()
extractor = ImageExtractor()

# Extract images from email
images = extractor.extract_images_from_email(email_message)

# Find profile photo
profile_image = extractor.find_profile_image(images)

# Analyze for phishing
if profile_image:
    analysis = detector.analyze_email(
        email_data={
            'sender': 'Raymond Franklin <raymond@example.com>',
            'subject': 'Exciting Opportunities',
            'body': '...'
        },
        email_message=email_message  # Full Gmail API message
    )
    
    print(detector.get_phishing_summary(analysis))
```

### Integration with Email Processing

```python
from erika.services import PhishingDetector

detector = PhishingDetector()

# When processing emails
for email in emails:
    analysis = detector.analyze_email(
        email_data=email,
        email_message=full_gmail_message
    )
    
    if analysis['is_phishing']:
        print(f"🚨 PHISHING DETECTED: {email['subject']}")
        print(f"Risk Score: {analysis['risk_score']:.0%}")
        # Mark as spam, block sender, etc.
```

## Detection Patterns

### High Risk Indicators

1. **Multiple Domains**: Image appears on 3+ unrelated domains
2. **Identity Mismatch**: Claimed role doesn't match image usage
   - Example: Claims recruiter, but image shows real estate agent
3. **Facebook Mismatch**: Image on Facebook with different name
4. **Suspicious Domains**: Image on law firms, real estate sites (common in phishing)

### Risk Scoring

- **0.0-0.3**: Low Risk ✅
- **0.4-0.6**: Medium Risk ⚠️
- **0.7-1.0**: High Risk 🚨 (Likely Phishing)

## Requirements

### Required
- `Pillow` - Image processing
- `requests` - HTTP requests

### Optional (for actual Google search)
- `selenium` - Browser automation
- `webdriver-manager` - Chrome driver management

Install with:
```bash
pip install Pillow selenium webdriver-manager
```

## Limitations

1. **Google Search**: Requires Selenium and Chrome driver
   - May be rate-limited by Google
   - Requires browser automation

2. **Image Quality**: Works best with clear profile photos
   - May miss very small or low-quality images
   - May have false positives with stock photos

3. **Privacy**: Uploads images to Google for search
   - Consider privacy implications
   - Images are processed by Google's servers

## Future Enhancements

- [ ] Support for other reverse image search engines (TinEye, Bing)
- [ ] Caching of search results
- [ ] Batch processing for multiple emails
- [ ] Integration with threat intelligence feeds
- [ ] Machine learning for better profile photo detection

## Security Considerations

- Reverse image search requires internet access
- Images are sent to Google's servers
- Consider data privacy regulations (GDPR, etc.)
- May want to disable for sensitive emails

## Troubleshooting

**"Selenium not available"**:
- Install: `pip install selenium webdriver-manager`
- Ensure Chrome browser is installed

**"No images found"**:
- Email may not contain images
- Images may be in unsupported format
- Check email HTML for embedded images

**"Search failed"**:
- Google may be blocking automated searches
- Check network connectivity
- Try again later (rate limiting)

