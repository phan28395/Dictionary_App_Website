"""
Database layer implementation for Dictionary App.
Handles SQLite connections, encryption, and query execution.
"""

import sqlite3
import json
import logging
import hashlib
import platform
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from contextlib import contextmanager
from threading import Lock
import queue
import time

logger = logging.getLogger(__name__)

# Try to import SQLCipher, fallback to regular SQLite
try:
    import pysqlcipher3.dbapi2 as sqlite3_encrypted
    SQLCIPHER_AVAILABLE = True
    logger.info("SQLCipher support available")
except ImportError:
    sqlite3_encrypted = sqlite3
    SQLCIPHER_AVAILABLE = False
    logger.warning("SQLCipher not available, using unencrypted SQLite")


class DatabaseConnectionPool:
    """
    Connection pool for SQLite database connections.
    """
    
    def __init__(self, database_path: Path, pool_size: int = 5, encrypted: bool = False, key: Optional[str] = None):
        """
        Initialize connection pool.
        
        Args:
            database_path: Path to database file
            pool_size: Number of connections in pool
            encrypted: Whether to use encryption
            key: Encryption key (if encrypted)
        """
        self.database_path = database_path
        self.pool_size = pool_size
        self.encrypted = encrypted and SQLCIPHER_AVAILABLE
        self.key = key
        self._pool = queue.Queue(maxsize=pool_size)
        self._lock = Lock()
        self._closed = False
        
        # Initialize the pool with connections
        self._init_pool()
    
    def _init_pool(self):
        """Initialize the connection pool."""
        for _ in range(self.pool_size):
            conn = self._create_connection()
            self._pool.put(conn)
    
    def _create_connection(self) -> sqlite3.Connection:
        """Create a new database connection."""
        if self.encrypted:
            conn = sqlite3_encrypted.connect(str(self.database_path))
            if self.key:
                conn.execute(f"PRAGMA key = '{self.key}'")
                # Test the connection with encryption
                try:
                    conn.execute("SELECT 1")
                except sqlite3.DatabaseError:
                    logger.error("Failed to decrypt database with provided key")
                    raise
        else:
            conn = sqlite3.connect(str(self.database_path), check_same_thread=False)
        
        # Enable foreign keys and optimizations
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.execute("PRAGMA temp_store = MEMORY")
        conn.execute("PRAGMA mmap_size = 30000000000")
        
        # Register JSON functions for SQLite
        conn.create_function("json_extract", 2, self._json_extract)
        
        return conn
    
    @staticmethod
    def _json_extract(json_str: str, path: str) -> Any:
        """Extract value from JSON string using path."""
        try:
            data = json.loads(json_str)
            keys = path.strip("$.").split(".")
            for key in keys:
                if key.isdigit():
                    data = data[int(key)]
                else:
                    data = data[key]
            return data
        except (json.JSONDecodeError, KeyError, IndexError):
            return None
    
    @contextmanager
    def get_connection(self):
        """
        Get a connection from the pool.
        
        Yields:
            Database connection
        """
        if self._closed:
            raise RuntimeError("Connection pool is closed")
        
        conn = None
        try:
            conn = self._pool.get(timeout=30)
            yield conn
        finally:
            if conn:
                self._pool.put(conn)
    
    def close(self):
        """Close all connections in the pool."""
        with self._lock:
            if self._closed:
                return
            
            self._closed = True
            
            while not self._pool.empty():
                try:
                    conn = self._pool.get_nowait()
                    conn.close()
                except queue.Empty:
                    break


class Database:
    """
    Main database interface for Dictionary App.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize database manager.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.database_path = Path(config.get('database', {}).get('path', 'data/dictionary.db'))
        self.database_path = self.database_path if self.database_path.is_absolute() else Path.cwd() / self.database_path
        
        # Ensure data directory exists
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Encryption settings
        self.encryption_enabled = config.get('database', {}).get('encryption', {}).get('enabled', False)
        self.encryption_key = None
        
        if self.encryption_enabled:
            self.encryption_key = self._derive_encryption_key()
        
        # Connection pool settings
        pool_size = config.get('database', {}).get('connection', {}).get('pool_size', 5)
        
        # Initialize connection pool
        self.pool = DatabaseConnectionPool(
            self.database_path,
            pool_size=pool_size,
            encrypted=self.encryption_enabled,
            key=self.encryption_key
        )
        
        # Initialize database if needed
        if not self.database_path.exists() or self.database_path.stat().st_size == 0:
            self._initialize_database()
    
    def _derive_encryption_key(self) -> str:
        """
        Derive encryption key from hardware identifiers.
        
        Returns:
            Encryption key string
        """
        components = []
        
        # Get MAC address
        try:
            import uuid
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                          for elements in range(0,8*6,8)][::-1])
            components.append(mac)
        except Exception as e:
            logger.warning(f"Could not get MAC address: {e}")
            components.append("default-mac")
        
        # Get CPU info
        try:
            if platform.system() == "Windows":
                cpu_id = subprocess.check_output("wmic cpu get ProcessorId", shell=True).decode().split('\n')[1].strip()
            elif platform.system() == "Linux":
                with open("/proc/cpuinfo", 'r') as f:
                    for line in f:
                        if "serial" in line.lower() or "processor" in line.lower():
                            cpu_id = line.split(':')[1].strip()
                            break
                    else:
                        cpu_id = "default-cpu"
            elif platform.system() == "Darwin":  # macOS
                cpu_id = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"]).decode().strip()
            else:
                cpu_id = "default-cpu"
            components.append(cpu_id)
        except Exception as e:
            logger.warning(f"Could not get CPU ID: {e}")
            components.append("default-cpu")
        
        # Create key from components
        key_material = '|'.join(components)
        key_hash = hashlib.pbkdf2_hmac(
            'sha256',
            key_material.encode(),
            b'dictionary-app-salt',
            iterations=self.config.get('database', {}).get('encryption', {}).get('key_derivation_rounds', 100000)
        )
        
        return key_hash.hex()
    
    def _initialize_database(self):
        """Initialize database with schema."""
        logger.info("Initializing database...")
        
        schema_path = Path(__file__).parent.parent / 'data' / 'database_schema.sql'
        
        if not schema_path.exists():
            logger.error(f"Database schema file not found: {schema_path}")
            return
        
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Split and execute each statement
            statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
            
            for statement in statements:
                try:
                    cursor.execute(statement)
                except sqlite3.Error as e:
                    logger.warning(f"Error executing statement: {e}\nStatement: {statement[:100]}...")
            
            conn.commit()
        
        logger.info("Database initialized successfully")
    
    def execute(self, query: str, params: Optional[Tuple] = None) -> List[Tuple]:
        """
        Execute a SELECT query.
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            Query results
        """
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
    
    def execute_one(self, query: str, params: Optional[Tuple] = None) -> Optional[Tuple]:
        """
        Execute a SELECT query and return first result.
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            First row or None
        """
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchone()
    
    def execute_many(self, query: str, params_list: List[Tuple]) -> int:
        """
        Execute multiple INSERT/UPDATE/DELETE queries.
        
        Args:
            query: SQL query
            params_list: List of parameter tuples
            
        Returns:
            Number of rows affected
        """
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount
    
    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """
        Insert a row into table.
        
        Args:
            table: Table name
            data: Column values
            
        Returns:
            Last row ID
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(data.values()))
            conn.commit()
            return cursor.lastrowid
    
    def update(self, table: str, data: Dict[str, Any], where: str, params: Tuple) -> int:
        """
        Update rows in table.
        
        Args:
            table: Table name
            data: Column values to update
            where: WHERE clause
            params: WHERE parameters
            
        Returns:
            Number of rows affected
        """
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where}"
        
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(data.values()) + params)
            conn.commit()
            return cursor.rowcount
    
    def delete(self, table: str, where: str, params: Tuple) -> int:
        """
        Delete rows from table.
        
        Args:
            table: Table name
            where: WHERE clause
            params: WHERE parameters
            
        Returns:
            Number of rows affected
        """
        query = f"DELETE FROM {table} WHERE {where}"
        
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
    
    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions.
        
        Usage:
            with db.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute(...)
                cursor.execute(...)
        """
        with self.pool.get_connection() as conn:
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
    
    def backup(self, backup_path: Path):
        """
        Create database backup.
        
        Args:
            backup_path: Path for backup file
        """
        with self.pool.get_connection() as conn:
            backup_conn = sqlite3.connect(str(backup_path))
            with backup_conn:
                conn.backup(backup_conn)
            backup_conn.close()
        
        logger.info(f"Database backed up to {backup_path}")
    
    def close(self):
        """Close database connections."""
        self.pool.close()
    
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get information about table columns.
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of column information
        """
        query = f"PRAGMA table_info({table_name})"
        rows = self.execute(query)
        
        return [
            {
                'cid': row[0],
                'name': row[1],
                'type': row[2],
                'notnull': row[3],
                'default': row[4],
                'pk': row[5]
            }
            for row in rows
        ]
    
    def table_exists(self, table_name: str) -> bool:
        """
        Check if table exists.
        
        Args:
            table_name: Name of the table
            
        Returns:
            True if table exists
        """
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        result = self.execute_one(query, (table_name,))
        return result is not None