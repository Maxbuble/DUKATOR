"""
Gestor de metadatos ID3v2 usando Mutagen
"""

from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TYER, TPE2, TCON, TRCK, APIC
from pathlib import Path
from typing import Optional
import requests
from io import BytesIO

class MetadataManager:
    def __init__(self):
        pass
    
    def tag_track(self,
                  file_path: str,
                  title: str,
                  artist: str,
                  album: str,
                  year: str = "",
                  track_number: int = 0,
                  total_tracks: int = 0,
                  cover_url: Optional[str] = None,
                  genre: str = "") -> bool:
        """
        Aplica etiquetas ID3v2 a un archivo MP3
        """
        try:
            audio = MP3(file_path)
            
            # Añadir etiquetas ID3 si no existen
            if audio.tags is None:
                audio.add_tags()
            
            tags = audio.tags
            
            # Metadatos básicos
            tags["TIT2"] = TIT2(encoding=3, text=title)  # Título
            tags["TPE1"] = TPE1(encoding=3, text=artist)  # Artista principal
            tags["TALB"] = TALB(encoding=3, text=album)   # Álbum
            tags["TPE2"] = TPE2(encoding=3, text=artist)  # Artista del álbum
            
            if year:
                tags["TYER"] = TYER(encoding=3, text=str(year))  # Año
            
            if genre:
                tags["TCON"] = TCON(encoding=3, text=genre)  # Género
            
            # Número de pista
            if track_number > 0:
                if total_tracks > 0:
                    tags["TRCK"] = TRCK(encoding=3, text=f"{track_number}/{total_tracks}")
                else:
                    tags["TRCK"] = TRCK(encoding=3, text=str(track_number))
            
            # Descargar y añadir carátula
            if cover_url:
                try:
                    response = requests.get(cover_url, timeout=10)
                    if response.status_code == 200:
                        mime_type = response.headers.get('content-type', 'image/jpeg')
                        tags["APIC"] = APIC(
                            encoding=3,
                            mime=mime_type,
                            type=3,  # Carátula frontal
                            desc='Cover',
                            data=response.content
                        )
                except Exception as e:
                    print(f"Error descargando carátula: {e}")
            
            # Guardar cambios
            audio.save()
            
            return True
            
        except Exception as e:
            print(f"Error aplicando metadatos: {e}")
            return False
    
    def create_folder_structure(self, base_path: Path, artist: str, year: str, album: str) -> Path:
        """
        Crea estructura de carpetas: Artista/Año - Álbum/
        """
        # Sanitizar nombres para carpetas
        safe_artist = self._sanitize_filename(artist)
        safe_album = self._sanitize_filename(album)
        
        folder_name = f"{year} - {safe_album}" if year else safe_album
        album_path = base_path / safe_artist / folder_name
        album_path.mkdir(parents=True, exist_ok=True)
        
        return album_path
    
    def _sanitize_filename(self, name: str) -> str:
        """Limpia caracteres inválidos para nombres de archivo"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '-')
        return name.strip()
    
    def read_metadata(self, file_path: str) -> dict:
        """Lee metadatos de un archivo MP3"""
        try:
            audio = MP3(file_path)
            tags = audio.tags if audio.tags else {}
            
            return {
                'title': str(tags.get('TIT2', 'Unknown')),
                'artist': str(tags.get('TPE1', 'Unknown')),
                'album': str(tags.get('TALB', 'Unknown')),
                'year': str(tags.get('TYER', '')),
                'track': str(tags.get('TRCK', '')),
                'duration': audio.info.length if audio.info else 0
            }
        except:
            return {}

# Instancia global
metadata_manager = MetadataManager()