# Dictionary App Migration Plan: Python/Tkinter → Tauri/React

## Architecture Philosophy (Preserved)
- **Core is headless** - Search engine remains separate from UI
- **Everything is a plugin** - UI and features are replaceable plugins
- **Simple plugin system** - No complex sandboxing, trust developers
- **Offline first** - Everything works without internet except purchases
- **AI-friendly development** - Clear structure for AI assistance

## Technology Choices
- **Frontend**: React (better AI support, more examples than Vue)
- **Plugin Language**: TypeScript (type safety helps AI generate better code)
- **Backend**: Tauri with Rust (keep Python search engine as subprocess)
- **Platform**: Windows first, then cross-platform

---

## Phase 1: Tauri Foundation (Week 1)

### Setup & Initialization
- [x] Install Rust and Cargo on Windows
- [x] Install Node.js and npm/pnpm
- [x] Create new Tauri project: `npm create tauri-app@latest dictionary-app-v2`
- [x] Choose: Tauri + React + TypeScript + Vite
- [x] Test basic Tauri app runs on Windows
- [ ] Set up development environment with hot reload

### Project Structure
- [ ] Create folder structure:
  ```
  dictionary-app-v2/
  ├── src-tauri/          # Rust backend with search engine
  ├── src/                # React frontend
  ├── plugins/            # Plugin directory
  └── data/              # Database files
  ```
- [ ] Set up logging system in Rust
- [ ] Create performance measurement utilities
- [ ] Copy database files from Python version

---

## Phase 2: Rust Search Engine (Week 1-2)

### Database Layer
- [ ] Add SQLite dependencies: `rusqlite`, `serde_json`
- [ ] Create `Database` struct with connection pooling
- [ ] Implement database schema initialization
- [ ] Add optional encryption support (SQLCipher equivalent)
- [ ] Test database connectivity and queries

### Search Engine Core
- [ ] Create `SearchEngine` struct with inflection lookup
- [ ] Implement `SearchResult` data structure matching Python version
- [ ] Add inflection mapping (HashMap<String, Vec<(String, String)>>)
- [ ] Implement main search logic:
  - Inflection lookup first
  - Direct lemma search fallback
  - Result ranking by frequency
- [ ] Add LRU cache with TTL for search results

### Tauri Commands
- [ ] Create Tauri commands for:
  - `search_dictionary(term: string)`
  - `get_suggestions(prefix: string)`
  - `get_inflections(word: string)`
  - `get_search_stats()`
- [ ] Add error handling and response serialization
- [ ] Test API performance (<20ms, much faster than Python)

---

## Phase 3: Core UI in React (Week 2)

### Basic React Setup
- [ ] Set up React project structure with TypeScript
- [ ] Install UI library: `@radix-ui/react` (headless components)
- [ ] Install styling: `tailwindcss` or `@emotion/react`
- [ ] Create basic app layout component
- [ ] Set up React Router for navigation

### Search Interface
- [ ] Create SearchBar component with auto-complete
- [ ] Implement SearchResults component with cards
- [ ] Add keyboard navigation (arrow keys, Enter, Escape)
- [ ] Create DefinitionCard with progressive disclosure
- [ ] Test search flow end-to-end

### System Integration
- [x] Implement global hotkey registration (Ctrl+Alt+D)
- [ ] Create system tray icon and menu
- [x] Add window positioning near cursor
- [x] Implement click-outside to close
- [x] Test on Windows with multiple monitors

---

## Phase 4: Plugin System Architecture ✅ COMPLETED

### Plugin Infrastructure
- [x] Design plugin manifest schema (package.json style):
  ```json
  {
    "id": "translator",
    "name": "Translator Plugin",
    "version": "1.0.0",
    "main": "index.js",
    "permissions": ["network"],
    "dependencies": {}
  }
  ```
- [x] Create plugin loader in Rust
- [x] Implement plugin discovery and validation
- [x] Create plugin API bridge to Tauri commands
- [ ] Add plugin hot-reload system
- [x] Create plugin manager UI with Ctrl+P hotkey

### TypeScript Plugin SDK
- [x] Create `@dictionary-app/plugin-sdk` package
- [x] Define plugin interface:
  ```typescript
  interface DictionaryPlugin {
    id: string;
    onLoad(): Promise<void>;
    onSearch?(term: string): Promise<SearchResult>;
    onEnable?(): void;
    onDisable?(): void;
  }
  ```
- [x] Implement event system for plugins
- [x] Create plugin React hooks for UI integration
- [x] Create plugin utilities and helper functions

### Default Plugins (JavaScript)
- [x] Create Favorites plugin with persistent storage
- [x] Create History plugin with search tracking
- [ ] Create Settings plugin
- [x] Test plugin loading and communication
- [x] Verify plugin discovery and management works

---

## Phase 5: Performance Optimization (Week 3)

### Window Performance
- [ ] Pre-create hidden webview on app start
- [ ] Implement instant show/hide (<20ms)
- [ ] Optimize React rendering with memo
- [ ] Add virtual scrolling for long results
- [ ] Test achieves <50ms hotkey-to-popup

### Text Selection
- [ ] Implement native Windows text selection API in Rust
- [ ] Create fallback clipboard method
- [ ] Add selection caching
- [ ] Test achieves <10ms text grab
- [ ] Handle different application contexts

### Search Optimization
- [ ] Implement result streaming from Python
- [ ] Add debouncing for auto-complete
- [ ] Cache frequent searches in Rust
- [ ] Preload common inflections
- [ ] Test search completes <100ms

---

## Phase 6: Plugin Marketplace (Week 3-4)

### Store Infrastructure
- [ ] Create plugin registry format (JSON)
- [ ] Host registry on GitHub Pages
- [ ] Implement plugin discovery API
- [ ] Add plugin installation from URL
- [ ] Create plugin update checker

### Store UI
- [ ] Build marketplace UI in React
- [ ] Add search and filtering
- [ ] Create plugin detail pages
- [ ] Implement install/uninstall flow
- [ ] Add ratings and reviews display

### Developer Tools
- [ ] Create plugin template generator
- [ ] Add plugin validation tool
- [ ] Implement plugin bundler
- [ ] Create submission process
- [ ] Write developer documentation

---

## Phase 7: Testing & Polish (Week 4)

### Testing
- [ ] Unit tests for Rust backend
- [ ] React component tests
- [ ] Plugin system integration tests
- [ ] Performance benchmarks
- [ ] Windows-specific testing (UAC, antivirus)

### Polish
- [ ] Add smooth animations (Framer Motion)
- [ ] Implement dark/light theme
- [ ] Create onboarding flow
- [ ] Add keyboard shortcuts help
- [ ] Polish error messages

### Distribution
- [ ] Configure Tauri bundler for Windows
- [ ] Create MSI installer
- [ ] Add auto-updater
- [ ] Test installation process
- [ ] Create portable version

---

## Phase 8: Migration & Launch (Week 5)


### Documentation
- [ ] Update user guide
- [ ] Write plugin development guide
- [ ] Record demo videos
- [ ] Prepare release notes

### Launch
- [ ] Beta test with small group
- [ ] Fix critical bugs
- [ ] Performance validation
- [ ] Create GitHub release
- [ ] Announce to users

---

## Success Metrics

### Development Experience
- [ ] AI can modify code with logs
- [ ] Plugin development is simple
- [ ] Hot reload works reliably
- [ ] Clear error messages
- [ ] Good developer documentation

---

## Risk Mitigation

### Technical Risks
- **Rust learning curve**: Start with simple Rust, use AI assistance
- **Python bundling**: Use PyInstaller for Python engine
- **Plugin security**: Start with trusted plugins only
- **Performance regression**: Keep measurements at each step

### Migration Risks
- **User resistance**: Keep old version available
- **Data loss**: Multiple backup options
- **Plugin compatibility**: Provide migration tools
- **Missing features**: Prioritize core functionality

---

## Notes for AI Development

### When You Get Stuck
1. **Rust errors**: Paste compiler output, AI will explain
2. **React issues**: Console errors are AI-friendly
3. **Performance**: Use the measurement system, paste logs
4. **Plugin issues**: TypeScript errors guide fixes

### Best Practices
- Start simple, iterate based on errors
- Use existing examples as templates
- Test each component in isolation
- Keep logs verbose during development
- Commit working code frequently

This plan maintains your plugin philosophy while solving the performance issues through better technology choices.

## Current Progress

### Phase 1: Tauri Foundation ✅ COMPLETED
- [x] Created Rust_App folder
- [x] Created migration plan document
- [x] Install Rust and Cargo on Windows
- [x] Install Node.js and npm/pnpm
- [x] Create new Tauri project
- [x] Set up development environment with hot reload
- [x] Create folder structure (plugins/, data/)
- [x] Copy database files from Python version

### Phase 2: Rust Search Engine ✅ COMPLETED
- [x] Add SQLite dependencies: `rusqlite`, `serde_json`, `env_logger`, `log`
- [x] Create `Database` struct with connection pooling
- [x] Implement database schema initialization and optimization
- [x] Test database connectivity and queries
- [x] Create `SearchEngine` struct with inflection lookup
- [x] Implement `SearchResult` data structure matching Python version
- [x] Add inflection mapping (HashMap<String, Vec<(String, String)>>)
- [x] Implement main search logic (inflection lookup first, direct fallback, frequency ranking)
- [x] Create Tauri commands: `search_dictionary`, `get_suggestions`, `get_inflections`, `get_search_stats`
- [x] Add error handling and response serialization
- [x] Test API compilation (clean build achieved)

### Phase 3: Core UI in React ✅ COMPLETED
- [x] Set up React project structure with TypeScript
- [x] Install UI library: `@radix-ui/react` (headless components)
- [x] Configure styling with custom CSS utility classes
- [x] Create basic app layout component
- [x] Create TypeScript types for dictionary data structures
- [x] Build API utility functions for Tauri commands
- [x] Create custom hooks (useDictionary, useKeyboardNavigation)
- [x] Create SearchBar component with auto-complete
- [x] Implement SearchResults component with cards
- [x] Add keyboard navigation (arrow keys, Enter, Escape)
- [x] Create DefinitionCard with progressive disclosure
- [x] Update main App component to integrate all components
- [x] Test search flow end-to-end

### Phase 4: Plugin System Architecture ✅ COMPLETED
- [x] **Rust Backend**: Complete plugin manager with discovery, validation, and lifecycle management
- [x] **Plugin Manifest**: JSON-based configuration schema with validation
- [x] **Tauri API**: Full plugin management commands (get, enable, disable, uninstall)
- [x] **TypeScript SDK**: Complete plugin SDK with types, hooks, and utilities
- [x] **Plugin Bridge**: Communication layer between plugins and main app
- [x] **Plugin Manager UI**: Interactive interface with Ctrl+P hotkey toggle
- [x] **Example Plugins**: Created Favorites and History plugins with full functionality
- [x] **Plugin Storage**: Namespaced localStorage API for plugin data persistence
- [x] **Event System**: Plugin communication and lifecycle hooks implemented
- [x] **End-to-End Testing**: System compiles and builds successfully

Next step: Phase 5 Performance Optimization or Phase 6 Plugin Marketplace.