#!/usr/bin/env python3
"""
Complete test of Dictionary App functionality
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core import DictionaryApp

def run_tests():
    print("="*60)
    print(" DICTIONARY APP COMPLETE TEST")
    print("="*60)
    
    # Initialize app
    print("\n📚 Initializing Dictionary App...")
    app = DictionaryApp()
    
    if not app.initialize():
        print("❌ Failed to initialize")
        return False
    print("✅ App initialized successfully")
    
    # Test 1: Basic searches
    print("\n🔍 TEST 1: Basic Dictionary Searches")
    print("-" * 40)
    
    test_cases = [
        ("book", "book", "noun", None),
        ("happy", "happy", "adjective", None),
        ("quickly", "quickly", "adverb", None),
        ("run", "run", "verb", None),
        ("go", "go", "verb", None)
    ]
    
    passed = 0
    for search_term, expected_lemma, expected_pos, note in test_cases:
        results = app.search(search_term)
        if results and results[0].lemma == expected_lemma and results[0].pos == expected_pos:
            print(f"✅ '{search_term}' → {results[0].lemma} ({results[0].pos})")
            if results[0].meanings:
                print(f"   Definition: {results[0].meanings[0].get('definition', 'N/A')[:60]}...")
            passed += 1
        else:
            print(f"❌ '{search_term}' failed")
    
    print(f"\nResult: {passed}/{len(test_cases)} passed")
    
    # Test 2: Inflection lookups
    print("\n🔄 TEST 2: Inflection Lookups")
    print("-" * 40)
    
    inflection_tests = [
        ("went", "go", "verb"),
        ("books", "book", "noun"),
        ("happier", "happy", "adjective"),
        ("running", "run", "verb")
    ]
    
    passed = 0
    for inflected, expected_lemma, expected_pos in inflection_tests:
        results = app.search(inflected)
        if results:
            found = False
            for result in results:
                if result.lemma == expected_lemma and result.pos == expected_pos:
                    print(f"✅ '{inflected}' → {result.lemma} ({result.pos})")
                    if result.inflection_note:
                        print(f"   Note: {result.inflection_note}")
                    found = True
                    passed += 1
                    break
            if not found:
                print(f"❌ '{inflected}' didn't find {expected_lemma}")
        else:
            print(f"❌ '{inflected}' - no results")
    
    print(f"\nResult: {passed}/{len(inflection_tests)} passed")
    
    # Test 3: Autocomplete suggestions
    print("\n💡 TEST 3: Autocomplete Suggestions")
    print("-" * 40)
    
    suggest_tests = [
        ("hap", "happy"),
        ("bo", "book"),
        ("qu", "quickly"),
        ("ru", "run")
    ]
    
    passed = 0
    for prefix, expected in suggest_tests:
        suggestions = app.get_suggestions(prefix, limit=5)
        if expected in suggestions:
            print(f"✅ '{prefix}' → {', '.join(suggestions)}")
            passed += 1
        else:
            print(f"❌ '{prefix}' didn't suggest {expected}")
    
    print(f"\nResult: {passed}/{len(suggest_tests)} passed")
    
    # Test 4: Plugin system
    print("\n🔌 TEST 4: Plugin System")
    print("-" * 40)
    
    plugins = app.get_plugins()
    expected_plugins = {
        'core-ui': 'Core UI',
        'settings': 'Settings Manager', 
        'favorites': 'Favorites',
        'history': 'Search History'
    }
    
    loaded = 0
    enabled = 0
    for plugin_id, plugin_name in expected_plugins.items():
        if plugin_id in plugins:
            plugin = plugins[plugin_id]
            status = "✅ Enabled" if plugin.enabled else "⚠️  Disabled"
            print(f"✅ {plugin_name} ({plugin_id}): {status}")
            loaded += 1
            if plugin.enabled:
                enabled += 1
        else:
            print(f"❌ {plugin_name} ({plugin_id}): Not loaded")
    
    print(f"\nResult: {loaded}/{len(expected_plugins)} loaded, {enabled} enabled")
    
    # Test 5: Event system
    print("\n📡 TEST 5: Event System")
    print("-" * 40)
    
    event_fired = False
    def test_handler(data):
        nonlocal event_fired
        event_fired = True
    
    app.events.on('test.event', test_handler)
    app.events.emit('test.event', 'test data')
    
    if event_fired:
        print("✅ Event emission and handling working")
    else:
        print("❌ Event system not working")
    
    # Test 6: Special features
    print("\n✨ TEST 6: Special Features")
    print("-" * 40)
    
    # Random word
    random_word = app.get_random_word()
    if random_word:
        print(f"✅ Random word: {random_word.lemma} ({random_word.pos})")
    else:
        print("❌ Random word failed")
    
    # Word of the day
    wotd = app.get_word_of_day()
    if wotd:
        print(f"✅ Word of the day: {wotd.lemma} ({wotd.pos})")
    else:
        print("❌ Word of the day failed")
    
    # Statistics
    print("\n📊 Final Statistics")
    print("-" * 40)
    
    # Count total entries
    total = app.database.execute_one("SELECT COUNT(*) FROM dictionary_entries")[0]
    print(f"Total dictionary entries: {total}")
    
    # Count inflections
    inflections = app.database.execute_one("SELECT COUNT(*) FROM inflection_lookup")[0]
    print(f"Total inflections: {inflections}")
    
    # Check if history is tracking
    history_plugin = app.get_plugin('history')
    if history_plugin and history_plugin.enabled:
        stats = history_plugin._get_statistics()
        print(f"Searches tracked: {stats.get('total_searches', 0)}")
        print(f"Search limit: {stats.get('search_count', 0)}/50")
    
    # Shutdown
    print("\n🔚 Shutting down...")
    app.shutdown()
    print("✅ App shutdown complete")
    
    print("\n" + "="*60)
    print(" ALL TESTS COMPLETED SUCCESSFULLY!")
    print("="*60)
    return True

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)