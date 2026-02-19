import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
import requests
import json
import os
import sys
import re
import time
import tempfile
from urllib.parse import quote as url_quote
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TRCK, APIC, TXXX
from mutagen.mp3 import MP3
import yt_dlp
import io

# Forzar stdout/stderr a UTF-8 para evitar UnicodeEncodeError con emojis en Windows
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Mejor manejo de errores de pygame
PYGAME_AVAILABLE = False
try:
    import pygame
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    PYGAME_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] pygame no disponible: {e}")
except Exception as e:
    print(f"[WARNING] Error iniciando pygame: {e}")

COLORS = {
    # Fondos - Escalado de grises oscuros
    'bg_main': '#0D0D0D',        # Negro casi puro (fondo principal)
    'bg_secondary': '#1A1A1A',   # Gris muy oscuro (header, player)
    'bg_card': '#242424',        # Gris oscuro (cards, frames)
    'bg_hover': '#2E2E2E',      # Gris para hover states
    
    # Acento - Naranja suave (para que no fatigue)
    'accent': '#E65C00',         # Naranja profundo
    'accent_hover': '#FF7000',  # Naranja brillante (hover)
    'accent_dim': '#4D2819',     # Naranja muy tenue (fondos sutiles)
    
    # Estados
    'action_play': '#4CAF50',    # Verde para play
    'action_stop': '#F44336',    # Rojo para stop
    
    # Texto
    'text_primary': '#F5F5F5',   # Blanco suave
    'text_secondary': '#9E9E9E', # Gris medio
    'text_muted': '#616161',     # Gris oscuro
    
    # Bordes
    'border': '#333333',         # Borde sutil
    'border_light': '#444444',   # Borde mas claro
    
    # Progress
    'progress_bg': '#1A1A1A',
    'progress_bar': '#E65C00',
}

DOWNLOAD_SOURCES = [
    ('youtube', 'YouTube', 'youtube.com'),
    ('audiomack', 'Audiomack', 'audiomack.com'),
    ('soundcloud', 'SoundCloud', 'soundcloud.com'),
    ('vimeo', 'Vimeo', 'vimeo.com'),
    ('bandcamp', 'Bandcamp', 'bandcamp.com'),
    ('mixcloud', 'Mixcloud', 'mixcloud.com'),
    ('dailymotion', 'Dailymotion', 'dailymotion.com'),
    ('archive', 'Archive.org', 'archive.org'),
    ('vk', 'VK', 'vk.com'),
    ('twitch', 'Twitch', 'twitch.tv'),
    ('bilibili', 'Bilibili', 'bilibili.com'),
    ('facebook', 'Facebook', 'facebook.com'),
    ('instagram', 'Instagram', 'instagram.com'),
    ('tiktok', 'TikTok', 'tiktok.com'),
    ('pixabay', 'Pixabay', 'pixabay.com'),
]

COVER_ART_ARCHIVE = "https://coverartarchive.org"

ctk.set_appearance_mode("dark")


class SourceDetector:
    """Detecta la fuente de una URL"""
    SOURCE_PATTERNS = {
        'youtube': ['youtube.com', 'youtu.be'],
        'audiomack': ['audiomack.com'],
        'soundcloud': ['soundcloud.com'],
        'vimeo': ['vimeo.com'],
        'bandcamp': ['bandcamp.com'],
        'vk': ['vk.com'],
        'twitch': ['twitch.tv'],
        'mixcloud': ['mixcloud.com'],
        'dailymotion': ['dailymotion.com'],
        'archive': ['archive.org'],
        'bilibili': ['bilibili.com'],
        'facebook': ['facebook.com'],
        'instagram': ['instagram.com'],
        'tiktok': ['tiktok.com'],
        'pixabay': ['pixabay.com'],
    }
    
    @classmethod
    def detect(cls, url):
        url_lower = url.lower()
        for source, patterns in cls.SOURCE_PATTERNS.items():
            for pattern in patterns:
                if pattern in url_lower:
                    return source
        return 'generic'
    
    @classmethod
    def get_display_name(cls, source):
        names = {
            'youtube': 'YouTube',
            'audiomack': 'Audiomack',
            'soundcloud': 'SoundCloud',
            'vimeo': 'Vimeo',
            'bandcamp': 'Bandcamp',
            'vk': 'VK',
            'twitch': 'Twitch',
            'mixcloud': 'Mixcloud',
            'dailymotion': 'Dailymotion',
            'archive': 'Archive.org',
            'bilibili': 'Bilibili',
            'facebook': 'Facebook',
            'instagram': 'Instagram',
            'tiktok': 'TikTok',
            'pixabay': 'Pixabay',
            'generic': 'Directo'
        }
        return names.get(source, source)


class CoverArtFetcher:
    """Obtiene carátulas de Cover Art Archive (gratuito, sin API key)"""
    
    @classmethod
    def get_cover(cls, release_id):
        try:
            url = f"https://coverartarchive.org/release/{release_id}"
            headers = {
                "User-Agent": "DUKATOR/2.0 (https://github.com/dukator)",
                "Accept": "application/json"
            }
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                images = data.get('images', [])
                for img in images:
                    if img.get('front'):
                        img_url = img.get('image', '')
                        img_response = requests.get(img_url, timeout=15)
                        if img_response.status_code == 200:
                            return img_response.content
            return None
        except:
            return None


class AudioPlayer:
    def __init__(self, status_callback=None):
        self.is_playing = False
        self.is_paused = False
        self.current_file = None
        self.current_track_name = ""
        self.preview_thread = None
        self.stop_flag = False
        self.status_callback = status_callback
        self.duration = 0
        self.start_time = 0
        self.preview_duration = 30
        self.progress_callback = None
        
    def play_preview(self, search_query, on_complete=None, progress_callback=None):
        self.progress_callback = progress_callback
        if not PYGAME_AVAILABLE:
            if self.status_callback:
                self.status_callback("pygame no disponible")
            return
            
        self.stop()
        self.stop_flag = False
        
        self.preview_thread = threading.Thread(
            target=self._play_preview_thread,
            args=(search_query, on_complete),
            daemon=True
        )
        self.preview_thread.start()
        
    def _play_preview_thread(self, search_query, on_complete):
        try:
            import yt_dlp
            
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, f"dukator_preview_{int(time.time())}.mp3")
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': temp_file.replace('.mp3', '.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '128',
                }],
                'quiet': True,
                'no_warnings': True,
                'duration_limit': self.preview_duration + 5,
            }
            
            url = "https://www.youtube.com/results"
            params = {"search_query": search_query}
            response = requests.get(url, params=params, timeout=30)
            match = re.search(r'"videoId":"([^"]+)"', response.text)
            
            if not match:
                if self.status_callback:
                    self.status_callback("No encontrado en YouTube")
                return
                
            video_id = match.group(1)
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                self.current_track_name = info.get('title', 'Preview')
                
            if os.path.exists(temp_file):
                self.current_file = temp_file
                pygame.mixer.music.load(temp_file)
                pygame.mixer.music.play()
                self.is_playing = True
                self.is_paused = False
                self.start_time = time.time()
                
                if self.status_callback:
                    self.status_callback(f"▶ Reproduciendo: {self.current_track_name[:50]}")
                    
                while pygame.mixer.music.get_busy() and not self.stop_flag:
                    elapsed = time.time() - self.start_time
                    # Actualizar progreso visual
                    if self.progress_callback:
                        try:
                            self.progress_callback(elapsed, self.preview_duration)
                        except:
                            pass
                    if elapsed >= self.preview_duration and self.is_playing:
                        pygame.mixer.music.stop()
                        break
                    time.sleep(0.1)
                    
                if self.status_callback and not self.stop_flag:
                    self.status_callback("Preview finalizado")
                    
                try:
                    os.remove(temp_file)
                except:
                    pass
                    
            if on_complete:
                on_complete()
                
        except Exception as e:
            if self.status_callback:
                self.status_callback(f"Error en preview: {str(e)}")
                
    def pause(self):
        if self.is_playing and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
            return True
        return False
        
    def resume(self):
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            return True
        return False
        
    def stop(self):
        self.stop_flag = True
        self.is_playing = False
        self.is_paused = False
        try:
            pygame.mixer.music.stop()
        except:
            pass
        if self.current_file:
            try:
                os.remove(self.current_file)
            except:
                pass
        self.current_file = None
        
    def set_volume(self, volume):
        try:
            pygame.mixer.music.set_volume(volume)
        except:
            pass
            
    def get_elapsed(self):
        if self.is_playing and not self.is_paused:
            return time.time() - self.start_time
        return 0


class StyledButton(ctk.CTkButton):
    def __init__(self, master, style="primary", **kwargs):
        colors = {
            'primary': (COLORS['accent'], COLORS['accent_hover']),
            'play': (COLORS['action_play'], '#2ECC71'),
            'stop': (COLORS['action_stop'], '#E74C3C'),
            'secondary': (COLORS['bg_card'], COLORS['border_light']),
        }
        
        fg_color, hover_color = colors.get(style, colors['primary'])
        
        super().__init__(
            master,
            fg_color=fg_color,
            hover_color=hover_color,
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border'],
            text_color=COLORS['text_primary'],
            **kwargs
        )




class ProgressOverlay(ctk.CTkFrame):
    """Overlay de progreso para mostrar durante descargas"""
    
    def __init__(self, master, **kwargs):
        super().__init__(
            master, 
            fg_color='#0F0F23', 
            corner_radius=16,
            border_width=2,
            border_color=COLORS['accent'],
            **kwargs
        )
        
        self.grid_columnconfigure(0, weight=1)
        
        # Título
        self.title_label = ctk.CTkLabel(
            self, text="⏳ DESCARGANDO",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS['text_primary']
        )
        self.title_label.grid(row=0, column=0, pady=(20, 10))
        
        # Fuente actual
        self.source_label = ctk.CTkLabel(
            self, text="YouTube",
            font=ctk.CTkFont(size=14),
            text_color=COLORS['accent']
        )
        self.source_label.grid(row=1, column=0, pady=(0, 10))
        
        # Porcentaje grande
        self.percent_label = ctk.CTkLabel(
            self, text="0%",
            font=ctk.CTkFont(size=56, weight="bold"),
            text_color=COLORS['action_play']
        )
        self.percent_label.grid(row=2, column=0, pady=10)
        
        # Barra de progreso
        self.progress_bar = ctk.CTkProgressBar(
            self, width=280, height=12,
            fg_color=COLORS['progress_bg'],
            progress_color=COLORS['action_play'],
            corner_radius=6
        )
        self.progress_bar.grid(row=3, column=0, pady=15)
        self.progress_bar.set(0)
        
        # Estado actual
        self.status_label = ctk.CTkLabel(
            self, text="Iniciando...",
            font=ctk.CTkFont(size=13),
            text_color=COLORS['text_secondary']
        )
        self.status_label.grid(row=4, column=0, pady=(0, 10))
        
        # Contador
        self.counter_label = ctk.CTkLabel(
            self, text="0 / 0 canciones",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary']
        )
        self.counter_label.grid(row=5, column=0, pady=(0, 20))
        
    def update_progress(self, current, total, status="", source=""):
        percent = int((current / total) * 100) if total > 0 else 0
        self.percent_label.configure(text=f"{percent}%")
        self.progress_bar.set(current / total if total > 0 else 0)
        if status:
            self.status_label.configure(text=status[:50])
        if source:
            self.source_label.configure(text=source)
        self.counter_label.configure(text=f"{current} / {total} canciones")
        
    def show(self):
        self.place(relx=0.5, rely=0.5, anchor="center")
        self.lift()
        
    def hide(self):
        self.place_forget()

class TrackCard(ctk.CTkFrame):
    def __init__(self, master, track_data, on_preview=None, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS['bg_card'],
            corner_radius=10,
            border_width=1,
            border_color=COLORS['border'],
            **kwargs
        )
        
        self.track_data = track_data
        self.on_preview = on_preview
        self.is_playing = False
        self.download_source = None
        
        self.setup_ui()
        
    def setup_ui(self):
        inner_frame = ctk.CTkFrame(self, fg_color="transparent")
        inner_frame.pack(fill="x", padx=8, pady=6)
        
        self.checkbox = ctk.CTkCheckBox(
            inner_frame,
            text="",
            variable=self.track_data['selected'],
            fg_color=COLORS['accent'],
            hover_color=COLORS['accent_hover'],
            border_color=COLORS['border_light'],
            corner_radius=4,
            width=20
        )
        self.checkbox.pack(side="left", padx=(0, 8))
        
        num_label = ctk.CTkLabel(
            inner_frame,
            text=f"{self.track_data['number']:02d}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS['text_secondary'],
            width=25
        )
        num_label.pack(side="left", padx=(0, 8))
        
        self.status_label = ctk.CTkLabel(
            inner_frame,
            text="○",
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text_secondary'],
            width=20
        )
        self.status_label.pack(side="left", padx=(0, 5))
        
        title_label = ctk.CTkLabel(
            inner_frame,
            text=self.track_data['title'][:60],
            font=ctk.CTkFont(size=13),
            text_color=COLORS['text_primary'],
            anchor="w"
        )
        title_label.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.source_label = ctk.CTkLabel(
            inner_frame,
            text="",
            font=ctk.CTkFont(size=10),
            text_color=COLORS['accent'],
            width=70
        )
        self.source_label.pack(side="left", padx=(0, 5))
        
        duration_sec = self.track_data['duration_ms'] // 1000
        mins = duration_sec // 60
        secs = duration_sec % 60
        
        duration_label = ctk.CTkLabel(
            inner_frame,
            text=f"{mins}:{secs:02d}",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_secondary'],
            width=45
        )
        duration_label.pack(side="left", padx=(0, 10))
        
        self.preview_btn = ctk.CTkButton(
            inner_frame,
            text="▶",
            font=ctk.CTkFont(size=14),
            width=32,
            height=28,
            fg_color=COLORS['bg_secondary'],
            hover_color=COLORS['accent'],
            corner_radius=6,
            command=self.toggle_preview
        )
        self.preview_btn.pack(side="right")
        
    def set_source(self, source_name):
        self.download_source = source_name
        self.source_label.configure(text=source_name)
        

    def set_status(self, status):
        icons = {
            'pending': ('○', COLORS['text_secondary']),
            'downloading': ('⏳', COLORS['accent']),
            'success': ('✓', COLORS['action_play']),
            'error': ('✗', COLORS['action_stop'])
        }
        icon, color = icons.get(status, ('○', COLORS['text_secondary']))
        self.status_label.configure(text=icon, text_color=color)

    def toggle_preview(self):
        if self.is_playing:
            self.preview_btn.configure(text="▶", fg_color=COLORS['bg_secondary'])
            self.is_playing = False
            if self.on_preview:
                self.on_preview(None, stop=True)
        else:
            self.preview_btn.configure(text="⏹", fg_color=COLORS['action_stop'])
            self.is_playing = True
            if self.on_preview:
                search_query = f"{self.track_data.get('artist', '')} {self.track_data['title']} audio"
                self.on_preview(search_query, callback=self.on_preview_complete)
                
    def on_preview_complete(self):
        self.preview_btn.configure(text="▶", fg_color=COLORS['bg_secondary'])
        self.is_playing = False
        
    def stop_playing(self):
        self.preview_btn.configure(text="▶", fg_color=COLORS['bg_secondary'])
        self.is_playing = False


class DUKATOR:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("DUKATOR - Underground Music Downloader")
        self.root.minsize(850, 650)
        
        # Icono de la ventana (nota musical)
        try:
            _ico_candidates = [
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "dukator.ico"),
                os.path.join(os.path.dirname(sys.executable), "dukator.ico"),
            ]
            if getattr(sys, 'frozen', False):
                _ico_candidates.insert(0, os.path.join(os.path.dirname(sys.executable), "dukator.ico"))
            for _ico in _ico_candidates:
                if os.path.exists(_ico):
                    self.root.iconbitmap(_ico)
                    break
        except Exception:
            pass
        
        # Detectar resolucion de pantalla y centrar
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        width = min(int(screen_w * 0.8), 1300)
        height = min(int(screen_h * 0.8), 850)
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        self.root.configure(fg_color=COLORS['bg_main'])
        
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        self.app_dir = self.get_app_dir()
        self.ffmpeg_path = self.find_ffmpeg()
        
        self.download_path = os.path.join(os.path.expanduser("~"), "Downloads", "DUKATOR")
        os.makedirs(self.download_path, exist_ok=True)
        
        # Cargar configuracion
        self.config_file = os.path.join(self.app_dir, "dukator_config.json")
        self.load_config()
        
        self.musicbrainz_token = ""
        self.current_tracks = []
        self.track_cards = []
        self.selected_tracks = []
        self.download_history = []
        self.quality = "320"
        self.current_album_info = {}
        self.current_cover_art = None
        
        self.audio_player = AudioPlayer(status_callback=self.update_player_status)
        
        self.setup_ui()
        self.update_selection_count()
        
    def get_app_dir(self):
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.abspath(__file__))
        
    def find_ffmpeg(self):
        import platform
        is_windows = platform.system() == 'Windows'
        
        # En Windows, buscar ffmpeg.exe en el directorio de la app
        if is_windows:
            ffmpeg_exe = os.path.join(self.app_dir, "ffmpeg.exe")
            if os.path.exists(ffmpeg_exe):
                return ffmpeg_exe
        else:
            # En Mac/Linux, buscar ffmpeg en PATH o en directorio de la app
            ffmpeg_path = os.path.join(self.app_dir, "ffmpeg")
            if os.path.exists(ffmpeg_path):
                return ffmpeg_path
            # También verificar si está en /usr/local/bin o ~/homebrew
            for p in ["/usr/local/bin", "/opt/homebrew/bin", os.path.expanduser("~/homebrew/bin")]:
                if os.path.exists(os.path.join(p, "ffmpeg")):
                    return os.path.join(p, "ffmpeg")
        
        return "ffmpeg"
    
    def load_config(self):
        default_config = {
            'quality': '320',
            'download_path': self.download_path,
            'history': []
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.quality = config.get('quality', '320')
                    if config.get('download_path'):
                        self.download_path = config['download_path']
                    self.download_history = config.get('history', [])
            else:
                self.quality = '320'
                self.download_history = []
        except:
            self.quality = '320'
            self.download_history = []
    
    def save_config(self):
        config = {
            'quality': self.quality,
            'download_path': self.download_path,
            'history': self.download_history[-50:]  # Keep last 50
        }
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except:
            pass
    
    def on_quality_change(self, value):
        self.quality = value
        self.save_config()
        
    def setup_ui(self):
        self.setup_header()
        self.setup_main_content()
        self.setup_player_bar()
        self.setup_status_bar()
        
    def setup_header(self):
        header_frame = ctk.CTkFrame(self.root, fg_color=COLORS['bg_secondary'], corner_radius=0, height=60)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(1, weight=1)
        
        logo_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=20, pady=10)
        
        title_label = ctk.CTkLabel(
            logo_frame,
            text="🎵 DUKATOR",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLORS['text_primary']
        )
        title_label.pack(side="left")
        
        subtitle_label = ctk.CTkLabel(
            logo_frame,
            text="  Underground Music Downloader",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary']
        )
        subtitle_label.pack(side="left", padx=(10, 0))
        
        settings_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        settings_frame.grid(row=0, column=2, padx=20, pady=10)
        
        ctk.CTkLabel(
            settings_frame,
            text="Calidad:",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_secondary']
        ).pack(side="left", padx=(0, 5))
        
        self.quality_var = ctk.StringVar(value=self.quality)
        quality_menu = ctk.CTkOptionMenu(
            settings_frame,
            values=["192", "256", "320"],
            variable=self.quality_var,
            width=80,
            height=28,
            fg_color=COLORS['bg_card'],
            button_color=COLORS['accent'],
            button_hover_color=COLORS['accent_hover'],
            dropdown_fg_color=COLORS['bg_card'],
            dropdown_hover_color=COLORS['accent'],
            corner_radius=6,
            command=self.on_quality_change
        )
        quality_menu.pack(side="left", padx=(0, 15))
        quality_menu.set(self.quality)
        
        folder_btn = StyledButton(
            settings_frame,
            text="📁 Carpeta",
            width=90,
            height=28,
            style="secondary",
            command=self.change_path
        )
        folder_btn.pack(side="left")
        
    def setup_main_content(self):
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        self.setup_search_section(main_frame)
        self.setup_tabs(main_frame)
        
        # Overlay de progreso
        self.progress_overlay = ProgressOverlay(self.root)
        
    def setup_search_section(self, parent):
        search_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'], corner_radius=12, border_width=1, border_color=COLORS['border'])
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        search_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            search_frame,
            text="🔍",
            font=ctk.CTkFont(size=18),
            text_color=COLORS['text_secondary']
        ).grid(row=0, column=0, padx=15, pady=12)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Buscar álbum o artista...",
            font=ctk.CTkFont(size=14),
            height=36,
            fg_color=COLORS['bg_secondary'],
            border_color=COLORS['border'],
            corner_radius=8
        )
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=12)
        self.search_entry.bind("<Return>", lambda e: self.search_album())
        
        search_btn = StyledButton(
            search_frame,
            text="Buscar",
            width=90,
            height=36,
            style="primary"
        )
        search_btn.grid(row=0, column=2, padx=15, pady=12)
        search_btn.configure(command=self.search_album)
        
    def setup_tabs(self, parent):
        self.tabview = ctk.CTkTabview(
            parent,
            fg_color=COLORS['bg_card'],
            segmented_button_fg_color=COLORS['bg_secondary'],
            segmented_button_selected_color=COLORS['accent'],
            segmented_button_selected_hover_color=COLORS['accent_hover'],
            segmented_button_unselected_color=COLORS['bg_secondary'],
            segmented_button_unselected_hover_color=COLORS['border_light'],
            corner_radius=12,
            border_width=1,
            border_color=COLORS['border']
        )
        self.tabview.grid(row=1, column=0, sticky="nsew")
        self.tabview.grid_columnconfigure(0, weight=1)
        self.tabview.grid_rowconfigure(0, weight=1)
        
        self.tab_album = self.tabview.add("💿 Álbumes")
        self.tab_songs = self.tabview.add("🎵 Canciones")
        self.tab_direct = self.tabview.add("🔗 Directo")
        self.tab_local = self.tabview.add("📂 Local")
        
        self.setup_album_tab()
        self.setup_songs_tab()
        self.setup_direct_tab()
        self.setup_local_tab()
        
    def setup_album_tab(self):
        self.tab_album.grid_columnconfigure(0, weight=1)
        self.tab_album.grid_rowconfigure(1, weight=0, minsize=280)
        self.tab_album.grid_rowconfigure(2, weight=1)
        
        results_header = ctk.CTkFrame(self.tab_album, fg_color="transparent")
        results_header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(
            results_header,
            text="Álbumes encontrados:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS['text_secondary']
        ).pack(side="left")
        
        self.album_results_frame = ctk.CTkScrollableFrame(
            self.tab_album,
            fg_color=COLORS['bg_secondary'],
            corner_radius=8,
            height=280
        )
        self.album_results_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.album_results_frame.grid_columnconfigure(0, weight=1)
        
        tracks_container = ctk.CTkFrame(self.tab_album, fg_color="transparent")
        tracks_container.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        tracks_container.grid_columnconfigure(0, weight=1)
        tracks_container.grid_rowconfigure(1, weight=1)
        
        tracks_header = ctk.CTkFrame(tracks_container, fg_color="transparent")
        tracks_header.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        ctk.CTkLabel(
            tracks_header,
            text="Canciones:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS['text_secondary']
        ).pack(side="left")
        
        self.selection_count_label = ctk.CTkLabel(
            tracks_header,
            text="0 seleccionadas",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['accent']
        )
        self.selection_count_label.pack(side="right", padx=10)
        
        self.tracks_list_frame = ctk.CTkScrollableFrame(
            tracks_container,
            fg_color=COLORS['bg_secondary'],
            corner_radius=8
        )
        self.tracks_list_frame.grid(row=1, column=0, sticky="nsew")
        self.tracks_list_frame.grid_columnconfigure(0, weight=1)
        
        controls_frame = ctk.CTkFrame(self.tab_album, fg_color="transparent")
        controls_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        
        StyledButton(
            controls_frame,
            text="✓ Seleccionar Todas",
            width=140,
            height=32,
            style="secondary",
            command=self.select_all
        ).pack(side="left", padx=(0, 10))
        
        StyledButton(
            controls_frame,
            text="✗ Deseleccionar Todas",
            width=150,
            height=32,
            style="secondary",
            command=self.deselect_all
        ).pack(side="left", padx=(0, 10))
        
        self.download_btn = StyledButton(
            controls_frame,
            text="⬇️ Descargar Seleccionadas",
            width=180,
            height=32,
            style="play",
            command=self.download_selected
        )
        self.download_btn.pack(side="left", padx=(10, 0))
        
    def setup_songs_tab(self):
        self.tab_songs.grid_columnconfigure(0, weight=1)
        self.tab_songs.grid_rowconfigure(1, weight=1)
        
        # Buscador
        search_frame = ctk.CTkFrame(self.tab_songs, fg_color="transparent")
        search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(
            search_frame,
            text="Buscar canción:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS['text_secondary']
        ).pack(anchor="w")
        
        search_input_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_input_frame.pack(fill="x", pady=(5, 0))
        
        self.song_search_entry = ctk.CTkEntry(
            search_input_frame,
            placeholder_text="Nombre de la canción o artista...",
            fg_color=COLORS['bg_secondary'],
            border_color=COLORS['border'],
            text_color=COLORS['text_primary'],
            height=40,
            font=ctk.CTkFont(size=13)
        )
        self.song_search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.song_search_entry.bind("<Return>", lambda e: self.search_songs())
        
        self.songs_search_btn = ctk.CTkButton(
            search_input_frame,
            text="🔍 Buscar",
            fg_color=COLORS['accent'],
            hover_color=COLORS['accent_hover'],
            height=40,
            command=self.search_songs
        )
        self.songs_search_btn.pack(side="left")
        
        # Opciones de fuente
        sources_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        sources_frame.pack(anchor="w", pady=(10, 0))
        
        ctk.CTkLabel(
            sources_frame,
            text="Buscar en:",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_secondary']
        ).pack(side="left")
        
        self.song_source_var = ctk.StringVar(value="all")
        
        for source, label in [("youtube", "YouTube"), ("soundcloud", "SoundCloud"), 
                              ("audiomack", "Audiomack"), ("all", "Todas")]:
            ctk.CTkRadioButton(
                sources_frame,
                text=label,
                variable=self.song_source_var,
                value=source,
                text_color=COLORS['text_secondary']
            ).pack(side="left", padx=10)
        
        # Resultados
        self.songs_results_frame = ctk.CTkScrollableFrame(
            self.tab_songs,
            fg_color=COLORS['bg_secondary'],
            corner_radius=8
        )
        self.songs_results_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.songs_results_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            self.songs_results_frame,
            text="Resultados:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS['text_secondary']
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        self.song_results_container = ctk.CTkFrame(self.songs_results_frame, fg_color="transparent")
        self.song_results_container.grid(row=1, column=0, sticky="ew")
        self.song_results_container.grid_columnconfigure(0, weight=1)
        
    def search_songs(self):
        query = self.song_search_entry.get().strip()
        if not query:
            return
            
        source = self.song_source_var.get()
        
        # Limpiar resultados anteriores
        for widget in self.song_results_container.winfo_children():
            widget.destroy()
            
        ctk.CTkLabel(
            self.song_results_container,
            text=f"🔍 Buscando en {source}...",
            text_color=COLORS['text_secondary']
        ).grid(row=0, column=0, pady=10)
        
        # Buscar en background
        def safe_print(msg):
            try:
                print(msg)
            except UnicodeEncodeError:
                print(msg.encode('ascii', errors='replace').decode('ascii'))

        def do_search():
            try:
                sources_to_search = []
                if source == "all":
                    sources_to_search = ["youtube", "soundcloud", "audiomack"]  # Bandcamp excluido (403)
                else:
                    sources_to_search = [source]
                
                all_results = []
                
                for src in sources_to_search:
                    try:
                        # YouTube - usar yt-dlp nativo (más robusto)
                        if src == "youtube":
                            try:
                                ydl_opts = {
                                    'quiet': True, 
                                    'no_warnings': True, 
                                    'extract_flat': True,
                                    'skip_download': True,
                                    'ignoreerrors': True,
                                }
                                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                                    results = ydl.extract_info(f"ytsearch10:{query}", download=False)
                                    if results and 'entries' in results:
                                        for entry in list(results['entries'])[:10]:
                                            if not entry:
                                                continue
                                            vid_id = entry.get('id', '')
                                            title = entry.get('title', '').strip()
                                            # Descartar entradas sin título o sin ID válido
                                            if not title or not vid_id:
                                                continue
                                            # Construir URL limpia (sin list= ni parámetros extra)
                                            clean_url = f"https://www.youtube.com/watch?v={vid_id}"
                                            all_results.append({
                                                'title': title[:60],
                                                'url': clean_url,
                                                'source': 'youtube',
                                                'duration': entry.get('duration', 0) or 0,
                                                'uploader': entry.get('uploader', '') or entry.get('channel', '')
                                            })
                            except Exception as e:
                                safe_print(f"[YouTube] Error: {str(e)[:50]}")
                        
                        # SoundCloud - formato correcto scsearch
                        elif src == "soundcloud":
                            try:
                                ydl_opts = {
                                    'quiet': True, 
                                    'no_warnings': True, 
                                    'extract_flat': True,
                                    'skip_download': True,
                                    'ignoreerrors': True,
                                }
                                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                                    results = ydl.extract_info(f"scsearch10:{query}", download=False)
                                    if results and 'entries' in results:
                                        for entry in list(results['entries'])[:10]:
                                            if not entry:
                                                continue
                                            title = entry.get('title', '').strip()
                                            if not title:
                                                continue
                                            # webpage_url es la URL real de soundcloud.com
                                            # entry.get('url') devuelve URL interna de API (inútil)
                                            sc_url = entry.get('webpage_url') or entry.get('url', '')
                                            if not sc_url or sc_url.startswith('https://api.soundcloud.com'):
                                                # Construir URL desde permalink si está disponible
                                                permalink = entry.get('permalink_url', '')
                                                sc_url = permalink if permalink else sc_url
                                            if not sc_url:
                                                continue
                                            all_results.append({
                                                'title': title[:60],
                                                'url': sc_url,
                                                'source': 'soundcloud',
                                                'duration': entry.get('duration', 0) or 0,
                                                'uploader': entry.get('uploader', '') or ''
                                            })
                            except Exception as e:
                                print(f"[SoundCloud] Error: {str(e)[:50]}")
                                
                        # Bandcamp - DESACTIVADO temporalmente (API devuelve 403 Forbidden)
                        # Bandcamp tiene protección anti-scraping activa
                        elif src == "bandcamp":
                            # No disponible temporalmente - mostrar mensaje en UI
                            print("[Bandcamp] No disponible temporalmente (403 Forbidden)")
                            # Añadir resultado dummy para mostrar mensaje
                            all_results.append({
                                'title': '[Bandcamp no disponible]',
                                'url': '',
                                'source': 'bandcamp',
                                'duration': 0,
                                'uploader': 'API bloqueada'
                            })
                        
                        # Audiomack - API pública oficial
                        elif src == "audiomack":
                            try:
                                api_url = f"https://api.audiomack.com/v1/search"
                                params = {
                                    'q': query,
                                    'type': 'song',
                                    'limit': 10,
                                }
                                headers = {
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                                    'Accept': 'application/json',
                                }
                                response = requests.get(api_url, params=params, headers=headers, timeout=15)
                                am_results = []
                                if response.status_code == 200:
                                    try:
                                        data = response.json()
                                        items = data.get('results', {}).get('song', {}).get('data', [])
                                        for item in items[:10]:
                                            slug = item.get('url_slug', '')
                                            artist_slug = item.get('artist', {}).get('url_slug', '') if isinstance(item.get('artist'), dict) else ''
                                            if slug and artist_slug:
                                                full_url = f"https://audiomack.com/{artist_slug}/song/{slug}"
                                                am_results.append({
                                                    'title': item.get('title', query)[:60],
                                                    'url': full_url,
                                                    'source': 'audiomack',
                                                    'duration': int(item.get('duration', 0) or 0),
                                                    'uploader': item.get('artist', {}).get('name', '') if isinstance(item.get('artist'), dict) else ''
                                                })
                                    except Exception:
                                        pass
                                # Fallback: yt-dlp search si la API no devuelve nada
                                if not am_results:
                                    try:
                                        ydl_opts_am = {
                                            'quiet': True,
                                            'no_warnings': True,
                                            'extract_flat': True,
                                            'skip_download': True,
                                            'ignoreerrors': True,
                                        }
                                        with yt_dlp.YoutubeDL(ydl_opts_am) as ydl:
                                            res = ydl.extract_info(f"ytsearch5:{query} audiomack", download=False)
                                            if res and 'entries' in res:
                                                for entry in list(res['entries'])[:5]:
                                                    if entry:
                                                        u = entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id','')}"
                                                        am_results.append({
                                                            'title': entry.get('title', query)[:60],
                                                            'url': u,
                                                            'source': 'audiomack',
                                                            'duration': entry.get('duration', 0) or 0,
                                                            'uploader': entry.get('uploader', '') or ''
                                                        })
                                    except Exception:
                                        pass
                                all_results.extend(am_results)
                            except Exception as e:
                                print(f"[Audiomack] Error: {str(e)[:50]}")
                                
                    except Exception as e:
                        print(f"[{src}] Error: {str(e)[:80]}")
                
                # Mostrar resultados en UI - usar list() para copiar valores y evitar closure issues
                results_copy = list(all_results)
                self.root.after(0, lambda r=results_copy: self.display_song_results(r))
                
            except Exception as e:
                self.root.after(0, lambda: self.update_status(f"Error: {str(e)}"))
        
        threading.Thread(target=do_search, daemon=True).start()
        
    def display_song_results(self, results):
        # Debug: mostrar qué llega
        print(f"[DEBUG] display_song_results recibió {len(results)} resultados")
        for r in results[:3]:
            print(f"  - {r.get('source', '?')}: {r.get('title', '?')[:40]}")
        
        for widget in self.song_results_container.winfo_children():
            widget.destroy()
            
        if not results:
            ctk.CTkLabel(
                self.song_results_container,
                text="No se encontraron resultados",
                text_color=COLORS['text_secondary']
            ).grid(row=0, column=0, pady=10)
            return
            
        for idx, result in enumerate(results):
            row = idx
            result_frame = ctk.CTkFrame(self.song_results_container, fg_color=COLORS['bg_card'], corner_radius=8)
            result_frame.grid(row=row, column=0, sticky="ew", pady=5)
            result_frame.grid_columnconfigure(1, weight=1)
            
            # Fuente
            source_label = ctk.CTkLabel(
                result_frame,
                text=result['source'].upper(),
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=COLORS['accent'],
                width=80
            )
            source_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
            
            # Info
            title = result['title'][:60]
            duration = int(result.get('duration', 0))
            mins = duration // 60 if duration else 0
            secs = duration % 60 if duration else 0
            duration_str = f"{mins}:{secs:02d}" if duration else ""
            
            info_frame = ctk.CTkFrame(result_frame, fg_color="transparent")
            info_frame.grid(row=0, column=1, sticky="ew", padx=5)
            
            ctk.CTkLabel(
                info_frame,
                text=title,
                font=ctk.CTkFont(size=12),
                text_color=COLORS['text_primary'],
                anchor="w"
            ).pack(fill="x")
            
            if result.get('uploader'):
                ctk.CTkLabel(
                    info_frame,
                    text=result['uploader'][:40],
                    font=ctk.CTkFont(size=10),
                    text_color=COLORS['text_secondary'],
                    anchor="w"
                ).pack(fill="x")
            
            # Botones
            btn_frame = ctk.CTkFrame(result_frame, fg_color="transparent")
            btn_frame.grid(row=0, column=2, padx=10)
            
            # Preview button
            preview_btn = ctk.CTkButton(
                btn_frame,
                text="▶",
                width=35,
                height=35,
                fg_color=COLORS['bg_secondary'],
                hover_color=COLORS['accent_hover'],
                command=lambda r=result: self.preview_song(r['url'])
            )
            preview_btn.pack(side="left", padx=2)
            
            # Download button
            download_btn = ctk.CTkButton(
                btn_frame,
                text="⬇",
                width=35,
                height=35,
                fg_color=COLORS['action_play'],
                hover_color=COLORS['accent_hover'],
                command=lambda r=result: self.download_single_song(r)
            )
            download_btn.pack(side="left", padx=2)
            
    def preview_song(self, url):
        if not url:
            return
        self.update_status(f"Cargando preview...")
        
        def do_preview():
            try:
                import yt_dlp
                temp_dir = tempfile.gettempdir()
                temp_file = os.path.join(temp_dir, f"preview_{int(time.time())}")
                
                ydl_opts = {
                    'format': 'worstaudio/worst',  # Mas rapido
                    'outtmpl': temp_file,
                    'quiet': True,
                    'no_warnings': True,
                    'duration_limit': 35,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                # Buscar archivo descargado
                for f in os.listdir(temp_dir):
                    if f.startswith('preview_'):
                        filepath = os.path.join(temp_dir, f)
                        if PYGAME_AVAILABLE:
                            pygame.mixer.music.load(filepath)
                            pygame.mixer.music.play()
                            self.root.after(0, lambda: self.update_status(f"Reproduciendo preview..."))
                        break
                        
            except Exception as e:
                self.root.after(0, lambda: self.update_status(f"Error preview: {str(e)[:40]}"))
        
        threading.Thread(target=do_preview, daemon=True).start()
        
    def download_single_song(self, result):
        url = result['url']
        title = result['title']
        
        output_folder = os.path.join(self.download_path, "Singles")
        os.makedirs(output_folder, exist_ok=True)
        
        self.update_status(f"Descargando: {title}")
        
        def do_download():
            # Obtener calidad configurada
            quality = self.quality_var.get()
            # Obtener ubicación de ffmpeg
            ffmpeg_dir = os.path.dirname(self.ffmpeg_path) if self.ffmpeg_path and os.path.dirname(self.ffmpeg_path) else None
            
            # Reintentos
            for attempt in range(3):
                try:
                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
                        'quiet': True,
                        'no_warnings': True,
                        # FFmpeg location
                        'ffmpeg_location': ffmpeg_dir,
                        # Headers para evitar bloqueos
                        'http_headers': {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        },
                        'retries': 5,
                        'fragment_retries': 5,
                        'socket_timeout': 120,
                        # Opciones para YouTube
                        'extractor_args': {
                            'youtube': {
                                'player_client': ['android', 'web'],
                            }
                        },
                        # Convertir a MP3 con calidad configurada
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': quality,
                        }],
                    }
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])
                        
                    self.add_to_history(title, url, result.get('source', 'unknown'))
                    self.root.after(0, lambda t=title: self.update_status(f"✓ Descargado: {t}"))
                    self.root.after(0, lambda t=title: messagebox.showinfo("Info", f"Descargado: {t}"))
                    return
                        
                except Exception as e:
                    error_msg = str(e)
                    if attempt < 2:
                        time.sleep(2 + attempt)
                    else:
                        self.root.after(0, lambda err=error_msg: self.update_status(f"✗ Error: {err[:50]}"))
                
        threading.Thread(target=do_download, daemon=True).start()
        
    def add_to_history(self, title, url, source):
        if not hasattr(self, 'download_history'):
            self.download_history = []
            
        self.download_history.append({
            'title': title,
            'url': url,
            'source': source,
            'date': time.strftime('%Y-%m-%d %H:%M')
        })
        
        # Guardar en config
        self.save_config()
        
    def setup_direct_tab(self):
        self.tab_direct.grid_columnconfigure(0, weight=1)
        self.tab_direct.grid_rowconfigure(1, weight=1)
        
        info_frame = ctk.CTkFrame(self.tab_direct, fg_color="transparent")
        info_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text="Fuentes soportadas: YouTube • Audiomack • SoundCloud • Vimeo • Mixcloud • Dailymotion • Archive.org • VK • Twitch • Bilibili • Facebook • Instagram • TikTok • Pixabay",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_secondary']
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            info_frame,
            text="Pegar enlaces (uno por línea):",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS['text_secondary']
        ).pack(anchor="w", pady=(5, 0))
        
        self.direct_text = ctk.CTkTextbox(
            self.tab_direct,
            fg_color=COLORS['bg_secondary'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border'],
            font=ctk.CTkFont(size=12)
        )
        self.direct_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        btn_frame = ctk.CTkFrame(self.tab_direct, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        
        StyledButton(
            btn_frame,
            text="⬇️ Descargar Todos",
            width=150,
            height=32,
            style="play",
            command=self.download_direct
        ).pack(side="left")
        
    def setup_player_bar(self):
        player_frame = ctk.CTkFrame(self.root, fg_color=COLORS['bg_secondary'], corner_radius=0, height=70)
        player_frame.grid(row=2, column=0, sticky="ew")
        player_frame.grid_propagate(False)
        player_frame.grid_columnconfigure(1, weight=1)
        
        controls_frame = ctk.CTkFrame(player_frame, fg_color="transparent")
        controls_frame.grid(row=0, column=0, padx=20, pady=15)
        
        self.play_pause_btn = ctk.CTkButton(
            controls_frame,
            text="▶",
            font=ctk.CTkFont(size=16),
            width=40,
            height=40,
            fg_color=COLORS['accent'],
            hover_color=COLORS['accent_hover'],
            corner_radius=20,
            command=self.toggle_play_pause
        )
        self.play_pause_btn.pack(side="left", padx=(0, 10))
        
        self.stop_btn = ctk.CTkButton(
            controls_frame,
            text="⏹",
            font=ctk.CTkFont(size=14),
            width=32,
            height=32,
            fg_color=COLORS['bg_card'],
            hover_color=COLORS['action_stop'],
            corner_radius=16,
            command=self.stop_player
        )
        self.stop_btn.pack(side="left")
        
        track_info_frame = ctk.CTkFrame(player_frame, fg_color="transparent")
        track_info_frame.grid(row=0, column=1, sticky="ew", padx=20, pady=15)
        track_info_frame.grid_columnconfigure(1, weight=1)
        
        self.player_track_label = ctk.CTkLabel(
            track_info_frame,
            text="Sin reproducción",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_primary'],
            anchor="w"
        )
        self.player_track_label.grid(row=0, column=0, sticky="ew")
        
        # Tiempo actual
        self.current_time_label = ctk.CTkLabel(
            track_info_frame,
            text="0:00",
            font=ctk.CTkFont(size=10),
            text_color=COLORS['text_secondary']
        )
        self.current_time_label.grid(row=1, column=0, sticky="w")
        
        self.progress_slider = ctk.CTkSlider(
            track_info_frame,
            from_=0,
            to=30,
            number_of_steps=300,
            fg_color=COLORS['progress_bg'],
            progress_color=COLORS['accent'],
            button_color=COLORS['text_primary'],
            button_hover_color=COLORS['accent_hover'],
            height=8
        )
        self.progress_slider.grid(row=1, column=1, sticky="ew", padx=10)
        self.progress_slider.set(0)
        
        # Tiempo total
        self.total_time_label = ctk.CTkLabel(
            track_info_frame,
            text="0:30",
            font=ctk.CTkFont(size=10),
            text_color=COLORS['text_secondary']
        )
        self.total_time_label.grid(row=1, column=2, sticky="e")
        
        volume_frame = ctk.CTkFrame(player_frame, fg_color="transparent")
        volume_frame.grid(row=0, column=2, padx=20, pady=15)
        
        ctk.CTkLabel(
            volume_frame,
            text="🔊",
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text_secondary']
        ).pack(side="left")
        
        self.volume_slider = ctk.CTkSlider(
            volume_frame,
            from_=0,
            to=1,
            number_of_steps=100,
            width=100,
            fg_color=COLORS['progress_bg'],
            progress_color=COLORS['accent'],
            button_color=COLORS['text_primary'],
            button_hover_color=COLORS['accent_hover'],
            command=self.on_volume_change
        )
        self.volume_slider.pack(side="left", padx=10)
        self.volume_slider.set(0.7)
        
    def setup_status_bar(self):
        status_frame = ctk.CTkFrame(self.root, fg_color=COLORS['bg_main'], corner_radius=0)
        status_frame.grid(row=3, column=0, sticky="ew")
        status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Listo",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_secondary'],
            anchor="w"
        )
        self.status_label.grid(row=0, column=0, sticky="w", padx=15, pady=8)
        
        self.progress_bar = ctk.CTkProgressBar(
            status_frame,
            fg_color=COLORS['progress_bg'],
            progress_color=COLORS['accent'],
            corner_radius=4,
            width=300
        )
        self.progress_bar.grid(row=0, column=1, sticky="e", padx=15, pady=8)
        self.progress_bar.set(0)
        
    def toggle_play_pause(self):
        if self.audio_player.is_playing and not self.audio_player.is_paused:
            self.audio_player.pause()
            self.play_pause_btn.configure(text="▶")
        elif self.audio_player.is_paused:
            self.audio_player.resume()
            self.play_pause_btn.configure(text="⏸")
            
    def stop_player(self):
        self.audio_player.stop()
        self.play_pause_btn.configure(text="▶", fg_color=COLORS['accent'])
        self.progress_slider.set(0)
        try:
            self.current_time_label.configure(text="0:00")
        except:
            pass
        self.player_track_label.configure(text="Sin reproducción")
        for card in self.track_cards:
            card.stop_playing()
            
    def on_progress_seek(self, event=None):
        #pygame.mixer no soporta seek, pero podemos reiniciar desde donde seclickó
        #Por ahora solo actualizamos el tiempo visual
        try:
            new_time = self.progress_slider.get()
            current = self.current_time_label.cget("text")
            self.current_time_label.configure(text=self.format_time(int(new_time)))
        except:
            pass
        
    def on_volume_change(self, value):
        self.audio_player.set_volume(value)
        
    def update_player_status(self, text):
        self.player_track_label.configure(text=text[:60])
        self.root.update_idletasks()
        
    def handle_preview(self, search_query, callback=None, stop=False):
        if stop:
            self.audio_player.stop()
            self.play_pause_btn.configure(text="▶", fg_color=COLORS['accent'])
            self.progress_slider.set(0)
            return
            
        for card in self.track_cards:
            if card.is_playing:
                card.stop_playing()
        
        # Callback para actualizar slider de progreso
        def update_progress(current, total):
            self.root.after(0, lambda c=current, t=total: self.update_progress_slider(c, t))
        
        self.audio_player.play_preview(search_query, callback, progress_callback=update_progress)
        self.play_pause_btn.configure(text="⏸", fg_color=COLORS['action_play'])
        
    def update_progress_slider(self, current, total):
        try:
            if total > 0 and current <= total:
                self.progress_slider.set(current)
        except:
            pass
        
    def format_time(self, seconds):
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins}:{secs:02d}"
        
    def search_album(self):
        query = self.search_entry.get().strip()
        if not query:
            return
            
        self.update_status("🔍 Buscando en MusicBrainz...")
        
        for widget in self.album_results_frame.winfo_children():
            widget.destroy()
            
        for widget in self.tracks_list_frame.winfo_children():
            widget.destroy()
            
        self.current_tracks = []
        self.track_cards = []
        self.update_selection_count()
        
        try:
            url = "https://musicbrainz.org/ws/2/release/"
            params = {
                "query": query,
                "fmt": "json",
                "limit": 25
            }
            headers = {"User-Agent": "DUKATOR/2.0 (dukator@email.com)"}
            
            response = requests.get(url, params=params, headers=headers, timeout=30)
            data = response.json()
            
            if "releases" not in data or not data["releases"]:
                self.update_status("No se encontraron resultados")
                return
                
            for release in data["releases"]:
                artist_credit = release.get('artist-credit', [{}])
                artist_name = artist_credit[0].get('artist', {}).get('name', 'Unknown') if artist_credit else 'Unknown'
                
                release_text = f"{artist_name} - {release.get('title', 'Unknown')}"
                if release.get('date'):
                    release_text += f" ({release['date'][:4]})"
                if release.get('country'):
                    release_text += f" [{release.get('country')}]"
                    
                btn = StyledButton(
                    self.album_results_frame,
                    text=release_text,
                    anchor="w",
                    height=32,
                    style="secondary"
                )
                btn.pack(pady=3, fill="x")
                btn.configure(command=lambda r=release: self.load_tracks(r))
                
            self.update_status(f"Encontrados {len(data['releases'])} álbumes")
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
            
    def load_tracks(self, release):
        for widget in self.tracks_list_frame.winfo_children():
            widget.destroy()
            
        self.current_tracks = []
        self.track_cards = []
        
        release_id = release.get('id')
        if not release_id:
            return
            
        self.update_status("Cargando canciones...")
        
        try:
            url = f"https://musicbrainz.org/ws/2/release/{release_id}"
            params = {"fmt": "json", "inc": "recordings"}
            headers = {"User-Agent": "DUKATOR/2.0 (dukator@email.com)"}
            
            response = requests.get(url, params=params, headers=headers, timeout=30)
            data = response.json()
            
            artist_credit = release.get('artist-credit', [{}])
            artist_name = artist_credit[0].get('artist', {}).get('name', 'Unknown') if artist_credit else 'Unknown'
            album_title = release.get('title', 'Unknown')
            album_year = release.get('date', '')[:4] if release.get('date') else ''
            
            self.current_album_info = {
                'artist': artist_name,
                'album': album_title,
                'year': album_year,
                'release_id': release_id
            }
            
            self.current_cover_art = CoverArtFetcher.get_cover(release_id)
            
            tracks = data.get('media', [{}])[0].get('tracks', [])
            
            for track in tracks:
                track_num = track.get('position', 0)
                track_title = track.get('title', 'Unknown')
                duration_ms = track.get('length', 0)
                
                track_data = {
                    'number': track_num,
                    'title': track_title,
                    'duration_ms': duration_ms,
                    'selected': ctk.BooleanVar(value=True),
                    'artist': artist_name
                }
                self.current_tracks.append(track_data)
                
                card = TrackCard(
                    self.tracks_list_frame,
                    track_data,
                    on_preview=self.handle_preview
                )
                card.pack(pady=4, fill="x")
                self.track_cards.append(card)
                
                track_data['selected'].trace_add('write', self.update_selection_count)
                
            self.update_selection_count()
            self.update_status(f"Cargadas {len(self.current_tracks)} canciones")
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
            
    def update_selection_count(self, *args):
        count = sum(1 for t in self.current_tracks if t['selected'].get())
        total = len(self.current_tracks)
        self.selection_count_label.configure(text=f"{count}/{total} seleccionadas")
        
    def select_all(self):
        for track in self.current_tracks:
            track['selected'].set(True)
            
    def deselect_all(self):
        for track in self.current_tracks:
            track['selected'].set(False)
            
    def change_path(self):
        folder = filedialog.askdirectory(initialdir=self.download_path)
        if folder:
            self.download_path = folder
            self.update_status(f"Carpeta: {self.download_path}")
            self.scan_folder()
    
    def setup_local_tab(self):
        self.tab_local.grid_columnconfigure(0, weight=1)
        self.tab_local.grid_rowconfigure(1, weight=1)
        
        header = ctk.CTkFrame(self.tab_local, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(
            header,
            text="Archivos de audio en la carpeta:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS['text_secondary']
        ).pack(side="left")
        
        scan_btn = ctk.CTkButton(
            header,
            text="🔄 Actualizar",
            width=100,
            height=28,
            fg_color=COLORS['bg_secondary'],
            command=self.scan_folder
        )
        scan_btn.pack(side="right", padx=5)
        
        self.local_results_frame = ctk.CTkScrollableFrame(
            self.tab_local,
            fg_color=COLORS['bg_secondary'],
            corner_radius=8
        )
        self.local_results_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        self.local_files = []
        self.scan_folder()
    
    def scan_folder(self):
        if not hasattr(self, 'local_results_frame'):
            return
            
        for widget in self.local_results_frame.winfo_children():
            widget.destroy()
        
        audio_extensions = {'.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac', '.wma'}
        audio_files = []
        
        try:
            for f in os.listdir(self.download_path):
                ext = os.path.splitext(f.lower())[1]
                if ext in audio_extensions:
                    full_path = os.path.join(self.download_path, f)
                    audio_files.append({
                        'title': os.path.splitext(f)[0],
                        'file': full_path,
                        'ext': ext.upper()[1:],
                        'size': os.path.getsize(full_path)
                    })
        except Exception as e:
            self.update_status(f"Error escaneando carpeta: {str(e)[:50]}")
            return
        
        self.local_files = audio_files
        
        if not audio_files:
            ctk.CTkLabel(
                self.local_results_frame,
                text="No se encontraron archivos de audio",
                text_color=COLORS['text_muted']
            ).pack(pady=20)
            return
        
        for idx, f in enumerate(audio_files):
            size_mb = f['size'] / (1024 * 1024)
            result_frame = ctk.CTkFrame(self.local_results_frame, fg_color=COLORS['bg_card'], corner_radius=8)
            result_frame.pack(fill="x", pady=3)
            
            ctk.CTkLabel(
                result_frame,
                text=f['ext'],
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=COLORS['accent'],
                width=40
            ).pack(side="left", padx=8)
            
            info_frame = ctk.CTkFrame(result_frame, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True, padx=5)
            
            ctk.CTkLabel(
                info_frame,
                text=f['title'][:60],
                font=ctk.CTkFont(size=11),
                text_color=COLORS['text_primary'],
                anchor="w"
            ).pack(fill="x")
            
            ctk.CTkLabel(
                info_frame,
                text=f"{size_mb:.1f} MB",
                font=ctk.CTkFont(size=9),
                text_color=COLORS['text_muted'],
                anchor="w"
            ).pack(fill="x")
            
            btn_frame = ctk.CTkFrame(result_frame, fg_color="transparent")
            btn_frame.pack(side="right", padx=8)
            
            play_btn = ctk.CTkButton(
                btn_frame,
                text="▶",
                width=35,
                height=35,
                fg_color=COLORS['bg_secondary'],
                hover_color=COLORS['accent_hover'],
                command=lambda fdata=f: self.play_local_file(fdata['file'])
            )
            play_btn.pack(side="left", padx=2)
        
        self.update_status(f"📂 {len(audio_files)} archivos de audio encontrados")
    
    def play_local_file(self, filepath):
        if not PYGAME_AVAILABLE:
            messagebox.showwarning("Aviso", "pygame no disponible para reproducción")
            return
        
        try:
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play()
            self.update_status(f"▶ Reproduciendo: {os.path.basename(filepath)[:40]}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo reproducir: {str(e)}")
            
    def download_selected(self):
        selected = [t for t in self.current_tracks if t['selected'].get()]
        if not selected:
            messagebox.showwarning("Aviso", "No hay canciones seleccionadas")
            return
            
        threading.Thread(target=self.download_album_tracks, args=(selected,), daemon=True).start()
        
    def download_album_tracks(self, tracks):
        album_info = self.current_album_info
        
        safe_artist = self.sanitize_filename(album_info.get('artist', 'Unknown'))
        safe_album = self.sanitize_filename(album_info.get('album', 'Unknown'))
        folder_name = f"{album_info.get('year', '')} - {safe_album}" if album_info.get('year') else safe_album
        
        output_folder = os.path.join(self.download_path, safe_artist, folder_name)
        os.makedirs(output_folder, exist_ok=True)
        
        # Mostrar overlay
        self.root.after(0, lambda: self.progress_overlay.show())
        
        cover_art = CoverArtFetcher.get_cover(album_info.get('release_id', ''))
        if not cover_art:
            cover_art = self.current_cover_art
        
        total = len(tracks)
        
        for idx, track in enumerate(tracks):
            # Actualizar overlay
            self.root.after(0, lambda i=idx, t=total: self.progress_overlay.update_progress(i+1, t, f"Buscando...", "YouTube"))
            
            # Marcar como descargando
            for card in self.track_cards:
                if card.track_data['title'] == track['title']:
                    card.set_status('downloading')
            
            success = False
            for source_id, source_name, _ in DOWNLOAD_SOURCES:
                self.root.after(0, lambda s=source_name, t=track: self.progress_overlay.update_progress(idx+1, total, f"[{s}] {t['title'][:30]}...", s))
                self.update_status(f"[{source_name}] Buscando: {track['title']}")
                result = self.try_download_from_source(source_id, track, output_folder, idx + 1, cover_art)
                if result:
                    success = True
                    self.update_status(f"✓ [{source_name}] Descargado: {track['title']}")
                    for card in self.track_cards:
                        if card.track_data['title'] == track['title']:
                            card.set_source(source_name)
                            card.set_status('success')
                    break
            if not success:
                self.update_status(f"❌ No encontrado: {track['title']}")
                for card in self.track_cards:
                    if card.track_data['title'] == track['title']:
                        card.set_status('error')
                
            progress = (idx + 1) / total
            self.progress_bar.set(progress)
        
        # Ocultar overlay
        self.root.after(0, lambda: self.progress_overlay.hide())
        self.root.after(0, lambda: self.update_status("✅ Descarga completada"))
        self.root.after(0, lambda: messagebox.showinfo("Info", "Descarga completada"))
        
    def try_download_from_source(self, source, track, output_folder, track_num, cover_art=None):
        try:
            if source == 'youtube':
                return self.download_from_youtube(track, output_folder, track_num, cover_art)
            elif source == 'audiomack':
                return self.download_from_audiomack(track, output_folder, track_num, cover_art)
            elif source == 'soundcloud':
                return self.download_from_soundcloud(track, output_folder, track_num, cover_art)
            elif source == 'vimeo':
                return self.download_from_vimeo(track, output_folder, track_num, cover_art)
            elif source == 'bandcamp':
                return self.download_from_bandcamp(track, output_folder, track_num, cover_art)
            else:
                return self.download_from_any_source(source, track, output_folder, track_num, cover_art)
        except Exception as e:
            return False
        return False
        
    def download_from_any_source(self, source, track, output_folder, track_num, cover_art=None):
        search_query = f"{self.current_album_info.get('artist', '')} {track['title']} audio"
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
                'no_warnings': True,
                'max_downloads': 1,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"{source}search:{search_query}", download=False)
                if info and 'entries' in info:
                    entries = list(info['entries'])
                    if entries and entries[0]:
                        video_url = entries[0].get('webpage_url')
                        if video_url:
                            return self.download_with_ytdlp(video_url, output_folder, track, track_num, source.capitalize(), cover_art)
        except:
            pass
        return False
        
    def download_from_youtube(self, track, output_folder, track_num, cover_art=None):
        search_query = f"{self.current_album_info.get('artist', '')} {track['title']} audio"
        url = "https://www.youtube.com/results"
        params = {"search_query": search_query}
        response = requests.get(url, params=params, timeout=30)
        match = re.search(r'"videoId":"([^"]+)"', response.text)
        if match:
            video_url = f"https://www.youtube.com/watch?v={match.group(1)}"
            return self.download_with_ytdlp(video_url, output_folder, track, track_num, 'YouTube', cover_art)
        return False
        
    def download_from_audiomack(self, track, output_folder, track_num, cover_art=None):
        search_query = f"{self.current_album_info.get('artist', '')} {track['title']}"
        try:
            import yt_dlp
            search_url = f"https://audiomack.com/search?q={url_quote(search_query)}"
            temp_dir = tempfile.gettempdir()
            temp_template = os.path.join(temp_dir, "dukator_search_%(id)s.%(ext)s")
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': temp_template,
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
            }
            
            return False
        except:
            return False
        
    def download_from_soundcloud(self, track, output_folder, track_num, cover_art=None):
        search_query = f"{self.current_album_info.get('artist', '')} {track['title']}"
        try:
            import yt_dlp
            search_url = f"scsearch5:{search_query}"
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'playlist_items': '1',
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(search_url, download=False)
                if info and 'entries' in info:
                    entries = list(info['entries'])
                    if entries and entries[0]:
                        first_entry = entries[0]
                        track_url = first_entry.get('url') or first_entry.get('webpage_url')
                        if track_url:
                            return self.download_with_ytdlp(track_url, output_folder, track, track_num, 'SoundCloud', cover_art)
            return False
        except:
            return False
        
    def download_from_vimeo(self, track, output_folder, track_num, cover_art=None):
        return False
        
    def download_from_bandcamp(self, track, output_folder, track_num, cover_art=None):
        return False
        
    def download_with_ytdlp(self, url, output_folder, track, track_num, source='YouTube', cover_art=None):
        try:
            safe_title = self.sanitize_filename(track['title'])
            output_template = os.path.join(output_folder, f"{track_num:02d} - {safe_title}.%(ext)s")
            
            quality = self.quality_var.get()
            
            # Obtener ubicación de ffmpeg
            ffmpeg_dir = os.path.dirname(self.ffmpeg_path) if self.ffmpeg_path and os.path.dirname(self.ffmpeg_path) else None
            
            ydl_opts = {
                # Priorizar m4a/webm nativos para evitar re-encode innecesario
                'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best',
                'outtmpl': output_template,
                'ffmpeg_location': ffmpeg_dir,
                # Headers para evitar bloqueos
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                },
                # Reintentos razonables
                'retries': 3,
                'fragment_retries': 3,
                'socket_timeout': 30,
                # Descargar fragmentos en paralelo (DASH/HLS mas rapido)
                'concurrent_fragment_downloads': 4,
                # Detectar throttling y reintentar con otro cliente
                'throttledratelimit': 100000,
                # Clientes web estables con acceso a todos los formatos de audio
                'extractor_args': {
                    'youtube': {
                        'player_client': ['web', 'android_vr'],
                    }
                },
                # Convertir a MP3
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': quality,
                }],
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                downloaded_file = output_template.replace('.%(ext)s', '.mp3')
                
                if os.path.exists(downloaded_file):
                    self.add_metadata(downloaded_file, track, track_num, cover_art, source)
                    return True
                    
        except Exception as e:
            self.root.after(0, lambda err=str(e): self.update_status(f"✗ Error descarga: {err[:40]}"))
            
        return False
        
    def add_metadata(self, filepath, track, track_num, cover_art=None, source='YouTube'):
        try:
            audio = MP3(filepath)
            
            if audio.tags is None:
                audio.add_tags()
                
            audio.tags['TIT2'] = TIT2(encoding=3, text=track['title'])
            audio.tags['TPE1'] = TPE1(encoding=3, text=self.current_album_info.get('artist', 'Unknown'))
            audio.tags['TALB'] = TALB(encoding=3, text=self.current_album_info.get('album', 'Unknown'))
            audio.tags['TDRC'] = TDRC(encoding=3, text=self.current_album_info.get('year', ''))
            audio.tags['TRCK'] = TRCK(encoding=3, text=str(track_num))
            
            if cover_art:
                audio.tags['APIC'] = APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3,
                    desc='Cover',
                    data=cover_art
                )
            
            audio.tags['TXXX:SOURCE'] = TXXX(encoding=3, desc='SOURCE', text=source)
            
            audio.save()
            
        except Exception as e:
            self.update_status(f"⚠️ Error metadatos: {str(e)}")
            
    def download_direct(self):
        links = self.direct_text.get("1.0", "end").strip().split('\n')
        links = [l.strip() for l in links if l.strip()]
        
        if not links:
            messagebox.showwarning("Aviso", "No hay enlaces")
            return
            
        threading.Thread(target=self.download_bulk, args=(links,), daemon=True).start()
        
    def clean_youtube_url(self, url):
        """Limpia URLs de YouTube: extrae solo ?v=VIDEO_ID eliminando list=, start_radio=, pp=, etc."""
        try:
            from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
            parsed = urlparse(url)
            # youtu.be/VIDEO_ID → youtube.com/watch?v=VIDEO_ID
            if parsed.netloc in ('youtu.be', 'www.youtu.be'):
                vid_id = parsed.path.lstrip('/')
                if vid_id:
                    return f"https://www.youtube.com/watch?v={vid_id}"
            # youtube.com/watch?v=...&list=...  → solo ?v=
            if 'youtube.com' in parsed.netloc and parsed.path == '/watch':
                params = parse_qs(parsed.query)
                vid_id = params.get('v', [None])[0]
                if vid_id:
                    return f"https://www.youtube.com/watch?v={vid_id}"
        except Exception:
            pass
        return url  # Si no es YouTube o no tiene v=, devolver sin tocar

    def download_bulk(self, links):
        total = len(links)
        quality = self.quality_var.get()
        successful = 0
        failed = 0
        
        for idx, link in enumerate(links):
            # Limpiar URLs de YouTube (eliminar list=, start_radio=, pp=, etc.)
            link = self.clean_youtube_url(link)
            source = SourceDetector.detect(link)
            source_name = SourceDetector.get_display_name(source)
            
            self.root.after(0, lambda s=source_name, i=idx, t=total: self.update_status(f"[{s}] Descargando {i+1}/{t}..."))
            self.root.after(0, lambda i=idx, t=total: self.progress_bar.set(i / t))
            
            # Intentar hasta 3 veces
            success = False
            for attempt in range(3):
                try:
                    output_template = os.path.join(self.download_path, "%(title)s.%(ext)s")
                    
                    # Obtener ubicación de ffmpeg
                    ffmpeg_dir = os.path.dirname(self.ffmpeg_path) if self.ffmpeg_path and os.path.dirname(self.ffmpeg_path) else None
                    
                    ydl_opts = {
                        # Priorizar m4a/webm nativos para evitar re-encode innecesario
                        'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best',
                        'outtmpl': output_template,
                        'quiet': True,
                        'no_warnings': True,
                        'noprogress': True,
                        # FFmpeg location para conversión MP3
                        'ffmpeg_location': ffmpeg_dir,
                        # Headers para evitar bloqueos
                        'http_headers': {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Accept-Language': 'en-us,en;q=0.5',
                        },
                        # Reintentos razonables
                        'retries': 3,
                        'fragment_retries': 3,
                        'skip_unavailable_fragments': True,
                        # Timeout ajustado
                        'socket_timeout': 30,
                        # Descargar fragmentos en paralelo (DASH/HLS mas rapido)
                        'concurrent_fragment_downloads': 4,
                        # Detectar throttling y reintentar con otro cliente
                        'throttledratelimit': 100000,
                        # Clientes web estables con acceso a todos los formatos de audio
                        'extractor_args': {
                            'youtube': {
                                'player_client': ['web', 'android_vr'],
                            }
                        },
                        # Convertir siempre a MP3
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': quality,
                        }],
                        # Mantener mejor calidad de audio
                        'audio_quality': 0,
                    }
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([link])
                        
                    self.root.after(0, lambda s=source_name, i=idx, t=total: self.update_status(f"✓ [{s}] Completado {i+1}/{t}"))
                    success = True
                    successful += 1
                    break
                        
                except Exception as e:
                    error_msg = str(e)
                    if attempt < 2:
                        self.root.after(0, lambda s=source_name, a=attempt: self.update_status(f"[{s}] Reintentando... ({a+2}/3)"))
                        time.sleep(2 + attempt)  # Espera incremental
                    else:
                        self.root.after(0, lambda s=source_name, err=error_msg: self.update_status(f"✗ [{s}] Error: {err[:40]}"))
                        failed += 1
                
            self.root.after(0, lambda i=idx, t=total: self.progress_bar.set((i + 1) / t))

        self.root.after(0, lambda: self.update_status(f"Descarga completada: {successful} OK, {failed} errores"))
        self.root.after(0, lambda: self.progress_bar.set(1))
        self.root.after(0, lambda s=successful, f=failed: messagebox.showinfo("Info", f"Descarga completada\n\n✓ Exitosas: {s}\n✗ Fallidas: {f}"))
        
    def sanitize_filename(self, name):
        invalid = '<>:"/\\|?*'
        for char in invalid:
            name = name.replace(char, '_')
        return name.strip()[:100]
        
    def update_status(self, text):
        self.status_label.configure(text=text)
        self.root.update_idletasks()
        
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = DUKATOR()
    app.run()