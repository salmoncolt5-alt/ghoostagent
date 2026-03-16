@echo off
title GhoostAgent - Launcher
echo -------------------------------
echo  GhoostAgent - Start Script
echo -------------------------------

if not exist "venv\" (
    echo [*] Creando entorno virtual...
    python -m venv venv
)

call venv\Scripts\activate

echo [*] Instalando requerimientos...
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt

echo [*] Ejecutando CloudAgent
python main.py

pause
