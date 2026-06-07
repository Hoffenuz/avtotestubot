@echo off
cd /d "%~dp0\.."

if not exist venv (
  echo venv topilmadi. Avval: scripts\setup.bat
  exit /b 1
)

venv\Scripts\python.exe run.py
