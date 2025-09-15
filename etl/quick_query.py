# etl/quick_query.py -- quick printing of view results
import sqlite3
from pathlib import Path

db = Path(__file__).resolve().parents[1] / "chronic_disease_dw.db"
conn = sqlite3.connect(str(db))
cur = conn.cursor()

print("=== disease_prevalence ===")
for row in cur.execute("SELECT * FROM disease_prevalence;"):
    print(row)

print("\n=== readmission_rate ===")
for row in cur.execute("SELECT * FROM readmission_rate;"):
    print(row)

print("\n=== medication_adherence ===")
for row in cur.execute("SELECT * FROM medication_adherence;"):
    print(row)

print("\n=== patient_outcomes_summary ===")
for row in cur.execute("SELECT * FROM patient_outcomes_summary;"):
    print(row)

conn.close()
