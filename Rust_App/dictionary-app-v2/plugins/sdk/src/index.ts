// Main SDK exports
export * from './types';
export * from './plugin-sdk';
export * from './hooks';

// Re-export common types for convenience
export type {
  DictionaryPlugin,
  PluginAPI,
  PluginManifest,
  PluginInfo,
  SearchResult,
  DictionaryTerm,
  PluginEvent,
  PluginEventType,
  PluginComponentProps,
  MenuItem,
} from './types';

// Re-export main classes and functions
export {
  BasePlugin,
  getPluginAPI,
  PluginAPIImpl,
} from './plugin-sdk';

// Re-export hooks
export {
  usePluginAPI,
  useDictionarySearch,
  useSuggestions,
  usePluginEvent,
  usePluginStorage,
  usePlugins,
  useNotifications,
} from './hooks';

// Version info
export const SDK_VERSION = '1.0.0';