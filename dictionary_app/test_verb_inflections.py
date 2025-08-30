#!/usr/bin/env python3
"""Test specific verb inflections."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.database import Database
from core.search import SearchEngine
from core.config import Config

def test_verb_inflections():
    """Test verb inflection lookups."""
    
    # Initialize components
    config = Config()
    db = Database(config)
    search_engine = SearchEngine(db, config)
    
    print("Testing Verb Inflection Lookups")
    print("=" * 50)
    
    # Test specific inflections
    test_cases = [
        ("fought", "fight"),
        ("ran", "run"),
        ("went", "go"),
        ("took", "take"),
        ("taken", "take"),
        ("made", "make"),
        ("making", "make"),
        ("got", "get"),
        ("gotten", "get"),
        ("had", "have"),
        ("having", "have"),
        ("has", "have"),
    ]
    
    for inflected, expected_lemma in test_cases:
        print(f"\nSearching: '{inflected}' → expecting '{expected_lemma}'")
        print("-" * 40)
        
        results = search_engine.search(inflected)
        
        if results:
            found = False
            for result in results:
                if result.lemma == expected_lemma and result.pos == 'verb':
                    found = True
                    print(f"✅ FOUND: {result.lemma} (verb)")
                    if result.meanings:
                        # Show first meaning
                        first = result.meanings[0]
                        if isinstance(first, dict):
                            def_text = first.get('definition', 'N/A')
                        else:
                            def_text = str(first)
                        print(f"   Definition: {def_text[:80]}")
                elif result.lemma == expected_lemma:
                    print(f"⚠️  Found as {result.pos}, not verb")
            
            if not found:
                lemmas = [r.lemma for r in results]
                print(f"❌ NOT FOUND: Got {lemmas} instead")
        else:
            print(f"❌ NO RESULTS")
    
    # Now check if the verbs exist directly
    print("\n" + "=" * 50)
    print("Direct Verb Lookups")
    print("=" * 50)
    
    verbs = ["fight", "run", "go", "take", "make", "get", "have", "do", "be"]
    
    for verb in verbs:
        results = search_engine.search(verb)
        verb_found = False
        
        if results:
            for result in results:
                if result.pos == 'verb':
                    verb_found = True
                    print(f"✓ {verb} exists as verb")
                    break
        
        if not verb_found:
            if results:
                other_pos = [r.pos for r in results]
                print(f"✗ {verb} NOT a verb (found as: {other_pos})")
            else:
                print(f"✗ {verb} NOT in database")

if __name__ == "__main__":
    test_verb_inflections()