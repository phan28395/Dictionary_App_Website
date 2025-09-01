"""
Core UI Plugin for Dictionary App
Provides system tray, global hotkeys, and search popup functionality.
"""

import sys
import os
import logging
import threading
from pathlib import Path

# Add parent to path for core imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import Plugin, CoreEvents

# UI imports (will fail gracefully if not installed)
try:
    import tkinter as tk
    from tkinter import ttk
    import customtkinter as ctk
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
    print("Warning: tkinter/customtkinter not available")

try:
    import pystray
    from PIL import Image, ImageDraw
    PYSTRAY_AVAILABLE = True
except ImportError as e:
    PYSTRAY_AVAILABLE = False
    print(f"Warning: pystray not available for system tray: {e}")
except Exception as e:
    PYSTRAY_AVAILABLE = False
    print(f"Warning: pystray initialization failed: {e}")

try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    print("Warning: pynput not available for global hotkeys")

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False
    print("Warning: pyperclip not available for clipboard access")

logger = logging.getLogger(__name__)


class CoreUIPlugin(Plugin):
    """
    Core UI plugin providing the default user interface.
    """
    
    def __init__(self, app):
        super().__init__(app)
        
        # UI components
        self.tray_icon = None
        self.search_window = None
        self.hotkey_listener = None
        self.last_hotkey_time = 0
        self.ctrl_pressed_count = 0
        
        # Enhanced hotkey detection
        self.ctrl_is_pressed = False
        self.ctrl_was_released = True
        self.first_ctrl_time = 0
        self.last_trigger_time = 0  # Prevent rapid re-triggers
        
        # Threading
        self.ui_thread = None
        self.tray_thread = None
        
        # Settings
        self.hotkey_combo = "ctrl+ctrl"
        self.show_in_tray = True
        
    def on_load(self):
        """Called when plugin is loaded."""
        logger.info("Core UI plugin loading...")
        
        # Load configuration
        config = self.load_config()
        self.hotkey_combo = config.get('hotkey', 'ctrl+ctrl')
        self.show_in_tray = config.get('show_in_tray', True)
        
        # Set dark mode for customtkinter if available
        if TKINTER_AVAILABLE:
            try:
                ctk.set_appearance_mode("dark")
                ctk.set_default_color_theme("blue")
            except:
                pass
    
    def on_enable(self):
        """Called when plugin is enabled."""
        super().on_enable()
        logger.info("Core UI plugin enabled")
        
        # Start system tray
        if self.show_in_tray and PYSTRAY_AVAILABLE:
            self._start_system_tray()
        
        # Start global hotkey listener
        if PYNPUT_AVAILABLE:
            logger.info(f"Starting hotkey listener for {self.hotkey_combo}")
            self._start_hotkey_listener()
        else:
            logger.warning("pynput not available - global hotkeys disabled")
        
        # Subscribe to search events
        self.app.events.on(CoreEvents.SEARCH_COMPLETE, self._on_search_complete)
    
    def on_disable(self):
        """Called when plugin is disabled."""
        super().on_disable()
        logger.info("Core UI plugin disabled")
        
        # Stop system tray
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
        
        # Stop hotkey listener
        if self.hotkey_listener:
            self.hotkey_listener.stop()
            self.hotkey_listener = None
        
        # Close search window
        if self.search_window:
            self.search_window.destroy()
            self.search_window = None
    
    def _create_tray_icon(self):
        """Create system tray icon image."""
        # Create a simple book icon
        image = Image.new('RGB', (64, 64), color=(73, 109, 137))
        draw = ImageDraw.Draw(image)
        
        # Draw a book shape
        draw.rectangle([10, 10, 54, 54], fill=(255, 255, 255))
        draw.rectangle([12, 12, 52, 52], fill=(73, 109, 137))
        draw.rectangle([14, 14, 50, 50], fill=(255, 255, 255))
        
        # Draw lines to represent text
        for y in range(20, 45, 8):
            draw.rectangle([18, y, 46, y+2], fill=(73, 109, 137))
        
        return image
    
    def _start_system_tray(self):
        """Start system tray icon."""
        if not PYSTRAY_AVAILABLE:
            return
        
        def setup(icon):
            icon.visible = True
            logger.info("System tray icon started")
        
        def on_quit(icon, item):
            """Quit the application."""
            icon.stop()
            self.app.shutdown()
        
        def on_search(icon, item):
            """Show search window."""
            self.show_search_window()
        
        def on_settings(icon, item):
            """Show settings (emit event for settings plugin)."""
            self.app.events.emit('settings.show')
        
        # Create menu
        menu = pystray.Menu(
            pystray.MenuItem("Search", on_search, default=True),
            pystray.MenuItem("Settings", on_settings),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", on_quit)
        )
        
        # Create icon
        image = self._create_tray_icon()
        self.tray_icon = pystray.Icon(
            "dictionary_app",
            image,
            "Dictionary App",
            menu
        )
        
        # Run in thread
        self.tray_thread = threading.Thread(target=lambda: self.tray_icon.run(setup), daemon=True)
        self.tray_thread.start()
    
    def _start_hotkey_listener(self):
        """Start global hotkey listener."""
        if not PYNPUT_AVAILABLE:
            logger.warning("pynput not available - global hotkeys disabled")
            return
        
        import time
        import platform
        
        # Check for Wayland on Linux (known limitation)
        if platform.system() == "Linux":
            wayland_session = any([
                "wayland" in str(os.environ.get("XDG_SESSION_TYPE", "")).lower(),
                "wayland" in str(os.environ.get("WAYLAND_DISPLAY", "")).lower(),
                os.environ.get("WAYLAND_DISPLAY") is not None
            ])
            if wayland_session:
                logger.warning("Wayland detected - global hotkeys may not work due to security restrictions")
                logger.info("Try using X11 session or access search via system tray")
        
        def on_press(key):
            """Handle key press."""
            current_time = time.time()
            
            # Check for Ctrl+Ctrl (double tap) - Enhanced version
            if self.hotkey_combo == "ctrl+ctrl":
                if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                    # Prevent rapid re-triggers (cooldown period)
                    if current_time - self.last_trigger_time < 1.0:
                        return
                    
                    if not self.ctrl_is_pressed:  # Ctrl not currently held
                        if self.ctrl_was_released and self.first_ctrl_time > 0:
                            # This is the second Ctrl press
                            time_diff = current_time - self.first_ctrl_time
                            if 0.1 <= time_diff <= 0.3:  # Between 100-300ms
                                # Valid double tap detected!
                                logger.info("Enhanced Double Ctrl detected - triggering search")
                                self.last_trigger_time = current_time
                                self._reset_hotkey_state()
                                self._handle_hotkey_triggered()
                                return
                        
                        # First Ctrl press or invalid timing
                        self.first_ctrl_time = current_time
                        self.ctrl_was_released = False
                    
                    self.ctrl_is_pressed = True
                
                # Reset state if any other key is pressed during Ctrl+Ctrl sequence
                elif self.first_ctrl_time > 0:
                    self._reset_hotkey_state()
            
            # Check for Super+Super (double tap)
            elif self.hotkey_combo == "super+super":
                # Check for Super/Meta/Windows key across platforms
                is_super_key = False
                try:
                    # Linux: Meta/Super keys
                    if (hasattr(keyboard.Key, 'cmd') and key == keyboard.Key.cmd) or \
                       (hasattr(keyboard.Key, 'cmd_l') and key == keyboard.Key.cmd_l) or \
                       (hasattr(keyboard.Key, 'cmd_r') and key == keyboard.Key.cmd_r):
                        is_super_key = True
                    # Alternative check for string representation
                    elif hasattr(key, 'name') and key.name in ['cmd', 'cmd_l', 'cmd_r']:
                        is_super_key = True
                    # Try to catch by value for Linux Meta key
                    elif str(key) in ["'\\xff\\xeb'", "'\\xff\\xec'"]:  # Meta_L, Meta_R
                        is_super_key = True
                except:
                    pass
                
                if is_super_key:
                    if current_time - self.last_hotkey_time < 0.5:  # Within 500ms
                        # Double Super pressed
                        self.ctrl_pressed_count = 0
                        self.last_hotkey_time = 0
                        
                        # Get selected text and search
                        self._handle_hotkey_triggered()
                    else:
                        self.ctrl_pressed_count = 1
                        self.last_hotkey_time = current_time
        
        def on_release(key):
            """Handle key release to track Ctrl state properly."""
            if self.hotkey_combo == "ctrl+ctrl":
                if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                    self.ctrl_is_pressed = False
                    self.ctrl_was_released = True
        
        # Start listener
        self.hotkey_listener = keyboard.Listener(
            on_press=on_press,
            on_release=on_release
        )
        self.hotkey_listener.daemon = True
        self.hotkey_listener.start()
        
        logger.info(f"Global hotkey listener started for {self.hotkey_combo}")
    
    def _reset_hotkey_state(self):
        """Reset hotkey detection state."""
        self.ctrl_is_pressed = False
        self.ctrl_was_released = True
        self.first_ctrl_time = 0
    
    def _handle_hotkey_triggered(self):
        """Handle when hotkey is triggered."""
        logger.info("Hotkey triggered")
        
        # Emit event
        self.app.events.emit(CoreEvents.HOTKEY_TRIGGERED)
        
        # Try to get selected text
        selected_text = self._get_selected_text()
        
        # Show search window
        if selected_text:
            self.show_search_window(selected_text)
        else:
            self.show_search_window()
    
    def _get_selected_text(self):
        """Get currently selected text from any application."""
        if not CLIPBOARD_AVAILABLE:
            return None
        
        try:
            # Save current clipboard
            old_clipboard = pyperclip.paste()
            
            # Clear clipboard
            pyperclip.copy('')
            
            # Simulate Ctrl+C using pynput
            if PYNPUT_AVAILABLE:
                controller = keyboard.Controller()
                with controller.pressed(keyboard.Key.ctrl):
                    controller.press('c')
                    controller.release('c')
                
                # Wait a bit for clipboard to update
                import time
                time.sleep(0.1)
                
                # Get new clipboard content
                selected = pyperclip.paste()
                
                # Restore old clipboard
                pyperclip.copy(old_clipboard)
                
                return selected if selected else None
        except Exception as e:
            logger.error(f"Error getting selected text: {e}")
            return None
        
        return None
    
    def show_search_window(self, initial_text=None):
        """Show the search popup window."""
        if not TKINTER_AVAILABLE:
            logger.error("tkinter not available, cannot show search window")
            return
        
        # Create window if it doesn't exist
        if not self.search_window or not self.search_window.winfo_exists():
            self._create_search_window()
        
        # Set initial text if provided
        if initial_text and hasattr(self, 'search_entry'):
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, initial_text)
            # Trigger full search immediately when text is populated via hotkey
            self._on_search_submit()
        
        # Show and focus window
        self.search_window.deiconify()
        self.search_window.lift()
        self.search_window.focus_force()
        if hasattr(self, 'search_entry'):
            self.search_entry.focus()
        
        # Position near cursor
        self._position_window_near_cursor()
        
        # Emit event
        self.app.events.emit(CoreEvents.WINDOW_SHOW)
    
    def _create_search_window(self):
        """Create the search popup window."""
        # Create window
        self.search_window = ctk.CTk() if 'CTk' in dir(ctk) else tk.Tk()
        self.search_window.title("Dictionary Search")
        
        # Make frameless and always on top
        self.search_window.overrideredirect(True)
        self.search_window.attributes('-topmost', True)
        
        # Set size
        self.search_window.geometry("500x400")
        
        # Create main frame with border
        main_frame = ctk.CTkFrame(self.search_window, corner_radius=10)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Create title bar for dragging
        title_frame = ctk.CTkFrame(main_frame, height=30)
        title_frame.pack(fill=tk.X, padx=5, pady=5)
        
        title_label = ctk.CTkLabel(title_frame, text="Dictionary", font=("Arial", 14, "bold"))
        title_label.pack(side=tk.LEFT, padx=10)
        
        close_btn = ctk.CTkButton(
            title_frame, text="✕", width=30,
            command=self._hide_search_window
        )
        close_btn.pack(side=tk.RIGHT, padx=5)
        
        # Make window draggable
        self._make_draggable(title_frame)
        
        # Search box
        search_frame = ctk.CTkFrame(main_frame)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.search_entry = ctk.CTkEntry(
            search_frame, 
            placeholder_text="Search for a word...",
            height=40,
            font=("Arial", 14)
        )
        self.search_entry.pack(fill=tk.X, padx=5, pady=5)
        
        # Bind events
        self.search_entry.bind('<KeyRelease>', lambda e: self._on_search_changed())
        self.search_entry.bind('<Return>', lambda e: self._on_search_submit())
        self.search_entry.bind('<Escape>', lambda e: self._hide_search_window())
        
        # Results area
        self.results_frame = ctk.CTkScrollableFrame(main_frame, height=300)
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Status label
        self.status_label = ctk.CTkLabel(main_frame, text="Ready", font=("Arial", 10))
        self.status_label.pack(pady=5)
        
        # Bind close on focus lost (optional)
        # self.search_window.bind('<FocusOut>', lambda e: self._hide_search_window())
    
    def _make_draggable(self, widget):
        """Make a widget draggable."""
        def start_drag(event):
            widget.x = event.x
            widget.y = event.y
        
        def drag(event):
            deltax = event.x - widget.x
            deltay = event.y - widget.y
            x = self.search_window.winfo_x() + deltax
            y = self.search_window.winfo_y() + deltay
            self.search_window.geometry(f"+{x}+{y}")
        
        widget.bind("<Button-1>", start_drag)
        widget.bind("<B1-Motion>", drag)
    
    def _position_window_near_cursor(self):
        """Position window near mouse cursor."""
        # Get cursor position
        x = self.search_window.winfo_pointerx()
        y = self.search_window.winfo_pointery()
        
        # Offset to not cover cursor
        x += 10
        y += 10
        
        # Get screen dimensions
        screen_width = self.search_window.winfo_screenwidth()
        screen_height = self.search_window.winfo_screenheight()
        
        # Get window dimensions
        window_width = 500
        window_height = 400
        
        # Adjust if window would go off screen
        if x + window_width > screen_width:
            x = screen_width - window_width - 10
        if y + window_height > screen_height:
            y = screen_height - window_height - 10
        
        self.search_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    def _hide_search_window(self):
        """Hide the search window."""
        if self.search_window:
            self.search_window.withdraw()
            # Emit event
            self.app.events.emit(CoreEvents.WINDOW_HIDE)
    
    def _on_search_changed(self):
        """Handle search text change."""
        search_text = self.search_entry.get()
        
        if len(search_text) >= 2:
            # Show suggestions
            suggestions = self.app.get_suggestions(search_text, limit=5)
            if suggestions:
                self._show_suggestions(suggestions)
    
    def _on_search_submit(self):
        """Handle search submission."""
        search_text = self.search_entry.get().strip()
        
        if search_text:
            self.status_label.configure(text="Searching...")
            
            # Perform search
            results = self.app.search(search_text)
            
            if results:
                self.status_label.configure(text=f"Found {len(results)} result(s)")
                self._display_results(results)
            else:
                self.status_label.configure(text="No results found")
                self._clear_results()
    
    def _show_suggestions(self, suggestions):
        """Show autocomplete suggestions."""
        # For now, just update status
        self.status_label.configure(text=f"Suggestions: {', '.join(suggestions)}")
    
    def _clear_results(self):
        """Clear results display."""
        for widget in self.results_frame.winfo_children():
            widget.destroy()
    
    def _display_results(self, results):
        """Display search results."""
        self._clear_results()
        
        for result in results:
            # Create result card
            card = ctk.CTkFrame(self.results_frame, corner_radius=5)
            card.pack(fill=tk.X, padx=5, pady=5)
            
            # Header with lemma and POS
            header_frame = ctk.CTkFrame(card)
            header_frame.pack(fill=tk.X, padx=10, pady=5)
            
            lemma_label = ctk.CTkLabel(
                header_frame,
                text=result.lemma,
                font=("Arial", 16, "bold")
            )
            lemma_label.pack(side=tk.LEFT)
            
            pos_label = ctk.CTkLabel(
                header_frame,
                text=f"({result.pos})",
                font=("Arial", 12)
            )
            pos_label.pack(side=tk.LEFT, padx=10)
            
            # Inflection note if present
            if result.inflection_note:
                inflection_label = ctk.CTkLabel(
                    card,
                    text=result.inflection_note,
                    font=("Arial", 10, "italic")
                )
                inflection_label.pack(anchor=tk.W, padx=10)
            
            # Meanings
            for i, meaning in enumerate(result.meanings[:3], 1):  # Show first 3 meanings
                meaning_frame = ctk.CTkFrame(card, fg_color="transparent")
                meaning_frame.pack(fill=tk.X, padx=10, pady=2)
                
                # Definition
                definition_text = f"{i}. {meaning.get('definition', 'No definition')}"
                definition_label = ctk.CTkLabel(
                    meaning_frame,
                    text=definition_text,
                    font=("Arial", 12),
                    justify=tk.LEFT,
                    wraplength=450
                )
                definition_label.pack(anchor=tk.W)
                
                # Examples (first 2)
                examples = meaning.get('examples', [])
                if examples:
                    for example in examples[:2]:
                        example_label = ctk.CTkLabel(
                            meaning_frame,
                            text=f"  • {example}",
                            font=("Arial", 10, "italic"),
                            justify=tk.LEFT,
                            wraplength=430
                        )
                        example_label.pack(anchor=tk.W, padx=20)
            
            # Show more button if more than 3 meanings
            if len(result.meanings) > 3:
                more_btn = ctk.CTkButton(
                    card,
                    text=f"Show {len(result.meanings) - 3} more meanings",
                    height=25,
                    command=lambda r=result: self._show_full_result(r)
                )
                more_btn.pack(pady=5)
    
    def _show_full_result(self, result):
        """Show full result in a new window or expanded view."""
        # TODO: Implement full result view
        logger.info(f"Show full result for {result.lemma}")
    
    def _on_search_complete(self, term, results):
        """Handle search complete event."""
        logger.debug(f"Search complete for '{term}': {len(results)} results")


# Required for plugin loader
__all__ = ['CoreUIPlugin']