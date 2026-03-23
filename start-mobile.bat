@echo off
setlocal enabledelayedexpansion

echo ========================================
echo English Trainer - Mobile Access Setup
echo ========================================
echo.

REM Get local IP address
for /f "tokens=2 delims=:" %%A in ('ipconfig ^| findstr /C:"IPv4"') do (
    set LOCAL_IP=%%A
    set LOCAL_IP=!LOCAL_IP: =!
    goto :ip_found
)

:ip_found
echo Your computer's IP address: !LOCAL_IP!
echo.

REM Find Python
for %%P in (python python3 py) do (
    where %%P >nul 2>nul
    if !errorlevel! equ 0 (
        set PYTHON_CMD=%%P
        goto :python_found
    )
)

echo [WARNING] Python not found in PATH
echo Trying common Python paths...

if exist "C:\Python312\python.exe" (
    set PYTHON_CMD=C:\Python312\python.exe
    goto :python_found
)
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe" (
    set PYTHON_CMD=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe
    goto :python_found
)

echo [ERROR] Cannot find Python
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
echo Backend URL: http://!LOCAL_IP!:8000
echo API Docs: http://!LOCAL_IP!:8000/docs
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
    echo Backend is running on: http://!LOCAL_IP!:8000
    echo You can access the static HTML on your mobile device
    echo ========================================
    echo.
    echo Mobile Access Instructions:
    echo 1. Make sure your phone and computer are on the same WiFi
    echo 2. Open browser on your phone
    echo 3. Visit: http://!LOCAL_IP!:8000/docs
    echo 4. Or transfer frontend/index.html to your phone
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
echo Frontend URL: http://!LOCAL_IP!:3000
echo.
echo ========================================
echo Mobile Access Ready!
echo ========================================
echo.
echo On your Android phone:
echo 1. Connect to the same WiFi network
echo 2. Open browser (Chrome recommended)
echo 3. Visit: http://!LOCAL_IP!:3000
echo.
echo Backend API: http://!LOCAL_IP!:8000
echo API Documentation: http://!LOCAL_IP!:8000/docs
echo.
echo Press Ctrl+C to stop the servers
echo.

call npm run dev -- --host 0.0.0.0

pause