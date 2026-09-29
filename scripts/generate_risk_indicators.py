import pandas as pd
import numpy as np

def assign_schedule_flag(months):
    """Assigns schedule extension flag handling missing values."""
    if pd.isna(months):
        return 'Unknown'
    elif months > 0:
        return 'Yes'
    else:
        return 'No'

def assign_monitoring_attention(row):
    """
    Determines overall monitoring attention.
    If any flag is 'Yes', returns 'Yes'.
    If no flag is 'Yes' but there is an 'Unknown', returns 'Unknown'.
    Otherwise returns 'No'.
    """
    flags = [
        row['schedule_extension_flag'], 
        row['expenditure_above_original_cost'], 
        row['low_progress_flag']
    ]
    
    if 'Yes' in flags:
        return 'Yes'
    elif 'Unknown' in flags:
        return 'Unknown'
    else:
        return 'No'

def main():
    input_csv = "data/processed/project_indicators.csv"
    output_csv = "data/processed/project_risk_indicators.csv"
    
    print(f"Loading data from: {input_csv}...")
    df = pd.read_csv(input_csv)
    
    # 3. Create schedule_extension_flag
    df['schedule_extension_flag'] = df['schedule_extension_months'].apply(assign_schedule_flag)
    
    # 4. Create expenditure_above_original_cost
    # It is 'Yes' when expenditure_to_original_cost_pct > 100, assuming no missing values here, 
    # but let's handle potential missing values safely.
    df['expenditure_above_original_cost'] = np.where(
        df['expenditure_to_original_cost_pct'].isna(), 
        'Unknown',
        np.where(df['expenditure_to_original_cost_pct'] > 100, 'Yes', 'No')
    )
    
    # 5. Create low_progress_flag
    # 'Yes' when progress is below 25%, handling missing safely
    df['low_progress_flag'] = np.where(
        df['physical_progress'].isna(),
        'Unknown',
        np.where(df['physical_progress'] < 25.0, 'Yes', 'No')
    )
    
    # 6. Create monitoring_attention
    df['monitoring_attention'] = df.apply(assign_monitoring_attention, axis=1)
    
    # 7. Save as data/processed/project_risk_indicators.csv
    df.to_csv(output_csv, index=False, encoding='utf-8')
    print(f"\nSaved transparent risk indicators to: {output_csv}")
    
    # 8. Print the number of flagged projects and a breakdown of each indicator
    print("\n" + "="*50)
    print("MONITORING INDICATORS BREAKDOWN")
    print("="*50)
    
    flags_to_summarize = [
        'schedule_extension_flag', 
        'expenditure_above_original_cost', 
        'low_progress_flag',
        'monitoring_attention'
    ]
    
    for flag in flags_to_summarize:
        counts = df[flag].value_counts()
        print(f"\n--- {flag} ---")
        for val, count in counts.items():
            print(f" {val}: {count}")
            
    total_flagged = (df['monitoring_attention'] == 'Yes').sum()
    print("\n" + "="*50)
    print(f"TOTAL PROJECTS REQUIRING MONITORING ATTENTION: {total_flagged}")
    print("="*50)
    print("\nDisclaimer: These are descriptive tracking indicators based on raw data, not ML predictions.")

if __name__ == "__main__":
    main()
