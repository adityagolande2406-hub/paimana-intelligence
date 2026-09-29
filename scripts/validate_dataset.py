import pandas as pd
import numpy as np
import re
import os
import io

def parse_float(val):
    if pd.isna(val) or str(val).strip() == '':
        return None
    
    # Remove commas and handle multiple numbers by just looking at the first one if we can't parse directly?
    # Actually, expenditure and physical progress should just be single numbers.
    val_str = str(val).replace(',', '').strip()
    try:
        return float(val_str)
    except ValueError:
        return 'UNPARSEABLE'

def extract_project_code(details):
    if pd.isna(details):
        return None
    # Look for exactly 6 digits enclosed in parentheses
    match = re.search(r'\((\d{6})\)', str(details))
    if match:
        return match.group(1)
    return None

def check_cost_values(cost_str):
    if pd.isna(cost_str):
        return 'missing', False # status, unparseable
    
    # Cost values often look like "1,712.00\n0.00"
    parts = str(cost_str).strip().split('\n')
    unparseable = False
    status = 'missing'
    
    parsed_parts = []
    original_strs = []
    for part in parts:
        val = part.replace(',', '').strip()
        original_strs.append(val)
        if not val:
            continue
        try:
            parsed_parts.append(float(val))
        except ValueError:
            unparseable = True
            
    # Assuming second value is revised cost
    if len(parsed_parts) > 1 and not unparseable:
        revised_val = parsed_parts[1]
        revised_str = original_strs[1]
        
        if revised_val == 0.0:
            status = 'genuine_zero'
        else:
            status = 'valid_nonzero'
            
    if unparseable:
        status = 'unparseable'
        
    return status, unparseable

def main():
    # 1. Load the existing CSV without modifying it
    input_file = r"G:\PAIMANA-Intelligence\data\processed\raw_project_rows.csv"
    output_report = r"G:\PAIMANA-Intelligence\data\processed\data_quality_report.txt"
    output_csv = r"G:\PAIMANA-Intelligence\data\processed\validation_records.csv"
    
    print(f"Loading dataset from: {input_file}")
    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return

    # Original row count
    total_rows = len(df)
    
    # 2. Extract six-digit project codes from project_details
    df['project_code'] = df['project_details'].apply(extract_project_code)
    
    # Calculate basic statistics
    unique_codes = df['project_code'].nunique()
    code_counts = df['project_code'].value_counts()
    repeated_codes = code_counts[code_counts > 1].index.tolist()
    
    # 6. Identify exact duplicate records separately from repeated project codes
    # We drop the newly added 'project_code' for exact duplicate check to just check original columns
    original_cols = [col for col in df.columns if col != 'project_code']
    df['is_exact_duplicate'] = df.duplicated(subset=original_cols, keep=False)
    exact_duplicates_count = df.duplicated(subset=original_cols, keep='first').sum()
    
    # Flag repeated codes
    df['is_repeated_code'] = df['project_code'].isin(repeated_codes)
    
    # Find missing values per row
    df['missing_columns'] = df[original_cols].apply(
        lambda row: ', '.join(row.index[row.isna() | (row.astype(str).str.strip() == '')]), 
        axis=1
    )
    
    # 7. Flag suspicious values
    # Progress outside 0-100
    def check_progress(val):
        parsed = parse_float(val)
        if parsed == 'UNPARSEABLE':
            return False, True # outside, unparseable
        if parsed is not None:
            if parsed < 0 or parsed > 100:
                return True, False
        return False, False

    progress_flags = df['physical_progress'].apply(check_progress)
    df['suspicious_progress'] = [x[0] for x in progress_flags]
    
    # Expenditure unparseable
    expenditure_unparseable = df['expenditure'].apply(lambda x: parse_float(x) == 'UNPARSEABLE')
    
    # Cost values flags
    cost_flags = df['cost_values'].apply(check_cost_values)
    df['revised_cost_status'] = [x[0] for x in cost_flags]
    df['suspicious_zero_revised_cost'] = (df['revised_cost_status'] == 'genuine_zero')
    
    # Combine unparseable flags
    def get_unparseable(row_idx):
        unp = []
        if progress_flags.iloc[row_idx][1]: unp.append('physical_progress')
        if expenditure_unparseable.iloc[row_idx]: unp.append('expenditure')
        if cost_flags.iloc[row_idx][1]: unp.append('cost_values')
        return ', '.join(unp)
        
    df['unparseable_fields'] = [get_unparseable(i) for i in range(len(df))]

    # 4. Report records grouped by source_page
    page_counts = df['source_page'].value_counts().sort_index()
    
    # Generate human readable report
    report = []
    report.append("=== Data Quality Validation Report ===")
    report.append(f"Total rows: {total_rows}")
    report.append(f"Unique project codes extracted: {unique_codes}")
    report.append(f"Number of project codes appearing more than once: {len(repeated_codes)}")
    
    repeated_rows_count = df['is_repeated_code'].sum()
    report.append(f"Total rows belonging to repeated project codes: {repeated_rows_count}")
    
    report.append(f"Exact duplicate full rows (excluding first occurrence): {exact_duplicates_count}")
    
    missing_any = (df['missing_columns'] != '').sum()
    report.append(f"Rows with missing values: {missing_any}")
    
    suspicious_prog_count = df['suspicious_progress'].sum()
    report.append(f"Rows with physical progress outside 0-100: {suspicious_prog_count}")
    
    status_counts = df['revised_cost_status'].value_counts()
    genuine_zeros = status_counts.get('genuine_zero', 0)
    missing_revised = status_counts.get('missing', 0)
    valid_nonzero = status_counts.get('valid_nonzero', 0)
    unparseable_revised = status_counts.get('unparseable', 0)
    
    report.append(f"Revised Cost Status - Genuine Zeros: {genuine_zeros}, Missing: {missing_revised}, Valid Nonzero: {valid_nonzero}, Unparseable: {unparseable_revised}")
    
    unparseable_count = (df['unparseable_fields'] != '').sum()
    report.append(f"Rows with unparseable numeric values: {unparseable_count}")
    
    report.append("\n=== Records Grouped by Source Page ===")
    for page, count in page_counts.items():
        report.append(f"Page {page}: {count} records")
        
    # 5. Compare repeated project-code records
    report.append("\n=== Analysis of Repeated Project Codes ===")
    if len(repeated_codes) > 0:
        report.append(f"Analyzing differences across records for the {len(repeated_codes)} repeated project codes...\n")
        
        # Group by project code and find which columns differ
        compare_cols = ['project_details', 'state', 'serial_number', 'approval_dates', 
                        'completion_dates', 'cost_values', 'expenditure', 'physical_progress']
        
        diff_summary = {col: 0 for col in compare_cols}
        
        for code in repeated_codes:
            subset = df[df['project_code'] == code]
            for col in compare_cols:
                # If there is more than 1 unique value in this column for this project code
                # we count it as a difference
                if subset[col].nunique(dropna=False) > 1:
                    diff_summary[col] += 1
                    
        report.append("Number of repeated project codes with varying fields:")
        for col in compare_cols:
            report.append(f" - {col}: {diff_summary[col]} codes have differing values")
    else:
        report.append("No repeated project codes found.")

    report_text = '\n'.join(report)
    
    # 8. Save a human-readable report
    with open(output_report, 'w', encoding='utf-8') as f:
        f.write(report_text)
    print(f"Human-readable report saved to: {output_report}")
    
    # 9. Save detailed record-level validation CSV
    df.to_csv(output_csv, index=False, encoding='utf-8')
    print(f"Detailed validation records saved to: {output_csv}")
    
    print("\n--- Summary of Findings ---")
    print(report_text[:1000] + "\n... (check report file for full details)")

if __name__ == '__main__':
    main()
