#!/usr/bin/env python3
"""
Test GUI functionality
"""

import sys
import time
import logging
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
    """Test GUI functionality."""
    logger.info("Starting Dictionary App with full GUI...")
    
    # Create app instance
    app = DictionaryApp()
    
    # Initialize app
    if not app.initialize():
        logger.error("Failed to initialize app")
        sys.exit(1)
    
    # Check if UI plugin loaded
    ui_plugin = app.get_plugin('core-ui')
    if ui_plugin and ui_plugin.enabled:
        logger.info("UI plugin loaded and enabled")
        
        # Test showing the search window
        logger.info("Testing search window...")
        ui_plugin.show_search_window("test")
        
        # Give time for window to appear
        time.sleep(2)
        
        logger.info("GUI test - check if window appeared")
        logger.info("You can test:")
        logger.info("  - System tray icon")
        logger.info("  - Double-tap Ctrl for hotkey")
        logger.info("  - Search window functionality")
    else:
        logger.error("UI plugin not found or not enabled")
    
    try:
        logger.info("App running. Press Ctrl+C to stop.")
        while app.running:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        app.shutdown()


if __name__ == '__main__':
    main()