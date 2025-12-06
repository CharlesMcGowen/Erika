#!/usr/bin/env python3
"""
Erika Services Package
=====================

Services for Erika email management system.
"""

from .egollama_gateway import ErikaEgoLlamaGateway, EgoLlamaGatewayError

# Optional imports for reverse image search
try:
    from .reverse_image_search import ReverseImageSearchService, ReverseImageSearchError
    from .image_extractor import ImageExtractor
    from .phishing_detector import PhishingDetector
    _HAS_IMAGE_SEARCH = True
except ImportError:
    _HAS_IMAGE_SEARCH = False
    ReverseImageSearchService = None
    ReverseImageSearchError = None
    ImageExtractor = None
    PhishingDetector = None

# Optional imports for AresBridge
try:
    from .ares_bridge import AresBridge
    from .footprint_analyzer import FootprintAnalyzer
    _HAS_ARES = True
except ImportError:
    _HAS_ARES = False
    AresBridge = None
    FootprintAnalyzer = None

__all__ = [
    'ErikaEgoLlamaGateway',
    'EgoLlamaGatewayError',
]

if _HAS_IMAGE_SEARCH:
    __all__.extend([
        'ReverseImageSearchService',
        'ReverseImageSearchError',
        'ImageExtractor',
        'PhishingDetector',
    ])

if _HAS_ARES:
    __all__.extend([
        'AresBridge',
        'FootprintAnalyzer',
    ])
