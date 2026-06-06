import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "network_monitor.db")


def get_connection():
    """Get a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT NOT NULL,
            hostname TEXT,
            first_seen TEXT NOT NULL,
            last_seen TEXT NOT NULL,
            status TEXT DEFAULT 'online'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT NOT NULL,
            hostname TEXT,
            event_type TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def upsert_device(ip: str, hostname: str, timestamp: str):
    """Insert a new device or update last_seen if it already exists."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM devices WHERE ip = ?", (ip,))
    existing = cursor.fetchone()

    if existing:
        cursor.execute(
            "UPDATE devices SET last_seen = ?, hostname = ?, status = 'online' WHERE ip = ?",
            (timestamp, hostname, ip)
        )
    else:
        cursor.execute(
            "INSERT INTO devices (ip, hostname, first_seen, last_seen, status) VALUES (?, ?, ?, ?, 'online')",
            (ip, hostname, timestamp, timestamp)
        )

    conn.commit()
    conn.close()
    return existing is None  # True if this is a new device


def log_event(ip: str, hostname: str, event_type: str, timestamp: str):
    """Log a network event (joined, left, etc.)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO events (ip, hostname, event_type, timestamp) VALUES (?, ?, ?, ?)",
        (ip, hostname, event_type, timestamp)
    )
    conn.commit()
    conn.close()


def get_all_devices():
    """Return all known devices."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM devices ORDER BY last_seen DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_recent_events(limit: int = 20):
    """Return the most recent events."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows
    