"""
Event system for Dictionary App.
Provides event emission and listening capabilities for plugins.
"""

import logging
import time
import threading
from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
from enum import Enum

logger = logging.getLogger(__name__)


class EventPriority(Enum):
    """Event listener priority levels."""
    HIGHEST = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    LOWEST = 4


@dataclass
class EventListener:
    """Represents an event listener."""
    callback: Callable
    priority: EventPriority
    plugin_id: Optional[str]
    once: bool = False
    
    def __lt__(self, other):
        """Compare by priority for sorting."""
        return self.priority.value < other.priority.value


class EventEmitter:
    """
    Event emitter system for plugin communication.
    """
    
    def __init__(self, debug_mode: bool = False):
        """
        Initialize event emitter.
        
        Args:
            debug_mode: Enable debug logging for events
        """
        self.debug_mode = debug_mode
        self._listeners: Dict[str, List[EventListener]] = defaultdict(list)
        self._wildcard_listeners: List[EventListener] = []
        self._lock = threading.RLock()
        self._event_stack = []  # For detecting infinite loops
        self._max_stack_depth = 100
        
        # Performance tracking
        self._event_metrics = defaultdict(lambda: {'count': 0, 'total_time': 0})
    
    def on(self, event_name: str, callback: Callable, 
           priority: EventPriority = EventPriority.NORMAL,
           plugin_id: Optional[str] = None) -> Callable:
        """
        Register an event listener.
        
        Args:
            event_name: Name of the event or '*' for wildcard
            callback: Function to call when event fires
            priority: Listener priority
            plugin_id: ID of plugin registering listener
            
        Returns:
            The callback function (for decorator use)
        """
        with self._lock:
            listener = EventListener(callback, priority, plugin_id, once=False)
            
            if event_name == '*':
                self._wildcard_listeners.append(listener)
                self._wildcard_listeners.sort()
            else:
                self._listeners[event_name].append(listener)
                self._listeners[event_name].sort()
            
            if self.debug_mode:
                logger.debug(f"Registered listener for '{event_name}' from plugin '{plugin_id}'")
        
        return callback
    
    def once(self, event_name: str, callback: Callable,
             priority: EventPriority = EventPriority.NORMAL,
             plugin_id: Optional[str] = None) -> Callable:
        """
        Register a one-time event listener.
        
        Args:
            event_name: Name of the event
            callback: Function to call when event fires
            priority: Listener priority
            plugin_id: ID of plugin registering listener
            
        Returns:
            The callback function
        """
        with self._lock:
            listener = EventListener(callback, priority, plugin_id, once=True)
            self._listeners[event_name].append(listener)
            self._listeners[event_name].sort()
            
            if self.debug_mode:
                logger.debug(f"Registered one-time listener for '{event_name}' from plugin '{plugin_id}'")
        
        return callback
    
    def off(self, event_name: str, callback: Callable):
        """
        Remove an event listener.
        
        Args:
            event_name: Name of the event or '*' for wildcard
            callback: Callback function to remove
        """
        with self._lock:
            if event_name == '*':
                self._wildcard_listeners = [
                    l for l in self._wildcard_listeners 
                    if l.callback != callback
                ]
            else:
                self._listeners[event_name] = [
                    l for l in self._listeners[event_name]
                    if l.callback != callback
                ]
    
    def remove_plugin_listeners(self, plugin_id: str):
        """
        Remove all listeners from a specific plugin.
        
        Args:
            plugin_id: Plugin ID
        """
        with self._lock:
            # Remove from regular listeners
            for event_name in self._listeners:
                self._listeners[event_name] = [
                    l for l in self._listeners[event_name]
                    if l.plugin_id != plugin_id
                ]
            
            # Remove from wildcard listeners
            self._wildcard_listeners = [
                l for l in self._wildcard_listeners
                if l.plugin_id != plugin_id
            ]
            
            if self.debug_mode:
                logger.debug(f"Removed all listeners from plugin '{plugin_id}'")
    
    def emit(self, event_name: str, *args, **kwargs) -> List[Any]:
        """
        Emit an event.
        
        Args:
            event_name: Name of the event
            *args: Positional arguments for callbacks
            **kwargs: Keyword arguments for callbacks
            
        Returns:
            List of return values from callbacks
        """
        # Check for infinite loop
        with self._lock:
            if len(self._event_stack) >= self._max_stack_depth:
                logger.error(f"Event stack depth exceeded for '{event_name}'. Possible infinite loop.")
                logger.error(f"Event stack: {' -> '.join(self._event_stack[-10:])}")
                return []
            
            self._event_stack.append(event_name)
        
        try:
            start_time = time.time()
            results = []
            
            if self.debug_mode:
                logger.debug(f"Emitting event '{event_name}' with args={args}, kwargs={kwargs}")
            
            # Get all listeners (regular + wildcard)
            listeners = []
            
            with self._lock:
                # Add specific event listeners
                if event_name in self._listeners:
                    listeners.extend(self._listeners[event_name][:])
                
                # Add wildcard listeners
                listeners.extend(self._wildcard_listeners[:])
            
            # Sort by priority
            listeners.sort()
            
            # Call each listener
            for listener in listeners:
                try:
                    # Pass event name to wildcard listeners
                    if listener in self._wildcard_listeners:
                        result = listener.callback(event_name, *args, **kwargs)
                    else:
                        result = listener.callback(*args, **kwargs)
                    
                    results.append(result)
                    
                    # Remove one-time listeners
                    if listener.once:
                        with self._lock:
                            if event_name in self._listeners:
                                try:
                                    self._listeners[event_name].remove(listener)
                                except ValueError:
                                    pass
                    
                except Exception as e:
                    logger.error(f"Error in event listener for '{event_name}': {e}")
                    if self.debug_mode:
                        logger.exception(e)
            
            # Track metrics
            elapsed = time.time() - start_time
            with self._lock:
                self._event_metrics[event_name]['count'] += 1
                self._event_metrics[event_name]['total_time'] += elapsed
            
            if self.debug_mode:
                logger.debug(f"Event '{event_name}' completed in {elapsed:.3f}s with {len(results)} listeners")
            
            return results
            
        finally:
            with self._lock:
                self._event_stack.pop()
    
    def emit_async(self, event_name: str, *args, **kwargs):
        """
        Emit an event asynchronously.
        
        Args:
            event_name: Name of the event
            *args: Positional arguments for callbacks
            **kwargs: Keyword arguments for callbacks
        """
        thread = threading.Thread(
            target=self.emit,
            args=(event_name,) + args,
            kwargs=kwargs,
            daemon=True
        )
        thread.start()
    
    def wait_for(self, event_name: str, timeout: Optional[float] = None) -> Optional[Tuple[Any, ...]]:
        """
        Wait for an event to be emitted.
        
        Args:
            event_name: Name of the event to wait for
            timeout: Maximum time to wait in seconds
            
        Returns:
            Event arguments or None if timeout
        """
        event_data = None
        event_received = threading.Event()
        
        def listener(*args, **kwargs):
            nonlocal event_data
            event_data = (args, kwargs)
            event_received.set()
        
        self.once(event_name, listener)
        
        if event_received.wait(timeout):
            return event_data
        else:
            # Remove listener if timeout
            self.off(event_name, listener)
            return None
    
    def get_listeners_count(self, event_name: Optional[str] = None) -> int:
        """
        Get count of registered listeners.
        
        Args:
            event_name: Optional event name to filter by
            
        Returns:
            Number of listeners
        """
        with self._lock:
            if event_name:
                return len(self._listeners.get(event_name, []))
            else:
                total = len(self._wildcard_listeners)
                for listeners in self._listeners.values():
                    total += len(listeners)
                return total
    
    def get_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get event performance metrics.
        
        Returns:
            Dictionary of event metrics
        """
        with self._lock:
            metrics = {}
            for event_name, data in self._event_metrics.items():
                metrics[event_name] = {
                    'count': data['count'],
                    'total_time': data['total_time'],
                    'avg_time': data['total_time'] / data['count'] if data['count'] > 0 else 0
                }
            return metrics
    
    def clear_metrics(self):
        """Clear performance metrics."""
        with self._lock:
            self._event_metrics.clear()
    
    def clear_all(self):
        """Remove all event listeners."""
        with self._lock:
            self._listeners.clear()
            self._wildcard_listeners.clear()
            if self.debug_mode:
                logger.debug("Cleared all event listeners")


# Core event names
class CoreEvents:
    """Standard core event names."""
    
    # Application lifecycle
    APP_READY = 'app.ready'
    APP_SHUTDOWN = 'app.shutdown'
    
    # Search events
    SEARCH_BEFORE = 'search.before'
    SEARCH_COMPLETE = 'search.complete'
    SEARCH_ERROR = 'search.error'
    
    # Plugin events
    PLUGIN_LOADED = 'plugin.loaded'
    PLUGIN_ENABLED = 'plugin.enabled'
    PLUGIN_DISABLED = 'plugin.disabled'
    PLUGIN_UNLOADED = 'plugin.unloaded'
    PLUGIN_ERROR = 'plugin.error'
    
    # Configuration events
    CONFIG_CHANGED = 'config.changed'
    CONFIG_SAVED = 'config.saved'
    
    # Database events
    DATABASE_CONNECTED = 'database.connected'
    DATABASE_DISCONNECTED = 'database.disconnected'
    DATABASE_ERROR = 'database.error'
    
    # User interaction events
    WINDOW_SHOW = 'window.show'
    WINDOW_HIDE = 'window.hide'
    HOTKEY_TRIGGERED = 'hotkey.triggered'
    
    # Extension events
    EXTENSION_INSTALLED = 'extension.installed'
    EXTENSION_UPDATED = 'extension.updated'
    EXTENSION_UNINSTALLED = 'extension.uninstalled'