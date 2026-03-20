"""
ui/login_window.py
Ventana de inicio de sesión.
"""
import tkinter as tk
from tkinter import messagebox
from ui.styles import C, F, make_btn
from services.user_service import login, UserServiceError


class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PetCare Bolivia — Iniciar Sesión")
        self.resizable(False, False)
        self.configure(bg=C["dark"])
        self._usuario_logueado = None
        self._centrar(440, 640)
        self._construir()

    def _centrar(self, w: int, h: int) -> None:
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def get_usuario(self):
        return self._usuario_logueado

    # ── Construcción UI ──────────────────────────────────────
    def _construir(self) -> None:
        # Cabecera oscura
        header = tk.Frame(self, bg=C["dark"], pady=16)
        header.pack(fill="x")

        tk.Label(header, text="🐾",
                 font=("Segoe UI Emoji", 32),
                 bg=C["dark"], fg=C["cream"]).pack()

        tk.Label(header, text="PetCare Bolivia",
                 font=F["title"],
                 bg=C["dark"], fg=C["cream"]).pack(pady=(6, 2))

        tk.Label(header, text="Sistema de Gestión de Usuarios",
                 font=F["small"],
                 bg=C["dark"], fg=C["gold"]).pack()

        # Card formulario
        card = tk.Frame(self, bg=C["card"], padx=36, pady=16)
        card.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        tk.Label(card, text="Iniciar Sesión",
                 font=F["subtitle"],
                 bg=C["card"], fg=C["dark"]).pack(anchor="w", pady=(0, 10))

        # Email
        tk.Label(card, text="CORREO ELECTRÓNICO",
                 font=F["label"], bg=C["card"], fg=C["mid"]).pack(anchor="w")
        self.e_email = tk.Entry(card, font=F["normal"],
                                bg=C["bg"], fg=C["dark"],
                                relief="flat", bd=1,
                                highlightthickness=2,
                                highlightbackground=C["sand"],
                                highlightcolor=C["terracota"],
                                insertbackground=C["dark"])
        self.e_email.pack(fill="x", ipady=8, pady=(4, 14))
        self.e_email.insert(0, "admin@petcare.bo")

        # Contraseña
        tk.Label(card, text="CONTRASEÑA",
                 font=F["label"], bg=C["card"], fg=C["mid"]).pack(anchor="w")
        self.e_pass = tk.Entry(card, font=F["normal"],
                               bg=C["bg"], fg=C["dark"],
                               relief="flat", bd=1,
                               highlightthickness=2,
                               highlightbackground=C["sand"],
                               highlightcolor=C["terracota"],
                               insertbackground=C["dark"],
                               show="•")
        self.e_pass.pack(fill="x", ipady=8, pady=(4, 6))
        self.e_pass.insert(0, "admin123")

        # Mostrar contraseña
        self._show_pass = tk.BooleanVar()
        tk.Checkbutton(card, text="Mostrar contraseña",
                       variable=self._show_pass,
                       font=F["small"], bg=C["card"], fg=C["light"],
                       activebackground=C["card"],
                       command=self._toggle_pass).pack(anchor="w", pady=(0, 10))

        # Mensaje error
        self.lbl_error = tk.Label(card, text="", font=F["small"],
                                  bg=C["error_bg"], fg=C["error_fg"],
                                  wraplength=320, justify="left",
                                  padx=10, pady=8)

        # Botón
        btn = make_btn(card, "  Iniciar Sesión  →",
                       C["terracota"], self._login, pady=12)
        btn.pack(fill="x", pady=(0, 16))

        # Separador
        tk.Frame(card, height=1, bg=C["sand"]).pack(fill="x", pady=8)

        # Cuentas demo
        demo = ("Cuentas de prueba:\n"
                "admin@petcare.bo    /  admin123  (admin)\n"
                "maria@example.com   /  1234      (dueño)\n"
                "ana@example.com     /  1234      (cuidador)")
        tk.Label(card, text=demo, font=F["mono"],
                 bg=C["warn_bg"], fg=C["warn_fg"],
                 justify="left", padx=10, pady=8,
                 relief="flat").pack(fill="x")

        # Pie
        tk.Label(self,
                 text="USFX · SIS324 Ingeniería de Software · Grupo 16-Python · 2026",
                 font=F["tiny"], bg=C["dark"], fg=C["light"]).pack(pady=(0, 8))

        self.bind("<Return>", lambda e: self._login())
        self.e_email.focus()

    def _toggle_pass(self) -> None:
        self.e_pass.config(show="" if self._show_pass.get() else "•")

    def _login(self) -> None:
        email    = self.e_email.get().strip()
        password = self.e_pass.get().strip()
        try:
            usuario = login(email, password)
            self._usuario_logueado = usuario
            self.withdraw()
            # Importación tardía para evitar ciclos
            from ui.main_window import MainWindow
            MainWindow(self, usuario)
        except UserServiceError as e:
            self.lbl_error.config(text=f"⚠  {e}")
            self.lbl_error.pack(fill="x", pady=(0, 12))
            self.e_pass.focus()
