import pandas as pd

def print_column_stats(df, col_list, category_name):
    """
    Helper function to print data type, missing count, and unique values
    for a specific list of columns.
    """
    print(f"\n--- {category_name} ---")
    for col in col_list:
        # Check if column exists in the dataframe
        if col in df.columns:
            dtype = df[col].dtype
            missing = df[col].isna().sum()
            unique = df[col].nunique(dropna=False)
            print(f"{col}:")
            print(f"  Type: {dtype} | Missing: {missing} | Unique: {unique}")
        else:
            print(f"{col}: Not found in dataset")

def main():
    input_csv = "data/processed/project_risk_indicators.csv"
    
    print(f"Loading dataset from: {input_csv}...")
    df = pd.read_csv(input_csv)
    
    # 2. Print the dataset shape
    print("\n" + "="*50)
    print(f"DATASET SHAPE: {df.shape[0]} rows, {df.shape[1]} columns")
    print("="*50)
    
    # 3. Categorized feature review groups
    feature_groups = {
        "Identifiers": ['serial_number', 'project_code', 'source_page'],
        "Descriptive": ['project_details', 'state'],
        "Numerical": [
            'original_cost_crore', 'revised_cost_crore', 'expenditure', 
            'physical_progress', 'schedule_extension_months', 'expenditure_to_original_cost_pct'
        ],
        "Date-related": [
            'original_approval_date', 'revised_approval_date', 
            'original_completion_date', 'revised_completion_date'
        ],
        "Existing indicators": [
            'progress_category', 'schedule_extension_flag', 
            'expenditure_above_original_cost', 'low_progress_flag', 'monitoring_attention'
        ],
        "Original source text": ['approval_dates', 'completion_dates']
    }
    
    # 4. Display stats for every column in the groups
    for category, columns in feature_groups.items():
        print_column_stats(df, columns, category)
        
    # 5. Print a short note about monitoring_attention
    print("\n" + "="*50)
    print("NOTE:")
    print("The existing 'monitoring_attention' column is purely rule-based.")
    print("It must NOT be used as an independent machine learning prediction target.")
    print("="*50)

if __name__ == "__main__":
    main()
