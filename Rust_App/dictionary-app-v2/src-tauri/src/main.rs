// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use log::{info, error};
use std::path::PathBuf;
use std::sync::Mutex;
use tauri::{State, Manager, WindowEvent, menu::{Menu, MenuItem}, tray::{TrayIconBuilder, MouseButton}};
use tauri_plugin_global_shortcut::GlobalShortcutExt;

mod database;
mod search_engine;
mod plugin_manager;
mod logger;

use search_engine::{SearchEngine, SearchEngineStats};
use plugin_manager::{PluginManager, PluginInfo, PluginManagerStats};

// Application state
struct AppState {
    search_engine: Mutex<Option<SearchEngine>>,
    plugin_manager: Mutex<Option<PluginManager>>,
}

// Tauri commands
#[tauri::command]
async fn initialize_search_engine(app: tauri::AppHandle, state: State<'_, AppState>) -> Result<String, String> {
    info!("Initializing search engine...");
    
    // Try to get resource directory for production builds
    let (db_path, inflection_path) = match app.path().resource_dir() {
        Ok(resource_dir) => {
            let db_path = resource_dir.join("data").join("dictionary.db");
            let inflection_path = resource_dir.join("data").join("inflection_lookup.tsv");
            (db_path, inflection_path)
        }
        Err(_) => {
            // Fallback for development - use working directory as project root
            let current_dir = std::env::current_dir().unwrap_or_else(|_| PathBuf::from("."));
            // For development builds, data should be in project root/data
            let project_root = if current_dir.to_string_lossy().contains("target") {
                // If we're in a target directory, navigate to project root
                current_dir.ancestors()
                    .find(|p| p.join("src-tauri").exists() && p.join("data").exists())
                    .unwrap_or(&current_dir)
                    .to_path_buf()
            } else {
                current_dir
            };
            let app_data_dir = project_root.join("data");
            let db_path = app_data_dir.join("dictionary.db");
            let inflection_path = app_data_dir.join("inflection_lookup.tsv");
            (db_path, inflection_path)
        }
    };
    
    info!("Looking for database at: {:?}", db_path);
    info!("Looking for inflections at: {:?}", inflection_path);
    
    if !db_path.exists() {
        let error_msg = format!("Database file not found at: {:?}", db_path);
        error!("{}", error_msg);
        return Err(error_msg);
    }
    
    if !inflection_path.exists() {
        let error_msg = format!("Inflection file not found at: {:?}", inflection_path);
        error!("{}", error_msg);
        return Err(error_msg);
    }
    
    match SearchEngine::new(db_path, inflection_path) {
        Ok(engine) => {
            let mut search_engine = state.search_engine.lock().unwrap();
            *search_engine = Some(engine);
            info!("Search engine initialized successfully");
            Ok("Search engine initialized successfully".to_string())
        }
        Err(e) => {
            let error_msg = format!("Failed to initialize search engine: {}", e);
            error!("{}", error_msg);
            Err(error_msg)
        }
    }
}

#[tauri::command]
async fn search_dictionary(term: String, state: State<'_, AppState>) -> Result<Vec<database::DictionaryEntry>, String> {
    let search_engine_guard = state.search_engine.lock().unwrap();
    
    match search_engine_guard.as_ref() {
        Some(engine) => {
            match engine.search(&term) {
                Ok(results) => Ok(results.entries),
                Err(e) => {
                    let error_msg = format!("Search failed for '{}': {}", term, e);
                    error!("{}", error_msg);
                    Err(error_msg)
                }
            }
        }
        None => Err("Search engine not initialized".to_string()),
    }
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
struct Suggestion {
    word: String,
}

#[tauri::command]
async fn get_suggestions(prefix: String, limit: Option<usize>, state: State<'_, AppState>) -> Result<Vec<Suggestion>, String> {
    let search_engine_guard = state.search_engine.lock().unwrap();
    let limit = limit.unwrap_or(10);
    
    match search_engine_guard.as_ref() {
        Some(engine) => {
            match engine.get_suggestions(&prefix, limit) {
                Ok(suggestions) => {
                    let formatted_suggestions: Vec<Suggestion> = suggestions
                        .into_iter()
                        .map(|word| Suggestion { word })
                        .collect();
                    Ok(formatted_suggestions)
                },
                Err(e) => {
                    let error_msg = format!("Failed to get suggestions for '{}': {}", prefix, e);
                    error!("{}", error_msg);
                    Err(error_msg)
                }
            }
        }
        None => Err("Search engine not initialized".to_string()),
    }
}

#[tauri::command]
async fn get_inflections(word: String, state: State<'_, AppState>) -> Result<Vec<(String, String)>, String> {
    let search_engine_guard = state.search_engine.lock().unwrap();
    
    match search_engine_guard.as_ref() {
        Some(engine) => Ok(engine.get_inflections(&word)),
        None => Err("Search engine not initialized".to_string()),
    }
}

#[tauri::command]
async fn get_search_stats(state: State<'_, AppState>) -> Result<SearchEngineStats, String> {
    let search_engine_guard = state.search_engine.lock().unwrap();
    
    match search_engine_guard.as_ref() {
        Some(engine) => Ok(engine.get_stats()),
        None => Err("Search engine not initialized".to_string()),
    }
}

// Plugin Management Commands
#[tauri::command]
async fn initialize_plugin_manager(app: tauri::AppHandle, state: State<'_, AppState>) -> Result<String, String> {
    info!("Initializing plugin manager...");
    
    // Try to get resource directory for production builds
    let plugins_dir = match app.path().resource_dir() {
        Ok(resource_dir) => resource_dir.join("plugins"),
        Err(_) => {
            // Fallback for development - go up from target/debug to project root
            let current_dir = std::env::current_dir().unwrap_or_else(|_| PathBuf::from("."));
            let project_root = if current_dir.ends_with("target/debug") {
                current_dir.parent().unwrap().parent().unwrap().to_path_buf()
            } else {
                current_dir
            };
            project_root.join("plugins")
        }
    };
    
    info!("Looking for plugins at: {:?}", plugins_dir);
    
    match PluginManager::new(plugins_dir) {
        Ok(manager) => {
            let stats = manager.get_stats();
            let mut plugin_manager = state.plugin_manager.lock().unwrap();
            *plugin_manager = Some(manager);
            info!("Plugin manager initialized successfully. Discovered {} plugins", stats.total);
            Ok(format!("Plugin manager initialized. Found {} plugins", stats.total))
        }
        Err(e) => {
            let error_msg = format!("Failed to initialize plugin manager: {}", e);
            error!("{}", error_msg);
            Err(error_msg)
        }
    }
}

#[tauri::command]
async fn get_plugins(state: State<'_, AppState>) -> Result<Vec<PluginInfo>, String> {
    let plugin_manager_guard = state.plugin_manager.lock().unwrap();
    
    match plugin_manager_guard.as_ref() {
        Some(manager) => {
            let plugins = manager.get_plugins().into_iter().cloned().collect();
            Ok(plugins)
        }
        None => Err("Plugin manager not initialized".to_string()),
    }
}

#[tauri::command]
async fn get_plugin(id: String, state: State<'_, AppState>) -> Result<PluginInfo, String> {
    let plugin_manager_guard = state.plugin_manager.lock().unwrap();
    
    match plugin_manager_guard.as_ref() {
        Some(manager) => {
            match manager.get_plugin(&id) {
                Some(plugin) => Ok(plugin.clone()),
                None => Err(format!("Plugin not found: {}", id)),
            }
        }
        None => Err("Plugin manager not initialized".to_string()),
    }
}

#[tauri::command]
async fn enable_plugin(id: String, state: State<'_, AppState>) -> Result<(), String> {
    let mut plugin_manager_guard = state.plugin_manager.lock().unwrap();
    
    match plugin_manager_guard.as_mut() {
        Some(manager) => manager.enable_plugin(&id),
        None => Err("Plugin manager not initialized".to_string()),
    }
}

#[tauri::command]
async fn disable_plugin(id: String, state: State<'_, AppState>) -> Result<(), String> {
    let mut plugin_manager_guard = state.plugin_manager.lock().unwrap();
    
    match plugin_manager_guard.as_mut() {
        Some(manager) => manager.disable_plugin(&id),
        None => Err("Plugin manager not initialized".to_string()),
    }
}

#[tauri::command]
async fn uninstall_plugin(id: String, state: State<'_, AppState>) -> Result<(), String> {
    let mut plugin_manager_guard = state.plugin_manager.lock().unwrap();
    
    match plugin_manager_guard.as_mut() {
        Some(manager) => manager.uninstall_plugin(&id),
        None => Err("Plugin manager not initialized".to_string()),
    }
}

#[tauri::command]
async fn get_plugin_stats(state: State<'_, AppState>) -> Result<PluginManagerStats, String> {
    let plugin_manager_guard = state.plugin_manager.lock().unwrap();
    
    match plugin_manager_guard.as_ref() {
        Some(manager) => Ok(manager.get_stats()),
        None => Err("Plugin manager not initialized".to_string()),
    }
}

#[tauri::command]
async fn toggle_window(app: tauri::AppHandle) -> Result<(), String> {
    match app.get_webview_window("main") {
        Some(window) => {
            match window.is_visible() {
                Ok(true) => {
                    window.hide().map_err(|e| e.to_string())?;
                }
                Ok(false) => {
                    // Position window near cursor before showing
                    position_window_near_cursor_sync(&window)?;
                    window.show().map_err(|e| e.to_string())?;
                    window.set_focus().map_err(|e| e.to_string())?;
                }
                Err(e) => return Err(e.to_string()),
            }
            Ok(())
        }
        None => Err("Main window not found".to_string()),
    }
}

#[tauri::command]
async fn hide_window(app: tauri::AppHandle) -> Result<(), String> {
    match app.get_webview_window("main") {
        Some(window) => {
            window.hide().map_err(|e| e.to_string())?;
            Ok(())
        }
        None => Err("Main window not found".to_string()),
    }
}

#[tauri::command]
async fn quit_app(app: tauri::AppHandle, state: State<'_, AppState>) -> Result<(), String> {
    info!("Quit command received, shutting down gracefully...");
    
    // Clean up search engine
    if let Ok(mut search_engine_guard) = state.search_engine.lock() {
        if let Some(engine) = search_engine_guard.take() {
            match engine.cleanup_and_shutdown() {
                Ok(_) => info!("Search engine cleaned up successfully"),
                Err(e) => error!("Failed to cleanup search engine: {}", e),
            }
        }
    }
    
    // Clean up plugin manager
    if let Ok(mut plugin_manager_guard) = state.plugin_manager.lock() {
        if let Some(_manager) = plugin_manager_guard.take() {
            info!("Plugin manager cleaned up");
        }
    }
    
    info!("Application shutdown complete - session logs preserved for debugging");
    info!("Logs will be cleaned up automatically on next app startup");
    
    // Exit the application (logs will be cleaned up on next startup)
    app.exit(0);
    Ok(())
}

fn position_window_near_cursor_sync(window: &tauri::WebviewWindow) -> Result<(), String> {
    #[cfg(windows)]
    {
        use winapi::um::winuser::{GetCursorPos, GetSystemMetrics, SM_CXSCREEN, SM_CYSCREEN};
        use winapi::shared::windef::POINT;
        
        unsafe {
            let mut cursor_pos = POINT { x: 0, y: 0 };
            if GetCursorPos(&mut cursor_pos) != 0 {
                let screen_width = GetSystemMetrics(SM_CXSCREEN);
                let screen_height = GetSystemMetrics(SM_CYSCREEN);
                
                // Window dimensions (from config)
                let window_width = 800;
                let window_height = 600;
                
                // Calculate position near cursor with offset
                let offset = 50;
                let mut x = cursor_pos.x + offset;
                let mut y = cursor_pos.y + offset;
                
                // Ensure window stays on screen
                if x + window_width > screen_width {
                    x = cursor_pos.x - window_width - offset;
                }
                if y + window_height > screen_height {
                    y = cursor_pos.y - window_height - offset;
                }
                
                // Ensure window doesn't go off screen on the left/top
                if x < 0 { x = 10; }
                if y < 0 { y = 10; }
                
                let position = tauri::PhysicalPosition::new(x, y);
                window.set_position(position).map_err(|e| e.to_string())?;
                return Ok(());
            }
        }
    }
    
    // Fallback to center if cursor positioning fails or not on Windows
    window.center().map_err(|e| e.to_string())?;
    Ok(())
}

#[tauri::command]
fn greet(name: &str) -> String {
    info!("Greeting request for: {}", name);
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[tauri::command]
async fn get_logs_info() -> Result<Vec<String>, String> {
    match logger::list_current_logs() {
        Ok(info) => Ok(info),
        Err(e) => Err(format!("Failed to get logs info: {}", e)),
    }
}

#[tauri::command]
async fn get_logs_directory() -> Result<String, String> {
    match logger::get_logs_dir() {
        Some(dir) => Ok(dir.to_string_lossy().to_string()),
        None => Err("Logs directory not initialized".to_string()),
    }
}

fn main() {
    let app_state = AppState {
        search_engine: Mutex::new(None),
        plugin_manager: Mutex::new(None),
    };

    tauri::Builder::default()
        .plugin(
            tauri_plugin_global_shortcut::Builder::new()
                .with_handler(|_app, shortcut, event| {
                    use tauri_plugin_global_shortcut::ShortcutState;
                    if event.state == ShortcutState::Pressed {
                        // Check which shortcut was pressed
                        let key_code = shortcut.key;
                        let modifiers = shortcut.mods;
                        
                        if format!("{:?}", key_code).contains("KeyQ") && 
                           format!("{:?}", modifiers).contains("CONTROL") && 
                           format!("{:?}", modifiers).contains("SHIFT") {
                            // Ctrl+Shift+Q - quit app
                            info!("Quit hotkey pressed (Ctrl+Shift+Q)");
                            _app.exit(0);
                        } else {
                            // Ctrl+Alt+D - toggle window
                            if let Some(window) = _app.get_webview_window("main") {
                                match window.is_visible() {
                                    Ok(true) => { let _ = window.hide(); }
                                    Ok(false) => { 
                                        let _ = position_window_near_cursor_sync(&window);
                                        let _ = window.show();
                                        let _ = window.set_focus();
                                    }
                                    Err(_) => {}
                                }
                            }
                        }
                    }
                })
                .build()
        )
        .manage(app_state)
        .setup(|app| {
            // Initialize centralized logging system
            if let Err(e) = logger::init_logger(app) {
                eprintln!("Failed to initialize logging system: {}", e);
            }
            
            info!("Dictionary App starting up with centralized logging...");
            
            // Register global shortcut
            use tauri_plugin_global_shortcut::{Code, Modifiers};
            
            // Register global shortcut for show/hide
            app.global_shortcut().register(
                tauri_plugin_global_shortcut::Shortcut::new(Some(Modifiers::CONTROL | Modifiers::ALT), Code::KeyD)
            )?;
            
            // Register global shortcut for quit (Ctrl+Shift+Q)  
            app.global_shortcut().register(
                tauri_plugin_global_shortcut::Shortcut::new(Some(Modifiers::CONTROL | Modifiers::SHIFT), Code::KeyQ)
            )?;

            // Create system tray
            let show_item = MenuItem::with_id(app, "show", "Show Dictionary", true, None::<&str>)?;
            let quit_item = MenuItem::with_id(app, "quit", "Quit", true, None::<&str>)?;
            let menu = Menu::with_items(app, &[&show_item, &quit_item])?;

            let _tray = TrayIconBuilder::with_id("main-tray")
                .icon(app.default_window_icon().unwrap().clone())
                .tooltip("Dictionary App")
                .menu(&menu)
                .on_menu_event(move |app, event| {
                    info!("Tray menu event: {}", event.id.as_ref());
                    match event.id.as_ref() {
                        "show" => {
                            info!("Show Dictionary requested from tray menu");
                            if let Some(window) = app.get_webview_window("main") {
                                let _ = position_window_near_cursor_sync(&window);
                                let _ = window.show();
                                let _ = window.set_focus();
                            }
                        }
                        "quit" => {
                            info!("Quit requested from system tray menu");
                            app.exit(0);
                        }
                        _ => {
                            info!("Unknown tray menu event: {}", event.id.as_ref());
                        }
                    }
                })
                .on_tray_icon_event(|tray, event| {
                    use tauri::tray::TrayIconEvent;
                    match event {
                        TrayIconEvent::Click { button, .. } => {
                            // Only handle left-clicks for toggle, let right-clicks show the menu
                            if button == MouseButton::Left {
                                info!("Tray left-click: toggling window");
                                let app = tray.app_handle();
                                if let Some(window) = app.get_webview_window("main") {
                                    match window.is_visible().unwrap_or(false) {
                                        true => { 
                                            let _ = window.hide(); 
                                        }
                                        false => { 
                                            let _ = position_window_near_cursor_sync(&window);
                                            let _ = window.show();
                                            let _ = window.set_focus();
                                        }
                                    }
                                }
                            }
                            // Right-clicks will automatically show the context menu (no logging needed)
                        }
                        _ => {
                            // Ignore other tray events (mouse movements, etc.) to reduce log noise
                        }
                    }
                })
                .build(app)?;

            // Hide window on startup
            if let Some(window) = app.get_webview_window("main") {
                let _ = window.hide();
            }
            
            info!("Global shortcut registered: Ctrl+Alt+D");
            info!("System tray created");
            info!("App setup complete");
            Ok(())
        })
        .on_window_event(|_window, event| match event {
            WindowEvent::CloseRequested { api, .. } => {
                // Check if user is holding Alt key to force close
                #[cfg(windows)]
                unsafe {
                    use winapi::um::winuser::{GetAsyncKeyState, VK_MENU};
                    let alt_pressed = GetAsyncKeyState(VK_MENU) < 0;
                    
                    if alt_pressed {
                        info!("Alt+Close detected, allowing app to quit");
                        // Don't prevent close, let app quit
                        return;
                    }
                }
                
                // Default behavior: hide instead of closing
                info!("Close button clicked, hiding window (use Alt+F4 or system tray to quit)");
                _window.hide().unwrap();
                api.prevent_close();
            }
            WindowEvent::Focused(false) => {
                // Hide window when it loses focus (click outside to close)
                _window.hide().unwrap();
            }
            _ => {}
        })
        .invoke_handler(tauri::generate_handler![
            greet,
            initialize_search_engine,
            search_dictionary,
            get_suggestions,
            get_inflections,
            get_search_stats,
            initialize_plugin_manager,
            get_plugins,
            get_plugin,
            enable_plugin,
            disable_plugin,
            uninstall_plugin,
            get_plugin_stats,
            toggle_window,
            hide_window,
            quit_app,
            get_logs_info,
            get_logs_directory
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}