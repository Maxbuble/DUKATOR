"""
Pestaña de búsqueda inteligente de álbumes
"""

import customtkinter as ctk
from tkinter import messagebox
import threading
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import COLORS, FONTS
from core.musicbrainz_client import mb_client
from core.downloader import DownloadEngine
from core.metadata import metadata_manager

class AlbumSearchTab(ctk.CTkFrame):
    def __init__(self, parent, download_path, ffmpeg_manager):
        super().__init__(parent, fg_color=COLORS["bg_primary"])
        
        self.download_path = download_path
        self.ffmpeg_manager = ffmpeg_manager
        self.downloader = None
        self.current_album = None
        self.selected_tracks = []
        
        self.create_ui()
    
    def create_ui(self):
        """Crea la interfaz de la pestaña"""
        # Panel superior: Búsqueda
        search_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"])
        search_frame.pack(fill="x", padx=10, pady=10)
        
        # Campos de búsqueda
        ctk.CTkLabel(search_frame, text="Artista:", font=FONTS["body"], text_color=COLORS["text_secondary"]).pack(side="left", padx=10, pady=10)
        self.artist_entry = ctk.CTkEntry(search_frame, width=200, font=FONTS["body"])
        self.artist_entry.pack(side="left", padx=5, pady=10)
        
        ctk.CTkLabel(search_frame, text="Álbum:", font=FONTS["body"], text_color=COLORS["text_secondary"]).pack(side="left", padx=10, pady=10)
        self.album_entry = ctk.CTkEntry(search_frame, width=200, font=FONTS["body"])
        self.album_entry.pack(side="left", padx=5, pady=10)
        
        self.search_btn = ctk.CTkButton(
            search_frame,
            text="🔍 Buscar",
            font=FONTS["heading"],
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_hover"],
            command=self.search_albums
        )
        self.search_btn.pack(side="left", padx=20, pady=10)
        
        # Panel central dividido
        center_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_primary"])
        center_frame.pack(fill="both", expand=True, padx=10, pady=5)
        center_frame.grid_columnconfigure(0, weight=1)
        center_frame.grid_columnconfigure(1, weight=2)
        center_frame.grid_rowconfigure(0, weight=1)
        
        # Panel izquierdo: Resultados de álbumes
        albums_frame = ctk.CTkFrame(center_frame, fg_color=COLORS["bg_secondary"])
        albums_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        ctk.CTkLabel(albums_frame, text="📀 Ediciones Encontradas", font=FONTS["heading"], text_color=COLORS["accent_secondary"]).pack(pady=10)
        
        self.albums_list = ctk.CTkScrollableFrame(albums_frame, fg_color=COLORS["bg_tertiary"], height=300)
        self.albums_list.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Panel derecho: Canciones
        tracks_frame = ctk.CTkFrame(center_frame, fg_color=COLORS["bg_secondary"])
        tracks_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        ctk.CTkLabel(tracks_frame, text="🎵 Canciones", font=FONTS["heading"], text_color=COLORS["accent_secondary"]).pack(pady=10)
        
        self.tracks_list = ctk.CTkScrollableFrame(tracks_frame, fg_color=COLORS["bg_tertiary"])
        self.tracks_list.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Panel inferior: Controles de descarga
        controls_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"])
        controls_frame.pack(fill="x", padx=10, pady=10)
        
        # Fuentes de búsqueda
        sources_label = ctk.CTkLabel(controls_frame, text="Fuentes (prioridad):", font=FONTS["body_small"], text_color=COLORS["text_secondary"])
        sources_label.pack(side="left", padx=10, pady=10)
        
        self.source_vars = {}
        sources = [("Bandcamp", True), ("SoundCloud", True), ("YouTube", True), ("Archive.org", False)]
        for source, default in sources:
            var = ctk.BooleanVar(value=default)
            self.source_vars[source] = var
            cb = ctk.CTkCheckBox(
                controls_frame,
                text=source,
                variable=var,
                font=FONTS["body_small"],
                text_color=COLORS["text_secondary"],
                fg_color=COLORS["accent_primary"],
                hover_color=COLORS["accent_hover"]
            )
            cb.pack(side="left", padx=5, pady=10)
        
        # Botones de acción
        self.select_all_btn = ctk.CTkButton(
            controls_frame,
            text="✓ Todas",
            font=FONTS["body_small"],
            fg_color=COLORS["bg_tertiary"],
            hover_color=COLORS["accent_hover"],
            width=80,
            command=self.select_all_tracks
        )
        self.select_all_btn.pack(side="right", padx=5, pady=10)
        
        self.download_btn = ctk.CTkButton(
            controls_frame,
            text="⬇️ Descargar Seleccionadas",
            font=FONTS["heading"],
            fg_color=COLORS["success"],
            hover_color="#059669",
            command=self.download_selected
        )
        self.download_btn.pack(side="right", padx=10, pady=10)
        
        # Barra de progreso
        self.progress_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_primary"])
        self.progress_frame.pack(fill="x", padx=10, pady=5)
        self.progress_frame.pack_forget()  # Ocultar inicialmente
        
        self.progress_label = ctk.CTkLabel(self.progress_frame, text="", font=FONTS["body"], text_color=COLORS["text_secondary"])
        self.progress_label.pack(side="left", padx=10)
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, width=400, progress_color=COLORS["accent_primary"])
        self.progress_bar.pack(side="left", padx=10, pady=5)
        self.progress_bar.set(0)
    
    def search_albums(self):
        """Busca álbumes en MusicBrainz"""
        artist = self.artist_entry.get().strip()
        album = self.album_entry.get().strip()
        
        if not artist or not album:
            messagebox.showwarning("Búsqueda", "Por favor introduce artista y álbum")
            return
        
        self.search_btn.configure(state="disabled", text="Buscando...")
        
        # Limpiar lista anterior
        for widget in self.albums_list.winfo_children():
            widget.destroy()
        
        # Buscar en thread
        def do_search():
            try:
                results = mb_client.search_albums(artist, album)
                self.after(0, lambda: self.show_albums(results))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Error buscando: {str(e)}"))
            finally:
                self.after(0, lambda: self.search_btn.configure(state="normal", text="🔍 Buscar"))
        
        threading.Thread(target=do_search, daemon=True).start()
    
    def show_albums(self, albums):
        """Muestra los álbumes encontrados"""
        if not albums:
            label = ctk.CTkLabel(self.albums_list, text="No se encontraron álbumes", font=FONTS["body"], text_color=COLORS["text_muted"])
            label.pack(pady=20)
            return
        
        for album in albums:
            btn = ctk.CTkButton(
                self.albums_list,
                text=f"{album['artist']} - {album['title']}\n{album['year']} | {album['format']} | {album['country']}",
                font=FONTS["body_small"],
                fg_color=COLORS["bg_secondary"],
                hover_color=COLORS["accent_primary"],
                anchor="w",
                command=lambda a=album: self.select_album(a)
            )
            btn.pack(fill="x", padx=5, pady=2)
    
    def select_album(self, album):
        """Selecciona un álbum y muestra sus canciones"""
        # Limpiar canciones anteriores
        for widget in self.tracks_list.winfo_children():
            widget.destroy()
        
        self.selected_tracks = []
        self.current_album = album
        
        # Mostrar loading
        loading = ctk.CTkLabel(self.tracks_list, text="Cargando canciones...", font=FONTS["body"], text_color=COLORS["text_muted"])
        loading.pack(pady=20)
        
        def load_tracks():
            try:
                album_data = mb_client.get_album_tracks(album['id'])
                self.after(0, lambda: self.show_tracks(album_data))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Error cargando canciones: {str(e)}"))
        
        threading.Thread(target=load_tracks, daemon=True).start()
    
    def show_tracks(self, album_data):
        """Muestra las canciones del álbum"""
        # Limpiar loading
        for widget in self.tracks_list.winfo_children():
            widget.destroy()
        
        if not album_data or not album_data.get('tracks'):
            label = ctk.CTkLabel(self.tracks_list, text="No se encontraron canciones", font=FONTS["body"], text_color=COLORS["text_muted"])
            label.pack(pady=20)
            return
        
        self.current_album = album_data
        
        # Checkbox para cada canción
        for track in album_data['tracks']:
            var = ctk.BooleanVar(value=True)
            self.selected_tracks.append((track, var))
            
            frame = ctk.CTkFrame(self.tracks_list, fg_color=COLORS["bg_secondary"])
            frame.pack(fill="x", padx=5, pady=2)
            
            cb = ctk.CTkCheckBox(
                frame,
                text="",
                variable=var,
                width=20,
                fg_color=COLORS["accent_primary"],
                hover_color=COLORS["accent_hover"]
            )
            cb.pack(side="left", padx=5)
            
            num_label = ctk.CTkLabel(frame, text=f"{track['number']:02d}", font=FONTS["mono"], text_color=COLORS["text_muted"], width=30)
            num_label.pack(side="left", padx=5)
            
            title_label = ctk.CTkLabel(frame, text=track['title'], font=FONTS["body"], text_color=COLORS["text_primary"])
            title_label.pack(side="left", padx=5, fill="x", expand=True)
            
            duration_label = ctk.CTkLabel(frame, text=track['duration_formatted'], font=FONTS["mono"], text_color=COLORS["text_secondary"], width=50)
            duration_label.pack(side="right", padx=10)
    
    def select_all_tracks(self):
        """Selecciona/deselecciona todas las canciones"""
        if not self.selected_tracks:
            return
        
        # Verificar si todas están seleccionadas
        all_selected = all(var.get() for _, var in self.selected_tracks)
        
        # Toggle
        for _, var in self.selected_tracks:
            var.set(not all_selected)
        
        self.select_all_btn.configure(text="✓ Ninguna" if all_selected else "✓ Todas")
    
    def download_selected(self):
        """Descarga las canciones seleccionadas"""
        if not self.current_album:
            messagebox.showwarning("Descarga", "Primero selecciona un álbum")
            return
        
        selected = [(track, var) for track, var in self.selected_tracks if var.get()]
        
        if not selected:
            messagebox.showwarning("Descarga", "Selecciona al menos una canción")
            return
        
        # Obtener fuentes seleccionadas
        sources = [s.lower().replace('.', '') for s, var in self.source_vars.items() if var.get()]
        
        # Mostrar progreso
        self.progress_frame.pack(fill="x", padx=10, pady=5)
        self.download_btn.configure(state="disabled", text="Descargando...")
        
        # Descargar en thread
        def do_download():
            try:
                # Inicializar downloader
                ffmpeg_path = self.ffmpeg_manager.get_ffmpeg_path()
                downloader = DownloadEngine(ffmpeg_path)
                
                # Crear estructura de carpetas
                album_path = metadata_manager.create_folder_structure(
                    self.download_path,
                    self.current_album['artist'],
                    self.current_album['year'],
                    self.current_album['title']
                )
                
                # Descargar cada canción
                total = len(selected)
                for i, (track, _) in enumerate(selected, 1):
                    progress = (i - 1) / total
                    self.after(0, lambda p=progress, t=track: self.update_progress(p, f"Buscando: {t['title']}"))
                    
                    # Construir query
                    query = f"{self.current_album['artist']} {track['title']}"
                    
                    # Nombre de archivo
                    safe_title = "".join(c for c in track['title'] if c.isalnum() or c in (' ', '-', '_'))[:50]
                    output_file = album_path / f"{track['number']:02d} - {safe_title}"
                    
                    # Descargar
                    def track_progress(percent, msg):
                        overall = progress + (percent / 100 / total)
                        self.after(0, lambda p=overall, m=msg: self.update_progress(p, f"{track['title'][:30]}... {m}"))
                    
                    result = downloader.download_track(
                        query,
                        output_file,
                        expected_duration=track['duration'],
                        progress_callback=track_progress,
                        source_priority=sources
                    )
                    
                    if result['success']:
                        # Aplicar metadatos
                        cover_url = mb_client.get_cover_art_url(self.current_album['id'])
                        metadata_manager.tag_track(
                            result['file_path'],
                            title=track['title'],
                            artist=self.current_album['artist'],
                            album=self.current_album['title'],
                            year=self.current_album['year'],
                            track_number=track['number'],
                            total_tracks=len(self.current_album['tracks']),
                            cover_url=cover_url
                        )
                
                self.after(0, lambda: self.download_complete(True, f"Descargadas {total} canciones en:\n{album_path}"))
                
            except Exception as e:
                self.after(0, lambda: self.download_complete(False, str(e)))
        
        threading.Thread(target=do_download, daemon=True).start()
    
    def update_progress(self, value, message):
        """Actualiza la barra de progreso"""
        self.progress_bar.set(value)
        self.progress_label.configure(text=message)
    
    def download_complete(self, success, message):
        """Callback cuando termina la descarga"""
        self.progress_frame.pack_forget()
        self.download_btn.configure(state="normal", text="⬇️ Descargar Seleccionadas")
        
        if success:
            messagebox.showinfo("Éxito", message)
        else:
            messagebox.showerror("Error", f"Error en descarga:\n{message}")
    
    def update_download_path(self, new_path):
        """Actualiza la ruta de descarga"""
        self.download_path = new_path