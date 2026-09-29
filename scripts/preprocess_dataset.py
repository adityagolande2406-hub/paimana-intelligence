import pandas as pd
import re

def clean_and_split_costs(df):
    """
    Splits the 'cost_values' column (e.g., '1,712.00\n0.00') into 
    'original_cost_crore' and 'revised_cost_crore' as numeric values.
    """
    # Create empty lists to hold our processed values
    original_costs = []
    revised_costs = []
    
    for val in df['cost_values']:
        if pd.isna(val):
            original_costs.append(None)
            revised_costs.append(None)
            continue
            
        # Convert to string and split by newline
        parts = str(val).strip().split('\n')
        
        # Process the first part (original cost)
        orig_str = parts[0].replace(',', '').strip()
        try:
            original_costs.append(float(orig_str))
        except ValueError:
            original_costs.append(None)
            
        # Process the second part (revised cost) if it exists
        if len(parts) > 1:
            rev_str = parts[1].replace(',', '').strip()
            try:
                revised_costs.append(float(rev_str))
            except ValueError:
                revised_costs.append(None)
        else:
            revised_costs.append(None)
            
    # Assign the lists to new columns in the DataFrame
    df['original_cost_crore'] = original_costs
    df['revised_cost_crore'] = revised_costs
    
    # We can drop the original 'cost_values' column now that we've extracted its data
    df = df.drop(columns=['cost_values'])
    return df

def clean_numeric_column(df, col_name):
    """
    Converts a column with string numbers (like '2,670.23') into float.
    """
    def to_float(val):
        if pd.isna(val):
            return None
        # Remove commas and convert to float
        clean_str = str(val).replace(',', '').strip()
        try:
            return float(clean_str)
        except ValueError:
            return None
            
    df[col_name] = df[col_name].apply(to_float)
    return df

def extract_project_code(df):
    """
    Extracts the six-digit project code from the 'project_details' string.
    Example: '(706724)' -> '706724'
    """
    def get_code(details):
        if pd.isna(details):
            return None
        # Look for exactly 6 digits enclosed in parentheses
        match = re.search(r'\((\d{6})\)', str(details))
        if match:
            return match.group(1)
        return None
        
    df['project_code'] = df['project_details'].apply(get_code)
    return df

def main():
    # 1. Read the raw dataset
    input_csv = "data/processed/raw_project_rows.csv"
    output_csv = "data/processed/cleaned_projects.csv"
    
    print(f"Loading data from: {input_csv}...")
    df = pd.read_csv(input_csv)
    
    # 2. Extract six-digit project code
    df = extract_project_code(df)
    
    # 3. Split and clean cost_values
    df = clean_and_split_costs(df)
    
    # 4 & 6. Convert expenditure and physical_progress to numeric formats
    df = clean_numeric_column(df, 'expenditure')
    df = clean_numeric_column(df, 'physical_progress')
    
    # 8. Save the processed dataset
    # We are preserving all 1,940 records as requested
    df.to_csv(output_csv, index=False, encoding='utf-8')
    print(f"\nData successfully cleaned and saved to: {output_csv}")
    
    # 9. Print basic dataset statistics and info
    print("-" * 50)
    print("DATASET OVERVIEW")
    print("-" * 50)
    print(f"Shape (Rows, Columns): {df.shape}")
    print("\nColumns present:")
    for col in df.columns:
        print(f" - {col}")
        
    print("\nMissing Values per column:")
    print(df.isna().sum())
    
    print("-" * 50)
    print("FIRST FIVE RECORDS:")
    print("-" * 50)
    print(df.head())

if __name__ == "__main__":
    main()
