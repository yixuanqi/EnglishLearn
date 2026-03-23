@echo off
setlocal enabledelayedexpansion

echo ========================================
echo English Trainer - Complete Build
echo ========================================
echo.

REM Build frontend
echo Step 1: Building frontend...
call "%~dp0build-frontend.bat"
if %errorlevel% neq 0 (
    echo [ERROR] Frontend build failed
    pause
    exit /b 1
)

echo.
echo Step 2: Preparing backend...
cd /d "%~dp0backend"

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Installing production dependencies...
pip install -r requirements/production.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build Completed Successfully!
echo ========================================
echo.
echo Frontend: frontend\dist\
echo Backend: backend\ (with venv)
echo.
echo Next steps:
echo 1. Update .env with production values
echo 2. Run deploy-production.bat to start the server
echo.

pause
