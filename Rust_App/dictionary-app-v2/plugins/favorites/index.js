// Favorites Plugin Implementation
class FavoritesPlugin {
  constructor() {
    this.id = 'favorites';
    this.name = 'Favorites Plugin';
    this.version = '1.0.0';
    this.favorites = [];
    this.api = null;
  }

  async onLoad() {
    console.log('Favorites plugin loaded');
    this.api = window.__DICTIONARY_PLUGIN_API__;
    
    if (this.api) {
      // Load existing favorites from storage
      try {
        const savedFavorites = await this.api.storage.get('favorites');
        this.favorites = savedFavorites || [];
        console.log(`Loaded ${this.favorites.length} favorites`);
      } catch (error) {
        console.error('Failed to load favorites:', error);
      }

      // Listen for search events to add favorite buttons
      this.api.on('search', (event) => {
        this.handleSearchEvent(event);
      });
    }
  }

  async onUnload() {
    console.log('Favorites plugin unloaded');
    if (this.api) {
      this.api.off('search', this.handleSearchEvent);
    }
  }

  getManifest() {
    return {
      id: this.id,
      name: this.name,
      version: this.version,
      description: "Bookmark and manage favorite dictionary words",
      author: "Dictionary App Team",
      main: "index.js",
      permissions: ["storage"],
      dependencies: {},
      enabled: true
    };
  }

  async addFavorite(word, definition = '') {
    const favorite = {
      word: word.toLowerCase(),
      definition: definition,
      dateAdded: new Date().toISOString(),
      id: Date.now().toString()
    };

    // Check if already exists
    if (this.favorites.some(f => f.word === favorite.word)) {
      console.log(`"${word}" is already in favorites`);
      return false;
    }

    this.favorites.unshift(favorite);
    await this.saveFavorites();
    
    if (this.api) {
      this.api.ui.showNotification(`Added "${word}" to favorites`, 'success');
    }
    
    return true;
  }

  async removeFavorite(word) {
    const initialLength = this.favorites.length;
    this.favorites = this.favorites.filter(f => f.word !== word.toLowerCase());
    
    if (this.favorites.length < initialLength) {
      await this.saveFavorites();
      
      if (this.api) {
        this.api.ui.showNotification(`Removed "${word}" from favorites`, 'info');
      }
      
      return true;
    }
    
    return false;
  }

  isFavorite(word) {
    return this.favorites.some(f => f.word === word.toLowerCase());
  }

  getFavorites() {
    return [...this.favorites];
  }

  async clearFavorites() {
    this.favorites = [];
    await this.saveFavorites();
    
    if (this.api) {
      this.api.ui.showNotification('Cleared all favorites', 'info');
    }
  }

  async saveFavorites() {
    if (this.api) {
      try {
        await this.api.storage.set('favorites', this.favorites);
      } catch (error) {
        console.error('Failed to save favorites:', error);
      }
    }
  }

  handleSearchEvent(event) {
    console.log('Search event received:', event.data);
    // This would integrate with the UI to add favorite buttons to search results
  }

  // Export functions for external use
  exportFunctions() {
    return {
      addFavorite: this.addFavorite.bind(this),
      removeFavorite: this.removeFavorite.bind(this),
      isFavorite: this.isFavorite.bind(this),
      getFavorites: this.getFavorites.bind(this),
      clearFavorites: this.clearFavorites.bind(this)
    };
  }
}

// Create plugin instance and register it
const favoritesPlugin = new FavoritesPlugin();

// Register with plugin system
if (window.__DICTIONARY_PLUGINS__) {
  window.__DICTIONARY_PLUGINS__.register(favoritesPlugin);
} else {
  window.__DICTIONARY_PLUGINS__ = { plugins: [] };
  window.__DICTIONARY_PLUGINS__.register = function(plugin) {
    this.plugins.push(plugin);
  };
  window.__DICTIONARY_PLUGINS__.register(favoritesPlugin);
}

// Export for direct access
window.FavoritesPlugin = favoritesPlugin;