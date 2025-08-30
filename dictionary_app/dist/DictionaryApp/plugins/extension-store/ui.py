#!/usr/bin/env python3
"""
Extension Store UI Components

Simple UI for browsing and managing extensions.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import logging
import threading
from datetime import datetime

logger = logging.getLogger(__name__)

class ExtensionStoreWindow:
    """Main extension store window"""
    
    def __init__(self, store_plugin):
        self.store = store_plugin
        self.window = None
        self.extensions_frame = None
        self.search_var = None
        self.category_var = None
        self.sort_var = None
        
    def show(self):
        """Show the extension store window"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
            
        self.window = tk.Toplevel()
        self.window.title("Extension Store")
        self.window.geometry("800x600")
        self.window.resizable(True, True)
        
        # Create UI
        self._create_ui()
        self._load_extensions()
        
    def _create_ui(self):
        """Create the UI components"""
        # Top toolbar
        toolbar = ttk.Frame(self.window)
        toolbar.pack(fill='x', padx=10, pady=5)
        
        # Search
        ttk.Label(toolbar, text="Search:").pack(side='left', padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=30)
        search_entry.pack(side='left', padx=(0, 10))
        search_entry.bind('<Return>', lambda e: self._filter_extensions())
        
        # Category filter
        ttk.Label(toolbar, text="Category:").pack(side='left', padx=(0, 5))
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(toolbar, textvariable=self.category_var, 
                                    values=['All'] + self.store.get_categories(), 
                                    state='readonly', width=15)
        category_combo.set('All')
        category_combo.pack(side='left', padx=(0, 10))
        category_combo.bind('<<ComboboxSelected>>', lambda e: self._filter_extensions())
        
        # Sort
        ttk.Label(toolbar, text="Sort:").pack(side='left', padx=(0, 5))
        self.sort_var = tk.StringVar()
        sort_combo = ttk.Combobox(toolbar, textvariable=self.sort_var,
                                values=['Popular', 'New', 'Updated', 'Rating', 'Name'],
                                state='readonly', width=10)
        sort_combo.set('Popular')
        sort_combo.pack(side='left', padx=(0, 10))
        sort_combo.bind('<<ComboboxSelected>>', lambda e: self._filter_extensions())
        
        # Refresh button
        ttk.Button(toolbar, text="Refresh", 
                  command=self._refresh_registry).pack(side='right')
        
        # Installed button
        ttk.Button(toolbar, text="Installed", 
                  command=self._show_installed).pack(side='right', padx=(0, 5))
        
        # Main content area with scrollbar
        content_frame = ttk.Frame(self.window)
        content_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Scrollable frame
        canvas = tk.Canvas(content_frame)
        scrollbar = ttk.Scrollbar(content_frame, orient='vertical', command=canvas.yview)
        self.extensions_frame = ttk.Frame(canvas)
        
        self.extensions_frame.bind('<Configure>', 
                                 lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        
        canvas.create_window((0, 0), window=self.extensions_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.window, textvariable=self.status_var, 
                             relief='sunken', anchor='w')
        status_bar.pack(side='bottom', fill='x')
        
    def _load_extensions(self):
        """Load and display extensions"""
        self.status_var.set("Loading extensions...")
        
        # Clear existing
        for widget in self.extensions_frame.winfo_children():
            widget.destroy()
            
        try:
            extensions = self.store.get_extensions()
            
            if not extensions:
                ttk.Label(self.extensions_frame, 
                         text="No extensions available. Try refreshing the registry.",
                         font=('TkDefaultFont', 12)).pack(pady=50)
                self.status_var.set("No extensions found")
                return
                
            for i, ext in enumerate(extensions):
                self._create_extension_card(ext, i)
                
            self.status_var.set(f"Showing {len(extensions)} extensions")
            
        except Exception as e:
            logger.error(f"Error loading extensions: {e}")
            ttk.Label(self.extensions_frame, 
                     text=f"Error loading extensions: {e}",
                     foreground='red').pack(pady=50)
            self.status_var.set("Error loading extensions")
            
    def _create_extension_card(self, extension, row):
        """Create a card for an extension"""
        card_frame = ttk.LabelFrame(self.extensions_frame, text="", padding=10)
        card_frame.pack(fill='x', pady=5)
        
        # Header with name and version
        header_frame = ttk.Frame(card_frame)
        header_frame.pack(fill='x')
        
        name_label = ttk.Label(header_frame, text=extension.get('name', 'Unknown'), 
                             font=('TkDefaultFont', 11, 'bold'))
        name_label.pack(side='left')
        
        version_label = ttk.Label(header_frame, text=f"v{extension.get('version', '?')}")
        version_label.pack(side='left', padx=(10, 0))
        
        # Author
        if extension.get('author'):
            author_label = ttk.Label(header_frame, text=f"by {extension['author']}")
            author_label.pack(side='right')
            
        # Description
        if extension.get('description'):
            desc_label = ttk.Label(card_frame, text=extension['description'], 
                                 wraplength=600, justify='left')
            desc_label.pack(anchor='w', pady=(5, 0))
            
        # Tags and categories
        tags_frame = ttk.Frame(card_frame)
        tags_frame.pack(fill='x', pady=(5, 0))
        
        # Categories
        categories = extension.get('categories', [])
        if categories:
            for cat in categories[:3]:  # Show max 3 categories
                tag_label = ttk.Label(tags_frame, text=cat, 
                                    background='lightblue', 
                                    padding=(4, 2))
                tag_label.pack(side='left', padx=(0, 5))
                
        # Action buttons
        button_frame = ttk.Frame(card_frame)
        button_frame.pack(anchor='e', pady=(10, 0))
        
        ext_id = extension.get('id')
        
        if self.store.is_extension_installed(ext_id):
            if self.store.is_extension_enabled(ext_id):
                ttk.Button(button_frame, text="Enabled", state='disabled').pack(side='right')
                ttk.Button(button_frame, text="Uninstall", 
                          command=lambda: self._uninstall_extension(ext_id)).pack(side='right', padx=(0, 5))
            else:
                ttk.Button(button_frame, text="Enable",
                          command=lambda: self._enable_extension(ext_id)).pack(side='right')
                ttk.Button(button_frame, text="Uninstall", 
                          command=lambda: self._uninstall_extension(ext_id)).pack(side='right', padx=(0, 5))
        else:
            ttk.Button(button_frame, text="Install", 
                      command=lambda: self._install_extension(ext_id)).pack(side='right')
            
        ttk.Button(button_frame, text="Details", 
                  command=lambda: self._show_details(ext_id)).pack(side='right', padx=(0, 5))
        
    def _filter_extensions(self):
        """Filter extensions based on search and filters"""
        search = self.search_var.get().strip()
        category = self.category_var.get()
        sort_by = self.sort_var.get().lower()
        
        # Clear existing
        for widget in self.extensions_frame.winfo_children():
            widget.destroy()
            
        try:
            extensions = self.store.get_extensions(
                category=None if category == 'All' else category,
                search=search if search else None,
                sort_by=sort_by
            )
            
            for i, ext in enumerate(extensions):
                self._create_extension_card(ext, i)
                
            self.status_var.set(f"Showing {len(extensions)} extensions")
            
        except Exception as e:
            logger.error(f"Error filtering extensions: {e}")
            self.status_var.set(f"Error: {e}")
            
    def _refresh_registry(self):
        """Refresh the extension registry"""
        def refresh_thread():
            try:
                self.status_var.set("Refreshing registry...")
                self.store.update_registry()
                self.window.after(0, self._load_extensions)
            except Exception as e:
                logger.error(f"Failed to refresh registry: {e}")
                self.window.after(0, lambda: self.status_var.set(f"Refresh failed: {e}"))
                
        thread = threading.Thread(target=refresh_thread, daemon=True)
        thread.start()
        
    def _install_extension(self, extension_id):
        """Install an extension"""
        def install_thread():
            try:
                self.window.after(0, lambda: self.status_var.set(f"Installing {extension_id}..."))
                self.store.install_extension(extension_id)
                self.window.after(0, lambda: [
                    self.status_var.set(f"Installed {extension_id} successfully"),
                    self._load_extensions()
                ])
            except Exception as e:
                logger.error(f"Failed to install {extension_id}: {e}")
                self.window.after(0, lambda: [
                    messagebox.showerror("Installation Failed", str(e)),
                    self.status_var.set("Installation failed")
                ])
                
        if messagebox.askyesno("Install Extension", 
                              f"Install extension '{extension_id}'?"):
            thread = threading.Thread(target=install_thread, daemon=True)
            thread.start()
            
    def _uninstall_extension(self, extension_id):
        """Uninstall an extension"""
        if messagebox.askyesno("Uninstall Extension", 
                              f"Uninstall extension '{extension_id}'?\nThis will remove all extension data."):
            try:
                self.store.uninstall_extension(extension_id)
                self.status_var.set(f"Uninstalled {extension_id}")
                self._load_extensions()
            except Exception as e:
                logger.error(f"Failed to uninstall {extension_id}: {e}")
                messagebox.showerror("Uninstall Failed", str(e))
                
    def _enable_extension(self, extension_id):
        """Enable an extension"""
        try:
            self.store.app.plugin_manager.enable_plugin(extension_id)
            self.status_var.set(f"Enabled {extension_id}")
            self._load_extensions()
        except Exception as e:
            logger.error(f"Failed to enable {extension_id}: {e}")
            messagebox.showerror("Enable Failed", str(e))
            
    def _show_details(self, extension_id):
        """Show extension details"""
        details = self.store.get_extension_details(extension_id)
        if not details:
            messagebox.showerror("Error", "Extension details not found")
            return
            
        # Create details window
        details_window = tk.Toplevel(self.window)
        details_window.title(f"Extension Details - {details.get('name', 'Unknown')}")
        details_window.geometry("600x500")
        details_window.resizable(True, True)
        
        # Scrollable text area
        text_area = scrolledtext.ScrolledText(details_window, wrap=tk.WORD, 
                                            font=('TkDefaultFont', 10))
        text_area.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Format details
        content = f"Name: {details.get('name', 'Unknown')}\n"
        content += f"Version: {details.get('version', 'Unknown')}\n"
        content += f"Author: {details.get('author', 'Unknown')}\n"
        content += f"ID: {details.get('id', 'Unknown')}\n\n"
        content += f"Description:\n{details.get('description', 'No description available')}\n\n"
        
        if details.get('categories'):
            content += f"Categories: {', '.join(details['categories'])}\n\n"
            
        if details.get('tags'):
            content += f"Tags: {', '.join(details['tags'])}\n\n"
            
        content += f"Downloads: {details.get('downloads', 0)}\n"
        content += f"Rating: {details.get('rating', 0)}/5\n"
        content += f"Installed: {'Yes' if details.get('installed') else 'No'}\n"
        content += f"Enabled: {'Yes' if details.get('enabled') else 'No'}\n"
        
        if details.get('homepage'):
            content += f"\nHomepage: {details['homepage']}\n"
            
        if details.get('repository'):
            content += f"Repository: {details['repository']}\n"
            
        text_area.insert(tk.END, content)
        text_area.config(state=tk.DISABLED)
        
    def _show_installed(self):
        """Show installed extensions"""
        installed_window = tk.Toplevel(self.window)
        installed_window.title("Installed Extensions")
        installed_window.geometry("700x500")
        
        # Create treeview
        tree = ttk.Treeview(installed_window, columns=('Version', 'Author', 'Status'), show='tree headings')
        tree.heading('#0', text='Name')
        tree.heading('Version', text='Version')
        tree.heading('Author', text='Author')
        tree.heading('Status', text='Status')
        
        tree.column('#0', width=200)
        tree.column('Version', width=100)
        tree.column('Author', width=150)
        tree.column('Status', width=100)
        
        # Load installed extensions
        installed = self.store.get_installed_extensions()
        for ext in installed:
            status = "Enabled" if ext['enabled'] else "Disabled"
            tree.insert('', 'end', text=ext['name'], 
                       values=(ext['version'], ext.get('author', ''), status))
                       
        tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Button frame
        button_frame = ttk.Frame(installed_window)
        button_frame.pack(pady=5)
        
        ttk.Button(button_frame, text="Close", 
                  command=installed_window.destroy).pack()


class ExtensionStoreUI:
    """UI integration for extension store"""
    
    def __init__(self, store_plugin):
        self.store = store_plugin
        self.store_window = None
        
    def open_store(self):
        """Open the extension store window"""
        if not self.store_window:
            self.store_window = ExtensionStoreWindow(self.store)
        self.store_window.show()
        
    def manage_installed(self):
        """Open installed extensions manager"""
        if not self.store_window:
            self.store_window = ExtensionStoreWindow(self.store)
        self.store_window.show()
        self.store_window._show_installed()
        
    def check_updates(self):
        """Check for extension updates"""
        try:
            self.store.update_registry()
            messagebox.showinfo("Updates", "Registry updated successfully!")
        except Exception as e:
            messagebox.showerror("Update Failed", f"Failed to update registry: {e}")