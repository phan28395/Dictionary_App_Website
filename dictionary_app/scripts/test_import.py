#!/usr/bin/env python3
"""
Test Import - Small Sample

Tests the bulk import system with just a few files to ensure it works.
"""

import sys
import json
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bulk_import import BulkImporter

def main():
    """Test import with limited files"""
    print("=" * 50)
    print("TESTING BULK IMPORT SYSTEM")
    print("=" * 50)
    
    # Create test importer  
    importer = BulkImporter()
    importer.batch_size = 100  # Smaller batches for testing
    
    try:
        # Initialize
        importer.initialize()
        
        # Test with just first few files of each POS type
        pos_types = ['adjective', 'noun', 'verb', 'adverb']
        
        for pos_type in pos_types:
            files = importer.get_pos_files(pos_type)
            if files:
                # Process only first 2 files for testing
                test_files = files[:2]
                print(f"\n🧪 Testing {pos_type} import with {len(test_files)} files...")
                
                for file_path in test_files:
                    importer.process_file(file_path, pos_type)
                    
                # Flush remaining batch
                if importer.batch_buffer:
                    importer.flush_batch()
                    
                print(f"✅ {pos_type} test completed")
            else:
                print(f"⚠️ No {pos_type} files found")
        
        # Print stats
        importer.print_final_stats()
        
        # Quick verification
        print("\n🔍 QUICK VERIFICATION:")
        total = importer.app.database.execute_one("SELECT COUNT(*) FROM dictionary_entries")[0]
        print(f"Total entries imported: {total:,}")
        
        # Test search
        test_words = ['good', 'bad', 'happy']
        for word in test_words:
            results = importer.app.search(word)
            if results:
                r = results[0]
                print(f"✅ Search '{word}' → {r.lemma} ({r.pos})")
            else:
                print(f"❌ '{word}' not found")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        importer.shutdown()
        
    print("\n🎉 BULK IMPORT TEST COMPLETED!")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)