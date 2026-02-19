# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_dynamic_libs
from PyInstaller.utils.hooks import collect_all

datas = [('dukator.ico', '.')]
binaries = []
hiddenimports = ['pygame', 'pygame.mixer', 'mutagen.id3', 'mutagen.mp3', 'yt_dlp']

# Detectar sistema operativo y configurar FFmpeg
if sys.platform == 'win32':
    # Windows: buscar FFmpeg en el directorio actual o en PATH
    ffmpeg_files = ['ffmpeg.exe', 'ffprobe.exe']
    dll_files = ['avcodec-62.dll', 'avformat-62.dll', 'avfilter-11.dll', 
                 'avdevice-62.dll', 'avutil-60.dll', 'swscale-9.dll', 'swresample-6.dll']
    
    for f in ffmpeg_files + dll_files:
        if os.path.exists(f):
            binaries.append((f, '.'))
        else:
            print(f"Warning: {f} not found, skipping...")
else:
    # macOS/Linux: FFmpeg debe estar en PATH, no se incluye en el bundle
    # El código buscará ffmpeg en el sistema
    print("macOS/Linux detected: FFmpeg should be installed via Homebrew/apt")

datas += collect_data_files('pygame')
binaries += collect_dynamic_libs('pygame')
tmp_ret = collect_all('pygame')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['dukator.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='DUKATOR',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='dukator.ico',
)
