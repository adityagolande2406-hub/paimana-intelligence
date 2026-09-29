import pandas as pd
import numpy as np
import re

def extract_dates(date_str):
    """
    Extracts original and revised dates from a string like "12/2016\n(03/2018)".
    If there is no revised date or it is "(-)", returns None for revised date.
    Returns: (original_date_str, revised_date_str)
    """
    if pd.isna(date_str):
        return None, None
        
    parts = str(date_str).strip().split('\n')
    original = parts[0].strip()
    revised = None
    
    if original == '(-)' or original == '-':
        original = None
        
    if len(parts) > 1:
        # Extract the date from inside parentheses
        match = re.search(r'\((.*?)\)', parts[1])
        if match:
            rev_val = match.group(1).strip()
            if rev_val != '-' and rev_val != '':
                revised = rev_val
                
    return original, revised

def assign_progress_category(progress):
    """
    Assigns a category based on physical progress.
    """
    if pd.isna(progress):
        return None
    
    if progress <= 25.0:
        return 'Low'
    elif progress <= 50.0:
        return 'Moderate'
    elif progress <= 75.0:
        return 'High'
    elif progress <= 100.0:
        return 'Very High'
    else:
        # Just in case there are values > 100
        return 'Very High'

def main():
    input_csv = "data/processed/unique_projects.csv"
    output_csv = "data/processed/project_indicators.csv"
    
    print(f"Loading data from: {input_csv}...")
    df = pd.read_csv(input_csv)
    
    # 1 & 2. Extract original and revised dates
    # Apply extraction logic to approval_dates
    approval_tuples = df['approval_dates'].apply(extract_dates)
    df['original_approval_date'] = [t[0] for t in approval_tuples]
    df['revised_approval_date'] = [t[1] for t in approval_tuples]
    
    # Apply extraction logic to completion_dates
    completion_tuples = df['completion_dates'].apply(extract_dates)
    df['original_completion_date'] = [t[0] for t in completion_tuples]
    df['revised_completion_date'] = [t[1] for t in completion_tuples]
    
    # 3. Handle (-) and invalid dates safely as missing
    # Convert string dates to actual datetime objects
    # Format is usually MM/YYYY
    df['original_approval_date'] = pd.to_datetime(df['original_approval_date'], format='%m/%Y', errors='coerce')
    df['revised_approval_date'] = pd.to_datetime(df['revised_approval_date'], format='%m/%Y', errors='coerce')
    df['original_completion_date'] = pd.to_datetime(df['original_completion_date'], format='%m/%Y', errors='coerce')
    df['revised_completion_date'] = pd.to_datetime(df['revised_completion_date'], format='%m/%Y', errors='coerce')
    
    # 4. Create schedule_extension_months
    # Difference in months = (year2 - year1) * 12 + (month2 - month1)
    df['schedule_extension_months'] = (
        (df['revised_completion_date'].dt.year - df['original_completion_date'].dt.year) * 12 + 
        (df['revised_completion_date'].dt.month - df['original_completion_date'].dt.month)
    )
    
    # 5. Create expenditure_to_original_cost_pct safely
    df['expenditure_to_original_cost_pct'] = np.where(
        df['original_cost_crore'] > 0,
        (df['expenditure'] / df['original_cost_crore']) * 100,
        0
    )
    
    # 6. Create progress_category
    df['progress_category'] = df['physical_progress'].apply(assign_progress_category)
    
    # 8. Save as data/processed/project_indicators.csv
    df.to_csv(output_csv, index=False, encoding='utf-8')
    print(f"\nSaved derived indicators to: {output_csv}")
    
    # 9. Print missing-value counts for the new columns
    new_cols = [
        'original_approval_date', 'revised_approval_date',
        'original_completion_date', 'revised_completion_date',
        'schedule_extension_months', 'expenditure_to_original_cost_pct',
        'progress_category'
    ]
    
    print("\n" + "="*50)
    print("DATE PARSING VERIFICATION")
    print("="*50)
    date_cols = [
        'original_approval_date', 'revised_approval_date',
        'original_completion_date', 'revised_completion_date'
    ]
    for col in date_cols:
        valid_count = df[col].notna().sum()
        missing_count = df[col].isna().sum()
        print(f"{col}: {valid_count} valid, {missing_count} missing")
        
    print("\n" + "="*50)
    print("MISSING VALUES IN OTHER NEW COLUMNS")
    print("="*50)
    other_new_cols = ['schedule_extension_months', 'expenditure_to_original_cost_pct', 'progress_category']
    missing_counts = df[other_new_cols].isna().sum()
    for col, count in missing_counts.items():
        print(f"{col}: {count} missing values")
        
    # 9. Print the first five records
    print("\n" + "="*50)
    print("FIRST FIVE RECORDS (New Columns Only)")
    print("="*50)
    # Print only the new columns to avoid cluttering the terminal
    print(df[new_cols].head().to_string())

if __name__ == "__main__":
    main()
