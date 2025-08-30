#!/usr/bin/env python3
"""Check the actual format of data in the database."""

import sqlite3
import json

db_path = 'data/dictionary.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check a few entries from dictionary_entries
print("Sample entries from dictionary_entries:")
cursor.execute("""
    SELECT id, lemma, pos, meanings
    FROM dictionary_entries 
    WHERE lemma IN ('fight', 'run', 'go', 'happy', 'child')
    LIMIT 10
""")

for row in cursor.fetchall():
    id, lemma, pos, meanings_raw = row
    print(f"\nLemma: {lemma} ({pos})")
    print(f"Meanings type: {type(meanings_raw)}")
    print(f"Meanings raw (first 200 chars): {str(meanings_raw)[:200]}")
    
    # Try to parse as JSON
    if meanings_raw:
        try:
            meanings = json.loads(meanings_raw)
            print(f"Parsed successfully! Type: {type(meanings)}")
            if isinstance(meanings, list) and meanings:
                print(f"First meaning type: {type(meanings[0])}")
                if isinstance(meanings[0], dict):
                    print(f"First meaning keys: {meanings[0].keys()}")
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")

# Check if there are entries for the specific lemmas we're testing
print("\n" + "="*50)
print("Checking for specific test lemmas:")
test_lemmas = ['fight', 'run', 'go', 'be', 'take', 'write', 'child', 'man', 'woman']
for lemma in test_lemmas:
    cursor.execute("SELECT COUNT(*) FROM dictionary_entries WHERE lemma = ?", (lemma,))
    count = cursor.fetchone()[0]
    if count > 0:
        print(f"✓ {lemma}: {count} entries")
    else:
        print(f"✗ {lemma}: NOT FOUND")

conn.close()