"""
Pestaña de descarga directa (bulk)
"""

import customtkinter as ctk
from tkinter import messagebox
import threading
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import COLORS, FONTS
from core.downloader import DownloadEngine
from core.metadata import metadata_manager

class BulkDownloadTab(ctk.CTkFrame):
    def __init__(self, parent, download_path, ffmpeg_manager):
        super().__init__(parent, fg_color=COLORS["bg_primary"])
        
        self.download_path = download_path
        self.ffmpeg_manager = ffmpeg_manager
        self.downloader = None
        
        self.create_ui()
    
    def create_ui(self):
        """Crea la interfaz de la pestaña"""
        # Panel superior: Instrucciones
        header_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"])
        header_frame.pack(fill="x", padx=10, pady=10)
        
        title = ctk.CTkLabel(
            header_frame,
            text="📥 Descarga Directa Bulk",
            font=FONTS["subtitle"],
            text_color=COLORS["accent_primary"]
        )
        title.pack(pady=10)
        
        desc = ctk.CTkLabel(
            header_frame,
            text="Pega URLs de YouTube, Bandcamp, SoundCloud, Archive.org, Mixcloud...\n"
                 "Una URL por línea. Se descargarán como MP3 320kbps",
            font=FONTS["body_small"],
            text_color=COLORS["text_secondary"],
            justify="center"
        )
        desc.pack(pady=5)
        
        # Área de texto para URLs
        self.urls_text = ctk.CTkTextbox(
            self,
            font=FONTS["mono"],
            fg_color=COLORS["bg_secondary"],
            text_color=COLORS["text_primary"],
            scrollbar_button_color=COLORS["accent_primary"],
            scrollbar_button_hover_color=COLORS["accent_hover"]
        )
        self.urls_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.urls_text.insert("1.0", "# Pega aquí tus URLs (una por línea)\n")
        
        # Panel de controles
        controls_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"])
        controls_frame.pack(fill="x", padx=10, pady=10)
        
        # Opciones
        options_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        options_frame.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        
        # Carpeta destino
        folder_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        folder_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(folder_frame, text="Carpeta:", font=FONTS["body_small"], text_color=COLORS["text_secondary"]).pack(side="left")
        self.folder_label = ctk.CTkLabel(
            folder_frame,
            text="DUKATOR/Bulk_YYYYMMDD",
            font=FONTS["body_small"],
            text_color=COLORS["text_primary"]
        )
        self.folder_label.pack(side="left", padx=10)
        
        self.bulk_path = self.download_path / f"Bulk_{datetime.now().strftime('%Y%m%d')}"
        
        # Estadísticas
        stats_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        stats_frame.pack(side="right", padx=10, pady=10)
        
        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text="0 URLs | 0 Descargadas | 0 Errores",
            font=FONTS["body_small"],
            text_color=COLORS["text_secondary"]
        )
        self.stats_label.pack()
        
        # Botones
        buttons_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_primary"])
        buttons_frame.pack(fill="x", padx=10, pady=5)
        
        self.clear_btn = ctk.CTkButton(
            buttons_frame,
            text="🗑️ Limpiar",
            font=FONTS["heading"],
            fg_color=COLORS["bg_tertiary"],
            hover_color=COLORS["accent_hover"],
            command=self.clear_urls
        )
        self.clear_btn.pack(side="left", padx=5)
        
        self.download_btn = ctk.CTkButton(
            buttons_frame,
            text="⬇️ DESCARGAR TODO",
            font=FONTS["heading"],
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_hover"],
            height=40,
            command=self.start_bulk_download
        )
        self.download_btn.pack(side="right", padx=5)
        
        # Barra de progreso
        self.progress_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"])
        self.progress_frame.pack(fill="x", padx=10, pady=10)
        
        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="Listo",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"]
        )
        self.progress_label.pack(side="left", padx=10, pady=10)
        
        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            width=500,
            progress_color=COLORS["accent_primary"]
        )
        self.progress_bar.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        self.progress_bar.set(0)
        
        # Log de resultados
        self.log_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"])
        self.log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(self.log_frame, text="📋 Registro de Descargas", font=FONTS["heading"], text_color=COLORS["accent_secondary"]).pack(pady=5)
        
        self.log_text = ctk.CTkTextbox(
            self.log_frame,
            font=FONTS["mono"],
            fg_color=COLORS["bg_tertiary"],
            text_color=COLORS["text_primary"],
            height=150,
            state="disabled"
        )
        self.log_text.pack(fill="both", expand=True, padx=10, pady=5)
    
    def clear_urls(self):
        """Limpia el área de URLs"""
        self.urls_text.delete("1.0", "end")
        self.log_message("Área de URLs limpiada")
    
    def log_message(self, message, tag="info"):
        """Añade mensaje al log"""
        self.log_text.configure(state="normal")
        
        color = COLORS["text_primary"]
        if tag == "success":
            color = COLORS["success"]
        elif tag == "error":
            color = COLORS["error"]
        elif tag == "warning":
            color = COLORS["warning"]
        
        self.log_text.insert("end", f"{message}\n")
        self.log_text.configure(state="disabled")
        self.log_text.see("end")
    
    def start_bulk_download(self):
        """Inicia la descarga bulk"""
        # Obtener URLs
        urls_text = self.urls_text.get("1.0", "end").strip()
        urls = [url.strip() for url in urls_text.split('\n') if url.strip() and not url.strip().startswith('#')]
        
        if not urls:
            messagebox.showwarning("Descarga", "No hay URLs válidas para descargar")
            return
        
        # Actualizar UI
        self.download_btn.configure(state="disabled", text="Descargando...")
        self.progress_bar.set(0)
        self.log_message(f"Iniciando descarga de {len(urls)} URLs...")
        
        # Actualizar ruta
        self.bulk_path = self.download_path / f"Bulk_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.bulk_path.mkdir(parents=True, exist_ok=True)
        self.folder_label.configure(text=str(self.bulk_path.name))
        
        # Descargar en thread
        def do_bulk_download():
            try:
                ffmpeg_path = self.ffmpeg_manager.get_ffmpeg_path()
                downloader = DownloadEngine(ffmpeg_path)
                
                total = len(urls)
                success_count = 0
                error_count = 0
                
                for i, url in enumerate(urls, 1):
                    progress = (i - 1) / total
                    self.after(0, lambda p=progress, u=url: self.update_progress(p, f"[{i}/{total}] {u[:50]}..."))
                    
                    def track_progress(percent, msg):
                        overall = progress + (percent / 100 / total)
                        self.after(0, lambda p=overall: self.progress_bar.set(p))
                    
                    result = downloader._download_from_url(url, self.bulk_path / f"track_{i}", None, track_progress)
                    
                    if result['success']:
                        success_count += 1
                        self.after(0, lambda u=url: self.log_message(f"✓ OK: {u[:60]}...", "success"))
                    else:
                        error_count += 1
                        self.after(0, lambda u=url, e=result['error']: self.log_message(f"✗ ERROR: {u[:40]}... - {e}", "error"))
                    
                    # Actualizar stats
                    self.after(0, lambda: self.stats_label.configure(
                        text=f"{total} URLs | {success_count} OK | {error_count} Errores"
                    ))
                
                self.after(0, lambda: self.bulk_complete(success_count, error_count))
                
            except Exception as e:
                self.after(0, lambda: self.bulk_error(str(e)))
        
        threading.Thread(target=do_bulk_download, daemon=True).start()
    
    def update_progress(self, value, message):
        """Actualiza la barra de progreso"""
        self.progress_bar.set(value)
        self.progress_label.configure(text=message)
    
    def bulk_complete(self, success, errors):
        """Callback cuando termina la descarga bulk"""
        self.download_btn.configure(state="normal", text="⬇️ DESCARGAR TODO")
        self.progress_bar.set(1)
        self.progress_label.configure(text="Completado")
        
        msg = f"Descarga completada!\n✓ Éxitos: {success}\n✗ Errores: {errors}\n\nGuardado en:\n{self.bulk_path}"
        messagebox.showinfo("Completado", msg)
    
    def bulk_error(self, error):
        """Callback de error"""
        self.download_btn.configure(state="normal", text="⬇️ DESCARGAR TODO")
        messagebox.showerror("Error", f"Error en descarga bulk:\n{error}")
    
    def update_download_path(self, new_path):
        """Actualiza la ruta de descarga"""
        self.download_path = new_path