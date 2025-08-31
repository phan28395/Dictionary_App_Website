#!/usr/bin/env python3
"""
Comprehensive dictionary data import script.
Imports ~30,000 entries from all POS types and 106K+ inflection mappings.
"""

import json
import sqlite3
import csv
import sys
import time
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add parent to path for core imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class DictionaryImporter:
    """Import dictionary data from JSONL files into SQLite database."""
    
    def __init__(self, db_path: Path, source_dir: Path, inflections_file: Path):
        self.db_path = db_path
        self.source_dir = source_dir
        self.inflections_file = inflections_file
        self.conn = None
        self.cursor = None
        
        # Statistics
        self.stats = {
            'nouns': 0,
            'verbs': 0,
            'adjectives': 0,
            'adverbs': 0,
            'inflections': 0,
            'errors': 0,
            'files_processed': 0
        }
        
    def connect(self):
        """Connect to SQLite database."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()
        self.conn.execute("PRAGMA foreign_keys = OFF")  # Disable during import
        self.conn.execute("PRAGMA journal_mode = WAL")
        self.conn.execute("PRAGMA synchronous = NORMAL")
        
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.commit()
            self.conn.close()
    
    def import_inflections(self) -> bool:
        """Import inflection lookup data from TSV file."""
        print(f"\n[IMPORT] Importing inflections from: {self.inflections_file}")
        
        if not self.inflections_file.exists():
            print(f"[ERROR] Inflections file not found: {self.inflections_file}")
            return False
        
        try:
            with open(self.inflections_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                batch = []
                batch_size = 5000
                
                for row in reader:
                    inflected_form = row.get('inflected_form', '').strip()
                    lemma = row.get('lemma', '').strip()
                    pos = row.get('pos', '').strip()
                    
                    if inflected_form and lemma and pos:
                        batch.append((inflected_form, lemma, pos))
                        
                        if len(batch) >= batch_size:
                            self._insert_inflection_batch(batch)
                            self.stats['inflections'] += len(batch)
                            print(f"   [PROGRESS] Imported {self.stats['inflections']:,} inflections", end='\\r')
                            batch = []
                
                # Insert remaining batch
                if batch:
                    self._insert_inflection_batch(batch)
                    self.stats['inflections'] += len(batch)
                
                print(f"   [SUCCESS] Imported {self.stats['inflections']:,} inflections")
                return True
                
        except Exception as e:
            print(f"[ERROR] Error importing inflections: {e}")
            return False
    
    def _insert_inflection_batch(self, batch: List[tuple]):
        """Insert batch of inflections."""
        self.cursor.executemany("""
            INSERT OR IGNORE INTO inflection_lookup (inflected_form, lemma, pos)
            VALUES (?, ?, ?)
        """, batch)
        self.conn.commit()
    
    def import_pos_data(self, pos_type: str) -> bool:
        """Import all data for a specific POS type."""
        print(f"\n[BOOKS] Importing {pos_type}s...")
        
        # Map POS types to directory names
        dir_mapping = {
            'noun': 'Noun_Generator/Noun_Json',
            'verb': 'Verb_Generator/Verb_Json', 
            'adjective': 'Adjective_Generator/Adjective_Json',
            'adverb': 'Adverb_Generator/Adverbs_Json'
        }
        
        pos_dir = self.source_dir / dir_mapping[pos_type]
        
        if not pos_dir.exists():
            print(f"[ERROR] Directory not found: {pos_dir}")
            return False
        
        # Get all JSONL files
        jsonl_files = list(pos_dir.glob('*.jsonl'))
        
        if not jsonl_files:
            print(f"[ERROR] No JSONL files found in: {pos_dir}")
            return False
        
        print(f"   [FOLDER] Found {len(jsonl_files)} files")
        
        # Process each file
        for i, file_path in enumerate(jsonl_files, 1):
            try:
                self._import_jsonl_file(file_path, pos_type)
                self.stats['files_processed'] += 1
                
                if i % 10 == 0 or i == len(jsonl_files):
                    print(f"   [FILE] Processed {i}/{len(jsonl_files)} files - {self.stats[pos_type + 's']:,} entries", end='\\r')
                
            except Exception as e:
                print(f"\\n   [WARNING]  Error processing {file_path.name}: {e}")
                self.stats['errors'] += 1
        
        print(f"   [SUCCESS] Imported {self.stats[pos_type + 's']:,} {pos_type}s from {len(jsonl_files)} files")
        return True
    
    def _import_jsonl_file(self, file_path: Path, pos_type: str):
        """Import entries from a single JSONL file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            entries = []
            
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entry = json.loads(line)
                        entries.append(entry)
                    except json.JSONDecodeError as e:
                        print(f"\\n   [WARNING]  JSON error in {file_path.name}: {e}")
                        self.stats['errors'] += 1
            
            # Import entries in batch
            if entries:
                self._import_entries_batch(entries, pos_type)
    
    def _import_entries_batch(self, entries: List[Dict], pos_type: str):
        """Import a batch of entries for a specific POS."""
        for entry in entries:
            try:
                if pos_type == 'noun':
                    self._import_noun(entry)
                elif pos_type == 'verb':
                    self._import_verb(entry)
                elif pos_type == 'adjective':
                    self._import_adjective(entry)
                elif pos_type == 'adverb':
                    self._import_adverb(entry)
                
                self.stats[pos_type + 's'] += 1
                
            except Exception as e:
                print(f"\\n   [WARNING]  Error importing {pos_type} '{entry.get('lemma', 'unknown')}': {e}")
                self.stats['errors'] += 1
        
        self.conn.commit()
    
    def _import_noun(self, entry: Dict[str, Any]):
        """Import a noun entry."""
        # Insert into dictionary_entries
        self.cursor.execute("""
            INSERT OR REPLACE INTO dictionary_entries 
            (lemma, pos, meanings, definitions, examples, frequency_meaning)
            VALUES (?, 'noun', ?, ?, ?, ?)
        """, (
            entry['lemma'],
            json.dumps(entry['meanings']),
            json.dumps(entry['definitions']),
            json.dumps(entry['examples']),
            json.dumps(entry['frequency_meaning'])
        ))
        
        entry_id = self.cursor.lastrowid
        
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
    
    def _import_verb(self, entry: Dict[str, Any]):
        """Import a verb entry."""
        # Insert into dictionary_entries
        self.cursor.execute("""
            INSERT OR REPLACE INTO dictionary_entries 
            (lemma, pos, meanings, definitions, examples, frequency_meaning)
            VALUES (?, 'verb', ?, ?, ?, ?)
        """, (
            entry['lemma'],
            json.dumps(entry['meanings']),
            json.dumps(entry['definitions']),
            json.dumps(entry['examples']),
            json.dumps(entry['frequency_meaning'])
        ))
        
        entry_id = self.cursor.lastrowid
        
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
    
    def _import_adjective(self, entry: Dict[str, Any]):
        """Import an adjective entry."""
        # Insert into dictionary_entries
        self.cursor.execute("""
            INSERT OR REPLACE INTO dictionary_entries 
            (lemma, pos, meanings, definitions, examples, frequency_meaning)
            VALUES (?, 'adjective', ?, ?, ?, ?)
        """, (
            entry['lemma'],
            json.dumps(entry['meanings']),
            json.dumps(entry['definitions']),
            json.dumps(entry['examples']),
            json.dumps(entry['frequency_meaning'])
        ))
        
        entry_id = self.cursor.lastrowid
        
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
    
    def _import_adverb(self, entry: Dict[str, Any]):
        """Import an adverb entry."""
        # Insert into dictionary_entries (adverbs only use common fields)
        self.cursor.execute("""
            INSERT OR REPLACE INTO dictionary_entries 
            (lemma, pos, meanings, definitions, examples, frequency_meaning)
            VALUES (?, 'adverb', ?, ?, ?, ?)
        """, (
            entry['lemma'],
            json.dumps(entry['meanings']),
            json.dumps(entry['definitions']),
            json.dumps(entry['examples']),
            json.dumps(entry['frequency_meaning'])
        ))
    
    def print_final_stats(self):
        """Print final import statistics."""
        print(f"\\n{'='*60}")
        print(f"[STATS] IMPORT COMPLETED")
        print(f"{'='*60}")
        print(f"[PROGRESS] Nouns:        {self.stats['nouns']:,}")
        print(f"[VERBS] Verbs:        {self.stats['verbs']:,}")
        print(f"[ADJECTIVES] Adjectives:   {self.stats['adjectives']:,}")
        print(f"[ADVERBS] Adverbs:      {self.stats['adverbs']:,}")
        print(f"[INFLECTIONS] Inflections:  {self.stats['inflections']:,}")
        print(f"[FOLDER] Files:        {self.stats['files_processed']:,}")
        print(f"[WARNING]  Errors:       {self.stats['errors']:,}")
        
        total_entries = (self.stats['nouns'] + self.stats['verbs'] + 
                        self.stats['adjectives'] + self.stats['adverbs'])
        print(f"\\n[TOTAL] Total Dictionary Entries: {total_entries:,}")
        print(f"[TOTAL] Total Inflection Mappings: {self.stats['inflections']:,}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Import dictionary data')
    parser.add_argument('--source', default='../../../DictGenerativeRule_2',
                       help='Source directory containing POS data')
    parser.add_argument('--inflections', default='../data/inflection_lookup.tsv',
                       help='Inflections TSV file path')
    parser.add_argument('--database', default='../data/dictionary.db',
                       help='Database file path')
    
    args = parser.parse_args()
    
    # Resolve paths
    base_path = Path(__file__).parent
    source_dir = (base_path / args.source).resolve()
    inflections_file = (base_path / args.inflections).resolve()
    db_path = (base_path / args.database).resolve()
    
    print("Dictionary Data Import")
    print("=" * 50)
    print(f"[SOURCE] Source directory: {source_dir}")
    print(f"[FILE] Inflections file: {inflections_file}")
    print(f"[DATABASE]  Database file: {db_path}")
    
    # Check prerequisites
    if not source_dir.exists():
        print(f"[ERROR] Source directory not found: {source_dir}")
        sys.exit(1)
    
    if not inflections_file.exists():
        print(f"[ERROR] Inflections file not found: {inflections_file}")
        sys.exit(1)
    
    if not db_path.exists():
        print(f"[ERROR] Database file not found: {db_path}")
        print(f"   Run 'python tools/init_database.py' first")
        sys.exit(1)
    
    # Start import
    start_time = time.time()
    
    importer = DictionaryImporter(db_path, source_dir, inflections_file)
    
    try:
        importer.connect()
        
        # Import dictionary entries first (required by foreign key constraints)
        for pos_type in ['noun', 'verb', 'adjective', 'adverb']:
            if not importer.import_pos_data(pos_type):
                print(f"[WARNING]  Failed to import {pos_type}s")
        
        # Import inflections after dictionary entries exist
        if not importer.import_inflections():
            print("[ERROR] Failed to import inflections")
            # Don't exit here since we already imported the main data
        
        # Print final statistics
        importer.print_final_stats()
        
        elapsed = time.time() - start_time
        print(f"\\n[TIME]  Total time: {elapsed:.1f} seconds")
        
        print(f"\\n[SUCCESS] Dictionary data import completed successfully!")
        print(f"   Next step: python tools/verify_database.py")
        
    except Exception as e:
        print(f"[ERROR] Import failed: {e}")
        sys.exit(1)
    
    finally:
        importer.close()


if __name__ == '__main__':
    main()