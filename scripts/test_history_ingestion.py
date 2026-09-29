import sys
import os
import io
import pandas as pd
from fastapi import HTTPException

# Add project root to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import app.main
from app.main import history_upload_preview, history_upload_confirm
import tempfile
from pathlib import Path

class MockUploadFile:
    def __init__(self, df, filename):
        self.filename = filename
        csv_str = df.to_csv(index=False)
        self.file = io.BytesIO(csv_str.encode('utf-8'))

def run_tests():
    print("=== PAIMANA Intelligence: Monthly Historical Ingestion Tests ===\n")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        test_snapshots = temp_path / "test_snapshots.csv"
        test_staging = temp_path / "staging"
        test_staging.mkdir(parents=True, exist_ok=True)
        
        # Override the global instances in app.main
        app.main.historical_store.storage_path = test_snapshots
        app.main.HISTORY_STAGING_DIR = test_staging
        
        valid_project = 706724 
        
        print("Test 1: Valid first-time import")
        df = pd.DataFrame([{"project_code": valid_project, "report_month": "2026-08", "physical_progress": 45}])
        mock_file = MockUploadFile(df, "test.csv")
        data = history_upload_preview(file=mock_file)
        assert data["valid"] is True
        assert data["valid_count"] == 1
        assert data["invalid_count"] == 0
        staging_id = data["staging_id"]
        
        conf_data = history_upload_confirm(staging_id=staging_id)
        assert conf_data["success"] is True
        assert conf_data["inserted"] == 1
        assert conf_data["updated"] == 0
        print("PASS")
        
        print("Test 2: Re-importing identical project-month records (Update)")
        df = pd.DataFrame([{"project_code": valid_project, "report_month": "2026-08", "physical_progress": 50}])
        mock_file = MockUploadFile(df, "test.csv")
        data = history_upload_preview(file=mock_file)
        staging_id = data["staging_id"]
        
        conf_data = history_upload_confirm(staging_id=staging_id)
        assert conf_data["success"] is True
        assert conf_data["inserted"] == 0
        assert conf_data["updated"] == 1
        print("PASS")
        
        print("Test 3: Same project across different months")
        df = pd.DataFrame([
            {"project_code": valid_project, "report_month": "2026-09", "physical_progress": 55},
            {"project_code": valid_project, "report_month": "2026-10", "physical_progress": 60}
        ])
        mock_file = MockUploadFile(df, "test.csv")
        data = history_upload_preview(file=mock_file)
        staging_id = data["staging_id"]
        
        conf_data = history_upload_confirm(staging_id=staging_id)
        assert conf_data["inserted"] == 2
        assert conf_data["updated"] == 0
        print("PASS")
        
        print("Test 4: Missing report_month")
        df = pd.DataFrame([{"project_code": valid_project, "physical_progress": 45}])
        mock_file = MockUploadFile(df, "test.csv")
        data = history_upload_preview(file=mock_file)
        assert data["valid"] is False
        assert "Missing required columns" in data["errors"][0]["msg"]
        print("PASS")
        
        print("Test 5-7: Invalid rows validation")
        df = pd.DataFrame([
            {"project_code": "", "report_month": "2026-08"}, 
            {"project_code": "99999999", "report_month": "2026-08"}, 
            {"project_code": valid_project, "report_month": "NotAMonth"} 
        ])
        mock_file = MockUploadFile(df, "test.csv")
        data = history_upload_preview(file=mock_file)
        assert data["valid"] is False
        assert data["invalid_count"] == 3
        print("PASS")
        
        print("Test 8: Duplicate project-month within file")
        df = pd.DataFrame([
            {"project_code": valid_project, "report_month": "2026-11"},
            {"project_code": valid_project, "report_month": "2026-11"}
        ])
        mock_file = MockUploadFile(df, "test.csv")
        data = history_upload_preview(file=mock_file)
        assert data["valid"] is False
        assert "Duplicate entry" in data["errors"][0]["msg"]
        print("PASS")
        
        print("Test 9: Invalid numeric values")
        df = pd.DataFrame([
            {"project_code": valid_project, "report_month": "2026-12", "physical_progress": 150}
        ])
        mock_file = MockUploadFile(df, "test.csv")
        data = history_upload_preview(file=mock_file)
        assert data["valid"] is False
        print("PASS")
        
        print("Test 10: Confirmation with missing/expired staging")
        try:
            history_upload_confirm(staging_id="nonexistent-id")
            assert False, "Should have raised exception"
        except HTTPException as e:
            assert e.status_code == 400
        print("PASS")
        
        print("Test 11: Repeated confirmation of the same staged batch")
        df = pd.DataFrame([{"project_code": valid_project, "report_month": "2027-01", "physical_progress": 10}])
        mock_file = MockUploadFile(df, "test.csv")
        data = history_upload_preview(file=mock_file)
        staging_id = data["staging_id"]
        
        history_upload_confirm(staging_id=staging_id)
        try:
            history_upload_confirm(staging_id=staging_id)
            assert False, "Should have raised exception"
        except HTTPException as e:
            assert e.status_code == 400
        print("PASS")
        
        print("\nAll tests passed successfully!")

if __name__ == "__main__":
    run_tests()
