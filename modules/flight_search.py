"""
flight_search.py — Flight Search Module
<<<<<<< HEAD
CS-4347 Airport Management System (Milestone 3)

Implements:
  flight(flight_number[, date])     → template and/or dated instance details
  trip(origin, destination, date)   → direct + 1-stop on a date (≥1h layover)
"""

from __future__ import annotations

from typing import Any

from modules.db import get_connection


def resolve_airport_code(identifier: str) -> list[str]:
    """
    Given a 3-letter code or a city name, return matching Airport_code(s).
    Case-insensitive.
    """
    conn = get_connection()
    identifier = identifier.strip()
    rows = conn.execute(
        "SELECT Airport_code FROM AIRPORT WHERE UPPER(Airport_code) = UPPER(?)",
        (identifier,),
    ).fetchall()
    if not rows:
        rows = conn.execute(
            "SELECT Airport_code FROM AIRPORT WHERE UPPER(City) LIKE UPPER(?)",
            (f"%{identifier}%",),
=======
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
>>>>>>> 5beb8ff18c4b0f299bb7d38fafd1ff805fbff25a
        ).fetchall()
    conn.close()
    return [r["Airport_code"] for r in rows]


<<<<<<< HEAD
# ── Layover: minutes between HH:MM times (same calendar day) ────────────────


def _layover_minutes(arr_hhmm: str, dep_hhmm: str) -> int:
    def to_min(t: str) -> int:
        parts = (t or "00:00").split(":")
        return int(parts[0]) * 60 + int(parts[1])

    return to_min(dep_hhmm) - to_min(arr_hhmm)


# ── Flight template (no specific date) ──────────────────────────────────────


def fetch_flight_template(flight_number: str) -> dict[str, Any] | None:
    """Return flight row + legs + fares for a flight number (schedule template)."""
    conn = get_connection()
    fn = flight_number.strip().upper()
    f_row = conn.execute(
        "SELECT * FROM FLIGHT WHERE UPPER(FLIGHT_Number) = ?", (fn,)
    ).fetchone()
    if not f_row:
        conn.close()
        return None
=======
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
>>>>>>> 5beb8ff18c4b0f299bb7d38fafd1ff805fbff25a
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
<<<<<<< HEAD
        (fn,),
    ).fetchall()
    fares = conn.execute(
        "SELECT Code, Amount, Restriction FROM FARE WHERE UPPER(Fare_Number) = ?",
        (fn,),
    ).fetchall()
    conn.close()
    return {
        "flight": dict(f_row),
        "legs": [dict(x) for x in legs],
        "fares": [dict(x) for x in fares],
    }


def flight(flight_number: str, date: str | None = None) -> None:
    """
    Print flight details. If `date` is set, show that day's leg instances
    (airline, flight number, date, times). Otherwise print the weekly template.
    """
    if date:
        rows = fetch_flight_instance_legs(flight_number, date)
        fn = flight_number.strip().upper()
        if not rows:
            print(f"[flight] No scheduled legs for {fn} on {date}")
            return
        print(f"\n{'='*55}")
        print(f"  Flight {fn}  on  {date}  ({rows[0]['Airline']})")
        print(f"{'='*55}")
        for r in rows:
            print(
                f"  Leg {r['Leg_no']}: {r['Departure_code']} → {r['Arrival_code']}  "
                f"{r['Scheduled_dep_time']} → {r['Scheduled_arr_time']}  "
                f"(aircraft {r['Airplane_id']})"
            )
        print()
        return

    data = fetch_flight_template(flight_number)
    if not data:
        print(f"[flight] No flight found with number '{flight_number}'")
        return
    f_row = data["flight"]
    print(f"\n{'='*55}")
    print(f"  Flight:  {f_row['FLIGHT_Number']}  ({f_row['Airline']})")
    print(f"  Operates: {f_row['Weekdays']}")
    print(f"{'='*55}")
    if not data["legs"]:
        print("  (No legs defined for this flight)")
    for leg in data["legs"]:
        print(
            f"  Leg {leg['Leg_no']:>2}: "
            f"{leg['Departure_code']} ({leg['dep_city']}) {leg['Scheduled_dep_time']}  →  "
            f"{leg['Arrival_code']} ({leg['arr_city']}) {leg['Scheduled_arr_time']}"
        )
    if data["fares"]:
        print("\n  Fares:")
        for fare in data["fares"]:
            restriction = f"  [{fare['Restriction']}]" if fare["Restriction"] else ""
            print(f"    {fare['Code']:<8} ${fare['Amount']:>8.2f}{restriction}")
    print()


def fetch_flight_instance_legs(flight_number: str, date: str) -> list[dict[str, Any]]:
    """Legs for a flight number on a specific date (from LEG_INSTANCE)."""
    conn = get_connection()
    fn = flight_number.strip().upper()
    rows = conn.execute(
        """
        SELECT  f.Airline,
                li.LEG_INSTANCE_Number AS flight_no,
                li.Leg_no,
                li.LEG_INSTANCE_Date AS flight_date,
                fl.Scheduled_dep_time,
                fl.Scheduled_arr_time,
                fl.Departure_code,
                fl.Arrival_code,
                li.Airplane_id
        FROM    LEG_INSTANCE li
        JOIN    FLIGHT f ON f.FLIGHT_Number = li.LEG_INSTANCE_Number
        JOIN    FLIGHT_LEG fl
                ON  fl.FLIGHT_LEG_Number = li.LEG_INSTANCE_Number
                AND fl.Leg_no            = li.Leg_no
        WHERE   UPPER(li.LEG_INSTANCE_Number) = ?
          AND   li.LEG_INSTANCE_Date          = ?
        ORDER   BY li.Leg_no
        """,
        (fn, date),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Trip search on a date (direct + one stop, ≥60 min connection) ───────────


def fetch_direct_routes(
    origin_code: str, dest_code: str, flight_date: str
) -> list[dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT  f.Airline,
                fl.FLIGHT_LEG_Number AS flight_no,
                fl.Leg_no,
                li.LEG_INSTANCE_Date AS flight_date,
                fl.Scheduled_dep_time,
                fl.Scheduled_arr_time,
                fl.Departure_code,
                fl.Arrival_code
        FROM    FLIGHT_LEG fl
        JOIN    FLIGHT f ON f.FLIGHT_Number = fl.FLIGHT_LEG_Number
        JOIN    LEG_INSTANCE li
                ON  li.LEG_INSTANCE_Number = fl.FLIGHT_LEG_Number
                AND li.Leg_no              = fl.Leg_no
                AND li.LEG_INSTANCE_Date   = ?
        WHERE   fl.Departure_code = ?
          AND   fl.Arrival_code   = ?
        ORDER   BY fl.Scheduled_dep_time
        """,
        (flight_date, origin_code, dest_code),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def fetch_one_stop_routes(
    origin_code: str, dest_code: str, flight_date: str
) -> list[dict[str, Any]]:
    """
    Two-leg itineraries on the same calendar date with at least 60 minutes
    between first leg arrival and second leg departure.
    """
    conn = get_connection()
    raw = conn.execute(
        """
        SELECT  f1.Airline              AS airline1,
                leg1.FLIGHT_LEG_Number  AS flight1,
                leg1.Leg_no             AS leg1_no,
                li1.LEG_INSTANCE_Date   AS flight_date,
                leg1.Scheduled_dep_time AS dep1,
                leg1.Scheduled_arr_time AS arr1,
                leg1.Departure_code     AS dep_code1,
                leg1.Arrival_code       AS connect_code,
                ca.City                 AS connect_city,
                f2.Airline              AS airline2,
                leg2.FLIGHT_LEG_Number  AS flight2,
                leg2.Leg_no             AS leg2_no,
                leg2.Scheduled_dep_time AS dep2,
                leg2.Scheduled_arr_time AS arr2,
                leg2.Arrival_code       AS arr_code2
        FROM    FLIGHT_LEG leg1
        JOIN    FLIGHT f1 ON f1.FLIGHT_Number = leg1.FLIGHT_LEG_Number
        JOIN    LEG_INSTANCE li1
                ON  li1.LEG_INSTANCE_Number = leg1.FLIGHT_LEG_Number
                AND li1.Leg_no              = leg1.Leg_no
                AND li1.LEG_INSTANCE_Date   = ?
        JOIN    FLIGHT_LEG leg2
                ON  leg2.Departure_code = leg1.Arrival_code
                AND leg2.Arrival_code   = ?
        JOIN    FLIGHT f2 ON f2.FLIGHT_Number = leg2.FLIGHT_LEG_Number
        JOIN    LEG_INSTANCE li2
                ON  li2.LEG_INSTANCE_Number = leg2.FLIGHT_LEG_Number
                AND li2.Leg_no              = leg2.Leg_no
                AND li2.LEG_INSTANCE_Date   = li1.LEG_INSTANCE_Date
        JOIN    AIRPORT ca ON ca.Airport_code = leg1.Arrival_code
        WHERE   leg1.Departure_code = ?
          AND   leg1.Arrival_code  != ?
        ORDER   BY leg1.Scheduled_dep_time, leg2.Scheduled_dep_time
        """,
        (flight_date, dest_code, origin_code, dest_code),
    ).fetchall()
    conn.close()
    out: list[dict[str, Any]] = []
    for r in raw:
        d = dict(r)
        if _layover_minutes(d["arr1"], d["dep2"]) >= 60:
            out.append(d)
    return out


def trip(origin: str, destination: str, flight_date: str) -> None:
    """
    Direct and one-stop itineraries on `flight_date` between two airports.
    `origin` / `destination` may be codes or city names.
=======
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
>>>>>>> 5beb8ff18c4b0f299bb7d38fafd1ff805fbff25a
    """
    orig_codes = resolve_airport_code(origin)
    dest_codes = resolve_airport_code(destination)

    if not orig_codes:
        print(f"[trip] Could not resolve origin: '{origin}'")
        return
    if not dest_codes:
        print(f"[trip] Could not resolve destination: '{destination}'")
        return

<<<<<<< HEAD
=======
    conn = get_connection()
>>>>>>> 5beb8ff18c4b0f299bb7d38fafd1ff805fbff25a
    found_any = False

    for orig in orig_codes:
        for dest in dest_codes:
            print(f"\n{'='*55}")
<<<<<<< HEAD
            print(f"  Trip search: {orig} → {dest}  on  {flight_date}")
            print(f"{'='*55}")

            directs = fetch_direct_routes(orig, dest, flight_date)
=======
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

>>>>>>> 5beb8ff18c4b0f299bb7d38fafd1ff805fbff25a
            if directs:
                print(f"\n  Direct flights ({len(directs)} found):")
                for d in directs:
                    print(
<<<<<<< HEAD
                        f"    {d['Airline']}  {d['flight_no']}  Leg {d['Leg_no']}  "
                        f"{d['flight_date']}  {d['Scheduled_dep_time']} → {d['Scheduled_arr_time']}"
=======
                        f"    {d['flight_no']} (Leg {d['Leg_no']})  "
                        f"{d['Airline']}  "
                        f"{d['Scheduled_dep_time']} -> {d['Scheduled_arr_time']}"
>>>>>>> 5beb8ff18c4b0f299bb7d38fafd1ff805fbff25a
                    )
                found_any = True
            else:
                print("\n  No direct flights found.")

<<<<<<< HEAD
            connections = fetch_one_stop_routes(orig, dest, flight_date)
            if connections:
                print(f"\n  1-stop connections ({len(connections)} found, ≥1h layover):")
                for c in connections:
                    print(
                        f"    Leg 1: {c['airline1']}  {c['flight1']}  {c['dep1']}→{c['arr1']}  "
                        f"via {c['connect_code']} ({c['connect_city']})"
                    )
                    print(
                        f"    Leg 2: {c['airline2']}  {c['flight2']}  {c['dep2']}→{c['arr2']}"
                    )
                found_any = True
            else:
                print("  No qualifying 1-stop connections found.")

    if not found_any:
        print("\n  No itineraries found for that date.")
    print()
=======
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
>>>>>>> 5beb8ff18c4b0f299bb7d38fafd1ff805fbff25a
