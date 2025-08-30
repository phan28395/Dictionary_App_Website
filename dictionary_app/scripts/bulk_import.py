#!/usr/bin/env python3
"""
Bulk Import System for Full Dictionary Dataset

Imports from DictGenerativeRule_2/ with all POS types:
- Adjectives: ~7,900 entries (159 files)
- Nouns: ~17,378 entries (348 files) 
- Verbs: ~90 files
- Adverbs: ~7 files

Features:
- Progress tracking with percentage
- Batch processing in chunks
- Error logging and recovery
- POS-specific field handling
- Duplicate detection
"""

import sys
import json
import sqlite3
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Generator
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import DictionaryApp

# Configure logging
log_dir = Path(__file__).parent.parent / 'logs'
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'bulk_import.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BulkImporter:
    """Bulk importer for full dictionary dataset"""
    
    def __init__(self):
        self.app = None
        self.data_dir = Path(__file__).parent.parent.parent / 'DictGenerativeRule_2'
        self.stats = {
            'files_processed': 0,
            'total_files': 0,
            'entries_imported': 0,
            'entries_skipped': 0,
            'errors': 0,
            'start_time': None
        }
        self.batch_size = 1000
        self.batch_buffer = []
        
    def initialize(self):
        """Initialize dictionary app and database"""
        logger.info("Initializing Dictionary App...")
        self.app = DictionaryApp()
        if not self.app.initialize():
            raise Exception("Failed to initialize Dictionary App")
        logger.info("Dictionary App initialized successfully")
        
        # Initialize database schema if needed
        self._ensure_schema_exists()
        
    def get_pos_files(self, pos_type: str) -> List[Path]:
        """Get all JSONL files for a specific POS type"""
        pos_dirs = {
            'adjective': 'Adjective_Generator/Adjective_Json',
            'noun': 'Noun_Generator/Noun_Json', 
            'verb': 'Verb_Generator',
            'adverb': 'Adverb_Generator/Adverbs_Json'
        }
        
        pos_dir = self.data_dir / pos_dirs[pos_type]
        if not pos_dir.exists():
            logger.warning(f"POS directory not found: {pos_dir}")
            return []
            
        # Get all .jsonl files
        files = list(pos_dir.glob('*.jsonl'))
        logger.info(f"Found {len(files)} {pos_type} files")
        return sorted(files)
        
    def count_total_files(self) -> int:
        """Count total JSONL files across all POS types"""
        total = 0
        for pos in ['adjective', 'noun', 'verb', 'adverb']:
            files = self.get_pos_files(pos)
            total += len(files)
        return total
        
    def read_jsonl_entries(self, file_path: Path) -> Generator[Dict[str, Any], None, None]:
        """Read entries from a JSONL file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                        
                    try:
                        entry = json.loads(line)
                        yield entry
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON decode error in {file_path}:{line_num}: {e}")
                        self.stats['errors'] += 1
                        
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            self.stats['errors'] += 1
            
    def determine_pos_from_path(self, file_path: Path) -> str:
        """Determine POS type from file path"""
        path_str = str(file_path).lower()
        if 'adjective' in path_str:
            return 'adjective'
        elif 'noun' in path_str:
            return 'noun'
        elif 'verb' in path_str:
            return 'verb'
        elif 'adverb' in path_str:
            return 'adverb'
        else:
            logger.warning(f"Cannot determine POS for file: {file_path}")
            return 'unknown'
            
    def validate_entry(self, entry: Dict[str, Any], pos: str) -> bool:
        """Validate entry has required fields for POS type"""
        required_fields = ['lemma', 'meanings', 'definitions', 'examples']
        
        # Check basic required fields
        for field in required_fields:
            if field not in entry:
                logger.warning(f"Missing required field '{field}' in entry: {entry.get('lemma', 'unknown')}")
                return False
                
        # POS-specific validation
        if pos == 'adjective':
            adj_fields = ['frequency_meaning', 'syntactic_position', 'gradability', 
                         'semantic_type', 'polarity', 'antonyms', 'typical_modifiers', 'key_collocates']
            missing = [f for f in adj_fields if f not in entry]
            if missing:
                logger.warning(f"Missing adjective fields {missing} in: {entry.get('lemma')}")
                return False
                
        # Validate frequency_meaning sums to 1.0 (approximately)
        if 'frequency_meaning' in entry:
            total = sum(entry['frequency_meaning'])
            if abs(total - 1.0) > 0.01:
                logger.warning(f"frequency_meaning sum {total} != 1.0 for: {entry.get('lemma')}")
                
        return True
        
    def prepare_entry_for_db(self, entry: Dict[str, Any], pos: str) -> Dict[str, Any]:
        """Prepare entry data for database insertion"""
        # Basic fields matching current schema
        db_entry = {
            'lemma': entry['lemma'],
            'pos': pos,
            'meanings': json.dumps(entry['meanings']),
            'definitions': json.dumps(entry['definitions']),
            'examples': json.dumps(entry['examples']),
            'frequency_meaning': json.dumps(entry.get('frequency_meaning', [1.0]))  # Default to single meaning
        }
        
        return db_entry
        
    def flush_batch(self):
        """Insert current batch into database"""
        if not self.batch_buffer:
            return
            
        try:
            # Insert into dictionary_entries table
            query = '''
                INSERT OR IGNORE INTO dictionary_entries 
                (lemma, pos, meanings, definitions, examples, frequency_meaning)
                VALUES (?, ?, ?, ?, ?, ?)
            '''
            
            batch_data = [
                (
                    entry['lemma'],
                    entry['pos'],
                    entry['meanings'],
                    entry['definitions'],
                    entry['examples'],
                    entry['frequency_meaning']
                )
                for entry in self.batch_buffer
            ]
            
            self.app.database.execute_many(query, batch_data)
            
            imported_count = len(batch_data)
            self.stats['entries_imported'] += imported_count
            logger.info(f"Imported batch of {imported_count} entries")
            
        except Exception as e:
            logger.error(f"Failed to import batch: {e}")
            self.stats['errors'] += 1
            
        finally:
            self.batch_buffer.clear()
            
    def process_file(self, file_path: Path, pos: str):
        """Process a single JSONL file"""
        logger.info(f"Processing {pos} file: {file_path.name}")
        
        entries_in_file = 0
        for entry in self.read_jsonl_entries(file_path):
            if not self.validate_entry(entry, pos):
                self.stats['entries_skipped'] += 1
                continue
                
            db_entry = self.prepare_entry_for_db(entry, pos)
            self.batch_buffer.append(db_entry)
            entries_in_file += 1
            
            # Flush batch if full
            if len(self.batch_buffer) >= self.batch_size:
                self.flush_batch()
                
        logger.info(f"Processed {entries_in_file} entries from {file_path.name}")
        self.stats['files_processed'] += 1
        
        # Progress reporting
        if self.stats['total_files'] > 0:
            progress = (self.stats['files_processed'] / self.stats['total_files']) * 100
            logger.info(f"Progress: {progress:.1f}% ({self.stats['files_processed']}/{self.stats['total_files']} files)")
            
    def import_pos_type(self, pos_type: str):
        """Import all files for a specific POS type"""
        logger.info(f"Starting import of {pos_type} entries...")
        
        files = self.get_pos_files(pos_type)
        if not files:
            logger.warning(f"No {pos_type} files found")
            return
            
        for file_path in files:
            try:
                self.process_file(file_path, pos_type)
            except Exception as e:
                logger.error(f"Failed to process file {file_path}: {e}")
                self.stats['errors'] += 1
                
        # Flush remaining entries
        if self.batch_buffer:
            self.flush_batch()
            
        logger.info(f"Completed {pos_type} import")
        
    def import_all(self):
        """Import all dictionary data"""
        self.stats['start_time'] = time.time()
        self.stats['total_files'] = self.count_total_files()
        
        logger.info(f"Starting bulk import of {self.stats['total_files']} files...")
        
        # Import in order of decreasing complexity
        pos_types = ['adjective', 'noun', 'verb', 'adverb']
        
        for pos_type in pos_types:
            self.import_pos_type(pos_type)
            
        self.print_final_stats()
        
    def _ensure_schema_exists(self):
        """Ensure database schema exists"""
        try:
            # Test if dictionary_entries table exists
            self.app.database.execute_one("SELECT COUNT(*) FROM dictionary_entries LIMIT 1")
            logger.info("Database schema already exists")
        except Exception:
            logger.error("Database schema does not exist. Please initialize the app first to create the database schema.")
            raise Exception("Database not initialized. Run the main app first to create the schema.")

    def print_final_stats(self):
        """Print final import statistics"""
        start_time = self.stats['start_time'] or time.time() 
        elapsed = time.time() - start_time
        
        logger.info("="*50)
        logger.info("BULK IMPORT COMPLETED")
        logger.info("="*50)
        logger.info(f"Files processed: {self.stats['files_processed']}")
        logger.info(f"Entries imported: {self.stats['entries_imported']:,}")
        logger.info(f"Entries skipped: {self.stats['entries_skipped']:,}")
        logger.info(f"Errors: {self.stats['errors']}")
        logger.info(f"Time elapsed: {elapsed:.1f} seconds")
        logger.info(f"Import rate: {self.stats['entries_imported']/elapsed:.1f} entries/second")
        
        # Database statistics
        try:
            total_entries = self.app.database.execute_one(
                "SELECT COUNT(*) FROM dictionary_entries"
            )[0]
            
            pos_counts = self.app.database.execute_all(
                "SELECT pos, COUNT(*) FROM dictionary_entries GROUP BY pos ORDER BY COUNT(*) DESC"
            )
            
            logger.info(f"Total entries in database: {total_entries:,}")
            logger.info("Entries by POS:")
            for pos, count in pos_counts:
                logger.info(f"  {pos}: {count:,}")
                
        except Exception as e:
            logger.error(f"Failed to get database statistics: {e}")
            
    def shutdown(self):
        """Cleanup and shutdown"""
        if self.app:
            self.app.shutdown()


def main():
    """Main entry point"""
    importer = BulkImporter()
    
    try:
        importer.initialize()
        importer.import_all()
    except KeyboardInterrupt:
        logger.info("Import cancelled by user")
    except Exception as e:
        logger.error(f"Import failed: {e}")
        sys.exit(1)
    finally:
        importer.shutdown()
        
    logger.info("Bulk import process completed!")


if __name__ == '__main__':
    main()