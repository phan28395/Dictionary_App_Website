import React, { useEffect, useState, useCallback, useRef } from 'react';
import { PluginAPI, SearchResult, PluginEvent, PluginEventType, PluginInfo } from './types';
import { getPluginAPI } from './plugin-sdk';

// Hook for accessing the plugin API
export function usePluginAPI(): PluginAPI {
  return getPluginAPI();
}

// Hook for dictionary search with caching
export function useDictionarySearch(initialTerm = '') {
  const [term, setTerm] = useState(initialTerm);
  const [result, setResult] = useState<SearchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const api = usePluginAPI();
  const cache = useRef(new Map<string, SearchResult>());

  const search = useCallback(async (searchTerm: string) => {
    if (!searchTerm.trim()) {
      setResult(null);
      setError(null);
      return;
    }

    // Check cache first
    if (cache.current.has(searchTerm)) {
      setResult(cache.current.get(searchTerm)!);
      setError(null);
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const searchResult = await api.search(searchTerm);
      cache.current.set(searchTerm, searchResult);
      setResult(searchResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
      setResult(null);
    } finally {
      setLoading(false);
    }
  }, [api]);

  useEffect(() => {
    if (term) {
      search(term);
    }
  }, [term, search]);

  return {
    term,
    setTerm,
    result,
    loading,
    error,
    search,
    clearCache: () => cache.current.clear(),
  };
}

// Hook for autocomplete suggestions with debouncing
export function useSuggestions(prefix: string, delay = 300, limit = 10) {
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  
  const api = usePluginAPI();

  useEffect(() => {
    if (!prefix.trim()) {
      setSuggestions([]);
      return;
    }

    setLoading(true);
    
    const timeoutId = setTimeout(async () => {
      try {
        const result = await api.getSuggestions(prefix, limit);
        setSuggestions(result);
      } catch (error) {
        console.error('Failed to get suggestions:', error);
        setSuggestions([]);
      } finally {
        setLoading(false);
      }
    }, delay);

    return () => clearTimeout(timeoutId);
  }, [prefix, delay, limit, api]);

  return { suggestions, loading };
}

// Hook for plugin events
export function usePluginEvent(
  eventType: PluginEventType,
  handler: (event: PluginEvent) => void,
  deps: React.DependencyList = []
) {
  const api = usePluginAPI();
  
  useEffect(() => {
    api.on(eventType, handler);
    return () => api.off(eventType, handler);
  }, [api, eventType, ...deps]);
}

// Hook for plugin storage
export function usePluginStorage<T>(key: string, defaultValue: T) {
  const [value, setValue] = useState<T>(defaultValue);
  const [loading, setLoading] = useState(true);
  
  const api = usePluginAPI();

  useEffect(() => {
    const loadValue = async () => {
      try {
        const stored = await api.storage.get(key);
        setValue(stored !== null ? stored : defaultValue);
      } catch (error) {
        console.error(`Failed to load storage key ${key}:`, error);
        setValue(defaultValue);
      } finally {
        setLoading(false);
      }
    };

    loadValue();
  }, [key, defaultValue, api.storage]);

  const updateValue = useCallback(async (newValue: T) => {
    try {
      await api.storage.set(key, newValue);
      setValue(newValue);
    } catch (error) {
      console.error(`Failed to save storage key ${key}:`, error);
    }
  }, [key, api.storage]);

  const removeValue = useCallback(async () => {
    try {
      await api.storage.remove(key);
      setValue(defaultValue);
    } catch (error) {
      console.error(`Failed to remove storage key ${key}:`, error);
    }
  }, [key, defaultValue, api.storage]);

  return {
    value,
    setValue: updateValue,
    removeValue,
    loading,
  };
}

// Hook for managing plugin list
export function usePlugins() {
  const [plugins, setPlugins] = useState<PluginInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const api = usePluginAPI();

  const loadPlugins = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const pluginList = await api.getPlugins();
      setPlugins(pluginList);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load plugins');
    } finally {
      setLoading(false);
    }
  }, [api]);

  const enablePlugin = useCallback(async (id: string) => {
    try {
      await api.enablePlugin(id);
      await loadPlugins(); // Reload to get updated state
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to enable plugin');
    }
  }, [api, loadPlugins]);

  const disablePlugin = useCallback(async (id: string) => {
    try {
      await api.disablePlugin(id);
      await loadPlugins(); // Reload to get updated state
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to disable plugin');
    }
  }, [api, loadPlugins]);

  useEffect(() => {
    loadPlugins();
  }, [loadPlugins]);

  // Listen for plugin events to refresh the list
  usePluginEvent('plugin-enabled', loadPlugins);
  usePluginEvent('plugin-disabled', loadPlugins);

  return {
    plugins,
    loading,
    error,
    reload: loadPlugins,
    enablePlugin,
    disablePlugin,
  };
}

// Hook for notifications
export function useNotifications() {
  const api = usePluginAPI();
  
  return {
    showInfo: (message: string) => api.ui.showNotification(message, 'info'),
    showSuccess: (message: string) => api.ui.showNotification(message, 'success'),
    showWarning: (message: string) => api.ui.showNotification(message, 'warning'),
    showError: (message: string) => api.ui.showNotification(message, 'error'),
  };
}