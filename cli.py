#!/usr/bin/env python3
"""
cli.py — Command-Line Interface
CS-4347 Airport Management System

Usage
-----
  python cli.py                              # interactive REPL
  python cli.py --init                       # schema + load ./data/*.csv if present
  python cli.py --init --data path/to/csv    # schema + load CSVs from that folder
  python cli.py --init --seed                # schema + small sql/seed.sql sample only
  python cli.py --init --repl                # init then open the REPL
  python cli.py --cmd "flight(1000)"         # run one REPL-style command and exit

Commands inside the REPL
------------------------
  flight(<number>)
  trip(<origin>, <destination>)
  availability(<flight_number>, <date>)
  itinerary(<customer_name>)
  report(<start_date>, <end_date>)
  help
  exit / quit
"""

import sys
import re
import argparse

# ── Add project root to path so `modules` is importable ──────
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.db            import init_db
from modules.flight_search import flight, trip
from modules.booking       import seat_availability, passenger_itinerary
from modules.reports       import aircraft_utilization_report


HELP_TEXT = """
  Commands:
    flight(<number>)                  — details for a flight number
    trip(<origin>, <dest>)            — direct + 1-stop itineraries
    availability(<flight>, <date>)    — seat availability for a flight on a date
    itinerary(<name>)                 — all bookings for a passenger
    report(<start_date>, <end_date>)  — (3) Infrastructure: Aircraft Utilization
                                        Report — every airplane (registration / type)
                                        and total flights assigned in the period
                                        (helps maintenance plan inspection cycles)

  Dates use YYYY-MM-DD. Airports: 3-letter codes or city names.

  Examples (professor data in ./data after: python cli.py --init):
    flight(1000)
    trip("DFW", "MEX")
    availability(1000, 2025-10-04)
    report(2025-10-04, 2025-10-11)
    itinerary("Jane Doe")            # valid; prints nothing if SEAT has no bookings

  Type 'exit' or 'quit' to leave.
"""

CLI_EXAMPLES = """
Shell examples (from project root; --init loads ./data CSVs if data/FLIGHT.csv exists):
  python cli.py --init
  python cli.py --init --data DIR
  python cli.py --init --repl
  python cli.py --cmd "flight(1000)"
  python cli.py --cmd "availability(1000, 2025-10-04)"
  python cli.py --cmd "report(2025-10-04, 2025-10-11)"   # aircraft utilization

PowerShell (trip needs single quotes on the outside so airport codes can use double quotes):
  python cli.py --cmd 'trip("DFW", "MEX")'
"""


def parse_args_from_input(raw: str):
    """
    Strip command name and parentheses, return a list of unquoted args.
    e.g.  'trip("DFW", "SFO")'  →  ['DFW', 'SFO']
    """
    # Extract everything inside the outer parentheses
    m = re.search(r'\((.+)\)', raw, re.DOTALL)
    if not m:
        return []
    inner = m.group(1)
    # Split on commas, strip whitespace and quotes
    parts = [p.strip().strip('"').strip("'") for p in inner.split(",")]
    return [p for p in parts if p]


def dispatch(line: str) -> bool:
    """
    Parse and execute a single command line.
    Returns False if the user wants to quit, True otherwise.
    """
    line = line.strip()
    if not line or line.startswith("#"):
        return True

    low = line.lower()

    if low in ("exit", "quit"):
        print("Goodbye.")
        return False

    if low == "help":
        print(HELP_TEXT)
        return True

    args = parse_args_from_input(line)

    if low.startswith("flight("):
        if len(args) != 1:
            print("  Usage: flight(<flight_number>)")
        else:
            flight(args[0])

    elif low.startswith("trip("):
        if len(args) != 2:
            print("  Usage: trip(<origin>, <destination>)")
        else:
            trip(args[0], args[1])

    elif low.startswith("availability("):
        if len(args) != 2:
            print("  Usage: availability(<flight_number>, <date>)")
        else:
            seat_availability(args[0], args[1])

    elif low.startswith("itinerary("):
        if len(args) != 1:
            print("  Usage: itinerary(<customer_name>)")
        else:
            passenger_itinerary(args[0])

    elif low.startswith("report("):
        if len(args) != 2:
            print("  Usage: report(<start_date>, <end_date>)")
        else:
            aircraft_utilization_report(args[0], args[1])

    else:
        print(f"  Unknown command. Type 'help' for a list.")

    return True


def repl():
    print("CS-4347 Airport Management System")
    print("Type 'help' for available commands, 'exit' to quit.\n")
    while True:
        try:
            line = input("prompt> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break
        if not dispatch(line):
            break


def main():
    parser = argparse.ArgumentParser(
        description="CS-4347 Airport Management CLI",
        epilog=CLI_EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--init",  action="store_true", help="Initialize (or reset) the database")
    parser.add_argument("--seed",  action="store_true", help="Load sql/seed.sql sample data (--data overrides)")
    parser.add_argument(
        "--data",
        type=str,
        metavar="DIR",
        help="Load professor CSVs from DIR (AIRPORT, FLIGHT, ...). Default: ./data if FLIGHT.csv exists",
    )
    parser.add_argument("--repl",  action="store_true", help="Open interactive REPL after --init")
    parser.add_argument("--cmd",   type=str,            help="Run a single command and exit")
    args = parser.parse_args()

    if args.init:
        csv_dir = args.data
        seed_path = "sql/seed.sql" if args.seed else None
        if args.seed and csv_dir:
            print("[cli] --seed ignored because --data was set.")
            seed_path = None
        if not csv_dir and not args.seed:
            default_data = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "FLIGHT.csv")
            if os.path.isfile(default_data):
                csv_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        init_db(schema_path="sql/schema.sql", seed_path=seed_path, csv_dir=csv_dir)
        if not args.repl and not args.cmd:
            return

    if args.cmd:
        dispatch(args.cmd)
        return

    repl()


if __name__ == "__main__":
    main()
