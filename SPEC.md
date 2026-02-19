# DUKATOR - Especificación Técnica

## 1. Descripción General

**Nombre:** DUKATOR
**Tipo:** Aplicación de escritorio portable para Windows
**Objetivo:** Archivar música difícil de encontrar, rarezas y discografías underground con máxima fidelidad

## 2. Arquitectura

### 2.1 Motor de Búsqueda
- **Fuente principal:** MusicBrainz API para metadata de álbumes
- Búsqueda por artista + álbum con selección de edición específica

### 2.2 Fuentes de Descarga
- YouTube (principal)
- Bandcamp
- SoundCloud
- Internet Archive
- Mixcloud
- RTVE Play

### 2.3 Motor de Descarga
- **yt-dlp** para descarga de audio
- **FFmpeg** para conversión y post-procesado

### 2.4 Formato de Salida
- MP3 320kbps CBR constante
- Metadatos ID3v2 (título, artista, álbum, año, número de pista, carátula)

### 2.5 Estructura de Archivos
```
Descargas/DUKATOR/
├── Artista/
│   └── Año - Álbum/
│       ├── 01 - Canción.mp3
│       ├── 02 - Canción.mp3
│       └── cover.jpg
```

## 3. Interfaz de Usuario

### 3.1 Tecnologías
- **CustomTkinter** para GUI moderna
- Tema oscuro por defecto

### 3.2 Pestañas

#### Pestaña A: Buscador de Álbumes
- Campo de búsqueda (Artista - Álbum)
- Botón de búsqueda
- Lista de resultados con ediciones
- Tabla de canciones con checkboxes
- Botón "Descargar Seleccionadas"

#### Pestaña B: Descarga Directa
- Área de texto para múltiples enlaces (uno por línea)
- Indicador de progreso
- Log de descargas

### 3.3 Elementos Comunes
- Barra de progreso
- Selector de carpeta de destino
- Estado de descarga en tiempo real

## 4. Portabilidad

- Compilación a .exe único con PyInstaller
- FFmpeg embebido en el ejecutable
- yt-dlp como dependencia
- Sin instalación requerida

## 5. Dependencias

```
customtkinter
mutagen
requests
yt-dlp
pyinstaller
```

## 6. Consideraciones

- Validación de duración (±10% margen) - marcar para revisión si supera
- Manejo de errores robusto
- Logging de actividades
- Retry automático en fallos de descarga
