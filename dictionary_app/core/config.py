"""
Configuration management system for Dictionary App.
Loads configuration from multiple sources with priority ordering.
"""

import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class Config:
    """
    Configuration manager that loads settings from multiple sources:
    1. Environment variables (highest priority)
    2. .env file
    3. config.json file
    4. default_config.json (lowest priority)
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            base_path: Base directory for the application (defaults to parent of core/)
        """
        if base_path is None:
            # Get the dictionary_app directory (parent of core/)
            base_path = Path(__file__).parent.parent
        
        self.base_path = Path(base_path)
        self.config_dir = self.base_path / "config"
        self.data = {}
        
        # Load configuration in priority order
        self._load_config()
    
    def _load_config(self):
        """Load configuration from all sources in priority order."""
        # 1. Load default configuration
        default_config_path = self.config_dir / "default_config.json"
        if default_config_path.exists():
            with open(default_config_path, 'r') as f:
                self.data = json.load(f)
                logger.info(f"Loaded default config from {default_config_path}")
        
        # 2. Load user configuration (if exists)
        user_config_path = self.config_dir / "config.json"
        if user_config_path.exists():
            with open(user_config_path, 'r') as f:
                user_config = json.load(f)
                self._deep_merge(self.data, user_config)
                logger.info(f"Loaded user config from {user_config_path}")
        
        # 3. Load .env file (if exists)
        env_path = self.base_path / ".env"
        if env_path.exists():
            load_dotenv(env_path)
            logger.info(f"Loaded environment variables from {env_path}")
        
        # 4. Override with environment variables
        self._apply_env_overrides()
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]):
        """
        Deep merge override dictionary into base dictionary.
        
        Args:
            base: Base dictionary to merge into
            override: Dictionary with values to override
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides to configuration."""
        # Map of environment variables to config paths
        env_mappings = {
            'DATABASE_PATH': 'database.path',
            'DATABASE_ENCRYPTION_ENABLED': 'database.encryption.enabled',
            'DATABASE_KEY_DERIVATION_ROUNDS': 'database.encryption.key_derivation_rounds',
            'PLUGIN_DIRECTORY': 'plugins.directory',
            'PLUGIN_DEV_DIRECTORY': 'plugins.dev_directory',
            'PLUGIN_HOT_RELOAD': 'plugins.hot_reload',
            'PLUGIN_SAFE_MODE': 'plugins.safe_mode',
            'DEBUG_MODE': 'logging.debug',
            'LOG_LEVEL': 'logging.level',
            'LOG_FILE': 'logging.file',
            'CACHE_SIZE_MB': 'search.cache.size_mb',
            'SEARCH_CACHE_TTL': 'search.cache.ttl_seconds',
            'MAX_PLUGIN_MEMORY_MB': 'performance.plugin_memory_limit_mb',
            'EXTENSION_REGISTRY_URL': 'marketplace.registry_url',
            'LICENSE_VALIDATION_URL': 'licensing.validation_url',
        }
        
        for env_var, config_path in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                self._set_nested_value(config_path, self._parse_value(env_value))
                logger.debug(f"Applied env override: {env_var} -> {config_path}")
    
    def _parse_value(self, value: str) -> Any:
        """
        Parse string value to appropriate type.
        
        Args:
            value: String value to parse
            
        Returns:
            Parsed value with appropriate type
        """
        # Boolean values
        if value.lower() in ('true', 'yes', '1'):
            return True
        elif value.lower() in ('false', 'no', '0'):
            return False
        
        # Numeric values
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # String value
        return value
    
    def _set_nested_value(self, path: str, value: Any):
        """
        Set a nested value in the configuration using dot notation.
        
        Args:
            path: Dot-separated path (e.g., 'database.encryption.enabled')
            value: Value to set
        """
        keys = path.split('.')
        target = self.data
        
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        
        target[keys[-1]] = value
    
    def get(self, path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-separated path.
        
        Args:
            path: Dot-separated path (e.g., 'database.encryption.enabled')
            default: Default value if path not found
            
        Returns:
            Configuration value or default
        """
        keys = path.split('.')
        value = self.data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def get_path(self, path_key: str) -> Path:
        """
        Get a path configuration value as a Path object.
        
        Args:
            path_key: Configuration key for the path
            
        Returns:
            Path object (absolute)
        """
        path_str = self.get(path_key)
        if path_str is None:
            return None
        
        path = Path(path_str)
        if not path.is_absolute():
            # Make relative paths relative to base_path
            path = self.base_path / path
        
        return path.resolve()
    
    def set(self, path: str, value: Any):
        """
        Set configuration value (runtime only, not persisted).
        
        Args:
            path: Dot-separated path
            value: Value to set
        """
        self._set_nested_value(path, value)
    
    def save_user_config(self, path: Optional[Path] = None):
        """
        Save current configuration to user config file.
        
        Args:
            path: Optional path to save to (defaults to config/config.json)
        """
        if path is None:
            path = self.config_dir / "config.json"
        
        # Create config directory if it doesn't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump(self.data, f, indent=2)
        
        logger.info(f"Saved configuration to {path}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Get full configuration as dictionary.
        
        Returns:
            Complete configuration dictionary
        """
        return self.data.copy()


# Global configuration instance
_config_instance = None


def get_config(base_path: Optional[Path] = None) -> Config:
    """
    Get global configuration instance.
    
    Args:
        base_path: Base directory for the application
        
    Returns:
        Global Config instance
    """
    global _config_instance
    
    if _config_instance is None:
        _config_instance = Config(base_path)
    
    return _config_instance


def reload_config():
    """Force reload of configuration."""
    global _config_instance
    _config_instance = None
    return get_config()