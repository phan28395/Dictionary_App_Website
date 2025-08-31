"""
Base test class with resource monitoring capabilities.
"""

import time
import psutil
import threading
import unittest
from pathlib import Path
from typing import Dict, List, Optional
import sys
import os

# Add parent to path for core imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import DictionaryApp


class ResourceMonitor:
    """Monitor system resource usage during tests."""
    
    def __init__(self, pid: Optional[int] = None):
        self.pid = pid or os.getpid()
        self.process = psutil.Process(self.pid)
        self.monitoring = False
        self.monitor_thread = None
        
        # Metrics storage
        self.cpu_samples = []
        self.memory_samples = []
        self.thread_count_samples = []
        self.timestamps = []
        
        # Performance thresholds
        self.max_idle_cpu = 5.0  # Max 5% CPU when idle
        self.max_memory_growth = 50 * 1024 * 1024  # Max 50MB memory growth
        self.max_threads = 20  # Max 20 threads
    
    def start_monitoring(self, interval: float = 0.1):
        """Start resource monitoring."""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,), daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop resource monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
    
    def _monitor_loop(self, interval: float):
        """Monitor resources in background thread."""
        while self.monitoring:
            try:
                # Get CPU usage (averaged over interval)
                cpu_percent = self.process.cpu_percent()
                
                # Get memory info
                memory_info = self.process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                
                # Get thread count
                thread_count = self.process.num_threads()
                
                # Store samples
                self.cpu_samples.append(cpu_percent)
                self.memory_samples.append(memory_mb)
                self.thread_count_samples.append(thread_count)
                self.timestamps.append(time.time())
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break
            
            time.sleep(interval)
    
    def get_stats(self) -> Dict:
        """Get statistics from monitoring session."""
        if not self.cpu_samples:
            return {}
        
        return {
            'cpu': {
                'min': min(self.cpu_samples),
                'max': max(self.cpu_samples),
                'avg': sum(self.cpu_samples) / len(self.cpu_samples),
                'samples': len(self.cpu_samples)
            },
            'memory': {
                'min': min(self.memory_samples),
                'max': max(self.memory_samples),
                'avg': sum(self.memory_samples) / len(self.memory_samples),
                'growth': max(self.memory_samples) - min(self.memory_samples) if self.memory_samples else 0,
                'samples': len(self.memory_samples)
            },
            'threads': {
                'min': min(self.thread_count_samples),
                'max': max(self.thread_count_samples),
                'avg': sum(self.thread_count_samples) / len(self.thread_count_samples),
                'samples': len(self.thread_count_samples)
            },
            'duration': self.timestamps[-1] - self.timestamps[0] if len(self.timestamps) > 1 else 0
        }
    
    def assert_performance(self, test_case: unittest.TestCase, idle_period: float = 2.0):
        """Assert performance meets requirements."""
        stats = self.get_stats()
        
        if not stats:
            test_case.fail("No performance data collected")
        
        # Check idle CPU usage
        if len(self.timestamps) > 1:
            idle_start_time = self.timestamps[-1] - idle_period
            idle_cpu_samples = [
                cpu for cpu, timestamp in zip(self.cpu_samples, self.timestamps)
                if timestamp >= idle_start_time
            ]
            
            if idle_cpu_samples:
                avg_idle_cpu = sum(idle_cpu_samples) / len(idle_cpu_samples)
                test_case.assertLess(
                    avg_idle_cpu, 
                    self.max_idle_cpu,
                    f"Idle CPU usage {avg_idle_cpu:.1f}% exceeds threshold {self.max_idle_cpu}%"
                )
        
        # Check memory growth
        test_case.assertLess(
            stats['memory']['growth'],
            self.max_memory_growth / 1024 / 1024,  # Convert to MB
            f"Memory growth {stats['memory']['growth']:.1f}MB exceeds threshold {self.max_memory_growth/1024/1024}MB"
        )
        
        # Check thread count
        test_case.assertLess(
            stats['threads']['max'],
            self.max_threads,
            f"Thread count {stats['threads']['max']} exceeds threshold {self.max_threads}"
        )


class BasePerformanceTest(unittest.TestCase):
    """Base class for performance tests."""
    
    def setUp(self):
        """Set up test environment."""
        self.app = None
        self.monitor = ResourceMonitor()
        
        # Start monitoring before test
        self.monitor.start_monitoring()
        
        # Allow baseline measurements
        time.sleep(0.5)
    
    def tearDown(self):
        """Clean up test environment."""
        # Stop monitoring
        self.monitor.stop_monitoring()
        
        # Shutdown app if created
        if self.app and self.app.running:
            self.app.shutdown()
        
        # Print performance stats
        stats = self.monitor.get_stats()
        if stats:
            print(f"\nPerformance Stats for {self._testMethodName}:")
            print(f"  CPU: avg={stats['cpu']['avg']:.1f}% max={stats['cpu']['max']:.1f}%")
            print(f"  Memory: avg={stats['memory']['avg']:.1f}MB growth={stats['memory']['growth']:.1f}MB")
            print(f"  Threads: avg={stats['threads']['avg']:.1f} max={stats['threads']['max']}")
            print(f"  Duration: {stats['duration']:.1f}s")
    
    def create_app(self, **kwargs) -> DictionaryApp:
        """Create and initialize app instance."""
        self.app = DictionaryApp(**kwargs)
        
        # Initialize app
        if not self.app.initialize():
            self.fail("Failed to initialize app")
        
        return self.app
    
    def wait_for_idle(self, duration: float = 2.0):
        """Wait for app to become idle."""
        time.sleep(duration)
    
    def assert_performance(self, idle_period: float = 2.0):
        """Assert performance requirements are met."""
        self.monitor.assert_performance(self, idle_period)


if __name__ == '__main__':
    # Simple test to verify monitoring works
    monitor = ResourceMonitor()
    monitor.start_monitoring()
    
    print("Monitoring for 5 seconds...")
    time.sleep(5)
    
    monitor.stop_monitoring()
    stats = monitor.get_stats()
    
    print(f"Stats: {stats}")