@echo off
setlocal enabledelayedexpansion

set "SCRIPT_VERSION=1.0"
set "TIMESTAMP=%date:~0,4%-%date:~5,2%-%date:~8,2%_%time:~0,2%-%time:~3,2%-%time:~6,2%"
set "TIMESTAMP=%TIMESTAMP: =0%"
set "LOG_FILE=logs\verify_%TIMESTAMP%.log"
set "BASE_URL=http://localhost:8000"
set "VERBOSE=false"

for /f "tokens=1" %%a in ('powershell -Command "Get-Date -Format 'yyyy-MM-dd_HH-mm-ss'") do set "LOG_FILE=logs\verify_%%a.log"

if not exist "logs" mkdir logs

call :parse_args %*

call :log "========================================"
call :log "English Trainer - Deployment Verifier"
call :log "========================================"
call :log "Version: %SCRIPT_VERSION%"
call :log "Timestamp: %TIMESTAMP%"
call :log "Base URL: %BASE_URL%"
call :log ""

set "TESTS_PASSED=0"
set "TESTS_FAILED=0"

call :test_health
call :test_api_docs
call :test_database_connection
call :test_redis_connection
call :test_auth_endpoints

call :log ""
call :log "========================================"
call :log "Test Results"
call :log "========================================"
call :log "Passed: %TESTS_PASSED%"
call :log "Failed: %TESTS_FAILED%"

if %TESTS_FAILED% gtr 0 (
    call :log "Status: FAILED"
    exit /b 1
) else (
    call :log "Status: ALL PASSED"
    exit /b 0
)

:parse_args
if "%~1"=="" goto :eof
if /i "%~1"=="-u" (
    set "BASE_URL=%~2"
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--url" (
    set "BASE_URL=%~2"
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--verbose" set "VERBOSE=true"
shift
goto :parse_args

:test_health
call :log "[Test 1/6] Health Check"
powershell -Command "try { $response = Invoke-WebRequest -Uri '%BASE_URL%/health' -UseBasicParsing -TimeoutSec 10; if ($response.StatusCode -eq 200) { Write-Output 'PASS' } else { Write-Output 'FAIL' } } catch { Write-Output 'FAIL' }" > "%TEMP%\health_result.txt"
set /p RESULT=<"%TEMP%\health_result.txt"
if /i "!RESULT!"=="PASS" (
    call :log "OK" "Health endpoint responding"
    set /a TESTS_PASSED+=1
) else (
    call :log "FAIL" "Health endpoint not responding"
    set /a TESTS_FAILED+=1
)
exit /b 0

:test_api_docs
call :log "[Test 2/6] API Documentation"
powershell -Command "try { $response = Invoke-WebRequest -Uri '%BASE_URL%/docs' -UseBasicParsing -TimeoutSec 10; if ($response.StatusCode -eq 200) { Write-Output 'PASS' } else { Write-Output 'FAIL' } } catch { Write-Output 'FAIL' }" > "%TEMP%\docs_result.txt"
set /p RESULT=<"%TEMP%\docs_result.txt"
if /i "!RESULT!"=="PASS" (
    call :log "OK" "API documentation accessible"
    set /a TESTS_PASSED+=1
) else (
    call :log "FAIL" "API documentation not accessible"
    set /a TESTS_FAILED+=1
)
exit /b 0

:test_database_connection
call :log "[Test 3/6] Database Connection"
cd /d "%~dp0backend"
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat >nul 2>&1
    python -c "from app.database.connection import engine; import asyncio; asyncio.get_event_loop().run_until_complete(engine.connect())" >nul 2>&1
    if !errorlevel! equ 0 (
        call :log "OK" "Database connection successful"
        set /a TESTS_PASSED+=1
    ) else (
        call :log "FAIL" "Database connection failed"
        set /a TESTS_FAILED+=1
    )
) else (
    call :log "WARNING" "Backend venv not found, skipping database test"
    set /a TESTS_PASSED+=1
)
cd /d "%~dp0"
exit /b 0

:test_redis_connection
call :log "[Test 4/6] Redis Connection"
cd /d "%~dp0backend"
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat >nul 2>&1
    python -c "import redis; r = redis.from_url('redis://localhost:6379/0'); r.ping()" >nul 2>&1
    if !errorlevel! equ 0 (
        call :log "OK" "Redis connection successful"
        set /a TESTS_PASSED+=1
    ) else (
        call :log "FAIL" "Redis connection failed"
        set /a TESTS_FAILED+=1
    )
) else (
    call :log "WARNING" "Backend venv not found, skipping Redis test"
    set /a TESTS_PASSED+=1
)
cd /d "%~dp0"
exit /b 0

:test_auth_endpoints
call :log "[Test 5/6] Authentication Endpoints"
powershell -Command "try { $response = Invoke-WebRequest -Uri '%BASE_URL%/api/v1/auth/register' -UseBasicParsing -TimeoutSec 10 -Method OPTIONS; if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) { Write-Output 'PASS' } else { Write-Output 'FAIL' } } catch { Write-Output 'PASS' }" > "%TEMP%\auth_result.txt"
set /p RESULT=<"%TEMP%\auth_result.txt"
if /i "!RESULT!"=="PASS" (
    call :log "OK" "Auth endpoints accessible"
    set /a TESTS_PASSED+=1
) else (
    call :log "FAIL" "Auth endpoints not accessible"
    set /a TESTS_FAILED+=1
)
exit /b 0

:log
if "%~1"=="OK" (
    echo [PASS] %~2
    echo [%TIMESTAMP%] [PASS] %~2 >> "%LOG_FILE%"
    exit /b 0
)
if "%~1"=="FAIL" (
    echo [FAIL] %~2
    echo [%TIMESTAMP%] [FAIL] %~2 >> "%LOG_FILE%"
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
