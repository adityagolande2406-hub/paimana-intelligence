import sys
import os
import pandas as pd
from datetime import datetime

# Add project root to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.main import get_project_history, historical_store
from fastapi import HTTPException

def run_tests():
    print("=== PAIMANA Intelligence: Historical Trend API Tests ===\n")
    
    # 1. Clean the store and inject test data
    store_path = historical_store.storage_path
    if store_path.exists():
        os.remove(store_path)
        
    # Valid project code from the dataset (e.g. 706724)
    valid_project = 706724
    
    print("Test 1: Valid project with no history")
    data = get_project_history(valid_project)
    assert data["observation_count"] == 0
    assert data["observations"] == []
    assert "not yet available" in data["message"].lower()
    print("PASS: Handled empty history")
    
    print("\nTest 2: Unknown project code")
    try:
        get_project_history(99999999)
        assert False, "Should have raised HTTPException 404"
    except HTTPException as e:
        assert e.status_code == 404
        assert e.detail == "Project not found"
        print("PASS: Handled unknown project")
    
    print("\nTest 3: Invalid report month format normalization")
    records = [
        {
            "project_code": valid_project,
            "report_month": "August 2026",
            "physical_progress": 90.0,
            "expenditure": 500.0,
            "original_cost_crore": 1000.0,
            "schedule_extension_months": 12.0
        },
        {
            "project_code": valid_project,
            "report_month": "2026-09",
            "physical_progress": 95.0,
            "expenditure": 600.0,
            "original_cost_crore": 1000.0,
            "schedule_extension_months": 15.0
        },
        {
            "project_code": valid_project,
            "report_month": "2026-10",
            "physical_progress": None,
            "expenditure": 650.0,
            "original_cost_crore": 1000.0,
            "schedule_extension_months": None
        }
    ]
    
    historical_store.append_snapshots(records)
    
    data = get_project_history(valid_project)
    assert data["observation_count"] == 3
    
    # Chronological sort check (2026-08, 2026-09, 2026-10)
    obs = data["observations"]
    assert obs[0]["report_month"] == "2026-08"
    assert obs[1]["report_month"] == "2026-09"
    assert obs[2]["report_month"] == "2026-10"
    print("PASS: Handled multiple months and normalized formats chronologically")
    
    print("\nTest 4: Correct month-to-month changes")
    # Change from Aug to Sep
    assert obs[1]["progress_change"] == 5.0
    assert obs[1]["expenditure_change"] == 100.0
    assert obs[1]["schedule_extension_change"] == 3.0
    print("PASS: Correctly calculated month-to-month changes")
    
    print("\nTest 5: Missing-value preservation")
    # Change from Sep to Oct (missing progress and extension in Oct)
    assert obs[2]["physical_progress"] is None
    assert obs[2]["schedule_extension_months"] is None
    assert obs[2]["progress_change"] is None
    assert obs[2]["schedule_extension_change"] is None
    assert obs[2]["expenditure_change"] == 50.0
    print("PASS: Preserved missing values and omitted changes correctly")
    
    # Clean up test data
    if store_path.exists():
        os.remove(store_path)
    
    print("\nAll tests passed successfully!")

if __name__ == "__main__":
    run_tests()
