#!/usr/bin/env python3
"""
cli.py - Command-Line Interface
CS-4347 Airport Management System (Milestone 3)

Usage
-----
  python cli.py                              # interactive REPL
  python gui_app.py                          # graphical UI (tkinter)
  python cli.py --init                       # schema; load ./data/*.csv if present
  python cli.py --init --data DIR            # schema + load CSVs from DIR
  python cli.py --init --seed                # schema + sql/seed.sql only (no auto ./data)
  python cli.py --init --repl                # init then REPL
  python cli.py --cmd 'trip("DFW","JFK","2025-08-01")'   # one REPL command, then exit

REPL commands
-------------
  flight(<number>[, <date>])
  trip(<origin>, <destination>, <date>)
  availability(<flight_number>, <date>)
  itinerary(<customer_name_or_id>)
  report(<start_date>, <end_date>[, <airplane_id>])
"""

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.booking import passenger_itinerary, seat_availability
from modules.db import init_db
from modules.flight_search import flight, trip
from modules.reports import aircraft_utilization_report

CLI_EXAMPLES = """
Examples (from project root):
  python cli.py --init
  python cli.py --init --seed --repl
  python cli.py --cmd 'trip("DFW", "JFK", "2025-08-01")'
  python cli.py --cmd 'flight("AA3478", "2025-08-01")'
  python gui_app.py
"""

HELP_TEXT = """
  Commands:
    flight(<number>[, <date>])              - schedule template, or dated instance
    trip(<origin>, <dest>, <date>)          - direct + 1-stop on date (>=1h connection)
    availability(<flight>, <date>)          - seat availability for that instance
    itinerary(<name_or_id>)                 - bookings (name partial match or Customer_id)
    report(<start>, <end>[, <reg>])         - aircraft utilization (optional registration)
    help
    exit / quit

  Dates: YYYY-MM-DD. Airports: 3-letter codes or city names.

  GUI:  python gui_app.py
"""


def parse_args_from_input(raw: str) -> list[str]:
    m = re.search(r"\((.+)\)", raw, re.DOTALL)
    if not m:
        return []
    inner = m.group(1)
    parts = [p.strip().strip('"').strip("'") for p in inner.split(",")]
    return [p for p in parts if p]


def dispatch(line: str) -> bool:
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
        if len(args) == 1:
            flight(args[0])
        elif len(args) == 2:
            flight(args[0], args[1])
        else:
            print("  Usage: flight(<flight_number>[, <date>])")

    elif low.startswith("trip("):
        if len(args) != 3:
            print("  Usage: trip(<origin>, <destination>, <date>)")
        else:
            trip(args[0], args[1], args[2])

    elif low.startswith("availability("):
        if len(args) != 2:
            print("  Usage: availability(<flight_number>, <date>)")
        else:
            seat_availability(args[0], args[1])

    elif low.startswith("itinerary("):
        if len(args) != 1:
            print("  Usage: itinerary(<customer_name_or_id>)")
        else:
            passenger_itinerary(args[0])

    elif low.startswith("report("):
        if len(args) == 2:
            aircraft_utilization_report(args[0], args[1])
        elif len(args) == 3:
            reg = args[2].strip() or None
            aircraft_utilization_report(args[0], args[1], reg)
        else:
            print("  Usage: report(<start_date>, <end_date>[, <airplane_id>])")

    else:
        print("  Unknown command. Type 'help' for a list.")

    return True


def repl() -> None:
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CS-4347 Airport Management CLI",
        epilog=CLI_EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--init", action="store_true", help="Initialize (or reset) the database")
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Load sql/seed.sql after schema (skipped if --data is used)",
    )
    parser.add_argument(
        "--data",
        type=str,
        metavar="DIR",
        help="Load professor CSVs from DIR. Default: ./data if data/FLIGHT.csv exists",
    )
    parser.add_argument("--repl", action="store_true", help="Open interactive REPL after --init")
    parser.add_argument("--cmd", type=str, help="Run a single command and exit")
    args = parser.parse_args()

    if args.init:
        root = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(root, "sql", "schema.sql")
        csv_dir = args.data
        seed_path: str | None = None
        if args.seed and csv_dir:
            print("[cli] --seed ignored because --data was set.")
        elif args.seed:
            seed_path = os.path.join(root, "sql", "seed.sql")
        if not csv_dir and not args.seed:
            default_flight = os.path.join(root, "data", "FLIGHT.csv")
            if os.path.isfile(default_flight):
                csv_dir = os.path.join(root, "data")
        init_db(schema_path=schema_path, seed_path=seed_path, csv_dir=csv_dir)
        if not args.repl and not args.cmd:
            return

    if args.cmd:
        dispatch(args.cmd)
        return

    repl()


if __name__ == "__main__":
    main()
