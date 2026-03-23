@echo off
setlocal enabledelayedexpansion

set "SCRIPT_VERSION=1.0"
set "TIMESTAMP=%date:~0,4%-%date:~5,2%-%date:~8,2%_%time:~0,2%-%time:~3,2%-%time:~6,2%"
set "TIMESTAMP=%TIMESTAMP: =0%"
set "LOG_FILE=logs\rollback_%TIMESTAMP%.log"
set "BACKUP_DIR=backups"
set "MAX_BACKUPS=5"

for /f "tokens=1" %%a in ('powershell -Command "Get-Date -Format 'yyyy-MM-dd_HH-mm-ss'") do set "LOG_FILE=logs\rollback_%%a.log"

if not exist "logs" mkdir logs
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

call :parse_args %*

call :log "========================================"
call :log "English Trainer - Rollback Script"
call :log "========================================"
call :log "Version: %SCRIPT_VERSION%"
call :log "Timestamp: %TIMESTAMP%"
call :log "Mode: %MODE%"
if defined TARGET_VERSION call :log "Target Version: %TARGET_VERSION%"
call :log ""

if "%MODE%"=="" goto :usage

if "%MODE%"=="list" goto :list_backups
if "%MODE%"=="rollback" goto :perform_rollback
if "%MODE%"=="backup" goto :create_backup
goto :usage

:usage
call :log "Usage: rollback.bat [OPTIONS]"
call :log ""
call :log "Options:"
call :log "  list                         List available backups"
call :log "  backup                       Create a manual backup before deployment"
call :log "  rollback                     Rollback to the last successful deployment"
call :log "  rollback --version VERSION   Rollback to a specific version"
call :log "  --keep-backups N             Number of backups to keep [default: %MAX_BACKUPS%]"
call :log ""
call :log "Examples:"
call :log "  rollback.bat list"
call :log "  rollback.bat backup"
call :log "  rollback.bat rollback"
call :log "  rollback.bat rollback --version 20260318_143022"
exit /b 0

:list_backups
call :log "Available Backups:"
call :log "----------------------------------------"
if exist "%BACKUP_DIR%\*" (
    for /f "tokens=*" %%f in ('dir /b /o-d "%BACKUP_DIR%\*" 2^>nul') do (
        call :log "  - %%f"
    )
) else (
    call :log "  No backups found"
)
exit /b 0

:create_backup
call :log "[1/3] Creating backup..."

set "BACKUP_NAME=backup_%TIMESTAMP%"
set "BACKUP_PATH=%BACKUP_DIR%\%BACKUP_NAME%"
mkdir "%BACKUP_PATH%"

call :log "INFO" "Backing up database..."
if exist "backend\english_trainer.db" (
    copy "backend\english_trainer.db" "%BACKUP_PATH%\" >nul
    call :log "OK" "Database backed up"
) else (
    call :log "WARNING" "Database file not found, skipping"
)

call :log "INFO" "Backing up environment file..."
if exist ".env" (
    copy ".env" "%BACKUP_PATH%\" >nul
    call :log "OK" "Environment file backed up"
)

call :log "INFO" "Backing up frontend dist..."
if exist "frontend\dist" (
    xcopy /s /e /y "frontend\dist" "%BACKUP_PATH%\dist\" >nul
    call :log "OK" "Frontend dist backed up"
)

call :log "INFO" "Compressing backup..."
powershell -Command "Compress-Archive -Path '%BACKUP_PATH%' -DestinationPath '%BACKUP_PATH%.zip' -Force"
rmdir /s /q "%BACKUP_PATH%" >nul 2>&1

call :log "OK" "Backup created: %BACKUP_NAME%.zip"

call :cleanup_old_backups
exit /b 0

:perform_rollback
call :log "[1/4] Preparing rollback..."

if defined TARGET_VERSION (
    set "BACKUP_FILE=%BACKUP_DIR%\backup_%TARGET_VERSION%.zip"
) else (
    for /f "tokens=*" %%f in ('dir /b /o-d "%BACKUP_DIR%\backup_*.zip" 2^>nul ^| head -n 1') do (
        set "BACKUP_FILE=%BACKUP_DIR%\%%f"
    )
)

if not defined BACKUP_FILE (
    call :log "ERROR" "No backup found to rollback to"
    exit /b 1
)

call :log "INFO" "Using backup: %BACKUP_FILE%"

call :log "[2/4] Extracting backup..."
powershell -Command "Expand-Archive -Path '%BACKUP_FILE%' -DestinationPath '%BACKUP_DIR%\temp_restore' -Force"
if %errorlevel% neq 0 (
    call :log "ERROR" "Failed to extract backup"
    exit /b 1
)
call :log "OK" "Backup extracted"

call :log "[3/4] Stopping current services..."
docker-compose -f docker-compose.prod.yml down >nul 2>&1
call :log "OK" "Services stopped"

call :log "INFO" "Restoring database..."
if exist "%BACKUP_DIR%\temp_restore\english_trainer.db" (
    if not exist "backend" mkdir backend
    copy "%BACKUP_DIR%\temp_restore\english_trainer.db" "backend\" >nul
    call :log "OK" "Database restored"
)

call :log "INFO" "Restoring environment file..."
if exist "%BACKUP_DIR%\temp_restore\.env" (
    copy "%BACKUP_DIR%\temp_restore\.env" ".\" >nul
    call :log "OK" "Environment file restored"
)

call :log "INFO" "Restoring frontend..."
if exist "%BACKUP_DIR%\temp_restore\dist" (
    if not exist "frontend" mkdir frontend
    xcopy /s /e /y "%BACKUP_DIR%\temp_restore\dist" "frontend\dist\" >nul
    call :log "OK" "Frontend restored"
)

rmdir /s /q "%BACKUP_DIR%\temp_restore" >nul 2>&1

call :log "[4/4] Restarting services..."
docker-compose -f docker-compose.prod.yml up -d
if %errorlevel% equ 0 (
    call :log "OK" "Services restarted"
) else (
    call :log "ERROR" "Failed to restart services"
    exit /b 1
)

call :log ""
call :log "========================================"
call :log "Rollback completed successfully!"
call :log "========================================"
exit /b 0

:cleanup_old_backups
call :log "INFO" "Cleaning up old backups (keeping %MAX_BACKUPS%)..."
set "COUNT=0"
for /f "tokens=*" %%f in ('dir /b /o-d "%BACKUP_DIR%\backup_*.zip" 2^>nul') do (
    set /a COUNT+=1
    if !COUNT! gtr %MAX_BACKUPS% (
        del "%BACKUP_DIR%\%%f" >nul 2>&1
        call :log "INFO" "Deleted old backup: %%f"
    )
)
exit /b 0

:parse_args
if "%~1"=="" goto :eof
if /i "%~1"=="list" set "MODE=list"
if /i "%~1"=="backup" set "MODE=backup"
if /i "%~1"=="rollback" set "MODE=rollback"
if /i "%~1"=="--version" (
    set "TARGET_VERSION=%~2"
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--keep-backups" (
    set "MAX_BACKUPS=%~2"
    shift
    shift
    goto :parse_args
)
shift
goto :parse_args

:log
if "%~1"=="INFO" (
    echo [INFO] %~2
    echo [%TIMESTAMP%] [INFO] %~2 >> "%LOG_FILE%"
    exit /b 0
)
if "%~1"=="OK" (
    echo [OK] %~2
    echo [%TIMESTAMP%] [OK] %~2 >> "%LOG_FILE%"
    exit /b 0
)
if "%~1"=="ERROR" (
    echo [ERROR] %~2
    echo [%TIMESTAMP%] [ERROR] %~2 >> "%LOG_FILE%"
    exit /b 0
)
if "%~1"=="WARNING" (
    echo [WARN] %~2
    echo [%TIMESTAMP%] [WARN] %~2 >> "%LOG_FILE%"
    exit /b 0
)
echo %~1
echo [%TIMESTAMP%] %~1 >> "%LOG_FILE%"
exit /b 0
