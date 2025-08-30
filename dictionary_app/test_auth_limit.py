#!/usr/bin/env python3
"""
Test search limit enforcement in Authentication plugin.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.app import DictionaryApp


def test_search_limit():
    """Test that search limit is enforced."""
    print("\n" + "="*50)
    print("Testing Search Limit Enforcement")
    print("="*50)
    
    # Create and initialize app
    app = DictionaryApp()
    if not app.initialize():
        print("❌ Failed to initialize app!")
        return
        
    # Check auth plugin
    if not hasattr(app, 'auth'):
        print("❌ Auth plugin not loaded!")
        return
        
    auth = app.auth
    print(f"✅ Auth plugin loaded")
    print(f"Guest ID: {auth.get_guest_id()}")
    
    # Get current search count from history
    history_count = 0
    if hasattr(app, 'history'):
        # The history plugin tracks searches
        try:
            # Get the actual count from history database
            query = "SELECT COUNT(*) FROM search_history"
            result = app.history.db.execute(query)
            if result:
                history_count = result.fetchone()[0]
        except:
            pass
    
    print(f"\nCurrent search count from history: {history_count}")
    
    # Check limit from auth settings
    limit = auth.settings.get('guest_search_limit', 50)
    print(f"Guest search limit: {limit}")
    
    # Test search blocking
    print("\n--- Testing Search Blocking ---")
    
    # Simulate being at the limit
    if history_count < limit:
        print(f"✅ Under limit - searches should be allowed")
        print(f"   Remaining: {limit - history_count}")
        
        # Test that search is allowed
        event_data = {}
        app.events.emit('search.before', event_data)
        
        if event_data.get('cancel'):
            print(f"❌ Search incorrectly blocked: {event_data.get('reason')}")
        else:
            print("✅ Search correctly allowed")
    else:
        print(f"⚠️ At or over limit - searches should be blocked")
        
        # Test that search is blocked
        event_data = {}
        app.events.emit('search.before', event_data)
        
        if event_data.get('cancel'):
            print(f"✅ Search correctly blocked: {event_data.get('reason')}")
        else:
            print("❌ Search should have been blocked!")
    
    # Test actual search functionality
    print("\n--- Testing Actual Search ---")
    
    if history_count < limit:
        # Try a real search
        results = app.search("happy")
        if results:
            print(f"✅ Search succeeded: Found {len(results)} results for 'happy'")
        else:
            print("⚠️ No results found for 'happy'")
    else:
        print("⚠️ Skipping search test - already at limit")
        
    # Check if guest data is persisted
    print("\n--- Testing Guest Data Persistence ---")
    
    guest_file = auth.guest_file
    if guest_file and guest_file.exists():
        print(f"✅ Guest data file exists: {guest_file}")
        
        import json
        with open(guest_file, 'r') as f:
            guest_data = json.load(f)
            print(f"   Guest ID: {guest_data.get('guest_id')}")
            print(f"   Created: {guest_data.get('created_at')}")
            print(f"   Stored count: {guest_data.get('search_count', 0)}")
    else:
        print("❌ Guest data file not found")
        
    print("\n" + "="*50)
    print("Search Limit Test Complete!")
    print("="*50)


if __name__ == "__main__":
    test_search_limit()