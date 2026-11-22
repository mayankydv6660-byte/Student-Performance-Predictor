import os
import mysql.connector


def get_connection():
    """
    Return a live MySQL connection using environment variables.
    """
    password = os.environ.get("DB_PASSWORD")
    if password is None:
        raise RuntimeError("Set the DB_PASSWORD environment variable before connecting to MySQL.")

    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "student_app"),
        password=password,
        database=os.environ.get("DB_NAME", "student_performance_db"),
        port=int(os.environ.get("DB_PORT", 3306))
    )
