import sqlite3
import pandas as pd
import os

# Paths
DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')
CSV_STUDENT_REG = os.path.join(os.path.dirname(__file__), '..', 'data', 'Course Registrations And Student Majors Fall2024 - WithOut Reg Date.csv')
CSV_CLASS_MEETINGS = os.path.join(os.path.dirname(__file__), '..', 'data', 'Fall2024 Class Enrollment vs Room Size.csv')

# Connect to database
conn = sqlite3.connect(DB_PATH)

# -------- Insert into StudentRegistrations --------
df_students = pd.read_csv(CSV_STUDENT_REG)

# Insert ALL columns into StudentRegistrations
df_students.to_sql('StudentRegistrations', conn, if_exists='append', index=False)

print(f"✅ Inserted {len(df_students)} rows into StudentRegistrations")

# -------- Insert into ClassMeetings --------
df_classes = pd.read_csv(CSV_CLASS_MEETINGS)

# Insert ALL columns into ClassMeetings
df_classes.to_sql('ClassMeetings', conn, if_exists='append', index=False)

print(f"✅ Inserted {len(df_classes)} rows into ClassMeetings")

# Close connection
conn.close()
print("🎯 All CSV data inserted successfully!")
