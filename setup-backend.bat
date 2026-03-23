@echo off
setlocal enabledelayedexpansion

echo ========================================
echo English Trainer - Backend Setup
echo ========================================
echo.

REM Find Python installation
set PYTHON_CMD=
if exist "C:\Python312\python.exe" (
    set PYTHON_CMD=C:\Python312\python.exe
    goto :python_found
)
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe" (
    set PYTHON_CMD=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe
    goto :python_found
)
if exist "C:\Program Files\Python312\python.exe" (
    set PYTHON_CMD=C:\Program Files\Python312\python.exe
    goto :python_found
)

echo [ERROR] Cannot find Python installation
echo Please install Python 3.12 from https://python.org
pause
exit /b 1

:python_found
echo [OK] Using Python: %PYTHON_CMD%
"%PYTHON_CMD%" --version
echo.

REM Change to backend directory
cd /d "%~dp0backend"

REM Create virtual environment if not exists
if not exist "venv" (
    echo Creating virtual environment...
    "%PYTHON_CMD%" -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing backend dependencies...
pip install -r requirements/development.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed

echo.
echo ========================================
echo Backend setup complete!
echo ========================================
echo.
echo To start the backend server, run:
echo   venv\Scripts\activate.bat
echo   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
echo.
pause