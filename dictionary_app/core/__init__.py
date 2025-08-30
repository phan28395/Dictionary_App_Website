"""
Dictionary App Core - Headless engine for dictionary functionality.
"""

from .app import DictionaryApp
from .config import Config, get_config, reload_config
from .database import Database
from .search import SearchEngine, SearchResult
from .plugin import Plugin, PluginLoader, PluginManifest
from .events import EventEmitter, EventPriority, CoreEvents

__version__ = "1.0.0"

__all__ = [
    'DictionaryApp',
    'Config',
    'get_config',
    'reload_config',
    'Database',
    'SearchEngine',
    'SearchResult',
    'Plugin',
    'PluginLoader',
    'PluginManifest',
    'EventEmitter',
    'EventPriority',
    'CoreEvents',
]