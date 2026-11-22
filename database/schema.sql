-- ==============================================================
-- Student Performance Predictor: 15-Feature Database Schema
-- Database: student_performance_db
-- ==============================================================

CREATE DATABASE IF NOT EXISTS student_performance_db;
USE student_performance_db;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS predictions;
DROP TABLE IF EXISTS students;
SET FOREIGN_KEY_CHECKS = 1;

-- 15-Feature Students Assessment Profile Table
CREATE TABLE students (
    student_id          INT NOT NULL AUTO_INCREMENT,
    student_name        VARCHAR(100) NOT NULL DEFAULT 'Anonymous',
    cgpa                DECIMAL(4,2) NOT NULL,
    attendance          DECIMAL(5,2) NOT NULL,
    quiz_score          DECIMAL(4,2) NOT NULL,
    backlogs            TINYINT UNSIGNED NOT NULL DEFAULT 0,
    entrance_score      DECIMAL(4,2) NOT NULL,
    study_hours         DECIMAL(3,1) NOT NULL,
    lms_usage           TINYINT NOT NULL,
    class_participation TINYINT NOT NULL,
    extra_activities    DECIMAL(4,1) NOT NULL DEFAULT 0,
    study_style         TINYINT NOT NULL DEFAULT 0,
    sleep_hours         DECIMAL(3,1) NOT NULL,
    screen_time         DECIMAL(3,1) NOT NULL,
    stress_level        TINYINT NOT NULL,
    procrastination     TINYINT NOT NULL,
    health_status       TINYINT NOT NULL,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Multi-Outcome Predictions Table
CREATE TABLE predictions (
    prediction_id       INT NOT NULL AUTO_INCREMENT,
    student_id          INT NOT NULL,
    predicted_grade     DECIMAL(5,2) NOT NULL,
    performance_level   VARCHAR(30) NOT NULL,
    model_name          VARCHAR(100) NOT NULL,
    dropout_risk        VARCHAR(20) NOT NULL DEFAULT 'Low',
    placement_readiness VARCHAR(50) NOT NULL DEFAULT 'Moderate (Requires Interview Prep)',
    remedial_needs      VARCHAR(200) NOT NULL DEFAULT 'None (On Track)',
    prediction_date     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (prediction_id),
    KEY student_id (student_id),
    CONSTRAINT fk_student_prediction 
        FOREIGN KEY (student_id) REFERENCES students (student_id) 
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
