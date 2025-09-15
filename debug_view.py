import sqlite3
import re
import csv
from datetime import datetime

# Connect to the database
conn = sqlite3.connect("chronic_disease_dw.db")
cur = conn.cursor()

# ============================================
# 1. Detect all tables and columns
# ============================================
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cur.fetchall()]

table_columns = {}
print("=== Tables and Columns ===")
for table in tables:
    cur.execute(f"PRAGMA table_info({table});")
    cols = [col[1] for col in cur.fetchall()]
    table_columns[table] = cols
    print(f"\nTable: {table}")
    for col in cols:
        print(f"  - {col}")

# ============================================
# 2. Drop and recreate fixed KPI views
# ============================================
views_sql = {
    "disease_prevalence": """
        DROP VIEW IF EXISTS disease_prevalence;
        CREATE VIEW disease_prevalence AS
        SELECT 
            d.name AS disease,
            COUNT(p.patient_id) AS total_patients
        FROM diseases d
        LEFT JOIN patients p ON d.name = p.disease
        GROUP BY d.name;
    """,
    "readmission_rate": """
        DROP VIEW IF EXISTS readmission_rate;
        CREATE VIEW readmission_rate AS
        SELECT 
            d.name AS disease,
            COUNT(DISTINCT v.patient_id) AS readmitted_patients,
            COUNT(DISTINCT p.patient_id) AS total_patients,
            ROUND(
                (CAST(COUNT(DISTINCT v.patient_id) AS REAL) / NULLIF(COUNT(DISTINCT p.patient_id), 0)) * 100,
                2
            ) AS readmission_rate_percent
        FROM diseases d
        LEFT JOIN patients p ON d.name = p.disease
        LEFT JOIN visits v ON p.patient_id = v.patient_id AND v.outcome = 'Readmitted'
        GROUP BY d.name;
    """,
    "medication_adherence": """
        DROP VIEW IF EXISTS medication_adherence;
        CREATE VIEW medication_adherence AS
        SELECT 
            d.name AS disease,
            ROUND(AVG(m.adherence), 2) AS avg_adherence_percent
        FROM diseases d
        LEFT JOIN patients p ON d.name = p.disease
        LEFT JOIN medications m ON p.patient_id = m.patient_id
        GROUP BY d.name;
    """,
    "patient_outcomes_summary": """
        DROP VIEW IF EXISTS patient_outcomes_summary;
        CREATE VIEW patient_outcomes_summary AS
        SELECT 
            v.outcome,
            COUNT(DISTINCT v.patient_id) AS total_patients
        FROM visits v
        GROUP BY v.outcome;
    """
}

for view_name, sql in views_sql.items():
    cur.executescript(sql)

# ============================================
# 3. Detect all views and validate
# ============================================
cur.execute("SELECT name, sql FROM sqlite_master WHERE type='view';")
views = cur.fetchall()

print("\n=== Views and Validation ===")

# Prepare report data
report_data = []

for view_name, view_sql in views:
    print(f"\nView: {view_name}")
    print(view_sql)

    matches = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)', view_sql)
    missing_columns = []
    for table_ref, col_ref in matches:
        if table_ref in table_columns:
            if col_ref not in table_columns[table_ref]:
                missing_columns.append(f"{table_ref}.{col_ref}")
        else:
            missing_columns.append(f"{table_ref}.{col_ref} (table does not exist)")

    if missing_columns:
        print("⚠ Missing columns or tables detected:")
        for col in missing_columns:
            print(f"  - {col}")
            report_data.append({"view": view_name, "missing_column": col})
    else:
        print("✔ All columns exist in tables.")

# ============================================
# 4. Save missing columns report to CSV
# ============================================
if report_data:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"missing_columns_report_{timestamp}.csv"
    with open(report_file, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["view", "missing_column"])
        writer.writeheader()
        writer.writerows(report_data)
    print(f"\n📄 Missing columns report saved: {report_file}")
else:
    print("\n✔ No missing columns detected. No report generated.")

# ============================================
# 5. Close connection
# ============================================
conn.close()
