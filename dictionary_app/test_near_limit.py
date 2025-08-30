#!/usr/bin/env python3
"""
Test behavior near the 50-search limit.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.app import DictionaryApp


def test_near_limit():
    """Test auth behavior near the 50-search limit."""
    print("\n" + "="*50)
    print("Testing Near Limit Behavior")
    print("="*50)
    
    # Create and initialize app
    app = DictionaryApp()
    if not app.initialize():
        print("❌ Failed to initialize app!")
        return
        
    # Get auth and check current status
    if not hasattr(app, 'auth'):
        print("❌ Auth plugin not loaded!")
        return
        
    auth = app.auth
    
    # Check current count
    current_count = auth.get_search_count()
    limit = auth.settings.get('guest_search_limit', 50)
    remaining = limit - current_count
    
    print(f"\n📊 Current Status:")
    print(f"   Searches used: {current_count}/{limit}")
    print(f"   Searches remaining: {remaining}")
    
    if remaining <= 0:
        print("\n⚠️ Already at or over limit!")
        print("Testing search blocking...")
        
        # Try to search
        event_data = {}
        app.events.emit('search.before', event_data)
        
        if event_data.get('cancel'):
            print(f"✅ Search correctly blocked: {event_data.get('reason')}")
        else:
            print("❌ Search should have been blocked!")
            
    elif remaining <= 5:
        print(f"\n⚠️ Near limit! Only {remaining} searches left")
        print("Performing a search...")
        
        results = app.search("test")
        if results:
            print(f"✅ Search allowed (now {auth.get_search_count()}/{limit})")
        
        new_remaining = limit - auth.get_search_count()
        print(f"   Remaining after search: {new_remaining}")
        
        if new_remaining <= 0:
            print("\n🚫 Limit reached! Next search should be blocked")
            
    else:
        print(f"\n✅ Still have {remaining} searches available")
        print("   Performing multiple searches to test counting...")
        
        words = ["happy", "sad", "good", "bad", "test"]
        for word in words[:min(5, remaining)]:
            results = app.search(word)
            new_count = auth.get_search_count()
            print(f"   Searched '{word}': {new_count}/{limit}")
            
            if new_count >= limit:
                print("\n🚫 Limit reached!")
                break
                
    # Final status
    print(f"\n📊 Final Status:")
    final_count = auth.get_search_count()
    final_remaining = max(0, limit - final_count)
    print(f"   Total searches: {final_count}/{limit}")
    print(f"   Remaining: {final_remaining}")
    
    if final_count >= limit:
        print("\n💡 Upgrade Required:")
        print("   The free tier limit has been reached.")
        print("   Sign up for unlimited searches!")
    
    print("\n" + "="*50)
    print("Near Limit Test Complete!")
    print("="*50)


if __name__ == "__main__":
    # Suppress logs for cleaner output
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    test_near_limit()