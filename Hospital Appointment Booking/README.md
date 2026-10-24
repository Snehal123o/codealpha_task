# 🏥 Hospital Appointment Booking System (Flask + Raw SQL)

A simpler, more transparent version of the hospital booking system — plain
**Python (Flask)**, **raw SQL queries** (no ORM), and **hand-written HTML/CSS**.
Every database query is visible in `app.py`, which makes this easier to explain
line-by-line in a viva or interview.

## Tech Stack

| Layer     | Technology                          |
|-----------|--------------------------------------|
| Frontend  | HTML, CSS (hand-written, no framework), Jinja2 templates |
| Backend   | Python 3 + Flask                    |
| Database  | SQLite (via Python's built-in `sqlite3`) — raw SQL, no ORM |
| Auth      | Flask sessions + Werkzeug password hashing |
| Server    | Flask's built-in dev server         |

> Every single database operation — inserts, selects, updates — is a plain
> SQL string in `app.py`. Nothing is hidden behind an ORM, so you can point
> to the exact line of SQL for any feature.

## Project Structure

```
hospital_flask/
├── app.py            # all routes + all SQL queries
├── database.py       # connects to SQLite, runs schema.sql, seeds admin
├── schema.sql         # raw SQL: CREATE TABLE statements
├── requirements.txt
├── templates/         # Jinja2 HTML templates
│   ├── base.html
│   ├── login.html / register.html
│   ├── patient_dashboard.html / doctor_list.html / book.html / my_appointments.html
│   ├── doctor_dashboard.html
│   └── admin_dashboard.html / add_doctor.html / all_appointments.html
└── static/css/style.css   # plain, hand-written CSS (no Bootstrap)
```

## Database Schema (from `schema.sql`)

```sql
users (id, username, password, full_name, email, phone, role, created_at)
doctors (id, user_id, specialization, department, qualification,
         experience_years, consultation_fee, available_days, available_time, is_active)
appointments (id, patient_id, doctor_id, appointment_date, time_slot,
              reason, status, created_at)
```

`appointments` has `UNIQUE (doctor_id, appointment_date, time_slot)` — this is
what stops two patients booking the same doctor at the same time. It's
enforced by the database itself, and the Flask view catches the resulting
error and shows a friendly message instead of crashing.

## Setup Instructions

### 1. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize the database
```bash
python database.py
```
This runs `schema.sql` to create the tables and seeds one admin account:
- **Username:** `admin`
- **Password:** `admin123`

> Re-running `python database.py` will **wipe and recreate** all tables
> (see the `DROP TABLE IF EXISTS` lines in `schema.sql`) — only do this if
> you want a fresh start.

### 4. Run the app
```bash
python app.py
```
Open **http://127.0.0.1:5000/** in your browser.

## How to see your data

Since this uses raw SQLite, the whole database is a single file: `hospital.db`,
created after you run `database.py`.

- **VS Code:** install the "SQLite Viewer" extension, click `hospital.db`
- **Command line:**
  ```bash
  sqlite3 hospital.db
  sqlite> SELECT * FROM doctors;
  sqlite> .tables
  sqlite> .schema appointments
  ```
- **Python shell:**
  ```python
  from database import get_db_connection
  conn = get_db_connection()
  print(conn.execute("SELECT * FROM doctors").fetchall())
  ```

## Usage Flow

1. Log in as `admin` / `admin123` → **Admin Dashboard**
2. Click **+ Add Doctor** → fill in login + specialization → this creates a
   row in `users` (role='doctor') and a linked row in `doctors`
3. Log out, register a new account (defaults to role='patient')
4. Log in as that patient → **Find a Doctor** → **Book Appointment**
5. Log in as the doctor (the username/password you set in step 2) → confirm
   and complete the appointment
6. Log back in as admin → **All Appointments** to see everything, filterable by status

## Key Talking Points for Your Interview

- **Why raw SQL instead of an ORM?** To show a clear understanding of how
  the database layer actually works — every query is visible and
  parameterized (`?` placeholders) to prevent SQL injection.
- **Password security:** passwords are never stored as plain text — hashed
  with `werkzeug.security.generate_password_hash` and checked with
  `check_password_hash`.
- **Session-based auth:** `session['user_id']`, `session['role']` are set on
  login; a custom `@login_required(role=...)` decorator protects each route.
- **Preventing double-booking:** enforced at the database level with a
  `UNIQUE` constraint on `(doctor_id, appointment_date, time_slot)`, and the
  resulting `IntegrityError` is caught in the `book_appointment` view.
- **Three roles, one `users` table:** a `role` column (`patient`/`doctor`/`admin`)
  distinguishes account types, similar in spirit to the Django version but
  without an ORM abstracting the table structure away.

## Migrating to MySQL later

The schema is written for SQLite but is nearly identical for MySQL. Changes needed:
- `INTEGER PRIMARY KEY AUTOINCREMENT` → `INT PRIMARY KEY AUTO_INCREMENT`
- Swap `import sqlite3` for `import mysql.connector` (or `pymysql`) in `database.py`
  and update `get_db_connection()` to connect with host/user/password/database
- Everything else (the SQL queries themselves) stays almost the same
