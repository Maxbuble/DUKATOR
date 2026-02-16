@echo off
chcp 65001 >nul
title DUKATOR - Ejecutar
cd /d "%~dp0"
python main.py
if errorlevel 1 (
    echo.
    echo ❌ Error al ejecutar. Asegúrate de haber ejecutado INSTALAR.bat primero.
    pause
)
