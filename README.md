# Student Performance Predictor

A Flask application that predicts student academic performance with a 15-feature Random Forest regressor and reports additional risk and support indicators.

## Model and data

The model uses CGPA, attendance, quiz score, backlogs, entrance score, study hours, LMS usage, class participation, extracurricular hours, study style, sleep, screen time, stress, procrastination, and health status. It predicts a grade on a **0–20 scale**. The pre-trained model is `models/new_student_model.pkl`; retrain it with `train_new_model.py` and `dataset/Student_performance_10k.csv`.

The repository includes `dataset/Student_performance_10k.csv`, `dataset/new_student_dataset.csv`, other project datasets, and the project notebooks. The supplied training script derives the 15 input features from the source dataset.

## Requirements

- Python 3.10 or later
- MySQL 8 or compatible server

## Setup (Windows PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Create the `student_performance_db` database and its tables using the included schema on a **new or backed-up database**. The schema drops existing `students` and `predictions` tables before recreating them:

```powershell
mysql -u root -p < database/schema.sql
```

Configure the connection for the current PowerShell session with the MySQL account you created:

```powershell
$env:DB_HOST = "localhost"
$env:DB_PORT = "3306"
$env:DB_USER = "student_app"
$env:DB_PASSWORD = Read-Host "MySQL password"
$env:DB_NAME = "student_performance_db"
```

`database/migrate_schema.py` is also available for migrating the schema; it uses the same environment variables and can drop existing tables. Back up any database you need to keep before running schema setup or migration.

## Run

From the project root:

```powershell
python -m backend.app
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000). The prediction API is available at `/api/predict`; prediction history and analytics use MySQL.

To retrain the model:

```powershell
python train_new_model.py
```
