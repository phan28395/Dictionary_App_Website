#!/usr/bin/env python3
"""
Complete Dictionary Data Import Script
Imports all dictionary entries and inflection mappings
"""

import os
import sys
import json
import sqlite3
import time
from pathlib import Path
from typing import Dict, List, Any
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DictionaryImporter:
    def __init__(self, db_path: str, data_dir: str):
        """Initialize importer with database and data paths."""
        self.db_path = Path(db_path)
        self.data_dir = Path(data_dir)
        self.conn = None
        self.stats = {
            'total_files': 0,
            'total_entries': 0,
            'nouns': 0,
            'verbs': 0,
            'adjectives': 0,
            'adverbs': 0,
            'errors': 0,
            'inflections': 0
        }
        
    def connect(self):
        """Connect to database."""
        logger.info(f"Connecting to database: {self.db_path}")
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("PRAGMA journal_mode = WAL")
        
    def clear_existing_data(self):
        """Clear existing dictionary data (but keep user data)."""
        logger.info("Clearing existing dictionary data...")
        cursor = self.conn.cursor()
        
        # Disable foreign keys temporarily
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        # Clear dictionary tables in reverse dependency order
        tables_to_clear = [
            'examples',  # Depends on word_meanings
            'word_meanings',  # Depends on dictionary_entries
            'noun_data',  # Depends on dictionary_entries
            'verb_data',  # Depends on dictionary_entries
            'adjective_data',  # Depends on dictionary_entries
            'adverb_data',  # Depends on dictionary_entries
            'dictionary_entries',  # Main table
            'inflection_lookup'  # Independent
        ]
        
        for table in tables_to_clear:
            try:
                cursor.execute(f"DELETE FROM {table}")
                logger.info(f"  Cleared table: {table}")
            except sqlite3.OperationalError:
                logger.warning(f"  Table {table} doesn't exist")
                
        # Re-enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        self.conn.commit()
        
    def import_inflections(self, inflection_file: Path):
        """Import inflection lookup data."""
        logger.info(f"Importing inflections from: {inflection_file}")
        
        if not inflection_file.exists():
            logger.error(f"Inflection file not found: {inflection_file}")
            return
            
        cursor = self.conn.cursor()
        batch = []
        batch_size = 1000
        
        with open(inflection_file, 'r', encoding='utf-8') as f:
            # Skip header if present
            first_line = f.readline().strip()
            if not first_line.startswith('inflected_form'):
                f.seek(0)  # Reset if no header
                
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                    
                parts = line.split('\t')
                if len(parts) >= 3:
                    inflected_form = parts[0].strip()
                    lemma = parts[1].strip()
                    pos = parts[2].strip().lower()
                    
                    # Map POS to our format
                    pos_map = {
                        'n': 'noun',
                        'v': 'verb',
                        'adj': 'adjective',
                        'adv': 'adverb',
                        'noun': 'noun',
                        'verb': 'verb',
                        'adjective': 'adjective',
                        'adverb': 'adverb'
                    }
                    
                    if pos in pos_map:
                        batch.append((inflected_form, lemma, pos_map[pos]))
                        
                        if len(batch) >= batch_size:
                            cursor.executemany(
                                "INSERT OR IGNORE INTO inflection_lookup (inflected_form, lemma, pos) VALUES (?, ?, ?)",
                                batch
                            )
                            self.stats['inflections'] += len(batch)
                            batch = []
                            
                            if line_num % 10000 == 0:
                                logger.info(f"  Processed {line_num:,} inflections...")
                                
        # Insert remaining batch
        if batch:
            cursor.executemany(
                "INSERT OR IGNORE INTO inflection_lookup (inflected_form, lemma, pos) VALUES (?, ?, ?)",
                batch
            )
            self.stats['inflections'] += len(batch)
            
        self.conn.commit()
        logger.info(f"  Imported {self.stats['inflections']:,} inflection mappings")
        
    def import_jsonl_file(self, file_path: Path) -> int:
        """Import a single JSONL file."""
        count = 0
        cursor = self.conn.cursor()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                        
                    try:
                        entry = json.loads(line)
                        self.import_entry(cursor, entry)
                        count += 1
                    except json.JSONDecodeError as e:
                        logger.debug(f"  JSON error in {file_path.name} line {line_num}: {e}")
                        self.stats['errors'] += 1
                    except Exception as e:
                        logger.debug(f"  Error in {file_path.name} line {line_num}: {e}")
                        self.stats['errors'] += 1
                        
        except Exception as e:
            logger.error(f"  Failed to read {file_path}: {e}")
            
        return count
        
    def import_entry(self, cursor, entry: Dict[str, Any]):
        """Import a single dictionary entry."""
        # Extract basic fields
        lemma = entry.get('lemma', '').strip()
        pos = entry.get('pos', '').strip().lower()
        
        if not lemma or not pos:
            return
            
        # Insert main entry
        cursor.execute("""
            INSERT OR IGNORE INTO dictionary_entries (lemma, pos)
            VALUES (?, ?)
        """, (lemma, pos))
        
        # Get entry_id
        cursor.execute("""
            SELECT id FROM dictionary_entries WHERE lemma = ? AND pos = ?
        """, (lemma, pos))
        
        result = cursor.fetchone()
        if not result:
            return
            
        entry_id = result[0]
        
        # Import meanings
        meanings = entry.get('meanings', [])
        if isinstance(meanings, str):
            meanings = [{'definition': meanings}]
        elif not isinstance(meanings, list):
            meanings = []
            
        for meaning in meanings:
            if isinstance(meaning, dict):
                definition = meaning.get('definition', '')
                frequency = meaning.get('frequency_meaning', 0.0)
                
                if definition:
                    cursor.execute("""
                        INSERT INTO word_meanings (entry_id, definition, frequency_rank)
                        VALUES (?, ?, ?)
                    """, (entry_id, definition, frequency))
                    
                    meaning_id = cursor.lastrowid
                    
                    # Import examples
                    examples = meaning.get('examples', [])
                    if isinstance(examples, list):
                        for example in examples:
                            if isinstance(example, dict):
                                text = example.get('text', '')
                                source = example.get('source', '')
                            else:
                                text = str(example)
                                source = ''
                                
                            if text:
                                cursor.execute("""
                                    INSERT INTO examples (meaning_id, example_text, source)
                                    VALUES (?, ?, ?)
                                """, (meaning_id, text, source))
                                
        # Import POS-specific data
        if pos == 'noun':
            self.import_noun_data(cursor, entry_id, entry)
            self.stats['nouns'] += 1
        elif pos == 'verb':
            self.import_verb_data(cursor, entry_id, entry)
            self.stats['verbs'] += 1
        elif pos == 'adjective':
            self.import_adjective_data(cursor, entry_id, entry)
            self.stats['adjectives'] += 1
        elif pos == 'adverb':
            self.import_adverb_data(cursor, entry_id, entry)
            self.stats['adverbs'] += 1
            
    def import_noun_data(self, cursor, entry_id: int, entry: Dict):
        """Import noun-specific data."""
        domains = json.dumps(entry.get('domains', []))
        semantic_function = entry.get('semantic_function', '')
        key_collocates = json.dumps(entry.get('key_collocates', []))
        
        cursor.execute("""
            INSERT OR REPLACE INTO noun_data (entry_id, domains, semantic_function, key_collocates)
            VALUES (?, ?, ?, ?)
        """, (entry_id, domains, semantic_function, key_collocates))
        
    def import_verb_data(self, cursor, entry_id: int, entry: Dict):
        """Import verb-specific data."""
        grammatical_patterns = json.dumps(entry.get('grammatical_patterns', []))
        semantic_roles = json.dumps(entry.get('semantic_roles', []))
        aspect_type = entry.get('aspect_type', '')
        
        cursor.execute("""
            INSERT OR REPLACE INTO verb_data (entry_id, grammatical_patterns, semantic_roles, aspect_type)
            VALUES (?, ?, ?, ?)
        """, (entry_id, grammatical_patterns, semantic_roles, aspect_type))
        
    def import_adjective_data(self, cursor, entry_id: int, entry: Dict):
        """Import adjective-specific data."""
        gradability = entry.get('gradability', '')
        semantic_prosody = entry.get('semantic_prosody', '')
        typical_nouns = json.dumps(entry.get('typical_nouns', []))
        comparative_form = entry.get('comparative_form', '')
        superlative_form = entry.get('superlative_form', '')
        register_distribution = json.dumps(entry.get('register_distribution', {}))
        collocational_strength = entry.get('collocational_strength', 0.0)
        
        cursor.execute("""
            INSERT OR REPLACE INTO adjective_data 
            (entry_id, gradability, semantic_prosody, typical_nouns, comparative_form, 
             superlative_form, register_distribution, collocational_strength)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (entry_id, gradability, semantic_prosody, typical_nouns, comparative_form,
              superlative_form, register_distribution, collocational_strength))
              
    def import_adverb_data(self, cursor, entry_id: int, entry: Dict):
        """Import adverb-specific data."""
        # Adverbs have minimal extra data
        cursor.execute("""
            INSERT OR REPLACE INTO adverb_data (entry_id)
            VALUES (?)
        """, (entry_id,))
        
    def import_all_jsonl_files(self):
        """Import all JSONL files from data directory."""
        logger.info(f"Scanning for JSONL files in: {self.data_dir}")
        
        # Find all JSONL files
        jsonl_files = list(self.data_dir.rglob("*.jsonl"))
        logger.info(f"Found {len(jsonl_files)} JSONL files")
        
        self.stats['total_files'] = len(jsonl_files)
        
        # Process each file
        for i, file_path in enumerate(jsonl_files, 1):
            relative_path = file_path.relative_to(self.data_dir)
            logger.info(f"[{i}/{len(jsonl_files)}] Processing: {relative_path}")
            
            count = self.import_jsonl_file(file_path)
            self.stats['total_entries'] += count
            
            # Commit every 10 files
            if i % 10 == 0:
                self.conn.commit()
                logger.info(f"  Progress: {self.stats['total_entries']:,} entries imported")
                
        # Final commit
        self.conn.commit()
        
    def create_indexes(self):
        """Create database indexes for better performance."""
        logger.info("Creating database indexes...")
        cursor = self.conn.cursor()
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_entries_lemma ON dictionary_entries(lemma)",
            "CREATE INDEX IF NOT EXISTS idx_entries_pos ON dictionary_entries(pos)",
            "CREATE INDEX IF NOT EXISTS idx_inflection_form ON inflection_lookup(inflected_form)",
            "CREATE INDEX IF NOT EXISTS idx_inflection_lemma ON inflection_lookup(lemma)",
            "CREATE INDEX IF NOT EXISTS idx_meanings_entry ON word_meanings(entry_id)",
            "CREATE INDEX IF NOT EXISTS idx_examples_meaning ON examples(meaning_id)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
            logger.info(f"  Created: {index_sql.split('idx_')[1].split(' ')[0]}")
            
        self.conn.commit()
        
    def verify_import(self):
        """Verify the import was successful."""
        logger.info("Verifying import...")
        cursor = self.conn.cursor()
        
        # Count entries by POS
        cursor.execute("""
            SELECT pos, COUNT(*) FROM dictionary_entries GROUP BY pos
        """)
        
        pos_counts = cursor.fetchall()
        for pos, count in pos_counts:
            logger.info(f"  {pos}: {count:,} entries")
            
        # Count inflections
        cursor.execute("SELECT COUNT(*) FROM inflection_lookup")
        inflection_count = cursor.fetchone()[0]
        logger.info(f"  Inflections: {inflection_count:,}")
        
        # Count meanings
        cursor.execute("SELECT COUNT(*) FROM word_meanings")
        meaning_count = cursor.fetchone()[0]
        logger.info(f"  Meanings: {meaning_count:,}")
        
        # Count examples
        cursor.execute("SELECT COUNT(*) FROM examples")
        example_count = cursor.fetchone()[0]
        logger.info(f"  Examples: {example_count:,}")
        
    def run(self, clear_existing: bool = True):
        """Run the complete import process."""
        start_time = time.time()
        
        logger.info("=" * 60)
        logger.info("DICTIONARY IMPORT STARTING")
        logger.info("=" * 60)
        
        try:
            # Connect to database
            self.connect()
            
            # Clear existing data if requested
            if clear_existing:
                self.clear_existing_data()
                
            # Import inflections
            inflection_file = Path(__file__).parent.parent / 'data' / 'inflection_lookup.tsv'
            if inflection_file.exists():
                self.import_inflections(inflection_file)
            else:
                logger.warning(f"Inflection file not found: {inflection_file}")
                
            # Import all JSONL files
            self.import_all_jsonl_files()
            
            # Create indexes
            self.create_indexes()
            
            # Verify import
            self.verify_import()
            
            # Print statistics
            elapsed = time.time() - start_time
            logger.info("=" * 60)
            logger.info("IMPORT COMPLETE")
            logger.info("=" * 60)
            logger.info(f"Time elapsed: {elapsed:.2f} seconds")
            logger.info(f"Files processed: {self.stats['total_files']:,}")
            logger.info(f"Total entries: {self.stats['total_entries']:,}")
            logger.info(f"  - Nouns: {self.stats['nouns']:,}")
            logger.info(f"  - Verbs: {self.stats['verbs']:,}")
            logger.info(f"  - Adjectives: {self.stats['adjectives']:,}")
            logger.info(f"  - Adverbs: {self.stats['adverbs']:,}")
            logger.info(f"Inflections: {self.stats['inflections']:,}")
            logger.info(f"Errors: {self.stats['errors']:,}")
            
            if self.stats['total_entries'] > 0:
                rate = self.stats['total_entries'] / elapsed
                logger.info(f"Import rate: {rate:.0f} entries/second")
                
        except Exception as e:
            logger.error(f"Import failed: {e}")
            raise
        finally:
            if self.conn:
                self.conn.close()

def main():
    """Main entry point."""
    # Set up paths
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    
    db_path = project_dir / 'data' / 'dictionary.db'
    data_dir = Path('/mnt/storage/Documents/Dictionary_App_Website/Dictionary_App_Website/DictGenerativeRule_2')
    
    # Check if data directory exists
    if not data_dir.exists():
        logger.error(f"Data directory not found: {data_dir}")
        sys.exit(1)
        
    # Run import
    importer = DictionaryImporter(db_path, data_dir)
    importer.run(clear_existing=True)

if __name__ == '__main__':
    main()