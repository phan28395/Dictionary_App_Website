#!/usr/bin/env python3
"""
Simple script to import sample data for testing
"""

import sys
import json
import sqlite3
from pathlib import Path

def import_sample_data():
    """Import sample data into database"""
    
    db_path = Path("data/dictionary.db")
    sample_path = Path("data/sample_data.jsonl")
    inflection_path = Path("data/inflection_lookup.tsv")
    
    if not db_path.exists():
        print("Database not found. Run with --create-tables first.")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    print("Importing sample data...")
    
    # Import dictionary entries
    with open(sample_path, 'r') as f:
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
                
                entry_id = cursor.lastrowid
                
                # Insert POS-specific data
                if entry['pos'] == 'noun' and entry_id:
                    cursor.execute("""
                        INSERT OR REPLACE INTO noun_entries 
                        (entry_id, domains, semantic_function, key_collocates)
                        VALUES (?, ?, ?, ?)
                    """, (
                        entry_id,
                        json.dumps(entry.get('domains')),
                        entry.get('semantic_function'),
                        json.dumps(entry.get('key_collocates'))
                    ))
                    
                elif entry['pos'] == 'verb' and entry_id:
                    cursor.execute("""
                        INSERT OR REPLACE INTO verb_entries 
                        (entry_id, grammatical_patterns, semantic_roles, aspect_type)
                        VALUES (?, ?, ?, ?)
                    """, (
                        entry_id,
                        json.dumps(entry.get('grammatical_patterns')),
                        entry.get('semantic_roles'),
                        entry.get('aspect_type')
                    ))
                    
                elif entry['pos'] == 'adjective' and entry_id:
                    cursor.execute("""
                        INSERT OR REPLACE INTO adjective_entries 
                        (entry_id, gradability, semantic_prosody, attributive_only, 
                         predicative_only, comparative_form, superlative_form, typical_modifiers)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        entry_id,
                        entry.get('gradability'),
                        entry.get('semantic_prosody'),
                        entry.get('attributive_only', False),
                        entry.get('predicative_only', False),
                        entry.get('comparative_form'),
                        entry.get('superlative_form'),
                        json.dumps(entry.get('typical_modifiers'))
                    ))
                    
                print(f"  Imported: {entry['lemma']} ({entry['pos']})")
                
            except Exception as e:
                print(f"  Error on line {line_num}: {e}")
    
    # Import some inflections
    print("\nImporting sample inflections...")
    inflections = [
        ('went', 'go', 'verb'),
        ('goes', 'go', 'verb'),
        ('going', 'go', 'verb'),
        ('ran', 'run', 'verb'),
        ('running', 'run', 'verb'),
        ('runs', 'run', 'verb'),
        ('books', 'book', 'noun'),
        ('happier', 'happy', 'adjective'),
        ('happiest', 'happy', 'adjective'),
        ('happily', 'happy', 'adverb'),
    ]
    
    for inflected, lemma, pos in inflections:
        cursor.execute("""
            INSERT OR REPLACE INTO inflection_lookup 
            (inflected_form, lemma, pos)
            VALUES (?, ?, ?)
        """, (inflected, lemma, pos))
        print(f"  {inflected} → {lemma} ({pos})")
    
    conn.commit()
    
    # Show statistics
    print("\n=== Database Statistics ===")
    
    cursor.execute("SELECT COUNT(*) FROM dictionary_entries")
    entries = cursor.fetchone()[0]
    print(f"Dictionary entries: {entries}")
    
    cursor.execute("SELECT COUNT(*) FROM inflection_lookup")
    inflections = cursor.fetchone()[0]
    print(f"Inflections: {inflections}")
    
    cursor.execute("SELECT COUNT(DISTINCT pos) FROM dictionary_entries")
    pos_types = cursor.fetchone()[0]
    print(f"POS types: {pos_types}")
    
    conn.close()
    print("\nSample data import complete!")

if __name__ == "__main__":
    import_sample_data()