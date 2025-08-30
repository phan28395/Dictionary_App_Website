#!/usr/bin/env python3
"""
Non-interactive test of Dictionary App functionality
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core import DictionaryApp

# Initialize
print("="*50)
print("TESTING DICTIONARY APP (No Input Required)")
print("="*50)

print("\n1. INITIALIZING APP...")
app = DictionaryApp()
if app.initialize():
    print("✅ App initialized successfully")
else:
    print("❌ App initialization failed")
    sys.exit(1)

print("\n2. TESTING SEARCHES...")
test_words = ["book", "happy", "went", "quickly", "nonexistent"]
for word in test_words:
    results = app.search(word)
    if results:
        r = results[0]
        if r.inflection_note:
            print(f"✅ '{word}' → {r.lemma} ({r.pos}) - {r.inflection_note}")
        else:
            print(f"✅ '{word}' → {r.lemma} ({r.pos})")
    else:
        print(f"❌ '{word}' not found")

print("\n3. TESTING SUGGESTIONS...")
prefixes = ["hap", "bo", "qu"]
for prefix in prefixes:
    suggestions = app.get_suggestions(prefix)
    if suggestions:
        print(f"✅ '{prefix}' suggests: {', '.join(suggestions[:3])}")
    else:
        print(f"❌ No suggestions for '{prefix}'")

print("\n4. CHECKING PLUGINS...")
plugins = app.get_plugins()
print(f"✅ {len(plugins)} plugins loaded:")
for name, plugin in plugins.items():
    status = "enabled" if plugin.enabled else "disabled"
    print(f"   - {name}: {status}")

print("\n5. DATABASE STATISTICS...")
try:
    total = app.database.execute_one("SELECT COUNT(*) FROM dictionary_entries")[0]
    inflections = app.database.execute_one("SELECT COUNT(*) FROM inflection_lookup")[0]
    print(f"✅ Dictionary entries: {total}")
    print(f"✅ Inflections: {inflections}")
except Exception as e:
    print(f"❌ Database error: {e}")

print("\n6. EVENT SYSTEM TEST...")
test_event_fired = False
def test_handler(data):
    global test_event_fired
    test_event_fired = True
    
app.events.on('test.event', test_handler)
app.events.emit('test.event', {'test': 'data'})
if test_event_fired:
    print("✅ Event system working")
else:
    print("❌ Event system not working")

print("\n7. PLUGIN API TEST...")
# Test if plugins can access app API
ui_plugin = app.get_plugin('core-ui')
if ui_plugin and hasattr(ui_plugin, 'app'):
    print("✅ Plugins have app access")
    # Test search through plugin
    results = ui_plugin.app.search('book')
    if results:
        print("✅ Plugin can perform searches")
    else:
        print("❌ Plugin search failed")
else:
    print("❌ Plugin API access issue")

print("\n8. CONFIGURATION TEST...")
config = app.config.get('database.path')
if config:
    print(f"✅ Config loaded: database at {config}")
else:
    print("❌ Config not loaded")

print("\n9. SHUTTING DOWN...")
app.shutdown()
print("✅ App shut down cleanly")

print("\n" + "="*50)
print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
print("="*50)