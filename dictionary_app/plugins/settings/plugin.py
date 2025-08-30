"""
Settings Plugin for Dictionary App
Provides configuration management interface.
"""

import sys
import logging
import json
from pathlib import Path
from typing import Any, Dict

# Add parent to path for core imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import Plugin, CoreEvents

try:
    import tkinter as tk
    from tkinter import ttk
    import customtkinter as ctk
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

logger = logging.getLogger(__name__)


class SettingsPlugin(Plugin):
    """
    Settings management plugin.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.settings_window = None
        self.current_tab = "general"
        
    def on_load(self):
        """Called when plugin is loaded."""
        logger.info("Settings plugin loaded")
        
    def on_enable(self):
        """Called when plugin is enabled."""
        super().on_enable()
        logger.info("Settings plugin enabled")
        
        # Subscribe to events
        self.app.events.on('settings.show', self._show_settings)
        self.app.events.on('settings.open_tab', self._open_tab)
        
    def on_disable(self):
        """Called when plugin is disabled."""
        super().on_disable()
        logger.info("Settings plugin disabled")
        
        # Close window if open
        if self.settings_window:
            self.settings_window.destroy()
            self.settings_window = None
            
    def _show_settings(self, tab=None):
        """Show settings window."""
        if not TKINTER_AVAILABLE:
            logger.error("tkinter not available")
            return
            
        if not self.settings_window or not self.settings_window.winfo_exists():
            self._create_settings_window()
            
        if tab:
            self._switch_tab(tab)
            
        self.settings_window.deiconify()
        self.settings_window.lift()
        self.settings_window.focus_force()
        
    def _open_tab(self, tab_name):
        """Open specific tab."""
        self._show_settings(tab_name)
        
    def _create_settings_window(self):
        """Create settings window."""
        self.settings_window = ctk.CTk() if 'CTk' in dir(ctk) else tk.Tk()
        self.settings_window.title("Settings")
        self.settings_window.geometry("700x500")
        
        # Create main container
        main_frame = ctk.CTkFrame(self.settings_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tab view
        self.tab_view = ctk.CTkTabview(main_frame)
        self.tab_view.pack(fill=tk.BOTH, expand=True)
        
        # Add tabs
        self.tab_general = self.tab_view.add("General")
        self.tab_extensions = self.tab_view.add("Extensions")
        self.tab_account = self.tab_view.add("Account")
        self.tab_about = self.tab_view.add("About")
        
        # Create tab contents
        self._create_general_tab()
        self._create_extensions_tab()
        self._create_account_tab()
        self._create_about_tab()
        
        # Button frame
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self._save_settings
        )
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.settings_window.withdraw
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
    def _create_general_tab(self):
        """Create general settings tab."""
        frame = ctk.CTkScrollableFrame(self.tab_general)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Hotkey setting
        hotkey_label = ctk.CTkLabel(frame, text="Global Hotkey:", font=("Arial", 12))
        hotkey_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.hotkey_entry = ctk.CTkEntry(frame, width=200)
        self.hotkey_entry.grid(row=0, column=1, pady=5)
        self.hotkey_entry.insert(0, self.app.get_config('hotkey', 'ctrl+ctrl'))
        
        # Startup options
        startup_label = ctk.CTkLabel(frame, text="Startup Options:", font=("Arial", 12, "bold"))
        startup_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        self.start_minimized = ctk.CTkCheckBox(frame, text="Start minimized")
        self.start_minimized.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=20)
        if self.app.get_config('startup.minimized', False):
            self.start_minimized.select()
            
        self.auto_start = ctk.CTkCheckBox(frame, text="Start with system")
        self.auto_start.grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=20)
        if self.app.get_config('startup.auto_start', False):
            self.auto_start.select()
            
        self.show_tray = ctk.CTkCheckBox(frame, text="Show in system tray")
        self.show_tray.grid(row=4, column=0, columnspan=2, sticky=tk.W, padx=20)
        if self.app.get_config('ui.show_tray', True):
            self.show_tray.select()
            
        # Search settings
        search_label = ctk.CTkLabel(frame, text="Search Settings:", font=("Arial", 12, "bold"))
        search_label.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        cache_label = ctk.CTkLabel(frame, text="Cache size (MB):", font=("Arial", 12))
        cache_label.grid(row=6, column=0, sticky=tk.W, padx=20, pady=5)
        
        self.cache_size = ctk.CTkEntry(frame, width=100)
        self.cache_size.grid(row=6, column=1, pady=5)
        self.cache_size.insert(0, str(self.app.get_config('search.cache.size_mb', 100)))
        
    def _create_extensions_tab(self):
        """Create extensions management tab."""
        frame = ctk.CTkFrame(self.tab_extensions)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title = ctk.CTkLabel(frame, text="Installed Extensions", font=("Arial", 14, "bold"))
        title.pack(pady=10)
        
        # Plugin list frame
        list_frame = ctk.CTkScrollableFrame(frame, height=300)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Get all plugins
        plugins = self.app.get_plugins()
        
        for plugin_id, plugin in plugins.items():
            # Plugin frame
            plugin_frame = ctk.CTkFrame(list_frame)
            plugin_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Plugin info
            info_frame = ctk.CTkFrame(plugin_frame)
            info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=5)
            
            name_label = ctk.CTkLabel(
                info_frame,
                text=plugin.manifest.name if plugin.manifest else plugin_id,
                font=("Arial", 12, "bold")
            )
            name_label.pack(anchor=tk.W)
            
            if plugin.manifest and plugin.manifest.description:
                desc_label = ctk.CTkLabel(
                    info_frame,
                    text=plugin.manifest.description,
                    font=("Arial", 10)
                )
                desc_label.pack(anchor=tk.W)
            
            # Enable/disable switch
            switch = ctk.CTkSwitch(
                plugin_frame,
                text="Enabled",
                command=lambda p=plugin_id: self._toggle_plugin(p)
            )
            switch.pack(side=tk.RIGHT, padx=10)
            
            if plugin.enabled:
                switch.select()
                
        # Bottom buttons
        button_frame = ctk.CTkFrame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        browse_btn = ctk.CTkButton(
            button_frame,
            text="Browse Store",
            command=self._open_extension_store
        )
        browse_btn.pack(side=tk.LEFT, padx=5)
        
        reload_btn = ctk.CTkButton(
            button_frame,
            text="Reload All",
            command=self._reload_plugins
        )
        reload_btn.pack(side=tk.LEFT, padx=5)
        
    def _create_account_tab(self):
        """Create account tab."""
        frame = ctk.CTkFrame(self.tab_account)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        title = ctk.CTkLabel(frame, text="Account & License", font=("Arial", 14, "bold"))
        title.pack(pady=10)
        
        # License status
        status_frame = ctk.CTkFrame(frame)
        status_frame.pack(fill=tk.X, padx=20, pady=10)
        
        status_label = ctk.CTkLabel(status_frame, text="License Status:", font=("Arial", 12))
        status_label.pack(side=tk.LEFT, padx=10)
        
        # Check if licensed (simplified for demo)
        is_licensed = self.app.get_config('license.activated', False)
        status_text = "Premium" if is_licensed else "Free (50 searches)"
        status_color = "green" if is_licensed else "orange"
        
        status_value = ctk.CTkLabel(
            status_frame,
            text=status_text,
            font=("Arial", 12, "bold"),
            text_color=status_color
        )
        status_value.pack(side=tk.LEFT)
        
        # Purchase button if not licensed
        if not is_licensed:
            purchase_btn = ctk.CTkButton(
                frame,
                text="Purchase License ($20)",
                command=self._show_purchase
            )
            purchase_btn.pack(pady=20)
            
    def _create_about_tab(self):
        """Create about tab."""
        frame = ctk.CTkFrame(self.tab_about)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # App name and version
        app_label = ctk.CTkLabel(
            frame,
            text="Dictionary App",
            font=("Arial", 20, "bold")
        )
        app_label.pack(pady=10)
        
        version_label = ctk.CTkLabel(
            frame,
            text=f"Version {self.app.version}",
            font=("Arial", 12)
        )
        version_label.pack()
        
        # Description
        desc_text = """
A powerful, extensible dictionary application
with plugin-based architecture.

Everything is a plugin - even the UI!

Built with Python and love.
        """
        
        desc_label = ctk.CTkLabel(
            frame,
            text=desc_text,
            font=("Arial", 11),
            justify=tk.CENTER
        )
        desc_label.pack(pady=20)
        
        # Links
        link_frame = ctk.CTkFrame(frame)
        link_frame.pack()
        
        github_btn = ctk.CTkButton(
            link_frame,
            text="GitHub",
            width=100,
            command=lambda: logger.info("Open GitHub")
        )
        github_btn.pack(side=tk.LEFT, padx=5)
        
        docs_btn = ctk.CTkButton(
            link_frame,
            text="Documentation",
            width=100,
            command=lambda: logger.info("Open docs")
        )
        docs_btn.pack(side=tk.LEFT, padx=5)
        
    def _toggle_plugin(self, plugin_id):
        """Toggle plugin enabled state."""
        plugin = self.app.get_plugin(plugin_id)
        if plugin:
            if plugin.enabled:
                self.app.disable_plugin(plugin_id)
            else:
                self.app.enable_plugin(plugin_id)
                
    def _reload_plugins(self):
        """Reload all plugins."""
        logger.info("Reloading all plugins...")
        # This would reload plugins - simplified for demo
        
    def _save_settings(self):
        """Save settings."""
        # Save general settings
        if hasattr(self, 'hotkey_entry'):
            self.app.set_config('hotkey', self.hotkey_entry.get())
            
        if hasattr(self, 'start_minimized'):
            self.app.set_config('startup.minimized', self.start_minimized.get())
            
        if hasattr(self, 'auto_start'):
            self.app.set_config('startup.auto_start', self.auto_start.get())
            
        if hasattr(self, 'show_tray'):
            self.app.set_config('ui.show_tray', self.show_tray.get())
            
        if hasattr(self, 'cache_size'):
            try:
                size = int(self.cache_size.get())
                self.app.set_config('search.cache.size_mb', size)
            except ValueError:
                pass
                
        # Save config to file
        self.app.save_config()
        
        # Hide window
        self.settings_window.withdraw()
        
        logger.info("Settings saved")
        
    def _show_purchase(self):
        """Show purchase dialog."""
        logger.info("Show purchase dialog")
        self.app.events.emit('purchase.show')
        
    def _switch_tab(self, tab_name):
        """Switch to specific tab."""
        if tab_name == "general":
            self.tab_view.set("General")
        elif tab_name == "extensions":
            self.tab_view.set("Extensions")
        elif tab_name == "account":
            self.tab_view.set("Account")
        elif tab_name == "about":
            self.tab_view.set("About")
            
    def _open_extension_store(self):
        """Open the extension store window."""
        # Get extension store plugin
        store_plugin = self.app.get_plugin('extension-store')
        if store_plugin and store_plugin.enabled:
            try:
                # Import UI module
                import importlib.util
                ui_spec = importlib.util.spec_from_file_location(
                    "extension_store_ui", 
                    store_plugin.plugin_path.parent / "ui.py"
                )
                ui_module = importlib.util.module_from_spec(ui_spec)
                ui_spec.loader.exec_module(ui_module)
                
                # Create and show store window
                store_ui = ui_module.ExtensionStoreUI(store_plugin)
                store_ui.open_store()
                
            except Exception as e:
                logger.error(f"Failed to open extension store: {e}")
                self._show_error("Extension Store", "Failed to open extension store. Please check if the extension store plugin is properly installed.")
        else:
            self._show_error("Extension Store", "Extension Store plugin is not available or not enabled.")
            
    def _show_error(self, title, message):
        """Show error dialog."""
        try:
            import tkinter.messagebox as mb
            mb.showerror(title, message)
        except Exception:
            logger.error(f"{title}: {message}")