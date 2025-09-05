use log::{info, warn};
use std::fs;
use std::path::{Path, PathBuf};
use std::sync::{Once, OnceLock};
use chrono::Local;
use tauri::Manager;

static INIT: Once = Once::new();
static LOGS_DIR: OnceLock<PathBuf> = OnceLock::new();

/// Initialize the centralized logging system
pub fn init_logger(app_handle: &tauri::App) -> Result<(), Box<dyn std::error::Error>> {
    INIT.call_once(|| {
        // Get app data directory
        let logs_dir = match get_logs_directory(app_handle) {
            Ok(dir) => dir,
            Err(e) => {
                eprintln!("Failed to create logs directory: {}", e);
                return;
            }
        };

        // Set the logs directory using OnceLock
        let _ = LOGS_DIR.set(logs_dir.clone());

        // Clean up any existing logs from previous sessions
        if let Err(e) = cleanup_old_logs(&logs_dir) {
            eprintln!("Failed to cleanup previous session logs: {}", e);
        }

        // Create logs directory
        if let Err(e) = fs::create_dir_all(&logs_dir) {
            eprintln!("Failed to create logs directory: {}", e);
            return;
        }

        // Store logs_dir for the closure
        let logs_dir_clone = logs_dir.clone();
        
        // Initialize env_logger with custom format
        let env = env_logger::Env::default()
            .filter_or("RUST_LOG", "info")
            .write_style_or("RUST_LOG_STYLE", "always");

        let mut builder = env_logger::Builder::from_env(env);
        
        builder.format(move |buf, record| {
            use std::io::Write;
            let timestamp = Local::now().format("%Y-%m-%d %H:%M:%S%.3f");
            let level = record.level();
            let target = record.target();
            let component = extract_component_name(target);
            
            // Write to component-specific log file
            if let Err(e) = write_to_component_log(&logs_dir_clone, &component, &format!(
                "[{}] [{}] [{}] {}\n",
                timestamp, level, target, record.args()
            )) {
                eprintln!("Failed to write to component log: {}", e);
            }

            // Also write to console/main log
            writeln!(
                buf,
                "[{}] [{}] [{}] {}",
                timestamp, level, component, record.args()
            )
        });

        builder.init();

        info!("Centralized logging system initialized");
        info!("Logs directory: {:?}", logs_dir);
    });

    Ok(())
}

fn get_logs_directory(app_handle: &tauri::App) -> Result<PathBuf, Box<dyn std::error::Error>> {
    // Try to get app data directory, fallback to current directory
    let base_dir = match app_handle.path().app_data_dir() {
        Ok(dir) => dir,
        Err(_) => {
            // Fallback for development
            let current_dir = std::env::current_dir()?;
            if current_dir.ends_with("target/debug") {
                current_dir.parent().unwrap().parent().unwrap().to_path_buf()
            } else {
                current_dir
            }
        }
    };
    
    Ok(base_dir.join("logs"))
}

fn extract_component_name(target: &str) -> String {
    // Extract component name from target like "dictionary_app::database" -> "database"
    if let Some(pos) = target.rfind("::") {
        target[pos + 2..].to_string()
    } else if target.starts_with("dictionary_app") {
        "main".to_string()
    } else {
        target.to_string()
    }
}

fn write_to_component_log(logs_dir: &Path, component: &str, message: &str) -> Result<(), Box<dyn std::error::Error>> {
    use std::io::Write;
    
    let log_file = logs_dir.join(format!("{}.log", component));
    let mut file = std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(log_file)?;
    
    file.write_all(message.as_bytes())?;
    file.flush()?;
    
    Ok(())
}

fn cleanup_old_logs(logs_dir: &Path) -> Result<(), Box<dyn std::error::Error>> {
    if !logs_dir.exists() {
        info!("No previous logs found - starting fresh");
        return Ok(());
    }

    println!("Cleaning up previous session logs...");
    let mut cleaned_count = 0;
    let mut file_names = Vec::new();
    
    for entry in fs::read_dir(logs_dir)? {
        let entry = entry?;
        let path = entry.path();
        
        if path.is_file() && path.extension().map_or(false, |ext| ext == "log") {
            let file_name = path.file_name().unwrap().to_string_lossy().to_string();
            
            if let Err(e) = fs::remove_file(&path) {
                warn!("Failed to remove old log file {:?}: {}", path, e);
            } else {
                file_names.push(file_name);
                cleaned_count += 1;
            }
        }
    }
    
    if cleaned_count > 0 {
        println!("Cleaned up {} previous log files: {}", cleaned_count, file_names.join(", "));
    } else {
        println!("No previous log files to clean up");
    }
    
    Ok(())
}

/// Get information about current session logs (preserved until next startup)
pub fn preserve_session_logs_info() -> Result<String, Box<dyn std::error::Error>> {
    if let Some(logs_dir) = LOGS_DIR.get() {
        let log_count = fs::read_dir(logs_dir)?
            .filter_map(|entry| entry.ok())
            .filter(|entry| {
                entry.path().is_file() && 
                entry.path().extension().map_or(false, |ext| ext == "log")
            })
            .count();
        
        Ok(format!("Session logs preserved at: {:?} ({} files) - will be cleaned on next startup", logs_dir, log_count))
    } else {
        Ok("No logs directory initialized".to_string())
    }
}

/// Get the current logs directory path
pub fn get_logs_dir() -> Option<PathBuf> {
    LOGS_DIR.get().cloned()
}

/// Log a message to a specific component
#[allow(dead_code)]
pub fn log_to_component(component: &str, level: log::Level, message: &str) {
    if let Some(logs_dir) = LOGS_DIR.get() {
        let timestamp = Local::now().format("%Y-%m-%d %H:%M:%S%.3f");
        let log_message = format!("[{}] [{}] [{}] {}\n", timestamp, level, component, message);
        
        if let Err(e) = write_to_component_log(logs_dir, component, &log_message) {
            eprintln!("Failed to write to component log {}: {}", component, e);
        }
    }
}

/// Create a logs viewer command (for development/debugging)
pub fn list_current_logs() -> Result<Vec<String>, Box<dyn std::error::Error>> {
    let mut logs_info = Vec::new();
    
    if let Some(logs_dir) = LOGS_DIR.get() {
        if !logs_dir.exists() {
            return Ok(vec!["No logs directory found".to_string()]);
        }
        
        logs_info.push(format!("Logs directory: {:?}", logs_dir));
        logs_info.push("Current log files:".to_string());
        
        for entry in fs::read_dir(logs_dir)? {
            let entry = entry?;
            let path = entry.path();
            
            if path.is_file() && path.extension().map_or(false, |ext| ext == "log") {
                let metadata = entry.metadata()?;
                let size = metadata.len();
                let name = path.file_name().unwrap().to_string_lossy();
                
                logs_info.push(format!("  {} ({} bytes)", name, size));
            }
        }
    } else {
        logs_info.push("Logging system not initialized".to_string());
    }
    
    Ok(logs_info)
}