import sqlite3
import pandas as pd

# Connect to SQLite database (creates chronic_disease_dw.db if not exists)
conn = sqlite3.connect("chronic_disease_dw.db")
cursor = conn.cursor()

# Load patients.csv
patients = pd.read_csv("../data/patients.csv")
patients.to_sql("patients", conn, if_exists="replace", index=False)

# Load visits.csv
visits = pd.read_csv("../data/visits.csv")
visits.to_sql("visits", conn, if_exists="replace", index=False)

# Load medications.csv
medications = pd.read_csv("../data/medications.csv")
medications.to_sql("medications", conn, if_exists="replace", index=False)

print("✅ Data loaded successfully into chronic_disease_dw.db")

conn.close()
