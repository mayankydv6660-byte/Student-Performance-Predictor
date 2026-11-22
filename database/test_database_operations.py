"""
Integration test: test database operations with MySQL student_performance_db.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_connection import get_connection

SAMPLE = {
    "student_name": "Test Student 15F",
    "cgpa": 8.2,
    "attendance": 90.0,
    "quiz_score": 7.5,
    "backlogs": 0,
    "entrance_score": 7.0,
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

PRED = {
    "predicted_grade": 13.9,
    "performance_level": "Good",
    "model_name": "Random Forest (Multi-Outcome)",
    "dropout_risk": "Low",
    "placement_readiness": "High (Industry Ready)",
    "remedial_needs": "None (On Track)",
}

def test_insert_and_retrieve():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SHOW COLUMNS FROM students")
    student_cols = {row["Field"].lower() for row in cur.fetchall()}

    if "cgpa" in student_cols:
        cur.execute("""
            INSERT INTO students
              (student_name, cgpa, attendance, quiz_score, backlogs, entrance_score,
               study_hours, lms_usage, class_participation, extra_activities,
               study_style, sleep_hours, screen_time, stress_level, procrastination, health_status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            SAMPLE["student_name"], SAMPLE["cgpa"], SAMPLE["attendance"],
            SAMPLE["quiz_score"], SAMPLE["backlogs"], SAMPLE["entrance_score"],
            SAMPLE["study_hours"], SAMPLE["lms_usage"], SAMPLE["class_participation"],
            SAMPLE["extra_activities"], SAMPLE["study_style"], SAMPLE["sleep_hours"],
            SAMPLE["screen_time"], SAMPLE["stress_level"], SAMPLE["procrastination"],
            SAMPLE["health_status"]
        ))
    else:
        cur.execute("""
            INSERT INTO students
              (student_name, school, sex, age, address, famsize, parent_status,
               mother_education, father_education, mother_job, father_job,
               study_time, previous_failures, school_support, family_support,
               internet_access, romantic_relationship, free_time, going_out,
               alcohol_weekday, alcohol_weekend, health, absences)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            SAMPLE["student_name"], "GP", "M", 18, "U", "GT3", "T",
            4, 4, "services", "services", 3, 0,
            "no", "yes", "yes", "no", 3, 3, 1, 1, 3, 4
        ))

    student_id = cur.lastrowid

    cur.execute("SHOW COLUMNS FROM predictions")
    pred_cols = {row["Field"].lower() for row in cur.fetchall()}

    if "dropout_risk" in pred_cols:
        cur.execute("""
            INSERT INTO predictions
              (student_id, predicted_grade, performance_level, model_name,
               dropout_risk, placement_readiness, remedial_needs)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            student_id, PRED["predicted_grade"], PRED["performance_level"],
            PRED["model_name"], PRED["dropout_risk"],
            PRED["placement_readiness"], PRED["remedial_needs"]
        ))
    else:
        cur.execute("""
            INSERT INTO predictions
              (student_id, predicted_grade, performance_level, model_name)
            VALUES (%s,%s,%s,%s)
        """, (
            student_id, PRED["predicted_grade"], PRED["performance_level"],
            PRED["model_name"]
        ))

    conn.commit()

    cur.execute("""
        SELECT s.student_id, s.student_name, p.predicted_grade, p.performance_level
        FROM students s
        JOIN predictions p ON s.student_id = p.student_id
        WHERE s.student_id = %s
    """, (student_id,))
    row = cur.fetchone()

    print("\n=== Database Test Result ===")
    for k, v in row.items():
        print(f"  {k:<20}: {v}")

    assert row["student_name"] == SAMPLE["student_name"]
    assert float(row["predicted_grade"]) == PRED["predicted_grade"]
    assert row["performance_level"] == PRED["performance_level"]
    print("\nAll database assertions passed!")

    cur.close()
    conn.close()

if __name__ == "__main__":
    test_insert_and_retrieve()
