"""
Main application class for Dictionary App.
Coordinates all core components and provides plugin API.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import Config, get_config
from .database import Database
from .search import SearchEngine, SearchResult
from .plugin import PluginLoader
from .events import EventEmitter, CoreEvents

logger = logging.getLogger(__name__)


class DictionaryApp:
    """
    Main application class that coordinates all components.
    This is the headless core - NO UI code here.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the Dictionary App.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.version = "1.0.0"
        self.running = False
        
        # Initialize configuration
        self.config = get_config(config_path)
        
        # Set up logging
        self._setup_logging()
        
        logger.info(f"Initializing Dictionary App v{self.version}")
        
        # Initialize core components
        self.events = EventEmitter(debug_mode=self.config.get('logging.debug', False))
        self.database = None
        self.search_engine = None
        self.plugin_loader = None
        
        # Plugin API storage
        self._plugin_storage = {}
        
    def _setup_logging(self):
        """Configure logging based on configuration."""
        log_level = self.config.get('logging.level', 'INFO')
        log_file = self.config.get_path('logging.file')
        
        # Create logs directory if needed
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(log_file) if log_file else logging.NullHandler()
            ]
        )
    
    def initialize(self) -> bool:
        """
        Initialize all components.
        
        Returns:
            True if successful
        """
        try:
            # Initialize database
            logger.info("Initializing database...")
            self.database = Database(self.config.to_dict())
            self.events.emit(CoreEvents.DATABASE_CONNECTED)
            
            # Initialize search engine
            logger.info("Initializing search engine...")
            self.search_engine = SearchEngine(self.database, self.config.to_dict())
            
            # Initialize plugin loader
            logger.info("Initializing plugin system...")
            self.plugin_loader = PluginLoader(self, self.config.to_dict())
            
            # Load all plugins
            self.plugin_loader.load_all_plugins()
            
            # Enable plugins that should be enabled
            self._enable_default_plugins()
            
            # Emit ready event
            self.events.emit(CoreEvents.APP_READY)
            
            self.running = True
            logger.info("Dictionary App initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Dictionary App: {e}")
            return False
    
    def _enable_default_plugins(self):
        """Enable plugins that should be enabled by default."""
        # Get list of plugins to enable
        enabled_by_default = [
            'core-ui',
            'settings', 
            'auth',
            'licensing',
            'favorites',
            'history',
            'extension-store'
        ]
        
        for plugin_id in enabled_by_default:
            if self.plugin_loader.get_plugin(plugin_id):
                self.plugin_loader.enable_plugin(plugin_id)
    
    def shutdown(self):
        """Shutdown the application and all components."""
        if not self.running:
            return
        
        logger.info("Shutting down Dictionary App...")
        
        # Emit shutdown event
        self.events.emit(CoreEvents.APP_SHUTDOWN)
        
        # Shutdown plugins
        if self.plugin_loader:
            self.plugin_loader.shutdown()
        
        # Close database
        if self.database:
            self.database.close()
            self.events.emit(CoreEvents.DATABASE_DISCONNECTED)
        
        self.running = False
        logger.info("Dictionary App shutdown complete")
    
    # === Plugin API Methods ===
    # These methods are exposed to plugins via the app object
    
    def search(self, term: str) -> List[SearchResult]:
        """
        Perform a dictionary search.
        
        Args:
            term: Search term
            
        Returns:
            List of search results
        """
        if not self.search_engine:
            logger.error("Search engine not initialized")
            return []
        
        # Emit before event and check if cancelled
        event_data = {'term': term, 'cancelled': False}
        self.events.emit(CoreEvents.SEARCH_BEFORE, event_data)
        
        # Check if search was cancelled by a plugin
        if event_data.get('cancelled', False):
            logger.info(f"Search for '{term}' was cancelled by plugin: {event_data.get('reason', 'unknown')}")
            return []
        
        try:
            # Perform search
            results = self.search_engine.search(term)
            
            # Emit complete event
            self.events.emit(CoreEvents.SEARCH_COMPLETE, term, results)
            
            return results
            
        except Exception as e:
            logger.error(f"Search error for '{term}': {e}")
            self.events.emit(CoreEvents.SEARCH_ERROR, term, str(e))
            return []
    
    def get_suggestions(self, prefix: str, limit: int = 10) -> List[str]:
        """
        Get autocomplete suggestions.
        
        Args:
            prefix: Search prefix
            limit: Maximum suggestions
            
        Returns:
            List of suggestions
        """
        if not self.search_engine:
            return []
        
        return self.search_engine.get_suggestions(prefix, limit)
    
    def get_random_word(self, pos: Optional[str] = None) -> Optional[SearchResult]:
        """
        Get a random word.
        
        Args:
            pos: Optional part of speech filter
            
        Returns:
            Random word or None
        """
        if not self.search_engine:
            return None
        
        return self.search_engine.get_random_word(pos)
    
    def get_word_of_day(self) -> Optional[SearchResult]:
        """
        Get word of the day.
        
        Returns:
            Word of the day or None
        """
        if not self.search_engine:
            return None
        
        return self.search_engine.get_word_of_day()
    
    def get_config(self, path: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            path: Dot-separated path
            default: Default value
            
        Returns:
            Configuration value
        """
        return self.config.get(path, default)
    
    def set_config(self, path: str, value: Any):
        """
        Set configuration value (runtime only).
        
        Args:
            path: Dot-separated path
            value: Value to set
        """
        old_value = self.config.get(path)
        self.config.set(path, value)
        
        # Emit event
        self.events.emit(CoreEvents.CONFIG_CHANGED, path, old_value, value)
    
    def save_config(self):
        """Save configuration to file."""
        self.config.save_user_config()
        self.events.emit(CoreEvents.CONFIG_SAVED)
    
    def get_plugin(self, plugin_id: str) -> Optional[Any]:
        """
        Get plugin instance by ID.
        
        Args:
            plugin_id: Plugin ID
            
        Returns:
            Plugin instance or None
        """
        if not self.plugin_loader:
            return None
        
        return self.plugin_loader.get_plugin(plugin_id)
    
    def get_plugins(self) -> Dict[str, Any]:
        """
        Get all loaded plugins.
        
        Returns:
            Dictionary of plugin ID to instance
        """
        if not self.plugin_loader:
            return {}
        
        return self.plugin_loader.plugins.copy()
    
    def enable_plugin(self, plugin_id: str) -> bool:
        """
        Enable a plugin.
        
        Args:
            plugin_id: Plugin ID
            
        Returns:
            True if successful
        """
        if not self.plugin_loader:
            return False
        
        success = self.plugin_loader.enable_plugin(plugin_id)
        if success:
            self.events.emit(CoreEvents.PLUGIN_ENABLED, plugin_id)
        
        return success
    
    def disable_plugin(self, plugin_id: str) -> bool:
        """
        Disable a plugin.
        
        Args:
            plugin_id: Plugin ID
            
        Returns:
            True if successful
        """
        if not self.plugin_loader:
            return False
        
        success = self.plugin_loader.disable_plugin(plugin_id)
        if success:
            self.events.emit(CoreEvents.PLUGIN_DISABLED, plugin_id)
        
        return success
    
    def reload_plugin(self, plugin_id: str) -> bool:
        """
        Reload a plugin.
        
        Args:
            plugin_id: Plugin ID
            
        Returns:
            True if successful
        """
        if not self.plugin_loader:
            return False
        
        return self.plugin_loader.reload_plugin(plugin_id)
    
    def get_plugin_storage(self, plugin_id: str) -> Dict[str, Any]:
        """
        Get plugin-specific storage dictionary.
        
        Args:
            plugin_id: Plugin ID
            
        Returns:
            Storage dictionary for plugin
        """
        if plugin_id not in self._plugin_storage:
            self._plugin_storage[plugin_id] = {}
        
        return self._plugin_storage[plugin_id]
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[tuple]:
        """
        Execute a database query (read-only).
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            Query results
        """
        if not self.database:
            return []
        
        # Only allow SELECT queries for plugins
        if not query.strip().upper().startswith('SELECT'):
            raise ValueError("Only SELECT queries are allowed")
        
        return self.database.execute(query, params)


def main():
    """Main entry point for the application."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Dictionary App')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()
    
    # Create app instance
    app = DictionaryApp(config_path=Path(args.config) if args.config else None)
    
    # Enable debug if requested
    if args.debug:
        app.config.set('logging.level', 'DEBUG')
        app.config.set('logging.debug', True)
    
    # Initialize app
    if not app.initialize():
        sys.exit(1)
    
    try:
        # Keep app running (plugins handle the actual work)
        import time
        logger.info("Dictionary App is running. Press Ctrl+C to stop.")
        while app.running:
            time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    
    finally:
        app.shutdown()


if __name__ == '__main__':
    main()