"""
main.py
Punto de entrada de la aplicación PetCare Bolivia.
Gestión de Usuarios — SIS324 Ingeniería de Software
Universidad San Francisco Xavier de Chuquisaca
Grupo 16-Python · 2026
"""
import sys
import os

# Asegura que Python encuentre los módulos desde cualquier carpeta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.connection import initialize
from ui.styles import aplicar_estilos
from ui.login_window import LoginWindow


def main() -> None:
    initialize()          # Crea tablas e inserta datos demo si es necesario
    app = LoginWindow()
    aplicar_estilos()     # Aplica estilos ttk globales
    app.mainloop()


if __name__ == "__main__":
    main()
