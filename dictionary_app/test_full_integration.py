#!/usr/bin/env python3
"""
Test full integration of auth plugin with the app.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.app import DictionaryApp


def test_full_integration():
    """Test auth plugin with full app integration."""
    print("\n" + "="*50)
    print("Testing Full Auth Integration")
    print("="*50)
    
    # Create and initialize app
    app = DictionaryApp()
    if not app.initialize():
        print("❌ Failed to initialize app!")
        return
        
    print("\n--- Loaded Plugins ---")
    plugins = app.get_plugins()
    for plugin_id, plugin in plugins.items():
        print(f"  • {plugin_id}: {plugin.__class__.__name__}")
        if plugin_id == 'auth' and hasattr(app, 'auth'):
            print(f"    ✅ Exposed as app.auth")
        if plugin_id == 'history':
            print(f"    Search count: {plugin.search_count if hasattr(plugin, 'search_count') else 'N/A'}")
            
    # Test auth plugin
    print("\n--- Auth Plugin Status ---")
    if hasattr(app, 'auth'):
        auth = app.auth
        print(f"✅ Auth plugin accessible")
        print(f"   Guest mode: {auth.is_guest()}")
        print(f"   Guest ID: {auth.get_guest_id()}")
        print(f"   Authenticated: {auth.is_authenticated()}")
        print(f"   Premium: {auth.is_premium}")
        print(f"   Search count: {auth.get_search_count()}")
        print(f"   Search limit: {auth.settings.get('guest_search_limit')}")
    else:
        print("❌ Auth plugin not accessible via app.auth")
        
    # Test searching with limit check
    print("\n--- Testing Search with Auth ---")
    
    # Get history plugin
    history_plugin = plugins.get('history')
    if history_plugin:
        print(f"History plugin search count: {history_plugin.search_count}")
    
    # Perform a search
    print("\nSearching for 'happy'...")
    results = app.search('happy')
    
    if results:
        print(f"✅ Search successful: {len(results)} results")
        print(f"   Lemma: {results[0].lemma}")
        print(f"   POS: {results[0].pos}")
    else:
        print("⚠️ No results found")
        
    # Check count after search
    if history_plugin:
        print(f"\nHistory count after search: {history_plugin.search_count}")
    if hasattr(app, 'auth'):
        print(f"Auth count after search: {app.auth.get_search_count()}")
        
    # Test limit enforcement
    print("\n--- Testing Limit Enforcement ---")
    
    if hasattr(app, 'auth'):
        auth = app.auth
        current_count = auth.get_search_count()
        limit = auth.settings.get('guest_search_limit', 50)
        
        if current_count >= limit:
            print(f"⚠️ At limit ({current_count}/{limit})")
            
            # Try another search
            print("Attempting search at limit...")
            results2 = app.search('test')
            
            # The search should still work but auth should have blocked it
            # Check if any event was emitted
        else:
            remaining = limit - current_count
            print(f"✅ Under limit ({current_count}/{limit})")
            print(f"   Searches remaining: {remaining}")
            
    print("\n--- Testing Event Integration ---")
    
    # Set up event listener
    limit_reached = []
    def on_limit(data):
        limit_reached.append(data)
        print(f"⚠️ Limit reached event: {data}")
        
    app.events.on('auth.limit_reached', on_limit)
    
    # Trigger search.before event
    event_data = {}
    app.events.emit('search.before', event_data)
    
    if event_data.get('cancel'):
        print(f"✅ Search blocked by auth: {event_data.get('reason')}")
    else:
        print("✅ Search allowed by auth")
        
    print("\n" + "="*50)
    print("Integration Test Complete!")
    print("="*50)


if __name__ == "__main__":
    # Suppress logs for cleaner output
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    test_full_integration()