# PAIMANA Intelligence — Historical Store Implementation (Task PI-ML-02)

## 1. Exact Files Created/Modified
- **Created**: `data/historical/` (Directory)
- **Created**: `app/historical_store.py` (Core module logic)
- **Created**: `scripts/test_historical_store.py` (Test script)
- **Created**: `reports/historical_store_implementation.md` (This report)

*(Note: No existing datasets, `app/main.py`, or frontend files were modified).*

## 2. Storage Format & Unique Key
- **Storage Format**: The module reads and writes securely using `pandas` and atomic `os.replace` to prevent race conditions or corrupted partial writes, maintaining the dataset as a standard CSV (`data/historical/historical_snapshots.csv`).
- **Unique Key**: The composite key is strictly `project_code` + `report_month`. 
- **Conflict Resolution (Upsert)**: When an identical `project_code` + `report_month` pair is uploaded, the script acts idempotently by overwriting/updating the old record with the new one. Different `report_month` values for the same project are safely appended as independent rows.

## 3. Test Results
The standalone synthetic test script (`scripts/test_historical_store.py`) successfully executed the following behaviors against a sandboxed `test_snapshots.csv`:
- **First snapshot insertion**: PASSED. Correctly inserted a new record for `2026-08`.
- **Second month insertion**: PASSED. Safely appended the `2026-09` record for the identical project.
- **Duplicate month rejection (Idempotent Update)**: PASSED. Safely dropped the older row and preserved the corrected values when identically keyed data was passed.
- **Missing value preservation**: PASSED. Explicitly verified that `NaN` and `None` fields remain mathematically empty instead of incorrectly defaulting to `0` or `0.0`.
- **Invalid project code handling**: PASSED. Missing `project_code` strings, empty strings (`"  "`), and `None` variables correctly trigger rejection protocols, increment the `rejected` counter, and yield documented error logs.

## 4. Limitations
- **Manual Implementation**: Currently, there is no UI element or scheduled cron-job triggering the historical store. Data must be supplied dynamically to the `append_snapshots(records)` method.
- **Report Month Format**: It trusts the uploading source to pass a consistently formatted string (e.g. `YYYY-MM`) for `report_month`. Malformed dates (e.g. `August 2026` vs `2026-08`) for the same project will not trigger the idempotent duplicate protection and will create two separate rows.
- **Empty Initialization**: As requested, this relies exclusively on the synthetic test suite. The `historical_snapshots.csv` has not yet been seeded with the actual 1,731 project records.
