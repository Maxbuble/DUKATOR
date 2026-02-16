"""
Cliente para MusicBrainz
Obtiene metadatos de álbumes y canciones
"""

import musicbrainzngs
from typing import List, Dict, Optional
import time

class MusicBrainzClient:
    def __init__(self):
        musicbrainzngs.set_useragent(
            "DUKATOR",
            "1.0",
            "dukator@local"
        )
        self.cache = {}
    
    def search_albums(self, artist: str, album: str, limit: int = 10) -> List[Dict]:
        """Busca álbumes por artista y título"""
        try:
            query = f'artist:"{artist}" AND release:"{album}"'
            result = musicbrainzngs.search_releases(query=query, limit=limit)
            
            albums = []
            for release in result['release-list']:
                album_data = {
                    'id': release['id'],
                    'title': release['title'],
                    'artist': release['artist-credit'][0]['artist']['name'] if release.get('artist-credit') else 'Unknown',
                    'year': release.get('date', '????')[:4] if release.get('date') else '????',
                    'country': release.get('country', '??'),
                    'format': self._get_format(release),
                    'track_count': release.get('medium-list', [{}])[0].get('track-count', 0),
                    'label': release.get('label-info-list', [{}])[0].get('label', {}).get('name', 'Unknown')
                }
                albums.append(album_data)
            
            return albums
        except Exception as e:
            print(f"Error buscando álbumes: {e}")
            return []
    
    def get_album_tracks(self, release_id: str) -> Optional[Dict]:
        """Obtiene las canciones de un álbum específico"""
        try:
            if release_id in self.cache:
                return self.cache[release_id]
            
            result = musicbrainzngs.get_release_by_id(
                release_id,
                includes=['recordings', 'artists', 'labels', 'release-groups']
            )
            
            release = result['release']
            album_data = {
                'id': release_id,
                'title': release['title'],
                'artist': release['artist-credit'][0]['artist']['name'] if release.get('artist-credit') else 'Unknown',
                'year': release.get('date', '????')[:4] if release.get('date') else '????',
                'tracks': []
            }
            
            # Extraer canciones
            for medium in release.get('medium-list', []):
                for i, track in enumerate(medium.get('track-list', []), 1):
                    recording = track.get('recording', {})
                    duration_ms = recording.get('length', 0)
                    duration_sec = duration_ms / 1000 if duration_ms else 0
                    
                    track_data = {
                        'number': i,
                        'title': recording.get('title', 'Unknown'),
                        'duration': duration_sec,
                        'duration_formatted': self._format_duration(duration_sec),
                        'recording_id': recording.get('id')
                    }
                    album_data['tracks'].append(track_data)
            
            self.cache[release_id] = album_data
            time.sleep(0.5)  # Respetar rate limit
            return album_data
            
        except Exception as e:
            print(f"Error obteniendo tracks: {e}")
            return None
    
    def get_cover_art_url(self, release_id: str) -> Optional[str]:
        """Obtiene URL de carátula desde Cover Art Archive"""
        try:
            result = musicbrainzngs.get_image_list(release_id)
            for image in result['images']:
                if image.get('front', False):
                    return image['thumbnails'].get('large', image['image'])
            return None
        except:
            return None
    
    def _get_format(self, release: Dict) -> str:
        """Extrae el formato del release"""
        formats = []
        for medium in release.get('medium-list', []):
            fmt = medium.get('format', 'Unknown')
            formats.append(fmt)
        return ', '.join(formats) if formats else 'Unknown'
    
    def _format_duration(self, seconds: float) -> str:
        """Formatea duración en MM:SS"""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}:{secs:02d}"

# Instancia global
mb_client = MusicBrainzClient()