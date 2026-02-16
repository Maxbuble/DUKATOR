# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT
from PyInstaller.utils.hooks import collect_all, collect_data_files

# Collect all data for customtkinter
datas = []
datas += collect_data_files('customtkinter')

# Analysis
a = Analysis(
    ['src/gui/app.py'],
    pathex=[],
    binaries=[],
    datas=datas + [
        ('src/config.py', '.'),
        ('src/core', 'core'),
        ('src/gui', 'gui'),
        ('src/utils', 'utils'),
    ],
    hiddenimports=[
        'customtkinter',
        'customtkinter.windows',
        'customtkinter.windows.widgets',
        'customtkinter.windows.widgets.core_rendering',
        'customtkinter.windows.widgets.core_rendering.ctk_canvas',
        'customtkinter.windows.widgets.core_rendering.draw_engine',
        'customtkinter.windows.widgets.theme',
        'customtkinter.windows.widgets.scaling',
        'customtkinter.windows.widgets.font',
        'customtkinter.windows.widgets.image',
        'yt_dlp',
        'yt_dlp.extractor',
        'yt_dlp.extractor.lazy_extractors',
        'yt_dlp.postprocessor',
        'yt_dlp.dependencies',
        'yt_dlp.dependencies.urllib3',
        'musicbrainzngs',
        'mutagen',
        'mutagen.mp3',
        'mutagen.id3',
        'mutagen.easyid3',
        'mutagen.flac',
        'mutagen.ogg',
        'mutagen.mp4',
        'requests',
        'urllib3',
        'urllib3.packages',
        'urllib3.packages.ssl_match_hostname',
        'charset_normalizer',
        'certifi',
        'idna',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'PIL.ImageDraw',
        'PIL.ImageFont',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# PYZ
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# EXE
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DUKATOR',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)