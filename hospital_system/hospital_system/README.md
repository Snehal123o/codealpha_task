# Smart Hospital Appointment Booking & Management System

Stack: Streamlit (frontend) · Python (backend) · MySQL (database) · SMTP email

Roles: Patient, Doctor, Admin

## 1. Prerequisites
- Python 3.9+
- MySQL Server running (MySQL Workbench / XAMPP / MySQL installer all work)

## 2. Setup (VS Code terminal)
    python -m venv venv
    venv\Scripts\activate            (Mac/Linux: source venv/bin/activate)
    pip install -r requirements.txt
    copy .env.example .env           (Mac/Linux: cp .env.example .env)

Open `.env` and set DB_PASSWORD (your MySQL root password) and the email settings.
The database and tables are created automatically on first run.

## 3. Run
    streamlit run app.py
Open http://localhost:8501

## 4. Default admin login
    Email: admin@hospital.com     Password: admin123
Log in, add doctors from Admin > Doctors, then change/remove the default password in the database for real use.

## 5. Email setup (Gmail)
1. Turn on 2-Step Verification in your Google account.
2. Create an App Password (Google Account > Security > App passwords).
3. Put your Gmail in SMTP_USER and the 16-character app password in SMTP_PASSWORD.
If email isn't configured, bookings still work and a warning is shown.

## 6. See MySQL tables in VS Code
Install the extension "Database Client" (by cweijan): click Add Connection > MySQL > enter host/user/password.
Expand hospital_db and double-click users, doctors or appointments to see them as tables.

## Flow
- Patient signs up, picks specialization > doctor > date > free slot, gets confirmation email.
- Doctor sees today's schedule, completes appointments with notes, sets availability.
- Admin adds/removes doctors, views patients and all appointments, sees statistics.
- Cancelling an appointment also emails the patient.
