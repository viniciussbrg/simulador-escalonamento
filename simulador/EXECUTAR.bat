@echo off
cd /d "%~dp0"
start "" pythonw "main.pyw"
if errorlevel 1 (
  python "main.py"
  pause
)
