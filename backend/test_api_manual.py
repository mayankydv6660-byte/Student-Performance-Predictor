"""
Manual smoke test: POST /api/predict with 15-feature payload.
Run directly: python backend/test_api_manual.py
"""
import json
import urllib.request
import urllib.error

PAYLOAD = {
    "student_name": "Mayank Yadav",
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
    "health_status": 3
}

req = urllib.request.Request(
    "http://127.0.0.1:5000/api/predict",
    data=json.dumps(PAYLOAD).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST"
)

try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    print("=" * 55)
    print("  STUDENT PERFORMANCE PREDICTOR — 15-FEATURE API TEST")
    print("=" * 55)
    print(json.dumps(result, indent=4))
    print("=" * 55)
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code, e.read().decode("utf-8", errors="replace"))
except urllib.error.URLError as e:
    print("Connection Error:", e.reason)
except Exception as e:
    print("Error:", e)
