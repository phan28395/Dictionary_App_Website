#!/usr/bin/env python3
"""
Test dictionary with full dataset
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.app import DictionaryApp

def test_full_dataset():
    """Test with complete dictionary data."""
    print("=" * 60)
    print("TESTING WITH FULL DICTIONARY DATASET")
    print("=" * 60)
    
    # Initialize app
    app = DictionaryApp()
    app.initialize()
    
    # Test various searches
    test_words = [
        "happy",      # Common adjective
        "run",        # Common verb
        "house",      # Common noun
        "quickly",    # Adverb
        "went",       # Inflected form (go)
        "better",     # Comparative form
        "children",   # Plural noun
        "beautiful",  # Adjective
        "computer",   # Modern noun
        "analyze"     # Verb
    ]
    
    print("\n1. Testing word searches:")
    for word in test_words:
        results = app.search(word)
        if results:
            result = results[0]
            print(f"   ✅ {word:12} → {result.lemma:12} ({result.pos}) - {len(results)} result(s)")
        else:
            print(f"   ❌ {word:12} → No results found")
            
    # Test inflection lookup
    print("\n2. Testing inflection mappings:")
    inflected_forms = ["went", "going", "better", "best", "children", "ran", "running"]
    
    for form in inflected_forms:
        results = app.search(form)
        if results:
            result = results[0]
            if result.inflected_from:
                print(f"   ✅ {form:12} → {result.lemma:12} (inflected from: {result.inflected_from})")
            else:
                print(f"   ✅ {form:12} → {result.lemma:12} (direct match)")
        else:
            print(f"   ❌ {form:12} → Not found")
            
    # Test suggestions
    print("\n3. Testing autocomplete suggestions:")
    prefixes = ["hap", "com", "bea", "ana"]
    
    for prefix in prefixes:
        suggestions = app.get_suggestions(prefix, limit=5)
        if suggestions:
            print(f"   ✅ '{prefix}' → {', '.join(suggestions[:5])}")
        else:
            print(f"   ❌ '{prefix}' → No suggestions")
            
    # Get database statistics
    print("\n4. Database Statistics:")
    conn = app.db.get_connection()
    cursor = conn.cursor()
    
    # Total entries
    cursor.execute("SELECT COUNT(*) FROM dictionary_entries")
    total = cursor.fetchone()[0]
    print(f"   Total entries: {total:,}")
    
    # By POS
    cursor.execute("SELECT pos, COUNT(*) FROM dictionary_entries GROUP BY pos ORDER BY COUNT(*) DESC")
    for pos, count in cursor.fetchall():
        print(f"   - {pos:10}: {count:,}")
        
    # Inflections
    cursor.execute("SELECT COUNT(*) FROM inflection_lookup")
    inflections = cursor.fetchone()[0]
    print(f"   Inflections: {inflections:,}")
    
    # Random words
    print("\n5. Random word samples:")
    for _ in range(5):
        word = app.get_random_word()
        if word:
            meanings = word.meanings[:2] if word.meanings else []
            meaning_preview = meanings[0].definition[:50] + "..." if meanings else "No definition"
            print(f"   • {word.lemma} ({word.pos}): {meaning_preview}")
            
    print("\n" + "=" * 60)
    print("FULL DATASET TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_full_dataset()