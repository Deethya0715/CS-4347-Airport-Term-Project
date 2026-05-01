-- ============================================================
-- CS-4347 Airport Management System
-- schema.sql  -- Run this first to initialize the database
-- ============================================================

-- NOTE: This project uses SQLite. Oracle syntax (VARCHAR2, TIMESTAMP)
--       has been adapted to SQLite-compatible types.

PRAGMA foreign_keys = ON;

-- ============================================================
-- Core lookup tables
-- ============================================================

CREATE TABLE IF NOT EXISTS AIRPORT (
    Airport_code TEXT PRIMARY KEY,
    City         TEXT NOT NULL,
    State        TEXT NOT NULL,
    Name         TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS AIRPLANE_TYPE (
    Type_name TEXT PRIMARY KEY,
    Company   TEXT NOT NULL,
    Max_seats INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS AIRPLANE (
    Airplane_id       TEXT PRIMARY KEY,
    Total_no_of_seats INTEGER NOT NULL,
    Type_name         TEXT NOT NULL,
    FOREIGN KEY (Type_name) REFERENCES AIRPLANE_TYPE(Type_name)
);

CREATE TABLE IF NOT EXISTS CAN_LAND (
    Airport_code TEXT NOT NULL,
    Type_name    TEXT NOT NULL,
    PRIMARY KEY (Airport_code, Type_name),
    FOREIGN KEY (Airport_code) REFERENCES AIRPORT(Airport_code) ON DELETE CASCADE,
    FOREIGN KEY (Type_name)    REFERENCES AIRPLANE_TYPE(Type_name) ON DELETE CASCADE
);

-- ============================================================
-- Flight structure
-- ============================================================

CREATE TABLE IF NOT EXISTS FLIGHT (
    FLIGHT_Number TEXT PRIMARY KEY,
    Airline       TEXT NOT NULL,
    Weekdays      TEXT NOT NULL   -- e.g. "Mon,Wed,Fri" or "Daily"
);

CREATE TABLE IF NOT EXISTS FLIGHT_LEG (
    FLIGHT_LEG_Number  TEXT NOT NULL,
    Leg_no             INTEGER NOT NULL,
    Departure_code     TEXT NOT NULL,
    Arrival_code       TEXT NOT NULL,
    Scheduled_dep_time TEXT,      -- stored as "HH:MM"
    Scheduled_arr_time TEXT,
    PRIMARY KEY (FLIGHT_LEG_Number, Leg_no),
    FOREIGN KEY (FLIGHT_LEG_Number) REFERENCES FLIGHT(FLIGHT_Number) ON DELETE CASCADE,
    FOREIGN KEY (Departure_code)    REFERENCES AIRPORT(Airport_code),
    FOREIGN KEY (Arrival_code)      REFERENCES AIRPORT(Airport_code)
);

CREATE TABLE IF NOT EXISTS FARE (
    Code        TEXT NOT NULL,
    Fare_Number TEXT NOT NULL,
    Amount      REAL NOT NULL,
    Restriction TEXT,
    PRIMARY KEY (Code, Fare_Number),
    FOREIGN KEY (Fare_Number) REFERENCES FLIGHT(FLIGHT_Number) ON DELETE CASCADE
);

-- ============================================================
-- Instances (scheduled occurrences of each leg)
-- ============================================================

CREATE TABLE IF NOT EXISTS LEG_INSTANCE (
    LEG_INSTANCE_Number    TEXT NOT NULL,
    Leg_no                 INTEGER NOT NULL,
    LEG_INSTANCE_Date      TEXT NOT NULL,   -- stored as "YYYY-MM-DD"
    No_of_available_seats  INTEGER,
    Airplane_id            TEXT NOT NULL,
    PRIMARY KEY (LEG_INSTANCE_Number, Leg_no, LEG_INSTANCE_Date),
    FOREIGN KEY (LEG_INSTANCE_Number, Leg_no)
        REFERENCES FLIGHT_LEG(FLIGHT_LEG_Number, Leg_no) ON DELETE CASCADE,
    FOREIGN KEY (Airplane_id) REFERENCES AIRPLANE(Airplane_id)
);

-- ============================================================
-- Seating
-- ============================================================

CREATE TABLE IF NOT EXISTS PHYSICAL_PLANE_SEAT (
    Airplane_id TEXT NOT NULL,
    Seat_no     TEXT NOT NULL,
    Class       TEXT NOT NULL,   -- e.g. "Economy", "Business", "First"
    PRIMARY KEY (Airplane_id, Seat_no),
    FOREIGN KEY (Airplane_id) REFERENCES AIRPLANE(Airplane_id)
);

CREATE TABLE IF NOT EXISTS SEAT (
    Seat_no       TEXT NOT NULL,
    Flight_Number TEXT NOT NULL,
    Leg_no        INTEGER NOT NULL,
    Seat_Date     TEXT NOT NULL,
    Customer_name TEXT NOT NULL,
    Cphone        TEXT,
    PRIMARY KEY (Seat_no, Flight_Number, Leg_no, Seat_Date),
    FOREIGN KEY (Flight_Number, Leg_no, Seat_Date)
        REFERENCES LEG_INSTANCE(LEG_INSTANCE_Number, Leg_no, LEG_INSTANCE_Date)
        ON DELETE CASCADE
);
