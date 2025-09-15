import sqlite3

conn = sqlite3.connect("chronic_disease_dw.db")
cursor = conn.cursor()

with open("sql/views.sql", "r") as f:
    cursor.executescript(f.read())

conn.commit()
conn.close()
print("✅ Views applied successfully")
