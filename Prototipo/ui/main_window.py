"""
ui/main_window.py
Ventana principal — CRUD de usuarios, pantalla completa.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from models.user import User
from ui.styles import C, F, make_btn
from services.user_service import (
    crear_usuario, actualizar_usuario, eliminar_usuario,
    buscar_usuarios, UserServiceError
)


# ══════════════════════════════════════════════════════════════
class MainWindow(tk.Toplevel):

    def __init__(self, login_win: tk.Tk, usuario_actual: User):
        super().__init__()
        self.login_win      = login_win
        self.usuario_actual = usuario_actual
        self.id_seleccionado: int | None = None

        self.title("PetCare Bolivia — Gestión de Usuarios")
        self.configure(bg=C["bg"])
        self.state("zoomed")            # pantalla completa Windows
        self.protocol("WM_DELETE_WINDOW", self._salir)

        self._construir_ui()
        self._refrescar_tabla()
        self._set_status(
            f"Sesión iniciada correctamente. Bienvenido/a, {usuario_actual.nombre_corto()}.",
            "success"
        )

    # ══════════════════════════════════════════════════════════
    #  UI PRINCIPAL
    # ══════════════════════════════════════════════════════════
    def _construir_ui(self) -> None:
        self._navbar()
        self._body()
        self._status_bar()

    # ── Navbar ───────────────────────────────────────────────
    def _navbar(self) -> None:
        nav = tk.Frame(self, bg=C["dark"], pady=12, padx=20)
        nav.pack(fill="x")

        # Logo
        logo = tk.Frame(nav, bg=C["dark"])
        logo.pack(side="left")
        tk.Label(logo, text="🐾", font=("Segoe UI Emoji", 20),
                 bg=C["dark"], fg=C["cream"]).pack(side="left")
        tk.Label(logo, text="  PetCare Bolivia",
                 font=F["nav"], bg=C["dark"], fg=C["cream"]).pack(side="left")
        tk.Label(logo, text="  ·  Gestión de Usuarios",
                 font=F["small"], bg=C["dark"], fg=C["gold"]).pack(side="left")

        # Usuario actual
        right = tk.Frame(nav, bg=C["dark"])
        right.pack(side="right")

        rol_col = {"admin": C["gold"], "cuidador": "#6ee7b7", "dueño": C["sand"]}
        tk.Label(right,
                 text=f"👤  {self.usuario_actual.nombre}  |  {self.usuario_actual.rol.upper()}",
                 font=F["small"],
                 bg=C["dark"],
                 fg=rol_col.get(self.usuario_actual.rol, C["sand"])).pack(side="left", padx=(0, 16))

        make_btn(right, "  Cerrar sesión  ",
                 C["danger"], self._salir,
                 font=F["btn_sm"], pady=6, padx=12).pack(side="left")

    # ── Body ─────────────────────────────────────────────────
    def _body(self) -> None:
        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True, padx=20, pady=16)

        # Panel izquierdo — formulario
        izq = tk.Frame(body, bg=C["card"],
                       highlightbackground=C["sand"],
                       highlightthickness=1)
        izq.pack(side="left", fill="y", padx=(0, 16))
        izq.pack_propagate(False)
        izq.config(width=340)
        self._form_panel(izq)

        # Panel derecho — tabla
        der = tk.Frame(body, bg=C["bg"])
        der.pack(side="left", fill="both", expand=True)
        self._tabla_panel(der)

    # ══════════════════════════════════════════════════════════
    #  PANEL FORMULARIO
    # ══════════════════════════════════════════════════════════
    def _form_panel(self, parent: tk.Frame) -> None:

        # Título
        header = tk.Frame(parent, bg=C["dark"], pady=14, padx=18)
        header.pack(fill="x")
        tk.Label(header, text="Datos del Usuario",
                 font=F["subtitle"], bg=C["dark"], fg=C["cream"]).pack(anchor="w")
        tk.Label(header, text="Completa el formulario para crear o editar",
                 font=F["tiny"], bg=C["dark"], fg=C["gold"]).pack(anchor="w", pady=(2, 0))

        # Scroll interior
        canvas = tk.Canvas(parent, bg=C["card"], highlightthickness=0)
        sb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=C["card"])
        canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        campos = tk.Frame(inner, bg=C["card"], padx=18, pady=12)
        campos.pack(fill="x")

        # ── Campos ───────────────────────────────────────────
        def entry_field(label, attr, show=""):
            tk.Label(campos, text=label, font=F["label"],
                     bg=C["card"], fg=C["mid"]).pack(anchor="w", pady=(10, 2))
            e = tk.Entry(campos, font=F["normal"],
                         bg=C["bg"], fg=C["dark"],
                         relief="flat", bd=0,
                         highlightthickness=2,
                         highlightbackground=C["sand"],
                         highlightcolor=C["terracota"],
                         insertbackground=C["dark"],
                         show=show)
            e.pack(fill="x", ipady=8)
            setattr(self, attr, e)

        entry_field("NOMBRE COMPLETO *",    "e_nombre")
        entry_field("CORREO ELECTRÓNICO *", "e_email")
        entry_field("TELÉFONO",             "e_telefono")
        entry_field("CIUDAD",               "e_ciudad")
        entry_field("CONTRASEÑA *",         "e_password", show="•")

        # Mostrar contraseña
        self._show_pw = tk.BooleanVar()
        tk.Checkbutton(campos, text="Mostrar contraseña",
                       variable=self._show_pw, font=F["small"],
                       bg=C["card"], fg=C["light"],
                       activebackground=C["card"],
                       command=lambda: self.e_password.config(
                           show="" if self._show_pw.get() else "•"
                       )).pack(anchor="w", pady=(4, 0))

        # Rol
        tk.Label(campos, text="ROL *", font=F["label"],
                 bg=C["card"], fg=C["mid"]).pack(anchor="w", pady=(12, 4))

        self.rol_var = tk.StringVar(value="dueño")
        rol_frame = tk.Frame(campos, bg=C["card"])
        rol_frame.pack(fill="x")
        rol_colores = {"dueño": C["warn_fg"], "cuidador": C["forest"], "admin": "#534ab7"}
        for rol in User.ROLES:
            tk.Radiobutton(
                rol_frame, text=f"  {rol.capitalize()}",
                variable=self.rol_var, value=rol,
                font=F["normal"], bg=C["card"],
                fg=rol_colores[rol],
                activebackground=C["card"],
                selectcolor=C["bg2"],
            ).pack(side="left", padx=(0, 10))

        # Activo (solo en edición)
        self.activo_var = tk.BooleanVar(value=True)
        self.chk_activo = tk.Checkbutton(
            campos, text="  Usuario activo",
            variable=self.activo_var,
            font=F["normal"], bg=C["card"], fg=C["forest"],
            activebackground=C["card"],
            selectcolor=C["bg2"],
        )

        # ── Separador ─────────────────────────────────────────
        tk.Frame(inner, height=1, bg=C["sand"]).pack(fill="x", padx=18, pady=8)

        # ── Botones ───────────────────────────────────────────
        btn_area = tk.Frame(inner, bg=C["card"], padx=18, pady=8)
        btn_area.pack(fill="x")

        fila1 = tk.Frame(btn_area, bg=C["card"])
        fila1.pack(fill="x", pady=(0, 6))
        self.btn_guardar = make_btn(fila1, "💾  Guardar",
                                    C["terracota"], self._guardar, pady=10)
        self.btn_guardar.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.btn_actualizar = make_btn(fila1, "✏️  Actualizar",
                                       C["forest"], self._actualizar, pady=10)
        self.btn_actualizar.pack(side="left", fill="x", expand=True, padx=(4, 0))
        self.btn_actualizar.config(state="disabled")

        fila2 = tk.Frame(btn_area, bg=C["card"])
        fila2.pack(fill="x")
        self.btn_eliminar = make_btn(fila2, "🗑  Eliminar",
                                     C["danger"], self._eliminar, pady=10)
        self.btn_eliminar.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.btn_eliminar.config(state="disabled")

        make_btn(fila2, "✕  Limpiar",
                 C["light"], self._limpiar, pady=10).pack(
                     side="left", fill="x", expand=True, padx=(4, 0))

        # Nota al pie del formulario
        tk.Label(inner, text="* Campos obligatorios",
                 font=F["tiny"], bg=C["card"],
                 fg=C["light"]).pack(anchor="w", padx=18, pady=(0, 12))

    # ══════════════════════════════════════════════════════════
    #  PANEL TABLA
    # ══════════════════════════════════════════════════════════
    def _tabla_panel(self, parent: tk.Frame) -> None:

        # ── Cabecera ──────────────────────────────────────────
        top = tk.Frame(parent, bg=C["bg"])
        top.pack(fill="x", pady=(0, 10))

        tk.Label(top, text="Lista de Usuarios",
                 font=F["subtitle"], bg=C["bg"], fg=C["dark"]).pack(side="left")

        # Buscador
        busq = tk.Frame(top, bg=C["bg"])
        busq.pack(side="right")

        tk.Label(busq, text="🔍", font=("Segoe UI Emoji", 13),
                 bg=C["bg"], fg=C["mid"]).pack(side="left", padx=(0, 4))

        self.e_buscar = tk.Entry(busq, font=F["normal"],
                                 bg=C["card"], fg=C["dark"],
                                 relief="flat", bd=0,
                                 highlightthickness=2,
                                 highlightbackground=C["sand"],
                                 highlightcolor=C["terracota"],
                                 insertbackground=C["dark"],
                                 width=26)
        self.e_buscar.pack(side="left", ipady=7, padx=(0, 6))
        self.e_buscar.bind("<KeyRelease>", lambda e: self._buscar())

        make_btn(busq, "Buscar", C["terracota"],
                 self._buscar, font=F["btn_sm"], pady=7, padx=14).pack(side="left", padx=(0, 4))
        make_btn(busq, "Ver todos", C["sky"],
                 self._ver_todos, font=F["btn_sm"], pady=7, padx=14).pack(side="left")

        # ── Leyenda de roles ──────────────────────────────────
        ley = tk.Frame(parent, bg=C["bg"])
        ley.pack(fill="x", pady=(0, 8))
        for txt, bg, fg in [
            ("  Admin  ",    C["row_admin"], "#26215c"),
            ("  Cuidador  ", C["row_cuid"],  "#085041"),
            ("  Dueño  ",    C["row_dueno"], C["mid"]),
            ("  Inactivo  ", C["row_inact"], C["error_fg"]),
        ]:
            tk.Label(ley, text=txt, font=F["tiny"],
                     bg=bg, fg=fg, relief="flat",
                     padx=4, pady=2).pack(side="left", padx=(0, 6))

        # ── Treeview ──────────────────────────────────────────
        tree_frame = tk.Frame(parent, bg=C["bg"])
        tree_frame.pack(fill="both", expand=True)

        cols = ("id", "nombre", "email", "telefono", "ciudad", "rol", "activo", "registro")
        self.tree = ttk.Treeview(tree_frame, columns=cols,
                                 show="headings", selectmode="browse")

        headers = {
            "id":       ("ID",         55,  "center"),
            "nombre":   ("Nombre",     200, "w"),
            "email":    ("Email",      240, "w"),
            "telefono": ("Teléfono",   110, "center"),
            "ciudad":   ("Ciudad",     110, "center"),
            "rol":      ("Rol",        90,  "center"),
            "activo":   ("Activo",     60,  "center"),
            "registro": ("Registro",   100, "center"),
        }
        for col, (head, w, anc) in headers.items():
            self.tree.heading(col, text=head,
                              command=lambda c=col: self._ordenar(c))
            self.tree.column(col, width=w, anchor=anc, minwidth=40)

        sb_v = ttk.Scrollbar(tree_frame, orient="vertical",   command=self.tree.yview)
        sb_h = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=sb_v.set, xscrollcommand=sb_h.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        sb_v.grid(row=0, column=1, sticky="ns")
        sb_h.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Tags de color
        self.tree.tag_configure("admin",    background=C["row_admin"], foreground="#26215c")
        self.tree.tag_configure("cuidador", background=C["row_cuid"],  foreground="#085041")
        self.tree.tag_configure("dueno",    background=C["row_dueno"], foreground=C["mid"])
        self.tree.tag_configure("inactivo", background=C["row_inact"], foreground=C["error_fg"])

        self.tree.bind("<<TreeviewSelect>>", self._seleccionar)

        # ── Contador ──────────────────────────────────────────
        self.lbl_contador = tk.Label(parent, text="",
                                     font=F["counter"],
                                     bg=C["bg"], fg=C["light"], anchor="e")
        self.lbl_contador.pack(fill="x", pady=(6, 0))

    # ── Barra de estado ───────────────────────────────────────
    def _status_bar(self) -> None:
        self.status_bar = tk.Label(
            self, text="", font=F["status"],
            anchor="w", padx=16, pady=6,
            bg=C["sand"], fg=C["mid"]
        )
        self.status_bar.pack(fill="x", side="bottom")

    # ══════════════════════════════════════════════════════════
    #  LÓGICA TABLA
    # ══════════════════════════════════════════════════════════
    def _refrescar_tabla(self, filtro: str = "") -> None:
        for row in self.tree.get_children():
            self.tree.delete(row)

        usuarios = buscar_usuarios(filtro)
        for u in usuarios:
            tag = ("inactivo" if not u.activo
                   else u.rol.replace("ñ", "n").replace("dueño", "dueno"))
            self.tree.insert("", "end", iid=str(u.id),
                             values=(
                                 u.id, u.nombre, u.email,
                                 u.telefono or "—", u.ciudad or "—",
                                 u.rol,
                                 "✅" if u.activo else "❌",
                                 u.fecha_registro,
                             ),
                             tags=(tag,))
        n = len(usuarios)
        self.lbl_contador.config(
            text=f"  {n} usuario{'s' if n != 1 else ''} encontrado{'s' if n != 1 else ''}"
        )

    def _seleccionar(self, event=None) -> None:
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        self.id_seleccionado = int(vals[0])

        self._limpiar_campos()
        self.e_nombre.insert(0,   vals[1])
        self.e_email.insert(0,    vals[2])
        self.e_telefono.insert(0, vals[3] if vals[3] != "—" else "")
        self.e_ciudad.insert(0,   vals[4] if vals[4] != "—" else "")
        self.rol_var.set(vals[5])
        self.activo_var.set(vals[6] == "✅")
        self.chk_activo.pack(anchor="w", pady=(10, 0))

        self.btn_guardar.config(state="disabled")
        self.btn_actualizar.config(state="normal")
        self.btn_eliminar.config(state="normal")
        self._set_status(f"Editando: {vals[1]}", "info")

    def _ordenar(self, col: str) -> None:
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        rev = getattr(self, f"_ord_{col}", False)
        items.sort(key=lambda x: x[0].lower(), reverse=rev)
        for i, (_, k) in enumerate(items):
            self.tree.move(k, "", i)
        setattr(self, f"_ord_{col}", not rev)

    def _buscar(self) -> None:
        self._refrescar_tabla(self.e_buscar.get())

    def _ver_todos(self) -> None:
        self.e_buscar.delete(0, "end")
        self._refrescar_tabla()

    # ══════════════════════════════════════════════════════════
    #  CRUD
    # ══════════════════════════════════════════════════════════
    def _guardar(self) -> None:
        try:
            u = crear_usuario(
                self.e_nombre.get(),
                self.e_email.get(),
                self.e_telefono.get(),
                self.e_ciudad.get(),
                self.e_password.get(),
                self.rol_var.get(),
            )
            self._limpiar()
            self._refrescar_tabla()
            self._set_status(f"✅  Usuario '{u.nombre}' creado correctamente.", "success")
        except UserServiceError as e:
            self._set_status(f"⚠  {e}", "error")
            messagebox.showwarning("Validación", str(e), parent=self)

    def _actualizar(self) -> None:
        if not self.id_seleccionado:
            return
        try:
            u = actualizar_usuario(
                uid              = self.id_seleccionado,
                nombre           = self.e_nombre.get(),
                email            = self.e_email.get(),
                telefono         = self.e_telefono.get(),
                ciudad           = self.e_ciudad.get(),
                rol              = self.rol_var.get(),
                activo           = self.activo_var.get(),
                nueva_password   = self.e_password.get(),
                usuario_actual_id= self.usuario_actual.id,
            )
            self._limpiar()
            self._refrescar_tabla()
            self._set_status(f"✅  Usuario '{u.nombre}' actualizado.", "success")
        except UserServiceError as e:
            self._set_status(f"⚠  {e}", "error")
            messagebox.showwarning("Validación", str(e), parent=self)

    def _eliminar(self) -> None:
        if not self.id_seleccionado:
            return
        nombre = self.e_nombre.get().strip()
        if not messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Eliminar al usuario '{nombre}'?\nEsta acción no se puede deshacer.",
            parent=self
        ):
            return
        try:
            eliminar_usuario(self.id_seleccionado, self.usuario_actual.id)
            self._limpiar()
            self._refrescar_tabla()
            self._set_status(f"🗑  Usuario '{nombre}' eliminado.", "warn")
        except UserServiceError as e:
            self._set_status(f"⚠  {e}", "error")
            messagebox.showwarning("Error", str(e), parent=self)

    def _limpiar(self) -> None:
        self.id_seleccionado = None
        self._limpiar_campos()
        self.chk_activo.pack_forget()
        self.btn_guardar.config(state="normal")
        self.btn_actualizar.config(state="disabled")
        self.btn_eliminar.config(state="disabled")
        self.tree.selection_remove(self.tree.selection())
        self._set_status("Formulario limpio. Listo para crear un nuevo usuario.", "info")

    def _limpiar_campos(self) -> None:
        for e in (self.e_nombre, self.e_email,
                  self.e_telefono, self.e_ciudad, self.e_password):
            e.delete(0, "end")
        self.rol_var.set("dueño")
        self.activo_var.set(True)

    # ── Status bar ────────────────────────────────────────────
    def _set_status(self, msg: str, tipo: str = "info") -> None:
        colores = {
            "success": (C["success_bg"], C["success_fg"]),
            "warn":    (C["warn_bg"],    C["warn_fg"]),
            "info":    (C["info_bg"],    C["info_fg"]),
            "error":   (C["error_bg"],   C["error_fg"]),
        }
        bg, fg = colores.get(tipo, colores["info"])
        self.status_bar.config(text=f"   {msg}", bg=bg, fg=fg)

    # ── Cerrar ────────────────────────────────────────────────
    def _salir(self) -> None:
        if messagebox.askyesno("Cerrar sesión",
                               "¿Deseas cerrar sesión y salir?",
                               parent=self):
            self.destroy()
            self.login_win.deiconify()
