import { useState, useEffect, useCallback, useRef } from 'react';
import { DictionaryAPI, apiUtils } from '../utils/api';
import type { SearchState, SearchResult, Suggestion, SearchConfig } from '../types';

const DEFAULT_CONFIG: SearchConfig = {
  debounceMs: 300,
  maxSuggestions: 8,
  maxResults: 50,
  enableInflectionSearch: true,
  enableFuzzySearch: false,
  cacheResults: true
};

export const useDictionary = (config: Partial<SearchConfig> = {}) => {
  const finalConfig = { ...DEFAULT_CONFIG, ...config };
  
  const [searchState, setSearchState] = useState<SearchState>({
    query: '',
    results: [],
    suggestions: [],
    isLoading: false,
    error: null,
    selectedIndex: -1,
    hasSearched: false
  });

  const [isInitialized, setIsInitialized] = useState(false);
  const [initializationError, setInitializationError] = useState<string | null>(null);
  
  // Cache for search results and suggestions
  const searchCache = useRef(new Map<string, SearchResult[]>());
  const suggestionCache = useRef(new Map<string, Suggestion[]>());
  
  // Debounced search and suggestion functions
  const debouncedSearch = useRef(
    apiUtils.debounce(async (query: string) => {
      if (!apiUtils.isValidQuery(query)) {
        setSearchState(prev => ({ ...prev, results: [], hasSearched: false }));
        return;
      }

      const normalizedQuery = apiUtils.normalizeQuery(query);
      
      // Check cache first
      if (finalConfig.cacheResults && searchCache.current.has(normalizedQuery)) {
        const cachedResults = searchCache.current.get(normalizedQuery)!;
        setSearchState(prev => ({
          ...prev,
          results: cachedResults,
          isLoading: false,
          error: null,
          hasSearched: true,
          selectedIndex: cachedResults.length > 0 ? 0 : -1
        }));
        return;
      }

      setSearchState(prev => ({ ...prev, isLoading: true, error: null }));

      const response = await DictionaryAPI.searchDictionary(normalizedQuery);

      if (response.success) {
        const results = response.data.results.slice(0, finalConfig.maxResults);
        
        // Cache the results
        if (finalConfig.cacheResults) {
          searchCache.current.set(normalizedQuery, results);
        }

        setSearchState(prev => ({
          ...prev,
          results,
          isLoading: false,
          hasSearched: true,
          selectedIndex: results.length > 0 ? 0 : -1
        }));
      } else {
        setSearchState(prev => ({
          ...prev,
          results: [],
          isLoading: false,
          error: response.error.message,
          hasSearched: true,
          selectedIndex: -1
        }));
      }
    }, finalConfig.debounceMs)
  );

  const debouncedGetSuggestions = useRef(
    apiUtils.debounce(async (prefix: string) => {
      if (!prefix.trim() || prefix.length < 2) {
        setSearchState(prev => ({ ...prev, suggestions: [] }));
        return;
      }

      const normalizedPrefix = apiUtils.normalizeQuery(prefix);
      
      // Check cache first
      if (finalConfig.cacheResults && suggestionCache.current.has(normalizedPrefix)) {
        const cachedSuggestions = suggestionCache.current.get(normalizedPrefix)!;
        setSearchState(prev => ({ ...prev, suggestions: cachedSuggestions }));
        return;
      }

      const response = await DictionaryAPI.getSuggestions(normalizedPrefix, finalConfig.maxSuggestions);

      if (response.success) {
        const suggestions = response.data.suggestions;
        
        // Cache the suggestions
        if (finalConfig.cacheResults) {
          suggestionCache.current.set(normalizedPrefix, suggestions);
        }

        setSearchState(prev => ({ ...prev, suggestions }));
      }
    }, Math.min(200, finalConfig.debounceMs))
  );

  // Initialize the dictionary API
  useEffect(() => {
    const initialize = async () => {
      const response = await DictionaryAPI.initialize();
      if (response.success) {
        setIsInitialized(true);
        setInitializationError(null);
      } else {
        setIsInitialized(false);
        setInitializationError(response.error.message);
      }
    };

    initialize();
  }, []);

  // Search function
  const search = useCallback((query: string) => {
    setSearchState(prev => ({ ...prev, query }));
    if (isInitialized) {
      debouncedSearch.current(query);
    }
  }, [isInitialized]);

  // Get suggestions function
  const getSuggestions = useCallback((prefix: string) => {
    if (isInitialized) {
      debouncedGetSuggestions.current(prefix);
    }
  }, [isInitialized]);

  // Clear search
  const clearSearch = useCallback(() => {
    setSearchState({
      query: '',
      results: [],
      suggestions: [],
      isLoading: false,
      error: null,
      selectedIndex: -1,
      hasSearched: false
    });
  }, []);

  // Set selected index
  const setSelectedIndex = useCallback((index: number) => {
    const maxIndex = searchState.results.length - 1;
    const newIndex = Math.max(-1, Math.min(maxIndex, index));
    setSearchState(prev => ({ ...prev, selectedIndex: newIndex }));
  }, [searchState.results.length]);

  // Navigate selection up
  const navigateUp = useCallback(() => {
    setSelectedIndex(searchState.selectedIndex - 1);
  }, [searchState.selectedIndex, setSelectedIndex]);

  // Navigate selection down
  const navigateDown = useCallback(() => {
    setSelectedIndex(searchState.selectedIndex + 1);
  }, [searchState.selectedIndex, setSelectedIndex]);

  // Get selected result
  const getSelectedResult = useCallback((): SearchResult | null => {
    if (searchState.selectedIndex >= 0 && searchState.selectedIndex < searchState.results.length) {
      return searchState.results[searchState.selectedIndex];
    }
    return null;
  }, [searchState.selectedIndex, searchState.results]);

  // Clear cache
  const clearCache = useCallback(() => {
    searchCache.current.clear();
    suggestionCache.current.clear();
  }, []);

  return {
    // State
    ...searchState,
    isInitialized,
    initializationError,
    
    // Actions
    search,
    getSuggestions,
    clearSearch,
    setSelectedIndex,
    navigateUp,
    navigateDown,
    getSelectedResult,
    clearCache,
    
    // Computed values
    hasResults: searchState.results.length > 0,
    hasSuggestions: searchState.suggestions.length > 0,
    canNavigate: searchState.results.length > 0,
    
    // Config
    config: finalConfig
  };
};