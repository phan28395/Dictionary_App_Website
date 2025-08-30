#!/usr/bin/env python3
"""Check if inflection data exists in the database."""

import sqlite3
import os

def check_inflection_data():
    """Check the inflection_lookup table in the database."""
    
    db_path = 'data/dictionary.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if inflection_lookup table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='inflection_lookup'
        """)
        
        if not cursor.fetchone():
            print("❌ inflection_lookup table does not exist!")
            return
        
        # Count entries in inflection_lookup
        cursor.execute("SELECT COUNT(*) FROM inflection_lookup")
        count = cursor.fetchone()[0]
        print(f"Inflection lookup table has {count} entries")
        
        if count == 0:
            print("❌ No inflection data in database!")
            print("Need to import inflection_lookup.tsv")
        else:
            # Show some sample inflections
            print("\nSample inflections in database:")
            cursor.execute("""
                SELECT inflected_form, lemma, pos 
                FROM inflection_lookup 
                WHERE inflected_form IN ('fought', 'ran', 'went', 'children', 'better')
                LIMIT 10
            """)
            
            results = cursor.fetchall()
            if results:
                for inflected, lemma, pos in results:
                    print(f"  {inflected} → {lemma} ({pos})")
            else:
                print("  None of the test inflections found")
                
            # Check for any verb inflections
            cursor.execute("""
                SELECT inflected_form, lemma, pos 
                FROM inflection_lookup 
                WHERE pos = 'verb'
                LIMIT 5
            """)
            
            print("\nSample verb inflections:")
            for inflected, lemma, pos in cursor.fetchall():
                print(f"  {inflected} → {lemma} ({pos})")
                
    except Exception as e:
        print(f"Error checking database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_inflection_data()