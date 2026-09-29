# PAIMANA Intelligence — Monthly Ingestion Architecture Audit (Task PI-ML-05)

## 1. Current Architecture
- **Historical Store**: `app/historical_store.py` manages a localized CSV at `data/historical/historical_snapshots.csv`. It supports atomic append operations (`append_snapshots(records)`), using `project_code` and `report_month` as a unique composite key.
- **Data Validation**: Currently, `historical_store.py` independently verifies the presence of `project_code` and `report_month`. It employs `pd.to_datetime` to strongly normalize `report_month` to `YYYY-MM`.
- **Operational Upload**: The existing UI in `Data Management` securely uploads, previews, and confirms *operational* datasets (`schedule_monitoring.csv`), utilizing a temporary staging file (`temp_upload.csv`).

## 2. Reusable Components
- **File Upload Mechanics**: The FastAPI `UploadFile` routing and standard Pandas CSV parsing patterns from `app/main.py` are highly reusable.
- **Atomic Operations**: The `os.replace` mechanism in `historical_store.py` safely prevents corrupted file states during imports.
- **Frontend Container**: The existing "Data Management View" inside `frontend/index.html` possesses the exact CSS, layouts, and loading states needed for a specialized "Historical Data Import" block.

## 3. Identified Gaps
A. **Project Code Validation**: `historical_store.py` does not currently check if a `project_code` actively exists in the operational `schedule_monitoring.csv` dataset before storing it.
B. **No History Preview API**: The existing operational upload endpoints (`/upload-preview`, `/upload-confirm`) are hardcoded to the operational dataset. The historical store has no endpoints for staging or previewing an import before committing it to disk.
C. **Operational and Historical Collision**: The existing upload endpoints cannot handle historical columns (like `report_month`) and would overwrite the main dataset if reused directly.

## 4. Proposed Minimal Implementation Plan
To implement a safe historical ingestion workflow:
1. **Backend Endpoints**: 
   - Add `POST /history/upload-preview`: Accepts a CSV, validates required columns (`project_code`, `report_month`), checks `project_code` against `schedule_monitoring.csv`, and saves it to a new `data/processed/temp_history_upload.csv`. Returns valid/invalid counts and a preview slice.
   - Add `POST /history/upload-confirm`: Reads the temporary file, converts it to a dictionary, passes it to `historical_store.append_snapshots()`, and returns the exact number of rows inserted/updated.
2. **Frontend Additions**:
   - Add a distinct "Historical Snapshots Upload" card in the Data Management UI inside `index.html`. 
   - Wire standard JavaScript fetch handlers for the two new history endpoints without modifying the operational upload logic.

## 5. Suggested Test Cases
1. **Valid historical import**: A standard CSV with known project codes properly validating and confirming.
2. **Missing required columns**: Reject files lacking `report_month` or `project_code`.
3. **Unknown project codes**: The preview API should explicitly flag rows containing project codes that don't exist in the operational dataset.
4. **Idempotent month updates**: Ensure uploading identical files twice accurately yields `updated: N, inserted: 0`.

## 6. Risks and Safeguards
- **Risk**: A user accidentally uploads the operational baseline CSV into the historical importer.
  - **Safeguard**: The historical preview API must enforce a strict check that `report_month` is a column. If missing, it immediately rejects the file.
- **Risk**: Temporary file collisions if multiple users upload history concurrently.
  - **Safeguard**: FastAPI blocks synchronously for simple file streams, but ideally, using unique temporary file IDs (e.g. `uuid`) prevents race conditions. For this prototype, `temp_history_upload.csv` is an acceptable minimal solution.
