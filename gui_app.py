#!/usr/bin/env python3
"""
gui_app.py - Tkinter GUI for CS-4347 Airport Management System (Milestone 3)
"""

from __future__ import annotations

import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk

# Project root on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.booking import (
    book_seat,
    fetch_passenger_itinerary,
    fetch_seat_availability,
)
from modules.db import init_db
from modules.flight_search import (
    fetch_direct_routes,
    fetch_flight_instance_legs,
    fetch_flight_template,
    fetch_one_stop_routes,
)
from modules.reports import fetch_aircraft_utilization


def _text_append(w: tk.Text, s: str) -> None:
    w.configure(state="normal")
    w.insert("end", s + "\n")
    w.see("end")
    w.configure(state="disabled")


class AirportApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("CS-4347 Airport Management System")
        self.geometry("900x620")
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=8, pady=8)

        self._build_tab_trip(nb)
        self._build_tab_flight(nb)
        self._build_tab_report(nb)
        self._build_tab_availability(nb)
        self._build_tab_book(nb)
        self._build_tab_itinerary(nb)

        f = ttk.Frame(self)
        f.pack(fill="x", padx=8, pady=(0, 8))
        ttk.Label(f, text="Database file:").pack(side="left")
        self.db_var = tk.StringVar(value=os.environ.get("AIRPORT_DB", "airport.db"))
        ttk.Entry(f, textvariable=self.db_var, width=40).pack(side="left", padx=6)
        ttk.Button(f, text="Re-init DB (schema+seed)", command=self._reinit_db).pack(
            side="left"
        )

    def _reinit_db(self) -> None:
        root = os.path.dirname(os.path.abspath(__file__))
        os.environ["AIRPORT_DB"] = self.db_var.get().strip() or "airport.db"
        schema = os.path.join(root, "sql", "schema.sql")
        seed = os.path.join(root, "sql", "seed.sql")
        try:
            init_db(schema_path=schema, seed_path=seed)
            messagebox.showinfo("Database", "Initialized with schema + seed data.")
        except OSError as e:
            messagebox.showerror("Database", str(e))

    def _build_tab_trip(self, nb: ttk.Notebook) -> None:
        tab = ttk.Frame(nb)
        nb.add(tab, text="Flight search (route + date)")
        r = 0
        ttk.Label(tab, text="Origin (code or city)").grid(row=r, column=0, sticky="w", padx=6, pady=4)
        self.trip_orig = tk.StringVar(value="DFW")
        ttk.Entry(tab, textvariable=self.trip_orig, width=20).grid(row=r, column=1, sticky="w", pady=4)
        r += 1
        ttk.Label(tab, text="Destination").grid(row=r, column=0, sticky="w", padx=6, pady=4)
        self.trip_dest = tk.StringVar(value="JFK")
        ttk.Entry(tab, textvariable=self.trip_dest, width=20).grid(row=r, column=1, sticky="w", pady=4)
        r += 1
        ttk.Label(tab, text="Date (YYYY-MM-DD)").grid(row=r, column=0, sticky="w", padx=6, pady=4)
        self.trip_date = tk.StringVar(value="2025-08-01")
        ttk.Entry(tab, textvariable=self.trip_date, width=20).grid(row=r, column=1, sticky="w", pady=4)
        r += 1
        ttk.Button(tab, text="Search", command=self._do_trip).grid(row=r, column=0, columnspan=2, pady=8)
        r += 1
        out = tk.Text(tab, height=22, wrap="word", state="disabled")
        out.grid(row=r, column=0, columnspan=2, sticky="nsew", padx=6, pady=4)
        tab.rowconfigure(r, weight=1)
        tab.columnconfigure(1, weight=1)
        self.trip_out = out

    def _do_trip(self) -> None:
        from modules.flight_search import resolve_airport_code

        d = self.trip_date.get().strip()
        o = self.trip_orig.get().strip()
        dest = self.trip_dest.get().strip()
        self.trip_out.configure(state="normal")
        self.trip_out.delete("1.0", "end")
        self.trip_out.configure(state="disabled")
        oc = resolve_airport_code(o)
        dc = resolve_airport_code(dest)
        if not oc:
            _text_append(self.trip_out, f"Unknown origin: {o}")
            return
        if not dc:
            _text_append(self.trip_out, f"Unknown destination: {dest}")
            return
        for orig in oc:
            for dst in dc:
                _text_append(self.trip_out, f"=== {orig} → {dst}  on  {d} ===\n")
                dirs = fetch_direct_routes(orig, dst, d)
                if dirs:
                    _text_append(self.trip_out, f"Direct ({len(dirs)}):")
                    for x in dirs:
                        _text_append(
                            self.trip_out,
                            f"  {x['Airline']}  {x['flight_no']}  leg {x['Leg_no']}  "
                            f"{x['flight_date']}  {x['Scheduled_dep_time']} → {x['Scheduled_arr_time']}",
                        )
                else:
                    _text_append(self.trip_out, "No direct flights.")
                cons = fetch_one_stop_routes(orig, dst, d)
                if cons:
                    _text_append(self.trip_out, f"\nOne-stop with ≥1h layover ({len(cons)}):")
                    for c in cons:
                        _text_append(
                            self.trip_out,
                            f"  Leg1: {c['airline1']} {c['flight1']} {c['dep1']}→{c['arr1']} "
                            f"via {c['connect_code']} ({c['connect_city']})",
                        )
                        _text_append(
                            self.trip_out,
                            f"  Leg2: {c['airline2']} {c['flight2']} {c['dep2']}→{c['arr2']}\n",
                        )
                else:
                    _text_append(self.trip_out, "No qualifying one-stop connections.\n")

    def _build_tab_flight(self, nb: ttk.Notebook) -> None:
        tab = ttk.Frame(nb)
        nb.add(tab, text="Flight by number (+ date)")
        r = 0
        ttk.Label(tab, text="Flight number").grid(row=r, column=0, sticky="w", padx=6, pady=4)
        self.fl_num = tk.StringVar(value="AA3478")
        ttk.Entry(tab, textvariable=self.fl_num, width=16).grid(row=r, column=1, sticky="w", pady=4)
        r += 1
        ttk.Label(tab, text="Date (optional, YYYY-MM-DD)").grid(row=r, column=0, sticky="w", padx=6, pady=4)
        self.fl_date = tk.StringVar()
        ttk.Entry(tab, textvariable=self.fl_date, width=16).grid(row=r, column=1, sticky="w", pady=4)
        r += 1
        bf = ttk.Frame(tab)
        bf.grid(row=r, column=0, columnspan=2, pady=6)
        ttk.Button(bf, text="Show schedule template", command=self._do_flight_template).pack(
            side="left", padx=4
        )
        ttk.Button(bf, text="Show dated instance", command=self._do_flight_dated).pack(side="left", padx=4)
        r += 1
        out = tk.Text(tab, height=24, wrap="word", state="disabled")
        out.grid(row=r, column=0, columnspan=2, sticky="nsew", padx=6, pady=4)
        tab.rowconfigure(r, weight=1)
        tab.columnconfigure(1, weight=1)
        self.fl_out = out

    def _do_flight_template(self) -> None:
        fn = self.fl_num.get().strip()
        self.fl_out.configure(state="normal")
        self.fl_out.delete("1.0", "end")
        self.fl_out.configure(state="disabled")
        data = fetch_flight_template(fn)
        if not data:
            _text_append(self.fl_out, f"No flight '{fn}'")
            return
        f = data["flight"]
        _text_append(self.fl_out, f"{f['FLIGHT_Number']} - {f['Airline']} - {f['Weekdays']}")
        for leg in data["legs"]:
            _text_append(
                self.fl_out,
                f"  Leg {leg['Leg_no']}: {leg['Departure_code']} ({leg['dep_city']}) "
                f"{leg['Scheduled_dep_time']} → {leg['Arrival_code']} ({leg['arr_city']}) {leg['Scheduled_arr_time']}",
            )
        if data["fares"]:
            _text_append(self.fl_out, "\nFares:")
            for fa in data["fares"]:
                _text_append(self.fl_out, f"  {fa['Code']}: ${fa['Amount']:.2f} {fa['Restriction'] or ''}")

    def _do_flight_dated(self) -> None:
        fn = self.fl_num.get().strip()
        d = self.fl_date.get().strip()
        self.fl_out.configure(state="normal")
        self.fl_out.delete("1.0", "end")
        self.fl_out.configure(state="disabled")
        if not d:
            messagebox.showwarning("Flight", "Enter a date for dated instance search.")
            return
        rows = fetch_flight_instance_legs(fn, d)
        if not rows:
            _text_append(self.fl_out, f"No legs scheduled for {fn} on {d}")
            return
        _text_append(self.fl_out, f"{fn} on {d} - {rows[0]['Airline']}")
        for r in rows:
            _text_append(
                self.fl_out,
                f"  Leg {r['Leg_no']}: {r['Departure_code']} → {r['Arrival_code']}  "
                f"{r['Scheduled_dep_time']} → {r['Scheduled_arr_time']}  ({r['Airplane_id']})",
            )

    def _build_tab_report(self, nb: ttk.Notebook) -> None:
        tab = ttk.Frame(nb)
        nb.add(tab, text="Aircraft utilization")
        r = 0
        ttk.Label(tab, text="Start date").grid(row=r, column=0, sticky="w", padx=6, pady=4)
        self.r_start = tk.StringVar(value="2025-08-01")
        ttk.Entry(tab, textvariable=self.r_start, width=16).grid(row=r, column=1, sticky="w", pady=4)
        r += 1
        ttk.Label(tab, text="End date").grid(row=r, column=0, sticky="w", padx=6, pady=4)
        self.r_end = tk.StringVar(value="2025-08-31")
        ttk.Entry(tab, textvariable=self.r_end, width=16).grid(row=r, column=1, sticky="w", pady=4)
        r += 1
        ttk.Label(tab, text="Registration (optional)").grid(row=r, column=0, sticky="w", padx=6, pady=4)
        self.r_reg = tk.StringVar()
        ttk.Entry(tab, textvariable=self.r_reg, width=16).grid(row=r, column=1, sticky="w", pady=4)
        r += 1
        ttk.Button(tab, text="Run report", command=self._do_report).grid(row=r, column=0, columnspan=2, pady=8)
        r += 1
        out = tk.Text(tab, height=24, wrap="word", state="disabled")
        out.grid(row=r, column=0, columnspan=2, sticky="nsew", padx=6, pady=4)
        tab.rowconfigure(r, weight=1)
        tab.columnconfigure(1, weight=1)
        self.r_out = out

    def _do_report(self) -> None:
        self.r_out.configure(state="normal")
        self.r_out.delete("1.0", "end")
        self.r_out.configure(state="disabled")
        reg = self.r_reg.get().strip() or None
        rows = fetch_aircraft_utilization(self.r_start.get().strip(), self.r_end.get().strip(), reg)
        if not rows:
            _text_append(self.r_out, "No rows.")
            return
        _text_append(self.r_out, f"{'Reg':<12} {'Type':<14} {'Co':<10} {'Seats':>5} {'Flts':>6}")
        for x in rows:
            _text_append(
                self.r_out,
                f"{x['Airplane_id']:<12} {x['Type_name']:<14} {x['Company']:<10} "
                f"{x['Total_no_of_seats']:>5} {x['total_flights']:>6}",
            )

    def _build_tab_availability(self, nb: ttk.Notebook) -> None:
        tab = ttk.Frame(nb)
        nb.add(tab, text="Seat availability")
        r = 0
        ttk.Label(tab, text="Flight number").grid(row=r, column=0, sticky="w", padx=6, pady=4)
        self.av_fn = tk.StringVar(value="AA3478")
        ttk.Entry(tab, textvariable=self.av_fn, width=14).grid(row=r, column=1, sticky="w", pady=4)
        r += 1
        ttk.Label(tab, text="Date").grid(row=r, column=0, sticky="w", padx=6, pady=4)
        self.av_dt = tk.StringVar(value="2025-08-01")
        ttk.Entry(tab, textvariable=self.av_dt, width=14).grid(row=r, column=1, sticky="w", pady=4)
        r += 1
        ttk.Button(tab, text="Check", command=self._do_avail).grid(row=r, column=0, columnspan=2, pady=8)
        r += 1
        out = tk.Text(tab, height=24, wrap="word", state="disabled")
        out.grid(row=r, column=0, columnspan=2, sticky="nsew", padx=6, pady=4)
        tab.rowconfigure(r, weight=1)
        tab.columnconfigure(1, weight=1)
        self.av_out = out

    def _do_avail(self) -> None:
        self.av_out.configure(state="normal")
        self.av_out.delete("1.0", "end")
        self.av_out.configure(state="disabled")
        legs = fetch_seat_availability(self.av_fn.get().strip(), self.av_dt.get().strip())
        if not legs:
            _text_append(self.av_out, "No leg instances for that flight/date.")
            return
        for leg in legs:
            ok = "Yes" if leg["remaining"] > 0 else "No"
            _text_append(
                self.av_out,
                f"Leg {leg['Leg_no']} {leg['Departure_code']}→{leg['Arrival_code']} "
                f"{leg['Scheduled_dep_time']}-{leg['Scheduled_arr_time']}\n"
                f"  Aircraft {leg['Airplane_id']} ({leg['Type_name']})  "
                f"capacity {leg['capacity']}  booked {leg['booked']}  remaining {leg['remaining']}\n"
                f"  Seats available: {ok}\n",
            )

    def _build_tab_book(self, nb: ttk.Notebook) -> None:
        tab = ttk.Frame(nb)
        nb.add(tab, text="Book seat")
        r = 0
        self.bk_fn = tk.StringVar(value="AA3478")
        self.bk_leg = tk.StringVar(value="1")
        self.bk_dt = tk.StringVar(value="2025-08-01")
        self.bk_seat = tk.StringVar(value="12A")
        self.bk_name = tk.StringVar(value="Test Passenger")
        self.bk_phone = tk.StringVar(value="555-0000")
        self.bk_id = tk.StringVar(value="P9999")
        for lab, var in [
            ("Flight number", self.bk_fn),
            ("Leg no.", self.bk_leg),
            ("Date (YYYY-MM-DD)", self.bk_dt),
            ("Seat", self.bk_seat),
            ("Customer name", self.bk_name),
            ("Phone", self.bk_phone),
            ("Customer ID (optional)", self.bk_id),
        ]:
            ttk.Label(tab, text=lab).grid(row=r, column=0, sticky="w", padx=6, pady=3)
            ttk.Entry(tab, textvariable=var, width=28).grid(row=r, column=1, sticky="w", pady=3)
            r += 1
        ttk.Button(tab, text="Book", command=self._do_book).grid(row=r, column=0, columnspan=2, pady=10)
        r += 1
        self.bk_out = tk.Text(tab, height=14, wrap="word", state="disabled")
        self.bk_out.grid(row=r, column=0, columnspan=2, sticky="nsew", padx=6, pady=4)
        tab.rowconfigure(r, weight=1)
        tab.columnconfigure(1, weight=1)

    def _do_book(self) -> None:
        self.bk_out.configure(state="normal")
        self.bk_out.delete("1.0", "end")
        self.bk_out.configure(state="disabled")
        ok, msg = book_seat(
            self.bk_fn.get().strip(),
            self.bk_leg.get().strip(),
            self.bk_dt.get().strip(),
            self.bk_seat.get().strip(),
            self.bk_name.get().strip(),
            self.bk_phone.get().strip(),
            self.bk_id.get().strip() or None,
        )
        _text_append(self.bk_out, msg)
        if ok:
            messagebox.showinfo("Booking", msg)
        else:
            messagebox.showwarning("Booking", msg)

    def _build_tab_itinerary(self, nb: ttk.Notebook) -> None:
        tab = ttk.Frame(nb)
        nb.add(tab, text="Passenger itinerary")
        r = 0
        ttk.Label(tab, text="Customer name or ID").grid(row=r, column=0, sticky="w", padx=6, pady=4)
        self.it_q = tk.StringVar(value="Bob Jones")
        ttk.Entry(tab, textvariable=self.it_q, width=28).grid(row=r, column=1, sticky="w", pady=4)
        r += 1
        ttk.Button(tab, text="Lookup", command=self._do_itin).grid(row=r, column=0, columnspan=2, pady=8)
        r += 1
        out = tk.Text(tab, height=26, wrap="word", state="disabled")
        out.grid(row=r, column=0, columnspan=2, sticky="nsew", padx=6, pady=4)
        tab.rowconfigure(r, weight=1)
        tab.columnconfigure(1, weight=1)
        self.it_out = out

    def _do_itin(self) -> None:
        self.it_out.configure(state="normal")
        self.it_out.delete("1.0", "end")
        self.it_out.configure(state="disabled")
        rows = fetch_passenger_itinerary(self.it_q.get().strip())
        if not rows:
            _text_append(self.it_out, "No bookings found.")
            return
        cur = None
        for r in rows:
            if r["Customer_name"] != cur:
                cur = r["Customer_name"]
                _text_append(
                    self.it_out,
                    f"\n{cur}  ID:{r['Customer_id'] or '-'}  Ph:{r['Cphone'] or '-'}",
                )
            _text_append(
                self.it_out,
                f"  {r['Seat_Date']}  {r['Flight_Number']} leg {r['Leg_no']} seat {r['Seat_no']}  "
                f"{r['Departure_code']} ({r['dep_city']}) {r['Scheduled_dep_time']} → "
                f"{r['Arrival_code']} ({r['arr_city']}) {r['Scheduled_arr_time']}  ac {r['Airplane_id']}",
            )


def main() -> None:
    AirportApp().mainloop()


if __name__ == "__main__":
    main()
