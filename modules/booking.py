"""
booking.py — Passenger & Booking Queries Module
<<<<<<< HEAD
CS-4347 Airport Management System (Milestone 3)

Implements:
  seat_availability(flight_number, date)
  book_seat(...)
  passenger_itinerary(customer)  — name (partial) or Customer_id
"""

from __future__ import annotations

from typing import Any

from modules.db import get_connection


def fetch_seat_availability(flight_number: str, date: str) -> list[dict[str, Any]]:
    """Return one row per leg instance with capacity / booked / remaining."""
    conn = get_connection()
    fn = flight_number.strip().upper()
=======
CS-4347 Airport Management System

Implements:
  seat_availability(flight_number, date)
    → Counts seats on the airplane type vs confirmed reservations.

  passenger_itinerary(customer)
    → Returns all flight legs booked under a customer name or ID.
"""

from modules.db import get_connection


# ──────────────────────────────────────────────────────────────
# Seat Availability Check
# ──────────────────────────────────────────────────────────────

def seat_availability(flight_number: str, date: str) -> None:
    """
    For a specific flight instance (flight_number + date), show:
      - airplane assigned
      - total physical seats on the airplane
      - confirmed reservations
      - remaining capacity

    Parameters
    ----------
    flight_number : str  — e.g. "AA3478"
    date          : str  — "YYYY-MM-DD"

    Example
    -------
    seat_availability("AA3478", "2025-08-01")
    """
    conn = get_connection()
    fn   = flight_number.strip().upper()

    # Fetch all legs of this flight on this date
>>>>>>> 5beb8ff18c4b0f299bb7d38fafd1ff805fbff25a
    legs = conn.execute(
        """
        SELECT  li.Leg_no,
                li.Airplane_id,
                a.Total_no_of_seats,
                at.Type_name,
                fl.Departure_code,
                fl.Arrival_code,
                fl.Scheduled_dep_time,
                fl.Scheduled_arr_time
        FROM    LEG_INSTANCE li
        JOIN    AIRPLANE a   ON a.Airplane_id    = li.Airplane_id
        JOIN    AIRPLANE_TYPE at ON at.Type_name = a.Type_name
        JOIN    FLIGHT_LEG fl
                ON fl.FLIGHT_LEG_Number = li.LEG_INSTANCE_Number
               AND fl.Leg_no            = li.Leg_no
        WHERE   UPPER(li.LEG_INSTANCE_Number) = ?
          AND   li.LEG_INSTANCE_Date          = ?
        ORDER   BY li.Leg_no
        """,
<<<<<<< HEAD
        (fn, date),
    ).fetchall()
    result: list[dict[str, Any]] = []
    for leg in legs:
=======
        (fn, date)
    ).fetchall()

    if not legs:
        print(f"\n[seat_availability] No instance found for {fn} on {date}")
        conn.close()
        return

    print(f"\n{'='*55}")
    print(f"  Seat Availability - Flight {fn}  on  {date}")
    print(f"{'='*55}")

    for leg in legs:
        # Count confirmed reservations for this leg instance
>>>>>>> 5beb8ff18c4b0f299bb7d38fafd1ff805fbff25a
        booked = conn.execute(
            """
            SELECT COUNT(*) AS cnt
            FROM   SEAT
            WHERE  UPPER(Flight_Number) = ?
              AND  Leg_no    = ?
              AND  Seat_Date = ?
            """,
<<<<<<< HEAD
            (fn, leg["Leg_no"], date),
        ).fetchone()["cnt"]
        cap = leg["Total_no_of_seats"]
        result.append(
            {
                "Leg_no": leg["Leg_no"],
                "Airplane_id": leg["Airplane_id"],
                "Type_name": leg["Type_name"],
                "Departure_code": leg["Departure_code"],
                "Arrival_code": leg["Arrival_code"],
                "Scheduled_dep_time": leg["Scheduled_dep_time"],
                "Scheduled_arr_time": leg["Scheduled_arr_time"],
                "capacity": cap,
                "booked": booked,
                "remaining": cap - booked,
            }
        )
    conn.close()
    return result


def seat_availability(flight_number: str, date: str) -> None:
    legs = fetch_seat_availability(flight_number, date)
    fn = flight_number.strip().upper()
    if not legs:
        print(f"\n[seat_availability] No instance found for {fn} on {date}")
        return
    print(f"\n{'='*55}")
    print(f"  Seat Availability — Flight {fn}  on  {date}")
    print(f"{'='*55}")
    for leg in legs:
        print(
            f"\n  Leg {leg['Leg_no']}: "
            f"{leg['Departure_code']} {leg['Scheduled_dep_time']} → "
            f"{leg['Arrival_code']} {leg['Scheduled_arr_time']}"
        )
        print(f"    Airplane : {leg['Airplane_id']} ({leg['Type_name']})")
        print(f"    Capacity : {leg['capacity']}")
        print(f"    Booked   : {leg['booked']}")
        print(f"    Available: {leg['remaining']}")
    print()


def book_seat(
    flight_number: str,
    leg_no: int,
    date: str,
    seat_no: str,
    customer_name: str,
    phone: str | None = None,
    customer_id: str | None = None,
) -> tuple[bool, str]:
    """
    Insert a reservation. Returns (ok, message).
    """
    conn = get_connection()
    fn = flight_number.strip().upper()
    seat_no = seat_no.strip()
    try:
        leg_no = int(leg_no)
    except (TypeError, ValueError):
        conn.close()
        return False, "Leg number must be an integer."

    li = conn.execute(
        """
        SELECT li.Airplane_id, a.Total_no_of_seats
        FROM   LEG_INSTANCE li
        JOIN   AIRPLANE a ON a.Airplane_id = li.Airplane_id
        WHERE  UPPER(li.LEG_INSTANCE_Number) = ?
          AND  li.Leg_no = ?
          AND  li.LEG_INSTANCE_Date = ?
        """,
        (fn, leg_no, date),
    ).fetchone()
    if not li:
        conn.close()
        return False, f"No flight instance for {fn} leg {leg_no} on {date}."

    booked = conn.execute(
        """
        SELECT COUNT(*) AS c FROM SEAT
        WHERE UPPER(Flight_Number)=? AND Leg_no=? AND Seat_Date=?
        """,
        (fn, leg_no, date),
    ).fetchone()["c"]
    if booked >= li["Total_no_of_seats"]:
        conn.close()
        return False, "Flight is full; no seats available."

    dup = conn.execute(
        """
        SELECT 1 FROM SEAT
        WHERE UPPER(Flight_Number)=? AND Leg_no=? AND Seat_Date=? AND Seat_no=?
        """,
        (fn, leg_no, date, seat_no),
    ).fetchone()
    if dup:
        conn.close()
        return False, f"Seat {seat_no} is already taken on this leg."

    try:
        conn.execute(
            """
            INSERT INTO SEAT (Seat_no, Flight_Number, Leg_no, Seat_Date, Customer_name, Cphone, Customer_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                seat_no,
                fn,
                leg_no,
                date,
                customer_name.strip(),
                (phone or "").strip() or None,
                (customer_id or "").strip() or None,
            ),
        )
        conn.commit()
    except Exception as e:  # noqa: BLE001 — surface FK/sqlite errors to user
        conn.close()
        return False, str(e)
    conn.close()
    return True, f"Booked seat {seat_no} on {fn} leg {leg_no} for {customer_name}."


def fetch_passenger_itinerary(customer: str) -> list[dict[str, Any]]:
    """Match Customer_id (exact, case-insensitive) OR Customer_name (LIKE)."""
    conn = get_connection()
    q = customer.strip()
    rows = conn.execute(
        """
        SELECT  s.Customer_name,
                s.Customer_id,
=======
            (fn, leg["Leg_no"], date)
        ).fetchone()["cnt"]

        capacity  = leg["Total_no_of_seats"]
        remaining = capacity - booked

        print(f"\n  Leg {leg['Leg_no']}: "
              f"{leg['Departure_code']} {leg['Scheduled_dep_time']} -> "
              f"{leg['Arrival_code']} {leg['Scheduled_arr_time']}")
        print(f"    Airplane : {leg['Airplane_id']} ({leg['Type_name']})")
        print(f"    Capacity : {capacity}")
        print(f"    Booked   : {booked}")
        print(f"    Available: {remaining}")

    print()
    conn.close()


# ──────────────────────────────────────────────────────────────
# Passenger Itinerary Retrieval
# ──────────────────────────────────────────────────────────────

def passenger_itinerary(customer: str) -> None:
    """
    Given a customer name (or partial name), return all flight legs
    they are booked on, including connection airports, scheduled times,
    and seat assignments.

    Parameters
    ----------
    customer : str  — full or partial name, case-insensitive

    Example
    -------
    passenger_itinerary("Bob Jones")
    passenger_itinerary("bob")
    """
    conn = get_connection()

    rows = conn.execute(
        """
        SELECT  s.Customer_name,
>>>>>>> 5beb8ff18c4b0f299bb7d38fafd1ff805fbff25a
                s.Cphone,
                s.Flight_Number,
                s.Leg_no,
                s.Seat_Date,
                s.Seat_no,
                fl.Departure_code,
                da.City          AS dep_city,
                fl.Arrival_code,
                aa.City          AS arr_city,
                fl.Scheduled_dep_time,
                fl.Scheduled_arr_time,
                li.Airplane_id
        FROM    SEAT s
        JOIN    FLIGHT_LEG fl
                ON  UPPER(fl.FLIGHT_LEG_Number) = UPPER(s.Flight_Number)
                AND fl.Leg_no                   = s.Leg_no
        JOIN    AIRPORT da ON da.Airport_code = fl.Departure_code
        JOIN    AIRPORT aa ON aa.Airport_code = fl.Arrival_code
        JOIN    LEG_INSTANCE li
                ON  UPPER(li.LEG_INSTANCE_Number) = UPPER(s.Flight_Number)
                AND li.Leg_no                     = s.Leg_no
                AND li.LEG_INSTANCE_Date          = s.Seat_Date
<<<<<<< HEAD
        WHERE   UPPER(IFNULL(s.Customer_id,'')) = UPPER(?)
           OR   UPPER(s.Customer_name) LIKE UPPER(?)
        ORDER   BY s.Customer_name, s.Seat_Date, s.Flight_Number, s.Leg_no
        """,
        (q, f"%{q}%"),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def passenger_itinerary(customer: str) -> None:
    rows = fetch_passenger_itinerary(customer)
    if not rows:
        print(f"\n[passenger_itinerary] No bookings found for '{customer}'")
        return
    print(f"\n{'='*65}")
    print(f"  Passenger Itinerary — search: '{customer}'")
    print(f"{'='*65}")
=======
        WHERE   UPPER(s.Customer_name) LIKE UPPER(?)
        ORDER   BY s.Customer_name, s.Seat_Date, s.Flight_Number, s.Leg_no
        """,
        (f"%{customer}%",)
    ).fetchall()

    if not rows:
        print(f"\n[passenger_itinerary] No bookings found for '{customer}'")
        conn.close()
        return

    print(f"\n{'='*65}")
    print(f"  Passenger Itinerary - search: '{customer}'")
    print(f"{'='*65}")

>>>>>>> 5beb8ff18c4b0f299bb7d38fafd1ff805fbff25a
    current_pax = None
    for r in rows:
        if r["Customer_name"] != current_pax:
            current_pax = r["Customer_name"]
<<<<<<< HEAD
            cid = r["Customer_id"] or "N/A"
            print(f"\n  Passenger: {current_pax}   ID: {cid}   Phone: {r['Cphone'] or 'N/A'}")
            print(f"  {'-'*60}")
=======
            print(f"\n  Passenger: {current_pax}   Phone: {r['Cphone'] or 'N/A'}")
            print(f"  {'-'*60}")

>>>>>>> 5beb8ff18c4b0f299bb7d38fafd1ff805fbff25a
        print(
            f"  {r['Seat_Date']}  Flight {r['Flight_Number']} Leg {r['Leg_no']}"
            f"  Seat {r['Seat_no']}"
        )
        print(
            f"           {r['Departure_code']} ({r['dep_city']}) "
<<<<<<< HEAD
            f"{r['Scheduled_dep_time']}  →  "
=======
            f"{r['Scheduled_dep_time']}  ->  "
>>>>>>> 5beb8ff18c4b0f299bb7d38fafd1ff805fbff25a
            f"{r['Arrival_code']} ({r['arr_city']}) "
            f"{r['Scheduled_arr_time']}"
        )
        print(f"           Aircraft: {r['Airplane_id']}")
<<<<<<< HEAD
    print()
=======

    print()
    conn.close()
>>>>>>> 5beb8ff18c4b0f299bb7d38fafd1ff805fbff25a
