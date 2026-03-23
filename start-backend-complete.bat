@echo off
setlocal enabledelayedexpansion

echo ========================================
echo English Trainer - Complete Backend Start
echo ========================================
echo.

REM Step 1: Install Python if needed
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found, installing...
    winget install Python.Python.3.12 --accept-source-agreements
    echo Waiting for Python installation...
    timeout /t 60 /nobreak
    echo Refreshing environment variables...
    refreshenv >nul 2>&1
)

REM Step 2: Verify Python
python --version
if %errorlevel% neq 0 (
    echo [ERROR] Python installation failed
    echo Please install Python manually from https://python.org
    pause
    exit /b 1
)

echo [OK] Python is available
echo.

REM Step 3: Setup backend
cd /d "%~dp0backend"

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing dependencies...
pip install -r requirements/development.txt

echo.
echo ========================================
echo Starting Backend Server...
echo ========================================
echo Backend URL: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause