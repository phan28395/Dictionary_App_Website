#!/usr/bin/env python3
"""
Import dictionary data from DictGenerativeRule_2 JSONL files into SQLite database
Handles all POS types: Noun, Verb, Adjective, Adverb
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any

class DictionaryImporter:
    def __init__(self, db_path: str, data_dir: str):
        """Initialize importer with database and data directory paths"""
        self.db_path = db_path
        self.data_dir = Path(data_dir)
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Connect to SQLite database"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        # Enable JSON support
        self.conn.execute("PRAGMA foreign_keys = ON")
        
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.commit()
            self.conn.close()
            
    def create_tables(self):
        """Create database tables from schema file"""
        schema_file = Path(__file__).parent / 'database_schema.sql'
        with open(schema_file, 'r') as f:
            schema = f.read()
            
        # Execute schema creation
        self.conn.executescript(schema)
        self.conn.commit()
        
    def import_noun(self, entry: Dict[str, Any]) -> int:
        """Import a noun entry and return its ID"""
        # Insert into main dictionary table
        self.cursor.execute("""
            INSERT OR IGNORE INTO dictionary_entries 
            (lemma, pos, meanings, definitions, examples, frequency_meaning)
            VALUES (?, 'noun', ?, ?, ?, ?)
        """, (
            entry['lemma'],
            json.dumps(entry['meanings']),
            json.dumps(entry['definitions']),
            json.dumps(entry['examples']),
            json.dumps(entry['frequency_meaning'])
        ))
        
        # Get the entry ID
        entry_id = self.cursor.lastrowid
        if entry_id == 0:  # Entry already existed
            self.cursor.execute(
                "SELECT id FROM dictionary_entries WHERE lemma = ? AND pos = 'noun'",
                (entry['lemma'],)
            )
            entry_id = self.cursor.fetchone()[0]
        
        # Insert noun-specific properties
        self.cursor.execute("""
            INSERT OR REPLACE INTO noun_properties 
            (entry_id, domains, semantic_function, key_collocates)
            VALUES (?, ?, ?, ?)
        """, (
            entry_id,
            json.dumps(entry.get('domains', [])),
            json.dumps(entry.get('semantic_function', [])),
            json.dumps(entry.get('key_collocates', []))
        ))
        
        return entry_id
    
    def import_verb(self, entry: Dict[str, Any]) -> int:
        """Import a verb entry and return its ID"""
        # Insert into main dictionary table
        self.cursor.execute("""
            INSERT OR IGNORE INTO dictionary_entries 
            (lemma, pos, meanings, definitions, examples, frequency_meaning)
            VALUES (?, 'verb', ?, ?, ?, ?)
        """, (
            entry['lemma'],
            json.dumps(entry['meanings']),
            json.dumps(entry['definitions']),
            json.dumps(entry['examples']),
            json.dumps(entry['frequency_meaning'])
        ))
        
        # Get the entry ID
        entry_id = self.cursor.lastrowid
        if entry_id == 0:  # Entry already existed
            self.cursor.execute(
                "SELECT id FROM dictionary_entries WHERE lemma = ? AND pos = 'verb'",
                (entry['lemma'],)
            )
            entry_id = self.cursor.fetchone()[0]
        
        # Insert verb-specific properties
        self.cursor.execute("""
            INSERT OR REPLACE INTO verb_properties 
            (entry_id, grammatical_patterns, semantic_roles, aspect_type, key_collocates)
            VALUES (?, ?, ?, ?, ?)
        """, (
            entry_id,
            json.dumps(entry.get('grammatical_patterns', [])),
            json.dumps(entry.get('semantic_roles', [])),
            json.dumps(entry.get('aspect_type', [])),
            json.dumps(entry.get('key_collocates', []))
        ))
        
        return entry_id
    
    def import_adjective(self, entry: Dict[str, Any]) -> int:
        """Import an adjective entry and return its ID"""
        # Insert into main dictionary table
        self.cursor.execute("""
            INSERT OR IGNORE INTO dictionary_entries 
            (lemma, pos, meanings, definitions, examples, frequency_meaning)
            VALUES (?, 'adjective', ?, ?, ?, ?)
        """, (
            entry['lemma'],
            json.dumps(entry['meanings']),
            json.dumps(entry['definitions']),
            json.dumps(entry['examples']),
            json.dumps(entry['frequency_meaning'])
        ))
        
        # Get the entry ID
        entry_id = self.cursor.lastrowid
        if entry_id == 0:  # Entry already existed
            self.cursor.execute(
                "SELECT id FROM dictionary_entries WHERE lemma = ? AND pos = 'adjective'",
                (entry['lemma'],)
            )
            entry_id = self.cursor.fetchone()[0]
        
        # Insert adjective-specific properties
        self.cursor.execute("""
            INSERT OR REPLACE INTO adjective_properties 
            (entry_id, syntactic_position, gradability, semantic_type, polarity, 
             antonyms, typical_modifiers, key_collocates)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry_id,
            json.dumps(entry.get('syntactic_position', [])),
            json.dumps(entry.get('gradability', [])),
            json.dumps(entry.get('semantic_type', [])),
            json.dumps(entry.get('polarity', [])),
            json.dumps(entry.get('antonyms', [])),
            json.dumps(entry.get('typical_modifiers', [])),
            json.dumps(entry.get('key_collocates', []))
        ))
        
        return entry_id
    
    def import_adverb(self, entry: Dict[str, Any]) -> int:
        """Import an adverb entry and return its ID"""
        # Adverbs only use the common fields
        self.cursor.execute("""
            INSERT OR IGNORE INTO dictionary_entries 
            (lemma, pos, meanings, definitions, examples, frequency_meaning)
            VALUES (?, 'adverb', ?, ?, ?, ?)
        """, (
            entry['lemma'],
            json.dumps(entry['meanings']),
            json.dumps(entry['definitions']),
            json.dumps(entry['examples']),
            json.dumps(entry['frequency_meaning'])
        ))
        
        entry_id = self.cursor.lastrowid
        if entry_id == 0:  # Entry already existed
            self.cursor.execute(
                "SELECT id FROM dictionary_entries WHERE lemma = ? AND pos = 'adverb'",
                (entry['lemma'],)
            )
            entry_id = self.cursor.fetchone()[0]
            
        return entry_id
    
    def import_jsonl_file(self, filepath: Path, pos: str):
        """Import all entries from a JSONL file"""
        print(f"Importing {filepath.name}...")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    entry = json.loads(line.strip())
                    
                    if pos == 'noun':
                        self.import_noun(entry)
                    elif pos == 'verb':
                        self.import_verb(entry)
                    elif pos == 'adjective':
                        self.import_adjective(entry)
                    elif pos == 'adverb':
                        self.import_adverb(entry)
                    
                    # Commit every 100 entries
                    if line_num % 100 == 0:
                        self.conn.commit()
                        print(f"  Processed {line_num} entries...")
                        
                except json.JSONDecodeError as e:
                    print(f"  Error parsing line {line_num}: {e}")
                except Exception as e:
                    print(f"  Error importing entry at line {line_num}: {e}")
        
        self.conn.commit()
        print(f"  Completed {filepath.name}")
    
    def import_all_data(self):
        """Import all dictionary data from DictGenerativeRule_2"""
        
        # Import Nouns
        print("\n=== Importing NOUNS ===")
        noun_dir = self.data_dir / "Noun_Generator" / "Noun_Json"
        if noun_dir.exists():
            for jsonl_file in sorted(noun_dir.glob("*.jsonl")):
                self.import_jsonl_file(jsonl_file, 'noun')
        
        # Import Verbs
        print("\n=== Importing VERBS ===")
        verb_file = self.data_dir / "Verb_Generator" / "verb_entries_output.jsonl"
        if verb_file.exists():
            self.import_jsonl_file(verb_file, 'verb')
        
        # Import Adjectives
        print("\n=== Importing ADJECTIVES ===")
        adj_dir = self.data_dir / "Adjective_Generator" / "Adjective_Json"
        if adj_dir.exists():
            for jsonl_file in sorted(adj_dir.glob("*.jsonl")):
                self.import_jsonl_file(jsonl_file, 'adjective')
        
        # Import Adverbs (they're in subdirectories)
        print("\n=== Importing ADVERBS ===")
        adv_dir = self.data_dir / "Adverb_Generator" / "Adverbs_Json"
        if adv_dir.exists():
            for subdir in adv_dir.iterdir():
                if subdir.is_dir():
                    for jsonl_file in sorted(subdir.glob("*.jsonl")):
                        self.import_jsonl_file(jsonl_file, 'adverb')
        
        print("\n=== Import Complete ===")
        
    def import_inflections(self, inflection_file: Path):
        """Import inflection lookup data from TSV file"""
        print(f"\n=== Importing inflections from {inflection_file.name} ===")
        
        with open(inflection_file, 'r', encoding='utf-8') as f:
            # Skip header if present
            header = f.readline().strip()
            
            for line_num, line in enumerate(f, 2):
                try:
                    parts = line.strip().split('\t')
                    if len(parts) >= 3:
                        inflected, lemma, pos = parts[:3]
                        
                        self.cursor.execute("""
                            INSERT OR IGNORE INTO inflection_lookup 
                            (inflected_form, lemma, pos)
                            VALUES (?, ?, ?)
                        """, (inflected, lemma, pos.lower()))
                    
                    if line_num % 1000 == 0:
                        self.conn.commit()
                        print(f"  Processed {line_num} inflections...")
                        
                except Exception as e:
                    print(f"  Error at line {line_num}: {e}")
        
        self.conn.commit()
        print(f"  Completed inflection import")
    
    def get_statistics(self):
        """Print database statistics"""
        print("\n=== Database Statistics ===")
        
        # Total entries by POS
        self.cursor.execute("""
            SELECT pos, COUNT(*) FROM dictionary_entries GROUP BY pos
        """)
        for pos, count in self.cursor.fetchall():
            print(f"{pos.capitalize()}s: {count:,}")
        
        # Total inflections
        self.cursor.execute("SELECT COUNT(*) FROM inflection_lookup")
        inflections = self.cursor.fetchone()[0]
        print(f"Inflections: {inflections:,}")
        
        # Total meanings
        self.cursor.execute("""
            SELECT SUM(json_array_length(meanings)) FROM dictionary_entries
        """)
        meanings = self.cursor.fetchone()[0]
        print(f"Total meanings: {meanings:,}")
        
        # Sample entries
        print("\n=== Sample Entries ===")
        self.cursor.execute("""
            SELECT lemma, pos FROM dictionary_entries 
            ORDER BY RANDOM() LIMIT 5
        """)
        for lemma, pos in self.cursor.fetchall():
            print(f"  {lemma} ({pos})")


def main():
    """Main function to run the import"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Import dictionary data into SQLite')
    parser.add_argument('--data-dir', 
                       default='DictGenerativeRule_2',
                       help='Path to DictGenerativeRule_2 directory')
    parser.add_argument('--db-file', 
                       default='dictionary.db',
                       help='Path to SQLite database file')
    parser.add_argument('--inflection-file',
                       default='inflection_lookup.tsv',
                       help='Path to inflection TSV file')
    parser.add_argument('--create-tables', 
                       action='store_true',
                       help='Create database tables')
    parser.add_argument('--stats-only',
                       action='store_true',
                       help='Only show statistics')
    
    args = parser.parse_args()
    
    # Create importer
    importer = DictionaryImporter(args.db_file, args.data_dir)
    
    try:
        importer.connect()
        
        if args.create_tables:
            print("Creating database tables...")
            importer.create_tables()
            print("Tables created successfully")
        
        if not args.stats_only:
            # Import dictionary data
            importer.import_all_data()
            
            # Import inflections if file exists
            inflection_path = Path(args.inflection_file)
            if inflection_path.exists():
                importer.import_inflections(inflection_path)
        
        # Show statistics
        importer.get_statistics()
        
    finally:
        importer.close()


if __name__ == "__main__":
    main()