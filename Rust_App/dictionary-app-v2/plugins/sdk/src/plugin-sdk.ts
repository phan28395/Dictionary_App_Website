import { DictionaryPlugin, PluginAPI, PluginEvent, PluginEventType, PluginInfo, SearchResult } from './types';

declare global {
  interface Window {
    __DICTIONARY_PLUGIN_API__: PluginAPI;
    __TAURI__: any;
  }
}

// Event emitter for plugin events
class PluginEventEmitter {
  private handlers = new Map<PluginEventType, Set<(event: PluginEvent) => void>>();

  on(event: PluginEventType, handler: (event: PluginEvent) => void): void {
    if (!this.handlers.has(event)) {
      this.handlers.set(event, new Set());
    }
    this.handlers.get(event)!.add(handler);
  }

  off(event: PluginEventType, handler: (event: PluginEvent) => void): void {
    const handlers = this.handlers.get(event);
    if (handlers) {
      handlers.delete(handler);
    }
  }

  emit(event: PluginEventType, data?: any, source = 'plugin'): void {
    const handlers = this.handlers.get(event);
    if (handlers) {
      const eventObj: PluginEvent = {
        type: event,
        data,
        timestamp: Date.now(),
        source,
      };
      
      handlers.forEach(handler => {
        try {
          handler(eventObj);
        } catch (error) {
          console.error(`Error in event handler for ${event}:`, error);
        }
      });
    }
  }

  removeAllListeners(event?: PluginEventType): void {
    if (event) {
      this.handlers.delete(event);
    } else {
      this.handlers.clear();
    }
  }
}

// Storage implementation with localStorage fallback
class PluginStorage {
  private prefix: string;

  constructor(pluginId: string) {
    this.prefix = `plugin_${pluginId}_`;
  }

  async get(key: string): Promise<any> {
    try {
      const fullKey = this.prefix + key;
      const value = localStorage.getItem(fullKey);
      return value ? JSON.parse(value) : null;
    } catch (error) {
      console.error('Plugin storage get error:', error);
      return null;
    }
  }

  async set(key: string, value: any): Promise<void> {
    try {
      const fullKey = this.prefix + key;
      localStorage.setItem(fullKey, JSON.stringify(value));
    } catch (error) {
      console.error('Plugin storage set error:', error);
      throw error;
    }
  }

  async remove(key: string): Promise<void> {
    try {
      const fullKey = this.prefix + key;
      localStorage.removeItem(fullKey);
    } catch (error) {
      console.error('Plugin storage remove error:', error);
      throw error;
    }
  }

  async clear(): Promise<void> {
    try {
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.startsWith(this.prefix)) {
          localStorage.removeItem(key);
        }
      });
    } catch (error) {
      console.error('Plugin storage clear error:', error);
      throw error;
    }
  }
}

// Tauri command wrappers
const invokeCommand = async (command: string, args?: any): Promise<any> => {
  if (window.__TAURI__?.core?.invoke) {
    return await window.__TAURI__.core.invoke(command, args);
  }
  throw new Error('Tauri not available');
};

// Main Plugin API implementation
export class PluginAPIImpl implements PluginAPI {
  private eventEmitter: PluginEventEmitter;
  private pluginStorages = new Map<string, PluginStorage>();
  private menuItems = new Map<string, any>();

  constructor() {
    this.eventEmitter = new PluginEventEmitter();
  }

  // Dictionary operations
  async search(term: string): Promise<SearchResult> {
    return await invokeCommand('search_dictionary', { term });
  }

  async getSuggestions(prefix: string, limit = 10): Promise<string[]> {
    return await invokeCommand('get_suggestions', { prefix, limit });
  }

  async getInflections(word: string): Promise<Array<[string, string]>> {
    return await invokeCommand('get_inflections', { word });
  }

  // Plugin management
  async getPlugins(): Promise<PluginInfo[]> {
    return await invokeCommand('get_plugins');
  }

  async getPlugin(id: string): Promise<PluginInfo> {
    return await invokeCommand('get_plugin', { id });
  }

  async enablePlugin(id: string): Promise<void> {
    await invokeCommand('enable_plugin', { id });
    this.emit('plugin-enabled', { pluginId: id });
  }

  async disablePlugin(id: string): Promise<void> {
    await invokeCommand('disable_plugin', { id });
    this.emit('plugin-disabled', { pluginId: id });
  }

  // Event system
  on(event: PluginEventType, handler: (event: PluginEvent) => void): void {
    this.eventEmitter.on(event, handler);
  }

  off(event: PluginEventType, handler: (event: PluginEvent) => void): void {
    this.eventEmitter.off(event, handler);
  }

  emit(event: PluginEventType, data?: any): void {
    this.eventEmitter.emit(event, data);
  }

  // Storage factory
  get storage() {
    // This will be bound to specific plugin context
    throw new Error('Storage must be accessed through plugin context');
  }

  getStorageForPlugin(pluginId: string) {
    if (!this.pluginStorages.has(pluginId)) {
      this.pluginStorages.set(pluginId, new PluginStorage(pluginId));
    }
    return this.pluginStorages.get(pluginId)!;
  }

  // UI utilities
  ui = {
    showNotification: (message: string, type: 'info' | 'success' | 'warning' | 'error' = 'info') => {
      console.log(`[${type.toUpperCase()}] ${message}`);
      // TODO: Implement actual notification system
    },

    showModal: async (component: any): Promise<any> => {
      console.log('Show modal:', component);
      // TODO: Implement modal system
      return null;
    },

    addMenuItem: (item: any) => {
      this.menuItems.set(item.id, item);
      // TODO: Implement menu system
    },

    removeMenuItem: (id: string) => {
      this.menuItems.delete(id);
      // TODO: Implement menu system
    },
  };
}

// Plugin factory and registration
let globalPluginAPI: PluginAPIImpl | null = null;

export function getPluginAPI(): PluginAPI {
  if (!globalPluginAPI) {
    globalPluginAPI = new PluginAPIImpl();
    // Make it available globally for plugins
    window.__DICTIONARY_PLUGIN_API__ = globalPluginAPI;
  }
  return globalPluginAPI;
}

// Base plugin class for easier development
export abstract class BasePlugin implements DictionaryPlugin {
  protected api: PluginAPI;
  protected storage: PluginStorage;

  constructor(
    public readonly id: string,
    public readonly name: string,
    public readonly version: string
  ) {
    this.api = getPluginAPI();
    this.storage = (this.api as PluginAPIImpl).getStorageForPlugin(this.id);
  }

  abstract getManifest(): import('./types').PluginManifest;

  // Default implementations (can be overridden)
  async onLoad(): Promise<void> {
    console.log(`Plugin ${this.name} loaded`);
  }

  async onUnload(): Promise<void> {
    console.log(`Plugin ${this.name} unloaded`);
  }

  async onEnable(): Promise<void> {
    console.log(`Plugin ${this.name} enabled`);
  }

  async onDisable(): Promise<void> {
    console.log(`Plugin ${this.name} disabled`);
  }

  // Helper methods
  protected log(message: string): void {
    console.log(`[${this.name}] ${message}`);
  }

  protected error(message: string, error?: any): void {
    console.error(`[${this.name}] ${message}`, error);
  }
}