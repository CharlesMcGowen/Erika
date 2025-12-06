# Erika Services

Services for Erika's email management and security features.

## Available Services

### 1. EgoLlama Gateway Integration
- **File**: `egollama_gateway.py`
- **Class**: `ErikaEgoLlamaGateway`
- **Purpose**: Connect to EgoLlama Gateway for AI-powered email analysis

### 2. Reverse Image Search
- **File**: `reverse_image_search.py`
- **Class**: `ReverseImageSearchService`
- **Purpose**: Perform Google reverse image search to verify profile photos

### 3. Image Extractor
- **File**: `image_extractor.py`
- **Class**: `ImageExtractor`
- **Purpose**: Extract images from email messages

### 4. Phishing Detector
- **File**: `phishing_detector.py`
- **Class**: `PhishingDetector`
- **Purpose**: Detect phishing emails using reverse image search

### 5. Google Lens Search (Implementation)
- **File**: `google_lens_search.py`
- **Class**: `GoogleLensSearch`
- **Purpose**: Actual Selenium-based Google Lens search implementation

## Usage Example

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
        email_message=email_message
    )
    
    if analysis['is_phishing']:
        print("🚨 PHISHING DETECTED!")
        print(f"Risk Score: {analysis['risk_score']:.0%}")
```

## Requirements

- `Pillow` - Image processing (required)
- `selenium` - Browser automation (optional, for Google search)
- `webdriver-manager` - Chrome driver (optional, for Google search)

