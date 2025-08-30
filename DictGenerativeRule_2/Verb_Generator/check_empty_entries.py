#!/usr/bin/env python3
import json
import os
import glob

def check_empty_entries(filepath):
    """Check if a JSONL file has empty entries."""
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
            if not lines:
                return None, 0, 0  # File is completely empty
            
            empty_count = 0
            total_count = 0
            
            for line in lines:
                if line.strip():
                    total_count += 1
                    entry = json.loads(line.strip())
                    # Check if any of the main arrays are empty
                    if (not entry.get('meanings', []) or 
                        not entry.get('definitions', []) or
                        not entry.get('examples', [])):
                        empty_count += 1
            
            return filepath, empty_count, total_count
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return filepath, -1, -1

# Get all JSONL files
pattern = "/home/miso/Documents/Dictionary_App_Website/Dictionary_App_Website/DictGenerativeRule_2/Verb_Generator/Verb_Json/*.jsonl"
files = sorted(glob.glob(pattern))

print(f"Checking {len(files)} files for empty entries...\n")
print(f"{'File':<50} {'Empty':<10} {'Total':<10} {'Status'}")
print("-" * 80)

files_with_empty = []

for filepath in files:
    filename = os.path.basename(filepath)
    _, empty, total = check_empty_entries(filepath)
    
    if empty == -1:
        status = "ERROR"
    elif empty == 0:
        status = "✓ Complete"
    else:
        status = f"⚠ {empty} empty"
        files_with_empty.append((filepath, empty, total))
    
    print(f"{filename:<50} {empty:<10} {total:<10} {status}")

print("\n" + "="*80)
if files_with_empty:
    print(f"\nFiles needing entries ({len(files_with_empty)}):")
    for filepath, empty, total in files_with_empty:
        print(f"  - {os.path.basename(filepath)}: {empty}/{total} entries are empty")
else:
    print("\n✅ All files have complete entries!")