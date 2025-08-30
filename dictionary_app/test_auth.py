#!/usr/bin/env python3
"""
Test script for Authentication plugin.
Tests guest mode and basic auth flow (without actual Supabase).
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.app import DictionaryApp

logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_auth_plugin():
    """Test authentication plugin functionality."""
    print("\n" + "="*50)
    print("Testing Authentication Plugin")
    print("="*50)
    
    # Create app instance
    app = DictionaryApp()
    
    # Initialize the app to load plugins
    if not app.initialize():
        print("❌ Failed to initialize app!")
        return
    
    # Check if auth plugin loaded
    if not hasattr(app, 'auth'):
        print("❌ Auth plugin not loaded!")
        return
        
    auth = app.auth
    print("✅ Auth plugin loaded successfully")
    
    # Test 1: Guest mode
    print("\n--- Testing Guest Mode ---")
    if auth.is_guest():
        print(f"✅ Guest mode active")
        print(f"   Guest ID: {auth.get_guest_id()}")
        print(f"   Search count: {auth.get_search_count()}")
    else:
        print("❌ Guest mode not initialized")
        
    # Test 2: Check authentication status
    print("\n--- Testing Auth Status ---")
    print(f"Is authenticated: {auth.is_authenticated()}")
    print(f"Is guest: {auth.is_guest()}")
    print(f"Is premium: {auth.is_premium}")
    
    # Test 3: Search limit check
    print("\n--- Testing Search Limit ---")
    search_count = auth.get_search_count()
    limit = auth.settings.get('guest_search_limit', 50)
    
    print(f"Current searches: {search_count}/{limit}")
    
    if search_count < limit:
        print(f"✅ Can search ({limit - search_count} remaining)")
    else:
        print(f"❌ Search limit reached!")
        
    # Test 4: Check settings
    print("\n--- Plugin Settings ---")
    print(f"Guest mode enabled: {auth.settings.get('enable_guest_mode')}")
    print(f"Guest search limit: {auth.settings.get('guest_search_limit')}")
    print(f"Remember login: {auth.settings.get('remember_login')}")
    print(f"Auto login: {auth.settings.get('auto_login')}")
    
    # Test 5: Check Supabase availability
    print("\n--- Supabase Status ---")
    if auth.supabase:
        print("✅ Supabase client initialized")
    else:
        print("⚠️ Supabase not available (guest mode only)")
        print("   To enable: Set SUPABASE_URL and SUPABASE_ANON_KEY in .env")
        
    # Test 6: Events
    print("\n--- Testing Events ---")
    
    # Listen for auth events
    def on_limit_reached(data):
        print(f"⚠️ Limit reached event: {data}")
        
    app.events.on('auth.limit_reached', on_limit_reached)
    
    # Simulate a search that might hit limit
    event_data = {}
    app.events.emit('search.before', event_data)
    
    if event_data.get('cancel'):
        print(f"❌ Search blocked: {event_data.get('reason')}")
    else:
        print("✅ Search allowed")
        
    print("\n" + "="*50)
    print("Auth Plugin Test Complete!")
    print("="*50)
    
    # Test UI if display is available
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        
        print("\n--- Testing UI Components ---")
        print("Display available - UI can be tested")
        print("Run 'python test_auth_ui.py' to test the login window")
        
    except:
        print("\n⚠️ No display - skipping UI tests")


def main():
    """Main entry point."""
    # Run async test
    asyncio.run(test_auth_plugin())
    

if __name__ == "__main__":
    main()