import pandas as pd
import re

def main():
    # 1. Define file paths
    raw_csv = "data/processed/raw_project_rows.csv"
    cleaned_csv = "data/processed/cleaned_projects.csv"
    unique_csv = "data/processed/unique_projects.csv"
    
    print("Loading datasets...")
    # Load the datasets
    df_raw = pd.read_csv(raw_csv)
    df_clean = pd.read_csv(cleaned_csv)
    df_unique = pd.read_csv(unique_csv)
    
    print("\n" + "="*50)
    print("DATASET SHAPES")
    print("="*50)
    # 2. Print the shape of each dataset
    print(f"Raw dataset shape: {df_raw.shape}")
    print(f"Cleaned dataset shape: {df_clean.shape}")
    print(f"Unique dataset shape: {df_unique.shape}")
    
    print("\n" + "="*50)
    print("RAW COST VALUES (FIRST 10 ENTRIES)")
    print("="*50)
    # 3. Display the first 10 raw cost_values entries
    # Replace newlines with '\n' visually for easier reading in terminal
    first_10_costs = df_raw['cost_values'].head(10).astype(str).str.replace('\n', '\\n')
    for idx, val in first_10_costs.items():
        print(f"Row {idx}: {val}")
        
    print("\n" + "="*50)
    print("COST VALUE ANALYSIS")
    print("="*50)
    
    two_line_count = 0
    non_zero_second_count = 0
    non_zero_examples = []
    
    # 4 & 5 & 7. Analyze raw cost entries
    for idx, row in df_raw.iterrows():
        cost_str = str(row['cost_values']).strip()
        parts = cost_str.split('\n')
        
        # Check if the entry contains two newline-separated values
        if len(parts) == 2:
            two_line_count += 1
            
            # Get the second value, strip commas and whitespace
            second_val_str = parts[1].replace(',', '').strip()
            
            try:
                # Parse to float safely
                second_val_float = float(second_val_str)
                # Check if it is strictly non-zero
                if second_val_float != 0.0:
                    non_zero_second_count += 1
                    
                    # Extract project code to display as an example (requirement 7)
                    details = str(row['project_details'])
                    match = re.search(r'\((.*?)\)', details)
                    proj_code = match.group(1) if match else "Unknown"
                    
                    # Store up to 10 examples
                    if len(non_zero_examples) < 10:
                        non_zero_examples.append({
                            'project_code': proj_code,
                            'raw_string': cost_str.replace('\n', '\\n'),
                            'parsed_revised_cost': second_val_float
                        })
            except ValueError:
                # Handle cases where the string cannot be parsed as a float
                pass
                
    print(f"Raw cost entries containing exactly two newline-separated values: {two_line_count}")
    print(f"Raw cost entries with a strictly NON-ZERO second value: {non_zero_second_count}")
    
    # 6. Count non-zero revised costs in cleaned and unique datasets
    clean_non_zero = (df_clean['revised_cost_crore'] != 0.0).sum()
    unique_non_zero = (df_unique['revised_cost_crore'] != 0.0).sum()
    
    print(f"Cleaned records with a non-zero revised cost: {clean_non_zero}")
    print(f"Unique records with a non-zero revised cost: {unique_non_zero}")
    
    # 7. Display up to 10 examples of non-zero raw second costs
    print("\n" + "="*50)
    print("NON-ZERO REVISED COST EXAMPLES (Up to 10)")
    print("="*50)
    
    if len(non_zero_examples) == 0:
        print("No non-zero revised cost examples found in the raw data.")
    else:
        for idx, example in enumerate(non_zero_examples):
            print(f"Example {idx + 1}:")
            print(f"  Project Code: {example['project_code']}")
            print(f"  Raw String: {example['raw_string']}")
            print(f"  Parsed Revised Cost: {example['parsed_revised_cost']}")
            print("-" * 30)
            
    print("\nDiagnostic complete.")

if __name__ == "__main__":
    main()
