"""
Gestor automático de FFmpeg
Descarga ffmpeg solo si no está presente
"""

import os
import sys
import zipfile
import requests
from pathlib import Path

class FFmpegManager:
    def __init__(self):
        self.app_dir = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent.parent.parent
        self.ffmpeg_dir = self.app_dir / "ffmpeg"
        self.ffmpeg_exe = self.ffmpeg_dir / "ffmpeg.exe"
        
    def is_installed(self):
        """Verifica si ffmpeg está disponible"""
        return self.ffmpeg_exe.exists()
    
    def get_ffmpeg_path(self):
        """Retorna la ruta al ejecutable ffmpeg"""
        return str(self.ffmpeg_exe) if self.is_installed() else "ffmpeg"
    
    def download_ffmpeg(self, progress_callback=None):
        """Descarga ffmpeg automáticamente"""
        try:
            # URL de descarga de ffmpeg (build estático para Windows)
            url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
            
            if progress_callback:
                progress_callback(0, "Descargando FFmpeg...")
            
            # Descargar
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            zip_path = self.app_dir / "ffmpeg_temp.zip"
            
            downloaded = 0
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total_size > 0:
                            progress = int((downloaded / total_size) * 50)
                            progress_callback(progress, f"Descargando FFmpeg... {progress}%")
            
            if progress_callback:
                progress_callback(50, "Extrayendo FFmpeg...")
            
            # Extraer solo ffmpeg.exe
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for member in zip_ref.namelist():
                    if member.endswith('ffmpeg.exe'):
                        zip_ref.extract(member, self.app_dir)
                        extracted_path = self.app_dir / member
                        # Mover a la ubicación final
                        self.ffmpeg_dir.mkdir(exist_ok=True)
                        extracted_path.rename(self.ffmpeg_exe)
                        # Limpiar directorios temporales
                        for p in self.app_dir.glob("ffmpeg-master-*"):
                            if p.is_dir():
                                import shutil
                                shutil.rmtree(p)
                        break
            
            # Limpiar zip
            zip_path.unlink(missing_ok=True)
            
            if progress_callback:
                progress_callback(100, "FFmpeg listo!")
            
            return True
            
        except Exception as e:
            if progress_callback:
                progress_callback(0, f"Error: {str(e)}")
            return False
    
    def ensure_ffmpeg(self, progress_callback=None):
        """Asegura que ffmpeg esté disponible"""
        if self.is_installed():
            return True
        return self.download_ffmpeg(progress_callback)