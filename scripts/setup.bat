@echo off
cd /d "%~dp0\.."

echo venv yaratilmoqda...
python -m venv venv

echo kutubxonalar o'rnatilmoqda...
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\python.exe -m pip install -r requirements.txt

if not exist .env (
  copy .env.example .env
  echo .env yaratildi — BOT_TOKEN ni to'ldiring!
)

echo.
echo Tayyor! Botni ishga tushirish:
echo   scripts\start.bat
