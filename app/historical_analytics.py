import math
from typing import List, Dict, Any, Optional

class HistoricalTrendAnalyzer:
    """
    Analyzes historical records and calculates month-over-month deltas and deterministic risk trends.
    """
    
    @staticmethod
    def _is_valid_numeric(val: Any) -> bool:
        if val is None:
            return False
        try:
            fval = float(val)
            return not math.isnan(fval)
        except (ValueError, TypeError):
            return False

    def analyze_history(self, history_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not history_records or len(history_records) < 2:
            return {
                "status": "Insufficient Data",
                "message": "At least two chronological observations are required to compute trends.",
                "metrics": None
            }

        # Filter out records without valid report_month
        valid_records = []
        for r in history_records:
            if r.get('report_month') and isinstance(r['report_month'], str):
                valid_records.append(r)

        if len(valid_records) < 2:
            return {
                "status": "Insufficient Data",
                "message": "At least two chronological observations are required to compute trends.",
                "metrics": None
            }

        # Sort chronologically by report_month
        sorted_records = sorted(valid_records, key=lambda x: x['report_month'])

        # Get latest and previous
        latest = sorted_records[-1]
        previous = sorted_records[-2]

        metrics = {
            "period_start": previous['report_month'],
            "period_end": latest['report_month'],
            "progress_change": None,
            "expenditure_change_crore": None,
            "expenditure_change_pct": None,
            "schedule_extension_change": None,
            "trend_indicator": "Unknown",
            "risk_movement": "Stable"
        }

        # Progress
        if self._is_valid_numeric(latest.get('physical_progress')) and self._is_valid_numeric(previous.get('physical_progress')):
            metrics["progress_change"] = round(float(latest['physical_progress']) - float(previous['physical_progress']), 2)

        # Expenditure
        if self._is_valid_numeric(latest.get('expenditure')) and self._is_valid_numeric(previous.get('expenditure')):
            exp_latest = float(latest['expenditure'])
            exp_prev = float(previous['expenditure'])
            metrics["expenditure_change_crore"] = round(exp_latest - exp_prev, 2)
            if exp_prev != 0.0:
                metrics["expenditure_change_pct"] = round(((exp_latest - exp_prev) / exp_prev) * 100, 2)

        # Schedule Extension
        if self._is_valid_numeric(latest.get('schedule_extension_months')) and self._is_valid_numeric(previous.get('schedule_extension_months')):
            metrics["schedule_extension_change"] = round(float(latest['schedule_extension_months']) - float(previous['schedule_extension_months']), 2)

        # Project Trend Indicators
        trend = "Stable"
        if metrics["progress_change"] is not None:
            if metrics["progress_change"] <= 0.0:
                trend = "Stagnant Progress"
            else:
                trend = "Active Progress"
                
            if metrics["expenditure_change_pct"] is not None:
                if metrics["expenditure_change_pct"] > 5.0 and metrics["progress_change"] <= 1.0:
                    trend = "High Cash Burn"

        metrics["trend_indicator"] = trend

        # Risk Movement
        risk_mov = "Stable"
        if metrics["schedule_extension_change"] is not None:
            if metrics["schedule_extension_change"] > 0:
                risk_mov = "Escalated"
            elif metrics["schedule_extension_change"] < 0:
                risk_mov = "Recovering"
        
        if metrics["progress_change"] is not None and metrics["progress_change"] > 5.0:
             risk_mov = "Recovering"

        metrics["risk_movement"] = risk_mov

        return {
            "status": "Success",
            "message": "Analytics generated successfully.",
            "metrics": metrics
        }
