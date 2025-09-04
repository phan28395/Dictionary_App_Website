import { useRef, useEffect, useState, useCallback } from "react";
import { useHotkeys } from "react-hotkeys-hook";
import { useDictionary, useKeyboardNavigation, useGlobalHotkeys } from "./hooks";
import { SearchBar, SearchResults } from "./components";
import PluginManager from "./components/PluginManager";
// import { apiUtils } from "./utils/api";
import type { SearchResult } from "./types";

function App() {
  const [showWelcome, setShowWelcome] = useState(true);
  const [copyMessage] = useState<string | null>(null);
  const [showPluginManager, setShowPluginManager] = useState(false);
  
  const containerRef = useRef<HTMLDivElement>(null);
  const searchBarRef = useRef<HTMLInputElement>(null);
  
  // Initialize dictionary hook
  const dictionary = useDictionary({
    debounceMs: 300,
    maxSuggestions: 8,
    maxResults: 50
  });

  // Handle search
  const handleSearch = useCallback((query: string) => {
    if (showWelcome) setShowWelcome(false);
    dictionary.search(query);
  }, [dictionary.search, showWelcome]);

  // Handle suggestion input for autocomplete
  const handleSuggestionInput = useCallback((query: string) => {
    dictionary.getSuggestions(query);
  }, [dictionary.getSuggestions]);

  // Handle result selection
  const handleResultSelect = useCallback((result: SearchResult, _index: number) => {
    console.log('Selected result:', result);
    // Here you could open a detailed view, copy to clipboard, etc.
  }, []);

  // Handle result hover for keyboard navigation
  const handleResultHover = useCallback((index: number) => {
    dictionary.setSelectedIndex(index);
  }, [dictionary.setSelectedIndex]);

  // Handle copy action (unused for now)
  // const handleCopy = useCallback((text: string) => {
  //   setCopyMessage(`Copied "${text}" to clipboard`);
  //   setTimeout(() => setCopyMessage(null), 2000);
  // }, []);

  // Keyboard navigation
  useKeyboardNavigation({
    enabled: dictionary.hasResults,
    onArrowUp: dictionary.navigateUp,
    onArrowDown: dictionary.navigateDown,
    onEnter: () => {
      const selected = dictionary.getSelectedResult();
      if (selected) {
        handleResultSelect(selected, dictionary.selectedIndex);
      }
    },
    onEscape: () => {
      dictionary.clearSearch();
      setShowWelcome(true);
    },
    scopes: ['navigation']
  });

  // Global hotkeys
  const { registerOpenHotkey } = useGlobalHotkeys();
  
  // Plugin manager hotkey
  useHotkeys('ctrl+p', (event) => {
    event.preventDefault();
    setShowPluginManager(prev => !prev);
  });

  // Focus search bar when app opens or Ctrl+Ctrl is pressed
  useEffect(() => {
    const cleanup = registerOpenHotkey(() => {
      searchBarRef.current?.focus();
    });
    
    // Focus on mount
    setTimeout(() => {
      searchBarRef.current?.focus();
    }, 100);

    return cleanup;
  }, [registerOpenHotkey]);

  // Auto-suggestions as user types
  useEffect(() => {
    if (dictionary.query && dictionary.query.length >= 2) {
      handleSuggestionInput(dictionary.query);
    }
  }, [dictionary.query, handleSuggestionInput]);

  return (
    <div 
      ref={containerRef}
      className="min-h-screen bg-gray-50 flex flex-col items-center justify-start pt-20 px-4"
    >
      {/* Main Container */}
      <div className="w-full max-w-4xl space-y-6">
        
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Dictionary App
          </h1>
          <p className="text-gray-600">
            Fast, offline dictionary with smart search and inflection support
          </p>
          
          {/* Status indicators */}
          <div className="flex items-center justify-center mt-4 space-x-4 text-sm">
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${
                dictionary.isInitialized ? 'bg-green-500' : 'bg-red-500'
              }`} />
              <span className="text-gray-600">
                {dictionary.isInitialized ? 'Ready' : 'Initializing...'}
              </span>
            </div>
            
            {dictionary.hasSearched && (
              <div className="text-gray-500">
                {dictionary.results.length} results in {dictionary.isLoading ? '...' : '< 100'}ms
              </div>
            )}
          </div>
        </div>

        {/* Search Bar */}
        <div className="space-y-4">
          <SearchBar
            value={dictionary.query}
            onChange={(value) => {
              dictionary.search(value);
              if (!value.trim()) setShowWelcome(true);
            }}
            onSubmit={handleSearch}
            placeholder="Search for any word... (Try 'running' or 'happiness')"
            isLoading={dictionary.isLoading}
            suggestions={dictionary.suggestions}
            onSuggestionSelect={handleSearch}
            className="w-full"
          />
        </div>

        {/* Error Message */}
        {dictionary.error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
            <div className="flex items-center">
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              Error: {dictionary.error}
            </div>
          </div>
        )}

        {/* Initialization Error */}
        {dictionary.initializationError && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
            <div className="flex items-center">
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              Failed to initialize: {dictionary.initializationError}
            </div>
          </div>
        )}

        {/* Welcome Message */}
        {showWelcome && !dictionary.hasSearched && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
            <div className="space-y-4">
              <div className="text-blue-900">
                <h2 className="text-xl font-semibold mb-2">Welcome to Dictionary App v2!</h2>
                <p className="text-blue-700">
                  This is the new Tauri + React version with improved performance and features.
                </p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div className="bg-white p-4 rounded-lg border border-blue-200">
                  <h3 className="font-medium text-blue-900 mb-2">🚀 Fast Search</h3>
                  <p className="text-blue-700">Rust-powered search with sub-100ms response time</p>
                </div>
                <div className="bg-white p-4 rounded-lg border border-blue-200">
                  <h3 className="font-medium text-blue-900 mb-2">🎯 Smart Suggestions</h3>
                  <p className="text-blue-700">Auto-complete with inflection support</p>
                </div>
                <div className="bg-white p-4 rounded-lg border border-blue-200">
                  <h3 className="font-medium text-blue-900 mb-2">⌨️ Keyboard Navigation</h3>
                  <p className="text-blue-700">Arrow keys, Enter, Escape, Ctrl+K</p>
                </div>
              </div>
              
              <div className="text-xs text-blue-600">
                Press Ctrl+K to focus search • Use arrow keys to navigate results • Press Ctrl+Ctrl for global access
              </div>
            </div>
          </div>
        )}

        {/* Plugin Manager */}
        {showPluginManager && (
          <PluginManager className="mt-4" />
        )}

        {/* Search Results */}
        {dictionary.hasSearched && (
          <SearchResults
            results={dictionary.results}
            selectedIndex={dictionary.selectedIndex}
            onResultSelect={handleResultSelect}
            onResultHover={handleResultHover}
            maxHeight={500}
          />
        )}

        {/* Copy Notification */}
        {copyMessage && (
          <div className="fixed bottom-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg animate-fade-in">
            {copyMessage}
          </div>
        )}

        {/* Footer */}
        <div className="text-center text-xs text-gray-500 mt-12 pb-4">
          <p>Dictionary App v2.0 • Built with Tauri + React + Rust</p>
          <p className="mt-1">Press Escape to clear • Ctrl+K to focus search • Ctrl+P for plugins</p>
        </div>
      </div>
    </div>
  );
}

export default App;