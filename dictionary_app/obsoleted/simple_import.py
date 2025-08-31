#!/usr/bin/env python3
"""
Simple data import for Windows testing
"""
import json
import sqlite3
from pathlib import Path

def import_sample():
    """Import sample data avoiding Unicode issues"""
    
    db_path = Path("data/dictionary.db")
    sample_path = Path("data/sample_data.jsonl")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    print("Importing sample data...")
    
    # Import dictionary entries  
    with open(sample_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                entry = json.loads(line.strip())
                
                # Insert main entry
                cursor.execute("""
                    INSERT OR REPLACE INTO dictionary_entries 
                    (lemma, pos, meanings, definitions, examples, frequency_meaning)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    entry['lemma'],
                    entry['pos'],
                    json.dumps(entry['meanings']),
                    json.dumps(entry['definitions']),
                    json.dumps(entry['examples']),
                    json.dumps(entry['frequency_meaning'])
                ))
                
                print(f"  Imported: {entry['lemma']} ({entry['pos']})")
                
            except Exception as e:
                print(f"  Error on line {line_num}: {e}")
    
    # Import some inflections
    inflections = [
        ("runs", "run", "verb"),
        ("running", "run", "verb"),
        ("ran", "run", "verb"),
        ("went", "go", "verb"),
        ("goes", "go", "verb"),
        ("going", "go", "verb"),
        ("gone", "go", "verb"),
        ("books", "book", "noun"),
        ("happier", "happy", "adjective"),
        ("happiest", "happy", "adjective")
    ]
    
    print("Importing inflections...")
    for inflected, lemma, pos in inflections:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO inflection_lookup (inflected_form, lemma, pos)
                VALUES (?, ?, ?)
            """, (inflected, lemma, pos))
            print(f"  {inflected} -> {lemma} ({pos})")
        except Exception as e:
            print(f"  Error: {e}")
    
    conn.commit()
    conn.close()
    
    print("Sample data imported successfully!")

if __name__ == "__main__":
    import_sample()