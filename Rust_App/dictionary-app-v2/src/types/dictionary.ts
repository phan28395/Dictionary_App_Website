// Dictionary search result types that match Rust backend

export interface SearchResult {
  id: number;
  lemma: string;
  pos: string; // part of speech
  meanings: string; // JSON array
  definitions: string; // JSON array
  examples: string; // JSON array
  frequency_meaning: string; // JSON array of decimal weights
}

export interface SearchResponse {
  results: SearchResult[];
  total_count: number;
  search_time_ms: number;
  query: string;
}

export interface Suggestion {
  word: string;
}

export interface SuggestionsResponse {
  suggestions: Suggestion[];
  query: string;
}

export interface InflectionInfo {
  inflected_form: string;
  grammatical_info: string;
  base_form: string;
}

export interface InflectionsResponse {
  inflections: InflectionInfo[];
  word: string;
}

export interface SearchStats {
  total_searches: number;
  cache_hits: number;
  cache_misses: number;
  average_search_time_ms: number;
  database_size: number;
  total_words: number;
}

// UI state types
export interface SearchState {
  query: string;
  results: SearchResult[];
  suggestions: Suggestion[];
  isLoading: boolean;
  error: string | null;
  selectedIndex: number;
  hasSearched: boolean;
}

export interface UIState {
  isVisible: boolean;
  position: { x: number; y: number };
  theme: 'light' | 'dark' | 'system';
  hotkeysEnabled: boolean;
}

// Component prop types
export interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: (query: string) => void;
  onFocus?: () => void;
  onBlur?: () => void;
  placeholder?: string;
  className?: string;
  isLoading?: boolean;
  suggestions?: Suggestion[];
  onSuggestionSelect?: (suggestion: string) => void;
}

export interface SearchResultsProps {
  results: SearchResult[];
  selectedIndex?: number;
  onResultSelect?: (result: SearchResult, index: number) => void;
  onResultHover?: (index: number) => void;
  className?: string;
  maxHeight?: number;
}

export interface DefinitionCardProps {
  result: SearchResult;
  isExpanded?: boolean;
  onToggleExpand?: () => void;
  onCopy?: (text: string) => void;
  onFavorite?: (result: SearchResult) => void;
  className?: string;
}

// API response types for error handling
export interface ApiError {
  message: string;
  code?: string;
  details?: any;
}

export type ApiResponse<T> = {
  success: true;
  data: T;
} | {
  success: false;
  error: ApiError;
};

// Search configuration
export interface SearchConfig {
  debounceMs: number;
  maxSuggestions: number;
  maxResults: number;
  enableInflectionSearch: boolean;
  enableFuzzySearch: boolean;
  cacheResults: boolean;
}

// Keyboard navigation
export interface KeyboardNavigation {
  selectedIndex: number;
  maxIndex: number;
  onArrowUp: () => void;
  onArrowDown: () => void;
  onEnter: () => void;
  onEscape: () => void;
}

// History and favorites
export interface HistoryEntry {
  query: string;
  timestamp: number;
  resultCount: number;
}

export interface FavoriteEntry {
  result: SearchResult;
  timestamp: number;
  tags?: string[];
}

// Plugin system types (matching Rust backend)
export interface PluginManifest {
  id: string;
  name: string;
  version: string;
  description?: string;
  author?: string;
  main: string;
  permissions: string[];
  dependencies: Record<string, string>;
  enabled: boolean;
}

export interface PluginInfo {
  manifest: PluginManifest;
  path: string;
  loaded: boolean;
  error?: string;
}

export interface PluginManagerStats {
  total: number;
  enabled: number;
  loaded: number;
  errors: number;
}