import pandas as pd
import numpy as np

def main():
    # File paths
    input_csv = "data/processed/cleaned_projects.csv"
    output_report_path = "data/processed/eda_report.txt"
    output_state_summary_path = "data/processed/state_summary.csv"
    
    print(f"Loading data from: {input_csv}...")
    # Read the cleaned dataset
    df = pd.read_csv(input_csv)
    
    # 1. Total number of records and unique project codes
    total_records = len(df)
    unique_projects = df['project_code'].nunique()
    
    # 2. Total original project cost and total expenditure
    total_original_cost = df['original_cost_crore'].sum()
    total_expenditure = df['expenditure'].sum()
    
    # 3. Average, median, minimum, and maximum physical progress
    avg_progress = df['physical_progress'].mean()
    median_progress = df['physical_progress'].median()
    min_progress = df['physical_progress'].min()
    max_progress = df['physical_progress'].max()
    
    # 4. Count projects by state
    state_counts = df['state'].value_counts().reset_index()
    state_counts.columns = ['state', 'project_count']
    
    # Save the state-wise project counts to CSV
    state_counts.to_csv(output_state_summary_path, index=False)
    print(f"Saved state summary to: {output_state_summary_path}")
    
    # 5. Identify the 10 projects with the lowest physical progress
    # We sort by 'physical_progress' ascending, then by 'project_code' or 'serial_number' for tie-breaking
    lowest_progress_projects = df.sort_values(by=['physical_progress', 'serial_number']).head(10)
    
    # 6. Calculate expenditure as a percentage of original cost
    # We use np.where to safely handle division by zero (where original_cost_crore is 0)
    df['expenditure_percentage'] = np.where(
        df['original_cost_crore'] > 0, 
        (df['expenditure'] / df['original_cost_crore']) * 100, 
        0
    )
    avg_expenditure_percentage = df['expenditure_percentage'].mean()
    
    # Prepare the analysis report content
    report_lines = [
        "=== Exploratory Data Analysis Report ===",
        f"Total Records: {total_records}",
        f"Unique Project Codes: {unique_projects}",
        "",
        "=== Financial Overview (in Rs. Crore) ===",
        f"Total Original Cost: {total_original_cost:,.2f}",
        f"Total Expenditure: {total_expenditure:,.2f}",
        f"Average Expenditure vs Original Cost Percentage: {avg_expenditure_percentage:,.2f}%",
        "",
        "=== Physical Progress Statistics ===",
        f"Average Progress: {avg_progress:,.2f}%",
        f"Median Progress: {median_progress:,.2f}%",
        f"Minimum Progress: {min_progress:,.2f}%",
        f"Maximum Progress: {max_progress:,.2f}%",
        "",
        "=== Top 10 Projects with Lowest Physical Progress ==="
    ]
    
    for idx, row in lowest_progress_projects.iterrows():
        # Keep project details brief for readability
        details_snippet = str(row['project_details']).replace('\n', ' ')[:60] + "..."
        report_lines.append(f" - Code: {row['project_code']} | Progress: {row['physical_progress']}% | State: {row['state']} | Details: {details_snippet}")
        
    report_content = "\n".join(report_lines)
    
    # 7. Save the analysis results to a text file
    with open(output_report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    print(f"Saved EDA report to: {output_report_path}")
    
    # Print the summary to the console
    print("\n" + "="*50)
    print("EDA SUMMARY")
    print("="*50)
    print(report_content)

if __name__ == "__main__":
    main()
