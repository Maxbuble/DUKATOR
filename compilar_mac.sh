#!/bin/bash

# DUKATOR - Compilador para macOS
# Este script compila DUKATOR para macOS

echo "========================================"
echo "  DUKATOR - Compilador para macOS"
echo "========================================"
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para mostrar mensajes
msg_ok() { echo -e "${GREEN}✓${NC} $1"; }
msg_warn() { echo -e "${YELLOW}⚠${NC} $1"; }
msg_error() { echo -e "${RED}✗${NC} $1"; }

# Verificar que estamos en macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    msg_error "Este script solo funciona en macOS"
    exit 1
fi

# 1. Verificar Python
echo "[1/5] Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
    msg_ok "Python encontrado: $(python3 --version)"
    
    # Instalar Python 3.12 si no está
    if [[ ! "$PYTHON_VERSION" == "3.12"* ]]; then
        msg_warn "Python 3.12 no encontrado. Instalar desde:"
        msg_warn "https://www.python.org/downloads/mac-osx/"
        msg_warn "O usar: brew install python312"
        # Intentar con pyenv o brew
        if command -v brew &> /dev/null; then
            msg_warn "Intentando instalar Python 3.12 con Homebrew..."
            brew install python312 || true
        fi
    fi
else
    msg_error "Python no encontrado. Instalar desde python.org"
    exit 1
fi

# 2. Instalar FFmpeg
echo ""
echo "[2/5] Verificando FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    msg_ok "FFmpeg encontrado: $(ffmpeg -version | head -n1)"
else
    msg_warn "FFmpeg no encontrado"
    if command -v brew &> /dev/null; then
        msg_warn "Instalando FFmpeg con Homebrew..."
        brew install ffmpeg
        msg_ok "FFmpeg instalado"
    else
        msg_error "Instalar Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        msg_error "O instalar FFmpeg manualmente desde: ffmpeg.org"
        exit 1
    fi
fi

# 3. Instalar dependencias Python
echo ""
echo "[3/5] Instalando dependencias Python..."
PIP_CMD="python3 -m pip"

# Actualizar pip
$PIP_CMD install --upgrade pip --quiet 2>/dev/null || true

# Instalar dependencias
$PIP_CMD install --quiet \
    customtkinter \
    yt-dlp \
    mutagen \
    pygame \
    pyinstaller \
    requests

if [ $? -eq 0 ]; then
    msg_ok "Dependencias instaladas"
else
    msg_error "Error instalando dependencias"
    exit 1
fi

# 4. Verificar archivos necesarios
echo ""
echo "[4/5] Verificando archivos del proyecto..."
if [ ! -f "dukator.py" ]; then
    msg_error "No se encontró dukator.py"
    exit 1
fi
if [ ! -f "DUKATOR.spec" ]; then
    msg_error "No se encontró DUKATOR.spec"
    exit 1
fi
msg_ok "Archivos verificados"

# 5. Compilar
echo ""
echo "[5/5] Compilando DUKATOR..."
echo "========================================"
echo ""

python3 -m PyInstaller DUKATOR.spec --clean --noconfirm

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    msg_ok "¡Compilación exitosa!"
    echo "========================================"
    echo ""
    echo "Ejecutable creado en: dist/DUKATOR.app"
    echo ""
    echo "Para ejecutar:"
    echo "  open dist/DUKATOR.app"
    echo ""
    echo "O desde terminal:"
    echo "  ./dist/DUKATOR.app/Contents/MacOS/DUKATOR"
else
    msg_error "Error en la compilación"
    exit 1
fi
