import os
import sys
import pandas as pd
from pathlib import Path

# Add project root to python path to allow importing app module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.historical_store import HistoricalStore

def run_tests():
    print("=== PAIMANA Intelligence: Historical Store Tests ===\n")
    
    # Use a separate test directory to avoid interfering with any real historical data (if any)
    test_dir = "data/historical_test"
    test_file = "test_snapshots.csv"
    
    if os.path.exists(f"{test_dir}/{test_file}"):
        os.remove(f"{test_dir}/{test_file}")
        
    store = HistoricalStore(storage_dir=test_dir, filename=test_file)
    
    # 1. First snapshot insertion
    print("Test 1: First snapshot insertion")
    data_1 = [
        {"project_code": "1001", "report_month": "2026-08", "physical_progress": 45.0, "source_report": "MoSPI Aug 2026"}
    ]
    res1 = store.append_snapshots(data_1)
    print(res1)
    assert res1["inserted"] == 1
    assert res1["updated"] == 0
    
    # 2. Second month insertion for the same project
    print("\nTest 2: Second month insertion for same project")
    data_2 = [
        {"project_code": "1001", "report_month": "2026-09", "physical_progress": 50.0, "source_report": "MoSPI Sep 2026"}
    ]
    res2 = store.append_snapshots(data_2)
    print(res2)
    assert res2["inserted"] == 1
    assert res2["updated"] == 0
    
    # 3. Duplicate month rejection (idempotent update)
    print("\nTest 3: Duplicate month update")
    data_3 = [
        {"project_code": "1001", "report_month": "2026-09", "physical_progress": 55.0, "source_report": "MoSPI Sep 2026 (Correction)"}
    ]
    res3 = store.append_snapshots(data_3)
    print(res3)
    assert res3["inserted"] == 0
    assert res3["updated"] == 1
    
    # 4. Multiple projects and missing value preservation
    print("\nTest 4: Multiple projects and missing values")
    data_4 = [
        {"project_code": "1002", "report_month": "2026-09", "physical_progress": None, "schedule_extension_months": None, "source_report": "MoSPI Sep 2026"},
        {"project_code": "1003", "report_month": "2026-09", "physical_progress": 99.0, "revised_cost_crore": 0.0}
    ]
    res4 = store.append_snapshots(data_4)
    print(res4)
    assert res4["inserted"] == 2
    
    # Verify missing values didn't become zero
    df = pd.read_csv(f"{test_dir}/{test_file}", dtype=str)
    proj_1002 = df[df['project_code'] == '1002'].iloc[0]
    assert pd.isna(proj_1002['physical_progress']), "Missing values were incorrectly filled!"
    
    # 5. Invalid project code handling
    print("\nTest 5: Invalid project code handling")
    data_5 = [
        {"project_code": None, "report_month": "2026-09"},
        {"project_code": "  ", "report_month": "2026-09"},
        {"project_code": "1004", "report_month": None}
    ]
    res5 = store.append_snapshots(data_5)
    print(res5)
    assert res5["rejected"] == 3
    assert len(res5["errors"]) == 3
    
    print("\nAll tests passed successfully!")
    print(f"Test CSV written to: {test_dir}/{test_file}")

if __name__ == "__main__":
    run_tests()
