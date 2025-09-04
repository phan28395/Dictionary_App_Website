use rusqlite::{Connection, Result};
use serde::{Deserialize, Serialize};
use log::{info, error, debug};
use std::path::PathBuf;
use std::sync::{Arc, Mutex};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DictionaryEntry {
    pub id: i64,
    pub lemma: String,
    pub part_of_speech: Option<String>,
    pub definition: String,
    pub pronunciation: Option<String>,
    pub frequency: Option<f64>,
    pub etymology: Option<String>,
    pub example: Option<String>,
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
        conn.execute("PRAGMA foreign_keys = ON;", [])?;
        
        // Performance optimizations
        conn.execute("PRAGMA journal_mode = WAL;", [])?;
        conn.execute("PRAGMA synchronous = NORMAL;", [])?;
        conn.execute("PRAGMA cache_size = 10000;", [])?;
        conn.execute("PRAGMA temp_store = MEMORY;", [])?;
        
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
            "SELECT id, lemma, part_of_speech, definition, pronunciation, frequency, etymology, example 
             FROM dictionary_entries 
             WHERE lemma = ?1 
             ORDER BY frequency DESC NULLS LAST"
        )?;
        
        let entries: Result<Vec<DictionaryEntry>> = stmt.query_map([term], |row| {
            Ok(DictionaryEntry {
                id: row.get(0)?,
                lemma: row.get(1)?,
                part_of_speech: row.get(2)?,
                definition: row.get(3)?,
                pronunciation: row.get(4)?,
                frequency: row.get(5)?,
                etymology: row.get(6)?,
                example: row.get(7)?,
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
             ORDER BY frequency DESC NULLS LAST 
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