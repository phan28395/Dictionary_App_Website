#!/usr/bin/env python3
"""Test inflection lookup functionality with various inflected forms."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.database import Database
from core.search import SearchEngine
from core.config import Config
import logging

def test_inflection_searches():
    """Test searching for inflected forms to verify they resolve to lemmas."""
    
    print("Testing Inflection Lookup System")
    print("=" * 50)
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize components directly
    config = Config()
    db = Database(config)
    search_engine = SearchEngine(db, config)
    
    # Test cases: inflected forms that should resolve to lemmas
    test_cases = [
        # Verb inflections
        ("fought", "fight"),  # past tense of fight
        ("ran", "run"),       # past tense of run
        ("went", "go"),       # past tense of go
        ("was", "be"),        # past tense of be
        ("going", "go"),      # present participle of go
        ("running", "run"),   # present participle of run
        ("taken", "take"),    # past participle of take
        ("wrote", "write"),   # past tense of write
        ("written", "write"), # past participle of write
        
        # Noun inflections
        ("children", "child"), # plural of child
        ("men", "man"),       # plural of man
        ("women", "woman"),   # plural of woman
        ("feet", "foot"),     # plural of foot
        ("teeth", "tooth"),   # plural of tooth
        ("mice", "mouse"),    # plural of mouse
        
        # Regular plurals
        ("dogs", "dog"),      # regular plural
        ("cats", "cat"),      # regular plural
        ("houses", "house"),  # regular plural with -es
        
        # Comparative/Superlative
        ("better", "good"),   # comparative (also exists as its own lemma)
        ("faster", "fast"),   # comparative of fast
    ]
    
    success_count = 0
    fail_count = 0
    partial_count = 0
    
    for inflected, expected_lemma in test_cases:
        print(f"\nSearching for: '{inflected}' (expecting lemma: '{expected_lemma}')")
        print("-" * 40)
        
        try:
            results = search_engine.search(inflected)
            
            if results:
                # Check if we found the expected lemma
                found_lemmas = set()
                found_expected = False
                
                for result in results:
                    lemma = result.get('lemma', '')
                    found_lemmas.add(lemma)
                    
                    if lemma == expected_lemma:
                        found_expected = True
                        print(f"✓ Found: {lemma} ({result.get('pos', 'unknown')})")
                        if result.get('inflection_of'):
                            print(f"  Note: '{inflected}' is an inflected form of '{lemma}'")
                        
                        # Show first meaning
                        meanings = result.get('meanings', [])
                        if meanings:
                            first_meaning = meanings[0]
                            definition = first_meaning.get('definition', 'N/A')
                            if len(definition) > 100:
                                definition = definition[:100] + "..."
                            print(f"  Definition: {definition}")
                
                if found_expected:
                    success_count += 1
                    print(f"✅ SUCCESS: Found expected lemma '{expected_lemma}'")
                elif found_lemmas:
                    # We found something, just not what we expected
                    partial_count += 1
                    print(f"⚠️  PARTIAL: Found {found_lemmas} instead of '{expected_lemma}'")
                    # This might be OK for words like "better" which is both an inflection and a lemma
                else:
                    fail_count += 1
                    print(f"❌ FAIL: No lemmas found")
            else:
                fail_count += 1
                print(f"❌ FAIL: No results found for '{inflected}'")
                
        except Exception as e:
            fail_count += 1
            print(f"❌ ERROR: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("INFLECTION LOOKUP TEST SUMMARY")
    print("=" * 50)
    print(f"Total tests: {len(test_cases)}")
    print(f"✅ Successful: {success_count}")
    print(f"⚠️  Partial matches: {partial_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"Success rate: {(success_count/len(test_cases)*100):.1f}%")
    
    # Test direct lemma search (should still work)
    print("\n" + "=" * 50)
    print("TESTING DIRECT LEMMA SEARCH")
    print("=" * 50)
    
    direct_tests = ["fight", "run", "go", "happy", "good", "child", "house", "dog"]
    
    for lemma in direct_tests:
        print(f"\nDirect search for lemma: '{lemma}'")
        results = search_engine.search(lemma)
        if results:
            print(f"✓ Found {len(results)} result(s)")
            for result in results[:2]:  # Show max 2 results
                print(f"  - {result['lemma']} ({result.get('pos', 'unknown')})")
                meanings = result.get('meanings', [])
                if meanings:
                    definition = meanings[0].get('definition', 'N/A')
                    if len(definition) > 60:
                        definition = definition[:60] + "..."
                    print(f"    Def: {definition}")
        else:
            print(f"✗ No results")

if __name__ == "__main__":
    test_inflection_searches()