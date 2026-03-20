"""
database/connection.py
Conexión a SQLite y creación de tablas.
"""
import sqlite3
import hashlib
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "petcare.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def initialize() -> None:
    """Crea las tablas e inserta datos demo si la BD está vacía."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre         TEXT    NOT NULL,
                email          TEXT    UNIQUE NOT NULL,
                telefono       TEXT    DEFAULT '',
                ciudad         TEXT    DEFAULT '',
                password_hash  TEXT    NOT NULL,
                rol            TEXT    NOT NULL DEFAULT 'dueño'
                               CHECK(rol IN ('dueño','cuidador','admin')),
                activo         INTEGER DEFAULT 1,
                fecha_registro TEXT    DEFAULT CURRENT_DATE
            )
        """)

        if conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] == 0:
            _insertar_demo(conn)


def _insertar_demo(conn: sqlite3.Connection) -> None:
    demo = [
        ("Administrador", "admin@petcare.bo",   "70000000", "Sucre", hash_password("admin123"), "admin"),
        ("María Pérez",   "maria@example.com",  "71111111", "Sucre", hash_password("1234"),     "dueño"),
        ("Carlos Rojas",  "carlos@example.com", "72222222", "Sucre", hash_password("1234"),     "dueño"),
        ("Ana Flores",    "ana@example.com",    "73333333", "Sucre", hash_password("1234"),     "cuidador"),
        ("Pedro Lima",    "pedro@example.com",  "74444444", "Sucre", hash_password("1234"),     "cuidador"),
    ]
    conn.executemany(
        "INSERT INTO usuarios (nombre,email,telefono,ciudad,password_hash,rol) VALUES (?,?,?,?,?,?)",
        demo
    )
