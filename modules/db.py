"""
db.py — Database connection helper
CS-4347 Airport Management System
"""

import os
import sqlite3


def _db_path() -> str:
    return os.environ.get("AIRPORT_DB", "airport.db")


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection with foreign keys enabled and row_factory set."""
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row          # rows accessible by column name
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(schema_path: str = "sql/schema.sql", seed_path: str | None = None) -> None:
    """Create tables and optionally load seed data."""
    conn = get_connection()
    with open(schema_path, "r") as f:
        conn.executescript(f.read())
    if seed_path and os.path.exists(seed_path):
        with open(seed_path, "r") as f:
            conn.executescript(f.read())
    conn.commit()
    conn.close()
    print(f"[db] Database initialized → {_db_path()}")
