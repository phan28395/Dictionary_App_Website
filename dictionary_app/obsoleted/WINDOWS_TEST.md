# Windows Testing Guide

## Prerequisites

### 1. Python 3.11+
```cmd
python --version
```
Should show Python 3.11.0 or higher.

### 2. Install Core Dependencies
```cmd
pip install -r requirements.txt
```

### 3. Install UI Plugin Dependencies
```cmd
pip install -r plugins\core-ui\requirements.txt
```

## Quick Test Steps

### Step 1: Basic App Test
```cmd
python run_app.py
```

**Expected Output:**
- App should start without errors
- Look for "Dictionary App initialized" message
- Look for "Core UI plugin loaded successfully"
- Should show "Double-tap Ctrl to open search"

### Step 2: Test Search Functionality
With the app running:
1. **Double-tap Ctrl key quickly** to trigger search popup
2. Type a word like "run" or "good"
3. Press Enter
4. Should see definition popup

### Step 3: Test System Tray
1. Look for dictionary icon in Windows system tray (bottom right)
2. Right-click the icon to see menu
3. Click "Show/Hide" to toggle main window

## Troubleshooting

### If App Won't Start:
```cmd
# Check if database exists
dir data\
```
Should show `dictionary.db` file.

### If No Search Results:
```cmd
# Test database connection
python -c "from core.database import DatabaseManager; db = DatabaseManager(); print('DB OK' if db.get_connection() else 'DB FAIL')"
```

### If Hotkey Doesn't Work:
- Try running as Administrator
- Check if another app is using Ctrl+Ctrl
- Look for error messages in console

### If No System Tray Icon:
- May need to run as Administrator on some Windows systems
- Check Windows notification area settings

## Expected Behavior

✅ **Working App Should:**
- Start without Python errors
- Show system tray icon
- Respond to Ctrl+Ctrl hotkey
- Display search popup near cursor
- Return dictionary definitions
- Allow favorites (star icon)

❌ **Common Issues:**
- Permission errors (run as Admin)
- Missing DLL errors (install Visual C++ Redistributable)
- Hotkey conflicts with other apps
- Windows Defender blocking system tray access

## Manual Testing Checklist

- [ ] App starts without errors
- [ ] System tray icon appears
- [ ] Ctrl+Ctrl hotkey works
- [ ] Search popup appears
- [ ] Can type in search box
- [ ] Returns definition for "run"
- [ ] Can close with ESC key
- [ ] Can click outside to close
- [ ] Star icon works for favorites
- [ ] App stops cleanly with Ctrl+C

## Performance Check

The app should:
- Start in under 5 seconds
- Search response in under 1 second
- Use less than 100MB RAM
- CPU usage near 0% when idle

## Quick Exit

Press **Ctrl+C** in the terminal to stop the app cleanly.

## Need Help?

If issues persist, check:
1. `data\dictionary.db` exists and is not empty
2. All pip packages installed correctly
3. Windows firewall not blocking Python
4. Running with Administrator privileges if needed