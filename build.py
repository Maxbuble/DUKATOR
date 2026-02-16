"""
Compilador de DUKATOR a .exe
Ejecutar: python build.py
"""

import PyInstaller.__main__
import os
import shutil
from pathlib import Path

def build():
    """Compila DUKATOR a un .exe standalone"""
    
    print("=" * 60)
    print("🏗️  COMPILANDO DUKATOR")
    print("=" * 60)
    
    # Directorios
    root_dir = Path(__file__).parent
    src_dir = root_dir / "src"
    dist_dir = root_dir / "dist"
    build_dir = root_dir / "build"
    
    # Limpiar builds anteriores
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    print("\n📦 Instalando dependencias...")
    os.system("pip install -r requirements.txt -q")
    
    print("\n🔨 Compilando ejecutable...")
    
    # Opciones de PyInstaller
    args = [
        str(src_dir / "gui" / "app.py"),  # Script principal
        "--name=DUKATOR",                  # Nombre del exe
        "--onefile",                       # Un solo archivo
        "--windowed",                      # Sin consola
        "--icon=NONE",                     # Sin icono por defecto
        "--clean",                         # Limpiar cache
        "--noconfirm",                     # No confirmar sobrescritura
        
        # Incluir datos
        f"--add-data={src_dir}/config.py;.",
        f"--add-data={src_dir}/core;core",
        f"--add-data={src_dir}/gui;gui",
        f"--add-data={src_dir}/utils;utils",
        
        # Ocultar imports
        "--hidden-import=customtkinter",
        "--hidden-import=yt_dlp",
        "--hidden-import=musicbrainzngs",
        "--hidden-import=mutagen",
        "--hidden-import=requests",
        "--hidden-import=PIL",
        "--hidden-import=urllib3",
        "--hidden-import=charset_normalizer",
        "--hidden-import=certifi",
        "--hidden-import=idna",
        
        # Optimización
        "--strip",                         # Reducir tamaño
        "--noupx",                         # No usar UPX (mejor compatibilidad)
    ]
    
    # Ejecutar PyInstaller
    PyInstaller.__main__.run(args)
    
    print("\n✅ Compilación completada!")
    print(f"📁 Ejecutable generado en: {dist_dir / 'DUKATOR.exe'}")
    
    # Crear archivo README
    readme_content = """# DUKATOR - Archivador de Música Underground

## Ejecución
Simplemente ejecuta `DUKATOR.exe`

La primera vez se descargará automáticamente FFmpeg (necesario para conversión de audio).

## Características
✓ Búsqueda de canciones sueltas
✓ Búsqueda de álbumes completos con metadatos
✓ Descarga directa de URLs (Bulk)
✓ Integración Soulseek P2P
✓ MP3 320kbps CBR
✓ Etiquetado automático ID3v2
✓ Carátulas automáticas

## Estructura de carpetas
Las descargas se guardan en:
- Canciones sueltas: `Descargas/DUKATOR/Canciones_Sueltas/`
- Álbumes: `Descargas/DUKATOR/Artista/Año - Álbum/`
- Bulk: `Descargas/DUKATOR/Bulk_YYYYMMDD/`

## Fuentes soportadas
- YouTube
- Bandcamp
- SoundCloud
- Archive.org
- Mixcloud
- Soulseek (P2P)

---
Generado automáticamente con PyInstaller
"""
    
    with open(dist_dir / "README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("📄 README.txt creado")
    print("\n🎉 LISTO! Copia DUKATOR.exe a cualquier carpeta y ejecútalo.")
    print("=" * 60)

if __name__ == "__main__":
    build()