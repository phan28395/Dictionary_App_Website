#!/usr/bin/env python3
"""
Database initialization script for Dictionary App.
Forces recreation of database schema even if file already exists.
"""

import sqlite3
import sys
from pathlib import Path

# Add parent to path for core imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def init_database():
    """Initialize database with complete schema."""
    
    # Database and schema paths
    db_path = Path(__file__).parent.parent / 'data' / 'dictionary.db'
    schema_path = Path(__file__).parent.parent / 'data' / 'database_schema.sql'
    
    print(f"Database path: {db_path}")
    print(f"Schema path: {schema_path}")
    
    # Check schema file exists
    if not schema_path.exists():
        print(f"ERROR: Schema file not found: {schema_path}")
        sys.exit(1)
    
    # Handle existing database
    if db_path.exists():
        print(f"[RESET] Resetting existing database...")
        # Try to delete file, but if in use, we'll drop tables instead
        try:
            db_path.unlink()
            print(f"   [OK] Database file deleted")
        except PermissionError:
            print(f"   [INFO] Database file in use, will drop existing tables")
    
    print(f"[SCHEMA] Loading schema from: {schema_path}")
    
    # Read schema
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # Create new database with schema
    print(f"[CREATE] Creating database: {db_path}")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Drop existing tables if database already exists
        if db_path.exists():
            print(f"   [CLEANUP] Dropping existing tables...")
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            for table in tables:
                cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")
            conn.commit()
        
        # Split and execute schema statements
        statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
        
        print(f"[SQL] Executing {len(statements)} SQL statements...")
        
        for i, statement in enumerate(statements, 1):
            if statement.strip():
                try:
                    cursor.execute(statement)
                    if i % 10 == 0 or i == len(statements):
                        print(f"   [OK] Executed {i}/{len(statements)} statements")
                except sqlite3.Error as e:
                    print(f"   [WARN] Warning on statement {i}: {e}")
                    print(f"      Statement: {statement[:100]}...")
        
        # Commit changes
        conn.commit()
        
        # Verify tables were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"\n[TABLES] Created {len(tables)} tables:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"   [TABLE] {table[0]}: {count} rows")
        
        # Verify views
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
        views = cursor.fetchall()
        
        if views:
            print(f"\n[VIEWS] Created {len(views)} views:")
            for view in views:
                print(f"   [VIEW] {view[0]}")
        
        # Verify indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND sql IS NOT NULL")
        indexes = cursor.fetchall()
        
        if indexes:
            print(f"\n[INDEXES] Created {len(indexes)} indexes:")
            for index in indexes:
                print(f"   [INDEX] {index[0]}")
        
        conn.close()
        
        print(f"\n[SUCCESS] Database initialization completed successfully!")
        print(f"   Database file size: {db_path.stat().st_size:,} bytes")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")
        return False


if __name__ == '__main__':
    print("Dictionary App Database Initialization")
    print("=" * 50)
    
    success = init_database()
    
    if success:
        print("\n[READY] Ready to import dictionary data!")
        print("   Next step: python tools/import_dictionary_data.py")
        sys.exit(0)
    else:
        print("\n[FAILED] Initialization failed!")
        sys.exit(1)