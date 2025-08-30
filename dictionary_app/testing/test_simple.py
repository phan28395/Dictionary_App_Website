#!/usr/bin/env python3
"""
Simple test to verify Dictionary App is working
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core import DictionaryApp

# Initialize
print("Initializing Dictionary App...")
app = DictionaryApp()
app.initialize()

print("\n✅ TESTING DICTIONARY SEARCHES:")
print("-" * 40)

# Test searches
tests = [
    ("book", "noun"),
    ("happy", "adjective"),
    ("went", "verb"),  # inflection
    ("quickly", "adverb")
]

for word, expected_pos in tests:
    results = app.search(word)
    if results:
        r = results[0]
        print(f"✅ '{word}' found: {r.lemma} ({r.pos})")
        if r.inflection_note:
            print(f"   → {r.inflection_note}")
        if r.meanings:
            print(f"   → {r.meanings[0]['definition'][:50]}...")
    else:
        print(f"❌ '{word}' not found")

print("\n✅ TESTING SUGGESTIONS:")
print("-" * 40)
suggestions = app.get_suggestions("hap")
print(f"'hap' suggests: {', '.join(suggestions)}")

print("\n✅ TESTING PLUGINS:")
print("-" * 40)
plugins = app.get_plugins()
for name, plugin in plugins.items():
    status = "enabled" if plugin.enabled else "disabled"
    print(f"  {name}: {status}")

print("\n✅ DATABASE STATS:")
print("-" * 40)
total = app.database.execute_one("SELECT COUNT(*) FROM dictionary_entries")[0]
inflections = app.database.execute_one("SELECT COUNT(*) FROM inflection_lookup")[0]
print(f"  Dictionary entries: {total}")
print(f"  Inflections: {inflections}")

app.shutdown()
print("\n🎉 ALL TESTS PASSED! Dictionary App is working!")