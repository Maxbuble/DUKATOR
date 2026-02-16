"""
Motor de descarga usando yt-dlp
Soporta: Bandcamp, SoundCloud, YouTube, Archive.org, Mixcloud
"""

import yt_dlp
import os
from pathlib import Path
from typing import Callable, Optional, Dict
import tempfile

class DownloadEngine:
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg_path = ffmpeg_path
        self.current_process = None
        
    def download_track(self, 
                      query: str,
                      output_path: Path,
                      expected_duration: Optional[float] = None,
                      progress_callback: Optional[Callable] = None,
                      source_priority: list = None) -> Dict:
        """
        Descarga una canción siguiendo prioridad de fuentes
        
        Args:
            query: Búsqueda o URL directa
            output_path: Ruta de salida
            expected_duration: Duración esperada en segundos
            progress_callback: Función de progreso
            source_priority: Lista de fuentes en orden de prioridad
        """
        if source_priority is None:
            source_priority = ['bandcamp', 'soundcloud', 'youtube']
        
        result = {
            'success': False,
            'file_path': None,
            'duration_match': False,
            'source': None,
            'error': None
        }
        
        # Si es URL directa, intentar descargar directamente
        if query.startswith(('http://', 'https://')):
            return self._download_from_url(query, output_path, expected_duration, progress_callback)
        
        # Buscar en fuentes por prioridad
        for source in source_priority:
            try:
                search_query = self._build_search_query(source, query)
                download_result = self._download_from_url(search_query, output_path, expected_duration, progress_callback)
                
                if download_result['success']:
                    return download_result
                    
            except Exception as e:
                print(f"Error en fuente {source}: {e}")
                continue
        
        result['error'] = "No se encontró la canción en ninguna fuente"
        return result
    
    def _build_search_query(self, source: str, query: str) -> str:
        """Construye query de búsqueda según la fuente"""
        if source == 'bandcamp':
            return f"ytsearch1:{query} bandcamp"
        elif source == 'soundcloud':
            return f"ytsearch1:{query} soundcloud"
        elif source == 'youtube':
            return f"ytsearch1:{query}"
        return f"ytsearch1:{query}"
    
    def _download_from_url(self, url: str, output_path: Path, expected_duration: Optional[float], progress_callback: Optional[Callable]) -> Dict:
        """Descarga desde URL específica"""
        result = {
            'success': False,
            'file_path': None,
            'duration_match': False,
            'source': None,
            'error': None,
            'actual_duration': None
        }
        
        def progress_hook(d):
            if d['status'] == 'downloading' and progress_callback:
                percent = d.get('downloaded_bytes', 0) / d.get('total_bytes', 1) * 100
                progress_callback(percent, f"Descargando... {percent:.1f}%")
            elif d['status'] == 'finished' and progress_callback:
                progress_callback(100, "Procesando audio...")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'ffmpeg_location': self.ffmpeg_path,
            'outtmpl': str(output_path.with_suffix('')),  # yt-dlp añade la extensión
            'progress_hooks': [progress_hook],
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Primero extraer info sin descargar para verificar duración
                info = ydl.extract_info(url, download=False)
                
                if info:
                    actual_duration = info.get('duration', 0)
                    result['actual_duration'] = actual_duration
                    
                    # Verificar coincidencia de duración (±10%)
                    if expected_duration and actual_duration:
                        diff_percent = abs(actual_duration - expected_duration) / expected_duration * 100
                        if diff_percent > 10:
                            result['error'] = f"Duración no coincide: {actual_duration}s vs {expected_duration}s ({diff_percent:.1f}% diff)"
                            result['duration_match'] = False
                            return result
                        result['duration_match'] = True
                    
                    # Descargar
                    ydl.download([url])
                    
                    result['success'] = True
                    result['file_path'] = str(output_path.with_suffix('.mp3'))
                    result['source'] = info.get('extractor', 'unknown')
                    
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def download_from_bulk_urls(self, urls: list, output_dir: Path, progress_callback: Optional[Callable] = None) -> list:
        """Descarga múltiples URLs en modo bulk"""
        results = []
        total = len(urls)
        
        for i, url in enumerate(urls, 1):
            if progress_callback:
                progress_callback((i-1)/total*100, f"Procesando {i}/{total}: {url[:50]}...")
            
            # Generar nombre basado en la URL
            safe_name = "".join(c for c in url if c.isalnum() or c in (' ', '-', '_'))[:50]
            output_path = output_dir / f"{safe_name}_{i}"
            
            result = self._download_from_url(url.strip(), output_path, None, None)
            results.append({
                'url': url,
                **result
            })
            
            if progress_callback:
                progress_callback(i/total*100, f"Completado {i}/{total}")
        
        return results
    
    def cancel_download(self):
        """Cancela la descarga actual"""
        if self.current_process:
            self.current_process.terminate()