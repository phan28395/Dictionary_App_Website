# Dictionary App 📖

A powerful, extensible dictionary application with global hotkeys, system tray integration, and a plugin-based architecture. Everything is a plugin - even the UI!

## 🚀 Quick Start (Windows Testing)

### Requirements
- **Windows 10/11** (recommended for testing)
- **Python 3.11+** ([Download here](https://www.python.org/downloads/))

### 📥 Installation

1. **Clone this repository:**
```bash
git clone <repository-url>
cd dictionary_app
```

2. **Run the app:**
```bash
# Option 1: Use the launcher (installs dependencies automatically)
DictionaryApp.bat

# Option 2: Manual installation
python -m pip install -r requirements.txt
python -m pip install -r plugins/core-ui/requirements.txt
python run_app.py
```

### 🎯 Testing the Hotkeys

1. **Start the app** - You should see a system tray icon 
2. **Double-tap Ctrl** quickly (within 500ms) 
3. **Search window should appear** near your cursor
4. **Try searching** for words like "happy", "go", "run"

### ✅ What to Test

- [ ] App starts without errors
- [ ] System tray icon appears
- [ ] Double Ctrl opens search window
- [ ] Search finds words in database (25K+ entries)  
- [ ] Selected text search (select text, double Ctrl)
- [ ] Settings window opens from tray menu
- [ ] App works after restart

## 🏗️ Project Architecture

### Core Principles
- **Headless Core**: No UI code in `core/` - everything UI is plugins
- **Plugin Everything**: Even core UI, settings, auth are replaceable plugins  
- **Offline First**: Works completely offline (except purchases)
- **Simple & Fast**: Focus on search accuracy and speed

## 🔥 Features

### ✅ **Implemented Features**
- **25,221+ Dictionary Entries** with full definitions, examples, collocations
- **Global Hotkeys** - Double Ctrl to search from anywhere
- **System Tray Integration** - Always accessible, minimal footprint
- **Selected Text Search** - Highlight text, double Ctrl to define
- **Plugin Architecture** - Everything is extensible
- **Offline Database** - Fast SQLite search with inflection lookup
- **Free Tier** - 50 searches, then upgrade prompt
- **Settings Management** - Hotkey customization, plugin management
- **Search History** - Track and revisit searches
- **Favorites System** - Bookmark important words
- **Modern UI** - CustomTkinter with dark mode support

## 🧪 Current Status

### ✅ **Working Great On:**
- **Windows** - Full hotkey and tray support
- **Wine/Windows Emulation** - Tested and working
- **Linux X11** - Full functionality

### ⚠️ **Limited On:**
- **Linux Wayland** - Hotkeys restricted (security), use tray menu instead
- **macOS** - Not yet tested (need Mac hardware)

## 🛠️ Development

### Running Tests

```bash
# Run with console output
python run_app.py

# Test search functionality
python -c "
from core.app import DictionaryApp
app = DictionaryApp()
app.initialize()
results = app.search('happy')
print(f'Found {len(results)} results')
"
```

## 🎯 Testing Checklist

### **Windows Testing** (High Priority)
- [ ] Download and run on Windows 10/11
- [ ] Test hotkeys (double Ctrl)
- [ ] Test system tray functionality
- [ ] Test with antivirus software
- [ ] Test on multiple screen setups
- [ ] Test selected text search
- [ ] Performance with large database
- [ ] Memory usage during long sessions

## 📊 Database Stats

- **Total Entries**: 25,221 dictionary entries
- **Entry Types**: 16,730 nouns, 7,776 adjectives, 52 verbs, 1 adverb
- **Inflections**: 10 common inflection mappings (went → go, etc.)
- **Database Size**: ~15MB uncompressed
- **Search Speed**: <50ms for most queries

## 🔐 Security & Privacy

- **Local-First**: All data stays on your device
- **No Tracking**: Search history never leaves your computer  
- **Encrypted Storage**: SQLite database with optional encryption
- **Minimal Cloud**: Only for authentication and license validation
- **Open Source**: Inspect all code, no hidden behavior

## 🐛 Bug Reports & Issues

**Testing on Windows?** Please report:

1. **What worked**: Features that functioned correctly
2. **What didn't work**: Errors, crashes, unexpected behavior  
3. **System specs**: Windows version, Python version, hardware
4. **Steps to reproduce**: Exact steps that caused issues
5. **Screenshots**: If UI looks broken or incorrect

## 🚀 Coming Next

1. **Windows Installer** - Proper .msi installer with digital signature
2. **macOS Port** - Native Mac experience with Cmd+Cmd hotkeys
3. **Extension Store** - Plugin marketplace with themes and tools
4. **Cloud Features** - Optional sync for premium users
5. **Advanced Search** - Fuzzy matching, regex, phonetic search

---

**Happy Testing!** 🎉 This dictionary app is built for power users who want fast, offline dictionary access with unlimited extensibility.

