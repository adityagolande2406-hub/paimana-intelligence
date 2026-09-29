import pandas as pd
import numpy as np

def assign_schedule_class(months):
    """Assigns schedule monitoring class."""
    if pd.isna(months):
        return "Schedule Data Unavailable"
    elif months > 0:
        return "Schedule Extension Recorded"
    else:
        return "No Recorded Extension"

def create_explanation(row):
    """
    Creates a transparent, human-readable monitoring explanation.
    It mentions applicable indicators without asserting the project is 'currently overdue'
    just because an extension was recorded.
    """
    reasons = []
    
    # 1. Schedule Explanation
    if row['schedule_monitoring_class'] == "Schedule Extension Recorded":
        reasons.append(f"A schedule extension of {int(row['schedule_extension_months'])} months is recorded.")
    elif row['schedule_monitoring_class'] == "No Recorded Extension":
        reasons.append("No schedule extension is currently recorded.")
    else:
        reasons.append("Schedule extension data is unavailable.")
        
    # 2. Progress Explanation
    if row['low_progress_indicator'] == 'Yes':
        reasons.append(f"Physical progress is low ({row['physical_progress']}%).")
    else:
        reasons.append(f"Physical progress is {row['physical_progress']}%.")
        
    # 3. Expenditure Explanation (without using revised_cost_crore)
    if row['expenditure_above_original_cost'] == 'Yes':
        reasons.append("Expenditure has exceeded the original project cost.")
        
    return " ".join(reasons)

def main():
    input_csv = "data/processed/project_risk_indicators.csv"
    output_csv = "data/processed/schedule_monitoring.csv"
    
    print(f"Loading data from: {input_csv}...")
    df = pd.read_csv(input_csv)
    
    # 2. Create schedule monitoring classification
    df['schedule_monitoring_class'] = df['schedule_extension_months'].apply(assign_schedule_class)
    
    # 3. Create low progress indicator
    df['low_progress_indicator'] = np.where(
        df['physical_progress'].isna(),
        'Unknown',
        np.where(df['physical_progress'] < 25.0, 'Yes', 'No')
    )
    
    # 4. Create human-readable monitoring explanation
    df['monitoring_explanation'] = df.apply(create_explanation, axis=1)
    
    # 7. Save the result
    df.to_csv(output_csv, index=False, encoding='utf-8')
    print(f"\nSaved schedule monitoring dataset to: {output_csv}")
    
    # 8. Print classification counts, missing-value counts, and output shape
    print("\n" + "="*50)
    print("OUTPUT SHAPE")
    print("="*50)
    print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
    
    print("\n" + "="*50)
    print("CLASSIFICATION COUNTS")
    print("="*50)
    print("\n--- Schedule Monitoring Class ---")
    print(df['schedule_monitoring_class'].value_counts().to_string())
    
    print("\n--- Low Progress Indicator ---")
    print(df['low_progress_indicator'].value_counts().to_string())
    
    print("\n" + "="*50)
    print("MISSING VALUE COUNTS (New Columns)")
    print("="*50)
    new_cols = ['schedule_monitoring_class', 'low_progress_indicator', 'monitoring_explanation']
    print(df[new_cols].isna().sum().to_string())
    
    print("\n" + "="*50)
    print("SAMPLE EXPLANATIONS")
    print("="*50)
    for idx, text in df['monitoring_explanation'].head(5).items():
        print(f"Project {idx + 1}: {text}")

if __name__ == "__main__":
    main()
