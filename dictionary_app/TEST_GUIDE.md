# Dictionary App Testing Guide

## Prerequisites
Before testing the GUI, make sure you have these installed:
```bash
# For system tray and GUI
sudo apt-get install python3-tk libayatana-appindicator3-1

# For GUI components (if not installed)
pip install customtkinter pystray pillow pynput
```

## How to Start the App

### Option 1: Run from Main Directory
```bash
cd /mnt/storage/Documents/Dictionary_App_Website/Dictionary_App_Website/dictionary_app
python run_app.py
```

### Option 2: Run from Standalone Package
```bash
cd dist/DictionaryApp
./DictionaryApp.sh
```

## What You'll See When App Starts

1. **Console Output** showing:
   - App initialization
   - Plugins loading (7 total)
   - Database connection
   - "Dictionary App is running. Press Ctrl+C to stop."

2. **System Tray Icon** (if display is available):
   - Dictionary icon in system tray
   - Right-click for menu options
   - Green when active

3. **Console Interface** with commands:
   ```
   ==================================================
   Dictionary App - Simple Console UI
   ==================================================
   Commands:
     search <word>  - Search for a word
     suggest <text> - Get suggestions
     random        - Get random word
     wotd          - Word of the day
     quit          - Exit application
   ==================================================
   ```

## Testing Core Features

### 1. Console Search (Easy Test)
In the console, type:
```
> search happy
```

Expected result:
- Shows definition for "happy" (adjective)
- Displays meanings and examples
- Updates search count (1/50)

### 2. Test Autocomplete
```
> suggest hap
```

Expected result:
- Shows: haphazard, hapless, happen, happening, happy

### 3. Test Random Word
```
> random
```

Expected result:
- Shows a random dictionary entry with definition

### 4. Test Word of the Day
```
> wotd
```

Expected result:
- Shows today's featured word

## Testing GUI Features (if display available)

### 1. System Tray Icon
- Look for dictionary icon in system tray
- Right-click to see menu:
  - Search
  - Settings
  - Exit

### 2. Global Hotkey (Main Feature!)
**Double-tap Ctrl key quickly**
- A search popup window should appear
- Type a word and press Enter
- See instant definitions

### 3. Settings Window
From system tray menu, click "Settings":
- General tab: Configure hotkeys
- Extensions tab: See all 7 plugins
- About tab: Version info

## Testing Monetization

### 1. Free Tier Limit
Keep searching until you hit 50 searches:
```
> search computer
> search house
> search run
... (continue until 50)
```

After 50 searches:
- Search will be blocked
- Upgrade prompt appears
- Shows "$20 one-time payment"

### 2. Check Search Count
```bash
sqlite3 data/plugin-storage/history/history.db "SELECT total_count FROM search_counts;"
```

### 3. Reset for More Testing
```bash
# Reset search count to 0
sqlite3 data/plugin-storage/history/history.db "UPDATE search_counts SET total_count = 0;"
```

## Testing with Full Dataset

### Test Words That Should Work:
- **Nouns**: house, computer, time, person, world, system
- **Adjectives**: happy, beautiful, good, bad, large, small
- **Verbs**: run, go, make, take, see, know
- **Inflections**: went (→go), better (→good), children (→child)

### Check Database Stats:
```bash
sqlite3 data/dictionary.db "SELECT pos, COUNT(*) FROM dictionary_entries GROUP BY pos;"
```

Should show:
- adjective: 7,776
- noun: 16,730
- verb: 50
- Total: 24,556 entries

## Common Issues & Solutions

### Issue: No GUI/System Tray
**Solution**: Install required packages
```bash
sudo apt-get install python3-tk libayatana-appindicator3-1
pip install customtkinter pystray
```

### Issue: Search Returns No Results
**Solution**: Check if you hit the 50-search limit
```bash
# Check count
sqlite3 data/plugin-storage/history/history.db "SELECT total_count FROM search_counts;"

# Reset if needed
sqlite3 data/plugin-storage/history/history.db "UPDATE search_counts SET total_count = 0;"
```

### Issue: Hotkey Doesn't Work
**Solution**: 
1. Make sure pynput is installed: `pip install pynput`
2. Check if another app is using Ctrl+Ctrl
3. Try running with sudo (Linux): `sudo python run_app.py`

### Issue: Database Empty
**Solution**: Re-import data
```bash
python scripts/bulk_import.py
```

## What Success Looks Like

✅ **Console works**: Can search words and get definitions
✅ **GUI loads**: System tray icon appears
✅ **Hotkey works**: Double-Ctrl opens search popup
✅ **Data loaded**: 24,556 entries available
✅ **Licensing works**: Blocks after 50 searches
✅ **Plugins active**: All 7 plugins loaded

## Quick Test Checklist

- [ ] App starts without errors
- [ ] Console search works (`search happy`)
- [ ] Suggestions work (`suggest com`)
- [ ] Random word works (`random`)
- [ ] Search count increases
- [ ] Blocks at 50 searches
- [ ] System tray icon appears (if GUI available)
- [ ] Double-Ctrl hotkey works (if GUI available)
- [ ] Settings window opens
- [ ] Can quit cleanly (`quit` or Ctrl+C)

## Advanced Testing

### Test Extension Store
```
> search test
```
Then check if extension store plugin tries to fetch registry.

### Test Favorites
After searching, the word is automatically trackable as favorite.

### Test History
Check search history:
```bash
sqlite3 data/plugin-storage/history/history.db "SELECT * FROM search_history LIMIT 5;"
```

## Support

If something doesn't work:
1. Check the console for error messages
2. Look at log files in `data/` directory
3. Verify all dependencies are installed
4. Reset search count if needed
5. Re-import data if database is empty

---

**Remember**: The app is designed to work even without GUI. The console interface is always available!