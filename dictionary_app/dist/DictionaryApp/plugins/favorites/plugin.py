"""
Favorites Plugin for Dictionary App
Manages user's favorite words.
"""

import sys
import logging
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add parent to path for core imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import Plugin, CoreEvents

logger = logging.getLogger(__name__)


class FavoritesPlugin(Plugin):
    """
    Plugin for managing favorite words.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.db_path = None
        self.conn = None
        
    def on_load(self):
        """Called when plugin is loaded."""
        logger.info("Favorites plugin loaded")
        
        # Set up storage
        storage_path = self.get_storage_path()
        if storage_path:
            self.db_path = storage_path / "favorites.db"
            self._init_database()
            
    def on_enable(self):
        """Called when plugin is enabled."""
        super().on_enable()
        logger.info("Favorites plugin enabled")
        
        # Subscribe to events
        self.app.events.on('favorites.add', self._add_favorite)
        self.app.events.on('favorites.remove', self._remove_favorite)
        self.app.events.on('favorites.list', self._list_favorites)
        self.app.events.on('favorites.check', self._is_favorite)
        self.app.events.on('favorites.export', self._export_favorites)
        
    def on_disable(self):
        """Called when plugin is disabled."""
        super().on_disable()
        logger.info("Favorites plugin disabled")
        
        # Close database
        if self.conn:
            self.conn.close()
            self.conn = None
            
    def _init_database(self):
        """Initialize favorites database."""
        if not self.db_path:
            return
            
        self.conn = sqlite3.connect(str(self.db_path))
        cursor = self.conn.cursor()
        
        # Create table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lemma TEXT NOT NULL,
                pos TEXT NOT NULL,
                meaning_index INTEGER DEFAULT 0,
                note TEXT,
                tags TEXT,  -- JSON array of tags
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(lemma, pos, meaning_index)
            )
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_favorites_lemma ON favorites(lemma)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_favorites_created ON favorites(created_at DESC)
        """)
        
        self.conn.commit()
        logger.info("Favorites database initialized")
        
    def _add_favorite(self, lemma: str, pos: str, meaning_index: int = 0, note: str = None, tags: List[str] = None):
        """
        Add a word to favorites.
        
        Args:
            lemma: Word lemma
            pos: Part of speech
            meaning_index: Index of specific meaning
            note: Optional user note
            tags: Optional list of tags
            
        Returns:
            Success boolean
        """
        if not self.conn:
            logger.error("Database not initialized")
            return False
            
        try:
            cursor = self.conn.cursor()
            
            # Convert tags to JSON
            tags_json = json.dumps(tags) if tags else None
            
            # Insert or update
            cursor.execute("""
                INSERT OR REPLACE INTO favorites 
                (lemma, pos, meaning_index, note, tags, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (lemma, pos, meaning_index, note, tags_json))
            
            self.conn.commit()
            
            logger.info(f"Added favorite: {lemma} ({pos})")
            
            # Emit event
            self.app.events.emit('favorites.added', {
                'lemma': lemma,
                'pos': pos,
                'meaning_index': meaning_index
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding favorite: {e}")
            return False
            
    def _remove_favorite(self, lemma: str, pos: str, meaning_index: int = None):
        """
        Remove a word from favorites.
        
        Args:
            lemma: Word lemma
            pos: Part of speech
            meaning_index: Optional specific meaning
            
        Returns:
            Success boolean
        """
        if not self.conn:
            return False
            
        try:
            cursor = self.conn.cursor()
            
            if meaning_index is not None:
                cursor.execute("""
                    DELETE FROM favorites 
                    WHERE lemma = ? AND pos = ? AND meaning_index = ?
                """, (lemma, pos, meaning_index))
            else:
                cursor.execute("""
                    DELETE FROM favorites 
                    WHERE lemma = ? AND pos = ?
                """, (lemma, pos))
                
            self.conn.commit()
            
            if cursor.rowcount > 0:
                logger.info(f"Removed favorite: {lemma} ({pos})")
                
                # Emit event
                self.app.events.emit('favorites.removed', {
                    'lemma': lemma,
                    'pos': pos,
                    'meaning_index': meaning_index
                })
                
            return cursor.rowcount > 0
            
        except Exception as e:
            logger.error(f"Error removing favorite: {e}")
            return False
            
    def _is_favorite(self, lemma: str, pos: str, meaning_index: int = None) -> bool:
        """
        Check if a word is in favorites.
        
        Args:
            lemma: Word lemma
            pos: Part of speech
            meaning_index: Optional specific meaning
            
        Returns:
            True if favorite
        """
        if not self.conn:
            return False
            
        try:
            cursor = self.conn.cursor()
            
            if meaning_index is not None:
                cursor.execute("""
                    SELECT 1 FROM favorites 
                    WHERE lemma = ? AND pos = ? AND meaning_index = ?
                    LIMIT 1
                """, (lemma, pos, meaning_index))
            else:
                cursor.execute("""
                    SELECT 1 FROM favorites 
                    WHERE lemma = ? AND pos = ?
                    LIMIT 1
                """, (lemma, pos))
                
            return cursor.fetchone() is not None
            
        except Exception as e:
            logger.error(f"Error checking favorite: {e}")
            return False
            
    def _list_favorites(self, tags: List[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List all favorites.
        
        Args:
            tags: Optional filter by tags
            limit: Maximum results
            
        Returns:
            List of favorite entries
        """
        if not self.conn:
            return []
            
        try:
            cursor = self.conn.cursor()
            
            if tags:
                # Filter by tags (simplified - would need proper JSON querying)
                query = """
                    SELECT lemma, pos, meaning_index, note, tags, created_at, updated_at
                    FROM favorites
                    ORDER BY created_at DESC
                    LIMIT ?
                """
                cursor.execute(query, (limit,))
            else:
                query = """
                    SELECT lemma, pos, meaning_index, note, tags, created_at, updated_at
                    FROM favorites
                    ORDER BY created_at DESC
                    LIMIT ?
                """
                cursor.execute(query, (limit,))
                
            results = []
            for row in cursor.fetchall():
                lemma, pos, meaning_index, note, tags_json, created_at, updated_at = row
                
                # Parse tags
                tags_list = json.loads(tags_json) if tags_json else []
                
                results.append({
                    'lemma': lemma,
                    'pos': pos,
                    'meaning_index': meaning_index,
                    'note': note,
                    'tags': tags_list,
                    'created_at': created_at,
                    'updated_at': updated_at
                })
                
            return results
            
        except Exception as e:
            logger.error(f"Error listing favorites: {e}")
            return []
            
    def _export_favorites(self, format: str = "json") -> Optional[str]:
        """
        Export favorites to various formats.
        
        Args:
            format: Export format (json, csv, anki)
            
        Returns:
            Exported data string or None
        """
        favorites = self._list_favorites(limit=10000)
        
        if format == "json":
            return json.dumps(favorites, indent=2, default=str)
            
        elif format == "csv":
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.DictWriter(
                output,
                fieldnames=['lemma', 'pos', 'meaning_index', 'note', 'tags', 'created_at']
            )
            writer.writeheader()
            
            for fav in favorites:
                row = fav.copy()
                row['tags'] = ', '.join(row['tags']) if row['tags'] else ''
                writer.writerow(row)
                
            return output.getvalue()
            
        elif format == "anki":
            # Format for Anki import
            lines = []
            for fav in favorites:
                # Get full definition from search
                results = self.app.search(fav['lemma'])
                definition = ""
                
                for result in results:
                    if result.pos == fav['pos']:
                        if fav['meaning_index'] < len(result.meanings):
                            meaning = result.meanings[fav['meaning_index']]
                            definition = meaning.get('definition', '')
                        break
                        
                # Format: Front\tBack\tTags
                front = fav['lemma']
                back = f"{fav['pos']}: {definition}"
                tags = ' '.join(fav['tags']) if fav['tags'] else 'dictionary'
                
                lines.append(f"{front}\t{back}\t{tags}")
                
            return '\n'.join(lines)
            
        else:
            logger.error(f"Unknown export format: {format}")
            return None
            
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get favorites statistics.
        
        Returns:
            Statistics dictionary
        """
        if not self.conn:
            return {}
            
        try:
            cursor = self.conn.cursor()
            
            # Total count
            cursor.execute("SELECT COUNT(*) FROM favorites")
            total = cursor.fetchone()[0]
            
            # By POS
            cursor.execute("""
                SELECT pos, COUNT(*) 
                FROM favorites 
                GROUP BY pos
            """)
            by_pos = dict(cursor.fetchall())
            
            # Recent additions
            cursor.execute("""
                SELECT COUNT(*) 
                FROM favorites 
                WHERE created_at > datetime('now', '-7 days')
            """)
            recent = cursor.fetchone()[0]
            
            return {
                'total': total,
                'by_pos': by_pos,
                'recent_week': recent
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}