from app.services.analytics import compute_crowding, compute_summary, compute_trend, occupancy_rate


def test_occupancy_rate():
    assert occupancy_rate(80, 200) == 40.0
    assert occupancy_rate(None, 200) is None


def test_summary_counts():
    records = [
        {"hospital_name": "A", "occupied_beds": 80, "total_beds": 200, "reporting_timestamp": "2025-01-01", "reporting_period": "2025-Q1"},
        {"hospital_name": "B", "occupied_beds": 150, "total_beds": 180, "reporting_timestamp": "2025-01-02", "reporting_period": "2025-Q1"},
    ]
    summary = compute_summary(records)
    assert summary["total_hospitals"] == 2
    assert summary["average_occupancy"] is not None


def test_crowding_threshold():
    records = [{"hospital_name": "A", "occupied_beds": 180, "total_beds": 200, "reporting_period": "2025-Q1"}]
    crowding = compute_crowding(records, threshold=75)
    assert crowding["flagged_hospitals"][0]["hospital_name"] == "A"


def test_trend_generation():
    records = [{"hospital_name": "A", "reporting_period": "2025-Q1", "occupied_beds": 50, "total_beds": 100}]
    trend = compute_trend(records)
    assert trend[0]["occupancy_rate"] == 50.0


def test_insufficient_data_case():
    assert occupancy_rate(10, 0) is None
