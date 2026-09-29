# PAIMANA Intelligence — Predictive Feasibility and Dataset Audit

## 1. Dataset Facts
- **Size**: 1,731 rows (unique project records), 25 columns.
- **Data Structure**: The dataset is a **single cross-sectional snapshot**. There are no multiple dated observations (longitudinal history) for the same projects.
- **Physical Progress**: Present for all 1,731 records (0 missing values).
- **Schedule Extensions**: 303 records (17.5%) are missing `revised_completion_date` and consequently `schedule_extension_months`. There are 27 projects with negative schedule extensions.
- **Cost Data**: The `revised_cost_crore` column is constant (`0.0` for all 1,731 rows).
- **Extreme Values**: `expenditure_to_original_cost_pct` contains extreme outliers, reaching up to 10,623% due to likely OCR/reporting artifacts.

## 2. Candidate Target Feasibility Table

| Candidate Target | Definition | Available Fields | Feasibility & Future Prediction |
| :--- | :--- | :--- | :--- |
| **Future schedule delay** | Predicting a delay that will happen *in the future*. | None (requires historical snapshots). | **NOT FEASIBLE.** We lack time-series data to train on past states predicting future states. |
| **Schedule extension** | The mathematical difference between original and revised completion dates. | `schedule_extension_months` | **NOT FEASIBLE FOR FUTURE PREDICTION.** It is a current historical outcome. We can use it as a target for *cross-sectional imputation* (estimating missing values based on progress), but it is not predicting the future. |
| **Low physical progress** | Categorical flag for physical progress < 25%. | `low_progress_flag`, `physical_progress` | **NOT FEASIBLE.** This is a deterministically derived rule, not an unknown target. Modeling it would be tautological. |
| **Expenditure above original cost** | Binary flag for expenditure > original cost. | `expenditure_above_original_cost` | **NOT FEASIBLE.** It is deterministically derived from current expenditure and original cost. |

## 3. Leakage Risks
If any modeling is attempted (e.g., inferring missing schedule extensions), the following features pose severe target leakage risks:
- **Heuristic Flags**: `schedule_monitoring_class`, `progress_category`, `monitoring_attention`, and `schedule_extension_flag`. These are rule-based derivations engineered directly from the targets. Including them in a feature matrix would result in artificial 100% accuracy.
- **Identifiers**: `project_code` and `serial_number` are arbitrary identifiers and must be dropped to prevent the model from memorizing the dataset.

## 4. Data Limitations
- **Zero-Variance Feature**: `revised_cost_crore` is entirely populated with zeros. It provides zero signal and cannot be used for cost-overrun prediction.
- **Lack of Temporal Dynamics**: Without monthly snapshots (e.g., month $T$ progress predicting month $T+6$ delay), supervised forecasting of future outcomes is impossible. 
- **Missing Ground Truth**: The dataset lacks true "project failure" or "abandonment" labels.

## 5. Recommended First Modelling Experiment
Since future prediction is impossible, the most defensible first experiment is a **cross-sectional imputation model**.
- **Objective**: Infer the missing `schedule_extension_months` for the 303 projects where `revised_completion_date` is unavailable.
- **Features**: `physical_progress`, `expenditure_to_original_cost_pct` (capped to handle extreme outliers), and `state` (categorical).
- **Models**: Start with a simple **Statistical Baseline** (e.g., median imputation by state/progress bucket) before attempting a lightweight **Random Forest Regressor** to capture non-linear relationships between expenditure ratios and delays.
- **Validation**: Random train/test split (80/20) on the 1,428 records that *do* have schedule extensions, using MAE (Mean Absolute Error) as the evaluation metric.

## 6. Explicit Go/No-Go Recommendation
**NO-GO for genuine predictive ML forecasting.**
Because the dataset is a single cross-sectional snapshot rather than a longitudinal history, it mathematically cannot support a model predicting future delays. Any model trained on this dataset can only perform inference/imputation on current missing data, not future prediction. 

Rule-based expert systems (like the current Risk Engine v1) remain the most transparent and scientifically sound approach until monthly historical snapshots are acquired.
