import os
import pickle
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "new_student_model.pkl")

if not os.path.isfile(MODEL_PATH):
    raise FileNotFoundError(f"Trained model not found at: {MODEL_PATH}")

with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

# 15 numeric features in exact order
FEATURES = [
    "cgpa",
    "attendance",
    "quiz_score",
    "backlogs",
    "entrance_score",
    "study_hours",
    "lms_usage",
    "class_participation",
    "extra_activities",
    "study_style",
    "sleep_hours",
    "screen_time",
    "stress_level",
    "procrastination",
    "health_status"
]

FEATURE_LABELS = {
    "cgpa": "Current CGPA / Percentage",
    "attendance": "Attendance Percentage",
    "quiz_score": "Quiz & Assignment Scores",
    "backlogs": "Active / Previous Backlogs",
    "entrance_score": "Standardized Entrance Score",
    "study_hours": "Daily Self-Study Hours",
    "lms_usage": "LMS & Portal Usage",
    "class_participation": "Class Participation",
    "extra_activities": "Extracurricular Hours",
    "study_style": "Study Methodology",
    "sleep_hours": "Average Sleep Hours",
    "screen_time": "Non-Academic Screen Time",
    "stress_level": "Stress & Motivation Level",
    "procrastination": "Procrastination Tendency",
    "health_status": "Physical Health & Well-being"
}

# Validation ranges
FEATURE_RANGES = {
    "cgpa": (0.0, 10.0),
    "attendance": (50.0, 100.0),
    "quiz_score": (0.0, 10.0),
    "backlogs": (0.0, 20.0),
    "entrance_score": (0.0, 10.0),
    "study_hours": (1.0, 8.0),
    "lms_usage": (1.0, 5.0),
    "class_participation": (1.0, 5.0),
    "extra_activities": (0.0, 10.0),
    "study_style": (0.0, 1.0),
    "sleep_hours": (5.0, 9.0),
    "screen_time": (1.0, 8.0),
    "stress_level": (1.0, 5.0),
    "procrastination": (1.0, 5.0),
    "health_status": (1.0, 4.0)
}


def performance_category(score: float) -> str:
    """Classify 0-20 score into performance level."""
    if score < 8:
        return "At Risk"
    elif score < 12:
        return "Needs Improvement"
    elif score < 16:
        return "Good"
    else:
        return "Excellent"


def validate_features(data: dict) -> dict:
    """Validate presence, numeric types, and ranges for all 15 features."""
    if not isinstance(data, dict):
        raise ValueError("Student data must be a JSON object.")

    missing = [f for f in FEATURES if f not in data or data[f] is None or str(data[f]).strip() == ""]
    if missing:
        raise ValueError(f"Missing required features: {', '.join(missing)}")

    parsed = {}
    errors = []
    for f in FEATURES:
        val = data[f]
        try:
            val_float = float(val)
        except (ValueError, TypeError):
            errors.append(f"Field '{f}' must be numeric (got {val!r}).")
            continue

        min_val, max_val = FEATURE_RANGES[f]
        if not (min_val <= val_float <= max_val):
            errors.append(f"Field '{f}' must be between {min_val} and {max_val} (got {val_float}).")
            continue

        if f == "study_style" and int(val_float) not in (0, 1):
            errors.append("Field 'study_style' must be 0 (Individual) or 1 (Peer Group).")
            continue

        parsed[f] = val_float

    if errors:
        raise ValueError("Validation failed: " + "; ".join(errors))

    return parsed


def evaluate_multi_outcomes(data: dict, grade: float) -> dict:
    """Compute multi-outcome indicators based on student metrics and projected grade."""
    # 1. Dropout / At-Risk Detection
    risk_reasons = []
    if data["attendance"] < 70:
        risk_reasons.append("Low attendance (<70%)")
    if data["backlogs"] >= 2:
        risk_reasons.append(f"{int(data['backlogs'])} active backlogs")
    if grade < 10:
        risk_reasons.append("Projected exam score below passing threshold")

    if grade < 8 or len(risk_reasons) >= 2:
        dropout_risk = "High"
    elif risk_reasons:
        dropout_risk = "Moderate"
    else:
        dropout_risk = "Low"

    # 2. Placement & Career Readiness
    if data["cgpa"] >= 7.5 and data["backlogs"] == 0 and grade >= 13:
        placement_readiness = "High (Industry Ready)"
    elif data["cgpa"] >= 6.0 and data["backlogs"] <= 1 and grade >= 10:
        placement_readiness = "Moderate (Requires Interview Prep)"
    else:
        placement_readiness = "Needs Upskilling"

    # 3. Remedial & Support Needs
    support_needs = []
    if data["backlogs"] > 0:
        support_needs.append("Backlog Clearing Tutoring")
    if data["quiz_score"] < 5.0:
        support_needs.append("Concept Reinforcement Sessions")
    if data["stress_level"] >= 3:
        support_needs.append("Academic Stress Counseling")
    if data["study_hours"] < 2.0:
        support_needs.append("Time Management Workshop")

    remedial_status = ", ".join(support_needs) if support_needs else "None (On Track)"

    return {
        "dropout_risk": dropout_risk,
        "placement_readiness": placement_readiness,
        "remedial_needs": remedial_status
    }


def predict_student(student_data: dict) -> dict:
    """Predict performance using Random Forest model on 15 features."""
    clean_data = validate_features(student_data)

    input_df = pd.DataFrame(
        [[clean_data[f] for f in FEATURES]],
        columns=FEATURES
    )

    raw_prediction = float(model.predict(input_df)[0])
    # Clamp to 0-20 scale and round to 2 decimals
    clamped_grade = round(max(0.0, min(20.0, raw_prediction)), 2)

    category = performance_category(clamped_grade)
    outcomes = evaluate_multi_outcomes(clean_data, clamped_grade)

    # Top 5 feature importances
    importances = model.feature_importances_
    factors = [
        {"feature": FEATURE_LABELS.get(f, f), "importance": round(float(imp), 4)}
        for f, imp in zip(FEATURES, importances)
    ]
    top_factors = sorted(factors, key=lambda x: x["importance"], reverse=True)[:5]

    return {
        "predicted_grade": clamped_grade,
        "performance_level": category,
        "model_name": "Random Forest (Multi-Outcome)",
        "top_factors": top_factors,
        "outcomes": outcomes
    }
