#!/usr/bin/env python3
"""
Image Extractor for Email Analysis
==================================

Extracts images from emails for reverse image search analysis.

Author: EGO Revolution Team
Version: 1.0.0
"""

import logging
import base64
import re
from typing import Dict, List, Optional, Any, Tuple
from email.message import Message
import io
from PIL import Image

logger = logging.getLogger(__name__)


class ImageExtractor:
    """Extracts images from email messages"""
    
    def __init__(self):
        """Initialize image extractor"""
        pass
    
    def extract_images_from_email(self, email_message: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract images from email message
        
        Args:
            email_message: Email message dictionary with Gmail API format
            
        Returns:
            List of image dictionaries with:
                - data: Image bytes
                - mime_type: MIME type
                - filename: Filename (if available)
                - is_embedded: bool (embedded vs attachment)
                - size: Image size in bytes
        """
        images = []
        
        try:
            payload = email_message.get('payload', {})
            
            # Extract from parts
            if 'parts' in payload:
                images.extend(self._extract_from_parts(payload['parts']))
            else:
                # Single part message
                image = self._extract_from_part(payload)
                if image:
                    images.append(image)
            
            # Also check for embedded images in HTML body
            body = email_message.get('body', '') or email_message.get('content', '')
            if body:
                embedded = self._extract_embedded_images(body)
                images.extend(embedded)
            
        except Exception as e:
            logger.error(f"Error extracting images from email: {e}")
        
        return images
    
    def _extract_from_parts(self, parts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract images from message parts recursively"""
        images = []
        
        for part in parts:
            # Check if this part is an image
            image = self._extract_from_part(part)
            if image:
                images.append(image)
            
            # Recursively check nested parts
            if 'parts' in part:
                images.extend(self._extract_from_parts(part['parts']))
        
        return images
    
    def _extract_from_part(self, part: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract image from a single part"""
        mime_type = part.get('mimeType', '').lower()
        
        # Check if it's an image
        if not mime_type.startswith('image/'):
            return None
        
        try:
            body = part.get('body', {})
            data = body.get('data', '')
            
            if not data:
                return None
            
            # Decode base64
            try:
                image_bytes = base64.urlsafe_b64decode(data)
            except Exception as e:
                logger.warning(f"Failed to decode image data: {e}")
                return None
            
            # Validate it's actually an image
            try:
                img = Image.open(io.BytesIO(image_bytes))
                img.verify()  # Verify it's a valid image
            except Exception as e:
                logger.warning(f"Invalid image data: {e}")
                return None
            
            # Get filename
            filename = None
            headers = part.get('headers', [])
            for header in headers:
                if header.get('name', '').lower() == 'content-disposition':
                    disposition = header.get('value', '')
                    # Extract filename from disposition
                    filename_match = re.search(r'filename="?([^"]+)"?', disposition)
                    if filename_match:
                        filename = filename_match.group(1)
            
            return {
                'data': image_bytes,
                'mime_type': mime_type,
                'filename': filename,
                'is_embedded': False,  # This is an attachment
                'size': len(image_bytes),
                'width': img.width if hasattr(img, 'width') else None,
                'height': img.height if hasattr(img, 'height') else None
            }
            
        except Exception as e:
            logger.error(f"Error extracting image from part: {e}")
            return None
    
    def _extract_embedded_images(self, html_body: str) -> List[Dict[str, Any]]:
        """
        Extract embedded images from HTML body (base64 data URIs)
        
        Args:
            html_body: HTML email body
            
        Returns:
            List of image dictionaries
        """
        images = []
        
        try:
            # Find base64 data URIs
            # Pattern: data:image/png;base64,<data>
            pattern = r'data:image/([^;]+);base64,([A-Za-z0-9+/=]+)'
            matches = re.findall(pattern, html_body)
            
            for mime_type, data in matches:
                try:
                    image_bytes = base64.b64decode(data)
                    
                    # Validate
                    img = Image.open(io.BytesIO(image_bytes))
                    img.verify()
                    
                    images.append({
                        'data': image_bytes,
                        'mime_type': f'image/{mime_type}',
                        'filename': None,
                        'is_embedded': True,
                        'size': len(image_bytes),
                        'width': img.width if hasattr(img, 'width') else None,
                        'height': img.height if hasattr(img, 'height') else None
                    })
                except Exception as e:
                    logger.debug(f"Failed to extract embedded image: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error extracting embedded images: {e}")
        
        return images
    
    def find_profile_image(self, images: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Find the most likely profile image from a list of images
        
        Criteria:
        - Square-ish aspect ratio (profile photos are usually square)
        - Reasonable size (not too small, not too large)
        - Not a logo or banner
        
        Args:
            images: List of image dictionaries
            
        Returns:
            Most likely profile image or None
        """
        if not images:
            return None
        
        # Score images
        scored = []
        for img in images:
            score = 0
            
            # Check aspect ratio (prefer square-ish)
            width = img.get('width')
            height = img.get('height')
            if width and height:
                aspect = width / height
                if 0.7 <= aspect <= 1.3:  # Square-ish
                    score += 3
                elif 0.5 <= aspect <= 2.0:  # Portrait/landscape
                    score += 1
            
            # Check size (prefer medium-sized images)
            size = img.get('size', 0)
            if 10000 <= size <= 500000:  # 10KB - 500KB
                score += 2
            elif size < 10000:  # Too small
                score -= 1
            elif size > 2000000:  # Too large (probably not a profile photo)
                score -= 1
            
            # Prefer embedded images (often profile photos in signatures)
            if img.get('is_embedded'):
                score += 1
            
            scored.append((score, img))
        
        # Sort by score and return best match
        scored.sort(reverse=True, key=lambda x: x[0])
        
        if scored and scored[0][0] > 0:
            return scored[0][1]
        
        # Fallback: return first image if no good match
        return images[0] if images else None

