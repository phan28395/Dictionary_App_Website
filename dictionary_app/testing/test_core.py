#!/usr/bin/env python3
"""
Test script for Dictionary App core functionality.
Tests database initialization, search, and plugin system.
"""

import sys
import logging
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core import DictionaryApp

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def test_core():
    """Test core functionality."""
    logger.info("=" * 50)
    logger.info("Dictionary App Core Test")
    logger.info("=" * 50)
    
    # Initialize app
    logger.info("\n1. Initializing Dictionary App...")
    app = DictionaryApp()
    
    if not app.initialize():
        logger.error("Failed to initialize app")
        return False
    
    logger.info("✓ App initialized successfully")
    
    # Test configuration
    logger.info("\n2. Testing configuration...")
    db_path = app.get_config('database.path')
    logger.info(f"  Database path: {db_path}")
    
    plugin_dir = app.get_config('plugins.directory')
    logger.info(f"  Plugin directory: {plugin_dir}")
    
    # Test database connection
    logger.info("\n3. Testing database...")
    if app.database and app.database.table_exists('dictionary_entries'):
        logger.info("✓ Database connected and schema loaded")
        
        # Count entries
        result = app.database.execute_one(
            "SELECT COUNT(*) FROM dictionary_entries"
        )
        count = result[0] if result else 0
        logger.info(f"  Dictionary entries: {count}")
    else:
        logger.warning("⚠ Database schema not found - run import_dictionary_data.py")
    
    # Test search
    logger.info("\n4. Testing search engine...")
    test_words = ['go', 'run', 'happy', 'quickly', 'went']
    
    for word in test_words:
        results = app.search(word)
        if results:
            result = results[0]
            logger.info(f"  '{word}' → {result.lemma} ({result.pos})")
            if result.inflection_note:
                logger.info(f"    Inflection: {result.inflection_note}")
            if result.meanings:
                logger.info(f"    Meanings: {len(result.meanings)}")
        else:
            logger.info(f"  '{word}' → No results")
    
    # Test suggestions
    logger.info("\n5. Testing autocomplete...")
    suggestions = app.get_suggestions('hap', limit=5)
    if suggestions:
        logger.info(f"  Suggestions for 'hap': {', '.join(suggestions)}")
    else:
        logger.info("  No suggestions found")
    
    # Test plugin system
    logger.info("\n6. Testing plugin system...")
    plugins = app.get_plugins()
    if plugins:
        logger.info(f"  Loaded plugins: {', '.join(plugins.keys())}")
        
        # Check enabled plugins
        enabled = [pid for pid, p in plugins.items() if p.enabled]
        if enabled:
            logger.info(f"  Enabled plugins: {', '.join(enabled)}")
    else:
        logger.info("  No plugins loaded (this is normal - plugins not implemented yet)")
    
    # Test event system
    logger.info("\n7. Testing event system...")
    
    event_received = False
    def test_listener(data):
        nonlocal event_received
        event_received = True
        logger.info(f"  Event received: {data}")
    
    app.events.on('test.event', test_listener)
    app.events.emit('test.event', 'Hello from test!')
    
    if event_received:
        logger.info("✓ Event system working")
    else:
        logger.error("✗ Event system not working")
    
    # Test word of the day
    logger.info("\n8. Testing word of the day...")
    wotd = app.get_word_of_day()
    if wotd:
        logger.info(f"  Word of the day: {wotd.lemma} ({wotd.pos})")
    else:
        logger.info("  No word of the day available")
    
    # Shutdown
    logger.info("\n9. Shutting down...")
    app.shutdown()
    logger.info("✓ Shutdown complete")
    
    logger.info("\n" + "=" * 50)
    logger.info("All core tests completed!")
    logger.info("=" * 50)
    
    return True


if __name__ == '__main__':
    success = test_core()
    sys.exit(0 if success else 1)