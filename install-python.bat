@echo off
setlocal enabledelayedexpansion

echo ========================================
echo English Trainer - Manual Python Setup
echo ========================================
echo.

REM Download Python installer
echo Downloading Python 3.12 installer...
powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe' -OutFile '%TEMP%\python-3.12.10-amd64.exe'"

if not exist "%TEMP%\python-3.12.10-amd64.exe" (
    echo [ERROR] Failed to download Python installer
    pause
    exit /b 1
)

echo [OK] Python installer downloaded

REM Install Python silently
echo Installing Python 3.12...
"%TEMP%\python-3.12.10-amd64.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

echo Waiting for installation to complete...
timeout /t 30 /nobreak

REM Clean up
del "%TEMP%\python-3.12.10-amd64.exe"

echo.
echo [OK] Python installation complete
echo.

REM Verify installation
python --version
if %errorlevel% neq 0 (
    echo [WARNING] Python not found in PATH
    echo You may need to restart your terminal or add Python to PATH manually
)

echo.
echo Setup complete!
pause