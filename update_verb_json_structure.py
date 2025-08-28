import json
import os
from pathlib import Path

def update_json_structure(file_path):
    """Update the JSON structure in a JSONL file to the new format."""
    
    updated_lines = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                
                # Remove old fields
                if 'domains' in data:
                    del data['domains']
                if 'semantic_function' in data:
                    del data['semantic_function']
                
                # Add new fields if they don't exist
                num_meanings = len(data.get('meanings', []))
                
                if 'grammatical_patterns' not in data:
                    # Create empty arrays of arrays matching the number of meanings
                    data['grammatical_patterns'] = [[] for _ in range(num_meanings)] if num_meanings > 0 else []
                
                if 'semantic_roles' not in data:
                    # Create empty array matching the number of meanings
                    data['semantic_roles'] = [''] * num_meanings if num_meanings > 0 else []
                
                if 'aspect_type' not in data:
                    # Create empty array matching the number of meanings
                    data['aspect_type'] = [''] * num_meanings if num_meanings > 0 else []
                
                # Ensure the order of fields matches the desired structure
                ordered_data = {
                    'lemma': data.get('lemma', ''),
                    'meanings': data.get('meanings', []),
                    'definitions': data.get('definitions', []),
                    'examples': data.get('examples', []),
                    'frequency_meaning': data.get('frequency_meaning', []),
                    'grammatical_patterns': data.get('grammatical_patterns', []),
                    'semantic_roles': data.get('semantic_roles', []),
                    'aspect_type': data.get('aspect_type', []),
                    'key_collocates': data.get('key_collocates', [])
                }
                
                updated_lines.append(json.dumps(ordered_data, ensure_ascii=False))
    
    # Write back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        for line in updated_lines:
            f.write(line + '\n')
    
    return len(updated_lines)

def main():
    # Path to the Verb_Json directory
    verb_json_dir = Path(r'E:\CompanyBuilding\DictionaryContent2\Dictionary_Content_2\DictGenerativeRule_2\Verb_Generator\Verb_Json')
    
    if not verb_json_dir.exists():
        print(f"Error: Directory {verb_json_dir} does not exist!")
        return
    
    # Get all JSONL files in the directory
    jsonl_files = list(verb_json_dir.glob('*.jsonl'))
    
    print(f"Found {len(jsonl_files)} JSONL files to update")
    print("=" * 50)
    
    total_entries = 0
    
    for file_path in sorted(jsonl_files):
        print(f"Updating: {file_path.name}")
        try:
            entries = update_json_structure(file_path)
            total_entries += entries
            print(f"  [OK] Updated {entries} entries")
        except Exception as e:
            print(f"  [ERROR] {e}")
    
    print("=" * 50)
    print(f"Update complete! Total entries updated: {total_entries}")

if __name__ == "__main__":
    main()