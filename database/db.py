import os
import sqlite3
from datetime import date

from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "spendly.db"
)

# scrypt is unavailable on this project's Python 3.9 build, so pin pbkdf2.
PASSWORD_HASH_METHOD = "pbkdf2:sha256"


def get_db():
    """Open a connection to spendly.db with Row access and FK enforcement."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create tables if they don't exist. Safe to call repeatedly."""
    conn = get_db()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT NOT NULL,
                email         TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at    TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS expenses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                amount      REAL NOT NULL,
                category    TEXT NOT NULL,
                date        TEXT NOT NULL,
                description TEXT,
                created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


def seed_db():
    """Insert a demo user and sample expenses. No-op if users already exist."""
    conn = get_db()
    try:
        if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
            return

        cur = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com",
             generate_password_hash("demo123", method=PASSWORD_HASH_METHOD)),
        )
        user_id = cur.lastrowid

        today = date.today()

        def d(day):
            return date(today.year, today.month, min(day, today.day)).isoformat()

        expenses = [
            (user_id, 12.50, "Food", d(1), "Lunch"),
            (user_id, 45.00, "Food", d(3), "Groceries"),
            (user_id, 20.00, "Transport", d(5), "Metro pass top-up"),
            (user_id, 120.00, "Bills", d(7), "Electricity bill"),
            (user_id, 60.00, "Health", d(10), "Pharmacy"),
            (user_id, 30.00, "Entertainment", d(14), "Movie night"),
            (user_id, 85.99, "Shopping", d(18), "New shoes"),
            (user_id, 15.00, "Other", d(21), "Miscellaneous"),
        ]
        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) "
            "VALUES (?, ?, ?, ?, ?)",
            expenses,
        )
        conn.commit()
    finally:
        conn.close()


def create_user(name, email, password):
    """Insert a new user with a hashed password and return the new id.

    Raises sqlite3.IntegrityError if the email is already registered.
    """
    conn = get_db()
    try:
        cur = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, generate_password_hash(password, method=PASSWORD_HASH_METHOD)),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_user_by_email(email):
    """Return the user row matching email, or None if not found."""
    conn = get_db()
    try:
        return conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
    finally:
        conn.close()
