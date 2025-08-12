import os
from pathlib import Path

def generate_progress_checklist(json_dir, output_file, pos_name):
    """Generate a progress checklist markdown file for tracking JSONL file completion."""
    
    # Get all JSONL files in the directory
    json_files = [f for f in os.listdir(json_dir) if f.endswith('.jsonl')]
    
    # Sort files numerically by extracting the start number
    def get_start_number(filename):
        parts = filename.replace('.jsonl', '').split('_')
        if len(parts) >= 3:
            try:
                return int(parts[2])
            except ValueError:
                return 0
        return 0
    
    json_files = sorted(json_files, key=get_start_number)
    
    # Write the checklist
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Progress Checklist - {pos_name} JSONL Files\n\n")
        f.write(f"Total files: {len(json_files)}\n\n")
        f.write("## File Completion Status\n\n")
        f.write("Mark each file with [x] when fully populated with data:\n\n")
        
        for json_file in json_files:
            # Extract the range from filename
            parts = json_file.replace('.jsonl', '').split('_')
            if len(parts) >= 5:
                start = parts[2]
                end = parts[4]
                f.write(f"- [ ] `{json_file}` (lemmas {start} to {end})\n")
            else:
                f.write(f"- [ ] `{json_file}`\n")
        
        f.write("\n## Summary Statistics\n\n")
        f.write(f"- Total files: {len(json_files)}\n")
        f.write(f"- Files completed: 0/{len(json_files)} (0%)\n")
        f.write(f"- Files in progress: 0\n")
        f.write(f"- Files not started: {len(json_files)}\n")
        
        f.write("\n## Notes\n\n")
        f.write("- Each file contains up to 50 lemma entries\n")
        f.write("- Mark files as complete only when all fields are properly filled\n")
        f.write("- Update the summary statistics as you progress\n")

def main():
    base_dir = "/mnt/storage/Documents/Dictionary_Generator/DictGenerativeRule_2"
    
    # Process each POS
    pos_configs = [
        ("Noun", "Noun_Generator/Noun_Json", "Noun_Generator/progress_checklist.md"),
        ("Adjective", "Adjective_Generator/Adjective_Json", "Adjective_Generator/progress_checklist.md"),
        ("Verb", "Verb_Generator/Verb_Json", "Verb_Generator/progress_checklist.md")
    ]
    
    for pos_name, json_dir, checklist_file in pos_configs:
        print(f"Generating progress checklist for {pos_name}...")
        json_path = os.path.join(base_dir, json_dir)
        checklist_path = os.path.join(base_dir, checklist_file)
        generate_progress_checklist(json_path, checklist_path, pos_name)
        print(f"Created: {checklist_file}")

if __name__ == "__main__":
    main()