@echo off
echo ========================================
echo English Trainer Project Launcher
echo ========================================
echo.

REM Check if Python is available
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found in PATH
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

echo [OK] Python found
python --version
echo.

REM Check if Node.js is available
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] Node.js is not found in PATH
    echo Frontend will run in static HTML mode
    echo To enable full React development, install Node.js from https://nodejs.org
    echo.
    echo Opening frontend in browser...
    start "" "frontend\index.html"
    pause
    exit /b 0
)

echo [OK] Node.js found
node --version
npm --version
echo.

echo ========================================
echo Starting Backend Server...
echo ========================================
cd backend

REM Create virtual environment if not exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies if needed
if not exist "venv\Lib\site-packages\fastapi" (
    echo Installing backend dependencies...
    pip install -r requirements/development.txt
)

REM Start backend in new window
echo Starting FastAPI server on http://localhost:8000
start "English Trainer Backend" cmd /k "cd /d %cd% && venv\Scripts\activate.bat && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

cd ..

echo ========================================
echo Starting Frontend Server...
echo ========================================
cd frontend

REM Install dependencies if needed
if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
)

REM Start frontend
echo Starting React dev server on http://localhost:3000
call npm run dev

pause