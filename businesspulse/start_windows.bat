@echo off
title BusinessPulse Analytics Platform
color 0B
echo.
echo  ==========================================
echo   BusinessPulse Analytics Platform v1.0
echo  ==========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found. Install from https://python.org
    pause
    exit /b
)

:: Install dependencies if needed
echo  Installing dependencies...
pip install flask flask-sqlalchemy -q

:: Start server
echo.
echo  Starting server at http://localhost:5000
echo  Press Ctrl+C to stop
echo.
start "" http://localhost:5000
python app.py
pause
