"""MySQL helpers + password hashing."""
import os, hashlib, hmac
import mysql.connector
from dotenv import load_dotenv

load_dotenv()
BASE = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.getenv("DB_NAME", "hospital_db")

def get_conn(with_db=True):
    cfg = dict(host=os.getenv("DB_HOST", "localhost"),
               port=int(os.getenv("DB_PORT", "3306")),
               user=os.getenv("DB_USER", "root"),
               password=os.getenv("DB_PASSWORD", ""))
    if with_db:
        cfg["database"] = DB_NAME
    return mysql.connector.connect(**cfg)

def fetch_all(sql, params=None):
    c = get_conn(); cur = c.cursor(dictionary=True)
    cur.execute(sql, params or None)
    rows = cur.fetchall()
    cur.close(); c.close()
    return rows

def execute(sql, params=None):
    c = get_conn(); cur = c.cursor()
    cur.execute(sql, params or None)
    c.commit()
    last = cur.lastrowid
    cur.close(); c.close()
    return last

def hash_password(pw):
    salt = os.urandom(16)
    h = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt, 100_000)
    return salt.hex() + "$" + h.hex()

def verify_password(pw, stored):
    try:
        salt, h = stored.split("$")
        new = hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt), 100_000).hex()
        return hmac.compare_digest(new, h)
    except Exception:
        return False

def init_db():
    """Create database, tables and a default admin account (first run only)."""
    c = get_conn(with_db=False); cur = c.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`")
    c.commit(); cur.close(); c.close()

    c = get_conn(); cur = c.cursor()
    for stmt in open(os.path.join(BASE, "schema.sql")).read().split(";"):
        if stmt.strip():
            cur.execute(stmt)
    cur.execute("SELECT id FROM users WHERE role='admin' LIMIT 1")
    if not cur.fetchone():
        cur.execute("INSERT INTO users(full_name,email,password_hash,role) VALUES(%s,%s,%s,'admin')",
                    ("System Admin", "admin@hospital.com", hash_password("admin123")))
    cur.execute("SELECT id FROM doctors LIMIT 1")
    if not cur.fetchone():
        cur.execute("SELECT id FROM users WHERE email=%s", ("doctor@hospital.com",))
        row = cur.fetchone()
        if row:
            uid = row[0]
        else:
            cur.execute(
                "INSERT INTO users(full_name,email,phone,password_hash,role) VALUES(%s,%s,%s,%s,'doctor')",
                ("Anita Sharma", "doctor@hospital.com", "9876543210", hash_password("doctor123")),
            )
            uid = cur.lastrowid
        cur.execute(
            """INSERT INTO doctors(user_id,specialization,experience_years,consultation_fee,
               available_days,start_time,end_time,slot_minutes) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""",
            (uid, "Cardiology", 8, 500.0, "Mon,Tue,Wed,Thu,Fri", "09:00", "17:00", 30),
        )
    c.commit(); cur.close(); c.close()
