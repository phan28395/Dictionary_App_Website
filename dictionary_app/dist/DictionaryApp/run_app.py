#!/usr/bin/env python3
"""
Run Dictionary App with UI plugin
"""

import sys
import logging
import time
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core import DictionaryApp

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    logger.info("Starting Dictionary App with UI...")
    
    # Create app instance
    app = DictionaryApp()
    
    # Initialize app
    if not app.initialize():
        logger.error("Failed to initialize app")
        sys.exit(1)
    
    logger.info("Dictionary App initialized")
    
    # The app is now running with plugins
    # Check if core-ui plugin loaded
    ui_plugin = app.get_plugin('core-ui')
    if ui_plugin:
        logger.info("Core UI plugin loaded successfully")
        if ui_plugin.enabled:
            logger.info("Core UI plugin is enabled")
        else:
            logger.info("Core UI plugin is not enabled")
    else:
        logger.warning("Core UI plugin not found")
    
    try:
        logger.info("Dictionary App is running. Press Ctrl+C to stop.")
        logger.info("Double-tap Ctrl to open search (if UI plugin is active)")
        
        # Keep app running
        while app.running:
            time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    
    finally:
        app.shutdown()
        logger.info("Application shutdown complete")


if __name__ == '__main__':
    main()