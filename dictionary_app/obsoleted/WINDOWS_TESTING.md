# Windows Testing Guide 🪟

This guide helps you test the Dictionary App on Windows systems.

## 🚀 Quick Setup

### Step 1: Prerequisites
1. **Install Python 3.11+**: https://www.python.org/downloads/
   - ✅ Check "Add Python to PATH" during installation
   - ✅ Choose "Install for all users" if you're admin

2. **Verify Python**:
```cmd
python --version
```
Should show Python 3.11.x or newer.

### Step 2: Download & Run
1. **Clone or download** this repository
2. **Navigate** to the dictionary_app folder
3. **Double-click** `DictionaryApp.bat` OR run in Command Prompt:
```cmd
DictionaryApp.bat
```

The launcher will automatically:
- Create virtual environment
- Install all dependencies (may take 2-3 minutes first time)
- Start the app

## 🎯 Testing Scenarios

### ✅ **Basic Functionality**

**Test 1: App Startup**
- [ ] App starts without error messages
- [ ] Console shows "Dictionary App is running"
- [ ] System tray icon appears (book icon)
- [ ] No crashes or freezes

**Test 2: System Tray**
- [ ] Right-click tray icon shows menu
- [ ] "Search" option opens search window  
- [ ] "Settings" option works
- [ ] "Quit" option closes app cleanly

**Test 3: Hotkeys**
- [ ] **Double-tap Ctrl quickly** (within 500ms)
- [ ] Search window appears near cursor
- [ ] Window is focused and ready to type
- [ ] ESC key closes search window

### 🔍 **Search Testing**

**Test 4: Basic Search**
- [ ] Type "happy" and press Enter
- [ ] Results appear with definitions
- [ ] Multiple meanings shown
- [ ] Examples provided for each meaning

**Test 5: Inflection Search**
- [ ] Search for "went" → should find "go"
- [ ] Search for "running" → should find "run"  
- [ ] Search for "better" → should find "good"
- [ ] Inflection note shown (e.g., "went → go")

**Test 6: Selected Text Search**
- [ ] Open Notepad, type "magnificent"
- [ ] Select the word "magnificent"  
- [ ] Double-tap Ctrl (while text selected)
- [ ] Search window opens with "magnificent" pre-filled
- [ ] Results load automatically

### ⚙️ **Settings & Configuration**

**Test 7: Settings Window**
- [ ] Right-click tray → Settings opens window
- [ ] All tabs load without errors
- [ ] Plugin list shows enabled plugins
- [ ] Changes save and persist after restart

**Test 8: Plugin Management**
- [ ] Settings → Extensions tab shows plugins
- [ ] Toggle switches work for plugins
- [ ] Disabled plugins don't interfere
- [ ] Re-enabling plugins works

### 🔄 **Persistence Testing**

**Test 9: Restart Behavior**
- [ ] Close app completely (Quit from tray)
- [ ] Restart app
- [ ] Settings preserved
- [ ] Hotkeys still work
- [ ] Search history available

**Test 10: Search Limits**
- [ ] Perform 50+ searches
- [ ] Upgrade prompt appears after limit
- [ ] App explains premium features
- [ ] Can still access previous searches

## 🐛 **Error Scenarios to Test**

### **Common Issues**

**Issue 1: Python Not Found**
```
'python' is not recognized as an internal or external command
```
**Solution**: Reinstall Python with "Add to PATH" checked

**Issue 2: Permission Errors**
```
Permission denied: ...
```
**Solution**: Run as Administrator or check antivirus

**Issue 3: Hotkeys Don't Work**
```
Global hotkey listener started for ctrl+ctrl
```
- Check if other apps use Ctrl+Ctrl hotkey
- Try different hotkey in settings
- Restart app after changing hotkey

**Issue 4: System Tray Missing**
- Check Windows notification area settings
- Try "Show hidden icons" in system tray
- Restart Windows Explorer if needed

## 📊 **Performance Testing**

### **Memory Usage**
- [ ] Check Task Manager during use
- [ ] Memory should be < 100MB normally
- [ ] Memory stable during long sessions
- [ ] No significant memory leaks

### **Startup Time**
- [ ] First run: ~30-60 seconds (dependency install)
- [ ] Subsequent runs: ~5-10 seconds  
- [ ] Hotkeys active within 15 seconds
- [ ] Search results appear < 1 second

### **Search Performance**
- [ ] Search results appear instantly (<100ms)
- [ ] No lag when typing in search box
- [ ] Smooth scrolling in results
- [ ] No freezing during search

## 🔍 **Advanced Testing**

### **Multi-Monitor Setup**
- [ ] Search window appears on correct monitor
- [ ] Window doesn't go off-screen
- [ ] Cursor positioning works correctly
- [ ] All monitors work the same way

### **Windows 11 Specific**
- [ ] Works with Windows 11 UI changes
- [ ] System tray behavior correct
- [ ] Notifications work properly
- [ ] Dark mode support

### **Antivirus Compatibility**
- [ ] Windows Defender allows app
- [ ] Third-party antivirus doesn't block
- [ ] No false positive warnings
- [ ] Performance not degraded

## 📋 **Bug Report Template**

If you find issues, please include:

```
**Windows Version**: (e.g., Windows 11 22H2)
**Python Version**: (run `python --version`)
**Issue Type**: [Startup/Hotkeys/Search/UI/Performance/Other]

**Steps to Reproduce**:
1. 
2. 
3. 

**Expected Behavior**:

**Actual Behavior**:

**Error Messages** (if any):

**Screenshots** (if applicable):

**System Specs**:
- RAM: 
- CPU: 
- Antivirus: 
- Other global hotkey apps: 
```

## ✅ **Success Criteria**

The Dictionary App passes Windows testing if:

- [x] **Installs cleanly** without manual dependency management
- [x] **Hotkeys work reliably** across different apps
- [x] **System tray integration** functions properly  
- [x] **Search is fast and accurate** with 25K+ entries
- [x] **Memory usage is reasonable** (<100MB typical)
- [x] **Settings persist** between sessions
- [x] **No crashes or freezes** during normal use
- [x] **Works with common antivirus** software

## 🎉 **Next Steps**

After successful Windows testing:

1. **Report results** with the template above
2. **Performance metrics** (startup time, memory usage, search speed)
3. **Compatibility notes** (Windows version, antivirus, other software)
4. **Feature requests** for Windows-specific improvements
5. **UI/UX feedback** for better Windows integration

**Thank you for testing!** Your feedback helps make this dictionary app better for all Windows users. 🙏
