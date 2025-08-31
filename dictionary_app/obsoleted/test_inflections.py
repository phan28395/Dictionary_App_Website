#!/usr/bin/env python3
"""Test inflection lookup functionality with various inflected forms."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.app import DictionaryApp

def test_inflection_searches():
    """Test searching for inflected forms to verify they resolve to lemmas."""
    
    print("Testing Inflection Lookup System")
    print("=" * 50)
    
    # Initialize the app
    app = DictionaryApp()
    
    # Test cases: inflected forms that should resolve to lemmas
    test_cases = [
        # Verb inflections
        ("fought", "fight"),  # past tense of fight
        ("ran", "run"),       # past tense of run
        ("went", "go"),       # past tense of go
        ("was", "be"),        # past tense of be
        ("were", "be"),       # past plural of be
        ("been", "be"),       # past participle of be
        ("going", "go"),      # present participle of go
        ("running", "run"),   # present participle of run
        ("fought", "fight"),  # past participle of fight
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
        ("geese", "goose"),   # plural of goose
        
        # Regular plurals
        ("dogs", "dog"),      # regular plural
        ("cats", "cat"),      # regular plural
        ("houses", "house"),  # regular plural with -es
        ("boxes", "box"),     # regular plural with -es
        
        # Adjective/Adverb forms
        ("better", "good"),   # comparative of good
        ("best", "good"),     # superlative of good
        ("worse", "bad"),     # comparative of bad
        ("worst", "bad"),     # superlative of bad
        ("faster", "fast"),   # comparative of fast
        ("fastest", "fast"),  # superlative of fast
    ]
    
    success_count = 0
    fail_count = 0
    
    for inflected, expected_lemma in test_cases:
        print(f"\nSearching for: '{inflected}' (expecting lemma: '{expected_lemma}')")
        print("-" * 40)
        
        try:
            results = app.search(inflected)
            
            if results:
                # Check if we found the expected lemma
                found_lemmas = set()
                for result in results:
                    lemma = result.get('lemma', '')
                    found_lemmas.add(lemma)
                    
                    if lemma == expected_lemma:
                        print(f"✓ Found: {lemma} ({result.get('pos', 'unknown')})")
                        if result.get('inflection_of'):
                            print(f"  Note: '{inflected}' is an inflected form of '{lemma}'")
                        
                        # Show first meaning
                        meanings = result.get('meanings', [])
                        if meanings:
                            first_meaning = meanings[0]
                            print(f"  Definition: {first_meaning.get('definition', 'N/A')[:100]}...")
                
                if expected_lemma in found_lemmas:
                    success_count += 1
                    print(f"✅ SUCCESS: Found expected lemma '{expected_lemma}'")
                else:
                    fail_count += 1
                    print(f"❌ FAIL: Expected '{expected_lemma}' but found: {found_lemmas}")
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
    print(f"❌ Failed: {fail_count}")
    print(f"Success rate: {(success_count/len(test_cases)*100):.1f}%")
    
    # Test direct lemma search (should still work)
    print("\n" + "=" * 50)
    print("TESTING DIRECT LEMMA SEARCH")
    print("=" * 50)
    
    direct_tests = ["fight", "run", "go", "happy", "good", "child"]
    
    for lemma in direct_tests:
        print(f"\nDirect search for lemma: '{lemma}'")
        results = app.search(lemma)
        if results:
            print(f"✓ Found {len(results)} result(s)")
            for result in results:
                print(f"  - {result['lemma']} ({result.get('pos', 'unknown')})")
        else:
            print(f"✗ No results")

if __name__ == "__main__":
    test_inflection_searches()