#!/usr/bin/env python3
"""
Quick Test Script for Dictionary App
Tests all major functionality quickly
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_dependencies():
    """Check if GUI dependencies are available."""
    print("Checking dependencies...")
    
    deps = {
        'tkinter': False,
        'customtkinter': False,
        'pystray': False,
        'PIL': False,
        'pynput': False
    }
    
    # Check each dependency
    try:
        import tkinter
        deps['tkinter'] = True
    except ImportError:
        pass
        
    try:
        import customtkinter
        deps['customtkinter'] = True
    except ImportError:
        pass
        
    try:
        import pystray
        deps['pystray'] = True
    except ImportError:
        pass
        
    try:
        from PIL import Image
        deps['PIL'] = True
    except ImportError:
        pass
        
    try:
        import pynput
        deps['pynput'] = True
    except ImportError:
        pass
        
    # Print results
    print("\nDependency Status:")
    for dep, installed in deps.items():
        status = "✅" if installed else "❌"
        print(f"  {status} {dep}")
        
    # Check if GUI will work
    gui_ready = deps['tkinter'] and deps['customtkinter']
    tray_ready = deps['pystray'] and deps['PIL']
    hotkey_ready = deps['pynput']
    
    print("\nFeature Availability:")
    print(f"  {'✅' if gui_ready else '❌'} GUI Windows")
    print(f"  {'✅' if tray_ready else '❌'} System Tray")
    print(f"  {'✅' if hotkey_ready else '❌'} Global Hotkeys")
    
    return gui_ready

def test_console_mode():
    """Test console functionality."""
    print("\n" + "="*50)
    print("Testing Console Mode")
    print("="*50)
    
    from core.app import DictionaryApp
    
    # Initialize app
    app = DictionaryApp()
    app.initialize()
    
    # Check plugins loaded
    plugin_count = len(app.plugin_loader.plugins)
    print(f"✅ Loaded {plugin_count} plugins")
    
    # Test search
    print("\nTesting search for 'happy'...")
    results = app.search("happy")
    if results:
        result = results[0]
        print(f"✅ Found: {result.lemma} ({result.pos})")
        if result.meanings:
            print(f"   Definition: {result.meanings[0].definition[:60]}...")
    else:
        print("❌ No results - might be at search limit")
        
    # Test suggestions
    print("\nTesting suggestions for 'com'...")
    suggestions = app.get_suggestions("com", 5)
    if suggestions:
        print(f"✅ Suggestions: {', '.join(suggestions)}")
    else:
        print("❌ No suggestions")
        
    # Check search count
    if 'history' in app.plugin_loader.plugins:
        history = app.plugin_loader.plugins['history']
        count = history.get_search_count()
        print(f"\n📊 Search count: {count}/50")
        
        if count >= 50:
            print("⚠️  Free tier limit reached! Reset with:")
            print("    sqlite3 data/plugin-storage/history/history.db \"UPDATE search_counts SET total_count = 0;\"")
            
    # Check database
    import sqlite3
    conn = sqlite3.connect('data/dictionary.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM dictionary_entries")
    total = cursor.fetchone()[0]
    print(f"\n📚 Dictionary entries: {total:,}")
    conn.close()
    
    return True

def test_gui_mode():
    """Test GUI functionality."""
    print("\n" + "="*50)
    print("Testing GUI Mode")
    print("="*50)
    
    try:
        import tkinter as tk
        from tkinter import messagebox
        
        # Create test window
        print("Creating test window...")
        root = tk.Tk()
        root.withdraw()  # Hide main window
        
        # Show test dialog
        result = messagebox.askyesno(
            "Dictionary App Test",
            "GUI is working!\n\n"
            "Would you like to start the full app with GUI?\n\n"
            "Click Yes to start the app, or No to continue testing."
        )
        
        root.destroy()
        
        if result:
            print("✅ GUI test successful!")
            print("\nTo start the full app, run:")
            print("    python run_app.py")
        else:
            print("✅ GUI test completed")
            
        return True
        
    except Exception as e:
        print(f"❌ GUI test failed: {e}")
        print("\nTo enable GUI, install:")
        print("    sudo apt-get install python3-tk")
        print("    pip install customtkinter")
        return False

def main():
    """Run all tests."""
    print("="*60)
    print("DICTIONARY APP QUICK TEST")
    print("="*60)
    
    # Test dependencies
    gui_available = test_dependencies()
    
    # Test console mode (always works)
    console_ok = test_console_mode()
    
    # Test GUI if available
    if gui_available:
        gui_ok = test_gui_mode()
    else:
        print("\n⚠️  GUI not available - console mode only")
        gui_ok = False
        
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"✅ Console Mode: {'Working' if console_ok else 'Failed'}")
    print(f"{'✅' if gui_ok else '⚠️'} GUI Mode: {'Working' if gui_ok else 'Not Available'}")
    
    print("\n📋 Quick Start Commands:")
    print("  Start app:        python run_app.py")
    print("  Reset searches:   sqlite3 data/plugin-storage/history/history.db \"UPDATE search_counts SET total_count = 0;\"")
    print("  Check GUI deps:   pip install customtkinter pystray pynput")
    
    print("\n💡 Tips:")
    print("  - Double-tap Ctrl to open search (if GUI available)")
    print("  - Type 'quit' in console to exit")
    print("  - After 50 searches, upgrade prompt appears")
    
if __name__ == "__main__":
    main()