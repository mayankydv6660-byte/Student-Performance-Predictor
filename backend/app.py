from flask import Flask, render_template
import mysql.connector
from backend.routes import api
from database.db_connection import get_connection

app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static"
)
app.register_blueprint(api)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/history")
def history():
    predictions = []
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute("SHOW COLUMNS FROM students")
        student_cols = {row["Field"].lower() for row in cur.fetchall()}

        cur.execute("SHOW COLUMNS FROM predictions")
        pred_cols = {row["Field"].lower() for row in cur.fetchall()}

        has_cgpa = "cgpa" in student_cols
        has_risk = "dropout_risk" in pred_cols

        if has_cgpa and has_risk:
            query = """
            SELECT
                p.prediction_id,
                s.student_name,
                s.cgpa,
                s.attendance,
                s.backlogs,
                p.predicted_grade,
                p.performance_level,
                p.dropout_risk,
                p.placement_readiness,
                p.remedial_needs,
                p.model_name,
                p.prediction_date
            FROM predictions p
            JOIN students s ON p.student_id = s.student_id
            ORDER BY p.prediction_date DESC
            """
        elif has_cgpa and not has_risk:
            query = """
            SELECT
                p.prediction_id,
                s.student_name,
                s.cgpa,
                s.attendance,
                s.backlogs,
                p.predicted_grade,
                p.performance_level,
                'Low' AS dropout_risk,
                'Moderate (Requires Interview Prep)' AS placement_readiness,
                'None (On Track)' AS remedial_needs,
                p.model_name,
                p.prediction_date
            FROM predictions p
            JOIN students s ON p.student_id = s.student_id
            ORDER BY p.prediction_date DESC
            """
        else:
            query = """
            SELECT
                p.prediction_id,
                s.student_name,
                ROUND(p.predicted_grade / 2.0, 1) AS cgpa,
                ROUND(100 - s.absences, 0) AS attendance,
                s.previous_failures AS backlogs,
                p.predicted_grade,
                p.performance_level,
                CASE WHEN p.predicted_grade < 10 THEN 'High' ELSE 'Low' END AS dropout_risk,
                CASE WHEN p.predicted_grade >= 13 THEN 'High (Industry Ready)' ELSE 'Moderate (Requires Interview Prep)' END AS placement_readiness,
                'None (On Track)' AS remedial_needs,
                p.model_name,
                p.prediction_date
            FROM predictions p
            JOIN students s ON p.student_id = s.student_id
            ORDER BY p.prediction_date DESC
            """

        cur.execute(query)
        predictions = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[HISTORY ROUTE ERROR] {e}")

    return render_template("history.html", predictions=predictions)


@app.route("/analytics")
def analytics():
    total = 0
    avg = 0.0
    model = "Random Forest (Multi-Outcome)"
    latest = "N/A"
    excellent = good = needs = poor = 0
    risk_low = risk_mod = risk_high = 0

    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT COUNT(*) AS total FROM predictions")
        row = cur.fetchone()
        total = row["total"] if row and row["total"] else 0

        cur.execute("SELECT ROUND(AVG(predicted_grade),2) AS avg_grade FROM predictions")
        row = cur.fetchone()
        avg = row["avg_grade"] if row and row["avg_grade"] else 0.0

        cur.execute("SELECT model_name FROM predictions ORDER BY prediction_id DESC LIMIT 1")
        row = cur.fetchone()
        if row and row["model_name"]:
            model = row["model_name"]

        cur.execute("SELECT prediction_date FROM predictions ORDER BY prediction_id DESC LIMIT 1")
        row = cur.fetchone()
        if row and row["prediction_date"]:
            latest = str(row["prediction_date"])

        cur.execute("""
            SELECT performance_level, COUNT(*) AS cnt
            FROM predictions
            GROUP BY performance_level
        """)
        for r in cur.fetchall():
            lvl = r["performance_level"]
            cnt = r["cnt"]
            if lvl == "Excellent":
                excellent = cnt
            elif lvl == "Good":
                good = cnt
            elif lvl == "Needs Improvement":
                needs = cnt
            else:
                poor = cnt

        cur.execute("SHOW COLUMNS FROM predictions")
        pred_cols = {c["Field"].lower() for c in cur.fetchall()}

        if "dropout_risk" in pred_cols:
            cur.execute("""
                SELECT dropout_risk, COUNT(*) AS cnt
                FROM predictions
                GROUP BY dropout_risk
            """)
            for r in cur.fetchall():
                rk = r["dropout_risk"]
                cnt = r["cnt"]
                if rk == "High":
                    risk_high = cnt
                elif rk == "Moderate":
                    risk_mod = cnt
                else:
                    risk_low = cnt
        else:
            risk_high = poor
            risk_mod = needs
            risk_low = excellent + good

        cur.close()
        conn.close()
    except Exception as e:
        print(f"[ANALYTICS ROUTE ERROR] {e}")

    return render_template(
        "analytics.html",
        total_predictions=total,
        avg_grade=avg,
        model_name=model,
        latest_date=latest,
        excellent=excellent,
        good=good,
        needs=needs,
        poor=poor,
        risk_low=risk_low,
        risk_mod=risk_mod,
        risk_high=risk_high
    )


if __name__ == "__main__":
    app.run(debug=True)
