@echo off
setlocal enabledelayedexpansion

echo ========================================
echo English Trainer - Production Deployment
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found
    echo Please install Python 3.11 or higher
    pause
    exit /b 1
)

echo [OK] Python found
python --version
echo.

REM Setup backend
cd /d "%~dp0backend"

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)

call venv\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing production dependencies...
pip install -r requirements/production.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

REM Run database migrations
echo Running database migrations...
alembic upgrade head
if %errorlevel% neq 0 (
    echo [WARNING] Database migration failed or no migrations to run
) else (
    echo [OK] Database migrations completed
)
echo.

REM Check if .env file exists
if not exist "%~dp0.env" (
    echo [WARNING] .env file not found
    echo Copying .env.production to .env...
    copy "%~dp0.env.production" "%~dp0.env"
    echo [INFO] Please update .env with your production values
    pause
)

echo.
echo ========================================
echo Starting Production Server...
echo ========================================
echo Backend URL: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start with gunicorn for production
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

pause
