"""
Train Student Performance Model using Student_performance_10k.csv
Maps raw scores → 15 features → predicts final grade (0-20 scale)
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
import pickle
import os

# ── Load raw dataset ─────────────────────────────────────────────────────────
CSV_PATH = "dataset/Student_performance_10k.csv"
df = pd.read_csv(CSV_PATH)
print(f"Loaded {df.shape[0]} rows, columns: {df.columns.tolist()}")

# ── Grade → numeric target (0–20 scale) ─────────────────────────────────────
grade_map = {'O': 20, 'A+': 18, 'A': 16, 'B+': 14, 'B': 12,
             'C': 10, 'D': 8, 'F': 4, 'P': 11}

df['grade_num'] = df['grade'].map(grade_map)
if df['grade_num'].isna().any():
    df['grade_num'] = df['grade_num'].fillna(df['grade_num'].median())
print(f"Grade distribution:\n{df['grade'].value_counts().to_string()}")

# ── Encode helper: map categorical cols to numeric ───────────────────────────
gender_map    = {'male': 1, 'female': 0}
lunch_map     = {1: 1, 0: 0, 'standard': 1, 'free/reduced': 0}
prep_map      = {1: 1, 0: 0, 'completed': 1, 'none': 0}
edu_map       = {'some high school': 1, 'high school': 2,
                 'some college': 3, "associate's degree": 4,
                 "bachelor's degree": 5, "master's degree": 6}

df['gender_n']   = df['gender'].map(gender_map).fillna(0)
df['lunch_n']    = df['lunch'].map(lunch_map).fillna(0)
df['prep_n']     = df['test_preparation_course'].map(prep_map).fillna(0)
df['edu_n']      = df['parental_level_of_education'].map(edu_map).fillna(3)

# ── Normalize raw scores to 0–10 range ───────────────────────────────────────
for col in ['math_score', 'reading_score', 'writing_score', 'science_score', 'total_score']:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(50)

max_total = df['total_score'].max()

# avg of all 4 scores (0–100 scale)
df['avg_score'] = (df['math_score'] + df['reading_score'] +
                   df['writing_score'] + df['science_score']) / 4

# ── Build 15 features from dataset signals ───────────────────────────────────
np.random.seed(42)
n = len(df)

# 1. cgpa: average score mapped to 0–10
df['cgpa'] = (df['avg_score'] / 10).clip(0, 10)

# 2. attendance: prep course → higher attendance
df['attendance'] = (60 + df['prep_n'] * 20 +
                    df['avg_score'] * 0.15 +
                    np.random.normal(0, 5, n)).clip(50, 100)

# 3. quiz_score: reading + writing proxy (0–10)
df['quiz_score'] = ((df['reading_score'] + df['writing_score']) / 20).clip(0, 10)

# 4. backlogs: inverse of avg_score
df['backlogs'] = np.where(df['avg_score'] < 40, np.random.randint(2, 6, n),
                 np.where(df['avg_score'] < 60, np.random.randint(0, 2, n), 0))

# 5. entrance_score: math + science proxy (0–10)
df['entrance_score'] = ((df['math_score'] + df['science_score']) / 20).clip(0, 10)

# 6. study_hours: prep course + score based (1–8)
df['study_hours'] = (1 + df['prep_n'] * 2 +
                     df['avg_score'] * 0.04 +
                     np.random.normal(0, 0.5, n)).clip(1, 8)

# 7. lms_usage: 1=Never, 2=Rarely, 3=Sometimes, 4=Often, 5=Always
df['lms_usage'] = (1 + df['prep_n'] * 2 +
                   (df['avg_score'] / 50) * 2 +
                   np.random.normal(0, 0.3, n)).clip(1, 5).round().astype(int)

# 8. class_participation: 1=Never...5=Always
df['class_participation'] = (1 + (df['avg_score'] / 50) * 3 +
                              df['prep_n'] +
                              np.random.normal(0, 0.3, n)).clip(1, 5).round().astype(int)

# 9. extra_activities: hours per week (0–10)
df['extra_activities'] = (np.random.uniform(0, 8, n) +
                           df['lunch_n'] * 1.5).clip(0, 10)

# 10. study_style: 0=Individual, 1=Peer group
df['study_style'] = df['prep_n'].apply(lambda x: 1 if x == 1 else np.random.choice([0, 1]))

# 11. sleep_hours: 5–9
df['sleep_hours'] = (7 + np.random.normal(0, 1, n)).clip(5, 9)

# 12. screen_time: 1–8 hours
df['screen_time'] = (8 - df['avg_score'] * 0.04 +
                     np.random.normal(0, 1, n)).clip(1, 8)

# 13. stress_level: 1=Very Low...5=Very High
df['stress_level'] = (5 - (df['avg_score'] / 50) * 3 +
                      np.random.normal(0, 0.5, n)).clip(1, 5).round().astype(int)

# 14. procrastination: 1=Never...5=Always
df['procrastination'] = (5 - df['prep_n'] * 1.5 -
                          (df['avg_score'] / 50) * 2 +
                          np.random.normal(0, 0.5, n)).clip(1, 5).round().astype(int)

# 15. health_status: 1=Poor...4=Excellent
df['health_status'] = (2 + df['lunch_n'] * 1 +
                        np.random.normal(0, 0.5, n)).clip(1, 4).round().astype(int)

# ── Assemble feature matrix ───────────────────────────────────────────────────
FEATURES = ["cgpa", "attendance", "quiz_score", "backlogs", "entrance_score",
            "study_hours", "lms_usage", "class_participation", "extra_activities",
            "study_style", "sleep_hours", "screen_time", "stress_level",
            "procrastination", "health_status"]

TARGET = "grade_num"

X = df[FEATURES].astype(float)
y = df[TARGET].astype(float)

print(f"\nFeature matrix: {X.shape}")
print(f"Target range: {y.min():.1f} – {y.max():.1f}")
print(f"Target mean: {y.mean():.2f}, std: {y.std():.2f}")

# ── Train / Test split ────────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ── Train Random Forest ───────────────────────────────────────────────────────
print("\nTraining Random Forest...")
model = RandomForestRegressor(
    n_estimators=300,
    max_depth=12,
    min_samples_split=4,
    min_samples_leaf=2,
    max_features='sqrt',
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)

# ── Evaluate ──────────────────────────────────────────────────────────────────
y_pred = model.predict(X_test)
r2  = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)

print(f"\n{'='*40}")
print(f"  R² Score  : {r2:.4f}  ({r2*100:.1f}%)")
print(f"  MAE       : {mae:.4f}")
print(f"  Accuracy  : ~{max(0, (1 - mae/20)*100):.1f}%")
print(f"{'='*40}")

# Feature importances
print("\nTop feature importances:")
importances = pd.Series(model.feature_importances_, index=FEATURES).sort_values(ascending=False)
for feat, imp in importances.items():
    print(f"  {feat:<22}: {imp:.4f}")

# ── Save model ────────────────────────────────────────────────────────────────
os.makedirs("models", exist_ok=True)
MODEL_PATH = "models/new_student_model.pkl"
with open(MODEL_PATH, 'wb') as f:
    pickle.dump(model, f)
print(f"\nModel saved → {MODEL_PATH}")

# ── Save processed dataset ────────────────────────────────────────────────────
processed = df[FEATURES + [TARGET]].copy()
processed.to_csv("dataset/new_student_dataset.csv", index=False)
print(f"Processed dataset saved → dataset/new_student_dataset.csv  ({len(processed)} rows)")

# ── Remove old UCI model ──────────────────────────────────────────────────────
old_model = "models/student_performance_model.pkl"
if os.path.exists(old_model):
    os.remove(old_model)
    print(f"Removed old model → {old_model}")

print("\nDONE! Model ready for deployment.")
