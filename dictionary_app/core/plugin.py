"""
Plugin system for Dictionary App.
Provides base classes and plugin loading functionality.
"""

import os
import sys
import json
import logging
import importlib
import importlib.util
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type
from abc import ABC, abstractmethod
from dataclasses import dataclass
import threading

logger = logging.getLogger(__name__)


@dataclass
class PluginManifest:
    """Plugin manifest data."""
    id: str
    name: str
    version: str
    main: str
    author: Optional[str] = None
    description: Optional[str] = None
    homepage: Optional[str] = None
    permissions: List[str] = None
    dependencies: List[str] = None
    replaces: Optional[str] = None
    min_app_version: Optional[str] = None
    max_app_version: Optional[str] = None
    
    @classmethod
    def from_json(cls, json_path: Path) -> 'PluginManifest':
        """Load manifest from JSON file."""
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate required fields
        required = ['id', 'name', 'version', 'main']
        for field in required:
            if field not in data:
                raise ValueError(f"Missing required field '{field}' in manifest")
        
        return cls(
            id=data['id'],
            name=data['name'],
            version=data['version'],
            main=data['main'],
            author=data.get('author'),
            description=data.get('description'),
            homepage=data.get('homepage'),
            permissions=data.get('permissions', []),
            dependencies=data.get('dependencies', []),
            replaces=data.get('replaces'),
            min_app_version=data.get('min_app_version'),
            max_app_version=data.get('max_app_version')
        )


class Plugin(ABC):
    """
    Base class for all plugins.
    """
    
    def __init__(self, app: Any):
        """
        Initialize plugin with app reference.
        
        Args:
            app: Application instance
        """
        self.app = app
        self.manifest = None
        self.enabled = False
        self.storage_path = None
        
    def on_load(self):
        """Called when plugin is loaded."""
        pass
    
    def on_enable(self):
        """Called when plugin is enabled."""
        self.enabled = True
    
    def on_disable(self):
        """Called when plugin is disabled."""
        self.enabled = False
    
    def on_unload(self):
        """Called when plugin is about to be unloaded."""
        pass
    
    def get_storage_path(self) -> Path:
        """
        Get plugin-specific storage directory.
        
        Returns:
            Path to plugin storage directory
        """
        if not self.storage_path:
            return None
        
        # Create directory if it doesn't exist
        self.storage_path.mkdir(parents=True, exist_ok=True)
        return self.storage_path
    
    def save_config(self, config: Dict[str, Any]):
        """
        Save plugin configuration.
        
        Args:
            config: Configuration dictionary
        """
        storage = self.get_storage_path()
        if storage:
            config_path = storage / 'config.json'
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load plugin configuration.
        
        Returns:
            Configuration dictionary
        """
        storage = self.get_storage_path()
        if storage:
            config_path = storage / 'config.json'
            if config_path.exists():
                with open(config_path, 'r') as f:
                    return json.load(f)
        return {}


class PluginLoader:
    """
    Manages loading and lifecycle of plugins.
    """
    
    def __init__(self, app: Any, config: Dict[str, Any]):
        """
        Initialize plugin loader.
        
        Args:
            app: Application instance
            config: Configuration dictionary
        """
        self.app = app
        self.config = config
        self.plugins: Dict[str, Plugin] = {}
        self.manifests: Dict[str, PluginManifest] = {}
        self.load_order: List[str] = []
        self._lock = threading.Lock()
        
        # Plugin directories
        self.plugin_dirs = [
            Path(config.get('plugins', {}).get('directory', 'plugins'))
        ]
        
        dev_dir = config.get('plugins', {}).get('dev_directory')
        if dev_dir:
            self.plugin_dirs.append(Path(dev_dir))
    
    def discover_plugins(self) -> Dict[str, PluginManifest]:
        """
        Discover all available plugins.
        
        Returns:
            Dictionary of plugin ID to manifest
        """
        discovered = {}
        
        for plugin_dir in self.plugin_dirs:
            if not plugin_dir.exists():
                continue
            
            # Look for plugin folders
            for item in plugin_dir.iterdir():
                if not item.is_dir():
                    continue
                
                manifest_path = item / 'manifest.json'
                if not manifest_path.exists():
                    continue
                
                try:
                    manifest = PluginManifest.from_json(manifest_path)
                    manifest.plugin_dir = item  # Store plugin directory
                    discovered[manifest.id] = manifest
                    logger.info(f"Discovered plugin: {manifest.id} v{manifest.version}")
                except Exception as e:
                    logger.error(f"Failed to load manifest from {manifest_path}: {e}")
        
        return discovered
    
    def resolve_dependencies(self, manifests: Dict[str, PluginManifest]) -> List[str]:
        """
        Resolve plugin dependencies and determine load order.
        
        Args:
            manifests: Dictionary of plugin manifests
            
        Returns:
            List of plugin IDs in load order
        """
        # Build dependency graph
        dependencies = {}
        for plugin_id, manifest in manifests.items():
            dependencies[plugin_id] = set(manifest.dependencies or [])
        
        # Detect circular dependencies
        def has_circular_dependency(node: str, visited: Set[str], stack: Set[str]) -> bool:
            visited.add(node)
            stack.add(node)
            
            for neighbor in dependencies.get(node, []):
                if neighbor not in visited:
                    if has_circular_dependency(neighbor, visited, stack):
                        return True
                elif neighbor in stack:
                    return True
            
            stack.remove(node)
            return False
        
        for plugin_id in dependencies:
            if has_circular_dependency(plugin_id, set(), set()):
                logger.error(f"Circular dependency detected involving plugin: {plugin_id}")
                # Remove from dependencies to break the cycle
                dependencies[plugin_id] = set()
        
        # Topological sort for load order
        load_order = []
        visited = set()
        
        def visit(node: str):
            if node in visited:
                return
            visited.add(node)
            
            for dep in dependencies.get(node, []):
                if dep in manifests:  # Only if dependency exists
                    visit(dep)
            
            load_order.append(node)
        
        # Check for predefined load order in config
        predefined = self.config.get('plugins', {}).get('load_order', [])
        
        # Visit predefined plugins first
        for plugin_id in predefined:
            if plugin_id in manifests:
                visit(plugin_id)
        
        # Visit remaining plugins
        for plugin_id in manifests:
            visit(plugin_id)
        
        return load_order
    
    def load_plugin(self, manifest: PluginManifest) -> Optional[Plugin]:
        """
        Load a single plugin.
        
        Args:
            manifest: Plugin manifest
            
        Returns:
            Plugin instance or None if failed
        """
        try:
            # Add plugin directory to Python path
            plugin_dir = manifest.plugin_dir
            if str(plugin_dir) not in sys.path:
                sys.path.insert(0, str(plugin_dir))
            
            # Load the main module
            main_path = plugin_dir / manifest.main
            
            if main_path.suffix == '.py':
                # Load Python file
                spec = importlib.util.spec_from_file_location(
                    f"plugins.{manifest.id}",
                    main_path
                )
                module = importlib.util.module_from_spec(spec)
                sys.modules[spec.name] = module
                spec.loader.exec_module(module)
            else:
                # Load Python package
                module = importlib.import_module(manifest.main)
            
            # Find Plugin subclass
            plugin_class = None
            for name in dir(module):
                obj = getattr(module, name)
                if (isinstance(obj, type) and 
                    issubclass(obj, Plugin) and 
                    obj is not Plugin):
                    plugin_class = obj
                    break
            
            if not plugin_class:
                logger.error(f"No Plugin subclass found in {manifest.id}")
                return None
            
            # Create plugin instance
            plugin = plugin_class(self.app)
            plugin.manifest = manifest
            
            # Set storage path
            storage_base = Path(self.config.get('plugins', {}).get('storage_directory', 'data/plugin-storage'))
            plugin.storage_path = storage_base / manifest.id
            
            # Call lifecycle method
            plugin.on_load()
            
            logger.info(f"Loaded plugin: {manifest.id}")
            return plugin
            
        except Exception as e:
            logger.error(f"Failed to load plugin {manifest.id}: {e}")
            return None
    
    def load_all_plugins(self):
        """Load all discovered plugins in dependency order."""
        with self._lock:
            # Discover plugins
            manifests = self.discover_plugins()
            self.manifests = manifests
            
            # Resolve dependencies and get load order
            self.load_order = self.resolve_dependencies(manifests)
            
            # Load plugins in order
            for plugin_id in self.load_order:
                if plugin_id in manifests:
                    plugin = self.load_plugin(manifests[plugin_id])
                    if plugin:
                        self.plugins[plugin_id] = plugin
    
    def enable_plugin(self, plugin_id: str) -> bool:
        """
        Enable a plugin.
        
        Args:
            plugin_id: Plugin ID
            
        Returns:
            True if successful
        """
        with self._lock:
            if plugin_id not in self.plugins:
                logger.error(f"Plugin not found: {plugin_id}")
                return False
            
            plugin = self.plugins[plugin_id]
            if not plugin.enabled:
                try:
                    plugin.on_enable()
                    logger.info(f"Enabled plugin: {plugin_id}")
                    return True
                except Exception as e:
                    logger.error(f"Failed to enable plugin {plugin_id}: {e}")
                    return False
            
            return True
    
    def disable_plugin(self, plugin_id: str) -> bool:
        """
        Disable a plugin.
        
        Args:
            plugin_id: Plugin ID
            
        Returns:
            True if successful
        """
        with self._lock:
            if plugin_id not in self.plugins:
                logger.error(f"Plugin not found: {plugin_id}")
                return False
            
            plugin = self.plugins[plugin_id]
            if plugin.enabled:
                try:
                    plugin.on_disable()
                    logger.info(f"Disabled plugin: {plugin_id}")
                    return True
                except Exception as e:
                    logger.error(f"Failed to disable plugin {plugin_id}: {e}")
                    return False
            
            return True
    
    def unload_plugin(self, plugin_id: str) -> bool:
        """
        Unload a plugin.
        
        Args:
            plugin_id: Plugin ID
            
        Returns:
            True if successful
        """
        with self._lock:
            return self._unload_plugin_internal(plugin_id)
    
    def reload_plugin(self, plugin_id: str) -> bool:
        """
        Reload a plugin (unload and load again).
        
        Args:
            plugin_id: Plugin ID
            
        Returns:
            True if successful
        """
        if plugin_id not in self.manifests:
            return False
        
        # Remember if it was enabled
        was_enabled = False
        if plugin_id in self.plugins:
            was_enabled = self.plugins[plugin_id].enabled
            self.unload_plugin(plugin_id)
        
        # Reload the plugin
        manifest = self.manifests[plugin_id]
        plugin = self.load_plugin(manifest)
        
        if plugin:
            self.plugins[plugin_id] = plugin
            
            # Re-enable if it was enabled
            if was_enabled:
                self.enable_plugin(plugin_id)
            
            return True
        
        return False
    
    def get_plugin(self, plugin_id: str) -> Optional[Plugin]:
        """
        Get plugin instance by ID.
        
        Args:
            plugin_id: Plugin ID
            
        Returns:
            Plugin instance or None
        """
        return self.plugins.get(plugin_id)
    
    def get_enabled_plugins(self) -> List[Plugin]:
        """
        Get list of enabled plugins.
        
        Returns:
            List of enabled plugin instances
        """
        return [p for p in self.plugins.values() if p.enabled]
    
    def shutdown(self):
        """Shutdown all plugins."""
        with self._lock:
            # Unload in reverse order
            for plugin_id in reversed(self.load_order):
                if plugin_id in self.plugins:
                    self._unload_plugin_internal(plugin_id)
    
    def _unload_plugin_internal(self, plugin_id: str) -> bool:
        """Internal unload method that doesn't acquire lock."""
        if plugin_id not in self.plugins:
            return False
        
        plugin = self.plugins[plugin_id]
        
        try:
            # Disable first if enabled
            if plugin.enabled:
                plugin.on_disable()
            
            # Call unload lifecycle
            plugin.on_unload()
            
            # Remove from registry
            del self.plugins[plugin_id]
            
            logger.info(f"Unloaded plugin: {plugin_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unload plugin {plugin_id}: {e}")
            return False