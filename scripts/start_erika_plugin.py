#!/usr/bin/env python3
"""
Start Erika Plugin Service
===========================

Launches Erika as a plugin service that connects to EgoLlama Gateway.
This service:
1. Connects to EgoLlama Gateway
2. Registers Erika plugin
3. Starts background email polling (optional)
4. Keeps connection alive

Usage:
    python scripts/start_erika_plugin.py [--gateway-url URL] [--standalone]

Author: Living Archive team
Version: 1.0.0
"""

import sys
import os
import argparse
import logging
import signal
import threading
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import Erika plugin
from erika.plugin.erika_plugin import ErikaPlugin
from erika.plugin.plugin_client import PluginConnectionError

# Global plugin instance for signal handling
_plugin_instance = None


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"\n🛑 Received signal {signum}, shutting down...")
    if _plugin_instance:
        _plugin_instance.unregister_from_gateway()
    sys.exit(0)


def main():
    """Main entry point"""
    global _plugin_instance
    
    parser = argparse.ArgumentParser(
        description="Start Erika plugin service for EgoLlama Gateway"
    )
    parser.add_argument(
        '--gateway-url',
        type=str,
        default=None,
        help='EgoLlama Gateway URL (default: http://localhost:8082)'
    )
    parser.add_argument(
        '--standalone',
        action='store_true',
        help='Run in standalone mode (for testing, not connected to gateway)'
    )
    parser.add_argument(
        '--keep-alive-interval',
        type=int,
        default=60,
        help='Keep-alive check interval in seconds (default: 60)'
    )
    
    args = parser.parse_args()
    
    # Get gateway URL
    gateway_url = args.gateway_url
    if not gateway_url:
        # Try environment variable
        gateway_url = os.getenv('EGOLLAMA_GATEWAY_URL')
        if not gateway_url:
            # Try config file
            try:
                config_path = Path.home() / ".erika" / "config.json"
                if config_path.exists():
                    import json
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                        gateway_url = config.get('egollama_gateway_url')
            except Exception:
                pass
        
        # Default fallback
        if not gateway_url:
            gateway_url = "http://localhost:8082"
    
    logger.info("🌿 Starting Erika Plugin Service")
    logger.info(f"   Gateway URL: {gateway_url}")
    logger.info(f"   Standalone mode: {args.standalone}")
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Initialize plugin
    plugin = ErikaPlugin(egollama_url=gateway_url)
    _plugin_instance = plugin
    
    if args.standalone:
        # Standalone mode - run FastAPI server directly
        logger.info("🚀 Running in standalone mode (FastAPI server)")
        logger.info("   Access Erika at: http://localhost:8000")
        logger.info("   Press Ctrl+C to stop")
        
        from fastapi import FastAPI
        import uvicorn
        
        app = plugin.create_standalone_app()
        
        try:
            uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
        except KeyboardInterrupt:
            logger.info("🛑 Shutting down standalone server...")
    else:
        # Plugin mode - connect to EgoLlama Gateway
        logger.info("🔌 Connecting to EgoLlama Gateway...")
        
        # Register plugin
        if not plugin.register_with_gateway():
            logger.error("❌ Failed to register plugin with gateway")
            logger.error("   Make sure EgoLlama Gateway is running")
            logger.error("   You can run in standalone mode with --standalone")
            sys.exit(1)
        
        logger.info("✅ Erika plugin registered successfully!")
        logger.info("")
        logger.info("📧 Erika is now available as an agent in EgoLlama Gateway")
        logger.info("   Access Erika endpoints at: {}/api/erika".format(gateway_url))
        logger.info("")
        logger.info("🔄 Starting keep-alive loop...")
        logger.info("   Press Ctrl+C to stop")
        
        # Start keep-alive loop in a separate thread
        keep_alive_thread = threading.Thread(
            target=plugin.client.keep_alive,
            args=(args.keep_alive_interval,),
            daemon=True
        )
        keep_alive_thread.start()
        
        # Keep main thread alive
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n🛑 Shutting down plugin service...")
            plugin.unregister_from_gateway()
            logger.info("✅ Plugin service stopped")


if __name__ == "__main__":
    main()

