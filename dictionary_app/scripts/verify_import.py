#!/usr/bin/env python3
"""
Verify Dictionary Import

Verifies the bulk import was successful and tests functionality.
"""

import sys
import json
import random
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import DictionaryApp

def test_database_counts(app):
    """Test database has expected number of entries"""
    print("🔍 TESTING DATABASE COUNTS")
    print("-" * 40)
    
    try:
        # Total entries
        total = app.database.execute_one("SELECT COUNT(*) FROM dictionary_entries")[0]
        print(f"✅ Total entries: {total:,}")
        
        # Entries by POS
        pos_counts = app.database.execute_all(
            "SELECT pos, COUNT(*) FROM dictionary_entries GROUP BY pos ORDER BY COUNT(*) DESC"
        )
        
        expected_minimums = {
            'noun': 10000,      # Should have most entries
            'adjective': 5000,  # Should have many entries
            'verb': 1000,       # Should have some entries
            'adverb': 100       # Should have fewer entries
        }
        
        for pos, count in pos_counts:
            expected = expected_minimums.get(pos, 0)
            status = "✅" if count >= expected else "⚠️"
            print(f"{status} {pos}: {count:,} (expected ≥{expected:,})")
            
        return total > 10000
        
    except Exception as e:
        print(f"❌ Database count test failed: {e}")
        return False

def test_search_functionality(app):
    """Test search works with new data"""
    print("\n🔍 TESTING SEARCH FUNCTIONALITY")
    print("-" * 40)
    
    # Test common words that should exist
    test_words = ['good', 'bad', 'big', 'small', 'fast', 'slow', 'happy', 'sad']
    
    found_count = 0
    for word in test_words:
        results = app.search(word)
        if results:
            result = results[0]
            print(f"✅ '{word}' → {result.lemma} ({result.pos})")
            found_count += 1
        else:
            print(f"❌ '{word}' not found")
            
    success_rate = found_count / len(test_words)
    print(f"\n📊 Search success rate: {success_rate:.1%} ({found_count}/{len(test_words)})")
    
    return success_rate >= 0.5

def test_pos_specific_data(app):
    """Test POS-specific data is properly stored"""
    print("\n🔍 TESTING POS-SPECIFIC DATA")
    print("-" * 40)
    
    try:
        # Test adjective with specific fields
        adj_results = app.database.execute_all(
            "SELECT lemma, pos_specific_data FROM dictionary_entries WHERE pos = 'adjective' AND pos_specific_data IS NOT NULL LIMIT 3"
        )
        
        adjective_test_passed = False
        for lemma, pos_data_json in adj_results:
            if pos_data_json:
                pos_data = json.loads(pos_data_json)
                expected_fields = ['frequency_meaning', 'gradability', 'semantic_type', 'polarity']
                has_fields = [field for field in expected_fields if field in pos_data]
                
                if len(has_fields) >= 2:
                    print(f"✅ Adjective '{lemma}' has fields: {', '.join(has_fields)}")
                    adjective_test_passed = True
                    break
                    
        if not adjective_test_passed:
            print("⚠️ No adjectives found with expected POS-specific fields")
            
        return adjective_test_passed
        
    except Exception as e:
        print(f"❌ POS-specific data test failed: {e}")
        return False

def test_random_samples(app):
    """Test random sample of entries"""
    print("\n🔍 TESTING RANDOM SAMPLES")
    print("-" * 40)
    
    try:
        # Get random entries from each POS
        for pos in ['noun', 'verb', 'adjective', 'adverb']:
            results = app.database.execute_all(
                f"SELECT lemma, meanings FROM dictionary_entries WHERE pos = ? ORDER BY RANDOM() LIMIT 2",
                (pos,)
            )
            
            if results:
                for lemma, meanings_json in results:
                    meanings = json.loads(meanings_json) if meanings_json else []
                    meaning_count = len(meanings)
                    first_meaning = meanings[0] if meanings else "No meanings"
                    print(f"✅ {pos.title()}: '{lemma}' ({meaning_count} meanings)")
                    print(f"   → {first_meaning}")
            else:
                print(f"❌ No {pos} entries found")
                
        return True
        
    except Exception as e:
        print(f"❌ Random sample test failed: {e}")
        return False

def test_database_integrity(app):
    """Test database integrity"""
    print("\n🔍 TESTING DATABASE INTEGRITY")
    print("-" * 40)
    
    try:
        # Check for duplicate lemma+pos combinations
        duplicates = app.database.execute_one(
            "SELECT COUNT(*) FROM (SELECT lemma, pos, COUNT(*) as cnt FROM dictionary_entries GROUP BY lemma, pos HAVING cnt > 1)"
        )[0]
        
        if duplicates == 0:
            print("✅ No duplicate lemma+pos combinations")
        else:
            print(f"⚠️ Found {duplicates} duplicate lemma+pos combinations")
            
        # Check for entries with no meanings
        no_meanings = app.database.execute_one(
            "SELECT COUNT(*) FROM dictionary_entries WHERE meanings IS NULL OR meanings = '[]'"
        )[0]
        
        if no_meanings == 0:
            print("✅ All entries have meanings")
        else:
            print(f"⚠️ Found {no_meanings} entries without meanings")
            
        # Check JSON validity
        invalid_json = app.database.execute_one(
            """SELECT COUNT(*) FROM dictionary_entries 
               WHERE (meanings IS NOT NULL AND json_valid(meanings) = 0)
                  OR (definitions IS NOT NULL AND json_valid(definitions) = 0)
                  OR (examples IS NOT NULL AND json_valid(examples) = 0)"""
        )[0]
        
        if invalid_json == 0:
            print("✅ All JSON fields are valid")
        else:
            print(f"⚠️ Found {invalid_json} entries with invalid JSON")
            
        return duplicates == 0 and no_meanings == 0 and invalid_json == 0
        
    except Exception as e:
        print(f"❌ Database integrity test failed: {e}")
        return False

def main():
    """Main verification"""
    print("=" * 50)
    print("DICTIONARY IMPORT VERIFICATION")
    print("=" * 50)
    
    # Initialize app
    print("📚 Initializing Dictionary App...")
    app = DictionaryApp()
    if not app.initialize():
        print("❌ Failed to initialize app")
        sys.exit(1)
    print("✅ App initialized successfully\n")
    
    # Run tests
    tests = [
        ("Database Counts", test_database_counts),
        ("Search Functionality", test_search_functionality), 
        ("POS-Specific Data", test_pos_specific_data),
        ("Random Samples", test_random_samples),
        ("Database Integrity", test_database_integrity)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func(app):
                passed_tests += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    # Final results
    print("\n" + "=" * 50)
    print("VERIFICATION RESULTS")
    print("=" * 50)
    print(f"Tests passed: {passed_tests}/{total_tests}")
    print(f"Success rate: {passed_tests/total_tests:.1%}")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED - Dictionary import is successful!")
    elif passed_tests >= total_tests * 0.8:
        print("✅ MOSTLY SUCCESSFUL - Dictionary import looks good with minor issues")
    else:
        print("⚠️ ISSUES DETECTED - Dictionary import may have problems")
        
    # Cleanup
    app.shutdown()

if __name__ == '__main__':
    main()