#!/usr/bin/env python3
"""
Real-time resource monitoring tool for Dictionary App.
Provides live visualization of CPU, memory, and thread usage.
"""

import sys
import time
import psutil
import threading
import argparse
from pathlib import Path
from collections import deque
from typing import Dict, List, Optional
import subprocess
import signal

# Add parent to path for core imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Only console output will be shown.")


class ResourceMonitor:
    """Real-time resource monitor with graphical display."""
    
    def __init__(self, pid: Optional[int] = None, history_size: int = 100):
        self.pid = pid
        self.process = None
        self.history_size = history_size
        
        # Data storage
        self.timestamps = deque(maxlen=history_size)
        self.cpu_data = deque(maxlen=history_size)
        self.memory_data = deque(maxlen=history_size)
        self.thread_data = deque(maxlen=history_size)
        
        # Monitoring state
        self.monitoring = False
        self.monitor_thread = None
        
        # Statistics
        self.stats = {
            'cpu': {'min': float('inf'), 'max': 0, 'avg': 0, 'current': 0},
            'memory': {'min': float('inf'), 'max': 0, 'avg': 0, 'current': 0},
            'threads': {'min': float('inf'), 'max': 0, 'avg': 0, 'current': 0},
            'uptime': 0
        }
        
        self.start_time = time.time()
        
        # Setup process monitoring
        if self.pid:
            try:
                self.process = psutil.Process(self.pid)
                print(f"Monitoring process {self.pid}: {self.process.name()}")
            except psutil.NoSuchProcess:
                print(f"Process {self.pid} not found")
                self.process = None
    
    def find_dictionary_process(self) -> Optional[int]:
        """Find running dictionary app process."""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline and any('run_app.py' in arg or 'dictionary' in arg.lower() for arg in cmdline):
                    return proc.info['pid']
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None
    
    def start_monitoring(self, interval: float = 0.5):
        """Start resource monitoring."""
        if not self.process and not self.pid:
            # Try to find dictionary process
            found_pid = self.find_dictionary_process()
            if found_pid:
                self.pid = found_pid
                self.process = psutil.Process(self.pid)
                print(f"Found dictionary process: {self.pid}")
            else:
                print("No dictionary process found. Monitoring current process.")
                self.pid = psutil.Process().pid
                self.process = psutil.Process(self.pid)
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop, 
            args=(interval,), 
            daemon=True
        )
        self.monitor_thread.start()
        print(f"Started monitoring process {self.pid} every {interval}s")
    
    def stop_monitoring(self):
        """Stop resource monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        print("Stopped monitoring")
    
    def _monitor_loop(self, interval: float):
        """Monitor resources in background thread."""
        while self.monitoring:
            try:
                if not self.process or not self.process.is_running():
                    break
                
                # Get current time
                current_time = time.time() - self.start_time
                
                # Get CPU usage
                cpu_percent = self.process.cpu_percent()
                
                # Get memory info (in MB)
                memory_info = self.process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                
                # Get thread count
                thread_count = self.process.num_threads()
                
                # Store data
                self.timestamps.append(current_time)
                self.cpu_data.append(cpu_percent)
                self.memory_data.append(memory_mb)
                self.thread_data.append(thread_count)
                
                # Update statistics
                self._update_stats(cpu_percent, memory_mb, thread_count, current_time)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                print("Process no longer accessible")
                break
            except Exception as e:
                print(f"Error monitoring process: {e}")
            
            time.sleep(interval)
    
    def _update_stats(self, cpu: float, memory: float, threads: int, uptime: float):
        """Update running statistics."""
        # CPU stats
        self.stats['cpu']['current'] = cpu
        self.stats['cpu']['min'] = min(self.stats['cpu']['min'], cpu)
        self.stats['cpu']['max'] = max(self.stats['cpu']['max'], cpu)
        if len(self.cpu_data) > 0:
            self.stats['cpu']['avg'] = sum(self.cpu_data) / len(self.cpu_data)
        
        # Memory stats
        self.stats['memory']['current'] = memory
        self.stats['memory']['min'] = min(self.stats['memory']['min'], memory)
        self.stats['memory']['max'] = max(self.stats['memory']['max'], memory)
        if len(self.memory_data) > 0:
            self.stats['memory']['avg'] = sum(self.memory_data) / len(self.memory_data)
        
        # Thread stats
        self.stats['threads']['current'] = threads
        self.stats['threads']['min'] = min(self.stats['threads']['min'], threads)
        self.stats['threads']['max'] = max(self.stats['threads']['max'], threads)
        if len(self.thread_data) > 0:
            self.stats['threads']['avg'] = sum(self.thread_data) / len(self.thread_data)
        
        # Uptime
        self.stats['uptime'] = uptime
    
    def print_stats(self):
        """Print current statistics to console."""
        if not self.timestamps:
            print("No data collected yet...")
            return
        
        print(f"\n{'='*60}")
        print(f"Process {self.pid} - Uptime: {self.stats['uptime']:.1f}s")
        print(f"{'='*60}")
        
        # CPU stats
        cpu = self.stats['cpu']
        print(f"CPU Usage:     {cpu['current']:6.1f}% (min: {cpu['min']:4.1f}%, max: {cpu['max']:4.1f}%, avg: {cpu['avg']:4.1f}%)")
        
        # Memory stats
        mem = self.stats['memory']
        print(f"Memory Usage:  {mem['current']:6.1f}MB (min: {mem['min']:4.1f}MB, max: {mem['max']:4.1f}MB, avg: {mem['avg']:4.1f}MB)")
        
        # Thread stats
        thr = self.stats['threads']
        print(f"Thread Count:  {thr['current']:6.0f}   (min: {thr['min']:4.0f}, max: {thr['max']:4.0f}, avg: {thr['avg']:4.1f})")
        
        print(f"Data Points:   {len(self.timestamps)}")
        
        # Performance warnings
        warnings = []
        if cpu['current'] > 10.0:
            warnings.append(f"HIGH CPU USAGE: {cpu['current']:.1f}%")
        if mem['max'] - mem['min'] > 50:
            warnings.append(f"MEMORY GROWTH: {mem['max'] - mem['min']:.1f}MB")
        if thr['current'] > 20:
            warnings.append(f"HIGH THREAD COUNT: {thr['current']}")
        
        if warnings:
            print(f"\n⚠️  WARNINGS:")
            for warning in warnings:
                print(f"   {warning}")
        
        print()
    
    def create_graph(self):
        """Create real-time graphs (requires matplotlib)."""
        if not MATPLOTLIB_AVAILABLE:
            print("Matplotlib not available for graphing")
            return
        
        # Set up the figure and subplots
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
        fig.suptitle(f'Dictionary App Resource Monitor (PID: {self.pid})', fontsize=16)
        
        # Initialize empty lines
        line1, = ax1.plot([], [], 'b-', linewidth=2)
        line2, = ax2.plot([], [], 'r-', linewidth=2)
        line3, = ax3.plot([], [], 'g-', linewidth=2)
        
        # Configure axes
        ax1.set_title('CPU Usage (%)')
        ax1.set_ylabel('CPU %')
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 100)
        
        ax2.set_title('Memory Usage (MB)')
        ax2.set_ylabel('Memory MB')
        ax2.grid(True, alpha=0.3)
        
        ax3.set_title('Thread Count')
        ax3.set_xlabel('Time (seconds)')
        ax3.set_ylabel('Threads')
        ax3.grid(True, alpha=0.3)
        
        def animate(frame):
            """Animation function for real-time updates."""
            if not self.timestamps:
                return line1, line2, line3
            
            # Get current data
            times = list(self.timestamps)
            cpu_vals = list(self.cpu_data)
            memory_vals = list(self.memory_data)
            thread_vals = list(self.thread_data)
            
            # Update lines
            line1.set_data(times, cpu_vals)
            line2.set_data(times, memory_vals)
            line3.set_data(times, thread_vals)
            
            # Update axis limits
            if times:
                time_range = max(30, max(times) - min(times))  # At least 30s range
                ax1.set_xlim(max(times) - time_range, max(times) + 1)
                ax2.set_xlim(max(times) - time_range, max(times) + 1)
                ax3.set_xlim(max(times) - time_range, max(times) + 1)
                
                # Auto-scale y-axes
                if memory_vals:
                    mem_min, mem_max = min(memory_vals), max(memory_vals)
                    mem_range = max(10, mem_max - mem_min)
                    ax2.set_ylim(mem_min - mem_range * 0.1, mem_max + mem_range * 0.1)
                
                if thread_vals:
                    thread_min, thread_max = min(thread_vals), max(thread_vals)
                    thread_range = max(5, thread_max - thread_min)
                    ax3.set_ylim(thread_min - 1, thread_max + 2)
            
            return line1, line2, line3
        
        # Create animation
        ani = animation.FuncAnimation(
            fig, animate, interval=500, blit=True, cache_frame_data=False
        )
        
        plt.tight_layout()
        plt.show()


def launch_dictionary_app():
    """Launch the dictionary app for monitoring."""
    app_path = Path(__file__).parent.parent / "run_app.py"
    if app_path.exists():
        print(f"Launching dictionary app: {app_path}")
        try:
            proc = subprocess.Popen(
                [sys.executable, str(app_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            time.sleep(2)  # Give app time to start
            return proc.pid
        except Exception as e:
            print(f"Failed to launch app: {e}")
            return None
    else:
        print(f"Dictionary app not found at {app_path}")
        return None


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Monitor Dictionary App resource usage')
    parser.add_argument('--pid', type=int, help='Process ID to monitor')
    parser.add_argument('--launch', action='store_true', help='Launch dictionary app automatically')
    parser.add_argument('--interval', type=float, default=0.5, help='Monitoring interval in seconds')
    parser.add_argument('--console-only', action='store_true', help='Console output only (no graphs)')
    parser.add_argument('--duration', type=int, help='Monitor for specified seconds then exit')
    
    args = parser.parse_args()
    
    pid = args.pid
    
    # Auto-launch app if requested
    if args.launch:
        pid = launch_dictionary_app()
        if not pid:
            print("Failed to launch dictionary app")
            sys.exit(1)
    
    # Create monitor
    monitor = ResourceMonitor(pid=pid)
    
    # Start monitoring
    monitor.start_monitoring(interval=args.interval)
    
    # Setup signal handler for clean shutdown
    def signal_handler(signum, frame):
        print("\nShutting down monitor...")
        monitor.stop_monitoring()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        if args.console_only or not MATPLOTLIB_AVAILABLE:
            # Console-only monitoring
            start_time = time.time()
            
            while monitor.monitoring:
                time.sleep(2.0)  # Update every 2 seconds
                
                # Clear screen (works on most terminals)
                print(chr(27) + "[2J" + chr(27) + "[H", end="")
                
                monitor.print_stats()
                
                # Check duration limit
                if args.duration and (time.time() - start_time) >= args.duration:
                    break
            
        else:
            # Start graphical monitoring
            print("Starting graphical monitor...")
            print("Close the graph window or press Ctrl+C to stop")
            monitor.create_graph()
    
    except KeyboardInterrupt:
        pass
    
    finally:
        monitor.stop_monitoring()
        print("Monitor stopped")


if __name__ == '__main__':
    main()