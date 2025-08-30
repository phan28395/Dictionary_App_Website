# Testing Directory

This folder contains all test files for the Dictionary App.

## Test Files

### Core Tests
- `test_simple.py` - Basic functionality test (console output)
- `test_no_input.py` - Non-interactive comprehensive test
- `test_core.py` - Core engine components test
- `quick_test.py` - Quick validation test

### Feature Tests  
- `test_complete.py` - Full integration test with all plugins
- `test_extension_store.py` - Extension marketplace functionality
- `test_gui.py` - GUI components test
- `test_ui.py` - UI plugin test

## Running Tests

```bash
# From dictionary_app/ root directory:

# Basic functionality
python testing/test_simple.py

# Non-interactive comprehensive test
python testing/test_no_input.py

# Full feature test
python testing/test_complete.py

# Extension store test
python testing/test_extension_store.py
```

## Test Coverage

✅ **Database & Search**
- SQLite connection and queries
- Dictionary search with inflections
- Autocomplete suggestions

✅ **Plugin System**
- Plugin discovery and loading
- Plugin lifecycle management
- Event system communication

✅ **Core Plugins**
- Core UI (console interface)
- Settings management
- Favorites system
- Search history tracking

✅ **Extension Store**
- Registry loading and caching
- Extension browsing and filtering
- Installation tracking database
- Rating system

## Notes

- Tests may timeout due to console UI starting interactive mode
- All core functionality tests pass successfully
- Extension store works with sample registry data
- Database files are created during testing