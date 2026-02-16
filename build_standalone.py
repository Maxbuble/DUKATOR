"""
Compilador de DUKATOR a .exe portable único
Ejecutar: python build_standalone.py
Genera un único archivo DUKATOR.exe portable
"""

import PyInstaller.__main__
import os
import shutil
from pathlib import Path

def build_portable():
    """Compila DUKATOR a un único .exe portable"""
    
    print("=" * 70)
    print("🏗️  COMPILANDO DUKATOR - Versión Portable")
    print("=" * 70)
    print("\n⚡ Generando .exe único y portable...")
    print("📦 Este archivo funcionará en cualquier Windows sin instalación\n")
    
    # Directorios
    root_dir = Path(__file__).parent.absolute()
    src_dir = root_dir / "src"
    dist_dir = root_dir / "dist"
    build_dir = root_dir / "build"
    
    # Limpiar builds anteriores
    print("🧹 Limpiando builds anteriores...")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # Verificar dependencias
    print("📦 Verificando dependencias...")
    os.system("pip install -r requirements.txt -q")
    
    print("\n🔨 Compilando ejecutable portable...")
    print("   Modo: Single file (.exe único)")
    print("   Interfaz: GUI (sin consola)")
    print("   FFmpeg: Se descargará automáticamente al ejecutar\n")
    
    # Opciones de PyInstaller para .exe único
    args = [
        str(src_dir / "gui" / "app.py"),  # Script principal
        "--name=DUKATOR",                  # Nombre del exe
        "--onefile",                       # UN SOLO ARCHIVO
        "--windowed",                      # Sin consola (solo GUI)
        "--clean",                         # Limpiar cache
        "--noconfirm",                     # No confirmar
        
        # Directorio de trabajo (donde se extraen archivos temporales)
        "--workpath=build",
        "--distpath=dist",
        "--specpath=build",
        
        # Incluir datos necesarios
        "--add-data=src/config.py;.",
        "--add-data=src/core;core",
        "--add-data=src/gui;gui", 
        "--add-data=src/utils;utils",
        
        # Imports ocultos necesarios
        "--hidden-import=customtkinter",
        "--hidden-import=customtkinter.windows",
        "--hidden-import=customtkinter.windows.widgets",
        "--hidden-import=yt_dlp",
        "--hidden-import=yt_dlp.extractor",
        "--hidden-import=yt_dlp.postprocessor",
        "--hidden-import=musicbrainzngs",
        "--hidden-import=mutagen",
        "--hidden-import=mutagen.mp3",
        "--hidden-import=mutagen.id3",
        "--hidden-import=requests",
        "--hidden-import=urllib3",
        "--hidden-import=charset_normalizer",
        "--hidden-import=certifi",
        "--hidden-import=idna",
        "--hidden-import=PIL",
        "--hidden-import=PIL.Image",
        "--hidden-import=PIL.ImageTk",
        
        # Optimizaciones
        "--strip",                         # Reducir tamaño
        "--noupx",                         # Sin UPX (mejor compatibilidad)
        
        # Icono (si existe)
        # "--icon=assets/icon.ico",
    ]
    
    try:
        # Ejecutar PyInstaller
        PyInstaller.__main__.run(args)
        
        print("\n" + "=" * 70)
        print("✅ COMPILACIÓN EXITOSA!")
        print("=" * 70)
        
        exe_path = dist_dir / "DUKATOR.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\n📁 Archivo generado:")
            print(f"   {exe_path}")
            print(f"   Tamaño: {size_mb:.1f} MB")
            print(f"\n✨ Este archivo es 100% PORTABLE:")
            print(f"   • Copia a USB y ejecuta en cualquier PC")
            print(f"   • No requiere instalación")
            print(f"   • No requiere Python")
            print(f"   • La primera vez descargará FFmpeg (~40MB)")
            print(f"\n🚀 Para usar:")
            print(f"   1. Copia DUKATOR.exe a tu USB o cualquier carpeta")
            print(f"   2. Ejecuta DUKATOR.exe (doble click)")
            print(f"   3. Espera a que descargue FFmpeg (solo primera vez)")
            print(f"   4. ¡Listo!")
            
            # Crear archivo de info
            info_path = dist_dir / "LEER - INSTRUCCIONES.txt"
            with open(info_path, "w", encoding="utf-8") as f:
                f.write("""DUKATOR - Instrucciones de Uso
================================

ARCHIVO PORTABLE
Este es un archivo ejecutable único que funciona sin instalación.

PRIMER USO:
1. La primera vez que ejecutes DUKATOR.exe, se descargará automáticamente 
   FFmpeg (necesario para procesar audio). Esto requiere conexión a internet.
   
2. Una vez descargado FFmpeg, podrás usar DUKATOR offline.

USO DESDE USB:
- Simplemente copia DUKATOR.exe a tu USB
- Ejecuta en cualquier PC con Windows 10/11
- Las descargas se guardarán en la carpeta del usuario

REQUISITOS:
- Windows 10 o 11 (64 bits)
- Conexión a internet (solo primera vez para FFmpeg)
- ~100MB de espacio libre

CARACTERÍSTICAS:
✓ Búsqueda de canciones individuales
✓ Descarga de álbumes completos
✓ Descarga bulk de URLs
✓ Integración Soulseek P2P
✓ MP3 320kbps con metadatos ID3v2

IMPORTANTE:
Respetar los derechos de autor de los materiales descargados.

---
DUKATOR - Archivador de Música Underground v1.0
""")
            
            print(f"\n📝 Instrucciones guardadas en: {info_path.name}")
            print("=" * 70)
            
            # Abrir carpeta dist
            os.startfile(dist_dir)
            
        else:
            print("\n❌ Error: No se encontró el archivo .exe generado")
            
    except Exception as e:
        print(f"\n❌ ERROR durante la compilación:")
        print(f"   {str(e)}")
        print(f"\nAsegúrate de tener instalado:")
        print(f"   pip install pyinstaller")
        raise

def build_with_ffmpeg():
    """Versión alternativa que incluye FFmpeg (más grande pero 100% offline)"""
    print("\n" + "=" * 70)
    print("🔨 COMPILANDO VERSIÓN CON FFMPEG INCLUIDO")
    print("=" * 70)
    print("\n⚠️  Esta versión es más grande (~70MB) pero funciona 100% offline\n")
    
    # Verificar si FFmpeg está descargado
    ffmpeg_path = Path(__file__).parent / "ffmpeg" / "ffmpeg.exe"
    
    if not ffmpeg_path.exists():
        print("❌ No se encontró ffmpeg.exe")
        print("   Para esta versión necesitas:")
        print("   1. Crear carpeta 'ffmpeg' en el directorio del proyecto")
        print("   2. Copiar ffmpeg.exe dentro de esa carpeta")
        print("   3. Volver a ejecutar este script")
        return False
    
    # Compilar con FFmpeg incluido
    root_dir = Path(__file__).parent.absolute()
    src_dir = root_dir / "src"
    dist_dir = root_dir / "dist-offline"
    
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    args = [
        str(src_dir / "gui" / "app.py"),
        "--name=DUKATOR_Offline",
        "--onefile",
        "--windowed",
        "--clean",
        "--noconfirm",
        f"--add-data={ffmpeg_path};ffmpeg",  # Incluir FFmpeg
        "--add-data=src/config.py;.",
        "--add-data=src/core;core",
        "--add-data=src/gui;gui",
        "--add-data=src/utils;utils",
        "--hidden-import=customtkinter",
        "--hidden-import=yt_dlp",
        "--hidden-import=musicbrainzngs",
        "--hidden-import=mutagen",
        "--hidden-import=requests",
        "--strip",
        "--noupx",
    ]
    
    PyInstaller.__main__.run(args)
    
    exe_path = dist_dir / "DUKATOR_Offline.exe"
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"\n✅ Versión offline generada: {size_mb:.1f} MB")
        print(f"   Ubicación: {exe_path}")
        os.startfile(dist_dir)
        return True
    
    return False

if __name__ == "__main__":
    import sys
    
    print("\nSelecciona modo de compilación:")
    print("1. 🚀 Versión estándar (25MB, descarga FFmpeg al ejecutar)")
    print("2. 💾 Versión offline (70MB, incluye FFmpeg, 100% offline)")
    print("3. ❌ Cancelar")
    
    try:
        opcion = input("\nOpción (1-3): ").strip()
        
        if opcion == "1":
            build_portable()
        elif opcion == "2":
            build_with_ffmpeg()
        else:
            print("\nCancelado.")
            
    except KeyboardInterrupt:
        print("\n\nCancelado por usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        input("\nPresiona Enter para salir...")
        sys.exit(1)