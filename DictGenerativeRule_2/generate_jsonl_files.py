import json
import os
from pathlib import Path

def generate_jsonl_files(lemma_file, output_dir, pos):
    """Generate JSONL files with 50 entries each from a lemma file."""
    
    # Read lemmas from file
    lemmas = []
    with open(lemma_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        # Skip header line
        for line in lines[1:]:
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                lemma = parts[1]
                lemmas.append(lemma)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate JSONL files with 50 entries each
    batch_size = 50
    for i in range(0, len(lemmas), batch_size):
        batch = lemmas[i:i+batch_size]
        start_idx = i + 1  # 1-based indexing
        end_idx = min(i + batch_size, len(lemmas))
        
        # Create filename
        filename = f"lemmas_{pos}_{start_idx}_to_{end_idx}.jsonl"
        filepath = os.path.join(output_dir, filename)
        
        # Write JSONL file
        with open(filepath, 'w', encoding='utf-8') as f:
            for lemma in batch:
                entry = {
                    "lemma": lemma,
                    "meanings": [],
                    "definitions": [],
                    "examples": [],
                    "frequency_meaning": [],
                    "domains": [],
                    "semantic_function": [],
                    "key_collocates": []
                }
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        
        print(f"Created: {filename}")

def main():
    base_dir = "/mnt/storage/Documents/Dictionary_Generator/DictGenerativeRule_2"
    
    # Process each POS
    pos_configs = [
        ("Noun", "lemmas_Noun.txt", "Noun_Generator/Noun_Json"),
        ("Adjective", "lemmas_Adjective.txt", "Adjective_Generator/Adjective_Json"),
        ("Verb", "lemmas_Verb.txt", "Verb_Generator/Verb_Json")
    ]
    
    for pos_name, lemma_file, output_dir in pos_configs:
        print(f"\nProcessing {pos_name} lemmas...")
        lemma_path = os.path.join(base_dir, lemma_file)
        output_path = os.path.join(base_dir, output_dir)
        generate_jsonl_files(lemma_path, output_path, pos_name)
        print(f"Completed {pos_name} lemmas")

if __name__ == "__main__":
    main()