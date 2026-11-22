"""
Unit tests for backend/predictor.py
Tests the 15-feature pipeline: validation, prediction output, ranges, and edge cases.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from backend.predictor import predict_student, FEATURES, FEATURE_LABELS, FEATURE_RANGES

GOOD_STUDENT = {
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

AT_RISK_STUDENT = {
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


def test_features_count():
    assert len(FEATURES) == 15


def test_feature_labels_complete():
    for f in FEATURES:
        assert f in FEATURE_LABELS, f"Missing label for '{f}'"


def test_feature_ranges_complete():
    for f in FEATURES:
        assert f in FEATURE_RANGES, f"Missing range for '{f}'"


def test_predict_returns_dict():
    result = predict_student(GOOD_STUDENT)
    assert isinstance(result, dict)


def test_predict_required_keys():
    result = predict_student(GOOD_STUDENT)
    for key in ("predicted_grade", "performance_level", "model_name", "top_factors", "outcomes"):
        assert key in result, f"Missing key: {key}"


def test_predicted_grade_in_range():
    result = predict_student(GOOD_STUDENT)
    assert 0.0 <= result["predicted_grade"] <= 20.0


def test_predicted_grade_rounded():
    result = predict_student(GOOD_STUDENT)
    assert result["predicted_grade"] == round(result["predicted_grade"], 2)


def test_performance_level_valid():
    result = predict_student(GOOD_STUDENT)
    assert result["performance_level"] in ("Excellent", "Good", "Needs Improvement", "At Risk")


def test_top_factors_count():
    result = predict_student(GOOD_STUDENT)
    assert len(result["top_factors"]) == 5


def test_top_factors_structure():
    result = predict_student(GOOD_STUDENT)
    for f in result["top_factors"]:
        assert "feature" in f
        assert "importance" in f
        assert 0.0 <= f["importance"] <= 1.0


def test_outcomes_keys():
    result = predict_student(GOOD_STUDENT)
    for key in ("dropout_risk", "placement_readiness", "remedial_needs"):
        assert key in result["outcomes"]


def test_model_name():
    result = predict_student(GOOD_STUDENT)
    assert result["model_name"] == "Random Forest (Multi-Outcome)"


def test_at_risk_student_grade_low():
    result = predict_student(AT_RISK_STUDENT)
    assert result["predicted_grade"] < 13.0


def test_at_risk_student_dropout_risk():
    result = predict_student(AT_RISK_STUDENT)
    assert result["outcomes"]["dropout_risk"] in ("High", "Moderate")


def test_good_student_low_dropout_risk():
    result = predict_student(GOOD_STUDENT)
    assert result["outcomes"]["dropout_risk"] == "Low"


def test_missing_field_raises():
    bad = {k: v for k, v in GOOD_STUDENT.items() if k != "cgpa"}
    with pytest.raises(ValueError, match="Missing required features"):
        predict_student(bad)


def test_non_numeric_raises():
    bad = {**GOOD_STUDENT, "cgpa": "not-a-number"}
    with pytest.raises(ValueError):
        predict_student(bad)


def test_out_of_range_cgpa_raises():
    bad = {**GOOD_STUDENT, "cgpa": 15.0}  # max is 10
    with pytest.raises(ValueError):
        predict_student(bad)


def test_out_of_range_attendance_raises():
    bad = {**GOOD_STUDENT, "attendance": 20.0}  # min is 50
    with pytest.raises(ValueError):
        predict_student(bad)


def test_non_dict_raises():
    with pytest.raises(ValueError):
        predict_student("not a dict")


def test_empty_string_field_raises():
    bad = {**GOOD_STUDENT, "cgpa": ""}
    with pytest.raises(ValueError):
        predict_student(bad)


def test_string_numeric_accepted():
    stringified = {k: str(v) for k, v in GOOD_STUDENT.items()}
    result = predict_student(stringified)
    assert "predicted_grade" in result
