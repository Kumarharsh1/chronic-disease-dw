import sqlite3
import pandas as pd

# Connect to SQLite DB
conn = sqlite3.connect("chronic_disease_dw.db")

# Load CSVs
patients = pd.read_csv("data/patients.csv")
visits = pd.read_csv("data/visits.csv")

# Push to DB
patients.to_sql("Patients", conn, if_exists="replace", index=False)
visits.to_sql("Visits", conn, if_exists="replace", index=False)

print("Data loaded successfully into the database!")
