"""
Pestaña de búsqueda de canciones individuales
"""

import customtkinter as ctk
from tkinter import messagebox
import threading
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import COLORS, FONTS
from core.downloader import DownloadEngine
from core.metadata import metadata_manager

class TrackSearchTab(ctk.CTkFrame):
    def __init__(self, parent, download_path, ffmpeg_manager):
        super().__init__(parent, fg_color=COLORS["bg_primary"])
        
        self.download_path = download_path
        self.ffmpeg_manager = ffmpeg_manager
        self.downloader = None
        self.search_results = []
        
        self.create_ui()
    
    def create_ui(self):
        """Crea la interfaz de la pestaña"""
        # Panel superior: Búsqueda
        search_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"])
        search_frame.pack(fill="x", padx=10, pady=10)
        
        title = ctk.CTkLabel(
            search_frame,
            text="🎵 Buscador de Canciones Sueltas",
            font=FONTS["subtitle"],
            text_color=COLORS["accent_primary"]
        )
        title.pack(pady=10)
        
        # Campos de búsqueda
        input_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(input_frame, text="Canción:", font=FONTS["body"], text_color=COLORS["text_secondary"]).pack(side="left", padx=5)
        self.track_entry = ctk.CTkEntry(input_frame, width=250, font=FONTS["body"], placeholder_text="Nombre de la canción")
        self.track_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(input_frame, text="Artista:", font=FONTS["body"], text_color=COLORS["text_secondary"]).pack(side="left", padx=5)
        self.artist_entry = ctk.CTkEntry(input_frame, width=200, font=FONTS["body"], placeholder_text="Artista (opcional)")
        self.artist_entry.pack(side="left", padx=5)
        
        self.search_btn = ctk.CTkButton(
            input_frame,
            text="🔍 Buscar",
            font=FONTS["heading"],
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_hover"],
            command=self.search_tracks
        )
        self.search_btn.pack(side="left", padx=20)
        
        # Opciones de búsqueda
        options_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        options_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(options_frame, text="Buscar en:", font=FONTS["body_small"], text_color=COLORS["text_secondary"]).pack(side="left", padx=5)
        
        self.source_vars = {}
        sources = [
            ("YouTube", True),
            ("SoundCloud", True),
            ("Bandcamp", True),
            ("Archive.org", False)
        ]
        
        for source, default in sources:
            var = ctk.BooleanVar(value=default)
            self.source_vars[source] = var
            cb = ctk.CTkCheckBox(
                options_frame,
                text=source,
                variable=var,
                font=FONTS["body_small"],
                text_color=COLORS["text_secondary"],
                fg_color=COLORS["accent_primary"],
                hover_color=COLORS["accent_hover"]
            )
            cb.pack(side="left", padx=10)
        
        # Panel de resultados
        results_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"])
        results_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(results_frame, text="🔎 Resultados de Búsqueda", font=FONTS["heading"], text_color=COLORS["accent_secondary"]).pack(pady=10)
        
        # Lista de resultados con scroll
        self.results_container = ctk.CTkScrollableFrame(results_frame, fg_color=COLORS["bg_tertiary"])
        self.results_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Mensaje inicial
        self.show_empty_message()
        
        # Panel inferior: Progreso y controles
        bottom_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"])
        bottom_frame.pack(fill="x", padx=10, pady=10)
        
        # Info
        self.info_label = ctk.CTkLabel(
            bottom_frame,
            text="Introduce el nombre de una canción para buscar",
            font=FONTS["body_small"],
            text_color=COLORS["text_muted"]
        )
        self.info_label.pack(side="left", padx=10, pady=10)
        
        # Botón descargar seleccionada
        self.download_btn = ctk.CTkButton(
            bottom_frame,
            text="⬇️ Descargar Seleccionada",
            font=FONTS["heading"],
            fg_color=COLORS["success"],
            hover_color="#059669",
            state="disabled",
            command=self.download_selected_track
        )
        self.download_btn.pack(side="right", padx=10, pady=10)
        
        # Barra de progreso
        self.progress_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_primary"])
        
        self.progress_label = ctk.CTkLabel(self.progress_frame, text="", font=FONTS["body"], text_color=COLORS["text_secondary"])
        self.progress_label.pack(side="left", padx=10)
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, width=400, progress_color=COLORS["accent_primary"])
        self.progress_bar.pack(side="left", padx=10, pady=5)
        self.progress_bar.set(0)
    
    def show_empty_message(self):
        """Muestra mensaje de búsqueda vacía"""
        for widget in self.results_container.winfo_children():
            widget.destroy()
        
        label = ctk.CTkLabel(
            self.results_container,
            text="🔍 Los resultados aparecerán aquí\n\n"
                 "Busca por nombre de canción y opcionalmente artista\n"
                 "La app buscará en todas las fuentes seleccionadas",
            font=FONTS["body"],
            text_color=COLORS["text_muted"],
            justify="center"
        )
        label.pack(pady=50)
    
    def search_tracks(self):
        """Busca canciones en las fuentes seleccionadas"""
        track_name = self.track_entry.get().strip()
        artist_name = self.artist_entry.get().strip()
        
        if not track_name:
            messagebox.showwarning("Búsqueda", "Por favor introduce el nombre de la canción")
            return
        
        # Construir query
        if artist_name:
            query = f"{artist_name} {track_name}"
        else:
            query = track_name
        
        # Obtener fuentes seleccionadas
        selected_sources = [s for s, var in self.source_vars.items() if var.get()]
        if not selected_sources:
            messagebox.showwarning("Búsqueda", "Selecciona al menos una fuente")
            return
        
        # Actualizar UI
        self.search_btn.configure(state="disabled", text="Buscando...")
        self.info_label.configure(text=f"Buscando: {query}")
        
        # Limpiar resultados anteriores
        for widget in self.results_container.winfo_children():
            widget.destroy()
        
        self.search_results = []
        self.selected_result = None
        self.download_btn.configure(state="disabled")
        
        # Buscar en thread
        def do_search():
            try:
                ffmpeg_path = self.ffmpeg_manager.get_ffmpeg_path()
                downloader = DownloadEngine(ffmpeg_path)
                
                # Buscar en cada fuente
                for i, source in enumerate(selected_sources):
                    self.after(0, lambda s=source: self.info_label.configure(text=f"Buscando en {s}..."))
                    
                    # Construir query específico por fuente
                    if source == "YouTube":
                        search_query = f"ytsearch3:{query} audio"
                    elif source == "SoundCloud":
                        search_query = f"ytsearch3:{query} soundcloud"
                    elif source == "Bandcamp":
                        search_query = f"ytsearch3:{query} bandcamp"
                    elif source == "Archive.org":
                        search_query = f"ytsearch3:{query} archive.org"
                    else:
                        search_query = f"ytsearch3:{query}"
                    
                    # Extraer info sin descargar
                    try:
                        import yt_dlp
                        ydl_opts = {'quiet': True, 'no_warnings': True}
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            results = ydl.extract_info(search_query, download=False)
                            
                            if results and 'entries' in results:
                                for entry in results['entries'][:3]:  # Top 3 por fuente
                                    if entry:
                                        result_data = {
                                            'title': entry.get('title', 'Unknown'),
                                            'artist': entry.get('uploader', 'Unknown'),
                                            'duration': entry.get('duration', 0),
                                            'url': entry.get('webpage_url', ''),
                                            'source': source,
                                            'thumbnail': entry.get('thumbnail', '')
                                        }
                                        self.search_results.append(result_data)
                                        self.after(0, lambda r=result_data: self.add_result_to_ui(r))
                    except Exception as e:
                        print(f"Error buscando en {source}: {e}")
                        continue
                
                if not self.search_results:
                    self.after(0, self.show_no_results)
                else:
                    self.after(0, lambda: self.info_label.configure(text=f"Se encontraron {len(self.search_results)} resultados"))
                
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Error en búsqueda: {str(e)}"))
            finally:
                self.after(0, lambda: self.search_btn.configure(state="normal", text="🔍 Buscar"))
        
        threading.Thread(target=do_search, daemon=True).start()
    
    def add_result_to_ui(self, result):
        """Añade un resultado a la UI"""
        # Frame del resultado
        frame = ctk.CTkFrame(self.results_container, fg_color=COLORS["bg_secondary"])
        frame.pack(fill="x", padx=5, pady=3)
        
        # Radio button para selección
        var = ctk.BooleanVar(value=False)
        
        def on_select():
            # Deseleccionar otros
            for child in self.results_container.winfo_children():
                if isinstance(child, ctk.CTkFrame):
                    for widget in child.winfo_children():
                        if isinstance(widget, ctk.CTkRadioButton):
                            if widget != rb:
                                widget.deselect()
            
            self.selected_result = result
            self.download_btn.configure(state="normal")
        
        rb = ctk.CTkRadioButton(
            frame,
            text="",
            variable=var,
            value=True,
            command=on_select,
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_hover"]
        )
        rb.pack(side="left", padx=5, pady=10)
        
        # Info del resultado
        info_frame = ctk.CTkFrame(frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        
        # Título
        title = ctk.CTkLabel(
            info_frame,
            text=result['title'][:60] + "..." if len(result['title']) > 60 else result['title'],
            font=FONTS["body"],
            text_color=COLORS["text_primary"],
            anchor="w"
        )
        title.pack(fill="x")
        
        # Subtítulo con fuente y duración
        duration_str = f"{int(result['duration'] // 60)}:{int(result['duration'] % 60):02d}" if result['duration'] else "?:??"
        subtitle_text = f"🎵 {result['source']} | 👤 {result['artist'][:30]} | ⏱️ {duration_str}"
        
        subtitle = ctk.CTkLabel(
            info_frame,
            text=subtitle_text,
            font=FONTS["body_small"],
            text_color=COLORS["text_secondary"],
            anchor="w"
        )
        subtitle.pack(fill="x")
    
    def show_no_results(self):
        """Muestra mensaje de sin resultados"""
        for widget in self.results_container.winfo_children():
            widget.destroy()
        
        label = ctk.CTkLabel(
            self.results_container,
            text="❌ No se encontraron resultados\n\n"
                 "Prueba con términos diferentes o verifica las fuentes seleccionadas",
            font=FONTS["body"],
            text_color=COLORS["error"],
            justify="center"
        )
        label.pack(pady=50)
        
        self.info_label.configure(text="Sin resultados")
    
    def download_selected_track(self):
        """Descarga la canción seleccionada"""
        if not self.selected_result:
            return
        
        result = self.selected_result
        
        # Mostrar progreso
        self.progress_frame.pack(fill="x", padx=10, pady=5, before=self.winfo_children()[-1])
        self.download_btn.configure(state="disabled", text="Descargando...")
        self.search_btn.configure(state="disabled")
        
        def do_download():
            try:
                ffmpeg_path = self.ffmpeg_manager.get_ffmpeg_path()
                downloader = DownloadEngine(ffmpeg_path)
                
                # Crear carpeta para tracks sueltos
                tracks_path = self.download_path / "Canciones_Sueltas"
                tracks_path.mkdir(parents=True, exist_ok=True)
                
                # Nombre de archivo seguro
                safe_name = "".join(c for c in result['title'] if c.isalnum() or c in (' ', '-', '_'))[:50]
                output_file = tracks_path / safe_name
                
                self.after(0, lambda: self.update_progress(0, f"Descargando: {result['title'][:40]}..."))
                
                def progress_callback(percent, msg):
                    self.after(0, lambda p=percent/100: self.update_progress(p, msg))
                
                # Descargar
                download_result = downloader._download_from_url(
                    result['url'],
                    output_file,
                    None,
                    progress_callback
                )
                
                if download_result['success']:
                    # Aplicar metadatos básicos
                    metadata_manager.tag_track(
                        download_result['file_path'],
                        title=result['title'],
                        artist=result['artist'],
                        album="Canciones Sueltas",
                        genre=""
                    )
                    
                    self.after(0, lambda: self.download_complete(True, f"✓ Descargado: {result['title']}\n📁 Guardado en: {tracks_path}"))
                else:
                    self.after(0, lambda: self.download_complete(False, f"Error: {download_result.get('error', 'Unknown error')}"))
                
            except Exception as e:
                self.after(0, lambda: self.download_complete(False, str(e)))
        
        threading.Thread(target=do_download, daemon=True).start()
    
    def update_progress(self, value, message):
        """Actualiza la barra de progreso"""
        self.progress_bar.set(value)
        self.progress_label.configure(text=message)
    
    def download_complete(self, success, message):
        """Callback de descarga completada"""
        self.progress_frame.pack_forget()
        self.download_btn.configure(state="normal", text="⬇️ Descargar Seleccionada")
        self.search_btn.configure(state="normal")
        
        if success:
            messagebox.showinfo("Éxito", message)
        else:
            messagebox.showerror("Error", message)
    
    def update_download_path(self, new_path):
        """Actualiza la ruta de descarga"""
        self.download_path = new_path