"""Smoke-test: verify MySQL connectivity."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_connection import get_connection

conn = get_connection()
if conn.is_connected():
    print("MySQL connection successful!")
conn.close()
print("Connection closed.")
