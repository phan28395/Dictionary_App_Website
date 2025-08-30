#!/usr/bin/env python3
"""
Test script for licensing plugin
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.app import DictionaryApp

def test_licensing():
    """Test licensing plugin functionality."""
    print("=" * 60)
    print("LICENSING PLUGIN TEST")
    print("=" * 60)
    
    # Create app instance
    app = DictionaryApp()
    app.initialize()
    
    # Check if licensing plugin loaded
    if hasattr(app.plugin_loader, 'plugins') and 'licensing' in app.plugin_loader.plugins:
        print("✅ Licensing plugin loaded")
        licensing = app.plugin_loader.plugins['licensing']
        
        # Check premium status
        is_premium = licensing.is_premium_user()
        print(f"Premium status: {'Yes' if is_premium else 'No'}")
        
        # Get search counts
        search_count = licensing.get_search_count()
        search_limit = licensing.get_search_limit()
        remaining = licensing.get_remaining_searches()
        
        print(f"Search count: {search_count}/{search_limit}")
        if remaining >= 0:
            print(f"Remaining searches: {remaining}")
        else:
            print("Remaining searches: Unlimited")
            
        # Test search with limit enforcement
        print("\n" + "-" * 40)
        print("Testing search limit enforcement...")
        print("-" * 40)
        
        # Try a search
        print("\nSearching for 'happy'...")
        results = app.search("happy")
        
        if results:
            print(f"✅ Search successful - found {len(results)} results")
        else:
            print("❌ Search blocked (possibly due to limit)")
            
        # Check updated counts
        if 'history' in app.plugin_loader.plugins:
            history = app.plugin_loader.plugins['history']
            new_count = history.get_search_count()
            print(f"Updated search count: {new_count}")
            
        # Simulate reaching the limit (for testing)
        if not is_premium:
            print("\n" + "-" * 40)
            print("Simulating free tier limit...")
            print("-" * 40)
            
            # This would normally happen after 50 searches
            # For testing, we'll just check the upgrade prompt logic
            if search_count < search_limit:
                print(f"You have {remaining} searches remaining in free tier")
            else:
                print("Free tier limit reached! Upgrade prompt would appear here.")
                
        # Device info
        print("\n" + "-" * 40)
        print("Device Information")
        print("-" * 40)
        print(f"Device ID: {licensing.device_id}")
        print(f"Device limit OK: {licensing.check_device_limit()}")
        
    else:
        print("❌ Licensing plugin not found")
        
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    
    # Test purchase flow (demo)
    if hasattr(app.plugin_loader, 'plugins') and 'licensing' in app.plugin_loader.plugins:
        print("\nTo test purchase flow, uncomment the line below:")
        print("# licensing.start_purchase_flow()")
        print("\nThis will open a browser with Stripe demo checkout")

if __name__ == "__main__":
    test_licensing()