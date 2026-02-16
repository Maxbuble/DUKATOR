"""
Script de preparación y compilación para Windows
Ejecutar: python preparar_y_compilar.py
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Ejecuta un comando y muestra progreso"""
    print(f"\n{'='*60}")
    print(f"⏳ {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ {description} - COMPLETADO")
        if result.stdout:
            print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR en {description}")
        print(f"Error: {e}")
        if e.stderr:
            print(f"Detalles: {e.stderr[-500:]}")
        return False

def main():
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║           ⚡ DUKATOR - Preparación y Compilación             ║
    ║                                                              ║
    ║  Este script instalará todo lo necesario y compilará         ║
    ║  DUKATOR.exe en un único archivo portable                    ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Verificar Python
    print("\n🔍 Verificando Python...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ ERROR: Necesitas Python 3.8 o superior")
        print(f"   Tu versión: {version.major}.{version.minor}")
        input("\nPresiona Enter para salir...")
        sys.exit(1)
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detectado")
    
    # Paso 1: Actualizar pip
    if not run_command("python -m pip install --upgrade pip -q", "Actualizando pip"):
        print("⚠️  Advertencia: No se pudo actualizar pip, continuando...")
    
    # Paso 2: Instalar dependencias
    if not run_command("pip install -r requirements.txt", "Instalando dependencias"):
        print("❌ ERROR: No se pudieron instalar las dependencias")
        input("\nPresiona Enter para salir...")
        sys.exit(1)
    
    # Paso 3: Instalar PyInstaller
    if not run_command("pip install pyinstaller", "Instalando PyInstaller"):
        print("❌ ERROR: No se pudo instalar PyInstaller")
        input("\nPresiona Enter para salir...")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("🚀 TODO LISTO - Iniciando compilación")
    print("="*60)
    print("\n📦 Generando DUKATOR.exe portable...")
    print("   Esto puede tomar 2-5 minutos...")
    print("   No cierres esta ventana\n")
    
    # Paso 4: Compilar
    try:
        import PyInstaller.__main__
        
        args = [
            'src/gui/app.py',
            '--name=DUKATOR',
            '--onefile',
            '--windowed',
            '--clean',
            '--noconfirm',
            '--add-data=src/config.py;.',
            '--add-data=src/core;core',
            '--add-data=src/gui;gui',
            '--add-data=src/utils;utils',
            '--hidden-import=customtkinter',
            '--hidden-import=customtkinter.windows',
            '--hidden-import=customtkinter.windows.widgets',
            '--hidden-import=yt_dlp',
            '--hidden-import=yt_dlp.extractor',
            '--hidden-import=musicbrainzngs',
            '--hidden-import=mutagen',
            '--hidden-import=mutagen.mp3',
            '--hidden-import=mutagen.id3',
            '--hidden-import=requests',
            '--hidden-import=urllib3',
            '--hidden-import=charset_normalizer',
            '--hidden-import=certifi',
            '--hidden-import=idna',
            '--hidden-import=PIL',
            '--hidden-import=PIL.Image',
            '--hidden-import=PIL.ImageTk',
            '--strip',
            '--noupx',
        ]
        
        PyInstaller.__main__.run(args)
        
        # Verificar que se creó
        exe_path = Path('dist/DUKATOR.exe')
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            
            print("\n" + "="*60)
            print("✅ ¡COMPILACIÓN EXITOSA!")
            print("="*60)
            print(f"\n📁 Archivo generado:")
            print(f"   {exe_path.absolute()}")
            print(f"   📊 Tamaño: {size_mb:.1f} MB")
            print(f"\n🎉 ¡Listo para usar!")
            print(f"\n💡 Instrucciones:")
            print(f"   1. Copia el archivo DUKATOR.exe a tu USB o cualquier carpeta")
            print(f"   2. Ejecútalo con doble click")
            print(f"   3. La primera vez descargará FFmpeg (~40MB)")
            print(f"   4. ¡Disfruta!")
            print(f"\n⚠️  Nota: La primera ejecución requiere internet para descargar FFmpeg")
            print(f"    Después funciona completamente offline")
            print("="*60)
            
            # Abrir carpeta dist
            os.startfile('dist')
            
        else:
            print("\n❌ ERROR: No se encontró el archivo .exe generado")
            print("   Revisa la carpeta 'dist'")
            
    except Exception as e:
        print(f"\n❌ ERROR durante la compilación: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n")
    input("Presiona Enter para cerrar...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelado por usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        input("\nPresiona Enter para salir...")
        sys.exit(1)