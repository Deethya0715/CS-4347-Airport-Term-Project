"""
booking.py — Passenger & Booking Queries Module
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
        booked = conn.execute(
            """
            SELECT COUNT(*) AS cnt
            FROM   SEAT
            WHERE  UPPER(Flight_Number) = ?
              AND  Leg_no    = ?
              AND  Seat_Date = ?
            """,
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

    current_pax = None
    for r in rows:
        if r["Customer_name"] != current_pax:
            current_pax = r["Customer_name"]
            print(f"\n  Passenger: {current_pax}   Phone: {r['Cphone'] or 'N/A'}")
            print(f"  {'-'*60}")

        print(
            f"  {r['Seat_Date']}  Flight {r['Flight_Number']} Leg {r['Leg_no']}"
            f"  Seat {r['Seat_no']}"
        )
        print(
            f"           {r['Departure_code']} ({r['dep_city']}) "
            f"{r['Scheduled_dep_time']}  ->  "
            f"{r['Arrival_code']} ({r['arr_city']}) "
            f"{r['Scheduled_arr_time']}"
        )
        print(f"           Aircraft: {r['Airplane_id']}")

    print()
    conn.close()
