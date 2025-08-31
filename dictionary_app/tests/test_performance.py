"""
Performance benchmark tests for Dictionary App.
Tests response times, throughput, and scalability.
"""

import time
import statistics
import concurrent.futures
from .base_test import BasePerformanceTest


class TestPerformanceBenchmarks(BasePerformanceTest):
    """Performance benchmark tests."""
    
    def setUp(self):
        """Set up with performance monitoring."""
        super().setUp()
        self.app = self.create_app()
        
        # Allow app to fully initialize
        time.sleep(1.0)
    
    def test_search_response_time(self):
        """Test search response time benchmarks."""
        test_words = ['hello', 'world', 'test', 'example', 'dictionary', 'performance']
        response_times = []
        
        # Warm up
        for word in test_words[:2]:
            self.app.search(word)
        
        # Benchmark searches
        for word in test_words:
            start_time = time.perf_counter()
            results = self.app.search(word)
            end_time = time.perf_counter()
            
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            response_times.append(response_time)
            
            # Verify we got results (if word exists)
            if results:
                self.assertGreater(len(results), 0, f"No results for '{word}'")
        
        # Calculate statistics
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
        
        print(f"\nSearch Response Times:")
        print(f"  Average: {avg_response_time:.1f}ms")
        print(f"  Maximum: {max_response_time:.1f}ms")
        print(f"  95th percentile: {p95_response_time:.1f}ms")
        
        # Assertions
        self.assertLess(avg_response_time, 50.0,
                       f"Average search time {avg_response_time:.1f}ms exceeds 50ms")
        self.assertLess(max_response_time, 200.0,
                       f"Maximum search time {max_response_time:.1f}ms exceeds 200ms")
    
    def test_suggestions_response_time(self):
        """Test autocomplete suggestions response time."""
        test_prefixes = ['hel', 'wor', 'tes', 'exa', 'dic', 'per']
        response_times = []
        
        for prefix in test_prefixes:
            start_time = time.perf_counter()
            suggestions = self.app.get_suggestions(prefix, limit=10)
            end_time = time.perf_counter()
            
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            response_times.append(response_time)
            
            # Verify suggestions format
            self.assertIsInstance(suggestions, list)
            self.assertLessEqual(len(suggestions), 10)
        
        # Calculate statistics
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        
        print(f"\nSuggestions Response Times:")
        print(f"  Average: {avg_response_time:.1f}ms")
        print(f"  Maximum: {max_response_time:.1f}ms")
        
        # Assertions (suggestions should be faster than full search)
        self.assertLess(avg_response_time, 20.0,
                       f"Average suggestions time {avg_response_time:.1f}ms exceeds 20ms")
        self.assertLess(max_response_time, 100.0,
                       f"Maximum suggestions time {max_response_time:.1f}ms exceeds 100ms")
    
    def test_plugin_loading_time(self):
        """Test plugin loading performance."""
        plugin_ids = ['favorites', 'history', 'settings']
        loading_times = []
        
        for plugin_id in plugin_ids:
            if not self.app.get_plugin(plugin_id):
                continue
            
            # Disable plugin first
            self.app.disable_plugin(plugin_id)
            time.sleep(0.1)
            
            # Measure loading time
            start_time = time.perf_counter()
            success = self.app.enable_plugin(plugin_id)
            end_time = time.perf_counter()
            
            if success:
                loading_time = (end_time - start_time) * 1000
                loading_times.append(loading_time)
                print(f"  {plugin_id}: {loading_time:.1f}ms")
            
            time.sleep(0.1)
        
        if loading_times:
            avg_loading_time = statistics.mean(loading_times)
            max_loading_time = max(loading_times)
            
            print(f"\nPlugin Loading Times:")
            print(f"  Average: {avg_loading_time:.1f}ms")
            print(f"  Maximum: {max_loading_time:.1f}ms")
            
            # Assertions
            self.assertLess(avg_loading_time, 500.0,
                           f"Average plugin loading time {avg_loading_time:.1f}ms exceeds 500ms")
            self.assertLess(max_loading_time, 1000.0,
                           f"Maximum plugin loading time {max_loading_time:.1f}ms exceeds 1000ms")
    
    def test_concurrent_searches(self):
        """Test concurrent search performance."""
        test_words = ['hello', 'world', 'test', 'example'] * 5  # 20 searches
        
        def perform_search(word):
            start_time = time.perf_counter()
            results = self.app.search(word)
            end_time = time.perf_counter()
            return end_time - start_time, len(results) if results else 0
        
        # Perform concurrent searches
        start_time = time.perf_counter()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(perform_search, word) for word in test_words]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        total_time = time.perf_counter() - start_time
        
        # Calculate statistics
        search_times = [result[0] * 1000 for result in results]  # Convert to ms
        total_results = sum(result[1] for result in results)
        
        avg_search_time = statistics.mean(search_times)
        throughput = len(test_words) / total_time  # searches per second
        
        print(f"\nConcurrent Search Performance:")
        print(f"  Total searches: {len(test_words)}")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Throughput: {throughput:.1f} searches/sec")
        print(f"  Average search time: {avg_search_time:.1f}ms")
        print(f"  Total results: {total_results}")
        
        # Assertions
        self.assertGreater(throughput, 10.0,
                          f"Concurrent search throughput {throughput:.1f} searches/sec too low")
        self.assertLess(avg_search_time, 100.0,
                       f"Average concurrent search time {avg_search_time:.1f}ms too high")
    
    def test_memory_efficiency(self):
        """Test memory efficiency under load."""
        # Get baseline memory
        baseline_stats = self.monitor.get_stats()
        baseline_memory = baseline_stats['memory']['avg'] if baseline_stats else 0
        
        # Perform many searches to test memory efficiency
        test_words = ['a', 'an', 'and', 'the', 'is', 'was', 'are', 'were'] * 25  # 200 searches
        
        for word in test_words:
            self.app.search(word)
        
        # Wait for cleanup
        time.sleep(2.0)
        
        # Check final memory usage
        final_stats = self.monitor.get_stats()
        final_memory = final_stats['memory']['avg']
        memory_per_search = (final_memory - baseline_memory) / len(test_words)
        
        print(f"\nMemory Efficiency:")
        print(f"  Baseline memory: {baseline_memory:.1f}MB")
        print(f"  Final memory: {final_memory:.1f}MB")
        print(f"  Memory per search: {memory_per_search:.3f}MB")
        print(f"  Total searches: {len(test_words)}")
        
        # Assertions
        self.assertLess(memory_per_search, 0.1,
                       f"Memory per search {memory_per_search:.3f}MB too high")
        self.assertLess(final_stats['memory']['growth'], 50,
                       f"Total memory growth {final_stats['memory']['growth']:.1f}MB too high")
    
    def test_startup_performance(self):
        """Test application startup performance."""
        # This test creates a fresh app instance to measure startup
        if self.app:
            self.app.shutdown()
            self.app = None
        
        # Measure startup time
        start_time = time.perf_counter()
        app = self.create_app()
        end_time = time.perf_counter()
        
        startup_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        print(f"\nStartup Performance:")
        print(f"  Startup time: {startup_time:.1f}ms")
        
        # Verify app is functional
        self.assertTrue(app.running)
        
        # Test basic functionality works
        results = app.search('test')
        self.assertIsInstance(results, list)
        
        # Assertions
        self.assertLess(startup_time, 2000.0,
                       f"Startup time {startup_time:.1f}ms exceeds 2 seconds")
    
    def test_plugin_system_performance(self):
        """Test plugin system performance."""
        plugin_operations = []
        
        available_plugins = ['favorites', 'history', 'settings', 'core-ui']
        
        for plugin_id in available_plugins:
            plugin = self.app.get_plugin(plugin_id)
            if not plugin:
                continue
            
            # Test disable performance
            start_time = time.perf_counter()
            success = self.app.disable_plugin(plugin_id)
            disable_time = (time.perf_counter() - start_time) * 1000
            
            if success:
                plugin_operations.append(('disable', plugin_id, disable_time))
            
            time.sleep(0.1)
            
            # Test enable performance
            start_time = time.perf_counter()
            success = self.app.enable_plugin(plugin_id)
            enable_time = (time.perf_counter() - start_time) * 1000
            
            if success:
                plugin_operations.append(('enable', plugin_id, enable_time))
            
            time.sleep(0.1)
        
        # Calculate statistics
        disable_times = [op[2] for op in plugin_operations if op[0] == 'disable']
        enable_times = [op[2] for op in plugin_operations if op[0] == 'enable']
        
        print(f"\nPlugin System Performance:")
        if disable_times:
            print(f"  Average disable time: {statistics.mean(disable_times):.1f}ms")
            print(f"  Max disable time: {max(disable_times):.1f}ms")
        
        if enable_times:
            print(f"  Average enable time: {statistics.mean(enable_times):.1f}ms")
            print(f"  Max enable time: {max(enable_times):.1f}ms")
        
        # Assertions
        if enable_times:
            self.assertLess(max(enable_times), 1000.0,
                           f"Plugin enable time {max(enable_times):.1f}ms too slow")
        
        if disable_times:
            self.assertLess(max(disable_times), 500.0,
                           f"Plugin disable time {max(disable_times):.1f}ms too slow")


if __name__ == '__main__':
    import unittest
    unittest.main(verbosity=2)