import sqlite3
import os

# Path where database will be created
DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

# Path where your converted .sql files are
SQL_FOLDER_PATH = os.path.join(os.path.dirname(__file__), '..', 'sql')  # adjust if needed

def initialize_database():
    # Connect to SQLite database (creates it if doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # List all .sql files
    sql_files = [f for f in os.listdir(SQL_FOLDER_PATH) if f.endswith('.sql')]
    sql_files.sort()  # optional, ensures a stable order

    # Execute each .sql file
    for sql_file in sql_files:
        sql_file_path = os.path.join(SQL_FOLDER_PATH, sql_file)
        print(f"🛠 Executing {sql_file} ...")
        
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()

        try:
            cursor.executescript(sql_script)
            print(f"✅ Successfully executed {sql_file}")
        except sqlite3.Error as e:
            print(f"❌ Error executing {sql_file}: {e}")

    # Save and close connection
    conn.commit()
    conn.close()
    print("\n🎯 Database setup completed successfully at:", DB_PATH)

if __name__ == '__main__':
    initialize_database()
