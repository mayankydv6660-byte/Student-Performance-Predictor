from flask import Blueprint, request, jsonify
from backend.predictor import predict_student, FEATURES
from database.db_connection import get_connection

api = Blueprint("api", __name__)


@api.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "success",
        "message": "Student Performance Predictor API is running"
    })


@api.route("/api/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({
                "status": "error",
                "message": "No student data received in JSON body"
            }), 400

        # Validate and predict using 15-feature model
        result = predict_student(data)

        student_id = None
        # Persist to database if connection is available
        try:
            conn = get_connection()
            cur = conn.cursor()

            # Check existing columns in students table
            cur.execute("SHOW COLUMNS FROM students")
            existing_cols = {row[0].lower() for row in cur.fetchall()}

            student_name = str(data.get("student_name", "Anonymous")).strip()[:100]

            if "cgpa" in existing_cols:
                # Upgraded 15-feature schema
                insert_student_sql = """
                INSERT INTO students (
                    student_name, cgpa, attendance, quiz_score, backlogs, entrance_score,
                    study_hours, lms_usage, class_participation, extra_activities,
                    study_style, sleep_hours, screen_time, stress_level,
                    procrastination, health_status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cur.execute(insert_student_sql, (
                    student_name,
                    float(data["cgpa"]),
                    float(data["attendance"]),
                    float(data["quiz_score"]),
                    int(float(data["backlogs"])),
                    float(data["entrance_score"]),
                    float(data["study_hours"]),
                    int(float(data["lms_usage"])),
                    int(float(data["class_participation"])),
                    float(data["extra_activities"]),
                    int(float(data["study_style"])),
                    float(data["sleep_hours"]),
                    float(data["screen_time"]),
                    int(float(data["stress_level"])),
                    int(float(data["procrastination"])),
                    int(float(data["health_status"])),
                ))
            else:
                # Compatible insert into existing table
                insert_student_sql = """
                INSERT INTO students (
                    student_name, school, sex, age, address, famsize, parent_status,
                    mother_education, father_education, mother_job, father_job,
                    study_time, previous_failures, school_support, family_support,
                    internet_access, romantic_relationship, free_time, going_out,
                    alcohol_weekday, alcohol_weekend, health, absences
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cur.execute(insert_student_sql, (
                    student_name, "GP", "M", 18, "U", "GT3", "T",
                    4, 4, "services", "services",
                    int(float(data.get("study_hours", 2))),
                    int(float(data.get("backlogs", 0))),
                    "no", "yes", "yes", "no",
                    int(float(data.get("sleep_hours", 7))),
                    int(float(data.get("screen_time", 4))),
                    1, 1,
                    int(float(data.get("health_status", 3))),
                    int(max(0, 100 - float(data.get("attendance", 85))))
                ))

            student_id = cur.lastrowid

            # Check existing columns in predictions table
            cur.execute("SHOW COLUMNS FROM predictions")
            pred_cols = {row[0].lower() for row in cur.fetchall()}

            if "dropout_risk" in pred_cols:
                pred_sql = """
                INSERT INTO predictions (
                    student_id, predicted_grade, performance_level, model_name,
                    dropout_risk, placement_readiness, remedial_needs
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cur.execute(pred_sql, (
                    student_id,
                    result["predicted_grade"],
                    result["performance_level"],
                    result["model_name"],
                    result["outcomes"]["dropout_risk"],
                    result["outcomes"]["placement_readiness"],
                    result["outcomes"]["remedial_needs"]
                ))
            else:
                pred_sql = """
                INSERT INTO predictions (
                    student_id, predicted_grade, performance_level, model_name
                ) VALUES (%s, %s, %s, %s)
                """
                cur.execute(pred_sql, (
                    student_id,
                    result["predicted_grade"],
                    result["performance_level"],
                    result["model_name"]
                ))

            conn.commit()
            cur.close()
            conn.close()
        except Exception as db_err:
            # If DB insert encounters an issue, log and continue returning prediction
            print(f"[DB LOGGING NOTICE] {db_err}")

        return jsonify({
            "status": "success",
            "student_id": student_id,
            "prediction": result
        })

    except ValueError as ve:
        return jsonify({
            "status": "error",
            "message": str(ve)
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Server error: {str(e)}"
        }), 500
