"""
Main entry point for ApplicationMetadata controller.
"""
import asyncio
import logging
import os
import signal
import sys

import kopf
from prometheus_client import start_http_server

from controller.config import load_config
from controller import handlers  # This imports and registers all kopf handlers

# Initialize logging
logger = logging.getLogger(__name__)

def main():
    """Main entry point."""
    # Load configuration
    config = load_config()
    
    # Configure logging
    log_level = getattr(logging, config.logging.level.upper())
    logging.basicConfig(
        level=log_level,
        format=config.logging.format
    )
    
    # Start metrics server if enabled
    if config.metrics.enabled:
        try:
            start_http_server(config.metrics.port)
            logger.info(f"📊 Started metrics server on port {config.metrics.port}")
        except Exception as e:
            logger.error(f"❌ Failed to start metrics server: {e}")
            sys.exit(1)
    
    # Log startup
    logger.info("🚀 Starting ApplicationMetadata Controller")
    logger.info(f"⚙️  Configuration loaded: {config.dict()}")
    
    # Configure file logging for readiness checks
    file_handler = logging.FileHandler('/tmp/controller.log')
    file_handler.setFormatter(logging.Formatter(config.logging.format))
    logging.getLogger().addHandler(file_handler)
    
    # Register signal handlers
    def signal_handler(sig, frame):
        logger.info("📥 Shutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start kopf
    # Run Kopf operator (no 'peering' arg for this Kopf version)
    ns = os.getenv("KOPF_NAMESPACE")
    if ns:
        kopf.run(standalone=True, namespace=ns)
    else:
        # Watch cluster-wide
        kopf.run(standalone=True)

if __name__ == "__main__":
    main()
