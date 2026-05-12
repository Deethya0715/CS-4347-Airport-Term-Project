"""
csv_loader.py - Load professor-provided milestone CSVs into SQLite.

Column mapping / quirks:
  AIRPORT.csv          → (Airport_code, City, State, Name)  [CSV order differs]
  SEAT.csv             → PHYSICAL_PLANE_SEAT (Airplane_id, Seat_no, Class)
  FARE.csv             → (Code, Fare_Number, …)  [CSV is Fare_Number, Code, …]
  LEG_INSTANCE.csv     → drops extra Scheduled_* columns not in schema
  Times                → normalized to HH:MM:SS for lexicographic comparisons
  Dates                → M/D/YYYY → YYYY-MM-DD
"""

from __future__ import annotations

import csv
import os
import sqlite3
from datetime import datetime


def _norm_time(raw: str) -> str:
    """Professor CSV uses '9:55:00' or '09:55:00'; normalize to HH:MM:SS."""
    raw = (raw or "").strip()
    if not raw:
        return ""
    parts = raw.split(":")
    if len(parts) < 2:
        return raw
    try:
        h, m = int(parts[0]), int(parts[1])
        s = int(parts[2]) if len(parts) > 2 else 0
        return f"{h:02d}:{m:02d}:{s:02d}"
    except ValueError:
        return raw


def _norm_date(raw: str) -> str:
    raw = (raw or "").strip()
    for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return raw


def _open_csv(csv_dir: str, name: str):
    path = os.path.join(csv_dir, name)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Missing CSV: {path}")
    return open(path, newline="", encoding="utf-8-sig")


def clear_tables(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA foreign_keys = OFF")
    for table in (
        "SEAT",
        "LEG_INSTANCE",
        "FARE",
        "FLIGHT_LEG",
        "FLIGHT",
        "PHYSICAL_PLANE_SEAT",
        "AIRPLANE",
        "CAN_LAND",
        "AIRPLANE_TYPE",
        "AIRPORT",
    ):
        conn.execute(f"DELETE FROM {table}")
    conn.execute("PRAGMA foreign_keys = ON")


def load_professor_csvs(conn: sqlite3.Connection, csv_dir: str) -> None:
    csv_dir = os.path.abspath(csv_dir)
    clear_tables(conn)

    # --- AIRPORT (CSV: Airport_code, Name, City, State) ---
    with _open_csv(csv_dir, "AIRPORT.csv") as f:
        r = csv.DictReader(f)
        conn.executemany(
            "INSERT INTO AIRPORT (Airport_code, City, State, Name) VALUES (?,?,?,?)",
            (
                (
                    row["Airport_code"].strip(),
                    row["City"].strip(),
                    row["State"].strip(),
                    row["Name"].strip(),
                )
                for row in r
            ),
        )

    # --- AIRPLANE_TYPE ---
    with _open_csv(csv_dir, "AIRPLANE_TYPE.csv") as f:
        r = csv.DictReader(f)
        conn.executemany(
            "INSERT INTO AIRPLANE_TYPE (Type_name, Company, Max_seats) VALUES (?,?,?)",
            (
                (
                    row["Type_name"].strip(),
                    row["Company"].strip(),
                    int(row["Max_seats"]),
                )
                for row in r
            ),
        )

    # --- AIRPLANE ---
    with _open_csv(csv_dir, "AIRPLANE.csv") as f:
        r = csv.DictReader(f)
        conn.executemany(
            "INSERT INTO AIRPLANE (Airplane_id, Total_no_of_seats, Type_name) VALUES (?,?,?)",
            (
                (
                    row["Airplane_id"].strip(),
                    int(row["Total_no_of_seats"]),
                    row["Type_name"].strip(),
                )
                for row in r
            ),
        )

    # --- FLIGHT (header is FLIGHT_Number in professor file) ---
    with _open_csv(csv_dir, "FLIGHT.csv") as f:
        r = csv.DictReader(f)
        fields = r.fieldnames or []
        fn_key = "FLIGHT_Number" if "FLIGHT_Number" in fields else "Flight_Number"
        rows = [
            (
                str(row[fn_key]).strip(),
                row["Airline"].strip(),
                str(row["Weekdays"]).strip(),
            )
            for row in r
            if row.get(fn_key)
        ]
        conn.executemany(
            "INSERT INTO FLIGHT (FLIGHT_Number, Airline, Weekdays) VALUES (?,?,?)",
            rows,
        )

    # --- FLIGHT_LEG ---
    with _open_csv(csv_dir, "FLIGHT_LEG.csv") as f:
        r = csv.DictReader(f)
        conn.executemany(
            """
            INSERT INTO FLIGHT_LEG (
                FLIGHT_LEG_Number, Leg_no, Departure_code, Arrival_code,
                Scheduled_dep_time, Scheduled_arr_time
            ) VALUES (?,?,?,?,?,?)
            """,
            (
                (
                    str(row["FLIGHT_LEG_Number"]).strip(),
                    int(row["Leg_no"]),
                    row["Departure_code"].strip(),
                    row["Arrival_code"].strip(),
                    _norm_time(row["Scheduled_dep_time"]),
                    _norm_time(row["Scheduled_arr_time"]),
                )
                for row in r
            ),
        )

    # --- FARE (CSV: Fare_Number, Code, Amount, Restriction) → DB (Code, Fare_Number, …) ---
    with _open_csv(csv_dir, "FARE.csv") as f:
        r = csv.DictReader(f)
        conn.executemany(
            "INSERT INTO FARE (Code, Fare_Number, Amount, Restriction) VALUES (?,?,?,?)",
            (
                (
                    row["Code"].strip(),
                    str(row["Fare_Number"]).strip(),
                    float(row["Amount"]),
                    (row.get("Restriction") or "").strip() or None,
                )
                for row in r
            ),
        )

    # --- LEG_INSTANCE (ignore Scheduled_* in CSV) ---
    with _open_csv(csv_dir, "LEG_INSTANCE.csv") as f:
        r = csv.DictReader(f)
        conn.executemany(
            """
            INSERT INTO LEG_INSTANCE (
                LEG_INSTANCE_Number, Leg_no, LEG_INSTANCE_Date,
                No_of_available_seats, Airplane_id
            ) VALUES (?,?,?,?,?)
            """,
            (
                (
                    str(row["LEG_INSTANCE_Number"]).strip(),
                    int(row["Leg_no"]),
                    _norm_date(row["LEG_INSTANCE_Date"]),
                    int(row["No_of_available_seats"])
                    if str(row.get("No_of_available_seats", "")).strip()
                    else None,
                    row["Airplane_id"].strip(),
                )
                for row in r
            ),
        )

    # --- SEAT.csv is physical layout → PHYSICAL_PLANE_SEAT ---
    with _open_csv(csv_dir, "SEAT.csv") as f:
        r = csv.DictReader(f)
        batch: list[tuple[str, str, str]] = []
        BATCH = 800
        for row in r:
            batch.append(
                (
                    row["Airplane_id"].strip(),
                    row["Seat_no"].strip(),
                    row["Class"].strip(),
                )
            )
            if len(batch) >= BATCH:
                conn.executemany(
                    "INSERT INTO PHYSICAL_PLANE_SEAT (Airplane_id, Seat_no, Class) VALUES (?,?,?)",
                    batch,
                )
                batch.clear()
        if batch:
            conn.executemany(
                "INSERT INTO PHYSICAL_PLANE_SEAT (Airplane_id, Seat_no, Class) VALUES (?,?,?)",
                batch,
            )

    conn.commit()
