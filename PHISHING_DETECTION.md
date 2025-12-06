# Phishing Detection with Reverse Image Search

Erika now includes advanced phishing detection using Google reverse image search to verify profile photos in emails.

## How It Works

### The Problem
Phishing emails often use stolen profile photos. For example:
- Email claims: "Raymond Franklin" is a recruiter
- Reality: Same photo appears on Facebook as "Mr Robert" (real estate agent)
- Reality: Same photo appears on law firm websites
- **Result**: 🚨 PHISHING DETECTED

### The Solution
1. **Extract Images**: Erika extracts all images from incoming emails
2. **Identify Profile Photo**: Finds the most likely profile photo (square, reasonable size)
3. **Google Reverse Search**: Performs Google Lens reverse image search
4. **Identity Verification**: Compares claimed identity with search results
5. **Risk Assessment**: Generates risk score and recommendations

## Detection Patterns

### High Risk (0.7-1.0) 🚨
- Image appears on 3+ unrelated domains
- Identity mismatch (claimed recruiter, but image shows real estate agent)
- Image on Facebook with different name
- Image used by law firms, real estate (common in phishing)

### Medium Risk (0.4-0.6) ⚠️
- Image appears on 2-3 domains
- Some inconsistencies found

### Low Risk (0.0-0.3) ✅
- Image appears consistent with claimed identity
- No suspicious patterns

## Usage

### Basic Usage

```python
from erika.services import PhishingDetector, ImageExtractor

# Initialize
detector = PhishingDetector()
extractor = ImageExtractor()

# Extract images from email (Gmail API message format)
images = extractor.extract_images_from_email(email_message)

# Find profile photo
profile_image = extractor.find_profile_image(images)

# Analyze for phishing
if profile_image:
    analysis = detector.analyze_email(
        email_data={
            'sender': 'Raymond Franklin <raymond@example.com>',
            'subject': 'Exciting Opportunities Await You',
            'body': 'Hi Charles, I hope you\'re doing well...'
        },
        email_message=email_message  # Full Gmail API message
    )
    
    # Get summary
    summary = detector.get_phishing_summary(analysis)
    print(summary)
    
    # Check if phishing
    if analysis['is_phishing']:
        print("🚨 BLOCK THIS EMAIL")
        # Mark as spam, block sender, etc.
```

### Integration with Email Processing

```python
from erika.services import PhishingDetector

detector = PhishingDetector()

# When processing emails from Gmail
for email_message in gmail_messages:
    # Extract email data
    email_data = {
        'sender': get_sender(email_message),
        'subject': get_subject(email_message),
        'body': get_body(email_message)
    }
    
    # Analyze for phishing
    analysis = detector.analyze_email(
        email_data=email_data,
        email_message=email_message
    )
    
    # Handle results
    if analysis['is_phishing']:
        print(f"🚨 PHISHING: {email_data['subject']}")
        print(f"Risk: {analysis['risk_score']:.0%}")
        print(f"Confidence: {analysis['confidence']:.0%}")
        
        # Mark as spam
        mark_as_spam(email_message)
        
        # Block sender
        block_sender(email_data['sender'])
    elif analysis['risk_score'] >= 0.4:
        print(f"⚠️  SUSPICIOUS: {email_data['subject']}")
        print(f"Risk: {analysis['risk_score']:.0%}")
        # Flag for review
```

## Example Output

```
🚨 PHISHING DETECTED
Confidence: 90%
Risk Score: 85%

Indicators:
  🚨 Profile photo appears on multiple unrelated domains
  🚨 Image associated with multiple different roles: recruiter, real_estate, legal
  🚨 Image found on Facebook with potentially different identity

Recommendations:
  🚨 HIGH RISK: Do not respond to this email
  Report as phishing/spam
  Block sender

Image found on 5 domain(s):
  - facebook.com
  - lorenzinjurylaw.com
  - missouri.edu
  - lawyer.com
  - alpinelegalgroup.com

Associated identities found:
  - Mr Robert - real estate - Facebook
  - Lorenz - attorney - Lorenz & Lorenz
  - Zwikelmaier - director - Missouri S&T
```

## Requirements

### Required
- `Pillow>=9.0.0` - Image processing

### Optional (for actual Google search)
- `selenium>=4.0.0` - Browser automation
- `webdriver-manager>=3.8.0` - Chrome driver management
- Chrome browser installed

Install with:
```bash
pip install Pillow selenium webdriver-manager
```

## Implementation Details

### Image Extraction
- Extracts images from email attachments
- Extracts embedded images from HTML body (base64 data URIs)
- Identifies profile photos by aspect ratio and size

### Profile Photo Detection
Criteria:
- Square-ish aspect ratio (0.7-1.3)
- Reasonable size (10KB-500KB)
- Prefers embedded images (often in signatures)

### Google Reverse Search
- Uses Selenium to automate Google Lens
- Extracts search results (titles, domains, snippets)
- Analyzes for suspicious patterns

### Identity Extraction
- Extracts names from search result titles
- Identifies roles (recruiter, real estate, attorney, etc.)
- Extracts company names

### Risk Scoring
- Multiple domains: +0.2 per domain over 3
- Identity mismatch: +0.4
- Facebook mismatch: +0.3
- Suspicious domains: +0.2 per match

## Limitations

1. **Google Search**: Requires Selenium and Chrome
   - May be rate-limited
   - Requires browser automation

2. **Image Quality**: Works best with clear profile photos
   - May miss very small images
   - May have false positives with stock photos

3. **Privacy**: Images uploaded to Google
   - Consider privacy implications
   - Images processed by Google servers

4. **Performance**: Reverse search takes time
   - ~5-10 seconds per image
   - Consider caching results

## Future Enhancements

- [ ] Support for TinEye, Bing reverse image search
- [ ] Caching of search results
- [ ] Batch processing optimization
- [ ] Machine learning for better profile detection
- [ ] Integration with threat intelligence feeds
- [ ] API rate limiting and retry logic

## Security Considerations

- Reverse image search requires internet access
- Images sent to Google servers
- Consider GDPR/privacy regulations
- May want to disable for sensitive emails
- Consider local image hashing for privacy

## Troubleshooting

**"Selenium not available"**:
```bash
pip install selenium webdriver-manager
# Also ensure Chrome browser is installed
```

**"No images found"**:
- Email may not contain images
- Images may be in unsupported format
- Check email HTML for embedded images

**"Search failed"**:
- Google may be blocking automated searches
- Check network connectivity
- Try again later (rate limiting)
- Check Chrome driver is up to date

## Integration with RAG System

The reverse image search results can be fed into Erika's RAG system for context:

```python
# Get phishing analysis
analysis = detector.analyze_email(email_data, email_message)

# Add to RAG context
rag_context = {
    'email': email_data,
    'phishing_analysis': analysis,
    'image_search_results': analysis.get('image_analysis', {}).get('search_results', {})
}

# Query RAG system with context
response = rag_system.query(
    "Is this email legitimate?",
    context=rag_context
)
```

This allows Erika's AI to make more informed decisions about email legitimacy.

