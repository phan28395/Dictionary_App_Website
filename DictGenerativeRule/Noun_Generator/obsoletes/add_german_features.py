import json
import os
import glob

def add_german_features_to_json(file_path):
    """Add German language features to a JSON file."""
    
    modified = False
    output_lines = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    output_lines.append(line)
                    continue
                
                try:
                    data = json.loads(line)
                    
                    # Check if German features already exist
                    if 'meanings_de' in data and 'examples_de' in data and 'definitions_de' in data:
                        output_lines.append(line)
                        continue
                    
                    # Add German features with empty arrays matching the structure
                    num_meanings = len(data.get('meanings', []))
                    
                    if 'meanings_de' not in data:
                        data['meanings_de'] = [""] * num_meanings
                        modified = True
                    
                    if 'definitions_de' not in data:
                        data['definitions_de'] = [""] * num_meanings
                        modified = True
                    
                    if 'examples_de' not in data:
                        # Match the nested structure of examples
                        examples_structure = data.get('examples', [])
                        data['examples_de'] = []
                        for example_pair in examples_structure:
                            if isinstance(example_pair, list):
                                data['examples_de'].append([""] * len(example_pair))
                            else:
                                data['examples_de'].append(["", ""])
                        modified = True
                    
                    # Convert back to JSON and add to output
                    output_lines.append(json.dumps(data, ensure_ascii=False))
                    
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON in {file_path}: {e}")
                    output_lines.append(line)
        
        # Write back to file if modifications were made
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                for line in output_lines:
                    f.write(line + '\n')
            print(f"✓ Updated: {file_path}")
        else:
            print(f"- Skipped (already has German features): {file_path}")
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def process_all_json_files():
    """Process all JSON files in the Nouns_Json directory and subdirectories."""
    
    base_dir = "Nouns_Json"
    
    if not os.path.exists(base_dir):
        print(f"Error: {base_dir} directory not found!")
        return
    
    # Find all JSON files recursively
    json_files = glob.glob(os.path.join(base_dir, "**", "*.json"), recursive=True)
    
    if not json_files:
        print(f"No JSON files found in {base_dir}")
        return
    
    print(f"Found {len(json_files)} JSON files to process...")
    print("-" * 50)
    
    updated_count = 0
    
    for json_file in sorted(json_files):
        # Skip any backup files
        if 'backup' in json_file.lower():
            continue
            
        add_german_features_to_json(json_file)
        updated_count += 1
    
    print("-" * 50)
    print(f"Processing complete! Processed {updated_count} files.")

if __name__ == "__main__":
    print("Adding German features to all JSON files...")
    print("Features to add: meanings_de, examples_de, definitions_de")
    print("=" * 50)
    
    process_all_json_files()