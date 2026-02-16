@echo off
chcp 65001 >nul
title DUKATOR - Compilar a EXE Portable
cls

echo ==========================================
echo    ⚡ DUKATOR - Compilador Portable
echo ==========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python no esta instalado
    echo.
    echo Por favor instala Python 3.8+ desde:
    echo https://www.python.org/downloads/
    echo.
    echo Asegurate de marcar "Add Python to PATH" durante la instalacion
    pause
    exit /b 1
)

echo ✅ Python detectado
python --version
echo.

REM Instalar dependencias
echo 📦 Instalando dependencias...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo ❌ Error instalando dependencias
    pause
    exit /b 1
)
echo ✅ Dependencias instaladas
echo.

REM Instalar PyInstaller si no existe
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo 📦 Instalando PyInstaller...
    pip install pyinstaller -q
)

REM Preguntar version
echo Selecciona el tipo de compilacion:
echo.
echo 1️⃣  VERSION PORTABLE ESTANDAR (~25 MB)
echo    ✓ Un solo archivo .exe
echo    ✓ Descarga FFmpeg automaticamente (1a vez)
echo    ✓ Ideal para USB
echo.
echo 2️⃣  VERSION OFFLINE COMPLETA (~70 MB)
echo    ✓ Incluye FFmpeg embebido
echo    ✓ Funciona 100%% sin internet
echo    ✓ Mas pesado pero autonomo
echo.
set /p opcion="Selecciona (1 o 2): "

if "%opcion%"=="1" (
    echo.
    echo 🚀 Compilando version PORTABLE...
    python build_standalone.py
) else if "%opcion%"=="2" (
    echo.
    echo 💾 Compilando version OFFLINE...
    echo.
    echo ⚠️  Para esta version necesitas tener ffmpeg.exe
echo    en la carpeta ffmpeg\ del proyecto.
    echo.
    choice /C SN /M "¿Continuar de todos modos"
    if errorlevel 2 goto :eof
    python build_standalone.py
) else (
    echo.
    echo ❌ Opcion no valida
    pause
    exit /b 1
)

echo.
echo ✅ Proceso completado!
echo.
echo El archivo .exe esta en la carpeta 'dist'
echo.
pause