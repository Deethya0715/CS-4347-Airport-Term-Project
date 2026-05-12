"""
generate_readme.py — generates readme.pdf for submission
CS-4347 Airport Management System
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

OUT = "/mnt/user-data/outputs/readme.pdf"

doc = SimpleDocTemplate(OUT, pagesize=letter,
                        leftMargin=inch, rightMargin=inch,
                        topMargin=inch, bottomMargin=inch)

styles = getSampleStyleSheet()
h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=16, spaceAfter=6)
h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=13, spaceAfter=4)
code_style = ParagraphStyle("Code", parent=styles["Code"],
                            fontName="Courier", fontSize=9,
                            backColor=colors.HexColor("#f4f4f4"),
                            borderPadding=4, leftIndent=12)
body = styles["Normal"]

def H(text, level=1):
    return Paragraph(text, h1 if level == 1 else h2)

def P(text):
    return Paragraph(text, body)

def C(text):
    return Paragraph(text, code_style)

def sp(n=8):
    return Spacer(1, n)

def hr():
    return HRFlowable(width="100%", thickness=0.5, color=colors.grey, spaceAfter=6)

story = [
    H("CS-4347 Airport Management System"),
    H("Milestone 2 — Build & Run Instructions", level=2),
    hr(),
    sp(),

    # Team + overview
    H("Project Overview", level=2),
    P("This is the Milestone 2 backend implementation for the CS-4347 Airport "
      "Management System. It provides a command-line interface backed by a SQLite "
      "database. All required features (flight search, trip planning, seat "
      "availability, passenger itinerary, and aircraft utilization report) are "
      "implemented in Python 3."),
    sp(),

    # Requirements
    H("Requirements", level=2),
    P("<b>Language:</b> Python 3.10 or higher"),
    P("<b>Database:</b> SQLite 3 (bundled with Python — no installation needed)"),
    P("<b>Third-party dependencies:</b> None (uses only the Python standard library)"),
    sp(),

    # File layout
    H("Project Structure", level=2),
    C("""\
airport_project/
  cli.py                   ← Entry point / REPL
  sql/
    schema.sql             ← DDL — creates all tables
    seed.sql               ← Sample data for testing
  modules/
    db.py                  ← DB connection helper
    flight_search.py       ← flight() and trip() functions
    booking.py             ← seat_availability() and passenger_itinerary()
    reports.py             ← aircraft_utilization_report()
  readme.pdf               ← This file"""),
    sp(),

    # Setup
    H("Setup & Initialization", level=2),
    P("1. Unzip the submission archive and <b>cd</b> into the project folder:"),
    C("cd airport_project"),
    sp(4),
    P("2. Initialize the database (creates <i>airport.db</i> in the current directory):"),
    C("python cli.py --init"),
    sp(4),
    P("3. (Optional) Also load sample/test data:"),
    C("python cli.py --init --seed"),
    sp(),

    # Running
    H("Running the Application", level=2),
    P("<b>Interactive REPL (recommended):</b>"),
    C("python cli.py"),
    sp(4),
    P("<b>Run a single command and exit:</b>"),
    C('python cli.py --cmd \'flight("AA3478")\''),
    sp(4),
    P("<b>Initialize + open REPL in one step:</b>"),
    C("python cli.py --init --seed --repl"),
    sp(),

    # Commands
    H("Available Commands", level=2),

    Table(
        [
            ["Command", "Description"],
            ['flight(<number>)',             "Show all legs and fares for a flight number"],
            ['trip(<origin>, <dest>)',        "Direct + 1-stop itineraries between airports"],
            ['availability(<flight>, <date>)',"Seat capacity vs. confirmed bookings"],
            ['itinerary(<name>)',             "All bookings for a passenger (partial name OK)"],
            ['report(<start>, <end>)',        "Aircraft utilization report for a date range"],
            ['help',                          "Print the command reference"],
            ['exit / quit',                  "Exit the REPL"],
        ],
        colWidths=[2.8*inch, 3.8*inch],
        style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c5f8a")),
            ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 0), (-1, -1), 9),
            ("FONTNAME",   (0, 1), (0, -1), "Courier"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [colors.HexColor("#f0f4f8"), colors.white]),
            ("GRID",       (0, 0), (-1, -1), 0.4, colors.grey),
            ("PADDING",    (0, 0), (-1, -1), 5),
        ])
    ),
    sp(),

    # Example session
    H("Example Session", level=2),
    C("""\
$ python cli.py --init --seed --repl
CS-4347 Airport Management System
Type 'help' for available commands, 'exit' to quit.

prompt> flight("AA3478")
prompt> trip("DFW", "SFO")
prompt> trip("Dallas", "San Francisco")
prompt> availability("AA3478", "2025-08-01")
prompt> itinerary("Bob Jones")
prompt> report("2025-08-01", "2025-08-31")
prompt> exit"""),
    sp(),

    # Schema notes
    H("Schema Notes", level=2),
    P("The database uses <b>SQLite</b>. The schema is derived from the textbook ER "
      "diagram and is backwards-compatible with the given specification. Notable "
      "adaptations from Oracle syntax:"),
    P("• <b>VARCHAR2</b> → <b>TEXT</b> (SQLite is typeless for strings)"),
    P("• <b>TIMESTAMP</b> → <b>TEXT</b> stored as 'HH:MM' for departure/arrival times"),
    P("• <b>DATE</b> → <b>TEXT</b> stored as 'YYYY-MM-DD'"),
    P("• Foreign key enforcement enabled via <i>PRAGMA foreign_keys = ON</i>"),
    P("The <b>PHYSICAL_PLANE_SEAT</b> table (not in the original schema) was added to "
      "track the physical seat layout of each airplane, enabling accurate capacity "
      "calculations independent of reservations."),
    sp(),

    H("Team Module Assignments", level=2),
    Table(
        [
            ["Member", "Module", "Files"],
            ["Member 1", "Database & Reports",   "sql/schema.sql, sql/seed.sql, modules/reports.py"],
            ["Member 2", "Flight Search",        "modules/flight_search.py"],
            ["Member 3", "Booking / Capacity",   "modules/booking.py (seat_availability)"],
            ["Member 4", "Passenger Queries",    "modules/booking.py (passenger_itinerary)"],
            ["Member 5", "CLI & Documentation",  "cli.py, modules/db.py, readme.pdf"],
        ],
        colWidths=[1.1*inch, 1.7*inch, 3.8*inch],
        style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c5f8a")),
            ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 0), (-1, -1), 8),
            ("FONTNAME",   (0, 1), (-1, -1), "Helvetica"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [colors.HexColor("#f0f4f8"), colors.white]),
            ("GRID",       (0, 0), (-1, -1), 0.4, colors.grey),
            ("PADDING",    (0, 0), (-1, -1), 5),
            ("VALIGN",     (0, 0), (-1, -1), "TOP"),
        ])
    ),
]

doc.build(story)
print(f"readme.pdf written to {OUT}")
