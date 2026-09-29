import sys
import os
import math

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.historical_analytics import HistoricalTrendAnalyzer

def run_tests():
    analyzer = HistoricalTrendAnalyzer()
    
    print("Test 1: Zero observations")
    res = analyzer.analyze_history([])
    assert res["status"] == "Insufficient Data"
    print("PASS")
    
    print("Test 2: One observation")
    res = analyzer.analyze_history([{"report_month": "2026-08", "physical_progress": 10}])
    assert res["status"] == "Insufficient Data"
    print("PASS")
    
    print("Test 3: Two chronological observations")
    data = [
        {"report_month": "2026-08", "physical_progress": 10, "expenditure": 100, "schedule_extension_months": 0},
        {"report_month": "2026-09", "physical_progress": 20, "expenditure": 110, "schedule_extension_months": 2}
    ]
    res = analyzer.analyze_history(data)
    metrics = res["metrics"]
    assert metrics["progress_change"] == 10.0
    assert metrics["expenditure_change_crore"] == 10.0
    assert metrics["expenditure_change_pct"] == 10.0
    assert metrics["schedule_extension_change"] == 2.0
    assert metrics["trend_indicator"] == "Active Progress"
    assert metrics["risk_movement"] == "Recovering" # progress > 5 overrides escalated
    print("PASS")
    
    print("Test 4: Out-of-order observations")
    data = [
        {"report_month": "2026-10", "physical_progress": 30, "expenditure": 120},
        {"report_month": "2026-09", "physical_progress": 20, "expenditure": 110}
    ]
    res = analyzer.analyze_history(data)
    assert res["metrics"]["period_start"] == "2026-09"
    assert res["metrics"]["period_end"] == "2026-10"
    assert res["metrics"]["progress_change"] == 10.0
    print("PASS")
    
    print("Test 5: Missing progress or expenditure")
    data = [
        {"report_month": "2026-08", "physical_progress": None, "expenditure": 100},
        {"report_month": "2026-09", "physical_progress": 20, "expenditure": None}
    ]
    res = analyzer.analyze_history(data)
    assert res["metrics"]["progress_change"] is None
    assert res["metrics"]["expenditure_change_crore"] is None
    print("PASS")
    
    print("Test 6: Previous expenditure equal to zero")
    data = [
        {"report_month": "2026-08", "physical_progress": 10, "expenditure": 0.0},
        {"report_month": "2026-09", "physical_progress": 10, "expenditure": 10.0}
    ]
    res = analyzer.analyze_history(data)
    assert res["metrics"]["expenditure_change_crore"] == 10.0
    assert res["metrics"]["expenditure_change_pct"] is None
    assert res["metrics"]["trend_indicator"] == "Stagnant Progress"
    print("PASS")
    
    print("Test 7: Missing schedule extension")
    data = [
        {"report_month": "2026-08", "schedule_extension_months": None},
        {"report_month": "2026-09", "schedule_extension_months": 5}
    ]
    res = analyzer.analyze_history(data)
    assert res["metrics"]["schedule_extension_change"] is None
    print("PASS")
    
    print("Test 8: Multiple months with changing values")
    data = [
        {"report_month": "2026-01", "physical_progress": 10, "expenditure": 50},
        {"report_month": "2026-02", "physical_progress": 15, "expenditure": 60},
        {"report_month": "2026-03", "physical_progress": 15, "expenditure": 70}, # Stagnant, high burn
    ]
    res = analyzer.analyze_history(data)
    assert res["metrics"]["period_start"] == "2026-02"
    assert res["metrics"]["period_end"] == "2026-03"
    assert res["metrics"]["progress_change"] == 0.0
    assert res["metrics"]["trend_indicator"] == "High Cash Burn"
    print("PASS")
    
    print("Test 9: Invalid or malformed records")
    data = [
        {"report_month": "2026-01", "physical_progress": "abc", "expenditure": 50},
        {"report_month": "2026-02", "physical_progress": float('nan'), "expenditure": 60}
    ]
    res = analyzer.analyze_history(data)
    assert res["metrics"]["progress_change"] is None
    print("PASS")

    print("\nAll tests passed successfully!")

if __name__ == "__main__":
    run_tests()
