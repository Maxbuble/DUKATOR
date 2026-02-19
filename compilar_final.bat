@echo off
setlocal EnableDelayedExpansion

echo ========================================
echo   DUKATOR - Compilador Inteligente
echo ========================================
echo.

set PYTHON_CMD=

REM Buscar Python en orden de prioridad (preferir 3.12 que tiene las dependencias)
echo [*] Buscando Python instalado...

REM Opcion 1: py -3.12 (tiene todas las dependencias instaladas)
py -3.12 --version >nul 2>&1
if !errorlevel! equ 0 (
    echo [OK] Encontrado: py -3.12
    set PYTHON_CMD=py -3.12
    goto :found
)

REM Opcion 2: Python 3.12 en AppData
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    echo [OK] Encontrado Python 3.12 en AppData
    set PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
    goto :found
)

REM Opcion 3: Python 3.12 en C:\
if exist "C:\Python312\python.exe" (
    echo [OK] Encontrado: C:\Python312\python.exe
    set PYTHON_CMD=C:\Python312\python.exe
    goto :found
)

REM Opcion 4: py -3.11
py -3.11 --version >nul 2>&1
if !errorlevel! equ 0 (
    echo [OK] Encontrado: py -3.11
    set PYTHON_CMD=py -3.11
    goto :found
)

REM Opcion 5: py launcher generico
where py >nul 2>&1
if !errorlevel! equ 0 (
    echo [OK] Encontrado: py launcher
    set PYTHON_CMD=py
    goto :found
)

REM Opcion 6: python en PATH
where python >nul 2>&1
if !errorlevel! equ 0 (
    echo [OK] Encontrado: python
    set PYTHON_CMD=python
    goto :found
)

REM No encontrado
:python-not-found
echo.
echo ========================================
echo   ERROR: Python no encontrado
echo ========================================
echo.
echo Python no esta instalado o no esta en el PATH.
echo.
echo Soluciones:
echo 1. Reinstala Python desde python.org
echo 2. Marca la opcion "Add Python to PATH"
echo 3. O ejecuta este .bat desde la carpeta donde esta instalado Python
echo.
pause
exit /b 1

:found
echo.
echo [*] Usando: !PYTHON_CMD!
!PYTHON_CMD! --version
echo.

REM Verificar/Instalar PyInstaller
echo [*] Verificando PyInstaller...
!PYTHON_CMD! -c "import PyInstaller" >nul 2>&1
if !errorlevel! neq 0 (
    echo [*] Instalando PyInstaller...
    !PYTHON_CMD! -m pip install pyinstaller --quiet
    if !errorlevel! neq 0 (
        echo [ERROR] No se pudo instalar PyInstaller
        pause
        exit /b 1
    )
    echo [OK] PyInstaller instalado
) else (
    echo [OK] PyInstaller ya esta instalado
)

echo.
echo ========================================
echo   COMPILANDO DUKATOR
echo ========================================
echo.

REM Compilar
!PYTHON_CMD! -m PyInstaller DUKATOR.spec --clean

if !errorlevel! neq 0 (
    echo.
    echo [ERROR] La compilacion fallo
    pause
    exit /b 1
)

echo.
echo ========================================
echo   COPIANDO EJECUTABLE
echo ========================================
echo.

if exist "dist\DUKATOR.exe" (
    copy /Y "dist\DUKATOR.exe" "DUKATOR.exe" >nul
    echo [OK] Creado: DUKATOR.exe
    echo.
    echo ========================================
    echo   !COMPILACION EXITOSA!
    echo ========================================
    echo.
    echo Ejecutable listo: DUKATOR.exe
    echo Con icono de nota musical incluido.
    echo.
) else (
    echo [ERROR] No se encontro el archivo compilado en dist\DUKATOR.exe
)

pause
