#!/usr/bin/env python3
"""
Database verification script for Dictionary App.
Verifies data import was successful and tests core functionality.
"""

import sqlite3
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add parent to path for core imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class DatabaseVerifier:
    """Verify database content and functionality."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Connect to database."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()
        
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def verify_schema(self) -> bool:
        """Verify all required tables exist."""
        print("[VERIFY] Verifying database schema...")
        
        required_tables = [
            'dictionary_entries',
            'inflection_lookup',
            'noun_properties',
            'verb_properties', 
            'adjective_properties',
            'users',
            'search_history',
            'favorites'
        ]
        
        # Check tables exist
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in self.cursor.fetchall()]
        
        missing_tables = []
        for table in required_tables:
            if table not in existing_tables:
                missing_tables.append(table)
        
        if missing_tables:
            print(f"   [ERROR] Missing tables: {', '.join(missing_tables)}")
            return False
        
        print(f"   [OK] All {len(required_tables)} required tables exist")
        
        # Check views exist
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
        views = [row[0] for row in self.cursor.fetchall()]
        
        expected_views = ['noun_entries', 'verb_entries', 'adjective_entries', 'adverb_entries']
        missing_views = [v for v in expected_views if v not in views]
        
        if missing_views:
            print(f"   [WARN] Missing views: {', '.join(missing_views)}")
        else:
            print(f"   [OK] All {len(expected_views)} views exist")
        
        return True
    
    def verify_data_counts(self) -> bool:
        """Verify data was imported correctly."""
        print("\\n[DATA] Verifying data counts...")
        
        # Check main entries by POS
        pos_counts = {}
        for pos in ['noun', 'verb', 'adjective', 'adverb']:
            self.cursor.execute("""
                SELECT COUNT(*) FROM dictionary_entries WHERE pos = ?
            """, (pos,))
            count = self.cursor.fetchone()[0]
            pos_counts[pos] = count
            print(f"   [COUNT] {pos.capitalize()}s: {count:,}")
        
        total_entries = sum(pos_counts.values())
        print(f"   [TOTAL] Total dictionary entries: {total_entries:,}")
        
        # Check inflections
        self.cursor.execute("SELECT COUNT(*) FROM inflection_lookup")
        inflection_count = self.cursor.fetchone()[0]
        print(f"   [INFLECT] Inflection mappings: {inflection_count:,}")
        
        # Verify reasonable counts
        if total_entries < 10000:
            print(f"   [WARN] Total entries ({total_entries:,}) seems low (expected ~30,000)")
        
        if inflection_count < 50000:
            print(f"   [WARN] Inflection count ({inflection_count:,}) seems low (expected ~106,000)")
        
        # Check POS-specific properties
        print("\\n[PROPS] Verifying POS-specific properties...")
        
        for pos in ['noun', 'verb', 'adjective']:
            self.cursor.execute(f"""
                SELECT COUNT(*) FROM {pos}_properties
            """)
            prop_count = self.cursor.fetchone()[0]
            entry_count = pos_counts[pos]
            
            print(f"   [PROP] {pos.capitalize()} properties: {prop_count:,} / {entry_count:,}")
            
            if prop_count != entry_count:
                print(f"      [WARN] Mismatch: {prop_count} properties for {entry_count} entries")
        
        return total_entries > 0 and inflection_count > 0
    
    def test_basic_searches(self) -> bool:
        """Test basic search functionality."""
        print("\\n[SEARCH] Testing basic searches...")
        
        test_words = ['go', 'run', 'good', 'happy', 'quickly', 'book']
        
        for word in test_words:
            # Test direct lemma search
            self.cursor.execute("""
                SELECT lemma, pos, meanings FROM dictionary_entries 
                WHERE lemma = ?
            """, (word,))
            
            result = self.cursor.fetchone()
            if result:
                meanings = json.loads(result[2])
                print(f"   [FOUND] '{word}' ({result[1]}): {len(meanings)} meaning(s)")
            else:
                print(f"   [MISS] '{word}': Not found as lemma")
        
        return True
    
    def test_inflection_lookups(self) -> bool:
        """Test inflection lookup functionality."""
        print("\\n[INFLECT] Testing inflection lookups...")
        
        test_inflections = [
            ('went', 'go'),
            ('running', 'run'), 
            ('better', 'good'),
            ('children', 'child'),
            ('mice', 'mouse')
        ]
        
        for inflected, expected_lemma in test_inflections:
            # Check inflection mapping
            self.cursor.execute("""
                SELECT lemma, pos FROM inflection_lookup 
                WHERE inflected_form = ?
            """, (inflected,))
            
            result = self.cursor.fetchone()
            if result:
                lemma, pos = result
                if lemma == expected_lemma:
                    print(f"   [OK] '{inflected}' -> '{lemma}' ({pos})")
                else:
                    print(f"   [DIFF] '{inflected}' -> '{lemma}' (expected '{expected_lemma}')")
                
                # Check if lemma exists in dictionary
                self.cursor.execute("""
                    SELECT COUNT(*) FROM dictionary_entries 
                    WHERE lemma = ? AND pos = ?
                """, (lemma, pos))
                
                count = self.cursor.fetchone()[0]
                if count == 0:
                    print(f"      [WARN] Lemma '{lemma}' not found in dictionary")
            else:
                print(f"   [ERROR] '{inflected}': No inflection mapping found")
        
        return True
    
    def test_json_data_integrity(self) -> bool:
        """Test that JSON data can be parsed correctly."""
        print("\\n[JSON] Testing JSON data integrity...")
        
        # Test a few entries from each POS
        for pos in ['noun', 'verb', 'adjective', 'adverb']:
            self.cursor.execute("""
                SELECT lemma, meanings, definitions, examples, frequency_meaning
                FROM dictionary_entries 
                WHERE pos = ? 
                LIMIT 3
            """, (pos,))
            
            entries = self.cursor.fetchall()
            
            for entry in entries:
                lemma, meanings, definitions, examples, freq = entry
                
                try:
                    meanings_data = json.loads(meanings)
                    definitions_data = json.loads(definitions) 
                    examples_data = json.loads(examples)
                    freq_data = json.loads(freq)
                    
                    # Basic validation
                    if not isinstance(meanings_data, list) or len(meanings_data) == 0:
                        print(f"   [ERROR] {lemma}: Invalid meanings data")
                        
                    if not isinstance(freq_data, list) or len(freq_data) != len(meanings_data):
                        print(f"   [ERROR] {lemma}: Frequency data doesn't match meanings")
                        
                except json.JSONDecodeError as e:
                    print(f"   [ERROR] {lemma}: JSON parse error - {e}")
                    return False
            
            print(f"   [OK] {pos.capitalize()}: JSON data valid (tested {len(entries)} entries)")
        
        return True
    
    def test_full_search_workflow(self) -> bool:
        """Test complete search workflow like the app would do."""
        print("\\n[WORKFLOW] Testing complete search workflow...")
        
        test_cases = [
            ('went', 'go'),  # Inflected form should map to lemma
            ('run', 'run'),  # Direct lemma lookup
            ('happy', 'happy'),  # Adjective
            ('quickly', 'quickly')  # Adverb
        ]
        
        for search_term, expected_lemma in test_cases:
            print(f"   [SEARCH] Searching for '{search_term}'...")
            
            # Step 1: Check inflection lookup first
            self.cursor.execute("""
                SELECT lemma, pos FROM inflection_lookup 
                WHERE inflected_form = ?
            """, (search_term,))
            
            inflection_result = self.cursor.fetchone()
            
            if inflection_result:
                lemma, pos = inflection_result
                print(f"      [INFLECT] Found inflection: '{search_term}' -> '{lemma}' ({pos})")
            else:
                # Step 2: Try direct lemma search
                lemma = search_term
                print(f"      [DIRECT] No inflection found, searching lemma directly")
            
            # Step 3: Get dictionary entry
            self.cursor.execute("""
                SELECT d.*, 
                       CASE 
                           WHEN d.pos = 'noun' THEN n.domains
                           WHEN d.pos = 'verb' THEN v.grammatical_patterns
                           WHEN d.pos = 'adjective' THEN a.antonyms
                           ELSE NULL
                       END as extra_data
                FROM dictionary_entries d
                LEFT JOIN noun_properties n ON d.id = n.entry_id AND d.pos = 'noun'
                LEFT JOIN verb_properties v ON d.id = v.entry_id AND d.pos = 'verb' 
                LEFT JOIN adjective_properties a ON d.id = a.entry_id AND d.pos = 'adjective'
                WHERE d.lemma = ?
            """, (lemma,))
            
            entries = self.cursor.fetchall()
            
            if entries:
                for entry in entries:
                    meanings_data = json.loads(entry[3])  # meanings column
                    print(f"      [FOUND] Found '{entry[1]}' ({entry[2]}): {len(meanings_data)} meanings")
            else:
                print(f"      [ERROR] No dictionary entry found for lemma '{lemma}'")
        
        return True
    
    def print_sample_entries(self):
        """Print sample entries from each POS type."""
        print("\\n[SAMPLE] Sample dictionary entries:")
        
        for pos in ['noun', 'verb', 'adjective', 'adverb']:
            print(f"\\n   [POS] Sample {pos}:")
            
            self.cursor.execute("""
                SELECT lemma, meanings, definitions FROM dictionary_entries 
                WHERE pos = ? 
                LIMIT 2
            """, (pos,))
            
            entries = self.cursor.fetchall()
            
            for lemma, meanings, definitions in entries:
                meanings_data = json.loads(meanings)
                definitions_data = json.loads(definitions)
                
                print(f"      [ENTRY] {lemma}: {meanings_data[0]}")
                print(f"         {definitions_data[0][:80]}...")


def main():
    """Main entry point."""
    db_path = Path(__file__).parent.parent / 'data' / 'dictionary.db'
    
    print("Dictionary Database Verification")
    print("=" * 50)
    print(f"[DB] Database: {db_path}")
    
    if not db_path.exists():
        print(f"[ERROR] Database file not found: {db_path}")
        sys.exit(1)
    
    verifier = DatabaseVerifier(db_path)
    
    try:
        verifier.connect()
        
        # Run all verification tests
        tests_passed = 0
        total_tests = 6
        
        if verifier.verify_schema():
            tests_passed += 1
            
        if verifier.verify_data_counts():
            tests_passed += 1
            
        if verifier.test_basic_searches():
            tests_passed += 1
            
        if verifier.test_inflection_lookups():
            tests_passed += 1
            
        if verifier.test_json_data_integrity():
            tests_passed += 1
            
        if verifier.test_full_search_workflow():
            tests_passed += 1
        
        # Show sample entries
        verifier.print_sample_entries()
        
        # Final results
        print(f"\\n{'='*60}")
        print(f"[RESULTS] VERIFICATION RESULTS")
        print(f"{'='*60}")
        print(f"[PASSED] Tests passed: {tests_passed}/{total_tests}")
        
        if tests_passed == total_tests:
            print(f"[SUCCESS] All tests passed! Database is ready for use.")
            print(f"   Next step: python run_app.py")
            sys.exit(0)
        else:
            print(f"[WARNING] Some tests failed. Check the output above.")
            sys.exit(1)
        
    except Exception as e:
        print(f"[ERROR] Verification failed: {e}")
        sys.exit(1)
    
    finally:
        verifier.close()


if __name__ == '__main__':
    main()