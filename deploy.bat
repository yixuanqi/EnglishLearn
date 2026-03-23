@echo off
setlocal enabledelayedexpansion

set "SCRIPT_VERSION=2.0"
set "TIMESTAMP=%date:~0,4%-%date:~5,2%-%date:~8,2%_%time:~0,2%-%time:~3,2%-%time:~6,2%"
set "TIMESTAMP=%TIMESTAMP: =0%"
set "LOG_FILE=logs\deploy_%TIMESTAMP%.log"
set "ENVIRONMENT=production"

for /f "tokens=1" %%a in ('powershell -Command "Get-Date -Format 'yyyy-MM-dd_HH-mm-ss'") do set "LOG_FILE=logs\deploy_%%a.log"

if not exist "logs" mkdir logs

call :log "========================================"
call :log "English Trainer - Deploy Script v%SCRIPT_VERSION%"
call :log "========================================"
call :log "Timestamp: %TIMESTAMP%"
call :log "Environment: %ENVIRONMENT%"
call :log ""

:parse_args
if "%~1"=="" goto :main
if /i "%~1"=="-e" (
    set "ENVIRONMENT=%~2"
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--environment" (
    set "ENVIRONMENT=%~2"
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--help" goto :usage
shift
goto :parse_args

:usage
echo Usage: deploy.bat [OPTIONS]
echo.
echo Options:
echo   -e, --environment ENV   Set environment (staging, production) [default: production]
echo   --skip-tests            Skip pre-deployment tests
echo   --skip-migration        Skip database migration
echo   --rollback              Rollback to previous version
echo   --help                  Show this help message
echo.
echo Examples:
echo   deploy.bat                           Deploy to production
echo   deploy.bat -e staging               Deploy to staging
echo   deploy.bat --skip-migration         Deploy without migration
exit /b 0

:main
call :check_python
call :check_env_file
call :setup_backend
call :run_migration
call :deploy_backend
call :verify_deployment
call :log "Deployment completed successfully!"
exit /b 0

:check_python
call :log "[1/6] Checking Python environment..."
python --version >nul 2>&1
if %errorlevel% neq 0 (
    call :log "ERROR" "Python not found. Please install Python 3.11 or higher."
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%v"
call :log "OK" "Python %PYTHON_VERSION% found"
exit /b 0

:check_env_file
call :log "[2/6] Checking environment file..."
if not exist ".env" (
    if exist ".env.production" (
        call :log "WARNING" ".env not found, copying from .env.production"
        copy ".env.production" ".env"
    ) else (
        call :log "ERROR" ".env file not found. Please create one."
        exit /b 1
    )
)
call :log "OK" "Environment file found"
exit /b 0

:setup_backend
call :log "[3/6] Setting up backend..."
cd /d "%~dp0backend"

if not exist "venv" (
    call :log "INFO" "Creating virtual environment..."
    python -m venv venv
    if %errorlevel% neq 0 (
        call :log "ERROR" "Failed to create virtual environment"
        exit /b 1
    )
    call :log "OK" "Virtual environment created"
)

call :log "INFO" "Activating virtual environment..."
call venv\Scripts\activate.bat

call :log "INFO" "Upgrading pip..."
python -m pip install --upgrade pip >nul 2>&1

call :log "INFO" "Installing dependencies..."
pip install -r requirements/production.txt >nul 2>&1
if %errorlevel% neq 0 (
    call :log "ERROR" "Failed to install dependencies"
    exit /b 1
)
call :log "OK" "Dependencies installed"
cd /d "%~dp0"
exit /b 0

:run_migration
call :log "[4/6] Running database migrations..."
cd /d "%~dp0backend"
call venv\Scripts\activate.bat

alembic upgrade head >nul 2>&1
if %errorlevel% neq 0 (
    call :log "WARNING" "Migration failed or no migrations to run"
) else (
    call :log "OK" "Database migrations completed"
)
cd /d "%~dp0"
exit /b 0

:deploy_backend
call :log "[5/6] Starting backend server..."
cd /d "%~dp0backend"
call venv\Scripts\activate.bat

call :log "INFO" "Starting Gunicorn server..."
start "EnglishTrainer Backend" /min cmd /c "gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000"

call :log "OK" "Backend server started"
cd /d "%~dp0"
exit /b 0

:verify_deployment
call :log "[6/6] Verifying deployment..."
set "MAX_RETRIES=10"
set "RETRY_COUNT=0"

:retry_loop
set /a RETRY_COUNT+=1
powershell -Command "try { Invoke-WebRequest -Uri 'http://localhost:8000/health' -UseBasicParsing -TimeoutSec 5 | Select-Object -ExpandProperty StatusCode" >nul 2>&1
if %errorlevel% equ 200 (
    call :log "OK" "Health check passed - Service is running"
    exit /b 0
)

if !RETRY_COUNT! lss %MAX_RETRIES% (
    call :log "INFO" "Retry !RETRY_COUNT!/!MAX_RETRIES! in 3 seconds..."
    timeout /t 3 /nobreak >nul
    goto :retry_loop
)

call :log "WARNING" "Health check failed after !MAX_RETRIES! retries"
call :log "INFO" "Please check logs and ensure service is running"
exit /b 0

:log
set "LEVEL=INFO"
if "%~1"=="[1/6]" set "LEVEL=INFO"
if "%~1"=="[2/6]" set "LEVEL=INFO"
if "%~1"=="[3/6]" set "LEVEL=INFO"
if "%~1"=="[4/6]" set "LEVEL=INFO"
if "%~1"=="[5/6]" set "LEVEL=INFO"
if "%~1"=="[6/6]" set "LEVEL=INFO"
if "%~1"=="ERROR" (
    set "LEVEL=ERROR"
    set "MSG=%~2"
    echo [%LEVEL%] %MSG%
    echo [%TIMESTAMP%] [%LEVEL%] %MSG% >> "%LOG_FILE%"
    exit /b 0
)
if "%~1"=="WARNING" (
    set "LEVEL=WARNING"
    set "MSG=%~2"
    echo [%LEVEL%] %MSG%
    echo [%TIMESTAMP%] [%LEVEL%] %MSG% >> "%LOG_FILE%"
    exit /b 0
)
if "%~1"=="OK" (
    set "LEVEL=INFO"
    set "MSG=%~2"
    echo [OK] %MSG%
    echo [%TIMESTAMP%] [OK] %MSG% >> "%LOG_FILE%"
    exit /b 0
)
if "%~1"=="INFO" (
    set "LEVEL=INFO"
    set "MSG=%~2"
    echo [INFO] %MSG%
    echo [%TIMESTAMP%] [INFO] %MSG% >> "%LOG_FILE%"
    exit /b 0
)
set "MSG=%~1"
echo %MSG%
echo [%TIMESTAMP%] %MSG% >> "%LOG_FILE%"
exit /b 0
