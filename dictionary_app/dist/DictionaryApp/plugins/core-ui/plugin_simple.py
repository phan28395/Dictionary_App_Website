"""
Simple Core UI Plugin for Dictionary App (Console-based for testing)
"""

import sys
import logging
import threading
from pathlib import Path

# Add parent to path for core imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import Plugin, CoreEvents

logger = logging.getLogger(__name__)


class CoreUIPlugin(Plugin):
    """
    Simplified Core UI plugin for testing.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.input_thread = None
        
    def on_load(self):
        """Called when plugin is loaded."""
        logger.info("Simple Core UI plugin loaded")
        
    def on_enable(self):
        """Called when plugin is enabled."""
        super().on_enable()
        logger.info("Simple Core UI plugin enabled")
        
        # Start input thread
        self.input_thread = threading.Thread(target=self._input_loop, daemon=True)
        self.input_thread.start()
        
        # Subscribe to events
        self.app.events.on(CoreEvents.SEARCH_COMPLETE, self._on_search_complete)
        
    def on_disable(self):
        """Called when plugin is disabled."""
        super().on_disable()
        logger.info("Simple Core UI plugin disabled")
        
    def _input_loop(self):
        """Simple input loop for testing."""
        import time
        time.sleep(1)  # Wait for app to initialize
        
        print("\n" + "="*50)
        print("Dictionary App - Simple Console UI")
        print("="*50)
        print("Commands:")
        print("  search <word>  - Search for a word")
        print("  suggest <text> - Get suggestions")
        print("  random        - Get random word")
        print("  wotd          - Word of the day")
        print("  quit          - Exit application")
        print("="*50)
        
        while self.enabled:
            try:
                # Get input
                user_input = input("\n> ").strip()
                
                if not user_input:
                    continue
                
                # Parse command
                parts = user_input.split(maxsplit=1)
                command = parts[0].lower()
                
                if command == 'quit' or command == 'exit':
                    print("Shutting down...")
                    self.app.shutdown()
                    break
                    
                elif command == 'search' and len(parts) > 1:
                    term = parts[1]
                    print(f"Searching for '{term}'...")
                    results = self.app.search(term)
                    self._display_results(results)
                    
                elif command == 'suggest' and len(parts) > 1:
                    prefix = parts[1]
                    suggestions = self.app.get_suggestions(prefix, limit=10)
                    if suggestions:
                        print(f"Suggestions: {', '.join(suggestions)}")
                    else:
                        print("No suggestions found")
                        
                elif command == 'random':
                    result = self.app.get_random_word()
                    if result:
                        print(f"Random word: {result.lemma} ({result.pos})")
                        self._display_results([result])
                    else:
                        print("No random word available")
                        
                elif command == 'wotd':
                    result = self.app.get_word_of_day()
                    if result:
                        print(f"Word of the day: {result.lemma} ({result.pos})")
                        self._display_results([result])
                    else:
                        print("No word of the day available")
                        
                elif command == 'help':
                    print("Commands: search <word>, suggest <text>, random, wotd, quit")
                    
                else:
                    print("Unknown command. Type 'help' for available commands.")
                    
            except EOFError:
                break
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Error in input loop: {e}")
                
    def _display_results(self, results):
        """Display search results in console."""
        if not results:
            print("No results found")
            return
            
        for result in results:
            print(f"\n{'='*40}")
            print(f"{result.lemma} ({result.pos})")
            
            if result.inflection_note:
                print(f"  Note: {result.inflection_note}")
                
            for i, meaning in enumerate(result.meanings[:3], 1):
                print(f"\n  {i}. {meaning.get('definition', 'No definition')}")
                
                examples = meaning.get('examples', [])
                for example in examples[:2]:
                    print(f"     • {example}")
                    
            if len(result.meanings) > 3:
                print(f"\n  ... and {len(result.meanings) - 3} more meanings")
                
    def _on_search_complete(self, term, results):
        """Handle search complete event."""
        logger.debug(f"Search complete for '{term}': {len(results)} results")


# Required for plugin loader
__all__ = ['CoreUIPlugin']