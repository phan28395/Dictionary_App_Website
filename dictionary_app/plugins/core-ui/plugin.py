"""
Core UI Plugin for Dictionary App
Provides system tray, global hotkeys, and search popup functionality.
"""

import sys
import logging
import threading
import queue
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
        
        # Threading
        self.ui_thread = None
        self.tray_thread = None
        self.ui_queue = queue.Queue()
        self.main_thread_id = threading.get_ident()
        
        # Tkinter root for main loop
        self.root = None
        
        # Performance optimization
        self.ui_queue_active = False
        self.poll_interval = 100  # Start with 100ms
        self.max_poll_interval = 500  # Max 500ms when idle
        
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
        
        # Initialize Tkinter root in main thread
        if TKINTER_AVAILABLE and threading.current_thread() is threading.main_thread():
            self._init_tkinter_root()
    
    def on_enable(self):
        """Called when plugin is enabled."""
        super().on_enable()
        logger.info("Core UI plugin enabled")
        
        # Initialize Tkinter if not already done
        if TKINTER_AVAILABLE and not self.root:
            self._init_tkinter_root()
        
        # Start system tray
        if self.show_in_tray and PYSTRAY_AVAILABLE:
            self._start_system_tray()
        
        # Start global hotkey listener
        if PYNPUT_AVAILABLE:
            self._start_hotkey_listener()
        
        # Start UI processing
        if self.root:
            self._process_ui_queue()
        
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
        
        # Stop tkinter root
        if self.root:
            self.root.quit()
            self.root = None
    
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
    
    def _init_tkinter_root(self):
        """Initialize Tkinter root window."""
        if not TKINTER_AVAILABLE:
            return
        
        self.root = tk.Tk()
        self.root.withdraw()  # Hide root window
        self.root.title("Dictionary App")
        
        logger.info("Tkinter root initialized")
    
    def _process_ui_queue(self):
        """Process UI operations from queue in main thread."""
        if not self.root:
            return
        
        operations_processed = 0
        
        try:
            # Process all queued UI operations
            while True:
                try:
                    operation = self.ui_queue.get_nowait()
                    operation()
                    operations_processed += 1
                except queue.Empty:
                    break
        except Exception as e:
            logger.error(f"Error processing UI queue: {e}")
        
        # Adaptive polling: reduce interval when idle, increase when active
        if operations_processed > 0:
            self.ui_queue_active = True
            self.poll_interval = 50  # Fast polling when active
        else:
            if self.ui_queue_active:
                # Just became idle, start backing off
                self.ui_queue_active = False
                self.poll_interval = 100
            else:
                # Stay idle, increase interval up to max
                self.poll_interval = min(self.poll_interval * 1.5, self.max_poll_interval)
        
        # Schedule next check with adaptive interval
        self.root.after(int(self.poll_interval), self._process_ui_queue)
    
    def _queue_ui_operation(self, operation):
        """Queue a UI operation to be executed in main thread."""
        self.ui_queue.put(operation)
    
    def run_main_loop(self):
        """Run the main Tkinter event loop."""
        if self.root:
            logger.info("Starting Tkinter main loop")
            self.root.mainloop()
    
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
            self._queue_ui_operation(lambda: self.show_search_window())
        
        def on_settings(icon, item):
            """Show settings window."""
            self._queue_ui_operation(lambda: self._show_settings_window())
        
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
            return
        
        import time
        
        def on_press(key):
            """Handle key press."""
            current_time = time.time()
            
            # Check for Ctrl+Ctrl (double tap)
            if self.hotkey_combo == "ctrl+ctrl":
                if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                    if current_time - self.last_hotkey_time < 0.5:  # Within 500ms
                        # Double Ctrl pressed
                        self.ctrl_pressed_count = 0
                        self.last_hotkey_time = 0
                        
                        # Get selected text and search
                        self._handle_hotkey_triggered()
                    else:
                        self.ctrl_pressed_count = 1
                        self.last_hotkey_time = current_time
        
        def on_release(key):
            """Handle key release."""
            pass
        
        # Start listener
        self.hotkey_listener = keyboard.Listener(
            on_press=on_press,
            on_release=on_release
        )
        self.hotkey_listener.daemon = True
        self.hotkey_listener.start()
        
        logger.info(f"Global hotkey listener started for {self.hotkey_combo}")
    
    def _handle_hotkey_triggered(self):
        """Handle when hotkey is triggered."""
        logger.info("Hotkey triggered")
        
        # Emit event
        self.app.events.emit(CoreEvents.HOTKEY_TRIGGERED)
        
        # Try to get selected text
        selected_text = self._get_selected_text()
        
        # Queue UI operation for main thread
        if selected_text:
            self._queue_ui_operation(lambda: self.show_search_window(selected_text))
        else:
            self._queue_ui_operation(lambda: self.show_search_window())
    
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
        if not TKINTER_AVAILABLE or not self.root:
            logger.error("tkinter not available, cannot show search window")
            return
        
        # Create window if it doesn't exist
        if not self.search_window or not self.search_window.winfo_exists():
            self._create_search_window()
        
        # Set initial text if provided
        if initial_text and hasattr(self, 'search_entry'):
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, initial_text)
            # Trigger search
            self._on_search_changed()
        
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
                
                # Short meaning (bold) with frequency indicator
                short_meaning = meaning.get('meaning', 'No meaning')
                frequency = meaning.get('frequency_meaning', 0)
                
                # Create frequency indicator (dots)
                if frequency > 0.4:
                    freq_indicator = "●●●"  # Very common
                elif frequency > 0.2:
                    freq_indicator = "●●○"  # Common  
                elif frequency > 0.1:
                    freq_indicator = "●○○"  # Less common
                else:
                    freq_indicator = "○○○"  # Rare
                
                meaning_text = f"{i}. {short_meaning}"
                
                # Create header frame for meaning and frequency
                meaning_header = ctk.CTkFrame(meaning_frame, fg_color="transparent")
                meaning_header.pack(fill=tk.X)
                
                meaning_label = ctk.CTkLabel(
                    meaning_header,
                    text=meaning_text,
                    font=("Arial", 12, "bold"),
                    justify=tk.LEFT,
                    wraplength=380
                )
                meaning_label.pack(side=tk.LEFT, anchor=tk.W)
                
                # Frequency indicator
                freq_label = ctk.CTkLabel(
                    meaning_header,
                    text=freq_indicator,
                    font=("Arial", 10),
                    text_color=("orange", "yellow")
                )
                freq_label.pack(side=tk.RIGHT, anchor=tk.E, padx=5)
                
                # Full definition (regular text, slightly smaller)
                definition = meaning.get('definition', '')
                if definition and definition != short_meaning:  # Only show if different from meaning
                    definition_label = ctk.CTkLabel(
                        meaning_frame,
                        text=f"   {definition}",
                        font=("Arial", 11),
                        justify=tk.LEFT,
                        wraplength=430,
                        text_color=("gray60", "gray40")  # Slightly muted color
                    )
                    definition_label.pack(anchor=tk.W, pady=(2, 0))
                
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
    def _show_settings_window(self):
        """Show simple settings window."""
        if not TKINTER_AVAILABLE or not self.root:
            logger.error("tkinter not available, cannot show settings window")
            return
        
        # Create settings window
        settings_win = ctk.CTkToplevel(self.root)
        settings_win.title("Settings")
        settings_win.geometry("400x300")
        settings_win.attributes('-topmost', True)
        
        # Create main frame
        main_frame = ctk.CTkFrame(settings_win)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(main_frame, text="Dictionary App Settings", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Hotkey setting
        hotkey_frame = ctk.CTkFrame(main_frame)
        hotkey_frame.pack(fill=tk.X, pady=10)
        
        ctk.CTkLabel(hotkey_frame, text="Hotkey:").pack(side=tk.LEFT, padx=10, pady=10)
        hotkey_var = tk.StringVar(value=self.hotkey_combo)
        hotkey_entry = ctk.CTkEntry(hotkey_frame, textvariable=hotkey_var)
        hotkey_entry.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Tray setting
        tray_frame = ctk.CTkFrame(main_frame)
        tray_frame.pack(fill=tk.X, pady=10)
        
        ctk.CTkLabel(tray_frame, text="Show in system tray:").pack(side=tk.LEFT, padx=10, pady=10)
        tray_var = tk.BooleanVar(value=self.show_in_tray)
        tray_check = ctk.CTkCheckBox(tray_frame, text="", variable=tray_var)
        tray_check.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        def save_settings():
            self.hotkey_combo = hotkey_var.get()
            self.show_in_tray = tray_var.get()
            logger.info(f"Settings saved: hotkey={self.hotkey_combo}, tray={self.show_in_tray}")
            settings_win.destroy()
        
        save_btn = ctk.CTkButton(button_frame, text="Save", command=save_settings)
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        cancel_btn = ctk.CTkButton(button_frame, text="Cancel", command=settings_win.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        # Center window
        settings_win.update_idletasks()
        x = (settings_win.winfo_screenwidth() - settings_win.winfo_width()) // 2
        y = (settings_win.winfo_screenheight() - settings_win.winfo_height()) // 2
        settings_win.geometry(f"+{x}+{y}")
        
        logger.info("Settings window opened")


# Required for plugin loader
__all__ = ['CoreUIPlugin']