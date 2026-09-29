import pandas as pd

def main():
    # 1. Read the cleaned dataset
    input_csv = "data/processed/cleaned_projects.csv"
    output_repeated_csv = "data/processed/repeated_projects.csv"
    
    print(f"Loading data from: {input_csv}...")
    df = pd.read_csv(input_csv)
    
    # We want to identify project codes that appear more than once
    # First, let's count how many times each project code appears
    code_counts = df['project_code'].value_counts()
    
    # 2. Identify all project codes appearing more than once
    repeated_codes = code_counts[code_counts > 1].index.tolist()
    
    # Filter the original dataframe to keep only the repeated records
    repeated_df = df[df['project_code'].isin(repeated_codes)].copy()
    
    # Sort the repeated records by project code so they are grouped together visually
    repeated_df = repeated_df.sort_values(by=['project_code', 'serial_number'])
    
    # 5. Save the repeated records to a new CSV file
    repeated_df.to_csv(output_repeated_csv, index=False, encoding='utf-8')
    print(f"Saved repeated records to: {output_repeated_csv}")
    
    # 6. Print the number of repeated codes
    print("\n" + "=" * 50)
    print("REPEATED PROJECT CODES SUMMARY")
    print("=" * 50)
    print(f"Total unique project codes: {df['project_code'].nunique()}")
    print(f"Number of project codes appearing more than once: {len(repeated_codes)}")
    print(f"Total number of repeated rows in dataset: {len(repeated_df)}")
    
    # Print a sample of 10 groups
    print("\n" + "=" * 50)
    print("SAMPLE OF REPEATED GROUPS (Showing up to 10 groups)")
    print("=" * 50)
    
    # 3. Compare their fields for the sample
    columns_to_compare = [
        'project_code', 'state', 'original_cost_crore', 'expenditure', 
        'physical_progress', 'approval_dates', 'completion_dates'
    ]
    
    # Get up to 10 repeated codes for the sample
    sample_codes = repeated_codes[:10]
    
    for code in sample_codes:
        print(f"\n--- Project Code: {code} ---")
        # Extract the rows for this specific project code
        group = repeated_df[repeated_df['project_code'] == code]
        
        # Display the comparison columns for each occurrence
        # We use .to_string(index=False) for cleaner console output
        print(group[columns_to_compare].to_string(index=False))

    print("\nFinished duplicate analysis without altering the original cleaned dataset.")

if __name__ == "__main__":
    main()
