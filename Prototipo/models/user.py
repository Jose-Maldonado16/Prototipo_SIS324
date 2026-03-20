"""
models/user.py
Modelo de datos — representa un Usuario del sistema.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class User:
    nombre:        str
    email:         str
    password_hash: str
    rol:           str         = "dueño"   # dueño | cuidador | admin
    telefono:      str         = ""
    ciudad:        str         = ""
    activo:        bool        = True
    fecha_registro: str        = ""
    id:            Optional[int] = None

    # Roles válidos
    ROLES = ("dueño", "cuidador", "admin")

    def nombre_corto(self) -> str:
        """Primer nombre solamente."""
        return self.nombre.strip().split()[0]

    def esta_activo(self) -> bool:
        return bool(self.activo)

    def __str__(self) -> str:
        return f"User(id={self.id}, nombre={self.nombre}, rol={self.rol})"
