# etl/setup_database.py
# Creates/opens chronic_disease_dw.db, creates diseases table (with sample entries),
# loads data/*.csv into tables, and creates KPI views.

import sqlite3
import pandas as pd
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
db_path = repo_root / "chronic_disease_dw.db"
data_dir = repo_root / "data"
schema_file = repo_root / "sql" / "schema.sql"   # optional use

print("Repo root:", repo_root)
print("DB path:", db_path)

conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

# 1) Ensure diseases table exists and insert sample rows if empty
cur.execute("""
CREATE TABLE IF NOT EXISTS diseases (
    disease_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT
);
""")
conn.commit()

cur.execute("SELECT COUNT(*) FROM diseases;")
count = cur.fetchone()[0]
if count == 0:
    print("Inserting sample disease master rows...")
    cur.executemany(
        "INSERT INTO diseases (disease_id, name, type) VALUES (?, ?, ?);",
        [
            (1, "Diabetes", "Chronic"),
            (2, "Hypertension", "Chronic"),
            (3, "Asthma", "Respiratory"),
            (4, "Heart Disease", "Cardiovascular")
        ]
    )
    conn.commit()

# 2) Load CSVs into tables using pandas (creates/replaces tables)
def load_csv_to_table(csv_path, table_name):
    if not csv_path.exists():
        print(f"Warning: {csv_path} not found — skipping {table_name}")
        return
    df = pd.read_csv(csv_path)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    print(f"Loaded {len(df):,} rows into table '{table_name}'")

load_csv_to_table(data_dir / "patients.csv", "patients")
load_csv_to_table(data_dir / "visits.csv", "visits")
load_csv_to_table(data_dir / "medications.csv", "medications")

# 3) Create KPI views (drop if exists then create)
views_sql = """
-- disease_prevalence
DROP VIEW IF EXISTS disease_prevalence;
CREATE VIEW disease_prevalence AS
SELECT d.name AS disease, COUNT(p.patient_id) AS total_patients
FROM diseases d
LEFT JOIN patients p ON d.disease_id = p.disease_id
GROUP BY d.name;

-- readmission_rate
DROP VIEW IF EXISTS readmission_rate;
CREATE VIEW readmission_rate AS
SELECT d.name AS disease,
       COUNT(DISTINCT CASE WHEN v.outcome='Readmitted' THEN v.patient_id END) AS readmitted_patients,
       COUNT(DISTINCT p.patient_id) AS total_patients,
       CASE WHEN COUNT(DISTINCT p.patient_id)=0 THEN 0
            ELSE ROUND(
               (COUNT(DISTINCT CASE WHEN v.outcome='Readmitted' THEN v.patient_id END)*1.0)
               / COUNT(DISTINCT p.patient_id) * 100, 2)
       END AS readmission_rate_percent
FROM diseases d
LEFT JOIN patients p ON d.disease_id = p.disease_id
LEFT JOIN visits v ON p.patient_id = v.patient_id
GROUP BY d.name;

-- medication_adherence
DROP VIEW IF EXISTS medication_adherence;
CREATE VIEW medication_adherence AS
SELECT d.name AS disease, ROUND(AVG(m.adherence), 2) AS avg_adherence_percent
FROM diseases d
LEFT JOIN patients p ON d.disease_id = p.disease_id
LEFT JOIN medications m ON p.patient_id = m.patient_id
GROUP BY d.name;

-- patient_outcomes_summary
DROP VIEW IF EXISTS patient_outcomes_summary;
CREATE VIEW patient_outcomes_summary AS
SELECT outcome, COUNT(DISTINCT patient_id) AS total_patients FROM visits GROUP BY outcome;
"""

cur.executescript(views_sql)
conn.commit()

# 4) Print quick counts
for t in ("diseases", "patients", "visits", "medications"):
    try:
        cur.execute(f"SELECT COUNT(*) FROM {t};")
        print(f"{t}: {cur.fetchone()[0]}")
    except Exception as e:
        print(f"{t}: (table missing)")

print("\n✅ Setup complete. Database and views are ready.")
print("DB file location:", db_path)

conn.close()
