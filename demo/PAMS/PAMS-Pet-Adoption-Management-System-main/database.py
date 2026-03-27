"""
database.py — Schema initialization & seed data for PAMS
Handles table creation, indexes for query performance, and optional demo seed data.
"""

import sqlite3
import hashlib
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'petadoption.db')


def get_db_connection():
    """Return a connection with Row factory and FK enforcement enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")   # enforce FK constraints
    conn.execute("PRAGMA journal_mode = WAL")  # better concurrent read perf
    return conn


def init_db():
    """Create all tables, indexes, and admin account if DB is fresh."""
    conn = get_db_connection()
    cur = conn.cursor()

    # ── Users ───────────────────────────────────────────────────────────────
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            user_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT    NOT NULL,
            email     TEXT    UNIQUE NOT NULL,
            phone     TEXT,
            address   TEXT,
            created_at TEXT DEFAULT (DATE('now'))
        )
    ''')

    # ── Pets ────────────────────────────────────────────────────────────────
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Pets (
            pet_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            species     TEXT    NOT NULL,
            breed       TEXT,
            age         INTEGER CHECK(age >= 0),
            gender      TEXT    CHECK(gender IN ('Male','Female','Unknown')),
            description TEXT,
            image_url   TEXT    DEFAULT '/static/img/default_pet.png',
            status      TEXT    DEFAULT 'Available'
                        CHECK(status IN ('Available','Pending','Adopted')),
            added_on    TEXT    DEFAULT (DATE('now'))
        )
    ''')

    # ── Adoption Requests ───────────────────────────────────────────────────
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Adoption_Requests (
            request_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            pet_id       INTEGER NOT NULL,
            request_date TEXT    DEFAULT (DATE('now')),
            status       TEXT    DEFAULT 'Pending'
                         CHECK(status IN ('Pending','Approved','Rejected')),
            notes        TEXT,
            FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (pet_id)  REFERENCES Pets(pet_id)   ON DELETE CASCADE,
            UNIQUE(user_id, pet_id)   -- prevent duplicate requests
        )
    ''')

    # ── Admin ───────────────────────────────────────────────────────────────
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Admin (
            admin_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            username  TEXT UNIQUE NOT NULL,
            password  TEXT NOT NULL   -- SHA-256 hashed
        )
    ''')

    # ── Indexes for common query patterns ──────────────────────────────────
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pets_status   ON Pets(status)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pets_species  ON Pets(species)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ar_user       ON Adoption_Requests(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ar_pet        ON Adoption_Requests(pet_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ar_status     ON Adoption_Requests(status)")

    # ── Default admin (username: admin / password: admin123) ───────────────
    pwd_hash = hashlib.sha256("admin123".encode()).hexdigest()
    cur.execute(
        "INSERT OR IGNORE INTO Admin (username, password) VALUES (?, ?)",
        ("admin", pwd_hash)
    )

    # ── Seed demo pets ─────────────────────────────────────────────────────
    existing = cur.execute("SELECT COUNT(*) FROM Pets").fetchone()[0]
    if existing == 0:
        demo_pets = [
            ("Buddy",   "Dog",    "Golden Retriever", 3, "Male",   "Friendly and loves fetch!"),
            ("Whiskers","Cat",    "Persian",          5, "Female", "Calm, indoor cat."),
            ("Thumper", "Rabbit", "Holland Lop",      2, "Male",   "Great with kids."),
            ("Nemo",    "Fish",   "Clownfish",        1, "Unknown","Low-maintenance and colorful."),
            ("Daisy",   "Dog",    "Beagle",           4, "Female", "Energetic and playful."),
            ("Shadow",  "Cat",    "Siamese",          6, "Male",   "Loves quiet evenings."),
        ]
        cur.executemany(
            "INSERT INTO Pets (name, species, breed, age, gender, description) VALUES (?,?,?,?,?,?)",
            demo_pets
        )

    conn.commit()
    conn.close()
    print("✅ Database initialized.")


if __name__ == "__main__":
    init_db()
