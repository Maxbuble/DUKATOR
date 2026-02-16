@echo off
chcp 65001 >nul
title DUKATOR - Compilacion Rapida
cls

echo ==========================================
echo    ⚡ DUKATOR - Compilacion Rapida
echo ==========================================
echo.

REM Compilacion directa a un solo .exe portable
echo 🔨 Compilando DUKATOR.exe portable...
echo.

python -c "
import PyInstaller.__main__
import sys

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
    '--hidden-import=yt_dlp',
    '--hidden-import=musicbrainzngs',
    '--hidden-import=mutagen',
    '--hidden-import=mutagen.mp3',
    '--hidden-import=mutagen.id3',
    '--hidden-import=requests',
    '--hidden-import=PIL',
    '--hidden-import=PIL.Image',
    '--strip',
    '--noupx',
]

print('Iniciando compilacion...')
PyInstaller.__main__.run(args)
print('\n✅ Compilacion completada!')
print('Archivo: dist/DUKATOR.exe')
"

if errorlevel 1 (
    echo.
    echo ❌ Error en la compilacion
    echo Asegurate de tener instalado: pip install pyinstaller
    pause
    exit /b 1
)

echo.
echo ✅ ¡Listo! Tu archivo portable esta en:
echo    dist\DUKATOR.exe
echo.
echo Copialo a tu USB y usalo en cualquier PC
echo.
pause
start dist