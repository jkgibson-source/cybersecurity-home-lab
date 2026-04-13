import sqlite3
import os

DB_PATH = os.path.expanduser("~/BirdsNest/burrow-data/burrow.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evidence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            source TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            host TEXT,
            tags TEXT,
            summary TEXT,
            path TEXT,
            exercise TEXT
        )
    """)
    conn.commit()
    conn.close()
    print(f"[db] Database initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()
