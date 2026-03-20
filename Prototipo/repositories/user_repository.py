"""
repositories/user_repository.py
Acceso a datos — todos los queries SQL de usuarios.
"""
import sqlite3
from typing import Optional
from database.connection import get_connection, hash_password
from models.user import User


def _row_to_user(row: sqlite3.Row) -> User:
    return User(
        id            = row["id"],
        nombre        = row["nombre"],
        email         = row["email"],
        telefono      = row["telefono"] or "",
        ciudad        = row["ciudad"]   or "",
        password_hash = row["password_hash"],
        rol           = row["rol"],
        activo        = bool(row["activo"]),
        fecha_registro= row["fecha_registro"] or "",
    )


def crear(user: User) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO usuarios
               (nombre, email, telefono, ciudad, password_hash, rol)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user.nombre, user.email, user.telefono,
             user.ciudad, user.password_hash, user.rol)
        )
        return cur.lastrowid


def obtener_todos(filtro: str = "") -> list[User]:
    with get_connection() as conn:
        if filtro:
            rows = conn.execute(
                """SELECT * FROM usuarios
                   WHERE nombre  LIKE ?
                      OR email   LIKE ?
                      OR ciudad  LIKE ?
                      OR telefono LIKE ?
                   ORDER BY nombre""",
                tuple(f"%{filtro}%" for _ in range(4))
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM usuarios ORDER BY nombre"
            ).fetchall()
        return [_row_to_user(r) for r in rows]


def obtener_por_id(uid: int) -> Optional[User]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM usuarios WHERE id = ?", (uid,)
        ).fetchone()
        return _row_to_user(row) if row else None


def obtener_por_email(email: str) -> Optional[User]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM usuarios WHERE email = ?", (email,)
        ).fetchone()
        return _row_to_user(row) if row else None


def actualizar(user: User) -> None:
    with get_connection() as conn:
        conn.execute(
            """UPDATE usuarios
               SET nombre=?, email=?, telefono=?, ciudad=?, rol=?, activo=?
               WHERE id=?""",
            (user.nombre, user.email, user.telefono,
             user.ciudad, user.rol, int(user.activo), user.id)
        )


def actualizar_password(uid: int, nueva_password: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE usuarios SET password_hash=? WHERE id=?",
            (hash_password(nueva_password), uid)
        )


def eliminar(uid: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM usuarios WHERE id=?", (uid,))


def email_existe(email: str, excluir_id: Optional[int] = None) -> bool:
    with get_connection() as conn:
        if excluir_id:
            row = conn.execute(
                "SELECT id FROM usuarios WHERE email=? AND id!=?",
                (email, excluir_id)
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT id FROM usuarios WHERE email=?", (email,)
            ).fetchone()
        return row is not None


def autenticar(email: str, password: str) -> Optional[User]:
    with get_connection() as conn:
        row = conn.execute(
            """SELECT * FROM usuarios
               WHERE email=? AND password_hash=? AND activo=1""",
            (email, hash_password(password))
        ).fetchone()
        return _row_to_user(row) if row else None


def contar() -> int:
    with get_connection() as conn:
        return conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
