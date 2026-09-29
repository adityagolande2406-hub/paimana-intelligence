from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional
import pandas as pd
from pathlib import Path
from datetime import datetime
import os
import uuid
import json
from app.risk_engine import ProjectRiskAssessor
from app.historical_store import HistoricalStore
from app.historical_analytics import HistoricalTrendAnalyzer
from fastapi.middleware.cors import CORSMiddleware

# Initialize the FastAPI application
risk_assessor = ProjectRiskAssessor()
trend_analyzer = HistoricalTrendAnalyzer()
app = FastAPI(title="PAIMANA Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Safely resolve the project root relative to this file's location
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = PROJECT_ROOT / "data" / "processed" / "schedule_monitoring.csv"
HISTORY_CSV = PROJECT_ROOT / "data" / "processed" / "import_history.csv"
TEMP_CSV = PROJECT_ROOT / "data" / "processed" / "temp_upload.csv"
historical_store = HistoricalStore(storage_dir=str(PROJECT_ROOT / "data" / "historical"))

HISTORY_STAGING_DIR = PROJECT_ROOT / "data" / "processed" / "staging"
HISTORY_STAGING_DIR.mkdir(parents=True, exist_ok=True)


# Direct static asset fallback routes
@app.get("/styles.css")
def get_root_css():
    return FileResponse(PROJECT_ROOT / "frontend" / "styles.css", media_type="text/css")

@app.get("/app.js")
def get_root_js():
    return FileResponse(PROJECT_ROOT / "frontend" / "app.js", media_type="application/javascript")

# Mount the static files (css, js) from the frontend directory
app.mount("/static", StaticFiles(directory=str(PROJECT_ROOT / "frontend")), name="static")


@app.get("/")
def read_root():
    """
    Root endpoint serving the frontend dashboard HTML.
    """
    return FileResponse(PROJECT_ROOT / "frontend" / "index.html")


@app.get("/health")
def read_health():
    """
    Simple health check endpoint.
    """
    return {"status": "healthy"}


@app.get("/summary")
def get_summary():
    """
    Reads the schedule monitoring dataset and returns high-level statistics.
    Handles file missing errors gracefully.
    """
    # Check if the dataset exists before trying to read it
    if not CSV_PATH.exists():
        # Raise an HTTP 500 Internal Server Error if the file is missing
        raise HTTPException(
            status_code=500, 
            detail=f"Dataset not found at {CSV_PATH}. Please ensure data processing scripts have been run."
        )
        
    try:
        # Read the dataset using pandas
        df = pd.read_csv(CSV_PATH)
        
        # Calculate statistics
        total_projects = len(df)
        # Calculate schedule category counts dynamically
        ext = df['schedule_extension_months']
        extension_recorded = int((ext > 0).sum())
        no_extension = int((ext == 0).sum())
        earlier_revised_completion = int((ext < 0).sum())
        data_unavailable = int(ext.isna().sum())
        
        # Count low progress projects
        low_progress = int((df['low_progress_indicator'] == 'Yes').sum())
        
        # Return the summary as a JSON response
        return {
            "total_projects": total_projects,
            "schedule_extension_recorded": extension_recorded,
            "no_recorded_extension": no_extension,
            "schedule_data_unavailable": data_unavailable,
            "earlier_revised_completion": earlier_revised_completion,
            "low_progress_projects": low_progress
        }
    except Exception as e:
        # Catch any unexpected parsing errors
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred while reading the dataset: {str(e)}"
        )

@app.get("/states")
def get_states():
    if not CSV_PATH.exists():
        return []
    df = pd.read_csv(CSV_PATH)
    states = [s for s in df['state'].unique() if pd.notnull(s)]
    return sorted(states)
def _apply_dynamic_classifications(df):
    mask_pos = df['schedule_extension_months'] > 0
    mask_zero = df['schedule_extension_months'] == 0
    mask_neg = df['schedule_extension_months'] < 0
    mask_nan = df['schedule_extension_months'].isna()
    
    df.loc[mask_pos, 'schedule_monitoring_class'] = 'Schedule Extension Recorded'
    df.loc[mask_zero, 'schedule_monitoring_class'] = 'No Recorded Extension'
    df.loc[mask_nan, 'schedule_monitoring_class'] = 'Schedule Data Unavailable'
    
    df.loc[mask_neg, 'schedule_monitoring_class'] = 'Earlier Revised Completion'
    df.loc[mask_neg, 'monitoring_explanation'] = 'The reported revised completion date is earlier than the original completion date. This requires verification.'
    
    return df

@app.get("/projects")
def get_projects(
    limit: int = 10, 
    page: int = 1, 
    q: Optional[str] = None, 
    state: Optional[str] = None
):
    """
    Returns actual project records for the frontend table.
    Supports a limit parameter (default 10) to avoid overloading the browser.
    Pass limit=0 to return all records.
    Supports q for searching, state for filtering, and page for pagination.
    """
    if not CSV_PATH.exists():
        raise HTTPException(
            status_code=500, 
            detail=f"Dataset not found at {CSV_PATH}. Please ensure data processing scripts have been run."
        )
        
    try:
        df = pd.read_csv(CSV_PATH)
        df = _apply_dynamic_classifications(df)
        
        # Filtering
        if q:
            q_lower = q.lower()
            mask = df['project_details'].str.lower().str.contains(q_lower, na=False) | \
                   df['project_code'].astype(str).str.contains(q_lower, na=False)
            df = df[mask]
            
        if state:
            df = df[df['state'] == state]
            
        total_records = len(df)
        
        # Select the requested columns
        cols = [
            'project_code', 
            'state', 
            'physical_progress', 
            'schedule_monitoring_class', 
            'monitoring_explanation'
        ]
        
        if limit > 0:
            start_idx = (page - 1) * limit
            df = df.iloc[start_idx:start_idx + limit]
            
        # Replace NaNs with None for proper JSON serialization
        df = df.where(pd.notnull(df), None)
        
        return {
            "items": df[cols].to_dict(orient="records"),
            "total": total_records,
            "page": page,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred while reading the dataset: {str(e)}"
        )

@app.get("/projects/{project_code}")
def get_project_details(project_code: int):
    """
    Returns the full details of a specific project based on its project code.
    """
    if not CSV_PATH.exists():
        raise HTTPException(status_code=500, detail="Dataset not found")
        
    try:
        df = pd.read_csv(CSV_PATH)
        df = _apply_dynamic_classifications(df)
        project = df[df['project_code'] == project_code]
        
        if project.empty:
            raise HTTPException(status_code=404, detail="Project not found")
            
        # Select one row and replace NaNs with None for JSON
        record = project.iloc[0].where(pd.notnull(project.iloc[0]), None).to_dict()
        return record
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/projects/{project_code}/risk")
def get_project_risk(project_code: int):
    """
    Returns the rule-based risk assessment for a specific project based on its project code.
    """
    if not CSV_PATH.exists():
        raise HTTPException(status_code=500, detail="Dataset not found")
        
    try:
        df = pd.read_csv(CSV_PATH)
        project = df[df['project_code'] == project_code]
        
        if project.empty:
            raise HTTPException(status_code=404, detail="Project not found")
            
        # Extract record and replace NaNs with None for safety
        record = project.iloc[0].where(pd.notnull(project.iloc[0]), None).to_dict()
        
        return risk_assessor.assess_project(record)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/projects/{project_code}/history")
def get_project_history(project_code: int):
    """
    Returns historical observations for a specific project.
    """
    if not CSV_PATH.exists():
        raise HTTPException(status_code=500, detail="Dataset not found")
        
    try:
        df_op = pd.read_csv(CSV_PATH)
        if df_op[df_op['project_code'] == project_code].empty:
            raise HTTPException(status_code=404, detail="Project not found")
            
        hist_df = historical_store._load_data()
        
        if hist_df.empty:
            return {
                "observation_count": 0,
                "observations": [],
                "analytics": {"status": "Insufficient Data", "message": "At least two chronological observations are required to compute trends.", "metrics": None},
                "message": "Historical observations are not yet available."
            }
            
        proj_hist = hist_df[hist_df['project_code'] == str(project_code)].copy()
        
        if proj_hist.empty:
            return {
                "observation_count": 0,
                "observations": [],
                "analytics": {"status": "Insufficient Data", "message": "At least two chronological observations are required to compute trends.", "metrics": None},
                "message": "Historical observations are not yet available."
            }
            
        proj_hist = proj_hist.sort_values(by='report_month', ascending=True).reset_index(drop=True)
        
        observations = []
        for i, row in proj_hist.iterrows():
            obs = {
                "report_month": row.get("report_month"),
                "physical_progress": row.get("physical_progress") if pd.notnull(row.get("physical_progress")) else None,
                "expenditure": row.get("expenditure") if pd.notnull(row.get("expenditure")) else None,
                "original_cost_crore": row.get("original_cost_crore") if pd.notnull(row.get("original_cost_crore")) else None,
                "revised_cost_crore": row.get("revised_cost_crore") if pd.notnull(row.get("revised_cost_crore")) else None,
                "schedule_extension_months": row.get("schedule_extension_months") if pd.notnull(row.get("schedule_extension_months")) else None,
                "progress_change": None,
                "expenditure_change": None,
                "schedule_extension_change": None
            }
            
            # Additional required field: expenditure ratio (if expenditure and original_cost_crore are valid and original_cost > 0)
            if obs["expenditure"] is not None and obs["original_cost_crore"] is not None and obs["original_cost_crore"] > 0:
                obs["expenditure_ratio"] = round((obs["expenditure"] / obs["original_cost_crore"]) * 100, 2)
            else:
                obs["expenditure_ratio"] = None
            
            if i > 0:
                prev = observations[i-1]
                if obs["physical_progress"] is not None and prev["physical_progress"] is not None:
                    obs["progress_change"] = round(float(obs["physical_progress"]) - float(prev["physical_progress"]), 2)
                    
                if obs["expenditure"] is not None and prev["expenditure"] is not None:
                    obs["expenditure_change"] = round(float(obs["expenditure"]) - float(prev["expenditure"]), 2)
                    
                if obs["schedule_extension_months"] is not None and prev["schedule_extension_months"] is not None:
                    obs["schedule_extension_change"] = float(obs["schedule_extension_months"]) - float(prev["schedule_extension_months"])
                    
            observations.append(obs)
            
        analytics = trend_analyzer.analyze_history(observations)
            
        return {
            "project_code": project_code,
            "observation_count": len(observations),
            "observations": observations,
            "analytics": analytics
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics")
def get_analytics():
    """
    Returns aggregate statistics for the Analytics dashboard.
    """
    if not CSV_PATH.exists():
        raise HTTPException(status_code=500, detail="Dataset not found")
        
    try:
        df = pd.read_csv(CSV_PATH)
        
        # 1. Physical Progress Categories
        # Use dynamic computation with strict < 25 boundary for Low Progress
        progress = df['physical_progress']
        progress_counts = {
            "Very High": int((progress >= 75).sum()),
            "High": int(((progress >= 50) & (progress < 75)).sum()),
            "Moderate": int(((progress >= 25) & (progress < 50)).sum()),
            "Low": int((progress < 25).sum())
        }
        
        # 2. Schedule Extension Categories
        ext = df['schedule_extension_months']
        schedule_ext_cats = {
            "Earlier Revised Completion": int((ext < 0).sum()),
            "No recorded extension": int((ext == 0).sum()),
            "1-12 months": int(((ext > 0) & (ext <= 12)).sum()),
            "13-24 months": int(((ext > 12) & (ext <= 24)).sum()),
            "Above 24 months": int((ext > 24).sum()),
            "Unavailable": int(ext.isna().sum())
        }
        
        # 3. Top 10 States
        top_states = df['state'].value_counts().head(10).to_dict()
        
        # 4. Monitoring Classification Counts
        monitoring_counts = {
            "Schedule Extension Recorded": int((ext > 0).sum()),
            "No Recorded Extension": int((ext == 0).sum()),
            "Earlier Revised Completion": int((ext < 0).sum()),
            "Schedule Data Unavailable": int(ext.isna().sum())
        }
        
        return {
            "progress_categories": progress_counts,
            "schedule_extensions": schedule_ext_cats,
            "top_states": top_states,
            "monitoring_classifications": monitoring_counts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-preview")
async def upload_preview(file: UploadFile = File(...)):
    """
    Validates uploaded CSV file without applying changes.
    Returns preview and any validation errors.
    """
    try:
        # Save temp file
        with open(TEMP_CSV, "wb") as f:
            f.write(await file.read())
            
        try:
            df = pd.read_csv(TEMP_CSV)
        except Exception:
            if TEMP_CSV.exists(): os.remove(TEMP_CSV)
            return {"valid": False, "errors": ["File is not a valid CSV."]}
            
        required_cols = ['project_code', 'state', 'physical_progress', 'schedule_monitoring_class', 'monitoring_explanation']
        missing_cols = [c for c in required_cols if c not in df.columns]
        if missing_cols:
            if TEMP_CSV.exists(): os.remove(TEMP_CSV)
            return {"valid": False, "errors": [f"Missing required columns: {', '.join(missing_cols)}"]}
            
        errors = []
        
        # Check project_code is numeric
        if not pd.api.types.is_numeric_dtype(df['project_code']):
            errors.append("Column 'project_code' must be numeric.")
            
        # Check project_code uniqueness
        if df['project_code'].duplicated().any():
            errors.append("Column 'project_code' contains duplicate values.")
            
        # Check physical progress range if numeric
        if pd.api.types.is_numeric_dtype(df['physical_progress']):
            if df['physical_progress'].min() < 0 or df['physical_progress'].max() > 100:
                errors.append("Column 'physical_progress' must be between 0 and 100.")
        else:
            errors.append("Column 'physical_progress' must be numeric.")
            
        if errors:
            if TEMP_CSV.exists(): os.remove(TEMP_CSV)
            return {"valid": False, "errors": errors}
            
        # Select first 5 rows for preview
        # Cast to object first to prevent pandas from coercing None back to NaN in numeric columns
        preview_df = df.head(5).astype(object).where(pd.notnull(df.head(5)), None)
        
        return {
            "valid": True,
            "preview": preview_df.to_dict(orient="records"),
            "record_count": len(df),
            "filename": file.filename
        }
    except Exception as e:
        if TEMP_CSV.exists(): os.remove(TEMP_CSV)
        return {"valid": False, "errors": [str(e)]}

@app.post("/upload-confirm")
def upload_confirm(filename: str):
    """
    Confirms the upload, merges the data, and records history.
    """
    if not TEMP_CSV.exists():
        raise HTTPException(status_code=400, detail="No temporary upload found to confirm.")
        
    try:
        try:
            new_df = pd.read_csv(TEMP_CSV)
        except Exception:
            os.remove(TEMP_CSV)
            raise HTTPException(status_code=400, detail="Temporary file is not a valid CSV.")
            
        # Re-validate structure
        required_cols = ['project_code', 'state', 'physical_progress', 'schedule_monitoring_class', 'monitoring_explanation']
        missing_cols = [c for c in required_cols if c not in new_df.columns]
        if missing_cols:
            os.remove(TEMP_CSV)
            raise HTTPException(status_code=400, detail=f"Missing required columns: {', '.join(missing_cols)}")
            
        if not pd.api.types.is_numeric_dtype(new_df['project_code']):
            os.remove(TEMP_CSV)
            raise HTTPException(status_code=400, detail="Column 'project_code' must be numeric.")
            
        if new_df['project_code'].duplicated().any():
            os.remove(TEMP_CSV)
            raise HTTPException(status_code=400, detail="Uploaded dataset contains duplicate project codes.")
            
        existing_df = pd.read_csv(CSV_PATH) if CSV_PATH.exists() else pd.DataFrame()
        
        if not existing_df.empty and existing_df['project_code'].duplicated().any():
            os.remove(TEMP_CSV)
            raise HTTPException(status_code=500, detail="Existing dataset contains duplicate project codes. Cannot safely perform upsert.")
        
        # Merge by project_code (Upsert)
        if not existing_df.empty:
            # Set project_code as index
            existing_df.set_index('project_code', inplace=True)
            new_df.set_index('project_code', inplace=True)
            
            # Update existing and append new
            existing_df.update(new_df)
            
            # Get new records
            new_records = new_df[~new_df.index.isin(existing_df.index)]
            if not new_records.empty:
                combined_df = pd.concat([existing_df, new_records])
            else:
                combined_df = existing_df
            
            # Reset index
            combined_df.reset_index(inplace=True)
        else:
            combined_df = new_df
            
        # Save back safely using a temporary file
        TMP_CSV_PATH = CSV_PATH.with_suffix('.tmp')
        combined_df.to_csv(TMP_CSV_PATH, index=False)
        
        # Log history
        history_record = {
            "filename": filename,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "record_count": len(new_df),
            "status": "Success"
        }
        
        history_df = pd.DataFrame([history_record])
        TMP_HISTORY = HISTORY_CSV.with_suffix('.tmp')
        
        if HISTORY_CSV.exists():
            existing_hist = pd.read_csv(HISTORY_CSV)
            new_hist = pd.concat([existing_hist, history_df])
            new_hist.to_csv(TMP_HISTORY, index=False)
        else:
            history_df.to_csv(TMP_HISTORY, index=False)
            
        # Atomic replace
        os.replace(TMP_CSV_PATH, CSV_PATH)
        os.replace(TMP_HISTORY, HISTORY_CSV)
        
        # Clean up
        os.remove(TEMP_CSV)
        
        return {"success": True, "message": "Dataset successfully updated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data/history")
def get_import_history():
    """Returns import history."""
    if not HISTORY_CSV.exists():
        return []
    try:
        df = pd.read_csv(HISTORY_CSV)
        return df.to_dict(orient="records")
    except Exception:
        return []

@app.post("/history/upload-preview")
def history_upload_preview(file: UploadFile = File(...)):
    """
    Validates a historical upload. Stages valid files.
    """
    if not file.filename.endswith('.csv'):
        return {"valid": False, "errors": [{"row": 0, "msg": "File must be a CSV."}]}
        
    try:
        df = pd.read_csv(file.file)
        
        required_cols = ['project_code', 'report_month']
        missing_cols = [c for c in required_cols if c not in df.columns]
        if missing_cols:
            return {"valid": False, "errors": [{"row": 0, "msg": f"Missing required columns: {', '.join(missing_cols)}"}]}
            
        # Get operational dataset
        op_df = pd.read_csv(CSV_PATH) if CSV_PATH.exists() else pd.DataFrame()
        valid_project_codes = set(op_df['project_code'].astype(str)) if not op_df.empty else set()
        
        errors = []
        valid_rows = []
        
        # Track duplicate project-month keys within the file
        seen_keys = set()
        
        # Numeric columns to validate
        numeric_cols = ['physical_progress', 'expenditure', 'original_cost_crore', 'revised_cost_crore', 'schedule_extension_months']
        
        for idx, row in df.iterrows():
            row_num = idx + 2 # Header is line 1, idx is 0-based
            row_dict = row.to_dict()
            
            raw_code = row_dict.get('project_code')
            raw_month = row_dict.get('report_month')
            
            if pd.isna(raw_code) or str(raw_code).strip() == "":
                errors.append({"row": row_num, "msg": "Missing project_code."})
                continue
            
            if pd.isna(raw_month) or str(raw_month).strip() == "":
                errors.append({"row": row_num, "msg": "Missing report_month."})
                continue
                
            code_str = str(raw_code).strip()
            if code_str not in valid_project_codes:
                errors.append({"row": row_num, "msg": f"Unknown project_code {code_str}. Project does not exist in operational dataset."})
                continue
                
            try:
                norm_month = pd.to_datetime(str(raw_month)).strftime("%Y-%m")
                row_dict['report_month'] = norm_month
            except Exception:
                errors.append({"row": row_num, "msg": f"Invalid report_month format: {raw_month}."})
                continue
                
            key = f"{code_str}_{norm_month}"
            if key in seen_keys:
                errors.append({"row": row_num, "msg": f"Duplicate entry for project {code_str} and month {norm_month} within the file."})
                continue
            seen_keys.add(key)
            
            # Numeric validation
            row_valid = True
            for col in numeric_cols:
                if col in row_dict and not pd.isna(row_dict[col]):
                    try:
                        val = float(row_dict[col])
                        # Handle specific ranges if needed, else just type validation
                        if col == 'physical_progress' and not (0 <= val <= 100):
                            errors.append({"row": row_num, "msg": f"physical_progress must be between 0 and 100. Got {val}."})
                            row_valid = False
                    except ValueError:
                        errors.append({"row": row_num, "msg": f"Invalid numeric value for {col}."})
                        row_valid = False
            
            if row_valid:
                # Replace NaNs with None for JSON serialization
                clean_dict = {k: (v if pd.notna(v) else None) for k, v in row_dict.items()}
                valid_rows.append(clean_dict)
                
        if errors:
            return {
                "valid": False,
                "errors": errors,
                "valid_count": len(valid_rows),
                "invalid_count": len(errors)
            }
            
        staging_id = str(uuid.uuid4())
        staging_file = HISTORY_STAGING_DIR / f"{staging_id}.json"
        
        with open(staging_file, "w") as f:
            json.dump(valid_rows, f)
            
        return {
            "valid": True,
            "staging_id": staging_id,
            "valid_count": len(valid_rows),
            "invalid_count": 0,
            "preview": valid_rows[:5]
        }
    except Exception as e:
        return {"valid": False, "errors": [{"row": 0, "msg": f"Error parsing file: {str(e)}"}]}

@app.post("/history/upload-confirm")
def history_upload_confirm(staging_id: str):
    """
    Commits a staged historical upload.
    """
    if not staging_id or not staging_id.isalnum() and '-' not in staging_id:
         raise HTTPException(status_code=400, detail="Invalid staging ID.")
         
    staging_file = HISTORY_STAGING_DIR / f"{staging_id}.json"
    
    if not staging_file.exists():
        raise HTTPException(status_code=400, detail="Staging file expired, missing, or already consumed.")
        
    try:
        with open(staging_file, "r") as f:
            records = json.load(f)
            
        res = historical_store.append_snapshots(records)
        
        # Clean up
        os.remove(staging_file)
        
        return {
            "success": True, 
            "inserted": res.get("inserted", 0), 
            "updated": res.get("updated", 0),
            "total_processed": len(records)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)

