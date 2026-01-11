@echo off
cd /d "%~dp0"
title BestSoft Launcher (Windows)
cls

echo BestSoft Launcher Baslatiliyor...
echo --------------------------------

REM 1. Sanal Ortam Kontrol
if not exist ".venv" (
    echo Sanal ortam bulunamadi, olusturuluyor...
    python -m venv .venv
    echo Sanal ortam olusturuldu.
)

REM 2. Sanal Ortami Aktif Et
call .venv\Scripts\activate.bat

REM 3. Python CLI Scriptini Calistir
python setup_cli.py

pause
