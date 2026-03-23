@echo off
setlocal enabledelayedexpansion

echo ========================================
echo English Trainer - Quick Start
echo ========================================
echo.

REM Find Python installation
for %%P in (python python3 py) do (
    where %%P >nul 2>nul
    if !errorlevel! equ 0 (
        set PYTHON_CMD=%%P
        goto :python_found
    )
)

echo [WARNING] Python not found in PATH
echo Trying to find Python in common locations...

REM Check common Python installation paths
if exist "C:\Python312\python.exe" (
    set PYTHON_CMD=C:\Python312\python.exe
    goto :python_found
)
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe" (
    set PYTHON_CMD=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe
    goto :python_found
)

echo [ERROR] Cannot find Python installation
echo Please install Python from https://python.org
pause
exit /b 1

:python_found
echo [OK] Using Python: %PYTHON_CMD%
"%PYTHON_CMD%" --version
echo.

REM Setup backend
cd /d "%~dp0backend"

if not exist "venv" (
    echo Creating virtual environment...
    "%PYTHON_CMD%" -m venv venv
)

call venv\Scripts\activate.bat

if not exist "venv\Lib\site-packages\fastapi" (
    echo Installing backend dependencies...
    pip install -r requirements/development.txt
)

echo.
echo ========================================
echo Starting Backend Server...
echo ========================================
echo Backend URL: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
start "Backend Server" cmd /k "cd /d %cd% && venv\Scripts\activate.bat && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

cd ..

REM Setup frontend
cd frontend

where node >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo [INFO] Node.js not found
    echo Opening static HTML version...
    echo ========================================
    start "" "%~dp0frontend\index.html"
    echo.
    echo Frontend opened in browser!
    echo Backend is running in separate window.
    echo You can now test the complete application!
    echo.
    pause
    exit /b 0
)

echo [OK] Node.js found
node --version

if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
)

echo.
echo ========================================
echo Starting Frontend Server...
echo ========================================
echo Frontend URL: http://localhost:3000
echo.
call npm run dev

pause