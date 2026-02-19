# DUKATOR - Underground Music Downloader

Descargador de música multiplataforma para Windows y macOS.

## Características

- 🔍 **Búsqueda por álbumes** - Busca y descarga álbumes completos desde MusicBrainz
- 🎵 **Búsqueda de canciones** - Busca en YouTube, SoundCloud y Audiomack
- 🔗 **Descarga por URL** - Pega enlaces directa de YouTube, SoundCloud, etc.
- 📂 **Biblioteca local** - Reproduce archivos de audio de tu carpeta
- 🎧 **Preview** - Escucha antes de descargar
- ⬇️ **Alta calidad** - Descarga en MP3 320kbps
- 🏷️ **Metadatos** - Añade automáticamente título, artista, álbum y portada

## Requisitos

### Windows
- Python 3.12+ (incluido en el exe)
- FFmpeg (incluido en la carpeta)

### macOS
- Python 3.12
- FFmpeg (se instala automáticamente con Homebrew)

## Uso Rápido

### Windows
 simplemente ejecuta `DUKATOR.exe`

### Desde código fuente (cualquier OS)
```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python dukator.py
```

## Compilar

### Windows
```bash
.\compilar_final.bat
```

### macOS
```bash
chmod +x compilar_mac.sh
./compilar_mac.sh
```

## Fuentes Soportadas

- YouTube
- SoundCloud  
- Audiomack
- Vimeo
- Mixcloud
- Dailymotion
- Archive.org
- VK
- Twitch
- Bilibili
- Facebook
- Instagram
- TikTok
- Pixabay

## Estructura del Proyecto

```
DUKATOR/
├── dukator.py           # Código principal
├── DUKATOR.spec         # Config PyInstaller
├── compilar_final.bat   # Compilar Windows
├── compilar_mac.sh      # Compilar macOS
├── requirements.txt     # Dependencias Python
├── dukator.ico         # Icono
└── ffmpeg.exe          # FFmpeg (Windows)
```

## Licencia

MIT License
