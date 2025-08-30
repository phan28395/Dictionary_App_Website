#!/usr/bin/env python3
"""Import the updated 'run' verb entry into the database."""

import json
import sqlite3

def import_run_verb():
    """Import the 'run' verb with its complete data."""
    
    # Connect to database
    conn = sqlite3.connect('data/dictionary.db')
    cursor = conn.cursor()
    
    # The complete 'run' verb data
    run_entry = {
        "lemma": "run",
        "meanings": ["move rapidly", "operate or function", "manage or direct", "extend or continue", "flow as liquid", "compete in election"],
        "definitions": [
            "move at a speed faster than walking by taking quick steps",
            "function or operate as a machine or system is designed to",
            "be in charge of and manage a business or organization",
            "extend in a particular direction or continue for a specific duration",
            "flow continuously as a liquid moves through or from something",
            "compete as a candidate for an elected position or office"
        ],
        "examples": [
            ["She runs five miles every morning before breakfast", "The children ran excitedly toward the playground"],
            ["This computer runs much faster than my old one", "The engine runs smoothly after the recent tune-up"],
            ["He successfully runs three restaurants in the city", "She has run the company for over ten years"],
            ["The road runs parallel to the river for miles", "The play will run for six weeks on Broadway"],
            ["Water runs through these old pipes into the tank", "The tap has been running all day long"],
            ["She decided to run for mayor this year", "He ran against the incumbent in the last election"]
        ],
        "frequency_meaning": [0.35, 0.2, 0.15, 0.1, 0.1, 0.1],
        "grammatical_patterns": [
            ["V", "V + prep"],
            ["V", "V + adv"],
            ["V + O"],
            ["V + prep", "V + for"],
            ["V", "V + prep"],
            ["V + for", "V + against"]
        ],
        "semantic_roles": ["agent_only", "theme_only", "agent_patient", "theme_only", "theme_only", "agent_only"],
        "aspect_type": ["activity", "activity", "activity", "state", "activity", "activity"],
        "key_collocates": [
            ["fast", "miles", "sprint", "jog"],
            ["operate", "function", "smoothly", "engine"],
            ["manage", "business", "company", "organization"],
            ["extend", "parallel", "continue", "direction"],
            ["water", "flow", "liquid", "tap"],
            ["candidate", "election", "mayor", "office"]
        ]
    }
    
    try:
        # First check if 'run' verb already exists
        cursor.execute("SELECT id FROM dictionary_entries WHERE lemma = 'run' AND pos = 'verb'")
        existing = cursor.fetchone()
        
        if existing:
            entry_id = existing[0]
            print(f"Updating existing 'run' verb entry (id={entry_id})")
            
            # Update the existing entry
            cursor.execute("""
                UPDATE dictionary_entries 
                SET meanings = ?, definitions = ?, examples = ?, frequency_meaning = ?
                WHERE id = ?
            """, (
                json.dumps(run_entry['meanings']),
                json.dumps(run_entry['definitions']),
                json.dumps(run_entry['examples']),
                json.dumps(run_entry['frequency_meaning']),
                entry_id
            ))
            
            # Update verb-specific properties
            cursor.execute("""
                UPDATE verb_properties
                SET grammatical_patterns = ?, semantic_roles = ?, aspect_type = ?, key_collocates = ?
                WHERE entry_id = ?
            """, (
                json.dumps(run_entry['grammatical_patterns']),
                json.dumps(run_entry['semantic_roles']),
                json.dumps(run_entry['aspect_type']),
                json.dumps(run_entry['key_collocates']),
                entry_id
            ))
            
        else:
            print("Inserting new 'run' verb entry")
            
            # Insert new entry
            cursor.execute("""
                INSERT INTO dictionary_entries (lemma, pos, meanings, definitions, examples, frequency_meaning)
                VALUES ('run', 'verb', ?, ?, ?, ?)
            """, (
                json.dumps(run_entry['meanings']),
                json.dumps(run_entry['definitions']),
                json.dumps(run_entry['examples']),
                json.dumps(run_entry['frequency_meaning'])
            ))
            
            entry_id = cursor.lastrowid
            
            # Insert verb-specific properties
            cursor.execute("""
                INSERT INTO verb_properties (entry_id, grammatical_patterns, semantic_roles, aspect_type, key_collocates)
                VALUES (?, ?, ?, ?, ?)
            """, (
                entry_id,
                json.dumps(run_entry['grammatical_patterns']),
                json.dumps(run_entry['semantic_roles']),
                json.dumps(run_entry['aspect_type']),
                json.dumps(run_entry['key_collocates'])
            ))
        
        # Commit changes
        conn.commit()
        print("✅ Successfully imported 'run' verb entry!")
        
        # Verify the import
        cursor.execute("""
            SELECT lemma, substr(meanings, 1, 100) 
            FROM dictionary_entries 
            WHERE lemma = 'run' AND pos = 'verb'
        """)
        result = cursor.fetchone()
        if result:
            print(f"Verified: {result[0]} - {result[1][:100]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    import_run_verb()