"""
API integration tests for POST /api/predict.
Requires Flask server running at http://127.0.0.1:5000
"""
import requests
import pytest

BASE = "http://127.0.0.1:5000"

GOOD_PAYLOAD = {
    "student_name": "Test Student API",
    "cgpa": 8.5,
    "attendance": 90.0,
    "quiz_score": 8.0,
    "backlogs": 0,
    "entrance_score": 7.5,
    "study_hours": 5.0,
    "lms_usage": 4,
    "class_participation": 4,
    "extra_activities": 3.0,
    "study_style": 1,
    "sleep_hours": 7.0,
    "screen_time": 3.0,
    "stress_level": 2,
    "procrastination": 2,
    "health_status": 3,
}

AT_RISK_PAYLOAD = {
    "student_name": "At Risk Student",
    "cgpa": 3.0,
    "attendance": 55.0,
    "quiz_score": 2.0,
    "backlogs": 4,
    "entrance_score": 2.0,
    "study_hours": 1.0,
    "lms_usage": 1,
    "class_participation": 1,
    "extra_activities": 0.0,
    "study_style": 0,
    "sleep_hours": 5.0,
    "screen_time": 7.0,
    "stress_level": 5,
    "procrastination": 5,
    "health_status": 1,
}


def test_health_endpoint():
    r = requests.get(f"{BASE}/api/health", timeout=5)
    assert r.status_code == 200
    assert r.json()["status"] == "success"


def test_predict_success_status():
    r = requests.post(f"{BASE}/api/predict", json=GOOD_PAYLOAD, timeout=15)
    assert r.status_code == 200
    assert r.json()["status"] == "success"


def test_predict_response_keys():
    r = requests.post(f"{BASE}/api/predict", json=GOOD_PAYLOAD, timeout=15)
    body = r.json()
    assert "prediction" in body
    pred = body["prediction"]
    for key in ("predicted_grade", "performance_level", "model_name", "top_factors", "outcomes"):
        assert key in pred


def test_predict_grade_range():
    r = requests.post(f"{BASE}/api/predict", json=GOOD_PAYLOAD, timeout=15)
    grade = r.json()["prediction"]["predicted_grade"]
    assert 0 <= grade <= 20


def test_predict_top_factors_count():
    r = requests.post(f"{BASE}/api/predict", json=GOOD_PAYLOAD, timeout=15)
    assert len(r.json()["prediction"]["top_factors"]) == 5


def test_predict_outcomes_present():
    r = requests.post(f"{BASE}/api/predict", json=GOOD_PAYLOAD, timeout=15)
    outcomes = r.json()["prediction"]["outcomes"]
    assert "dropout_risk" in outcomes
    assert "placement_readiness" in outcomes
    assert "remedial_needs" in outcomes


def test_predict_good_student_low_risk():
    r = requests.post(f"{BASE}/api/predict", json=GOOD_PAYLOAD, timeout=15)
    assert r.json()["prediction"]["outcomes"]["dropout_risk"] == "Low"


def test_predict_at_risk_student():
    r = requests.post(f"{BASE}/api/predict", json=AT_RISK_PAYLOAD, timeout=15)
    assert r.status_code == 200
    pred = r.json()["prediction"]
    assert pred["predicted_grade"] < 13.0
    assert pred["outcomes"]["dropout_risk"] in ("High", "Moderate")


def test_predict_missing_field_returns_400():
    bad = {k: v for k, v in GOOD_PAYLOAD.items() if k != "cgpa"}
    r = requests.post(f"{BASE}/api/predict", json=bad, timeout=15)
    assert r.status_code == 400
    assert r.json()["status"] == "error"


def test_predict_out_of_range_returns_400():
    bad = {**GOOD_PAYLOAD, "cgpa": 15.0}
    r = requests.post(f"{BASE}/api/predict", json=bad, timeout=15)
    assert r.status_code == 400
