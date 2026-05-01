"""
db.py — Database connection helper
CS-4347 Airport Management System
"""

import sqlite3
import os

DB_PATH = os.environ.get("AIRPORT_DB", "airport.db")


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection with foreign keys enabled and row_factory set."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row          # rows accessible by column name
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(
    schema_path: str = "sql/schema.sql",
    seed_path: str | None = None,
    csv_dir: str | None = None,
) -> None:
    """Create tables and optionally load seed SQL or professor CSV bundle."""
    conn = get_connection()
    with open(schema_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    if csv_dir:
        from modules.csv_loader import load_professor_csvs

        load_professor_csvs(conn, csv_dir)
        print(f"[db] Loaded CSV data from {os.path.abspath(csv_dir)}")
    elif seed_path and os.path.exists(seed_path):
        with open(seed_path, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        print(f"[db] Loaded seed SQL -> {seed_path}")
    conn.commit()
    conn.close()
    print(f"[db] Database initialized -> {DB_PATH}")
