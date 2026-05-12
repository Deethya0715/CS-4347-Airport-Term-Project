"""
reports.py - Infrastructure Reports Module
CS-4347 Airport Management System (Milestone 3)

Implements:
  aircraft_utilization_report(start_date, end_date[, airplane_id])
"""

from __future__ import annotations

from typing import Any

from modules.db import get_connection


def fetch_aircraft_utilization(
    start_date: str, end_date: str, airplane_id: str | None = None
) -> list[dict[str, Any]]:
    """
    Rows: Airplane_id, Type_name, Company, Total_no_of_seats, total_flights.
    If airplane_id is set, restrict to that registration.
    """
    conn = get_connection()
    if airplane_id and airplane_id.strip():
        aid = airplane_id.strip()
        rows = conn.execute(
            """
            SELECT  a.Airplane_id,
                    a.Type_name,
                    at.Company,
                    a.Total_no_of_seats,
                    COUNT(li.LEG_INSTANCE_Number) AS total_flights
            FROM    AIRPLANE a
            JOIN    AIRPLANE_TYPE at ON at.Type_name = a.Type_name
            LEFT JOIN LEG_INSTANCE li
                    ON  li.Airplane_id        = a.Airplane_id
                    AND li.LEG_INSTANCE_Date >= ?
                    AND li.LEG_INSTANCE_Date <= ?
            WHERE   a.Airplane_id = ?
            GROUP   BY a.Airplane_id, a.Type_name, at.Company, a.Total_no_of_seats
            ORDER   BY a.Airplane_id
            """,
            (start_date, end_date, aid),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT  a.Airplane_id,
                    a.Type_name,
                    at.Company,
                    a.Total_no_of_seats,
                    COUNT(li.LEG_INSTANCE_Number) AS total_flights
            FROM    AIRPLANE a
            JOIN    AIRPLANE_TYPE at ON at.Type_name = a.Type_name
            LEFT JOIN LEG_INSTANCE li
                    ON  li.Airplane_id        = a.Airplane_id
                    AND li.LEG_INSTANCE_Date >= ?
                    AND li.LEG_INSTANCE_Date <= ?
            GROUP   BY a.Airplane_id, a.Type_name, at.Company, a.Total_no_of_seats
            ORDER   BY total_flights DESC, a.Airplane_id
            """,
            (start_date, end_date),
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def aircraft_utilization_report(
    start_date: str, end_date: str, airplane_id: str | None = None
) -> None:
    rows = fetch_aircraft_utilization(start_date, end_date, airplane_id)
    title_extra = f"  [{airplane_id}]" if airplane_id and airplane_id.strip() else ""
    print(f"\n{'='*65}")
    print(f"  AIRCRAFT UTILIZATION REPORT  [{start_date}  to  {end_date}]{title_extra}")
    print(f"{'='*65}")
    print(f"  {'Reg. No.':<12}  {'Type':<14}  {'Company':<10}  {'Seats':>5}  {'Flights':>7}")
    print(f"  {'-'*12}  {'-'*14}  {'-'*10}  {'-'*5}  {'-'*7}")
    if not rows:
        print("  (No data found for this period / registration)")
    for r in rows:
        print(
            f"  {r['Airplane_id']:<12}  "
            f"{r['Type_name']:<14}  "
            f"{r['Company']:<10}  "
            f"{r['Total_no_of_seats']:>5}  "
            f"{r['total_flights']:>7}"
        )
    print()
