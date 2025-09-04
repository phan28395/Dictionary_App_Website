// Search History Plugin Implementation
class HistoryPlugin {
  constructor() {
    this.id = 'history';
    this.name = 'Search History Plugin';
    this.version = '1.0.0';
    this.history = [];
    this.maxHistorySize = 100;
    this.api = null;
  }

  async onLoad() {
    console.log('History plugin loaded');
    this.api = window.__DICTIONARY_PLUGIN_API__;
    
    if (this.api) {
      // Load existing history from storage
      try {
        const savedHistory = await this.api.storage.get('searchHistory');
        this.history = savedHistory || [];
        console.log(`Loaded ${this.history.length} history entries`);
      } catch (error) {
        console.error('Failed to load history:', error);
      }

      // Listen for search events
      this.api.on('search', (event) => {
        this.handleSearchEvent(event);
      });
    }
  }

  async onUnload() {
    console.log('History plugin unloaded');
    if (this.api) {
      this.api.off('search', this.handleSearchEvent);
    }
  }

  getManifest() {
    return {
      id: this.id,
      name: this.name,
      version: this.version,
      description: "Track and manage search history",
      author: "Dictionary App Team",
      main: "index.js",
      permissions: ["storage"],
      dependencies: {},
      enabled: true
    };
  }

  async addToHistory(searchTerm, resultCount = 0) {
    const entry = {
      term: searchTerm,
      timestamp: new Date().toISOString(),
      resultCount: resultCount,
      id: Date.now().toString()
    };

    // Remove existing entry for the same term
    this.history = this.history.filter(h => h.term.toLowerCase() !== searchTerm.toLowerCase());
    
    // Add to beginning
    this.history.unshift(entry);
    
    // Limit size
    if (this.history.length > this.maxHistorySize) {
      this.history = this.history.slice(0, this.maxHistorySize);
    }

    await this.saveHistory();
  }

  getHistory(limit = 10) {
    return this.history.slice(0, limit);
  }

  getRecentSearches(limit = 5) {
    return this.history
      .filter(entry => entry.resultCount > 0)
      .slice(0, limit)
      .map(entry => entry.term);
  }

  async removeFromHistory(term) {
    const initialLength = this.history.length;
    this.history = this.history.filter(h => h.term.toLowerCase() !== term.toLowerCase());
    
    if (this.history.length < initialLength) {
      await this.saveHistory();
      return true;
    }
    
    return false;
  }

  async clearHistory() {
    this.history = [];
    await this.saveHistory();
    
    if (this.api) {
      this.api.ui.showNotification('Search history cleared', 'info');
    }
  }

  getSearchFrequency(term) {
    return this.history.filter(h => h.term.toLowerCase() === term.toLowerCase()).length;
  }

  getMostSearchedTerms(limit = 10) {
    const termFrequency = {};
    
    this.history.forEach(entry => {
      const term = entry.term.toLowerCase();
      termFrequency[term] = (termFrequency[term] || 0) + 1;
    });

    return Object.entries(termFrequency)
      .sort((a, b) => b[1] - a[1])
      .slice(0, limit)
      .map(([term, count]) => ({ term, count }));
  }

  async saveHistory() {
    if (this.api) {
      try {
        await this.api.storage.set('searchHistory', this.history);
      } catch (error) {
        console.error('Failed to save history:', error);
      }
    }
  }

  handleSearchEvent(event) {
    if (event.data && event.data.term) {
      const resultCount = event.data.resultCount || 0;
      this.addToHistory(event.data.term, resultCount);
      console.log(`Added "${event.data.term}" to search history`);
    }
  }

  // Export functions for external use
  exportFunctions() {
    return {
      getHistory: this.getHistory.bind(this),
      getRecentSearches: this.getRecentSearches.bind(this),
      removeFromHistory: this.removeFromHistory.bind(this),
      clearHistory: this.clearHistory.bind(this),
      getSearchFrequency: this.getSearchFrequency.bind(this),
      getMostSearchedTerms: this.getMostSearchedTerms.bind(this)
    };
  }
}

// Create plugin instance and register it
const historyPlugin = new HistoryPlugin();

// Register with plugin system
if (window.__DICTIONARY_PLUGINS__) {
  window.__DICTIONARY_PLUGINS__.register(historyPlugin);
} else {
  window.__DICTIONARY_PLUGINS__ = { plugins: [] };
  window.__DICTIONARY_PLUGINS__.register = function(plugin) {
    this.plugins.push(plugin);
  };
  window.__DICTIONARY_PLUGINS__.register(historyPlugin);
}

// Export for direct access
window.HistoryPlugin = historyPlugin;