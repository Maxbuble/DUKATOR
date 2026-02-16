"""
Ventana principal de DUKATOR
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import sys
from pathlib import Path

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import COLORS, FONTS
from utils.ffmpeg_manager import FFmpegManager
from gui.album_search_tab import AlbumSearchTab
from gui.bulk_download_tab import BulkDownloadTab
from gui.track_search_tab import TrackSearchTab

class DukatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuración ventana
        self.title("DUKATOR - Archivador Underground")
        self.geometry("1200x800")
        self.minsize(1000, 600)
        
        # Centrar ventana
        self.center_window()
        
        # Variables
        self.ffmpeg_manager = FFmpegManager()
        self.download_path = Path.home() / "Music" / "DUKATOR"
        self.download_path.mkdir(parents=True, exist_ok=True)
        
        # Configurar grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Crear UI
        self.create_header()
        self.create_tabs()
        self.create_footer()
        
        # Verificar FFmpeg al inicio
        self.after(1000, self.check_ffmpeg)
    
    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.update_idletasks()
        width = 1200
        height = 800
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_header(self):
        """Crea la cabecera con logo"""
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"], height=70)
        header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header.grid_propagate(False)
        
        # Logo
        logo = ctk.CTkLabel(
            header,
            text="⚡ DUKATOR",
            font=FONTS["title"],
            text_color=COLORS["accent_primary"]
        )
        logo.pack(side="left", padx=20, pady=10)
        
        # Subtítulo
        subtitle = ctk.CTkLabel(
            header,
            text="Archivador de Música Underground",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"]
        )
        subtitle.pack(side="left", padx=10, pady=10)
        
        # Botón configuración
        settings_btn = ctk.CTkButton(
            header,
            text="⚙️ Config",
            font=FONTS["body_small"],
            fg_color=COLORS["bg_tertiary"],
            hover_color=COLORS["accent_hover"],
            width=100,
            command=self.open_settings
        )
        settings_btn.pack(side="right", padx=20, pady=15)
    
    def create_tabs(self):
        """Crea las pestañas principales"""
        self.tabview = ctk.CTkTabview(
            self,
            fg_color=COLORS["bg_primary"],
            segmented_button_fg_color=COLORS["bg_secondary"],
            segmented_button_selected_color=COLORS["accent_primary"],
            segmented_button_selected_hover_color=COLORS["accent_hover"],
            segmented_button_unselected_color=COLORS["bg_tertiary"],
            segmented_button_unselected_hover_color=COLORS["bg_secondary"]
        )
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        # Pestaña 1: Buscador de Canciones Sueltas
        self.tab_tracks = self.tabview.add("🎵 Canciones")
        self.tracks_tab = TrackSearchTab(self.tab_tracks, self.download_path, self.ffmpeg_manager)
        self.tracks_tab.pack(fill="both", expand=True)
        
        # Pestaña 2: Buscador de Álbumes
        self.tab_album = self.tabview.add("🔍 Álbumes")
        self.album_tab = AlbumSearchTab(self.tab_album, self.download_path, self.ffmpeg_manager)
        self.album_tab.pack(fill="both", expand=True)
        
        # Pestaña 3: Descarga Bulk
        self.tab_bulk = self.tabview.add("📥 Bulk URLs")
        self.bulk_tab = BulkDownloadTab(self.tab_bulk, self.download_path, self.ffmpeg_manager)
        self.bulk_tab.pack(fill="both", expand=True)
        
        # Pestaña 4: Soulseek (P2P)
        self.tab_soulseek = self.tabview.add("🌐 Soulseek")
        self.create_soulseek_tab()
    
    def create_soulseek_tab(self):
        """Crea pestaña de Soulseek"""
        frame = ctk.CTkFrame(self.tab_soulseek, fg_color=COLORS["bg_secondary"])
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        title = ctk.CTkLabel(
            frame,
            text="🌐 Soulseek P2P",
            font=FONTS["subtitle"],
            text_color=COLORS["accent_primary"]
        )
        title.pack(pady=20)
        
        # Descripción
        desc = ctk.CTkLabel(
            frame,
            text="Búsqueda en red P2P Soulseek para rarezas underground\n\n"
                 "Esta función conecta con la red Soulseek para encontrar\n"
                 "materiales que no están en otras fuentes.",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"],
            justify="center"
        )
        desc.pack(pady=10)
        
        # Botón conectar
        self.slsk_btn = ctk.CTkButton(
            frame,
            text="Conectar a Soulseek",
            font=FONTS["heading"],
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_hover"],
            height=40,
            command=self.connect_soulseek
        )
        self.slsk_btn.pack(pady=20)
        
        # Estado
        self.slsk_status = ctk.CTkLabel(
            frame,
            text="Desconectado",
            font=FONTS["body_small"],
            text_color=COLORS["text_muted"]
        )
        self.slsk_status.pack()
    
    def create_footer(self):
        """Crea el pie de página"""
        footer = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"], height=40)
        footer.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        footer.grid_propagate(False)
        
        # Ruta de descarga
        path_label = ctk.CTkLabel(
            footer,
            text=f"📁 {self.download_path}",
            font=FONTS["body_small"],
            text_color=COLORS["text_muted"]
        )
        path_label.pack(side="left", padx=20, pady=10)
        
        # Botón cambiar ruta
        change_btn = ctk.CTkButton(
            footer,
            text="Cambiar",
            font=FONTS["body_small"],
            fg_color=COLORS["bg_tertiary"],
            hover_color=COLORS["accent_hover"],
            width=80,
            command=self.change_download_path
        )
        change_btn.pack(side="left", padx=5, pady=8)
        
        # Status FFmpeg
        self.ffmpeg_label = ctk.CTkLabel(
            footer,
            text="⏳ FFmpeg: Verificando...",
            font=FONTS["body_small"],
            text_color=COLORS["warning"]
        )
        self.ffmpeg_label.pack(side="right", padx=20, pady=10)
    
    def check_ffmpeg(self):
        """Verifica e instala FFmpeg si es necesario"""
        if self.ffmpeg_manager.is_installed():
            self.ffmpeg_label.configure(
                text="✅ FFmpeg: Listo",
                text_color=COLORS["success"]
            )
        else:
            self.ffmpeg_label.configure(
                text="⬇️ FFmpeg: Descargando...",
                text_color=COLORS["warning"]
            )
            # Descargar en background
            self.after(100, self.download_ffmpeg)
    
    def download_ffmpeg(self):
        """Descarga FFmpeg"""
        def progress(percent, msg):
            self.ffmpeg_label.configure(text=f"⬇️ FFmpeg: {msg}")
            self.update()
        
        if self.ffmpeg_manager.ensure_ffmpeg(progress):
            self.ffmpeg_label.configure(
                text="✅ FFmpeg: Listo",
                text_color=COLORS["success"]
            )
        else:
            self.ffmpeg_label.configure(
                text="❌ FFmpeg: Error",
                text_color=COLORS["error"]
            )
            messagebox.showerror(
                "Error",
                "No se pudo descargar FFmpeg. La aplicación puede no funcionar correctamente."
            )
    
    def change_download_path(self):
        """Cambia la ruta de descarga"""
        new_path = filedialog.askdirectory(initialdir=str(self.download_path))
        if new_path:
            self.download_path = Path(new_path)
            self.tracks_tab.update_download_path(self.download_path)
            self.album_tab.update_download_path(self.download_path)
            self.bulk_tab.update_download_path(self.download_path)
            # Actualizar label del footer
            for widget in self.winfo_children():
                if isinstance(widget, ctk.CTkFrame):
                    for child in widget.winfo_children():
                        if isinstance(child, ctk.CTkLabel) and "📁" in child.cget("text"):
                            child.configure(text=f"📁 {self.download_path}")
    
    def connect_soulseek(self):
        """Conecta a Soulseek"""
        from core.soulseek_client import soulseek_client
        
        if soulseek_client.connect():
            self.slsk_status.configure(
                text="✅ Conectado",
                text_color=COLORS["success"]
            )
            self.slsk_btn.configure(
                text="Búsqueda P2P",
                command=self.open_soulseek_search
            )
    
    def open_soulseek_search(self):
        """Abre diálogo de búsqueda Soulseek"""
        # TODO: Implementar diálogo de búsqueda
        messagebox.showinfo("Soulseek", "Función en desarrollo")
    
    def open_settings(self):
        """Abre configuración"""
        # TODO: Implementar ventana de configuración
        messagebox.showinfo("Configuración", "Panel de configuración (en desarrollo)")

def main():
    app = DukatorApp()
    app.mainloop()

if __name__ == "__main__":
    main()