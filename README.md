# CS-4347 Airport Management System — Milestone 2

Milestone 2 is a **Python command-line interface** backed by **SQLite** for the Airport Management System. It supports flight search, trip planning (direct and one-stop), seat availability, passenger itinerary lookup, and an **aircraft utilization** report for a date range.

## Requirements

- **Python** 3.10 or higher  
- **SQLite** 3 (included with Python)  

The application uses only the **standard library**. Optional: `reportlab` is required only if you run `generate_readme.py` to produce a PDF readme for submission.

## Project layout

| Path | Role |
|------|------|
| `cli.py` | Entry point: REPL, `--init`, `--cmd`, etc. |
| `sql/schema.sql` | DDL — creates all tables |
| `sql/seed.sql` | Small sample dataset (SQL) |
| `data/*.csv` | Professor-style CSV bundle (loaded when `./data/FLIGHT.csv` exists on `--init`) |
| `modules/db.py` | Connection helper; `init_db()` |
| `modules/csv_loader.py` | Loads CSV bundle into SQLite |
| `modules/flight_search.py` | `flight()`, `trip()` |
| `modules/booking.py` | `seat_availability()`, `passenger_itinerary()` |
| `modules/reports.py` | `aircraft_utilization_report()` |
| `airport.db` | SQLite database (created after `--init`; path overridable, see below) |

## Setup and initialization

From the project root:

```bash
# Create / reset DB and load ./data/*.csv when data/FLIGHT.csv is present
python cli.py --init
```

Other options:

```bash
# Load CSVs from a specific folder
python cli.py --init --data path/to/csv_folder

# Schema + sql/seed.sql only (no CSV folder)
python cli.py --init --seed

# If you pass both --seed and --data, --seed is ignored
```

The database file defaults to **`airport.db`** in the current working directory. To use another path:

```bash
set AIRPORT_DB=C:\path\to\my.db
python cli.py --init
```

(On Unix: `export AIRPORT_DB=/path/to/my.db`.)

## Running the app

**Interactive REPL (recommended):**

```bash
python cli.py
```

**Initialize then open the REPL:**

```bash
python cli.py --init --repl
```

**Run one command and exit:**

```bash
python cli.py --cmd "flight(1000)"
python cli.py --cmd "availability(1000, 2025-10-04)"
python cli.py --cmd "report(2025-10-04, 2025-10-11)"
```

On **PowerShell**, use single quotes on the outside when the command contains double-quoted strings:

```powershell
python cli.py --cmd 'trip("DFW", "MEX")'
```

## REPL commands

| Command | Description |
|---------|-------------|
| `flight(<number>)` | Legs and fares for a flight number |
| `trip(<origin>, <dest>)` | Direct and one-stop itineraries (IATA codes or city names) |
| `availability(<flight>, <date>)` | Seat capacity vs. confirmed bookings |
| `itinerary(<name>)` | Bookings for a passenger (partial name match) |
| `report(<start>, <end>)` | Aircraft utilization: registration, type, flight count in range (`YYYY-MM-DD`) |
| `help` | Command reference |
| `exit` / `quit` | Leave the REPL |

**Examples** (after `python cli.py --init` with data loaded):

```
flight(1000)
trip("DFW", "MEX")
availability(1000, 2025-10-04)
itinerary("Jane Doe")
report(2025-10-04, 2025-10-11)
```

## Schema notes (SQLite)

- String types use **`TEXT`**; dates are stored as **`YYYY-MM-DD`**; times as **`HH:MM`** where applicable.  
- Foreign keys are enforced with **`PRAGMA foreign_keys = ON`**.  
- **`PHYSICAL_PLANE_SEAT`** models per-aircraft seating so capacity can be computed independently of reservations.

## Optional PDF readme

`generate_readme.py` builds a formatted PDF using **ReportLab**. Install ReportLab, set the output path in the script if needed, then run:

```bash
pip install reportlab
python generate_readme.py
```

## Team module map

| Member | Area | Files |
|--------|------|--------|
| Deethya Janjanam | Database & reports | `sql/schema.sql`, `sql/seed.sql`, `modules/reports.py` |
| Ritikha Ashok | Flight search | `modules/flight_search.py` |
| Salamot Itunuoluwa Fakoya | Booking / capacity | `modules/booking.py` (seat availability) |
| Ananya Ramanan | Passenger queries | `modules/booking.py` (passenger itinerary) |
| Kavyadharshini Seenuvasan | CLI & docs | `cli.py`, `modules/db.py`, README / submission docs |
