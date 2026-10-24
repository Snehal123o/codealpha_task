-- Hospital Appointment Booking System - Database Schema
-- Plain SQL, works with SQLite as-is. For MySQL, see the note at the bottom.

DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS doctors;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,          -- stored as a hash, never plain text
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    role TEXT NOT NULL CHECK(role IN ('patient', 'doctor', 'admin')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE doctors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    specialization TEXT NOT NULL,
    department TEXT NOT NULL,
    qualification TEXT,
    experience_years INTEGER DEFAULT 0,
    consultation_fee REAL DEFAULT 0,
    available_days TEXT,             -- e.g. "Mon,Wed,Fri"
    available_time TEXT,             -- e.g. "10:00 AM - 4:00 PM"
    is_active INTEGER DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    appointment_date TEXT NOT NULL,   -- YYYY-MM-DD
    time_slot TEXT NOT NULL,
    reason TEXT,
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','confirmed','completed','cancelled')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE,
    UNIQUE (doctor_id, appointment_date, time_slot)  -- prevents double-booking at the DB level
);

-- Seed one admin account so you can log in immediately.
-- Username: admin | Password: admin123 (hashed below with werkzeug's default method)
-- The actual hash is inserted by database.py (Python) since it depends on Werkzeug's
-- hashing implementation - see init_db() in database.py.

/*
MySQL notes if you migrate this later:
- AUTOINCREMENT -> AUTO_INCREMENT
- INTEGER PRIMARY KEY AUTOINCREMENT -> INT PRIMARY KEY AUTO_INCREMENT
- CHECK() constraints are supported in MySQL 8.0.16+, otherwise enforce in Python
- TIMESTAMP DEFAULT CURRENT_TIMESTAMP works the same way in MySQL
*/
