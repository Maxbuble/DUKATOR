"""
DUKATOR - Archivador de Música Underground
Tema visual: Underground (Morado/Negro)
"""

import customtkinter as ctk

# Configuración de tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Paleta de colores Underground
COLORS = {
    "bg_primary": "#0a0a0f",        # Negro casi puro
    "bg_secondary": "#151520",      # Negro azulado
    "bg_tertiary": "#1e1e2e",       # Gris oscuro
    "accent_primary": "#8b5cf6",    # Violeta eléctrico
    "accent_secondary": "#a78bfa",  # Violeta claro
    "accent_hover": "#7c3aed",      # Violeta hover
    "success": "#10b981",           # Verde éxito
    "warning": "#f59e0b",           # Naranja advertencia
    "error": "#ef4444",             # Rojo error
    "text_primary": "#f8fafc",      # Blanco
    "text_secondary": "#94a3b8",    # Gris claro
    "text_muted": "#64748b",        # Gris medio
    "border": "#2d2d3d"             # Borde sutil
}

# Configuración de fuentes
FONTS = {
    "title": ("Segoe UI", 24, "bold"),
    "subtitle": ("Segoe UI", 16, "bold"),
    "heading": ("Segoe UI", 14, "bold"),
    "body": ("Segoe UI", 12),
    "body_small": ("Segoe UI", 10),
    "mono": ("Consolas", 10)
}