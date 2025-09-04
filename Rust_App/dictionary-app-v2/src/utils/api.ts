import { invoke } from '@tauri-apps/api/core';
import type {
  SearchResponse,
  SuggestionsResponse,
  InflectionsResponse,
  SearchStats,
  ApiResponse,
  SearchResult,
  Suggestion,
  InflectionInfo,
  PluginInfo,
  PluginManagerStats
} from '../types';

// API wrapper functions for Tauri commands
export class DictionaryAPI {
  private static isInitialized = false;

  /**
   * Initialize the search engine with database paths
   */
  static async initialize(): Promise<ApiResponse<void>> {
    try {
      await invoke('initialize_search_engine');
      await invoke('initialize_plugin_manager');
      this.isInitialized = true;
      return { success: true, data: undefined };
    } catch (error) {
      console.error('Failed to initialize:', error);
      return {
        success: false,
        error: {
          message: error instanceof Error ? error.message : 'Failed to initialize application',
          code: 'INIT_ERROR'
        }
      };
    }
  }

  /**
   * Search dictionary for a term with inflection support
   */
  static async searchDictionary(term: string): Promise<ApiResponse<SearchResponse>> {
    try {
      if (!this.isInitialized) {
        await this.initialize();
      }

      const startTime = Date.now();
      const results: SearchResult[] = await invoke('search_dictionary', { term });
      const searchTime = Date.now() - startTime;

      const response: SearchResponse = {
        results,
        total_count: results.length,
        search_time_ms: searchTime,
        query: term
      };

      return { success: true, data: response };
    } catch (error) {
      console.error('Search failed:', error);
      return {
        success: false,
        error: {
          message: error instanceof Error ? error.message : 'Search failed',
          code: 'SEARCH_ERROR'
        }
      };
    }
  }

  /**
   * Get autocomplete suggestions for a prefix
   */
  static async getSuggestions(prefix: string, limit = 10): Promise<ApiResponse<SuggestionsResponse>> {
    try {
      if (!this.isInitialized) {
        await this.initialize();
      }

      const suggestions: Suggestion[] = await invoke('get_suggestions', { prefix, limit });

      const response: SuggestionsResponse = {
        suggestions,
        query: prefix
      };

      return { success: true, data: response };
    } catch (error) {
      console.error('Failed to get suggestions:', error);
      return {
        success: false,
        error: {
          message: error instanceof Error ? error.message : 'Failed to get suggestions',
          code: 'SUGGESTIONS_ERROR'
        }
      };
    }
  }

  /**
   * Get inflections for a specific word
   */
  static async getInflections(word: string): Promise<ApiResponse<InflectionsResponse>> {
    try {
      if (!this.isInitialized) {
        await this.initialize();
      }

      const inflections: InflectionInfo[] = await invoke('get_inflections', { word });

      const response: InflectionsResponse = {
        inflections,
        word
      };

      return { success: true, data: response };
    } catch (error) {
      console.error('Failed to get inflections:', error);
      return {
        success: false,
        error: {
          message: error instanceof Error ? error.message : 'Failed to get inflections',
          code: 'INFLECTIONS_ERROR'
        }
      };
    }
  }

  /**
   * Get search statistics and performance metrics
   */
  static async getSearchStats(): Promise<ApiResponse<SearchStats>> {
    try {
      if (!this.isInitialized) {
        await this.initialize();
      }

      const stats: SearchStats = await invoke('get_search_stats');
      return { success: true, data: stats };
    } catch (error) {
      console.error('Failed to get search stats:', error);
      return {
        success: false,
        error: {
          message: error instanceof Error ? error.message : 'Failed to get search stats',
          code: 'STATS_ERROR'
        }
      };
    }
  }

  /**
   * Toggle window visibility
   */
  static async toggleWindow(): Promise<ApiResponse<void>> {
    try {
      await invoke('toggle_window');
      return { success: true, data: undefined };
    } catch (error) {
      console.error('Failed to toggle window:', error);
      return {
        success: false,
        error: {
          message: error instanceof Error ? error.message : 'Failed to toggle window',
          code: 'WINDOW_ERROR'
        }
      };
    }
  }

  /**
   * Hide window
   */
  static async hideWindow(): Promise<ApiResponse<void>> {
    try {
      await invoke('hide_window');
      return { success: true, data: undefined };
    } catch (error) {
      console.error('Failed to hide window:', error);
      return {
        success: false,
        error: {
          message: error instanceof Error ? error.message : 'Failed to hide window',
          code: 'WINDOW_ERROR'
        }
      };
    }
  }

  // Plugin Management API
  /**
   * Get all discovered plugins
   */
  static async getPlugins(): Promise<ApiResponse<PluginInfo[]>> {
    try {
      const plugins: PluginInfo[] = await invoke('get_plugins');
      return { success: true, data: plugins };
    } catch (error) {
      console.error('Failed to get plugins:', error);
      return {
        success: false,
        error: {
          message: error instanceof Error ? error.message : 'Failed to get plugins',
          code: 'PLUGINS_ERROR'
        }
      };
    }
  }

  /**
   * Get specific plugin by ID
   */
  static async getPlugin(id: string): Promise<ApiResponse<PluginInfo>> {
    try {
      const plugin: PluginInfo = await invoke('get_plugin', { id });
      return { success: true, data: plugin };
    } catch (error) {
      console.error(`Failed to get plugin ${id}:`, error);
      return {
        success: false,
        error: {
          message: error instanceof Error ? error.message : `Failed to get plugin ${id}`,
          code: 'PLUGIN_ERROR'
        }
      };
    }
  }

  /**
   * Enable a plugin
   */
  static async enablePlugin(id: string): Promise<ApiResponse<void>> {
    try {
      await invoke('enable_plugin', { id });
      return { success: true, data: undefined };
    } catch (error) {
      console.error(`Failed to enable plugin ${id}:`, error);
      return {
        success: false,
        error: {
          message: error instanceof Error ? error.message : `Failed to enable plugin ${id}`,
          code: 'PLUGIN_ERROR'
        }
      };
    }
  }

  /**
   * Disable a plugin
   */
  static async disablePlugin(id: string): Promise<ApiResponse<void>> {
    try {
      await invoke('disable_plugin', { id });
      return { success: true, data: undefined };
    } catch (error) {
      console.error(`Failed to disable plugin ${id}:`, error);
      return {
        success: false,
        error: {
          message: error instanceof Error ? error.message : `Failed to disable plugin ${id}`,
          code: 'PLUGIN_ERROR'
        }
      };
    }
  }

  /**
   * Uninstall a plugin
   */
  static async uninstallPlugin(id: string): Promise<ApiResponse<void>> {
    try {
      await invoke('uninstall_plugin', { id });
      return { success: true, data: undefined };
    } catch (error) {
      console.error(`Failed to uninstall plugin ${id}:`, error);
      return {
        success: false,
        error: {
          message: error instanceof Error ? error.message : `Failed to uninstall plugin ${id}`,
          code: 'PLUGIN_ERROR'
        }
      };
    }
  }

  /**
   * Get plugin manager statistics
   */
  static async getPluginStats(): Promise<ApiResponse<PluginManagerStats>> {
    try {
      const stats: PluginManagerStats = await invoke('get_plugin_stats');
      return { success: true, data: stats };
    } catch (error) {
      console.error('Failed to get plugin stats:', error);
      return {
        success: false,
        error: {
          message: error instanceof Error ? error.message : 'Failed to get plugin stats',
          code: 'PLUGIN_STATS_ERROR'
        }
      };
    }
  }
}

// Utility functions for common operations
export const apiUtils = {
  /**
   * Check if API is ready
   */
  isReady: () => DictionaryAPI['isInitialized'],

  /**
   * Debounce function for search input
   */
  debounce: <T extends (...args: any[]) => any>(
    func: T,
    waitMs: number
  ): ((...args: Parameters<T>) => void) => {
    let timeoutId: NodeJS.Timeout;
    return (...args: Parameters<T>) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => func.apply(null, args), waitMs);
    };
  },

  /**
   * Format search time for display
   */
  formatSearchTime: (timeMs: number): string => {
    if (timeMs < 1) return '< 1ms';
    if (timeMs < 1000) return `${Math.round(timeMs)}ms`;
    return `${(timeMs / 1000).toFixed(2)}s`;
  },

  /**
   * Highlight search terms in text
   */
  highlightText: (text: string, searchTerm: string): string => {
    if (!searchTerm) return text;
    
    const regex = new RegExp(`(${searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    return text.replace(regex, '<mark class="bg-yellow-200 px-1 rounded">$1</mark>');
  },

  /**
   * Clean and normalize search query
   */
  normalizeQuery: (query: string): string => {
    return query.trim().toLowerCase().replace(/\s+/g, ' ');
  },

  /**
   * Check if query is valid for searching
   */
  isValidQuery: (query: string): boolean => {
    const cleaned = query.trim();
    return cleaned.length >= 1 && cleaned.length <= 100;
  }
};

// Error handling utilities
export const errorUtils = {
  /**
   * Get user-friendly error message
   */
  getErrorMessage: (error: any): string => {
    if (typeof error === 'string') return error;
    if (error?.message) return error.message;
    if (error?.error?.message) return error.error.message;
    return 'An unexpected error occurred';
  },

  /**
   * Log error for debugging
   */
  logError: (context: string, error: any): void => {
    console.error(`[${context}]`, error);
    
    // In development, show more details
    if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
      console.trace('Error stack trace:');
    }
  },

  /**
   * Check if error is retryable
   */
  isRetryableError: (error: any): boolean => {
    const retryableCodes = ['NETWORK_ERROR', 'TIMEOUT_ERROR'];
    return retryableCodes.includes(error?.code);
  }
};

// Export everything
export default DictionaryAPI;