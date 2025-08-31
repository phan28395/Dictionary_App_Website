# Dictionary App Implementation Plan

## Project Overview
Build an extensible dictionary application with a plugin-based architecture where EVERYTHING (including UI) is a plugin. The core engine is headless and only handles dictionary search and plugin management. Monetization through core app purchase ($20) and premium extensions marketplace.

## Key Documents to Reference
- [x] Read `user_experience_flow.md` for complete UI/UX specifications including extension marketplace
- [x] Read `database_schema.sql` for complete database structure
- [x] Read `import_dictionary_data.py` to understand data import process
- [x] Check `inflection_lookup.tsv` for inflected forms mapping
- [x] Review JSON structure in `DictGenerativeRule_2/` for each POS

## Supabase Integration Overview (Authentication & Licensing Only)

### Why Supabase?
- **Authentication Only**: Handle user accounts, login, OAuth providers
- **License Validation**: Track who purchased the app
- **Minimal Cloud Dependency**: Everything else runs offline
- **Privacy First**: No user data or search history uploaded

### Supabase Setup Requirements
1. Create a Supabase project at https://supabase.com
2. Configure authentication providers in the dashboard
3. Set up minimal database tables (only for auth/licensing)
4. Configure Stripe webhook endpoint for payments
5. Set environment variables with project credentials

### Minimal Supabase Tables (Auth & Licensing Only)
```sql
-- User profile for license status
CREATE TABLE public.user_profiles (
  id UUID REFERENCES auth.users PRIMARY KEY,
  display_name TEXT,
  is_premium BOOLEAN DEFAULT false,
  license_key TEXT UNIQUE,
  license_activated_at TIMESTAMPTZ,
  stripe_customer_id TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Track app purchases only
CREATE TABLE public.purchases (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users NOT NULL,
  product_type TEXT NOT NULL, -- 'core_app' or 'extension_name'
  stripe_payment_id TEXT UNIQUE,
  amount DECIMAL(10,2),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Device activations for license limits
CREATE TABLE public.device_activations (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users NOT NULL,
  hardware_fingerprint TEXT NOT NULL,
  device_name TEXT,
  activated_at TIMESTAMPTZ DEFAULT NOW(),
  last_seen TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, hardware_fingerprint)
);
```

### What Stays Local (NOT in Supabase)
- ✅ All dictionary data (25K+ entries)
- ✅ Search history (privacy)
- ✅ Favorites (user data)
- ✅ Settings and preferences
- ✅ Extension files
- ✅ Usage statistics
- ✅ Everything except auth & license status

## Phase 1: Project Foundation

### 1.1 Project Structure Setup
- [x] Create main project directory `dictionary_app/`
- [x] Create subdirectory structure:
  - `core/` - Headless engine (NO UI code here)
  - `plugins/` - All plugins including default UI
  - `data/` - Database and cache files
  - `config/` - Configuration files
  - `docs/` - Documentation
  - `tests/` - Test files
  - `build/` - Build artifacts
  - `temp/` - Temporary files for development

### 1.2 Python Environment Setup
- [x] Create virtual environment using Python 3.11 or higher
- [x] Create `requirements.txt` with ONLY core dependencies:
  ```
  sqlcipher3 - for encrypted database
  watchdog - for plugin hot-reload
  python-dotenv - for configuration
  ```
- [x] DO NOT include UI libraries in core requirements (they go in UI plugin)
- [x] Create separate `requirements-dev.txt` for development tools

### 1.3 Configuration System
- [x] Create `.env.example` with all configuration options documented
- [x] Implement configuration loader that reads from:
  - Environment variables (highest priority)
  - `.env` file
  - `config.json` file
  - Default values (lowest priority)
- [ ] Configuration should include:
  - Database path and encryption key derivation settings
  - Plugin directories (main and development)
  - Hot reload settings
  - API endpoints for extension marketplace
  - License validation endpoints

## Phase 2: Core Engine (Headless - NO UI)

### 2.1 Database Layer Implementation
- [x] Implement SQLite connection manager with connection pooling
- [x] Add SQLCipher encryption layer:
  - Use hardware-based key derivation (MAC address + CPU ID)
  - Store encrypted key in system keyring if available
  - Fallback to file-based encrypted storage
- [x] Create database initialization function:
  - Check if database exists
  - Run schema creation from `database_schema.sql`
  - Verify all tables and indexes exist
  - Run migrations if schema version differs
- [x] Implement database access layer with methods for:
  - Query execution with parameterized queries
  - JSON field extraction helpers
  - Transaction management
  - Connection pool management
- [ ] Create database backup/restore functionality

### 2.2 Data Import System
- [ ] Implement JSONL parser for each POS type:
  - Parse noun entries with domains, semantic_function, key_collocates
  - Parse verb entries with grammatical_patterns, semantic_roles, aspect_type
  - Parse adjective entries with all 7 specific fields
  - Parse adverb entries with basic fields only
- [ ] Create batch import system:
  - Process files in chunks of 1000 entries
  - Show progress indicators
  - Handle malformed entries gracefully
  - Log errors to file for review
- [x] Import inflection lookup from TSV:
  - Parse inflection_lookup.tsv
  - Create indexed mappings for fast lookup
  - Handle multiple inflections pointing to same lemma
- [ ] Implement data validation:
  - Verify JSON structure matches expected format
  - Check for required fields
  - Validate frequency_meaning sums to 1.0
  - Ensure examples array structure is correct

### 2.3 Search Engine Core
- [x] Implement primary search pipeline:
  1. Accept search term (may be inflected form)
  2. Normalize input (lowercase, trim whitespace)
  3. Check inflection_lookup table first
  4. If found, get lemma and POS
  5. Query dictionary_entries with lemma and POS
  6. If not found in inflections, try direct lemma search
  7. Return results with all POS variants
- [x] Implement result ranking:
  - Sort meanings by frequency_meaning values
  - Prioritize exact matches over partial
  - Consider POS frequency in corpus
- [x] Create result formatter:
  - Structure results as Python objects
  - Include all POS-specific fields
  - Format for plugin consumption (read-only)
- [x] Add search optimizations:
  - Cache frequently searched terms in memory
  - Preload common inflections
  - Use SQLite FTS5 for full-text search capability

### 2.4 Plugin System Foundation
- [x] Create Plugin base class with lifecycle methods:
  - `__init__(app)` - Initialize with app reference
  - `on_load()` - Called when plugin loads
  - `on_enable()` - Called when plugin is enabled
  - `on_disable()` - Called when plugin is disabled
  - `on_unload()` - Cleanup when plugin unloads
- [x] Implement plugin manifest parser:
  - Read and validate manifest.json structure
  - Check required fields: id, name, version, main
  - Parse optional fields: permissions, replaces, dependencies
  - Validate version compatibility
- [x] Create plugin loader:
  - Scan plugins/ directory for plugin folders
  - Load manifest.json for each plugin
  - Check dependencies and conflicts
  - Load plugins in dependency order
  - Handle circular dependencies gracefully
- [x] Implement hot-reload system:
  - Watch plugin directories for changes
  - Reload changed plugins without restart
  - Maintain plugin state during reload
  - Show reload status in developer mode

### 2.5 Event System
- [x] Create event emitter/listener system:
  - Allow plugins to emit custom events
  - Support multiple listeners per event
  - Implement event priority/ordering
  - Add wildcard event listeners
- [x] Define core events:
  - `app.ready` - Application initialized
  - `search.before` - Before search execution
  - `search.complete` - After search results
  - `plugin.loaded` - Plugin loaded
  - `plugin.unloaded` - Plugin unloaded
  - `config.changed` - Configuration updated
- [x] Implement event debugging:
  - Log all events in developer mode
  - Track event performance
  - Detect infinite event loops

### 2.6 Plugin API
- [x] Create app object exposed to plugins with:
  - `app.search(term)` - Perform dictionary search
  - `app.events` - Event system access
  - `app.config` - Read configuration
  - `app.plugins` - Access other plugins
  - `app.storage` - Plugin-specific storage
  - `app.version` - App version info
- [x] Implement plugin storage system:
  - Each plugin gets isolated storage directory
  - Support for JSON config files
  - SQLite database per plugin if needed
  - File storage with size limits
- [x] Add plugin communication:
  - Direct plugin-to-plugin messaging
  - Shared data store with permissions
  - Request/response pattern support

## Phase 3: Default Plugin Bundle

### 3.1 Core UI Plugin (`plugins/core-ui/`)
- [x] Create manifest declaring this as the default UI provider
- [x] Implement system tray integration:
  - Show dictionary icon in system tray
  - Green when active, gray when disabled
  - Right-click menu with options
  - Click to show/hide main window
- [x] Create global hotkey listener:
  - Default: Ctrl+Ctrl to trigger search
  - Detect selected text in any application
  - Show popup at cursor position
  - Handle multi-monitor setups correctly
- [x] Implement search popup window:
  - Frameless window with custom styling
  - Position near cursor without going off-screen
  - Auto-focus search box
  - ESC key to close
  - Click outside to close
- [x] Create definition card component:
  - Display lemma with pronunciation
  - Show inflection note if applicable ("went → go")
  - Multiple meanings with frequency indicators
  - Expandable examples
  - POS tabs for words with multiple parts of speech
- [x] Implement progressive disclosure:
  - Show first 2 meanings initially
  - "Show more" button for additional meanings
  - Expand examples on click
  - Smooth animations for expansion
- [x] Add favorites integration:
  - Star icon on each definition
  - Visual feedback on click
  - Emit event for favorites plugin

### 3.2 Settings Plugin (`plugins/settings/`)
- [x] Create settings window with tabs:
  - General - Hotkeys, startup options
  - Extensions - Plugin management
  - Account - License and purchases
  - Languages - Language pack management
  - About - Version and credits
- [x] Implement General settings:
  - Hotkey customization with conflict detection
  - Startup options (minimized, auto-start)
  - Notification preferences
  - Update checking frequency
- [x] Create Extensions tab (like Obsidian):
  - List installed plugins with toggle switches
  - Version numbers and descriptions
  - Settings button for each plugin
  - Browse Store button
  - Safe mode toggle
  - Reload all plugins button
  - Developer mode toggle
- [x] Implement plugin settings panels:
  - Each plugin provides settings UI
  - Dynamically load plugin settings
  - Save to plugin-specific storage
  - Apply changes without restart

### 3.3 Authentication Plugin (`plugins/auth/`) - Using Supabase
- [ ] Setup Supabase integration:
  - Install `supabase-py` dependency
  - Configure Supabase URL and anon key in environment
  - Initialize Supabase client in plugin
  - Handle connection errors gracefully
- [ ] Implement guest mode:
  - Generate unique guest ID locally
  - Store in local configuration (no Supabase account)
  - Track search count locally (50 limit)
  - Prompt to create account when approaching limit
- [ ] Create account system via Supabase Auth:
  - Email/password registration (Supabase Auth)
  - Magic link authentication option
  - Email verification (automatic via Supabase)
  - Password reset (Supabase handles email flow)
  - Remember me with persistent sessions
- [ ] Add OAuth providers via Supabase:
  - Google Sign-In (configure in Supabase dashboard)
  - GitHub authentication (configure in Supabase dashboard)
  - Apple Sign-In (configure in Supabase dashboard)
  - Microsoft Account (configure in Supabase dashboard)
  - Discord/Twitter as bonus options
- [ ] Implement session management:
  - Use Supabase session handling
  - Auto-refresh tokens (handled by Supabase)
  - Store session in secure local storage
  - Sync user preferences to Supabase database
  - Handle offline mode with cached credentials

### 3.4 Licensing Plugin (`plugins/licensing/`) - Local + Supabase Auth
- [ ] Implement free tier logic (LOCAL):
  - Track searches locally in SQLite
  - Show counter in UI from local database
  - Block search at 50 limit locally
  - No cloud tracking for privacy
  - Show upgrade prompt when limit reached
- [ ] Create license validation:
  - Check Supabase for is_premium status on login
  - Cache license status locally for offline use
  - Validate every 7 days when online
  - Hardware fingerprint stored locally
  - Work fully offline after initial activation
- [ ] Implement purchase flow:
  - Open Stripe Checkout in browser
  - Webhook updates Supabase user_profiles.is_premium
  - App polls for license status after purchase
  - Email receipt via Stripe
  - License tied to Supabase account (not device)
- [ ] Add license management:
  - Check device count via Supabase (max 3)
  - Deactivate old devices from account page
  - Transfer by logging in on new device
  - License status cached locally
  - Grace period for offline use

### 3.5 Favorites Plugin (`plugins/favorites/`) - Local Only
- [x] Create favorites database:
  - Separate SQLite file in plugin storage
  - Track: entry_id, meaning_index, timestamp, notes
  - Support for tags and categories
- [x] Implement favorites management:
  - Add/remove favorites
  - Edit notes for favorites
  - Sort by date, alphabetical, frequency
  - Search within favorites
- [x] Create favorites UI:
  - List view with search
  - Card view with full definitions
  - Export options (CSV, JSON, Anki)
  - Import from backup
- [x] Keep favorites completely local:
  - No cloud sync for privacy
  - Export/import for manual backup
  - User owns their data

### 3.6 History Plugin (`plugins/history/`) - Local Only
- [x] Track all searches:
  - Store search term and timestamp
  - Track found lemma and POS
  - Record search context (hotkey vs manual)
- [x] Implement history features:
  - Clear history (all or date range)
  - Search within history
  - History statistics
  - Most searched words
- [x] Create history UI:
  - Timeline view
  - Calendar heat map
  - Quick access to recent searches
  - Export history data
- [x] Keep history completely local:
  - No cloud tracking for privacy
  - Search count tracked locally for free tier
  - Export for personal analytics
  - User controls their data

## Phase 4: Extension Marketplace

### 4.1 Extension Store Plugin (`plugins/extension-store/`)
- [x] Create store UI matching user_experience_flow.md:
  - Browse view with cards
  - Search and filter functionality
  - Sort by: popular, new, updated, rating
  - Categories: themes, tools, languages, etc.
- [x] Implement extension registry:
  - Fetch from GitHub repository (like Obsidian)
  - Cache registry locally
  - Check for updates periodically
  - Handle offline mode gracefully
- [x] Create installation system:
  - Download extension packages
  - Verify package integrity
  - Extract to plugins directory
  - Load without restart
  - Handle dependencies
- [x] Add extension details view:
  - Screenshots and description
  - Version history
  - User ratings and reviews
  - Developer information
  - Required permissions

### 4.2 Developer Mode Features
- [ ] Create development UI:
  - Load unpacked extensions
  - Console output viewer
  - API documentation viewer
  - Performance profiler
- [ ] Implement extension creator:
  - Template selection
  - Boilerplate generation
  - Manifest builder
  - Icon generator
- [ ] Add debugging tools:
  - Event inspector
  - API call logger
  - Memory usage monitor
  - Error tracking

### 4.3 Premium Extensions System - Local Store + Supabase License
- [ ] Keep extension files local:
  - Extensions stored locally only
  - GitHub registry for discovery
  - Direct download from developer CDN
  - No cloud storage needed
- [ ] Implement paid extension support:
  - Price tiers ($0.99 - $4.99)
  - Stripe Checkout for purchases
  - Purchase record in Supabase (minimal)
  - License check via Supabase on install
  - Extensions work offline after activation
- [ ] Create developer portal (web-based):
  - Submit extensions via web portal
  - GitHub hosting for extension files
  - Analytics from download counts
  - Version management via Git tags
  - Revenue reports from Stripe dashboard
- [ ] Add review system (local + aggregate):
  - Reviews submitted to web API
  - Cached locally for offline viewing
  - Star ratings aggregated weekly
  - No personal data tracked

## Phase 5: Security and Protection

### 5.1 Database Encryption
- [ ] Implement SQLCipher integration:
  - Generate encryption key from hardware
  - Use PBKDF2 for key derivation
  - Secure key storage in OS keyring
  - Fallback encrypted file storage
- [ ] Add tampering detection:
  - Database checksum verification
  - Schema integrity checks
  - Data corruption recovery
  - Backup verification

### 5.2 Extension Security
- [ ] No sandboxing (keep it simple like Obsidian)
- [ ] Add basic security warnings:
  - Warn about extensions requesting network access
  - Show permission requirements
  - Community verification badges
  - Report malicious extensions
- [ ] Implement extension signing:
  - Optional developer signatures
  - Verification in store
  - Trust indicators in UI

### 5.3 License Protection
- [ ] Hardware fingerprinting:
  - Combine MAC address, CPU ID, disk serial
  - Handle hardware changes gracefully
  - Support virtual machines
- [ ] License file encryption:
  - RSA signature validation
  - AES encryption for content
  - Tamper detection
  - Expiry handling

## Phase 6: Performance Optimization

### 6.1 Search Optimization
- [ ] Implement caching layer:
  - Memory cache for frequent searches
  - Disk cache for full results
  - Cache invalidation strategy
  - Size limits and eviction
- [ ] Add search indexes:
  - Pre-built inflection mappings
  - Frequency-based sorting
  - Fuzzy search capability
  - Phonetic matching

### 6.2 Startup Optimization
- [ ] Lazy loading strategy:
  - Load core engine first
  - Load UI plugin immediately
  - Defer other plugins
  - Progressive plugin activation
- [ ] Minimize startup tasks:
  - Async database connection
  - Delayed index building
  - Background data loading
  - Quick splash screen

### 6.3 Memory Management
- [ ] Implement memory limits:
  - Plugin memory quotas
  - Cache size limits
  - Image compression
  - Garbage collection triggers
- [ ] Add memory monitoring:
  - Track plugin usage
  - Detect memory leaks
  - Alert on high usage
  - Automatic cleanup

## Phase 7: User Experience Polish

### 7.1 Animations and Transitions
- [ ] Add smooth animations:
  - Popup fade in/out
  - Definition card expansion
  - Tab switching
  - Loading indicators
- [ ] Implement gesture support:
  - Swipe to dismiss
  - Pinch to zoom
  - Drag to reposition
  - Touch-friendly interactions

### 7.2 Accessibility
- [ ] Screen reader support:
  - ARIA labels
  - Keyboard navigation
  - Focus indicators
  - High contrast mode
- [ ] Customization options:
  - Font size adjustment
  - Color blind modes
  - Reduce motion option
  - Custom key bindings

### 7.3 Error Handling
- [ ] User-friendly error messages:
  - Clear problem description
  - Suggested solutions
  - Help links
  - Report bug option
- [ ] Graceful degradation:
  - Offline mode
  - Plugin failures
  - Database corruption
  - Network issues

## Phase 8: Testing Strategy

### 8.1 Unit Tests
- [ ] Test search algorithm with various inputs
- [ ] Test inflection lookup accuracy
- [ ] Test plugin loading system
- [ ] Test event system
- [ ] Test database operations
- [ ] Test license validation

### 8.2 Integration Tests
- [ ] Test complete search flow
- [ ] Test plugin communication
- [ ] Test extension installation
- [ ] Test payment flow
- [ ] Test data import process

### 8.3 User Acceptance Tests
- [ ] Test 50-search limit enforcement
- [ ] Test purchase and activation
- [ ] Test extension marketplace
- [ ] Test hotkey functionality
- [ ] Test multi-monitor support

## Phase 9: Build and Distribution

### 9.1 Build System
- [ ] Create build script using PyInstaller:
  - Bundle Python and dependencies
  - Include plugins directory
  - Compress resources
  - Generate single executable
- [ ] Platform-specific builds:
  - Windows: .exe with NSIS installer
  - macOS: .app bundle with DMG
  - Linux: AppImage or Snap package
- [ ] Code signing:
  - Windows: Authenticode certificate
  - macOS: Developer ID certificate
  - Linux: GPG signature

### 9.2 Update System
- [ ] Implement auto-updater:
  - Check for updates on startup
  - Download in background
  - Verify update signature
  - Apply on restart
- [ ] Delta updates:
  - Only download changed files
  - Patch binary differences
  - Rollback on failure

### 9.3 Distribution Channels
- [ ] Direct download website:
  - Landing page with features
  - Download links
  - Documentation
  - Support contact
- [ ] Platform stores:
  - Microsoft Store (optional)
  - Mac App Store (optional)
  - Snap Store for Linux
- [ ] Enterprise deployment:
  - MSI installer for Windows
  - Mass deployment tools
  - License management
  - Update control

## Phase 10: Documentation

### 10.1 User Documentation
- [ ] Create user guide:
  - Installation instructions
  - Basic usage
  - Hotkey configuration
  - Extension installation
  - Troubleshooting
- [ ] Video tutorials:
  - Getting started
  - Installing extensions
  - Creating favorites
  - Advanced features

### 10.2 Developer Documentation
- [ ] Extension API reference:
  - All available methods
  - Event documentation
  - Code examples
  - Best practices
- [ ] Extension tutorials:
  - Hello World extension
  - Theme creation
  - Language pack creation
  - Advanced techniques
- [ ] Sample extensions:
  - Basic examples
  - Complete themes
  - Tool integrations
  - UI replacements

### 10.3 Business Documentation
- [ ] Privacy policy
- [ ] Terms of service
- [ ] License agreement
- [ ] Refund policy
- [ ] Developer agreement

## Success Metrics

### Technical Success
- [ ] Search works correctly and returns accurate results
- [ ] Application starts without errors
- [ ] Memory usage stays reasonable (don't worry about exact limits)
- [ ] Extensions load without crashing the app
- [ ] Database operations work reliably

### User Success
- [ ] Hotkey triggers search popup (speed not critical initially)
- [ ] 50-search limit properly enforced
- [ ] Extensions install without restart
- [ ] Basic animations work (60fps nice-to-have later)
- [ ] Works offline completely

### Business Success
- [ ] Payment processing works reliably
- [ ] License validation prevents piracy
- [ ] Extension store loads and functions
- [ ] Developer uploads work
- [ ] Basic analytics track usage

## Important Implementation Notes

### Architecture Principles
1. **Core is headless** - NO UI code in core, everything UI is in plugins
2. **Everything is a plugin** - Even core UI is replaceable
3. **Simple plugin system** - No complex sandboxing, trust developers like Obsidian
4. **Correct search** - Focus on accuracy over speed initially, optimize later
5. **Offline first** - Everything works without internet except purchases

### Development Workflow
1. Start with core engine (headless)
2. Build plugin system next
3. Create default UI plugin
4. Add other default plugins
5. Build extension marketplace last

### Security Considerations
1. Encrypt database with SQLCipher
2. Simple plugin system without sandboxing
3. Hardware-based licensing
4. Optional extension signing
5. Community-based trust model

### Performance Guidelines (Nice-to-Have, Not Required)
1. Get it working first, optimize later
2. Cache can help but don't over-engineer initially
3. Basic database indexes are good enough to start
4. Profile only if performance becomes a real problem
5. Functionality over speed in early development

### Testing Priorities
1. Search accuracy is critical
2. Plugin system stability
3. Payment flow reliability
4. Extension installation
5. Cross-platform compatibility

## Next Steps for Implementation

1. **Start Here**: Set up project structure and Python environment
2. **Then**: Build core engine with database and search
3. **Next**: Implement plugin system
4. **After**: Create default UI plugin
5. **Finally**: Add marketplace and monetization

Remember: Keep it simple, make it extensible, and focus on search speed!

## CRITICAL RULE: Session Summary Documentation

### Session History Location
📁 **All session summaries are stored in: `development/SESSION_HISTORY.md`**

### When Implementation Continues
**MANDATORY**: 
1. **FIRST** read `development/SESSION_HISTORY.md` to understand current state
2. **AFTER** each development session, update `development/SESSION_HISTORY.md` with new summary at the top

### Session Summary Format
```markdown
## Session Summary - [Date] (Brief Title)

### Completed Tasks
- [x] Checkbox item that was finished
- [x] Another completed item

### Files Created/Modified
- `path/to/file.py` - Brief description of what it does
- `path/to/config.json` - Configuration changes made

### Current State
Brief description of what's working and what's not.

### Next Session Should Start With
1. Specific task to begin with
2. Any setup needed
3. Files to examine first

### Decisions Made
- Architecture choice and reasoning
- Any deviations from the original plan

### Open Questions/Blockers
- Issues that need user input
- Technical decisions to be made
```

### Why This Is Critical
Without session summaries, the next AI will:
- ❌ Waste time figuring out what was done
- ❌ Potentially redo completed work  
- ❌ Miss important context and decisions
- ❌ Make conflicting architectural choices

With session summaries, the next AI can:
- ✅ Immediately understand the current state
- ✅ Continue exactly where previous session ended
- ✅ Build on previous decisions
- ✅ Focus on productive work immediately

### Current Status
**Latest Update**: See `development/SESSION_HISTORY.md` for complete development history and current state.

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.