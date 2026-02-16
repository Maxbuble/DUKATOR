@echo off
chcp 65001 >nul
title DUKATOR - Instalador
cls

echo ==========================================
echo    ⚡ DUKATOR - Instalador
echo ==========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python no está instalado
    echo Por favor instala Python 3.8 o superior desde:
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python detectado
echo.

REM Instalar dependencias
echo 📦 Instalando dependencias...
pip install -r requirements.txt -q

if errorlevel 1 (
    echo ❌ ERROR: No se pudieron instalar las dependencias
    pause
    exit /b 1
)

echo ✅ Dependencias instaladas
echo.

REM Preguntar qué hacer
echo ¿Qué deseas hacer?
echo.
echo 1️⃣  Ejecutar DUKATOR ahora
echo 2️⃣  Compilar a .exe portable
echo 3️⃣  Salir
echo.
set /p opcion="Selecciona una opción (1-3): "

if "%opcion%"=="1" (
    echo.
    echo 🚀 Iniciando DUKATOR...
    python main.py
) else if "%opcion%"=="2" (
    echo.
    echo 🔨 Compilando a .exe...
    python build.py
    echo.
    echo ✅ Compilación completada!
    echo El archivo DUKATOR.exe está en la carpeta 'dist'
    pause
) else (
    echo.
    echo 👋 Hasta luego!
)
