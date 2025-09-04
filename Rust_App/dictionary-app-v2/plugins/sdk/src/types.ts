// Plugin Manifest Types (matching Rust structure)
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

// Plugin Info (for runtime)
export interface PluginInfo {
  manifest: PluginManifest;
  path: string;
  loaded: boolean;
  error?: string;
}

// Dictionary Types (matching the search engine)
export interface SearchResult {
  terms: DictionaryTerm[];
  query: string;
  total_results: number;
  search_time_ms: number;
}

export interface DictionaryTerm {
  lemma: string;
  pos: string;
  definition: string;
  examples: string[];
  frequency: number;
  etymology?: string;
  pronunciation?: string;
  inflections: string[];
}

// Plugin Event Types
export type PluginEventType = 
  | 'search'
  | 'result-clicked'
  | 'plugin-enabled'
  | 'plugin-disabled'
  | 'app-startup'
  | 'app-shutdown'
  | 'window-shown'
  | 'window-hidden';

export interface PluginEvent {
  type: PluginEventType;
  data?: any;
  timestamp: number;
  source: string;
}

// UI Component Props
export interface PluginComponentProps {
  plugin: PluginInfo;
  api: PluginAPI;
}

// Plugin API Interface
export interface PluginAPI {
  // Dictionary operations
  search(term: string): Promise<SearchResult>;
  getSuggestions(prefix: string, limit?: number): Promise<string[]>;
  getInflections(word: string): Promise<Array<[string, string]>>;

  // Plugin management
  getPlugins(): Promise<PluginInfo[]>;
  getPlugin(id: string): Promise<PluginInfo>;
  enablePlugin(id: string): Promise<void>;
  disablePlugin(id: string): Promise<void>;

  // Event system
  on(event: PluginEventType, handler: (event: PluginEvent) => void): void;
  off(event: PluginEventType, handler: (event: PluginEvent) => void): void;
  emit(event: PluginEventType, data?: any): void;

  // Storage (plugin-specific)
  storage: {
    get(key: string): Promise<any>;
    set(key: string, value: any): Promise<void>;
    remove(key: string): Promise<void>;
    clear(): Promise<void>;
  };

  // UI utilities
  ui: {
    showNotification(message: string, type?: 'info' | 'success' | 'warning' | 'error'): void;
    showModal(component: React.ComponentType): Promise<any>;
    addMenuItem(item: MenuItem): void;
    removeMenuItem(id: string): void;
  };
}

export interface MenuItem {
  id: string;
  label: string;
  icon?: string;
  onClick: () => void;
  separator?: boolean;
}

// Plugin Lifecycle Hooks
export interface PluginHooks {
  onLoad?(): Promise<void> | void;
  onUnload?(): Promise<void> | void;
  onEnable?(): Promise<void> | void;
  onDisable?(): Promise<void> | void;
  onSearch?(term: string): Promise<SearchResult[]> | SearchResult[];
  onEvent?(event: PluginEvent): Promise<void> | void;
}

// Main Plugin Interface
export interface DictionaryPlugin extends PluginHooks {
  readonly id: string;
  readonly name: string;
  readonly version: string;
  
  // Plugin metadata
  getManifest(): PluginManifest;
  
  // UI Components (optional)
  components?: {
    SettingsPanel?: React.ComponentType<PluginComponentProps>;
    SearchResultExtra?: React.ComponentType<PluginComponentProps & { result: SearchResult }>;
    SidebarWidget?: React.ComponentType<PluginComponentProps>;
    ContextMenu?: React.ComponentType<PluginComponentProps & { term: string }>;
  };
}