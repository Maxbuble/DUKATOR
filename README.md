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

## Plataformas Soportadas

| Plataforma | Estado | Descarga |
|------------|--------|----------|
| ✅ **Windows** | Soportado | `DUKATOR.exe` (incluye FFmpeg) |
| ✅ **macOS ARM** (M1/M2/M3) | Soportado | `DUKATOR-ARM.app` (requiere FFmpeg) |
| ⚠️ **macOS Intel** | [Compilar desde código](#macos-intel) | No hay build automático |

## Requisitos

### Windows
- Windows 10/11 (64-bit)
- FFmpeg incluido en el ejecutable

### macOS ARM (M1/M2/M3)
- macOS 12.0 o superior
- FFmpeg: `brew install ffmpeg`

### macOS Intel
- macOS 10.15 o superior
- [Compilar desde código fuente](#compilar-desde-código)

## Descargas

Ve a [Releases](https://github.com/Maxbuble/DUKATOR/releases/latest) para descargar la última versión.

> **⚠️ Nota:** Solo descarga el archivo ejecutable para tu plataforma. **No necesitas** descargar el "Source code".

### Windows
1. Descarga solo **`DUKATOR.exe`** (~37 MB)
2. Haz doble click para ejecutar
3. ¡Listo! No requiere instalación

### macOS ARM (M1/M2/M3)
1. Descarga **`DUKATOR-ARM.app.tar.gz`** (~34 MB)
2. Descomprime el archivo
3. Haz doble click en `DUKATOR-ARM.app`
4. Si aparece error de seguridad: **Clic derecho → Abrir → Abrir de todos modos**
5. Requiere FFmpeg: `brew install ffmpeg` (solo una vez)

### ¿Qué NO descargar?
❌ `Source code (zip)` - Código fuente, no necesario para usuarios  
❌ `Source code (tar.gz)` - Código fuente, no necesario para usuarios  
❌ Otros archivos del repositorio - Solo necesitas el ejecutable

#### macOS Intel
Ver [Compilar desde código](#compilar-desde-código)

## Compilar desde código

### Requisitos previos
- Python 3.12 o superior
- FFmpeg instalado
- pip

### Paso a paso

```bash
# Clonar el repositorio
git clone https://github.com/Maxbuble/DUKATOR.git
cd DUKATOR

# Instalar dependencias
pip install -r requirements.txt

# Compilar
# Windows:
.\compilar_final.bat

# macOS (cualquier arquitectura):
chmod +x compilar_mac.sh
./compilar_mac.sh
```

El ejecutable se creará en la carpeta `dist/`.

## Compilar para macOS Intel específicamente

Si tienes una Mac con procesador Intel (2019 o anterior):

```bash
git clone https://github.com/Maxbuble/DUKATOR.git
cd DUKATOR

# Instalar dependencias
pip install -r requirements.txt

# Instalar FFmpeg si no lo tienes
brew install ffmpeg

# Compilar
pyinstaller DUKATOR.spec --clean --noconfirm

# El archivo estará en dist/DUKATOR.app
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
├── dukator.py           # Código principal (single-file)
├── DUKATOR.spec         # Configuración PyInstaller
├── compilar_final.bat   # Script Windows
├── compilar_mac.sh      # Script macOS
├── requirements.txt     # Dependencias Python
├── dukator.ico         # Icono
└── README.md           # Este archivo
```

## Notas sobre macOS Intel

GitHub Actions (la plataforma de CI/CD gratuita) ya no ofrece runners Mac Intel. Por eso:
- **Mac ARM**: Build automático disponible
- **Mac Intel**: Debes compilar desde el código fuente

La compilación es sencilla y toma ~2 minutos siguiendo las instrucciones de arriba.

## Licencia

MIT License

## Soporte

Si tienes problemas:
1. Verifica que cumples los [requisitos](#requisitos)
2. Para Mac Intel, asegúrate de compilar desde código
3. Abre un [Issue](https://github.com/Maxbuble/DUKATOR/issues) si persiste el problema
