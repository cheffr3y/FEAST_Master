# Create a new file called verify_db.py
import sqlite3

conn = sqlite3.connect('banquet_planning.db')
cursor = conn.cursor()

# Get table info
cursor.execute("PRAGMA table_info(recipes)")
columns = cursor.fetchall()

print("\nRecipe Table Columns:")
for col in columns:
    print(f"Column: {col[1]}, Type: {col[2]}")

conn.close()