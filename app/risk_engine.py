import math
import json

class ProjectRiskAssessor:
    """
    A transparent, explainable, rule-based expert system for assessing project risk dimensions.
    This is not a machine learning model and does not output predictive scores or arbitrary overall ratings.
    """
    
    def __init__(self, unusual_expenditure_threshold: float = 500.0):
        self.unusual_expenditure_threshold = unusual_expenditure_threshold
        self.limitations_statement = (
            "This assessment is a deterministic, rule-based expert system. "
            "It generates monitoring indicators based solely on reported data fields. "
            "It is not a machine learning prediction, does not calculate absolute failure probabilities, "
            "and does not represent official audits or verified cost-overrun determinations."
        )

    def _is_valid_number(self, val):
        if val is None:
            return False
        try:
            f_val = float(val)
            if math.isnan(f_val) or math.isinf(f_val):
                return False
            return True
        except (ValueError, TypeError):
            return False

    def assess_project(self, record: dict) -> dict:
        project_code = record.get('project_code')
        
        # Safe extraction
        raw_schedule = record.get('schedule_extension_months')
        raw_finance = record.get('expenditure_to_original_cost_pct')
        raw_progress = record.get('physical_progress')
        
        schedule = float(raw_schedule) if self._is_valid_number(raw_schedule) else None
        finance = float(raw_finance) if self._is_valid_number(raw_finance) else None
        progress = float(raw_progress) if self._is_valid_number(raw_progress) else None

        warnings = []
        evidence = []
        
        # 1. Schedule Assessment
        if schedule is None:
            schedule_assessment = "Schedule Data Unavailable"
            warnings.append("Missing schedule extension data.")
        elif schedule > 0:
            schedule_assessment = "Schedule Extension Recorded"
            evidence.append(f"A schedule extension of {schedule} months is recorded.")
        elif schedule == 0:
            schedule_assessment = "No Recorded Extension"
            evidence.append("No schedule extension is recorded.")
        else: # schedule < 0
            schedule_assessment = "Earlier Revised Completion"
            warnings.append("Negative schedule extension detected.")
            evidence.append(f"Revised completion is {abs(schedule)} months earlier than original.")

        # 2. Financial Monitoring
        if finance is None:
            financial_assessment = "Financial Data Unavailable"
            warnings.append("Missing or invalid financial data (expenditure ratio).")
        elif finance > 100:
            financial_assessment = "Expenditure Above Original Cost"
            evidence.append(f"Expenditure is {finance}% of the original cost.")
        elif 80 <= finance <= 100:
            financial_assessment = "Elevated Expenditure Ratio"
            evidence.append(f"Expenditure has reached {finance}% of the original cost.")
        else:
            financial_assessment = "No threshold flag under this rule"
            
        # Data Quality warning for extreme finance
        if finance is not None and finance > self.unusual_expenditure_threshold:
            warnings.append(f"Unusually high expenditure ratio recorded (> {self.unusual_expenditure_threshold}%).")

        # 3. Physical Progress
        if progress is None:
            progress_assessment = "Progress Data Unavailable"
            warnings.append("Missing or invalid physical progress data.")
        elif progress < 25:
            progress_assessment = "Low Reported Physical Progress"
            evidence.append(f"Reported physical progress is {progress}%.")
        else:
            progress_assessment = "No low-progress flag under this rule"

        # 4. Cross-dimensional indicator
        execution_indicator = None
        if progress is not None and finance is not None:
            if progress < 25 and finance > 50:
                execution_indicator = "Low Progress with Elevated Expenditure Ratio"
                evidence.append("Cross-dimensional flag triggered: Physical progress is below 25% while expenditure ratio exceeds 50%.")

        return {
            "project_code": project_code if self._is_valid_number(project_code) else None,
            "schedule_assessment": schedule_assessment,
            "financial_assessment": financial_assessment,
            "progress_assessment": progress_assessment,
            "execution_indicator": execution_indicator,
            "data_quality_warnings": warnings,
            "evidence": evidence,
            "limitations": self.limitations_statement
        }

if __name__ == "__main__":
    assessor = ProjectRiskAssessor()
    
    tests = [
        {
            "desc": "Normal project",
            "data": {"project_code": 1, "schedule_extension_months": 0, "expenditure_to_original_cost_pct": 50, "physical_progress": 60}
        },
        {
            "desc": "Missing schedule extension",
            "data": {"project_code": 2, "schedule_extension_months": float('nan'), "expenditure_to_original_cost_pct": 40, "physical_progress": 50}
        },
        {
            "desc": "Negative extension",
            "data": {"project_code": 3, "schedule_extension_months": -5, "expenditure_to_original_cost_pct": 30, "physical_progress": 90}
        },
        {
            "desc": "Expenditure above original cost",
            "data": {"project_code": 4, "schedule_extension_months": 12, "expenditure_to_original_cost_pct": 110, "physical_progress": 80}
        },
        {
            "desc": "Low progress with elevated expenditure",
            "data": {"project_code": 5, "schedule_extension_months": 24, "expenditure_to_original_cost_pct": 60, "physical_progress": 15}
        },
        {
            "desc": "NaN and infinity",
            "data": {"project_code": 6, "schedule_extension_months": float('nan'), "expenditure_to_original_cost_pct": float('inf'), "physical_progress": None}
        },
        {
            "desc": "Extreme expenditure ratio data warning",
            "data": {"project_code": 7, "schedule_extension_months": 0, "expenditure_to_original_cost_pct": 600, "physical_progress": 100}
        }
    ]
    
    print("--- Running Risk Engine v1 Core Tests ---\n")
    for t in tests:
        print(f"Test: {t['desc']}")
        result = assessor.assess_project(t['data'])
        print(json.dumps(result, indent=2))
        print("-" * 50)
