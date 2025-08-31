#!/usr/bin/env python3
"""
Extension Store Plugin

Provides a marketplace for downloading and installing extensions.
"""

import json
import logging
import os
import sqlite3
import urllib.request
import urllib.error
import zipfile
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from core.plugin import Plugin

logger = logging.getLogger(__name__)

class ExtensionStorePlugin(Plugin):
    """Extension marketplace and installer"""
    
    def __init__(self, app):
        super().__init__(app)
        self.registry_url = "https://raw.githubusercontent.com/dictionary-app/extensions/main/registry.json"
        self.cache_file = None
        self.extensions_db = None
        self.registry_cache = []
        self.last_update = None
        
    def on_load(self):
        """Initialize extension store"""
        logger.info("Extension Store plugin loaded")
        
        # Create storage directory
        plugin_storage_path = Path(self.app.config.get('data.plugin_storage_path', 'data/plugin-storage'))
        self.storage_path = plugin_storage_path / 'extension-store'
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize cache file and database
        self.cache_file = self.storage_path / 'registry_cache.json'
        self.extensions_db = self.storage_path / 'extensions.db'
        
        # Initialize database
        self._init_database()
        
        # Load cached registry
        self._load_cache()
        
    def on_enable(self):
        """Enable extension store"""
        logger.info("Extension Store plugin enabled")
        
        # Update registry if needed (once per day)
        if self._should_update_registry():
            try:
                self.update_registry()
            except Exception as e:
                logger.info(f"Extension registry not available (offline mode): {e}")
                # Continue without registry - extension store will work with local extensions only
                
    def on_disable(self):
        """Disable extension store"""
        logger.info("Extension Store plugin disabled")
        
    def on_unload(self):
        """Cleanup extension store"""
        logger.info("Extension Store plugin unloaded")
        
    def _init_database(self):
        """Initialize extensions database"""
        conn = sqlite3.connect(str(self.extensions_db))
        conn.execute('''
            CREATE TABLE IF NOT EXISTS installed_extensions (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                version TEXT NOT NULL,
                author TEXT,
                description TEXT,
                install_date TEXT NOT NULL,
                enabled BOOLEAN DEFAULT 1,
                source_url TEXT,
                local_path TEXT
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS extension_ratings (
                extension_id TEXT,
                user_id TEXT,
                rating INTEGER,
                review TEXT,
                date TEXT,
                PRIMARY KEY (extension_id, user_id)
            )
        ''')
        conn.commit()
        conn.close()
        
    def _load_cache(self):
        """Load registry from cache file"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    self.registry_cache = data.get('extensions', [])
                    self.last_update = datetime.fromisoformat(data.get('last_update', '2000-01-01'))
                    logger.info(f"Loaded {len(self.registry_cache)} extensions from cache")
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
                self.registry_cache = []
                self.last_update = None
                
    def _save_cache(self):
        """Save registry to cache file"""
        try:
            data = {
                'extensions': self.registry_cache,
                'last_update': datetime.now().isoformat()
            }
            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
            
    def _should_update_registry(self):
        """Check if registry should be updated"""
        if not self.last_update:
            return True
        return datetime.now() - self.last_update > timedelta(days=1)
        
    def update_registry(self):
        """Fetch latest extension registry from GitHub"""
        logger.info("Updating extension registry...")
        
        try:
            with urllib.request.urlopen(self.registry_url, timeout=10) as response:
                data = json.loads(response.read().decode())
                
            # Validate registry format
            if 'extensions' in data and isinstance(data['extensions'], list):
                self.registry_cache = data['extensions']
                self.last_update = datetime.now()
                self._save_cache()
                logger.info(f"Updated registry with {len(self.registry_cache)} extensions")
                
                # Emit event
                self.app.events.emit('extension-store.registry-updated', {
                    'count': len(self.registry_cache)
                })
                
            else:
                raise ValueError("Invalid registry format")
                
        except urllib.error.URLError as e:
            logger.error(f"Network error updating registry: {e}")
            raise
        except Exception as e:
            logger.error(f"Error updating registry: {e}")
            raise
            
    def get_extensions(self, category=None, search=None, sort_by='popular'):
        """Get available extensions with optional filtering"""
        extensions = self.registry_cache.copy()
        
        # Filter by category
        if category:
            extensions = [ext for ext in extensions 
                         if category in ext.get('categories', [])]
                         
        # Filter by search term
        if search:
            search = search.lower()
            extensions = [ext for ext in extensions 
                         if search in ext.get('name', '').lower() or 
                            search in ext.get('description', '').lower() or
                            search in ' '.join(ext.get('tags', [])).lower()]
                            
        # Sort extensions
        if sort_by == 'popular':
            extensions.sort(key=lambda x: x.get('downloads', 0), reverse=True)
        elif sort_by == 'new':
            extensions.sort(key=lambda x: x.get('created_date', ''), reverse=True)
        elif sort_by == 'updated':
            extensions.sort(key=lambda x: x.get('updated_date', ''), reverse=True)
        elif sort_by == 'rating':
            extensions.sort(key=lambda x: x.get('rating', 0), reverse=True)
        elif sort_by == 'name':
            extensions.sort(key=lambda x: x.get('name', '').lower())
            
        return extensions
        
    def get_extension_details(self, extension_id):
        """Get detailed information about an extension"""
        for ext in self.registry_cache:
            if ext.get('id') == extension_id:
                # Add installation status
                ext = ext.copy()
                ext['installed'] = self.is_extension_installed(extension_id)
                ext['enabled'] = self.is_extension_enabled(extension_id)
                return ext
        return None
        
    def install_extension(self, extension_id):
        """Install an extension from the registry"""
        logger.info(f"Installing extension: {extension_id}")
        
        # Find extension in registry
        extension = None
        for ext in self.registry_cache:
            if ext.get('id') == extension_id:
                extension = ext
                break
                
        if not extension:
            raise ValueError(f"Extension '{extension_id}' not found in registry")
            
        # Check if already installed
        if self.is_extension_installed(extension_id):
            raise ValueError(f"Extension '{extension_id}' is already installed")
            
        try:
            # Download extension
            download_url = extension.get('download_url')
            if not download_url:
                raise ValueError(f"No download URL for extension '{extension_id}'")
                
            logger.info(f"Downloading from: {download_url}")
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # Download zip file
                zip_path = Path(temp_dir) / f"{extension_id}.zip"
                urllib.request.urlretrieve(download_url, zip_path)
                
                # Extract zip
                extract_path = Path(temp_dir) / "extracted"
                with zipfile.ZipFile(zip_path, 'r') as zip_file:
                    zip_file.extractall(extract_path)
                    
                # Find manifest.json
                manifest_files = list(extract_path.glob('**/manifest.json'))
                if not manifest_files:
                    raise ValueError("No manifest.json found in extension package")
                    
                manifest_path = manifest_files[0]
                extension_dir = manifest_path.parent
                
                # Validate manifest
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                    
                if manifest.get('id') != extension_id:
                    raise ValueError(f"Extension ID mismatch in manifest")
                    
                # Copy to plugins directory
                plugins_path = Path(self.app.config.get('plugins.path'))
                target_path = plugins_path / extension_id
                
                if target_path.exists():
                    shutil.rmtree(target_path)
                    
                shutil.copytree(extension_dir, target_path)
                
                # Record installation
                self._record_installation(extension, str(target_path))
                
                logger.info(f"Extension '{extension_id}' installed successfully")
                
                # Emit event
                self.app.events.emit('extension-store.extension-installed', {
                    'id': extension_id,
                    'name': extension.get('name'),
                    'version': extension.get('version')
                })
                
                # Try to load the plugin immediately
                try:
                    self.app.plugin_manager.discover_plugins()
                    self.app.plugin_manager.load_plugin(extension_id)
                    self.app.plugin_manager.enable_plugin(extension_id)
                    logger.info(f"Extension '{extension_id}' loaded and enabled")
                except Exception as e:
                    logger.warning(f"Failed to load extension immediately: {e}")
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to install extension '{extension_id}': {e}")
            raise
            
    def uninstall_extension(self, extension_id):
        """Uninstall an extension"""
        logger.info(f"Uninstalling extension: {extension_id}")
        
        if not self.is_extension_installed(extension_id):
            raise ValueError(f"Extension '{extension_id}' is not installed")
            
        try:
            # Disable and unload plugin first
            if self.app.plugin_manager.is_plugin_loaded(extension_id):
                self.app.plugin_manager.disable_plugin(extension_id)
                self.app.plugin_manager.unload_plugin(extension_id)
                
            # Remove from filesystem
            plugins_path = Path(self.app.config.get('plugins.path'))
            target_path = plugins_path / extension_id
            
            if target_path.exists():
                shutil.rmtree(target_path)
                
            # Remove from database
            conn = sqlite3.connect(str(self.extensions_db))
            conn.execute('DELETE FROM installed_extensions WHERE id = ?', (extension_id,))
            conn.execute('DELETE FROM extension_ratings WHERE extension_id = ?', (extension_id,))
            conn.commit()
            conn.close()
            
            logger.info(f"Extension '{extension_id}' uninstalled successfully")
            
            # Emit event
            self.app.events.emit('extension-store.extension-uninstalled', {
                'id': extension_id
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to uninstall extension '{extension_id}': {e}")
            raise
            
    def is_extension_installed(self, extension_id):
        """Check if extension is installed"""
        conn = sqlite3.connect(str(self.extensions_db))
        result = conn.execute('SELECT id FROM installed_extensions WHERE id = ?', 
                            (extension_id,)).fetchone()
        conn.close()
        return result is not None
        
    def is_extension_enabled(self, extension_id):
        """Check if extension is enabled"""
        if not self.is_extension_installed(extension_id):
            return False
        return self.app.plugin_manager.is_plugin_enabled(extension_id)
        
    def get_installed_extensions(self):
        """Get list of installed extensions"""
        conn = sqlite3.connect(str(self.extensions_db))
        cursor = conn.execute('''
            SELECT id, name, version, author, description, install_date, enabled 
            FROM installed_extensions ORDER BY name
        ''')
        
        extensions = []
        for row in cursor.fetchall():
            ext = {
                'id': row[0],
                'name': row[1],
                'version': row[2],
                'author': row[3],
                'description': row[4],
                'install_date': row[5],
                'enabled': bool(row[6])
            }
            extensions.append(ext)
            
        conn.close()
        return extensions
        
    def _record_installation(self, extension, local_path):
        """Record extension installation in database"""
        conn = sqlite3.connect(str(self.extensions_db))
        conn.execute('''
            INSERT OR REPLACE INTO installed_extensions 
            (id, name, version, author, description, install_date, enabled, source_url, local_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            extension.get('id'),
            extension.get('name'),
            extension.get('version'),
            extension.get('author'),
            extension.get('description'),
            datetime.now().isoformat(),
            1,  # enabled by default
            extension.get('download_url'),
            local_path
        ))
        conn.commit()
        conn.close()
        
    def search_extensions(self, query, limit=20):
        """Search extensions by name, description, or tags"""
        return self.get_extensions(search=query)[:limit]
        
    def get_categories(self):
        """Get all available categories"""
        categories = set()
        for ext in self.registry_cache:
            categories.update(ext.get('categories', []))
        return sorted(list(categories))
        
    def get_extension_rating(self, extension_id):
        """Get average rating for an extension"""
        conn = sqlite3.connect(str(self.extensions_db))
        result = conn.execute('''
            SELECT AVG(rating), COUNT(*) FROM extension_ratings 
            WHERE extension_id = ?
        ''', (extension_id,)).fetchone()
        conn.close()
        
        if result and result[1] > 0:
            return {
                'average': round(result[0], 1),
                'count': result[1]
            }
        return {'average': 0, 'count': 0}
        
    def rate_extension(self, extension_id, rating, review=None, user_id='default'):
        """Rate an extension"""
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
            
        conn = sqlite3.connect(str(self.extensions_db))
        conn.execute('''
            INSERT OR REPLACE INTO extension_ratings 
            (extension_id, user_id, rating, review, date)
            VALUES (?, ?, ?, ?, ?)
        ''', (extension_id, user_id, rating, review, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        
        logger.info(f"Rated extension '{extension_id}': {rating}/5")
        
    # UI Integration methods for settings plugin
    def get_settings_ui(self):
        """Return UI components for settings integration"""
        return {
            'name': 'Extension Store',
            'description': 'Manage dictionary extensions and themes',
            'icon': '🏪',
            'sections': [
                {
                    'title': 'Extension Store',
                    'items': [
                        {'type': 'button', 'label': 'Browse Extensions', 'action': 'open_store'},
                        {'type': 'button', 'label': 'Manage Installed', 'action': 'manage_installed'},
                        {'type': 'button', 'label': 'Check for Updates', 'action': 'check_updates'},
                        {'type': 'separator'},
                        {'type': 'toggle', 'label': 'Auto-update extensions', 'key': 'auto_update', 'default': True},
                        {'type': 'toggle', 'label': 'Show developer extensions', 'key': 'show_dev', 'default': False}
                    ]
                }
            ]
        }


# Plugin instance - required for plugin loading
def create_plugin(app):
    return ExtensionStorePlugin(app)