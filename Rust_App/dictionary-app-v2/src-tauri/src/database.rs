use rusqlite::{Connection, Result};
use serde::{Deserialize, Serialize};
use log::{info, error, debug};
use std::path::PathBuf;
use std::sync::{Arc, Mutex};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DictionaryEntry {
    pub id: i64,
    pub lemma: String,
    pub pos: String,
    pub meanings: String,
    pub definitions: String,
    pub examples: String,
    pub frequency_meaning: String,
}

pub struct Database {
    connection: Arc<Mutex<Connection>>,
    db_path: PathBuf,
}

impl Database {
    pub fn new(db_path: PathBuf) -> Result<Self> {
        info!("Opening database at: {:?}", db_path);
        
        let conn = Connection::open(&db_path)?;
        
        // Enable foreign key support
        conn.execute("PRAGMA foreign_keys = ON", [])?;
        
        // Performance optimizations  
        // Use prepare/query for PRAGMA statements that return results
        let _ = conn.prepare("PRAGMA journal_mode = WAL")?.query([])?;
        conn.execute("PRAGMA synchronous = NORMAL", [])?;
        conn.execute("PRAGMA cache_size = 10000", [])?;
        conn.execute("PRAGMA temp_store = MEMORY", [])?;
        
        info!("Database connection established successfully");
        
        Ok(Database {
            connection: Arc::new(Mutex::new(conn)),
            db_path,
        })
    }
    
    pub fn search_by_lemma(&self, term: &str) -> Result<Vec<DictionaryEntry>> {
        debug!("Searching for lemma: {}", term);
        
        let conn = self.connection.lock().unwrap();
        let mut stmt = conn.prepare_cached(
            "SELECT id, lemma, pos, meanings, definitions, examples, frequency_meaning 
             FROM dictionary_entries 
             WHERE lemma = ?1"
        )?;
        
        let entries: Result<Vec<DictionaryEntry>> = stmt.query_map([term], |row| {
            Ok(DictionaryEntry {
                id: row.get(0)?,
                lemma: row.get(1)?,
                pos: row.get(2)?,
                meanings: row.get(3)?,
                definitions: row.get(4)?,
                examples: row.get(5)?,
                frequency_meaning: row.get(6)?,
            })
        })?.collect();
        
        match entries {
            Ok(ref results) => debug!("Found {} entries for lemma '{}'", results.len(), term),
            Err(ref e) => error!("Error searching lemma '{}': {}", term, e),
        }
        
        entries
    }
    
    pub fn search_by_prefix(&self, prefix: &str, limit: usize) -> Result<Vec<String>> {
        debug!("Searching for prefix: {} (limit: {})", prefix, limit);
        
        let conn = self.connection.lock().unwrap();
        let mut stmt = conn.prepare_cached(
            "SELECT DISTINCT lemma 
             FROM dictionary_entries 
             WHERE lemma LIKE ?1 || '%' 
             LIMIT ?2"
        )?;
        
        let suggestions: Result<Vec<String>> = stmt.query_map([prefix, &limit.to_string()], |row| {
            Ok(row.get(0)?)
        })?.collect();
        
        match suggestions {
            Ok(ref results) => debug!("Found {} suggestions for prefix '{}'", results.len(), prefix),
            Err(ref e) => error!("Error searching prefix '{}': {}", prefix, e),
        }
        
        suggestions
    }
    
    pub fn get_stats(&self) -> Result<DatabaseStats> {
        debug!("Getting database statistics");
        
        let conn = self.connection.lock().unwrap();
        
        let total_entries: i64 = conn.query_row(
            "SELECT COUNT(*) FROM dictionary_entries",
            [],
            |row| row.get(0)
        )?;
        
        let unique_lemmas: i64 = conn.query_row(
            "SELECT COUNT(DISTINCT lemma) FROM dictionary_entries",
            [],
            |row| row.get(0)
        )?;
        
        Ok(DatabaseStats {
            total_entries,
            unique_lemmas,
        })
    }
    
    pub fn cleanup_and_close(&self) -> Result<()> {
        info!("Cleaning up database before shutdown...");
        
        let conn = self.connection.lock().unwrap();
        
        // Checkpoint WAL file to merge changes back to main database
        match conn.execute("PRAGMA wal_checkpoint(TRUNCATE);", []) {
            Ok(_) => {
                info!("WAL checkpoint completed successfully");
            }
            Err(e) => {
                error!("Failed to checkpoint WAL file: {}", e);
                // Continue with cleanup even if checkpoint fails
            }
        }
        
        // Close prepared statement cache
        match conn.cache_flush() {
            Ok(_) => debug!("Statement cache flushed"),
            Err(e) => error!("Failed to flush statement cache: {}", e),
        }
        
        info!("Database cleanup completed");
        Ok(())
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct DatabaseStats {
    pub total_entries: i64,
    pub unique_lemmas: i64,
}

impl Clone for Database {
    fn clone(&self) -> Self {
        Database {
            connection: Arc::clone(&self.connection),
            db_path: self.db_path.clone(),
        }
    }
}