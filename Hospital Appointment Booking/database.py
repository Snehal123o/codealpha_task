

import sqlite3
from werkzeug.security import generate_password_hash

DB_NAME = "hospital.db"


def get_db_connection():
    """Open a connection with rows returned as dict-like objects."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables from schema.sql and seed a default admin account."""
    conn = get_db_connection()
    with open("schema.sql", "r") as f:
        conn.executescript(f.read())

    admin_password_hash = generate_password_hash("admin123")
    conn.execute(
        """INSERT INTO users (username, password, full_name, email, phone, role)
           VALUES (?, ?, ?, ?, ?, ?)""",
        ("admin", admin_password_hash, "System Admin", "admin@hospital.com", "0000000000", "admin"),
    )
    conn.commit()
    conn.close()
    print("Database initialized. Default admin login -> username: admin | password: admin123")


if __name__ == "__main__":
    init_db()
