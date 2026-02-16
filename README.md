# ⚡ DUKATOR - Archivador de Música Underground

Aplicación de escritorio portable para Windows que permite archivar música difícil de encontrar, rarezas y discografías underground con máxima fidelidad.

## 🚀 Características Principales

### 🎵 Búsqueda de Canciones Sueltas
- Busca canciones individuales por nombre
- Búsqueda múltiples fuentes simultáneamente (YouTube, SoundCloud, Bandcamp, Archive.org)
- Previsualización de resultados con duración y fuente
- Descarga directa con un click

### 🔍 Buscador Inteligente de Álbumes
- Integración completa con MusicBrainz
- Búsqueda por artista y álbum
- Selección de edición exacta (vinilo, remaster, año específico)
- Tabla de canciones con selección individual
- Filtro de calidad Smart-Duration (±10% margen de error)

### 📥 Descarga Directa Bulk
- Pega múltiples URLs (YouTube, Bandcamp, SoundCloud, Archive.org, Mixcloud)
- Descarga en lote automática
- Organización en carpetas por fecha
- Log detallado de resultados

### 🌐 Soulseek P2P
- Integración con red Soulseek para rarezas
- Búsqueda P2P de material underground
- Descarga directa desde usuarios

### ✨ Características Técnicas
- **Calidad**: MP3 320kbps CBR (constante)
- **Metadatos**: Etiquetado automático ID3v2 (Título, Artista, Álbum, Año, Pista)
- **Carátulas**: Descarga automática desde Cover Art Archive
- **Organización**: Estructura automática `Artista/Año - Álbum/XX - Canción.mp3`
- **Tema**: Interfaz dark underground (morado/negro)

## 📁 Estructura de Carpetas de Salida

```
Descargas/
└── DUKATOR/
    ├── Canciones_Sueltas/          # Tracks individuales
    │   └── Nombre Canción.mp3
    ├── Artista/
    │   └── 2024 - Nombre Album/
    │       ├── 01 - Canción 1.mp3
    │       ├── 02 - Canción 2.mp3
    │       └── cover.jpg
    └── Bulk_20240216_143022/       # Descargas bulk
        └── ...
```

## 🎨 Fuentes Soportadas

| Fuente | Tipo de Contenido | Prioridad |
|--------|------------------|-----------|
| Bandcamp | FLAC/WAV originales, alta calidad | ⭐⭐⭐ |
| SoundCloud | Demos, maquetas, inéditos | ⭐⭐ |
| YouTube | Videoclips, rarezas | ⭐ |
| Archive.org | Material histórico, hemerotecas | ⭐⭐ |
| Mixcloud | Sets, mixes exclusivos | ⭐⭐ |
| Soulseek | Red P2P para rarezas | ⭐⭐⭐ |

## 🛠️ Instalación y Uso

### Opción 1: Ejecutable Portable (Recomendado)

1. Descarga `DUKATOR.exe` desde la carpeta `dist/`
2. Colócalo en cualquier carpeta
3. Ejecuta `DUKATOR.exe`
4. La primera vez se descargará automáticamente FFmpeg (~40MB)

### Opción 2: Desde Código Fuente

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python main.py

# O compilar a .exe
python build.py
```

## 🖥️ Requisitos del Sistema

- **OS**: Windows 10/11 (x64)
- **RAM**: 2GB mínimo (4GB recomendado)
- **Espacio**: 200MB + espacio para descargas
- **Internet**: Conexión estable para descargas
- **Python**: 3.8+ (solo si ejecutas desde código)

## 🎮 Guía de Uso Rápido

### Descargar Canción Suelta
1. Ve a pestaña "🎵 Canciones"
2. Introduce nombre de canción y opcionalmente artista
3. Selecciona fuentes de búsqueda
4. Click en "Buscar"
5. Selecciona resultado y "Descargar"

### Descargar Álbum Completo
1. Ve a pestaña "🔍 Álbumes"
2. Introduce Artista y Álbum
3. Selecciona edición correcta de los resultados
4. Marca las canciones que quieres
5. Click en "Descargar Seleccionadas"

### Descarga Bulk
1. Ve a pestaña "📥 Bulk URLs"
2. Pega URLs (una por línea)
3. Click en "DESCARGAR TODO"

## ⚙️ Configuración

La app crea automáticamente la carpeta de descargas en:
- Por defecto: `C:\Users\[TuUsuario]\Music\DUKATOR`
- Puedes cambiarla desde el botón "Cambiar" en el footer

## 🔧 Tecnologías Utilizadas

- **GUI**: CustomTkinter (Python)
- **Descarga**: yt-dlp
- **Audio**: FFmpeg
- **Metadatos**: Mutagen (ID3v2)
- **Base de datos**: MusicBrainz API
- **Compilación**: PyInstaller

## ⚠️ Notas Importantes

- **Primera ejecución**: Se descargará FFmpeg automáticamente (~40MB)
- **Calidad**: Forzado a MP3 320kbps CBR para consistencia
- **Filtro Smart**: Las canciones con duración muy diferente (±10%) se marcan para revisión
- **Portabilidad**: El .exe es completamente portable, no requiere instalación

## 📝 TODO / Roadmap

- [ ] Implementar búsqueda Soulseek completa
- [ ] Añadir soporte para listas de reproducción
- [ ] Integración con Discogs para rarezas
- [ ] Sistema de favoritos/historial
- [ ] Preview de audio antes de descargar
- [ ] Soporte para otros formatos (FLAC, OGG)

## 📄 Licencia

Este proyecto es de código abierto. Úsalo bajo tu propia responsabilidad.

**Nota**: Respeta los derechos de autor y las licencias de las fuentes de música.

---

<p align="center">
  <b>⚡ DUKATOR - Hecho para coleccionistas underground ⚡</b>
</p>

<p align="center">
  <sub>Compilado con PyInstaller para Windows</sub>
</p>
