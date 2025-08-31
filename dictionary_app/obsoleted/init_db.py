#!/usr/bin/env python3
"""
Initialize database with schema
"""
import sqlite3
from pathlib import Path

def init_database():
    """Initialize database with schema."""
    db_path = Path("data/dictionary.db")
    schema_path = Path("data/database_schema.sql")
    
    # Read schema
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = f.read()
    
    # Connect and execute schema
    conn = sqlite3.connect(str(db_path))
    conn.executescript(schema)
    conn.close()
    
    print(f"Database initialized: {db_path}")

if __name__ == "__main__":
    init_database()