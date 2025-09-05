use crate::database::{Database, DictionaryEntry};
use serde::{Deserialize, Serialize};
use log::{info, debug, error, warn};
use std::collections::HashMap;
use std::path::PathBuf;
use std::fs;
use std::sync::{Arc, Mutex};
use std::time::Instant;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SearchResult {
    pub entries: Vec<DictionaryEntry>,
    pub search_time_ms: u64,
    pub total_results: usize,
    pub query_used: String,
    pub found_inflections: bool,
}

pub struct SearchEngine {
    database: Database,
    inflection_map: Arc<Mutex<HashMap<String, Vec<(String, String)>>>>, // inflected -> [(lemma, tag), ...]
    stats: Arc<Mutex<SearchStats>>,
}

#[derive(Debug, Default)]
struct SearchStats {
    total_searches: u64,
    cache_hits: u64,
    inflection_lookups: u64,
    direct_lookups: u64,
}

impl SearchEngine {
    pub fn new(db_path: PathBuf, inflection_tsv_path: PathBuf) -> Result<Self, Box<dyn std::error::Error>> {
        info!("Initializing search engine...");
        let start_time = Instant::now();
        
        // Initialize database
        let database = Database::new(db_path)?;
        info!("Database initialized");
        
        // Load inflection mappings
        let inflection_map = Self::load_inflection_map(&inflection_tsv_path)?;
        info!("Inflection map loaded with {} entries", inflection_map.len());
        
        let initialization_time = start_time.elapsed();
        info!("Search engine initialized in {}ms", initialization_time.as_millis());
        
        Ok(SearchEngine {
            database,
            inflection_map: Arc::new(Mutex::new(inflection_map)),
            stats: Arc::new(Mutex::new(SearchStats::default())),
        })
    }
    
    fn load_inflection_map(tsv_path: &PathBuf) -> Result<HashMap<String, Vec<(String, String)>>, Box<dyn std::error::Error>> {
        debug!("Loading inflection map from: {:?}", tsv_path);
        let content = fs::read_to_string(tsv_path)?;
        let mut inflection_map = HashMap::new();
        
        for (line_num, line) in content.lines().enumerate() {
            if line.trim().is_empty() || line.starts_with('#') {
                continue;
            }
            
            let parts: Vec<&str> = line.split('\t').collect();
            if parts.len() >= 3 {
                let inflected = parts[0].to_lowercase();
                let lemma = parts[1].to_lowercase();
                let tag = parts[2].to_string();
                
                inflection_map
                    .entry(inflected)
                    .or_insert_with(Vec::new)
                    .push((lemma, tag));
            } else {
                warn!("Skipping malformed line {} in inflection file: {}", line_num + 1, line);
            }
        }
        
        Ok(inflection_map)
    }
    
    pub fn search(&self, term: &str) -> Result<SearchResult, Box<dyn std::error::Error>> {
        let search_start = Instant::now();
        let normalized_term = term.trim().to_lowercase();
        
        debug!("Starting search for term: '{}'", normalized_term);
        
        let mut stats = self.stats.lock().unwrap();
        stats.total_searches += 1;
        drop(stats);
        
        // Try inflection lookup first
        let (search_lemmas, found_inflections) = self.get_search_lemmas(&normalized_term);
        
        // Search for all possible lemmas
        let mut all_entries = Vec::new();
        let mut searched_terms = Vec::new();
        
        for lemma in search_lemmas {
            match self.database.search_by_lemma(&lemma) {
                Ok(mut entries) => {
                    if !entries.is_empty() {
                        searched_terms.push(lemma.clone());
                        all_entries.append(&mut entries);
                    }
                }
                Err(e) => {
                    error!("Database search error for '{}': {}", lemma, e);
                }
            }
        }
        
        // If no inflections found, try direct search
        if all_entries.is_empty() && !found_inflections {
            debug!("No inflections found, trying direct search for '{}'", normalized_term);
            match self.database.search_by_lemma(&normalized_term) {
                Ok(mut entries) => {
                    if !entries.is_empty() {
                        searched_terms.push(normalized_term.clone());
                        all_entries.append(&mut entries);
                    }
                }
                Err(e) => {
                    error!("Direct database search error for '{}': {}", normalized_term, e);
                }
            }
            
            let mut stats = self.stats.lock().unwrap();
            stats.direct_lookups += 1;
        }
        
        // Remove duplicates by ID (no frequency sorting since we don't have frequency column)
        all_entries.sort_by(|a, b| a.id.cmp(&b.id));
        
        // Remove duplicates by ID
        all_entries.dedup_by(|a, b| a.id == b.id);
        
        let search_time = search_start.elapsed();
        let query_used = if searched_terms.is_empty() {
            normalized_term.clone()
        } else {
            searched_terms.join(", ")
        };
        
        debug!(
            "Search completed for '{}' -> '{}': {} results in {}ms", 
            normalized_term, 
            query_used,
            all_entries.len(), 
            search_time.as_millis()
        );
        
        Ok(SearchResult {
            total_results: all_entries.len(),
            entries: all_entries,
            search_time_ms: search_time.as_millis() as u64,
            query_used,
            found_inflections,
        })
    }
    
    fn get_search_lemmas(&self, term: &str) -> (Vec<String>, bool) {
        let inflections = self.inflection_map.lock().unwrap();
        
        if let Some(lemma_tags) = inflections.get(term) {
            debug!("Found {} inflections for '{}'", lemma_tags.len(), term);
            
            let mut stats = self.stats.lock().unwrap();
            stats.inflection_lookups += 1;
            drop(stats);
            
            let lemmas: Vec<String> = lemma_tags
                .iter()
                .map(|(lemma, _tag)| lemma.clone())
                .collect();
            
            (lemmas, true)
        } else {
            debug!("No inflections found for '{}'", term);
            (vec![term.to_string()], false)
        }
    }
    
    pub fn get_suggestions(&self, prefix: &str, limit: usize) -> Result<Vec<String>, Box<dyn std::error::Error>> {
        let normalized_prefix = prefix.trim().to_lowercase();
        debug!("Getting suggestions for prefix: '{}' (limit: {})", normalized_prefix, limit);
        
        let suggestions = self.database.search_by_prefix(&normalized_prefix, limit)?;
        
        debug!("Found {} suggestions for prefix '{}'", suggestions.len(), normalized_prefix);
        Ok(suggestions)
    }
    
    pub fn get_inflections(&self, word: &str) -> Vec<(String, String)> {
        let normalized_word = word.trim().to_lowercase();
        let inflections = self.inflection_map.lock().unwrap();
        
        inflections
            .get(&normalized_word)
            .cloned()
            .unwrap_or_else(Vec::new)
    }
    
    pub fn get_stats(&self) -> SearchEngineStats {
        let stats = self.stats.lock().unwrap();
        let db_stats = self.database.get_stats().unwrap_or_default();
        
        SearchEngineStats {
            total_searches: stats.total_searches,
            cache_hits: stats.cache_hits,
            inflection_lookups: stats.inflection_lookups,
            direct_lookups: stats.direct_lookups,
            total_dictionary_entries: db_stats.total_entries,
            unique_lemmas: db_stats.unique_lemmas,
        }
    }
    
    pub fn cleanup_and_shutdown(&self) -> Result<(), Box<dyn std::error::Error>> {
        info!("Shutting down search engine...");
        
        // Clean up database connections
        self.database.cleanup_and_close()?;
        
        // Clear in-memory data structures
        {
            let mut inflections = self.inflection_map.lock().unwrap();
            inflections.clear();
            info!("Inflection map cleared");
        }
        
        {
            let stats = self.stats.lock().unwrap();
            info!("Final search stats - Total searches: {}, Cache hits: {}, Inflection lookups: {}, Direct lookups: {}", 
                  stats.total_searches, stats.cache_hits, stats.inflection_lookups, stats.direct_lookups);
        }
        
        info!("Search engine shutdown completed");
        Ok(())
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SearchEngineStats {
    pub total_searches: u64,
    pub cache_hits: u64,
    pub inflection_lookups: u64,
    pub direct_lookups: u64,
    pub total_dictionary_entries: i64,
    pub unique_lemmas: i64,
}

impl Clone for SearchEngine {
    fn clone(&self) -> Self {
        SearchEngine {
            database: self.database.clone(),
            inflection_map: Arc::clone(&self.inflection_map),
            stats: Arc::clone(&self.stats),
        }
    }
}

// Add a Default implementation for DatabaseStats to fix the unwrap_or_default() call
impl Default for crate::database::DatabaseStats {
    fn default() -> Self {
        Self {
            total_entries: 0,
            unique_lemmas: 0,
        }
    }
}