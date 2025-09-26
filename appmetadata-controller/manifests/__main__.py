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

from .config import load_config
from . import handlers  # This imports and registers all kopf handlers

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
    
    # Register signal handlers
    def signal_handler(sig, frame):
        logger.info("📥 Shutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start kopf
    kopf.run()