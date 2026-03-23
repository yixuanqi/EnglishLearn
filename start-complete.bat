@echo off
setlocal enabledelayedexpansion

echo ========================================
echo English Trainer - Complete Setup
echo ========================================
echo.

REM Set Python path
set "PYTHON_PATH=C:\Users\0qyx\AppData\Local\Programs\Python\Python312\python.exe"
set "PIP_PATH=C:\Users\0qyx\AppData\Local\Programs\Python\Python312\Scripts\pip.exe"

if not exist "%PYTHON_PATH%" (
    echo [ERROR] Python not found at %PYTHON_PATH%
    echo Please install Python 3.12 manually
    pause
    exit /b 1
)

echo [OK] Python found
"%PYTHON_PATH%" --version
echo.

REM Create backend virtual environment
cd /d "%~dp0backend"
if not exist "venv" (
    echo Creating Python virtual environment...
    "%PYTHON_PATH%" -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install backend dependencies
if not exist "venv\Lib\site-packages\fastapi" (
    echo Installing backend dependencies...
    pip install -r requirements/development.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
    echo [OK] Backend dependencies installed
)

REM Start backend in new window
echo.
echo ========================================
echo Starting Backend Server...
echo ========================================
echo Backend will run on: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
start "English Trainer Backend" cmd /k "cd /d %cd% && venv\Scripts\activate.bat && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

cd ..

REM Setup frontend
cd frontend

REM Check if Node.js is available
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo [INFO] Node.js not found
    echo Opening static HTML version instead...
    echo ========================================
    start "" "%~dp0frontend\index.html"
    echo.
    echo Frontend opened in browser!
    echo Backend is running in separate window.
    echo.
    pause
    exit /b 0
)

echo [OK] Node.js found
node --version
npm --version
echo.

REM Install frontend dependencies
if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install frontend dependencies
        pause
        exit /b 1
    )
    echo [OK] Frontend dependencies installed
)

REM Start frontend
echo.
echo ========================================
echo Starting Frontend Server...
echo ========================================
echo Frontend will run on: http://localhost:3000
echo.
call npm run dev

pause