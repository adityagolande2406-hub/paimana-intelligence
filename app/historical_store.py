import os
import pandas as pd
from datetime import datetime
from pathlib import Path

class HistoricalStore:
    def __init__(self, storage_dir="data/historical", filename="historical_snapshots.csv"):
        os.makedirs(storage_dir, exist_ok=True)
        self.storage_path = Path(storage_dir) / filename
        self.columns = [
            "project_code",
            "report_month",
            "report_date",
            "physical_progress",
            "expenditure",
            "original_cost_crore",
            "revised_cost_crore",
            "original_completion_date",
            "revised_completion_date",
            "schedule_extension_months",
            "source_report",
            "imported_at"
        ]
        
    def _load_data(self):
        if not self.storage_path.exists():
            return pd.DataFrame(columns=self.columns)
        return pd.read_csv(self.storage_path, dtype={'project_code': str, 'report_month': str})
        
    def _save_data(self, df):
        temp_path = self.storage_path.with_suffix('.tmp')
        df.to_csv(temp_path, index=False)
        os.replace(temp_path, self.storage_path)

    def append_snapshots(self, records: list) -> dict:
        """
        Appends new monthly snapshots. Updates existing records for the same project_code + report_month.
        """
        if not records:
            return {"inserted": 0, "updated": 0, "rejected": 0, "errors": []}
            
        df = self._load_data()
        
        valid_records = []
        rejected = 0
        errors = []
        
        imported_at = datetime.utcnow().isoformat()
        
        for r in records:
            # Validate required fields
            raw_code = r.get("project_code")
            raw_month = r.get("report_month")
            
            if raw_code is None or str(raw_code).strip() == "" or str(raw_code) == "nan":
                rejected += 1
                errors.append(f"Missing or invalid project_code for record: {r}")
                continue
                
            try:
                norm_month = pd.to_datetime(str(raw_month)).strftime("%Y-%m")
            except Exception:
                norm_month = None
                
            if norm_month is None:
                rejected += 1
                errors.append(f"Missing or invalid report_month for project {raw_code}")
                continue
                
            clean_record = {
                "project_code": str(raw_code).strip(),
                "report_month": norm_month,
                "report_date": r.get("report_date"),
                "physical_progress": r.get("physical_progress"),
                "expenditure": r.get("expenditure"),
                "original_cost_crore": r.get("original_cost_crore"),
                "revised_cost_crore": r.get("revised_cost_crore"),
                "original_completion_date": r.get("original_completion_date"),
                "revised_completion_date": r.get("revised_completion_date"),
                "schedule_extension_months": r.get("schedule_extension_months"),
                "source_report": r.get("source_report", "Unknown"),
                "imported_at": imported_at
            }
            valid_records.append(clean_record)
            
        if not valid_records:
            return {"inserted": 0, "updated": 0, "rejected": rejected, "errors": errors}
            
        new_df = pd.DataFrame(valid_records, columns=self.columns)
        
        if df.empty:
            self._save_data(new_df)
            return {"inserted": len(new_df), "updated": 0, "rejected": rejected, "errors": errors}
            
        # Combine existing and new data
        combined = pd.concat([df, new_df], ignore_index=True)
        
        # Deduplicate, keeping the newly inserted one if project_code + report_month matches
        initial_len = len(combined)
        combined.drop_duplicates(subset=["project_code", "report_month"], keep='last', inplace=True)
        final_len = len(combined)
        
        updated = initial_len - final_len
        inserted = len(new_df) - updated
        
        self._save_data(combined)
        
        return {"inserted": inserted, "updated": updated, "rejected": rejected, "errors": errors}
