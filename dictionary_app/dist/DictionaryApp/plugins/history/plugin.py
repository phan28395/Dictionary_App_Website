"""
History Plugin for Dictionary App
Tracks user search history.
"""

import sys
import logging
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import Counter

# Add parent to path for core imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import Plugin, CoreEvents

logger = logging.getLogger(__name__)


class HistoryPlugin(Plugin):
    """
    Plugin for tracking search history.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.db_path = None
        self.conn = None
        self.search_count = 0
        
    def on_load(self):
        """Called when plugin is loaded."""
        logger.info("History plugin loaded")
        
        # Set up storage
        storage_path = self.get_storage_path()
        if storage_path:
            self.db_path = storage_path / "history.db"
            self._init_database()
            
    def on_enable(self):
        """Called when plugin is enabled."""
        super().on_enable()
        logger.info("History plugin enabled")
        
        # Subscribe to events
        self.app.events.on(CoreEvents.SEARCH_COMPLETE, self._record_search)
        self.app.events.on('history.list', self._list_history)
        self.app.events.on('history.clear', self._clear_history)
        self.app.events.on('history.stats', self._get_statistics)
        self.app.events.on('history.export', self._export_history)
        
        # Track search count for free tier limit
        self._load_search_count()
        
    def on_disable(self):
        """Called when plugin is disabled."""
        super().on_disable()
        logger.info("History plugin disabled")
        
        # Close database
        if self.conn:
            self.conn.close()
            self.conn = None
            
    def _init_database(self):
        """Initialize history database."""
        if not self.db_path:
            return
            
        self.conn = sqlite3.connect(str(self.db_path))
        cursor = self.conn.cursor()
        
        # Create table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                search_term TEXT NOT NULL,
                found_lemma TEXT,
                found_pos TEXT,
                result_count INTEGER DEFAULT 0,
                search_context TEXT,  -- 'hotkey', 'manual', 'suggestion'
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create search count table (for free tier tracking)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_counts (
                id INTEGER PRIMARY KEY,
                user_type TEXT DEFAULT 'guest',
                daily_count INTEGER DEFAULT 0,
                total_count INTEGER DEFAULT 0,
                last_reset DATE DEFAULT CURRENT_DATE
            )
        """)
        
        # Initialize search count record
        cursor.execute("""
            INSERT OR IGNORE INTO search_counts (id, user_type)
            VALUES (1, 'guest')
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_history_timestamp 
            ON search_history(timestamp DESC)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_history_term 
            ON search_history(search_term)
        """)
        
        self.conn.commit()
        logger.info("History database initialized")
        
    def _load_search_count(self):
        """Load current search count for free tier limit."""
        if not self.conn:
            return
            
        try:
            cursor = self.conn.cursor()
            
            # Check if we need to reset daily count
            cursor.execute("""
                SELECT daily_count, total_count, last_reset
                FROM search_counts
                WHERE id = 1
            """)
            
            row = cursor.fetchone()
            if row:
                daily_count, total_count, last_reset = row
                
                # Reset daily count if it's a new day
                today = datetime.now().date().isoformat()
                if last_reset != today:
                    cursor.execute("""
                        UPDATE search_counts
                        SET daily_count = 0, last_reset = ?
                        WHERE id = 1
                    """, (today,))
                    self.conn.commit()
                    self.search_count = total_count
                else:
                    self.search_count = total_count
                    
                logger.info(f"Search count loaded: {self.search_count}")
                
        except Exception as e:
            logger.error(f"Error loading search count: {e}")
            
    def _record_search(self, term: str, results: List[Any]):
        """
        Record a search in history.
        
        Args:
            term: Search term
            results: Search results
        """
        if not self.conn:
            return
            
        try:
            cursor = self.conn.cursor()
            
            # Get first result info if available
            found_lemma = None
            found_pos = None
            if results and len(results) > 0:
                found_lemma = results[0].lemma
                found_pos = results[0].pos
                
            # Determine context
            context = "manual"  # Could be enhanced to detect hotkey vs manual
            
            # Insert history record
            cursor.execute("""
                INSERT INTO search_history 
                (search_term, found_lemma, found_pos, result_count, search_context)
                VALUES (?, ?, ?, ?, ?)
            """, (term, found_lemma, found_pos, len(results), context))
            
            # Update search count
            cursor.execute("""
                UPDATE search_counts
                SET daily_count = daily_count + 1,
                    total_count = total_count + 1
                WHERE id = 1
            """)
            
            self.conn.commit()
            self.search_count += 1
            
            # Check free tier limit
            self._check_search_limit()
            
            logger.debug(f"Recorded search: {term} ({len(results)} results)")
            
        except Exception as e:
            logger.error(f"Error recording search: {e}")
            
    def _check_search_limit(self):
        """Check if free tier search limit reached."""
        # Check if user is licensed
        is_licensed = self.app.get_config('license.activated', False)
        
        if not is_licensed and self.search_count >= 50:
            logger.warning("Free tier search limit reached")
            self.app.events.emit('search.limit_reached', self.search_count)
            
    def _list_history(self, limit: int = 100, days: int = None) -> List[Dict[str, Any]]:
        """
        List search history.
        
        Args:
            limit: Maximum results
            days: Filter to last N days
            
        Returns:
            List of history entries
        """
        if not self.conn:
            return []
            
        try:
            cursor = self.conn.cursor()
            
            if days:
                query = """
                    SELECT search_term, found_lemma, found_pos, 
                           result_count, search_context, timestamp
                    FROM search_history
                    WHERE timestamp > datetime('now', '-' || ? || ' days')
                    ORDER BY timestamp DESC
                    LIMIT ?
                """
                cursor.execute(query, (days, limit))
            else:
                query = """
                    SELECT search_term, found_lemma, found_pos,
                           result_count, search_context, timestamp
                    FROM search_history
                    ORDER BY timestamp DESC
                    LIMIT ?
                """
                cursor.execute(query, (limit,))
                
            results = []
            for row in cursor.fetchall():
                term, lemma, pos, count, context, timestamp = row
                results.append({
                    'search_term': term,
                    'found_lemma': lemma,
                    'found_pos': pos,
                    'result_count': count,
                    'context': context,
                    'timestamp': timestamp
                })
                
            return results
            
        except Exception as e:
            logger.error(f"Error listing history: {e}")
            return []
            
    def _clear_history(self, days: int = None) -> bool:
        """
        Clear search history.
        
        Args:
            days: Clear only entries older than N days (None = all)
            
        Returns:
            Success boolean
        """
        if not self.conn:
            return False
            
        try:
            cursor = self.conn.cursor()
            
            if days:
                cursor.execute("""
                    DELETE FROM search_history
                    WHERE timestamp < datetime('now', '-' || ? || ' days')
                """, (days,))
            else:
                cursor.execute("DELETE FROM search_history")
                
            self.conn.commit()
            
            deleted = cursor.rowcount
            logger.info(f"Cleared {deleted} history entries")
            
            return True
            
        except Exception as e:
            logger.error(f"Error clearing history: {e}")
            return False
            
    def get_search_count(self) -> int:
        """
        Get total search count (public API for other plugins).
        
        Returns:
            Total number of searches
        """
        if not self.conn:
            return 0
            
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT total_count FROM search_counts WHERE id = 1")
            row = cursor.fetchone()
            return row[0] if row else 0
        except Exception as e:
            logger.error(f"Error getting search count: {e}")
            return 0
            
    def _get_statistics(self) -> Dict[str, Any]:
        """
        Get history statistics.
        
        Returns:
            Statistics dictionary
        """
        if not self.conn:
            return {}
            
        try:
            cursor = self.conn.cursor()
            
            # Total searches
            cursor.execute("SELECT COUNT(*) FROM search_history")
            total = cursor.fetchone()[0]
            
            # Today's searches
            cursor.execute("""
                SELECT COUNT(*) FROM search_history
                WHERE date(timestamp) = date('now')
            """)
            today = cursor.fetchone()[0]
            
            # This week's searches
            cursor.execute("""
                SELECT COUNT(*) FROM search_history
                WHERE timestamp > datetime('now', '-7 days')
            """)
            week = cursor.fetchone()[0]
            
            # Most searched terms
            cursor.execute("""
                SELECT search_term, COUNT(*) as count
                FROM search_history
                GROUP BY search_term
                ORDER BY count DESC
                LIMIT 10
            """)
            top_searches = [
                {'term': row[0], 'count': row[1]}
                for row in cursor.fetchall()
            ]
            
            # Search success rate
            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN result_count > 0 THEN 1 END) * 100.0 / COUNT(*)
                FROM search_history
            """)
            success_rate = cursor.fetchone()[0] or 0
            
            # Get current search count for limit
            cursor.execute("""
                SELECT total_count FROM search_counts WHERE id = 1
            """)
            search_count = cursor.fetchone()[0] or 0
            
            return {
                'total_searches': total,
                'searches_today': today,
                'searches_week': week,
                'top_searches': top_searches,
                'success_rate': round(success_rate, 1),
                'search_count': search_count,
                'limit_reached': search_count >= 50 and not self.app.get_config('license.activated', False)
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
            
    def _export_history(self, format: str = "json") -> Optional[str]:
        """
        Export history to various formats.
        
        Args:
            format: Export format (json, csv)
            
        Returns:
            Exported data string or None
        """
        history = self._list_history(limit=10000)
        
        if format == "json":
            return json.dumps(history, indent=2, default=str)
            
        elif format == "csv":
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.DictWriter(
                output,
                fieldnames=['search_term', 'found_lemma', 'found_pos', 
                          'result_count', 'context', 'timestamp']
            )
            writer.writeheader()
            writer.writerows(history)
            
            return output.getvalue()
            
        else:
            logger.error(f"Unknown export format: {format}")
            return None