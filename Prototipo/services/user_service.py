"""
services/user_service.py
Lógica de negocio — validaciones y operaciones sobre usuarios.
"""
import re
from typing import Optional
from models.user import User
from database.connection import hash_password
import repositories.user_repository as repo


class UserServiceError(Exception):
    """Error de validación o regla de negocio."""
    pass


# ── Autenticación ────────────────────────────────────────────
def login(email: str, password: str) -> User:
    email = email.strip().lower()
    if not email or not password:
        raise UserServiceError("Completa todos los campos.")
    user = repo.autenticar(email, password)
    if not user:
        raise UserServiceError("Correo o contraseña incorrectos.")
    return user


# ── Crear ────────────────────────────────────────────────────
def crear_usuario(nombre: str, email: str, telefono: str,
                  ciudad: str, password: str, rol: str) -> User:
    _validar_campos(nombre, email, password=password, rol=rol)

    email = email.strip().lower()
    if repo.email_existe(email):
        raise UserServiceError("El correo ya está registrado.")

    user = User(
        nombre        = nombre.strip(),
        email         = email,
        telefono      = telefono.strip(),
        ciudad        = ciudad.strip(),
        password_hash = hash_password(password),
        rol           = rol,
    )
    user.id = repo.crear(user)
    return user


# ── Actualizar ───────────────────────────────────────────────
def actualizar_usuario(uid: int, nombre: str, email: str,
                       telefono: str, ciudad: str, rol: str,
                       activo: bool, nueva_password: str = "",
                       usuario_actual_id: int = None) -> User:
    _validar_campos(nombre, email, rol=rol)

    email = email.strip().lower()
    if repo.email_existe(email, excluir_id=uid):
        raise UserServiceError("El correo ya está en uso por otro usuario.")

    if uid == usuario_actual_id and not activo:
        raise UserServiceError("No puedes desactivar tu propia cuenta.")

    user = repo.obtener_por_id(uid)
    if not user:
        raise UserServiceError("Usuario no encontrado.")

    user.nombre   = nombre.strip()
    user.email    = email
    user.telefono = telefono.strip()
    user.ciudad   = ciudad.strip()
    user.rol      = rol
    user.activo   = activo

    repo.actualizar(user)

    if nueva_password:
        if len(nueva_password) < 4:
            raise UserServiceError("La nueva contraseña debe tener al menos 4 caracteres.")
        repo.actualizar_password(uid, nueva_password)

    return user


# ── Eliminar ─────────────────────────────────────────────────
def eliminar_usuario(uid: int, usuario_actual_id: int) -> None:
    if uid == usuario_actual_id:
        raise UserServiceError("No puedes eliminar tu propia cuenta.")
    if not repo.obtener_por_id(uid):
        raise UserServiceError("Usuario no encontrado.")
    repo.eliminar(uid)


# ── Buscar ───────────────────────────────────────────────────
def buscar_usuarios(filtro: str = "") -> list[User]:
    return repo.obtener_todos(filtro.strip())


def contar_usuarios() -> int:
    return repo.contar()


# ── Validaciones internas ────────────────────────────────────
def _validar_campos(nombre: str, email: str,
                    password: str = "", rol: str = "") -> None:
    if not nombre or not nombre.strip():
        raise UserServiceError("El nombre es obligatorio.")
    if len(nombre.strip()) < 3:
        raise UserServiceError("El nombre debe tener al menos 3 caracteres.")
    if not email or not email.strip():
        raise UserServiceError("El correo es obligatorio.")
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email.strip()):
        raise UserServiceError("El correo no tiene un formato válido.")
    if password and len(password) < 4:
        raise UserServiceError("La contraseña debe tener al menos 4 caracteres.")
    if rol and rol not in User.ROLES:
        raise UserServiceError(f"Rol inválido. Opciones: {', '.join(User.ROLES)}")
