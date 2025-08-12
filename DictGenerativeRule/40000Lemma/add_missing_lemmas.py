import json
import pandas as pd
from pathlib import Path
import os

base_path = Path(r'E:\CompanyBuilding\DictionaryContent')

# Function to extract lemmas from JSON/JSONL files
def extract_lemmas_from_folder(folder_path, pos_type):
    lemmas = set()
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for line in lines:
                            if line.strip():
                                try:
                                    entry = json.loads(line.strip())
                                    if 'lemma' in entry:
                                        lemmas.add(entry['lemma'])
                                except:
                                    pass
                except Exception as e:
                    print(f"Error reading {file}: {e}")
                    
            elif file.endswith('.jsonl'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip():
                                try:
                                    entry = json.loads(line.strip())
                                    if 'lemma' in entry:
                                        lemmas.add(entry['lemma'])
                                except:
                                    pass
                except Exception as e:
                    print(f"Error reading {file}: {e}")
    
    return lemmas, pos_type

# Extract lemmas from each generator folder
print("Extracting lemmas from generator folders...")
adjective_lemmas, _ = extract_lemmas_from_folder(base_path / 'Adjective_Generator' / 'Adjectives_Json', 'a')
noun_lemmas, _ = extract_lemmas_from_folder(base_path / 'Noun_Generator' / 'Nouns_Json', 'n')
verb_lemmas, _ = extract_lemmas_from_folder(base_path / 'Verb_Generator' / 'Verbs_Json', 'v')

print(f"Found {len(adjective_lemmas)} adjectives")
print(f"Found {len(noun_lemmas)} nouns")
print(f"Found {len(verb_lemmas)} verbs")

# Load wordFrequency file
print("\nLoading wordFrequency file...")
word_freq_df = pd.read_excel(
    r'E:\CompanyBuilding\DictionaryContent\dataAndDocumentation\wordFrequency_Adjusted_10typesPoS.xlsx',
    sheet_name='1 lemmas'
)

# Get lemmas from wordFrequency (only n, v, j)
word_freq_lemmas = set()
for _, row in word_freq_df.iterrows():
    if row['PoS'] in ['n', 'v', 'j']:
        word_freq_lemmas.add(row['lemma'])

print(f"Found {len(word_freq_lemmas)} lemmas in wordFrequency (n, v, j only)")

# Filter out lemmas that already exist in wordFrequency
new_adjectives = adjective_lemmas - word_freq_lemmas
new_nouns = noun_lemmas - word_freq_lemmas
new_verbs = verb_lemmas - word_freq_lemmas

print(f"\nNew adjectives to add: {len(new_adjectives)}")
print(f"New nouns to add: {len(new_nouns)}")
print(f"New verbs to add: {len(new_verbs)}")

# Load current merged_lemmas.xlsx
print("\nLoading merged_lemmas.xlsx...")
merged_df = pd.read_excel(r'E:\CompanyBuilding\DictionaryContent\40000Lemma\merged_lemmas.xlsx')
last_id = merged_df['id'].max()
print(f"Last ID in merged_lemmas.xlsx: {last_id}")

# Get existing lemmas in merged_lemmas
existing_merged_lemmas = set(merged_df['lemma'].values)

# Further filter to exclude lemmas already in merged_lemmas
new_adjectives = new_adjectives - existing_merged_lemmas
new_nouns = new_nouns - existing_merged_lemmas
new_verbs = new_verbs - existing_merged_lemmas

print(f"\nAfter removing duplicates from merged_lemmas:")
print(f"New adjectives to add: {len(new_adjectives)}")
print(f"New nouns to add: {len(new_nouns)}")
print(f"New verbs to add: {len(new_verbs)}")

# Create new entries
new_entries = []
current_id = last_id + 1

# Add adjectives
for lemma in sorted(new_adjectives):
    new_entries.append({
        'id': current_id,
        'lemma': lemma,
        'pos': 'a',
        'worth_defining': '',
        'confidence': '',
        'reason': ''
    })
    current_id += 1

# Add nouns
for lemma in sorted(new_nouns):
    new_entries.append({
        'id': current_id,
        'lemma': lemma,
        'pos': 'n',
        'worth_defining': '',
        'confidence': '',
        'reason': ''
    })
    current_id += 1

# Add verbs
for lemma in sorted(new_verbs):
    new_entries.append({
        'id': current_id,
        'lemma': lemma,
        'pos': 'v',
        'worth_defining': '',
        'confidence': '',
        'reason': ''
    })
    current_id += 1

# Create new dataframe with all entries
if new_entries:
    new_df = pd.DataFrame(new_entries)
    combined_df = pd.concat([merged_df, new_df], ignore_index=True)
    
    # Save the updated file
    combined_df.to_excel(r'E:\CompanyBuilding\DictionaryContent\40000Lemma\merged_lemmas.xlsx', index=False)
    
    print(f"\nAdded {len(new_entries)} new entries to merged_lemmas.xlsx")
    print(f"New ID range: {last_id + 1} to {current_id - 1}")
    
    # Show sample of added entries
    print("\nSample of added entries:")
    print(new_df.head(10))
else:
    print("\nNo new entries to add.")