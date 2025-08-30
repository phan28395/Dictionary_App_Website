#!/usr/bin/env python3
"""
Quick test of Dictionary App functionality
"""

import sys
import time
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core import DictionaryApp

def test_app():
    print("="*50)
    print("Dictionary App Quick Test")
    print("="*50)
    
    # Initialize app
    print("\n1. Initializing app...")
    app = DictionaryApp()
    
    if not app.initialize():
        print("❌ Failed to initialize")
        return False
    print("✅ App initialized")
    
    # Test search
    print("\n2. Testing searches...")
    
    test_words = [
        ("book", "book", "noun"),
        ("happy", "happy", "adjective"),
        ("quickly", "quickly", "adverb"),
        ("run", "run", "verb"),
        ("went", "go", "verb"),  # Inflection test
    ]
    
    for search_term, expected_lemma, expected_pos in test_words:
        results = app.search(search_term)
        if results and results[0].lemma == expected_lemma:
            print(f"  ✅ '{search_term}' → {results[0].lemma} ({results[0].pos})")
            if results[0].inflection_note:
                print(f"     Note: {results[0].inflection_note}")
        else:
            print(f"  ❌ '{search_term}' failed")
    
    # Test suggestions
    print("\n3. Testing suggestions...")
    suggestions = app.get_suggestions("hap")
    if "happy" in suggestions:
        print(f"  ✅ Suggestions for 'hap': {', '.join(suggestions)}")
    else:
        print(f"  ❌ Suggestions failed")
    
    # Test plugins
    print("\n4. Testing plugins...")
    plugins = app.get_plugins()
    expected_plugins = ['core-ui', 'settings', 'favorites', 'history']
    
    for plugin_id in expected_plugins:
        if plugin_id in plugins:
            status = "enabled" if plugins[plugin_id].enabled else "disabled"
            print(f"  ✅ {plugin_id}: {status}")
        else:
            print(f"  ⚠️  {plugin_id}: not loaded")
    
    # Test favorites (if plugin loaded)
    print("\n5. Testing favorites...")
    favorites_plugin = app.get_plugin('favorites')
    if favorites_plugin and favorites_plugin.enabled:
        # Add a favorite
        app.events.emit('favorites.add', 'book', 'noun', 0, 'Test note')
        
        # Check if it was added
        is_fav = app.events.emit('favorites.check', 'book', 'noun')
        if is_fav:
            print(f"  ✅ Favorite added successfully")
        
        # List favorites
        favs = app.events.emit('favorites.list')
        print(f"  ✅ Favorites count: {len(favs[0]) if favs else 0}")
    else:
        print(f"  ⚠️  Favorites plugin not available")
    
    # Test history (if plugin loaded)
    print("\n6. Testing history...")
    history_plugin = app.get_plugin('history')
    if history_plugin and history_plugin.enabled:
        stats = app.events.emit('history.stats')
        if stats:
            print(f"  ✅ History tracking active")
            if stats[0]:
                print(f"     Total searches: {stats[0].get('total_searches', 0)}")
                print(f"     Search count: {stats[0].get('search_count', 0)}/50")
    else:
        print(f"  ⚠️  History plugin not available")
    
    # Shutdown
    print("\n7. Shutting down...")
    app.shutdown()
    print("✅ Shutdown complete")
    
    print("\n" + "="*50)
    print("All tests completed!")
    print("="*50)
    return True

if __name__ == '__main__':
    success = test_app()
    sys.exit(0 if success else 1)