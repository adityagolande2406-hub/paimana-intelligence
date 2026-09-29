# PAIMANA Intelligence — Historical Analytics Design (Task PI-ML-06)

## 1. Proposed Architecture
The engine will be implemented as a standalone, deterministic Python module at `app/historical_analytics.py`. 
It will expose a `HistoricalTrendAnalyzer` class that accepts a chronologically sorted list of historical snapshot records for a single project. The engine will return a JSON-serializable dictionary containing calculated deltas, trend classifications, and risk momentum.
This module will be cleanly integrated into the existing `GET /projects/{project_code}/history` endpoint to enrich the API payload without altering the underlying data store or the `HistoricalStore` class.

## 2. Formulas and Metrics
### A. Month-over-Month (MoM) Physical Progress Change
- **Formula**: $Progress_{T} - Progress_{T-1}$ (Result in absolute percentage points).
- **Minimum Data**: At least two chronological snapshots with non-null `physical_progress`.

### B. Expenditure Change
- **Absolute Formula**: $Expenditure_{T} - Expenditure_{T-1}$ (in crores).
- **Percentage Formula**: $\frac{Expenditure_{T} - Expenditure_{T-1}}{Expenditure_{T-1}} \times 100$
- **Minimum Data**: At least two chronological snapshots with non-null `expenditure`.

### C. Schedule Extension Change
- **Formula**: $Extension_{T} - Extension_{T-1}$ (in months).
- **Minimum Data**: At least two snapshots with non-null `schedule_extension_months`.

### D. Project Trend Indicators (Deterministic Rules)
Derived strictly from the most recent two valid observations:
- **Stagnant Progress**: Physical progress change $\le 0.0$ over the observed period.
- **Active Progress**: Physical progress change $> 0.0$.
- **High Cash Burn**: Expenditure % change is disproportionately higher than the Physical Progress absolute change (e.g., spent 10% more money for 0% progress).

### E. Historical Risk Movement (No Predictive ML)
Instead of predicting future failure, this evaluates the *momentum* of risk:
- **Escalated**: Schedule extension increased ($Extension Change > 0$).
- **Stable**: Metrics remained identical or improved marginally.
- **Recovering**: Schedule extension decreased (time clawed back) or progress surged $> 5\%$ in a single reporting period.

## 3. Edge Cases & Safe Handling
- **Missing Values**: If any operand ($T$ or $T-1$) is `None` or `NaN`, the corresponding change metric safely evaluates to `None`. No artificial zeros are fabricated.
- **Zero Denominators**: In Expenditure % change, if $Expenditure_{T-1} == 0$, the formula will catch the `DivisionByZero` risk and return `None` (or a specific flag) to prevent generating non-serializable `inf` payloads.
- **Chronological Gaps**: If snapshots jump from August to October (skipping September), the delta is calculated between the *latest available* observations. The engine will explicitly label this as `period_gap_months = 2` rather than strictly `1`.
- **Single Observation**: If a project only has 1 historical snapshot, all trend indicators immediately short-circuit and return `None` or `"Insufficient Data"`.

## 4. Test Cases
The module will be validated via a dedicated test script (`scripts/test_historical_analytics.py`) using strictly isolated, hardcoded memory dictionaries:
1. **Perfect Sequence**: Two consecutive months with all fields populated. Verifies accurate delta math.
2. **Missing Operands**: One month has `null` expenditure. Verifies `expenditure_change` evaluates to `None` without crashing.
3. **Zero Denominator Protection**: $Expenditure_{T-1} = 0.0$, $Expenditure_{T} = 10.0$. Verifies safe handling.
4. **Out of Order Input**: Feeds December then August. Verifies the engine forces a chronological sort based on `report_month` before calculating deltas.
5. **Single Record**: Feeds one month. Verifies safe bypass returning "Insufficient Data".

## 5. Concise Implementation Plan
1. **Create Module**: Author `app/historical_analytics.py` containing the deterministic rules outlined above.
2. **Create Tests**: Author `scripts/test_historical_analytics.py` to assert edge cases using synthetic in-memory lists (no CSV interaction).
3. **Integrate**: Import the module into `app/main.py`. Pass the output of `HistoricalStore.get_project_history()` through the analyzer before returning the JSON payload in `/projects/{project_code}/history`.
4. **Deploy**: Verify that the frontend can gracefully read the enriched payload without breaking existing charts.

*(Awaiting approval to proceed with implementation).*
