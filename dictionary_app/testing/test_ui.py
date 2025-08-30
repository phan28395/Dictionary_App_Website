#!/usr/bin/env python3
"""
Test script to interact with running Dictionary App
"""

import sys
import time

def test_commands():
    """Test various commands."""
    
    # Give app time to start
    time.sleep(2)
    
    commands = [
        "search book",
        "search go", 
        "search went",
        "search happy",
        "suggest hap",
        "random",
        "wotd",
        "quit"
    ]
    
    for cmd in commands:
        print(cmd)
        time.sleep(1)
        sys.stdout.flush()

if __name__ == "__main__":
    test_commands()