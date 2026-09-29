import pandas as pd

def main():
    input_csv = "data/processed/repeated_projects.csv"
    output_report = "data/processed/duplicate_verification.txt"
    
    print(f"Loading repeated projects from: {input_csv}...")
    df = pd.read_csv(input_csv)
    
    # 1. Define the columns that represent 'analytical values'
    analytical_cols = [
        'original_cost_crore', 'revised_cost_crore', 
        'expenditure', 'physical_progress', 
        'approval_dates', 'completion_dates'
    ]
    
    # 2. Define the columns that represent 'descriptive/metadata values'
    descriptive_cols = [
        'project_details', 'state', 'serial_number', 'source_page'
    ]
    
    # Group the dataframe by project_code
    grouped = df.groupby('project_code')
    
    identical_analytical_count = 0
    conflicting_analytical_count = 0
    
    # Track the number of groups with differing descriptive values
    differing_descriptive = {col: 0 for col in descriptive_cols}
    
    report_lines = []
    report_lines.append("=== Duplicate Verification Report ===")
    report_lines.append(f"Total Repeated Project Codes: {len(grouped)}")
    report_lines.append("")
    
    # Iterate through each group (each repeated project code)
    for code, group in grouped:
        # Check for analytical identicality:
        # A group has identical values if there is only 1 unique value per column.
        # We use dropna=False to treat NaNs correctly when checking uniqueness
        has_conflict = False
        
        for col in analytical_cols:
            if group[col].nunique(dropna=False) > 1:
                has_conflict = True
                break
                
        if has_conflict:
            conflicting_analytical_count += 1
        else:
            identical_analytical_count += 1
            
        # Check for differences in descriptive columns
        for col in descriptive_cols:
            if group[col].nunique(dropna=False) > 1:
                differing_descriptive[col] += 1
                
    # 3 & 4. Summarize counts of identical and conflicting analytical values
    report_lines.append("=== Analytical Values (Costs, Progress, Dates) ===")
    report_lines.append(f"Groups with IDENTICAL analytical values: {identical_analytical_count}")
    report_lines.append(f"Groups with CONFLICTING analytical values: {conflicting_analytical_count}")
    
    if conflicting_analytical_count == 0:
        report_lines.append("-> Conclusion: The numerical and date data for repeated projects is perfectly consistent!")
    else:
        report_lines.append("-> Conclusion: There are inconsistencies in the numerical/date data for some repeated projects.")
        
    report_lines.append("\n=== Descriptive Values (Details, State, Page, Serial) ===")
    report_lines.append("Number of groups with DIFFERING values in specific columns:")
    for col in descriptive_cols:
        report_lines.append(f" - {col}: {differing_descriptive[col]} groups differ")
        
    report_content = "\n".join(report_lines)
    
    # 5. Save the results
    with open(output_report, 'w', encoding='utf-8') as f:
        f.write(report_content)
        
    print(f"Saved verification report to: {output_report}")
    print("\n" + "="*50)
    print("VERIFICATION SUMMARY")
    print("="*50)
    print(report_content)

if __name__ == "__main__":
    main()
