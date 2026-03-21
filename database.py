"""
database.py — SQLite-backed user authentication for the Y-Strainer app.

Passwords are hashed with PBKDF2-HMAC-SHA256 (100 000 iterations) using
Python's standard-library hashlib — no external dependencies required.
"""

import hashlib
import os
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "users.db"


def init_db() -> None:
    """Create the users table if it does not already exist."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                username      TEXT    UNIQUE NOT NULL,
                email         TEXT    UNIQUE NOT NULL,
                password_hash TEXT    NOT NULL,
                created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


# ── Password helpers ───────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return salt.hex() + ":" + key.hex()


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt_hex, key_hex = stored_hash.split(":", 1)
        salt = bytes.fromhex(salt_hex)
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
        return key.hex() == key_hex
    except Exception:
        return False


# ── CRUD helpers ───────────────────────────────────────────────────────────────

def create_user(username: str, email: str, password: str) -> tuple:
    """Register a new user.  Returns (True, '') on success or (False, reason)."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username.strip(), email.strip().lower(), hash_password(password)),
            )
            conn.commit()
        return True, ""
    except sqlite3.IntegrityError as exc:
        msg = str(exc).lower()
        if "username" in msg:
            return False, "Username already taken."
        if "email" in msg:
            return False, "Email already registered."
        return False, "Registration failed."


def get_user_by_username(username: str) -> dict | None:
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT id, username, email, password_hash FROM users WHERE username = ?",
            (username.strip(),),
        ).fetchone()
    if row:
        return {"id": row[0], "username": row[1], "email": row[2], "password_hash": row[3]}
    return None
