"""
Resource usage tests for Dictionary App.
Tests CPU, memory, and thread usage under various conditions.
"""

import time
import threading
import unittest
from .base_test import BasePerformanceTest


class TestResourceUsage(BasePerformanceTest):
    """Test resource usage patterns."""
    
    def test_headless_startup_idle(self):
        """Test resource usage for headless startup and idle state."""
        # Create headless app (no UI)
        app = self.create_app()
        
        # Disable UI plugin to test headless mode
        if app.get_plugin('core-ui'):
            app.disable_plugin('core-ui')
        
        # Wait for app to become idle
        self.wait_for_idle(3.0)
        
        # Assert performance requirements
        self.assert_performance(idle_period=2.0)
        
        # Check that app is running
        self.assertTrue(app.running)
    
    def test_ui_plugin_startup_idle(self):
        """Test resource usage with UI plugin enabled."""
        # Create app with UI
        app = self.create_app()
        
        # Ensure UI plugin is enabled
        ui_plugin = app.get_plugin('core-ui')
        if ui_plugin and not ui_plugin.enabled:
            app.enable_plugin('core-ui')
        
        # Wait for startup to complete
        time.sleep(2.0)
        
        # Wait for idle state
        self.wait_for_idle(3.0)
        
        # Assert performance requirements
        self.assert_performance(idle_period=2.0)
    
    def test_plugin_loading_unloading(self):
        """Test resource usage during plugin loading/unloading."""
        app = self.create_app()
        
        # Get list of available plugins
        available_plugins = ['core-ui', 'settings', 'favorites', 'history']
        
        # Test loading and unloading plugins
        for plugin_id in available_plugins:
            if app.get_plugin(plugin_id):
                # Disable plugin
                app.disable_plugin(plugin_id)
                time.sleep(0.5)
                
                # Re-enable plugin
                app.enable_plugin(plugin_id)
                time.sleep(0.5)
        
        # Wait for idle
        self.wait_for_idle(2.0)
        
        # Check performance
        self.assert_performance(idle_period=1.0)
    
    def test_search_operations(self):
        """Test resource usage during search operations."""
        app = self.create_app()
        
        # Perform multiple searches
        test_words = ['hello', 'world', 'test', 'example', 'dictionary']
        
        for word in test_words:
            results = app.search(word)
            time.sleep(0.1)  # Small delay between searches
        
        # Wait for idle
        self.wait_for_idle(2.0)
        
        # Check performance
        self.assert_performance(idle_period=1.0)
    
    def test_rapid_searches(self):
        """Test resource usage under rapid search load."""
        app = self.create_app()
        
        # Perform rapid searches
        words = ['a', 'an', 'and', 'the', 'is', 'was', 'are', 'were'] * 10
        
        start_time = time.time()
        for word in words:
            app.search(word)
            if time.time() - start_time > 5.0:  # Limit test duration
                break
        
        # Wait for idle
        self.wait_for_idle(2.0)
        
        # Check performance (more lenient for stress test)
        stats = self.monitor.get_stats()
        
        # Custom assertions for stress test
        self.assertLess(stats['memory']['growth'], 100, 
                       f"Memory growth {stats['memory']['growth']:.1f}MB too high for stress test")
        
        self.assertLess(stats['threads']['max'], 25,
                       f"Thread count {stats['threads']['max']} too high for stress test")
    
    def test_memory_stability(self):
        """Test memory usage stability over time."""
        app = self.create_app()
        
        # Run for longer period with periodic activity
        test_duration = 10.0
        start_time = time.time()
        
        search_count = 0
        while time.time() - start_time < test_duration:
            # Periodic search activity
            if search_count % 10 == 0:
                app.search(f"test{search_count}")
            
            search_count += 1
            time.sleep(0.1)
        
        # Wait for final idle
        self.wait_for_idle(2.0)
        
        # Check for memory leaks
        stats = self.monitor.get_stats()
        
        # Memory growth should be minimal over time
        self.assertLess(stats['memory']['growth'], 20,
                       f"Potential memory leak: {stats['memory']['growth']:.1f}MB growth")
    
    def test_thread_count_stability(self):
        """Test that thread count remains stable."""
        app = self.create_app()
        
        # Record initial thread count
        initial_stats = self.monitor.get_stats()
        initial_threads = initial_stats['threads']['max'] if initial_stats else 0
        
        # Perform various operations
        operations = [
            lambda: app.search('test'),
            lambda: app.get_suggestions('hel', 5),
            lambda: app.enable_plugin('favorites'),
            lambda: app.disable_plugin('favorites'),
            lambda: app.enable_plugin('favorites'),
        ]
        
        # Execute operations multiple times
        for _ in range(5):
            for op in operations:
                try:
                    op()
                    time.sleep(0.1)
                except:
                    pass  # Some operations might fail, that's ok
        
        # Wait for idle
        self.wait_for_idle(2.0)
        
        # Check thread count didn't grow significantly
        final_stats = self.monitor.get_stats()
        final_threads = final_stats['threads']['max']
        
        thread_growth = final_threads - initial_threads
        self.assertLess(thread_growth, 5,
                       f"Thread count grew by {thread_growth} (from {initial_threads} to {final_threads})")


class TestUIResourceUsage(BasePerformanceTest):
    """Test UI-specific resource usage."""
    
    def setUp(self):
        """Set up with longer monitoring for UI tests."""
        super().setUp()
        # UI tests need longer baseline
        time.sleep(1.0)
    
    def test_ui_queue_polling(self):
        """Test UI queue polling efficiency."""
        app = self.create_app()
        
        ui_plugin = app.get_plugin('core-ui')
        if not ui_plugin or not ui_plugin.enabled:
            self.skipTest("UI plugin not available")
        
        # Wait for UI to initialize
        time.sleep(2.0)
        
        # Test idle polling
        self.wait_for_idle(5.0)
        
        # Check that polling doesn't consume excessive CPU
        stats = self.monitor.get_stats()
        
        # Get CPU usage in the last 3 seconds (idle period)
        idle_start_time = stats.get('duration', 0) - 3.0
        if len(self.monitor.timestamps) > 1:
            idle_cpu_samples = [
                cpu for cpu, timestamp in zip(self.monitor.cpu_samples, self.monitor.timestamps)
                if (self.monitor.timestamps[-1] - timestamp) <= 3.0
            ]
            
            if idle_cpu_samples:
                avg_idle_cpu = sum(idle_cpu_samples) / len(idle_cpu_samples)
                self.assertLess(avg_idle_cpu, 3.0,
                               f"UI polling using {avg_idle_cpu:.1f}% CPU when idle")
    
    def test_ui_operations_queuing(self):
        """Test UI operation queuing performance."""
        app = self.create_app()
        
        ui_plugin = app.get_plugin('core-ui')
        if not ui_plugin or not ui_plugin.enabled:
            self.skipTest("UI plugin not available")
        
        # Queue multiple UI operations rapidly
        for i in range(50):
            ui_plugin._queue_ui_operation(lambda i=i: print(f"UI operation {i}"))
            time.sleep(0.01)
        
        # Wait for operations to process
        time.sleep(2.0)
        
        # Wait for idle
        self.wait_for_idle(2.0)
        
        # Check performance
        self.assert_performance(idle_period=1.0)


if __name__ == '__main__':
    unittest.main(verbosity=2)