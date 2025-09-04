use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::path::{Path, PathBuf};
use log::{info, warn};

// Plugin manifest structure
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PluginManifest {
    pub id: String,
    pub name: String,
    pub version: String,
    pub description: Option<String>,
    pub author: Option<String>,
    pub main: String, // Entry point file (e.g., "index.js")
    pub permissions: Vec<String>,
    pub dependencies: HashMap<String, String>,
    pub enabled: bool,
}

// Plugin metadata for runtime
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PluginInfo {
    pub manifest: PluginManifest,
    pub path: PathBuf,
    pub loaded: bool,
    pub error: Option<String>,
}

// Plugin manager state
#[derive(Debug)]
pub struct PluginManager {
    plugins: HashMap<String, PluginInfo>,
    plugins_dir: PathBuf,
}

impl PluginManager {
    pub fn new(plugins_dir: PathBuf) -> Result<Self, String> {
        // Ensure plugins directory exists
        if !plugins_dir.exists() {
            fs::create_dir_all(&plugins_dir)
                .map_err(|e| format!("Failed to create plugins directory: {}", e))?;
            info!("Created plugins directory: {:?}", plugins_dir);
        }

        let mut manager = PluginManager {
            plugins: HashMap::new(),
            plugins_dir,
        };

        // Discover plugins on initialization
        manager.discover_plugins()?;
        
        Ok(manager)
    }

    /// Discover all plugins in the plugins directory
    pub fn discover_plugins(&mut self) -> Result<(), String> {
        info!("Discovering plugins in: {:?}", self.plugins_dir);
        
        let entries = fs::read_dir(&self.plugins_dir)
            .map_err(|e| format!("Failed to read plugins directory: {}", e))?;

        for entry in entries {
            let entry = entry.map_err(|e| format!("Failed to read directory entry: {}", e))?;
            let path = entry.path();

            if path.is_dir() {
                match self.load_plugin_manifest(&path) {
                    Ok(manifest) => {
                        let plugin_info = PluginInfo {
                            manifest: manifest.clone(),
                            path: path.clone(),
                            loaded: false,
                            error: None,
                        };
                        
                        self.plugins.insert(manifest.id.clone(), plugin_info);
                        info!("Discovered plugin: {} v{}", manifest.name, manifest.version);
                    }
                    Err(e) => {
                        warn!("Failed to load plugin from {:?}: {}", path, e);
                    }
                }
            }
        }

        info!("Discovered {} plugins", self.plugins.len());
        Ok(())
    }

    /// Load plugin manifest from directory
    fn load_plugin_manifest(&self, plugin_path: &Path) -> Result<PluginManifest, String> {
        let manifest_path = plugin_path.join("plugin.json");
        
        if !manifest_path.exists() {
            return Err("plugin.json not found".to_string());
        }

        let manifest_content = fs::read_to_string(&manifest_path)
            .map_err(|e| format!("Failed to read plugin.json: {}", e))?;

        let mut manifest: PluginManifest = serde_json::from_str(&manifest_content)
            .map_err(|e| format!("Failed to parse plugin.json: {}", e))?;

        // Validate required fields
        if manifest.id.is_empty() {
            return Err("Plugin ID cannot be empty".to_string());
        }
        
        if manifest.name.is_empty() {
            return Err("Plugin name cannot be empty".to_string());
        }

        if manifest.main.is_empty() {
            return Err("Plugin main file cannot be empty".to_string());
        }

        // Check if main file exists
        let main_file_path = plugin_path.join(&manifest.main);
        if !main_file_path.exists() {
            return Err(format!("Main file '{}' not found", manifest.main));
        }

        // Set default values
        if manifest.version.is_empty() {
            manifest.version = "0.1.0".to_string();
        }
        
        Ok(manifest)
    }

    /// Get all discovered plugins
    pub fn get_plugins(&self) -> Vec<&PluginInfo> {
        self.plugins.values().collect()
    }

    /// Get plugin by ID
    pub fn get_plugin(&self, id: &str) -> Option<&PluginInfo> {
        self.plugins.get(id)
    }

    /// Enable a plugin
    pub fn enable_plugin(&mut self, id: &str) -> Result<(), String> {
        if let Some(plugin) = self.plugins.get_mut(id) {
            plugin.manifest.enabled = true;
            let plugin_clone = plugin.clone();
            self.save_plugin_manifest(&plugin_clone)?;
            info!("Enabled plugin: {}", id);
            Ok(())
        } else {
            Err(format!("Plugin not found: {}", id))
        }
    }

    /// Disable a plugin
    pub fn disable_plugin(&mut self, id: &str) -> Result<(), String> {
        if let Some(plugin) = self.plugins.get_mut(id) {
            plugin.manifest.enabled = false;
            plugin.loaded = false;
            let plugin_clone = plugin.clone();
            self.save_plugin_manifest(&plugin_clone)?;
            info!("Disabled plugin: {}", id);
            Ok(())
        } else {
            Err(format!("Plugin not found: {}", id))
        }
    }

    /// Save plugin manifest to disk
    fn save_plugin_manifest(&self, plugin: &PluginInfo) -> Result<(), String> {
        let manifest_path = plugin.path.join("plugin.json");
        let manifest_json = serde_json::to_string_pretty(&plugin.manifest)
            .map_err(|e| format!("Failed to serialize manifest: {}", e))?;
        
        fs::write(&manifest_path, manifest_json)
            .map_err(|e| format!("Failed to write manifest: {}", e))?;
        
        Ok(())
    }

    /// Install a plugin from a directory
    pub fn install_plugin(&mut self, source_path: &Path) -> Result<String, String> {
        // Load manifest from source
        let manifest = self.load_plugin_manifest(source_path)?;
        
        // Check if plugin already exists
        if self.plugins.contains_key(&manifest.id) {
            return Err(format!("Plugin '{}' already installed", manifest.id));
        }

        // Copy plugin to plugins directory
        let target_path = self.plugins_dir.join(&manifest.id);
        self.copy_dir_all(source_path, &target_path)
            .map_err(|e| format!("Failed to copy plugin: {}", e))?;

        // Add to plugins registry
        let plugin_info = PluginInfo {
            manifest: manifest.clone(),
            path: target_path,
            loaded: false,
            error: None,
        };
        
        self.plugins.insert(manifest.id.clone(), plugin_info);
        info!("Installed plugin: {} v{}", manifest.name, manifest.version);
        
        Ok(manifest.id)
    }

    /// Uninstall a plugin
    pub fn uninstall_plugin(&mut self, id: &str) -> Result<(), String> {
        if let Some(plugin) = self.plugins.remove(id) {
            fs::remove_dir_all(&plugin.path)
                .map_err(|e| format!("Failed to remove plugin directory: {}", e))?;
            info!("Uninstalled plugin: {}", id);
            Ok(())
        } else {
            Err(format!("Plugin not found: {}", id))
        }
    }

    /// Recursively copy directory
    fn copy_dir_all(&self, src: &Path, dst: &Path) -> std::io::Result<()> {
        fs::create_dir_all(dst)?;
        
        for entry in fs::read_dir(src)? {
            let entry = entry?;
            let src_path = entry.path();
            let dst_path = dst.join(entry.file_name());
            
            if src_path.is_dir() {
                self.copy_dir_all(&src_path, &dst_path)?;
            } else {
                fs::copy(&src_path, &dst_path)?;
            }
        }
        Ok(())
    }

    /// Get plugin statistics
    pub fn get_stats(&self) -> PluginManagerStats {
        let total = self.plugins.len();
        let enabled = self.plugins.values().filter(|p| p.manifest.enabled).count();
        let loaded = self.plugins.values().filter(|p| p.loaded).count();
        let errors = self.plugins.values().filter(|p| p.error.is_some()).count();

        PluginManagerStats {
            total,
            enabled,
            loaded,
            errors,
        }
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct PluginManagerStats {
    pub total: usize,
    pub enabled: usize,
    pub loaded: usize,
    pub errors: usize,
}