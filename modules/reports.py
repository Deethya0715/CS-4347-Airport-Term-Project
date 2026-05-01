"""
reports.py — Infrastructure Reports (Requirement 3)
CS-4347 Airport Management System

Aircraft Utilization Report:
  For a given time period, list every airplane (by registration number and
  aircraft type) with the total number of flights it was assigned to — supports
  maintenance planners scheduling inspections from usage cycles.

  aircraft_utilization_report(start_date, end_date)
"""

from modules.db import get_connection


def aircraft_utilization_report(start_date: str, end_date: str) -> None:
    """
    Print an Aircraft Utilization Report for the given date range.

    Parameters
    ----------
    start_date : str  — "YYYY-MM-DD"
    end_date   : str  — "YYYY-MM-DD"

    Example
    -------
    aircraft_utilization_report("2025-08-01", "2025-08-31")
    """
    conn = get_connection()

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
        (start_date, end_date)
    ).fetchall()

    print(f"\n{'='*65}")
    print(f"  AIRCRAFT UTILIZATION REPORT  [{start_date}  to  {end_date}]")
    print(f"{'='*65}")
    print(f"  {'Reg. No.':<12}  {'Type':<14}  {'Company':<10}  {'Seats':>5}  {'Flights':>7}")
    print(f"  {'-'*12}  {'-'*14}  {'-'*10}  {'-'*5}  {'-'*7}")

    if not rows:
        print("  (No data found for this period)")
    for r in rows:
        print(
            f"  {r['Airplane_id']:<12}  "
            f"{r['Type_name']:<14}  "
            f"{r['Company']:<10}  "
            f"{r['Total_no_of_seats']:>5}  "
            f"{r['total_flights']:>7}"
        )

    print()
    conn.close()
