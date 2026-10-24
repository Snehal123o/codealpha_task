from datetime import date
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db_connection

app = Flask(__name__)
app.secret_key = "change-this-secret-key-before-deploying"  # used to sign session cookies

TIME_SLOTS = ["10:00 AM", "11:00 AM", "12:00 PM", "02:00 PM", "03:00 PM", "04:00 PM"]


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def login_required(role=None):
    """Decorator that blocks a view unless the user is logged in,
    and optionally restricts it to a specific role (patient/doctor/admin)."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in first.", "warning")
                return redirect(url_for("login"))
            if role and session.get("role") != role:
                flash("You don't have access to that page.", "danger")
                return redirect(url_for("dashboard"))
            return view_func(*args, **kwargs)
        return wrapped
    return decorator


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        full_name = request.form["full_name"].strip()
        email = request.form["email"].strip()
        phone = request.form.get("phone", "").strip()

        conn = get_db_connection()
        existing = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        if existing:
            flash("That username is already taken.", "danger")
            conn.close()
            return render_template("register.html")

        password_hash = generate_password_hash(password)
        conn.execute(
            """INSERT INTO users (username, password, full_name, email, phone, role)
               VALUES (?, ?, ?, ?, ?, 'patient')""",
            (username, password_hash, full_name, email, phone),
        )
        conn.commit()
        conn.close()
        flash("Account created. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["full_name"] = user["full_name"]
            session["role"] = user["role"]
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required()
def dashboard():
    role = session["role"]
    if role == "patient":
        return redirect(url_for("patient_dashboard"))
    elif role == "doctor":
        return redirect(url_for("doctor_dashboard"))
    elif role == "admin":
        return redirect(url_for("admin_dashboard"))
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Patient routes
# ---------------------------------------------------------------------------

@app.route("/patient/dashboard")
@login_required(role="patient")
def patient_dashboard():
    return render_template("patient_dashboard.html")


@app.route("/doctors")
@login_required(role="patient")
def doctor_list():
    department = request.args.get("department", "")

    conn = get_db_connection()
    if department:
        doctors = conn.execute(
            """SELECT doctors.*, users.full_name FROM doctors
               JOIN users ON doctors.user_id = users.id
               WHERE doctors.is_active = 1 AND doctors.department = ?""",
            (department,),
        ).fetchall()
    else:
        doctors = conn.execute(
            """SELECT doctors.*, users.full_name FROM doctors
               JOIN users ON doctors.user_id = users.id
               WHERE doctors.is_active = 1"""
        ).fetchall()

    departments = conn.execute("SELECT DISTINCT department FROM doctors").fetchall()
    conn.close()
    return render_template(
        "doctor_list.html", doctors=doctors, departments=departments, selected_department=department
    )


@app.route("/book/<int:doctor_id>", methods=["GET", "POST"])
@login_required(role="patient")
def book_appointment(doctor_id):
    conn = get_db_connection()
    doctor = conn.execute(
        """SELECT doctors.*, users.full_name FROM doctors
           JOIN users ON doctors.user_id = users.id
           WHERE doctors.id = ?""",
        (doctor_id,),
    ).fetchone()

    if not doctor:
        conn.close()
        flash("Doctor not found.", "danger")
        return redirect(url_for("doctor_list"))

    if request.method == "POST":
        appt_date = request.form["date"]
        time_slot = request.form["time_slot"]
        reason = request.form.get("reason", "").strip()

        if appt_date < str(date.today()):
            flash("You cannot book a date in the past.", "danger")
            return render_template("book.html", doctor=doctor, time_slots=TIME_SLOTS)

        try:
            conn.execute(
                """INSERT INTO appointments (patient_id, doctor_id, appointment_date, time_slot, reason)
                   VALUES (?, ?, ?, ?, ?)""",
                (session["user_id"], doctor_id, appt_date, time_slot, reason),
            )
            conn.commit()
            flash("Appointment booked successfully!", "success")
            conn.close()
            return redirect(url_for("my_appointments"))
        except conn.IntegrityError:
            # UNIQUE(doctor_id, appointment_date, time_slot) constraint caught a clash
            flash("That slot is already booked. Please choose a different time.", "danger")

    conn.close()
    return render_template("book.html", doctor=doctor, time_slots=TIME_SLOTS)


@app.route("/my-appointments")
@login_required(role="patient")
def my_appointments():
    conn = get_db_connection()
    appointments = conn.execute(
        """SELECT appointments.*, users.full_name AS doctor_name, doctors.department
           FROM appointments
           JOIN doctors ON appointments.doctor_id = doctors.id
           JOIN users ON doctors.user_id = users.id
           WHERE appointments.patient_id = ?
           ORDER BY appointments.appointment_date DESC""",
        (session["user_id"],),
    ).fetchall()
    conn.close()
    return render_template("my_appointments.html", appointments=appointments)


@app.route("/cancel/<int:appointment_id>")
@login_required(role="patient")
def cancel_appointment(appointment_id):
    conn = get_db_connection()
    conn.execute(
        """UPDATE appointments SET status = 'cancelled'
           WHERE id = ? AND patient_id = ? AND status IN ('pending', 'confirmed')""",
        (appointment_id, session["user_id"]),
    )
    conn.commit()
    conn.close()
    flash("Appointment cancelled.", "success")
    return redirect(url_for("my_appointments"))


# ---------------------------------------------------------------------------
# Doctor routes
# ---------------------------------------------------------------------------

@app.route("/doctor/dashboard")
@login_required(role="doctor")
def doctor_dashboard():
    conn = get_db_connection()
    doctor = conn.execute("SELECT * FROM doctors WHERE user_id = ?", (session["user_id"],)).fetchone()
    appointments = conn.execute(
        """SELECT appointments.*, users.full_name AS patient_name
           FROM appointments
           JOIN users ON appointments.patient_id = users.id
           WHERE appointments.doctor_id = ?
           ORDER BY appointments.appointment_date, appointments.time_slot""",
        (doctor["id"],),
    ).fetchall()
    conn.close()
    return render_template("doctor_dashboard.html", doctor=doctor, appointments=appointments)


@app.route("/doctor/appointment/<int:appointment_id>/<string:new_status>")
@login_required(role="doctor")
def update_appointment_status(appointment_id, new_status):
    if new_status not in ("confirmed", "completed"):
        flash("Invalid status.", "danger")
        return redirect(url_for("doctor_dashboard"))

    conn = get_db_connection()
    doctor = conn.execute("SELECT * FROM doctors WHERE user_id = ?", (session["user_id"],)).fetchone()
    conn.execute(
        "UPDATE appointments SET status = ? WHERE id = ? AND doctor_id = ?",
        (new_status, appointment_id, doctor["id"]),
    )
    conn.commit()
    conn.close()
    flash(f"Appointment marked as {new_status}.", "success")
    return redirect(url_for("doctor_dashboard"))


# ---------------------------------------------------------------------------
# Admin routes
# ---------------------------------------------------------------------------

@app.route("/admin/dashboard")
@login_required(role="admin")
def admin_dashboard():
    conn = get_db_connection()
    doctors = conn.execute(
        """SELECT doctors.*, users.full_name, users.username FROM doctors
           JOIN users ON doctors.user_id = users.id"""
    ).fetchall()
    appointments = conn.execute(
        """SELECT appointments.*, patients.full_name AS patient_name, docs.full_name AS doctor_name
           FROM appointments
           JOIN users AS patients ON appointments.patient_id = patients.id
           JOIN doctors ON appointments.doctor_id = doctors.id
           JOIN users AS docs ON doctors.user_id = docs.id
           ORDER BY appointments.appointment_date DESC LIMIT 20"""
    ).fetchall()

    stats = {
        "total_doctors": conn.execute("SELECT COUNT(*) FROM doctors").fetchone()[0],
        "total_patients": conn.execute("SELECT COUNT(*) FROM users WHERE role = 'patient'").fetchone()[0],
        "total_appointments": conn.execute("SELECT COUNT(*) FROM appointments").fetchone()[0],
        "pending_appointments": conn.execute(
            "SELECT COUNT(*) FROM appointments WHERE status = 'pending'"
        ).fetchone()[0],
    }
    conn.close()
    return render_template("admin_dashboard.html", doctors=doctors, appointments=appointments, stats=stats)


@app.route("/admin/add-doctor", methods=["GET", "POST"])
@login_required(role="admin")
def add_doctor():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        full_name = request.form["full_name"].strip()
        email = request.form["email"].strip()
        specialization = request.form["specialization"].strip()
        department = request.form["department"].strip()
        qualification = request.form.get("qualification", "").strip()
        experience_years = request.form.get("experience_years", 0)
        consultation_fee = request.form.get("consultation_fee", 0)
        available_days = request.form.get("available_days", "").strip()
        available_time = request.form.get("available_time", "").strip()

        conn = get_db_connection()
        existing = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        if existing:
            flash("That username is already taken.", "danger")
            conn.close()
            return render_template("add_doctor.html")

        password_hash = generate_password_hash(password)
        cursor = conn.execute(
            """INSERT INTO users (username, password, full_name, email, role)
               VALUES (?, ?, ?, ?, 'doctor')""",
            (username, password_hash, full_name, email),
        )
        user_id = cursor.lastrowid

        conn.execute(
            """INSERT INTO doctors
               (user_id, specialization, department, qualification, experience_years,
                consultation_fee, available_days, available_time)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, specialization, department, qualification, experience_years,
             consultation_fee, available_days, available_time),
        )
        conn.commit()
        conn.close()
        flash("Doctor added successfully.", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("add_doctor.html")


@app.route("/admin/toggle-doctor/<int:doctor_id>")
@login_required(role="admin")
def toggle_doctor(doctor_id):
    conn = get_db_connection()
    conn.execute(
        "UPDATE doctors SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END WHERE id = ?",
        (doctor_id,),
    )
    conn.commit()
    conn.close()
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/all-appointments")
@login_required(role="admin")
def all_appointments():
    status_filter = request.args.get("status", "")
    conn = get_db_connection()
    query = """SELECT appointments.*, patients.full_name AS patient_name, docs.full_name AS doctor_name
               FROM appointments
               JOIN users AS patients ON appointments.patient_id = patients.id
               JOIN doctors ON appointments.doctor_id = doctors.id
               JOIN users AS docs ON doctors.user_id = docs.id"""
    params = ()
    if status_filter:
        query += " WHERE appointments.status = ?"
        params = (status_filter,)
    query += " ORDER BY appointments.appointment_date DESC"

    appointments = conn.execute(query, params).fetchall()
    conn.close()
    return render_template("all_appointments.html", appointments=appointments, selected_status=status_filter)


if __name__ == "__main__":
    app.run(debug=True)
