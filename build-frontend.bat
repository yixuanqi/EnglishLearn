@echo off
setlocal enabledelayedexpansion

echo ========================================
echo English Trainer - Build Frontend
echo ========================================
echo.

REM Check Node.js installation
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found
    echo Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)

echo [OK] Node.js found
node --version
npm --version
echo.

REM Setup frontend
cd /d "%~dp0frontend"

REM Install dependencies
if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed
)

REM Build for production
echo.
echo ========================================
echo Building Frontend for Production...
echo ========================================
call npm run build
if %errorlevel% neq 0 (
    echo [ERROR] Build failed
    pause
    exit /b 1
)

echo.
echo [OK] Frontend build completed
echo Build output: frontend\dist\
echo.

pause
