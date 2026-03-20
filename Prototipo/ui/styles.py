"""
ui/styles.py
Constantes de colores, fuentes y estilos visuales.
"""
from tkinter import ttk

# ── Paleta de colores ────────────────────────────────────────
C = {
    "bg":          "#fdf8f3",
    "bg2":         "#f5ede0",
    "dark":        "#1e1612",
    "dark2":       "#2d2018",
    "terracota":   "#c4704a",
    "rust":        "#a0522d",
    "forest":      "#3d6b4f",
    "leaf":        "#5a8c69",
    "sky":         "#4a7fa5",
    "gold":        "#d4a843",
    "gold2":       "#f0c060",
    "danger":      "#ef4444",
    "danger2":     "#dc2626",
    "card":        "#ffffff",
    "sand":        "#e8d5be",
    "sand2":       "#d4bfa0",
    "mid":         "#5c4a3a",
    "light":       "#9b8576",
    "cream":       "#fdf8f3",
    "success_bg":  "#ecfdf5",
    "success_fg":  "#065f46",
    "error_bg":    "#fef2f2",
    "error_fg":    "#991b1b",
    "warn_bg":     "#fffbeb",
    "warn_fg":     "#92400e",
    "info_bg":     "#eff6ff",
    "info_fg":     "#1e40af",
    "row_admin":   "#eeedfe",
    "row_cuid":    "#e1f5ee",
    "row_dueno":   "#fdf8f3",
    "row_inact":   "#fef2f2",
    "row_sel":     "#fdf4e7",
    "row_hover":   "#fafaf9",
}

# ── Fuentes ──────────────────────────────────────────────────
F = {
    "title":    ("Georgia",   20, "bold"),
    "subtitle": ("Georgia",   14, "bold"),
    "section":  ("Segoe UI",  11, "bold"),
    "label":    ("Segoe UI",   9, "bold"),
    "normal":   ("Segoe UI",  11),
    "small":    ("Segoe UI",   9),
    "tiny":     ("Segoe UI",   8),
    "btn":      ("Segoe UI",  10, "bold"),
    "btn_sm":   ("Segoe UI",   9, "bold"),
    "mono":     ("Consolas",   9),
    "table":    ("Segoe UI",  10),
    "table_h":  ("Segoe UI",  10, "bold"),
    "nav":      ("Georgia",   13, "bold"),
    "counter":  ("Segoe UI",   9),
    "status":   ("Segoe UI",  10),
}

# ── Configurar ttk styles ────────────────────────────────────
def aplicar_estilos() -> None:
    style = ttk.Style()
    style.theme_use("clam")

    # Entry
    style.configure("TEntry",
        padding=(8, 6),
        relief="flat",
        borderwidth=1,
        fieldbackground=C["card"],
        foreground=C["dark"],
        font=F["normal"],
    )
    style.map("TEntry",
        bordercolor=[("focus", C["terracota"]), ("!focus", C["sand"])],
        lightcolor=[("focus", C["terracota"])],
    )

    # Combobox
    style.configure("TCombobox",
        padding=(8, 6),
        fieldbackground=C["card"],
        foreground=C["dark"],
        font=F["normal"],
    )

    # Scrollbar
    style.configure("TScrollbar",
        background=C["sand"],
        troughcolor=C["bg2"],
        borderwidth=0,
        arrowsize=14,
    )

    # Treeview
    style.configure("Treeview",
        background=C["card"],
        fieldbackground=C["card"],
        foreground=C["dark"],
        rowheight=36,
        font=F["table"],
        borderwidth=0,
    )
    style.configure("Treeview.Heading",
        background=C["dark"],
        foreground=C["cream"],
        font=F["table_h"],
        relief="flat",
        padding=(8, 10),
    )
    style.map("Treeview",
        background=[("selected", C["row_sel"])],
        foreground=[("selected", C["dark"])],
    )
    style.map("Treeview.Heading",
        background=[("active", C["dark2"])],
    )

    # Separador
    style.configure("TSeparator", background=C["sand"])


# ── Helper: botón con estilo personalizado ───────────────────
def make_btn(parent, text, color, command,
             font=None, pady=10, padx=16, width=None):
    import tkinter as tk
    hover_color = {
        C["terracota"]: C["rust"],
        C["forest"]:    C["leaf"],
        C["danger"]:    C["danger2"],
        C["light"]:     C["sand2"],
        C["sky"]:       "#3a6a8a",
    }.get(color, color)

    btn = tk.Button(
        parent,
        text=text,
        font=font or F["btn"],
        bg=color,
        fg="white",
        relief="flat",
        activebackground=hover_color,
        activeforeground="white",
        cursor="hand2",
        pady=pady,
        padx=padx,
        width=width,
        command=command,
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=hover_color))
    btn.bind("<Leave>", lambda e: btn.config(bg=color))
    return btn
