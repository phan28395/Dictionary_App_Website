#!/usr/bin/env python3
"""Import verb entries from JSONL files."""

import json
import sqlite3
import os
from pathlib import Path

def import_verbs():
    """Import verb entries from DictGenerativeRule_2."""
    
    # Connect to database
    db_path = 'data/dictionary.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Path to verb files
    verb_dir = Path('../DictGenerativeRule_2/Verb_Generator/Verb_Json')
    
    if not verb_dir.exists():
        print(f"❌ Verb directory not found: {verb_dir}")
        return
    
    print(f"Importing verbs from {verb_dir}")
    
    imported = 0
    skipped_empty = 0
    errors = 0
    
    # Get all JSONL files
    jsonl_files = sorted(verb_dir.glob('*.jsonl'))
    print(f"Found {len(jsonl_files)} verb JSONL files")
    
    for jsonl_file in jsonl_files:
        print(f"Processing {jsonl_file.name}...")
        
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    entry = json.loads(line)
                    
                    lemma = entry.get('lemma', '')
                    meanings = entry.get('meanings', [])
                    
                    # Skip entries with empty meanings
                    if not meanings or (isinstance(meanings, list) and len(meanings) == 0):
                        skipped_empty += 1
                        continue
                    
                    # Check if this verb already exists
                    cursor.execute(
                        "SELECT id FROM dictionary_entries WHERE lemma = ? AND pos = 'verb'",
                        (lemma,)
                    )
                    
                    if cursor.fetchone():
                        print(f"  Skipping duplicate: {lemma}")
                        continue
                    
                    # Prepare the data
                    definitions = entry.get('definitions', [])
                    examples = entry.get('examples', [])
                    frequency_meaning = entry.get('frequency_meaning', [])
                    
                    # Insert into dictionary_entries
                    cursor.execute("""
                        INSERT INTO dictionary_entries 
                        (lemma, pos, meanings, definitions, examples, frequency_meaning)
                        VALUES (?, 'verb', ?, ?, ?, ?)
                    """, (
                        lemma,
                        json.dumps(meanings),
                        json.dumps(definitions),
                        json.dumps(examples),
                        json.dumps(frequency_meaning)
                    ))
                    
                    entry_id = cursor.lastrowid
                    
                    # Insert verb-specific data into verb_properties table
                    grammatical_patterns = entry.get('grammatical_patterns', [])
                    semantic_roles = entry.get('semantic_roles', [])
                    aspect_type = entry.get('aspect_type', [])
                    key_collocates = entry.get('key_collocates', [])
                    
                    # Only insert if we have POS-specific data
                    if grammatical_patterns or semantic_roles or aspect_type or key_collocates:
                        cursor.execute("""
                            INSERT OR REPLACE INTO verb_properties
                            (entry_id, grammatical_patterns, semantic_roles, aspect_type, key_collocates)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            entry_id,
                            json.dumps(grammatical_patterns) if grammatical_patterns else None,
                            json.dumps(semantic_roles) if semantic_roles else None,
                            json.dumps(aspect_type) if aspect_type else None,
                            json.dumps(key_collocates) if key_collocates else None
                        ))
                    
                    imported += 1
                    
                    if imported % 100 == 0:
                        print(f"  Imported {imported} verbs...")
                        conn.commit()
                    
                except json.JSONDecodeError as e:
                    errors += 1
                    print(f"  JSON error in {jsonl_file.name} line {line_num}: {e}")
                except Exception as e:
                    errors += 1
                    print(f"  Error in {jsonl_file.name} line {line_num}: {e}")
    
    # Final commit
    conn.commit()
    
    # Show results
    print("\n" + "="*50)
    print("VERB IMPORT COMPLETE")
    print("="*50)
    print(f"✅ Imported: {imported} verbs")
    print(f"⏭️  Skipped (empty): {skipped_empty}")
    print(f"❌ Errors: {errors}")
    
    # Check specific verbs
    print("\nChecking for key verbs:")
    test_verbs = ['fight', 'run', 'go', 'be', 'have', 'do', 'take', 'make', 'get']
    for verb in test_verbs:
        cursor.execute(
            "SELECT COUNT(*) FROM dictionary_entries WHERE lemma = ? AND pos = 'verb'",
            (verb,)
        )
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"  ✓ {verb}")
        else:
            print(f"  ✗ {verb}")
    
    conn.close()

if __name__ == "__main__":
    import_verbs()