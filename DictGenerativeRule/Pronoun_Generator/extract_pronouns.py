import pandas as pd
import os

# Path to the Excel file
excel_file = r"E:\CompanyBuilding\DictionaryContent\dataAndDocumentation\wordFrequency_Adjusted_10typesPoS.xlsx"

# Try reading with different parameters
try:
    # Read all sheets
    all_sheets = pd.read_excel(excel_file, sheet_name=None)
    print(f"Found {len(all_sheets)} sheets in the Excel file:")
    for sheet_name in all_sheets.keys():
        print(f"  - {sheet_name}")
    
    # Try the first sheet with different header row
    print("\nTrying to read with different header rows...")
    
    # Try with header starting from different rows
    for header_row in range(10):
        try:
            df = pd.read_excel(excel_file, header=header_row)
            if len(df.columns) > 2 and not all('Unnamed' in str(col) for col in df.columns):
                print(f"\nFound proper headers at row {header_row}:")
                print("Column names:", df.columns.tolist())
                print("\nFirst few rows:")
                print(df.head())
                break
        except:
            continue
    
except Exception as e:
    print(f"Error reading Excel file: {e}")
    
# Focus on the '1 lemmas' sheet
print("\n\nReading '1 lemmas' sheet:")
try:
    # Try reading the lemmas sheet
    df_lemmas = pd.read_excel(excel_file, sheet_name='1 lemmas')
    print("Column names in '1 lemmas' sheet:")
    print(df_lemmas.columns.tolist())
    print("\nFirst 10 rows:")
    print(df_lemmas.head(10))
    
    # Try with different header rows for this sheet
    for header_row in range(5):
        df_lemmas_test = pd.read_excel(excel_file, sheet_name='1 lemmas', header=header_row)
        if len(df_lemmas_test.columns) > 2:
            print(f"\n\nTrying header row {header_row} for '1 lemmas' sheet:")
            print("Columns:", df_lemmas_test.columns.tolist())
            print("First few rows:")
            print(df_lemmas_test.head())
            
            # Store the best dataframe
            if not all('Unnamed' in str(col) for col in df_lemmas_test.columns):
                df = df_lemmas_test
                break
    
except Exception as e:
    print(f"Error reading lemmas sheet: {e}")

# Now extract pronouns - they are marked with 'p' in the PoS column
print("\n\nExtracting pronouns (PoS = 'p'):")

# Make sure we have the correct dataframe
if 'df' not in locals():
    df = pd.read_excel(excel_file, sheet_name='1 lemmas')

# Filter for pronouns
pronouns_df = df[df['PoS'] == 'p']

# Display pronoun information
if not pronouns_df.empty:
    print(f"\nFound {len(pronouns_df)} pronouns:")
    print("\nPronoun list with frequency rank:")
    
    # Get the pronoun list
    pronoun_list = []
    for _, row in pronouns_df.iterrows():
        pronoun = row['lemma']
        rank = row['rank']
        freq = row['freq']
        print(f"  Rank {rank}: {pronoun} (frequency: {freq:,})")
        pronoun_list.append(pronoun)
    
    # Save to a text file
    with open('pronoun_list.txt', 'w') as f:
        for pronoun in pronoun_list:
            f.write(f"{pronoun}\n")
    
    print(f"\nPronoun list saved to pronoun_list.txt")
    print(f"Total pronouns: {len(pronoun_list)}")
    
    # Also save with more details
    pronouns_df[['rank', 'lemma', 'freq', 'perMil']].to_csv('pronouns_detailed.csv', index=False)
    print("Detailed pronoun data saved to pronouns_detailed.csv")
else:
    print("\nNo pronouns found in the dataframe")