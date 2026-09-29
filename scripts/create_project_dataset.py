import pandas as pd

def main():
    # Define file paths
    input_csv = "data/processed/cleaned_projects.csv"
    output_csv = "data/processed/unique_projects.csv"
    
    print(f"Loading cleaned dataset from: {input_csv}...")
    # 1. Read the cleaned dataset
    df = pd.read_csv(input_csv)
    
    # Check initial shape
    print(f"Initial shape: {df.shape}")
    
    # 2. Keep exactly one row per unique project_code
    # Since our previous analysis proved that all analytical values (costs, progress, dates)
    # are identical across repeated project codes, it is perfectly safe to just drop duplicates
    # based on 'project_code' and keep the first occurrence as the representative record.
    unique_df = df.drop_duplicates(subset=['project_code'], keep='first')
    
    # 5. Save the deduplicated result to a new CSV file without modifying the original data
    unique_df.to_csv(output_csv, index=False, encoding='utf-8')
    print(f"\nSaved unique projects dataset to: {output_csv}")
    
    # 6. Verify that the output has exactly 1,731 rows and 1,731 unique project codes
    total_rows = len(unique_df)
    unique_codes = unique_df['project_code'].nunique()
    
    print("\n" + "="*50)
    print("VERIFICATION")
    print("="*50)
    print(f"Total Rows: {total_rows} (Expected: 1731)")
    print(f"Unique Project Codes: {unique_codes} (Expected: 1731)")
    
    if total_rows == 1731 and unique_codes == 1731:
        print("-> Success! The dataset has been correctly deduplicated.")
    else:
        print("-> Warning: The row counts do not match the expected 1,731.")
        
    # 7. Print the output shape and first five records
    print("\n" + "="*50)
    print("DATASET OVERVIEW")
    print("="*50)
    print(f"Final Output Shape (Rows, Columns): {unique_df.shape}")
    
    print("\nFirst five records:")
    # We use .to_string(index=False) for cleaner visual output in the terminal
    print(unique_df.head().to_string(index=False))

if __name__ == "__main__":
    main()
