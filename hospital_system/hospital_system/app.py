import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import db
import email_service as mail

st.set_page_config(page_title="Smart Hospital", page_icon="🏥", layout="wide")

@st.cache_resource
def setup():
    db.init_db()
    return True

try:
    setup()
except Exception as e:
    st.error(f"Cannot connect to MySQL: {e}")
    st.info("Check that MySQL is running and that your .env file has the right DB_USER and DB_PASSWORD.")
    st.stop()

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

APPT_SQL = """
SELECT a.id, a.appointment_date AS appt_date, LEFT(CAST(a.appointment_time AS CHAR),5) AS appt_time,
       p.full_name AS patient_name, p.email AS patient_email, p.phone AS patient_phone,
       du.full_name AS doctor_name, d.specialization, a.reason, a.status, a.doctor_notes AS notes,
       d.id AS doctor_id
FROM appointments a
JOIN users p ON p.id = a.patient_id
JOIN doctors d ON d.id = a.doctor_id
JOIN users du ON du.id = d.user_id
"""

DOCTOR_SQL = """
SELECT d.id, d.user_id, u.full_name, u.email, u.phone, d.specialization, d.experience_years,
       d.consultation_fee, d.available_days, d.slot_minutes,
       LEFT(CAST(d.start_time AS CHAR),5) AS start_t, LEFT(CAST(d.end_time AS CHAR),5) AS end_t
FROM doctors d JOIN users u ON u.id = d.user_id
"""

# ---------------- helpers ----------------
def flash(msg, kind="success"):
    st.session_state.flash = (kind, msg)

def show_flash():
    if "flash" in st.session_state:
        kind, msg = st.session_state.pop("flash")
        getattr(st, kind)(msg)

def get_appt(appt_id):
    return db.fetch_all(APPT_SQL + " WHERE a.id=%s", (appt_id,))[0]

def free_slots(doc, day):
    if day.strftime("%a") not in doc["available_days"].split(","):
        return []
    step = timedelta(minutes=doc["slot_minutes"])
    cur = datetime.combine(day, datetime.strptime(doc["start_t"], "%H:%M").time())
    end = datetime.combine(day, datetime.strptime(doc["end_t"], "%H:%M").time())
    booked = {r["t"] for r in db.fetch_all(
        "SELECT LEFT(CAST(appointment_time AS CHAR),5) AS t FROM appointments "
        "WHERE doctor_id=%s AND appointment_date=%s AND status<>'Cancelled'", (doc["id"], day))}
    out = []
    while cur + step <= end:
        t = cur.strftime("%H:%M")
        if t not in booked and cur > datetime.now():
            out.append(t)
        cur += step
    return out

def cancel_appt(appt_id):
    db.execute("UPDATE appointments SET status='Cancelled' WHERE id=%s", (appt_id,))
    a = get_appt(appt_id)
    ok, msg = mail.send_email(a["patient_email"], f"Appointment #{a['id']} cancelled", mail.cancel_email(a))
    flash(f"Appointment #{appt_id} cancelled. {msg}", "success" if ok else "warning")

def appt_card(r, actions=None, who="doctor"):
    with st.container(border=True):
        c1, c2 = st.columns([4, 1])
        title = f"Dr. {r['doctor_name']} ({r['specialization']})" if who == "doctor" else f"{r['patient_name']}"
        c1.markdown(f"**{title}**  \n{r['appt_date']} at {r['appt_time']} · **{r['status']}**")
        if r["reason"]:
            c1.caption(f"Reason: {r['reason']}")
        if r["notes"]:
            c1.info(f"Doctor's notes: {r['notes']}")
        return c2

# ---------------- login / signup ----------------
def auth_screen():
    st.title("🏥 Smart Hospital Appointment System")
    st.caption("Book, manage and track appointments in one place.")
    t1, t2 = st.tabs(["Log in", "Patient sign up"])
    with t1:
        with st.form("login"):
            email = st.text_input("Email")
            pw = st.text_input("Password", type="password")
            if st.form_submit_button("Log in"):
                rows = db.fetch_all("SELECT * FROM users WHERE email=%s", (email.strip().lower(),))
                if rows and db.verify_password(pw, rows[0]["password_hash"]):
                    u = rows[0]
                    st.session_state.user = dict(id=u["id"], full_name=u["full_name"],
                                                 email=u["email"], role=u["role"])
                    st.rerun()
                else:
                    st.error("Wrong email or password.")
    with t2:
        with st.form("signup"):
            name = st.text_input("Full name")
            email = st.text_input("Email address")
            phone = st.text_input("Phone")
            pw = st.text_input("Password (min 6 characters)", type="password")
            if st.form_submit_button("Create account"):
                if not name.strip() or "@" not in email or len(pw) < 6:
                    st.error("Enter your name, a valid email and a password of at least 6 characters.")
                elif db.fetch_all("SELECT id FROM users WHERE email=%s", (email.strip().lower(),)):
                    st.error("That email is already registered.")
                else:
                    db.execute("INSERT INTO users(full_name,email,phone,password_hash,role) VALUES(%s,%s,%s,%s,'patient')",
                               (name.strip(), email.strip().lower(), phone.strip(), db.hash_password(pw)))
                    st.success("Account created. You can log in now.")
    st.caption("Doctor accounts are created by the hospital admin.")

# ---------------- PATIENT ----------------
def patient_book(user):
    st.subheader("Book an appointment")
    docs = db.fetch_all(DOCTOR_SQL + " ORDER BY u.full_name")
    if not docs:
        st.info("No doctors have been added yet. Please check back soon.")
        return
    spec = st.selectbox("Specialization", ["All"] + sorted({d["specialization"] for d in docs}))
    pool = [d for d in docs if spec == "All" or d["specialization"] == spec]
    doc = st.selectbox("Doctor", pool, format_func=lambda d: f"Dr. {d['full_name']} · {d['specialization']} · fee {d['consultation_fee']}")
    st.caption(f"Works {doc['available_days']} · {doc['start_t']}–{doc['end_t']} · {doc['slot_minutes']}-minute slots")
    day = st.date_input("Date", value=date.today(), min_value=date.today())
    slots = free_slots(doc, day)
    if not slots:
        st.warning("No free slots on this date. Try another day.")
        return
    with st.form("book"):
        slot = st.selectbox("Time slot", slots)
        reason = st.text_area("Reason for visit", max_chars=250)
        if st.form_submit_button("Confirm booking"):
            if slot not in free_slots(doc, day):
                st.error("That slot was just taken. Please pick another.")
                return
            appt_id = db.execute(
                "INSERT INTO appointments(patient_id,doctor_id,appointment_date,appointment_time,reason) VALUES(%s,%s,%s,%s,%s)",
                (user["id"], doc["id"], day, slot, reason.strip()))
            a = get_appt(appt_id)
            ok, msg = mail.send_email(a["patient_email"], f"Appointment confirmed – #{appt_id}", mail.booking_email(a))
            if ok:
                db.execute("UPDATE appointments SET email_sent=TRUE WHERE id=%s", (appt_id,))
            flash(f"Booked with Dr. {a['doctor_name']} on {a['appt_date']} at {a['appt_time']}. {msg}",
                  "success" if ok else "warning")
            st.rerun()

def patient_list(user):
    st.subheader("My appointments")
    rows = db.fetch_all(APPT_SQL + " WHERE a.patient_id=%s ORDER BY a.appointment_date DESC, a.appointment_time DESC", (user["id"],))
    if not rows:
        st.info("You have no appointments yet. Book one from the Book appointment page.")
    for r in rows:
        col = appt_card(r, who="doctor")
        if r["status"] == "Confirmed" and r["appt_date"] >= date.today():
            if col.button("Cancel", key=f"pc{r['id']}"):
                cancel_appt(r["id"]); st.rerun()

# ---------------- DOCTOR ----------------
def my_doctor(user):
    return db.fetch_all(DOCTOR_SQL + " WHERE d.user_id=%s", (user["id"],))[0]

def doctor_dashboard(user):
    doc = my_doctor(user)
    st.subheader(f"Welcome, Dr. {user['full_name']}")
    rows = db.fetch_all(APPT_SQL + " WHERE a.doctor_id=%s", (doc["id"],))
    today = date.today()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Today", sum(r["appt_date"] == today and r["status"] == "Confirmed" for r in rows))
    c2.metric("Upcoming", sum(r["appt_date"] > today and r["status"] == "Confirmed" for r in rows))
    c3.metric("Completed", sum(r["status"] == "Completed" for r in rows))
    c4.metric("Patients seen", len({r["patient_email"] for r in rows if r["status"] == "Completed"}))
    st.markdown("#### Today's schedule")
    todays = sorted([r for r in rows if r["appt_date"] == today and r["status"] == "Confirmed"], key=lambda r: r["appt_time"])
    if todays:
        st.dataframe(pd.DataFrame(todays)[["appt_time", "patient_name", "patient_phone", "reason"]]
                     .rename(columns=lambda c: c.replace("_", " ").title()), hide_index=True, use_container_width=True)
    else:
        st.info("No appointments today.")

def doctor_appointments(user):
    doc = my_doctor(user)
    st.subheader("Appointments")
    view = st.radio("Show", ["Upcoming", "Completed", "Cancelled", "All"], horizontal=True)
    rows = db.fetch_all(APPT_SQL + " WHERE a.doctor_id=%s ORDER BY a.appointment_date, a.appointment_time", (doc["id"],))
    if view == "Upcoming":
        rows = [r for r in rows if r["status"] == "Confirmed"]
    elif view != "All":
        rows = [r for r in rows if r["status"] == view]
    if not rows:
        st.info("Nothing to show here.")
    for r in rows:
        col = appt_card(r, who="patient")
        if r["status"] == "Confirmed":
            with col.popover("Manage"):
                notes = st.text_area("Notes / prescription", key=f"n{r['id']}")
                if st.button("Mark completed", key=f"d{r['id']}"):
                    db.execute("UPDATE appointments SET status='Completed', doctor_notes=%s WHERE id=%s", (notes.strip(), r["id"]))
                    flash(f"Appointment #{r['id']} marked as completed."); st.rerun()
                if st.button("Cancel appointment", key=f"x{r['id']}"):
                    cancel_appt(r["id"]); st.rerun()

def doctor_schedule(user):
    doc = my_doctor(user)
    st.subheader("My availability")
    with st.form("sched"):
        days = st.multiselect("Working days", DAYS, default=doc["available_days"].split(","))
        c1, c2, c3 = st.columns(3)
        start = c1.time_input("Start time", datetime.strptime(doc["start_t"], "%H:%M").time())
        end = c2.time_input("End time", datetime.strptime(doc["end_t"], "%H:%M").time())
        slot = c3.selectbox("Slot length (min)", [15, 20, 30, 45, 60], index=[15, 20, 30, 45, 60].index(doc["slot_minutes"]) if doc["slot_minutes"] in [15, 20, 30, 45, 60] else 2)
        if st.form_submit_button("Save schedule"):
            if not days or start >= end:
                st.error("Choose at least one day and make sure the end time is after the start time.")
            else:
                db.execute("UPDATE doctors SET available_days=%s, start_time=%s, end_time=%s, slot_minutes=%s WHERE id=%s",
                           (",".join(d for d in DAYS if d in days), start.strftime("%H:%M"), end.strftime("%H:%M"), slot, doc["id"]))
                flash("Schedule updated."); st.rerun()

# ---------------- ADMIN ----------------
def admin_dashboard():
    st.subheader("Hospital overview")
    n = lambda q: db.fetch_all(q)[0]["n"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Patients", n("SELECT COUNT(*) AS n FROM users WHERE role='patient'"))
    c2.metric("Doctors", n("SELECT COUNT(*) AS n FROM doctors"))
    c3.metric("Appointments", n("SELECT COUNT(*) AS n FROM appointments"))
    c4.metric("Today", n("SELECT COUNT(*) AS n FROM appointments WHERE appointment_date=CURDATE() AND status='Confirmed'"))
    l, r = st.columns(2)
    by_status = pd.DataFrame(db.fetch_all("SELECT status, COUNT(*) AS total FROM appointments GROUP BY status"))
    by_spec = pd.DataFrame(db.fetch_all("""SELECT d.specialization, COUNT(*) AS total FROM appointments a
        JOIN doctors d ON d.id=a.doctor_id GROUP BY d.specialization"""))
    l.markdown("**Appointments by status**")
    r.markdown("**Appointments by specialization**")
    if not by_status.empty:
        l.bar_chart(by_status.set_index("status"))
        r.bar_chart(by_spec.set_index("specialization"))
    else:
        l.info("No appointments yet.")

def admin_doctors():
    st.subheader("Doctors")
    t1, t2 = st.tabs(["All doctors", "Add doctor"])
    with t1:
        docs = db.fetch_all(DOCTOR_SQL + " ORDER BY u.full_name")
        if not docs:
            st.info("No doctors yet. Add one in the next tab.")
        else:
            df = pd.DataFrame(docs)[["id", "full_name", "email", "phone", "specialization", "experience_years",
                                     "consultation_fee", "available_days", "start_t", "end_t"]]
            st.dataframe(df, hide_index=True, use_container_width=True)
            target = st.selectbox("Remove a doctor", docs, format_func=lambda d: f"Dr. {d['full_name']} ({d['specialization']})")
            if st.button("Remove doctor"):
                db.execute("DELETE FROM users WHERE id=%s", (target["user_id"],))
                flash("Doctor removed along with their appointments."); st.rerun()
    with t2:
        with st.form("add_doc", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name, email = c1.text_input("Full name"), c2.text_input("Email")
            phone, pw = c1.text_input("Phone"), c2.text_input("Temporary password", type="password")
            spec = c1.text_input("Specialization (e.g. Cardiology)")
            exp = c2.number_input("Experience (years)", 0, 60, 5)
            fee = c1.number_input("Consultation fee", 0.0, 100000.0, 500.0, step=50.0)
            days = c2.multiselect("Working days", DAYS, default=DAYS[:5])
            t_start = c1.time_input("Start time", datetime.strptime("09:00", "%H:%M").time())
            t_end = c2.time_input("End time", datetime.strptime("17:00", "%H:%M").time())
            slot = c1.selectbox("Slot length (min)", [15, 20, 30, 45, 60], index=2)
            if st.form_submit_button("Add doctor"):
                if not (name.strip() and spec.strip() and "@" in email and len(pw) >= 6 and days) or t_start >= t_end:
                    st.error("Fill every field, use a password of 6+ characters, and make sure end time is after start time.")
                elif db.fetch_all("SELECT id FROM users WHERE email=%s", (email.strip().lower(),)):
                    st.error("That email is already registered.")
                else:
                    uid = db.execute("INSERT INTO users(full_name,email,phone,password_hash,role) VALUES(%s,%s,%s,%s,'doctor')",
                                     (name.strip(), email.strip().lower(), phone.strip(), db.hash_password(pw)))
                    db.execute("""INSERT INTO doctors(user_id,specialization,experience_years,consultation_fee,
                                  available_days,start_time,end_time,slot_minutes) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""",
                               (uid, spec.strip(), exp, fee, ",".join(d for d in DAYS if d in days),
                                t_start.strftime("%H:%M"), t_end.strftime("%H:%M"), slot))
                    flash(f"Dr. {name} added. They can now log in."); st.rerun()

def admin_patients():
    st.subheader("Patients")
    rows = db.fetch_all("""SELECT u.id, u.full_name, u.email, u.phone, u.created_at AS registered,
        COUNT(a.id) AS appointments FROM users u LEFT JOIN appointments a ON a.patient_id=u.id
        WHERE u.role='patient' GROUP BY u.id ORDER BY u.created_at DESC""")
    if rows:
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
    else:
        st.info("No patients have registered yet.")

def admin_appointments():
    st.subheader("All appointments")
    rows = db.fetch_all(APPT_SQL + " ORDER BY a.appointment_date DESC, a.appointment_time DESC")
    if not rows:
        st.info("No appointments yet.")
        return
    status = st.multiselect("Filter by status", ["Confirmed", "Completed", "Cancelled"], default=["Confirmed", "Completed", "Cancelled"])
    rows = [r for r in rows if r["status"] in status]
    st.dataframe(pd.DataFrame(rows)[["id", "appt_date", "appt_time", "patient_name", "doctor_name", "specialization", "reason", "status"]],
                 hide_index=True, use_container_width=True)
    active = [r for r in rows if r["status"] == "Confirmed"]
    if active:
        pick = st.selectbox("Cancel an appointment", active, format_func=lambda r: f"#{r['id']} · {r['patient_name']} → Dr. {r['doctor_name']} · {r['appt_date']} {r['appt_time']}")
        if st.button("Cancel selected appointment"):
            cancel_appt(pick["id"]); st.rerun()

# ---------------- router ----------------
if "user" not in st.session_state:
    auth_screen()
    st.stop()

user = st.session_state.user
PAGES = {
    "patient": {"Book appointment": lambda: patient_book(user), "My appointments": lambda: patient_list(user)},
    "doctor": {"Dashboard": lambda: doctor_dashboard(user), "Appointments": lambda: doctor_appointments(user),
               "My availability": lambda: doctor_schedule(user)},
    "admin": {"Overview": admin_dashboard, "Doctors": admin_doctors, "Patients": admin_patients,
              "Appointments": admin_appointments},
}[user["role"]]

with st.sidebar:
    st.markdown("### 🏥 Smart Hospital")
    st.write(f"**{user['full_name']}**")
    st.caption(user["role"].title())
    page = st.radio("Menu", list(PAGES), label_visibility="collapsed")
    if st.button("Log out"):
        st.session_state.clear(); st.rerun()

show_flash()
PAGES[page]()
