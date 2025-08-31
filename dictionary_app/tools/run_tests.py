#!/usr/bin/env python3
"""
Test runner for Dictionary App performance tests.
"""

import sys
import unittest
import argparse
from pathlib import Path
import time

# Add parent to path for test imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_resource_tests():
    """Run resource usage tests."""
    print("Running Resource Usage Tests...")
    print("=" * 50)
    
    from tests.test_resource_usage import TestResourceUsage
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestResourceUsage)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_performance_tests():
    """Run performance benchmark tests."""
    print("\nRunning Performance Benchmark Tests...")
    print("=" * 50)
    
    from tests.test_performance import TestPerformanceBenchmarks
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPerformanceBenchmarks)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_all_tests():
    """Run all performance tests."""
    print("Dictionary App Performance Test Suite")
    print("=" * 60)
    print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    success = True
    
    # Run resource tests
    if not run_resource_tests():
        success = False
    
    # Run performance tests
    if not run_performance_tests():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED")
        print("Performance requirements met!")
    else:
        print("❌ SOME TESTS FAILED")
        print("Performance issues detected!")
    
    print(f"Completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    return success

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Run Dictionary App performance tests')
    parser.add_argument('--resource', action='store_true', help='Run only resource usage tests')
    parser.add_argument('--performance', action='store_true', help='Run only performance benchmark tests')
    parser.add_argument('--test', help='Run specific test method')
    
    args = parser.parse_args()
    
    try:
        if args.resource:
            success = run_resource_tests()
        elif args.performance:
            success = run_performance_tests()
        elif args.test:
            # Run specific test
            suite = unittest.TestLoader().loadTestsFromName(args.test)
            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(suite)
            success = result.wasSuccessful()
        else:
            success = run_all_tests()
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(3)

if __name__ == '__main__':
    main()