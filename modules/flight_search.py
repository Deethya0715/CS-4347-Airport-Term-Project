"""
flight_search.py — Flight Search Module
CS-4347 Airport Management System

Implements:
  flight(flight_number)          → details of a single flight
  trip(origin, destination)      → direct + 1-stop itineraries
"""

from modules.db import get_connection


# ──────────────────────────────────────────────────────────────
# Helper: resolve airport code from either a code or city name
# ──────────────────────────────────────────────────────────────

def resolve_airport_code(identifier: str) -> list[str]:
    """
    Given a 3-letter code or a city name, return matching Airport_code(s).
    Case-insensitive. Returns a list (a city might have multiple airports).
    """
    conn = get_connection()
    identifier = identifier.strip()
    # Try exact code match first
    rows = conn.execute(
        "SELECT Airport_code FROM AIRPORT WHERE UPPER(Airport_code) = UPPER(?)",
        (identifier,)
    ).fetchall()
    if not rows:
        # Fallback: city name substring match
        rows = conn.execute(
            "SELECT Airport_code FROM AIRPORT WHERE UPPER(City) LIKE UPPER(?)",
            (f"%{identifier}%",)
        ).fetchall()
    conn.close()
    return [r["Airport_code"] for r in rows]


# ──────────────────────────────────────────────────────────────
# flight(flight_number)
# ──────────────────────────────────────────────────────────────

def flight(flight_number: str) -> None:
    """
    Print details for every leg of the given flight number.
    Usage: flight("AA3478")
    """
    conn = get_connection()
    fn = flight_number.strip().upper()

    # Basic flight info
    f_row = conn.execute(
        "SELECT * FROM FLIGHT WHERE UPPER(FLIGHT_Number) = ?", (fn,)
    ).fetchone()

    if not f_row:
        print(f"[flight] No flight found with number '{flight_number}'")
        conn.close()
        return

    print(f"\n{'='*55}")
    print(f"  Flight:  {f_row['FLIGHT_Number']}  ({f_row['Airline']})")
    print(f"  Operates: {f_row['Weekdays']}")
    print(f"{'='*55}")

    # Legs
    legs = conn.execute(
        """
        SELECT fl.Leg_no,
               fl.Departure_code, da.City AS dep_city,
               fl.Arrival_code,   aa.City AS arr_city,
               fl.Scheduled_dep_time, fl.Scheduled_arr_time
        FROM   FLIGHT_LEG fl
        JOIN   AIRPORT da ON da.Airport_code = fl.Departure_code
        JOIN   AIRPORT aa ON aa.Airport_code = fl.Arrival_code
        WHERE  UPPER(fl.FLIGHT_LEG_Number) = ?
        ORDER  BY fl.Leg_no
        """,
        (fn,)
    ).fetchall()

    if not legs:
        print("  (No legs defined for this flight)")
    for leg in legs:
        print(
            f"  Leg {leg['Leg_no']:>2}: "
            f"{leg['Departure_code']} ({leg['dep_city']}) {leg['Scheduled_dep_time']}  ->  "
            f"{leg['Arrival_code']} ({leg['arr_city']}) {leg['Scheduled_arr_time']}"
        )

    # Fares
    fares = conn.execute(
        "SELECT Code, Amount, Restriction FROM FARE WHERE UPPER(Fare_Number) = ?",
        (fn,)
    ).fetchall()

    if fares:
        print(f"\n  Fares:")
        for fare in fares:
            restriction = f"  [{fare['Restriction']}]" if fare['Restriction'] else ""
            print(f"    {fare['Code']:<8} ${fare['Amount']:>8.2f}{restriction}")

    print()
    conn.close()


# ──────────────────────────────────────────────────────────────
# trip(origin, destination)
# ──────────────────────────────────────────────────────────────

def trip(origin: str, destination: str) -> None:
    """
    Search for direct and 1-stop itineraries between two airports.
    origin / destination may be 3-letter codes or city names.
    Usage: trip("DFW", "SFO")  or  trip("Dallas", "San Francisco")
    """
    orig_codes = resolve_airport_code(origin)
    dest_codes = resolve_airport_code(destination)

    if not orig_codes:
        print(f"[trip] Could not resolve origin: '{origin}'")
        return
    if not dest_codes:
        print(f"[trip] Could not resolve destination: '{destination}'")
        return

    conn = get_connection()
    found_any = False

    for orig in orig_codes:
        for dest in dest_codes:
            print(f"\n{'='*55}")
            print(f"  Trip search: {orig} -> {dest}")
            print(f"{'='*55}")

            # ── Direct flights ────────────────────────────────
            directs = conn.execute(
                """
                SELECT fl.FLIGHT_LEG_Number  AS flight_no,
                       fl.Leg_no,
                       f.Airline,
                       fl.Scheduled_dep_time,
                       fl.Scheduled_arr_time
                FROM   FLIGHT_LEG fl
                JOIN   FLIGHT f ON f.FLIGHT_Number = fl.FLIGHT_LEG_Number
                WHERE  fl.Departure_code = ?
                  AND  fl.Arrival_code   = ?
                ORDER  BY fl.Scheduled_dep_time
                """,
                (orig, dest)
            ).fetchall()

            if directs:
                print(f"\n  Direct flights ({len(directs)} found):")
                for d in directs:
                    print(
                        f"    {d['flight_no']} (Leg {d['Leg_no']})  "
                        f"{d['Airline']}  "
                        f"{d['Scheduled_dep_time']} -> {d['Scheduled_arr_time']}"
                    )
                found_any = True
            else:
                print("\n  No direct flights found.")

            # ── 1-stop connections ────────────────────────────
            connections = conn.execute(
                """
                SELECT leg1.FLIGHT_LEG_Number  AS flight1,
                       leg1.Leg_no             AS leg1_no,
                       f1.Airline              AS airline1,
                       leg1.Scheduled_dep_time AS dep1,
                       leg1.Scheduled_arr_time AS arr1,
                       leg1.Arrival_code       AS connect_code,
                       ca.City                 AS connect_city,
                       leg2.FLIGHT_LEG_Number  AS flight2,
                       leg2.Leg_no             AS leg2_no,
                       f2.Airline              AS airline2,
                       leg2.Scheduled_dep_time AS dep2,
                       leg2.Scheduled_arr_time AS arr2
                FROM   FLIGHT_LEG leg1
                JOIN   FLIGHT f1  ON f1.FLIGHT_Number = leg1.FLIGHT_LEG_Number
                JOIN   FLIGHT_LEG leg2
                         ON  leg2.Departure_code = leg1.Arrival_code
                         AND leg2.Arrival_code   = ?
                         AND leg2.Scheduled_dep_time > leg1.Scheduled_arr_time
                JOIN   FLIGHT f2  ON f2.FLIGHT_Number = leg2.FLIGHT_LEG_Number
                JOIN   AIRPORT ca ON ca.Airport_code  = leg1.Arrival_code
                WHERE  leg1.Departure_code = ?
                  AND  leg1.Arrival_code  != ?
                ORDER  BY leg1.Scheduled_dep_time, leg2.Scheduled_dep_time
                """,
                (dest, orig, dest)
            ).fetchall()

            if connections:
                print(f"\n  1-stop connections ({len(connections)} found):")
                for c in connections:
                    print(
                        f"    {c['flight1']} (Leg {c['leg1_no']}) {c['dep1']}->{c['arr1']}"
                        f"  connect {c['connect_code']} ({c['connect_city']})"
                        f"  {c['flight2']} (Leg {c['leg2_no']}) {c['dep2']}->{c['arr2']}"
                    )
                found_any = True
            else:
                print("  No 1-stop connections found.")

    if not found_any:
        print("\n  No itineraries found between those airports.")

    print()
    conn.close()
