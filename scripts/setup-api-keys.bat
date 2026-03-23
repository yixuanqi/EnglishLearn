@echo off
setlocal enabledelayedexpansion

echo ================================================
echo English Trainer - API Configuration Setup
echo ================================================
echo.

echo This script will help you configure the API keys.
echo.
echo To obtain the required keys:
echo.
echo 1. Azure OpenAI: https://portal.azure.com -> Search "Azure OpenAI"
echo 2. Azure Speech:  https://portal.azure.com -> Search "Speech"
echo 3. OpenAI:        https://platform.openai.com/api-keys
echo.
echo ================================================
echo.

set /p AZURE_OPENAI_KEY="Azure OpenAI API Key (or press Enter to skip): "
set /p AZURE_OPENAI_ENDPOINT="Azure OpenAI Endpoint (or press Enter to skip): "
set /p OPENAI_KEY="OpenAI API Key (or press Enter to skip): "
set /p AZURE_SPEECH_KEY="Azure Speech Key: "
set /p AZURE_SPEECH_REGION="Azure Speech Region [eastus]: "

if "%AZURE_SPEECH_REGION%"=="" set "AZURE_SPEECH_REGION=eastus"

echo.
echo ================================================
echo Configuration Summary
echo ================================================
echo.

if not "%AZURE_OPENAI_KEY%"=="" (
    echo Azure OpenAI Key: ****%AZURE_OPENAI_KEY:~-4%
) else (
    echo Azure OpenAI Key: Not configured
)

if not "%OPENAI_KEY%"=="" (
    echo OpenAI Key: ****%OPENAI_KEY:~-4%
) else (
    echo OpenAI Key: Not configured
)

if not "%AZURE_SPEECH_KEY%"=="" (
    echo Azure Speech Key: ****%AZURE_SPEECH_KEY:~-4%
) else (
    echo Azure Speech Key: Not configured
)

echo Azure Speech Region: %AZURE_SPEECH_REGION%
echo.

set /p CONFIRM="Save configuration to .env? (Y/N): "
if /i not "%CONFIRM%"=="Y" (
    echo Configuration cancelled.
    exit /b 0
)

echo.

if exist ".env" (
    echo Backing up existing .env to .env.backup
    copy ".env" ".env.backup"
)

(
echo APP_NAME=English Trainer API
echo APP_VERSION=1.0.0
echo DEBUG=false
echo.
echo DATABASE_URL=sqlite+aiosqlite:///./english_trainer.db
echo REDIS_URL=redis://localhost:6379/0
echo.
echo JWT_SECRET_KEY=your_very_secure_jwt_secret_key_change_in_production
echo JWT_ALGORITHM=HS256
echo JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
echo JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
echo.
) > ".env"

if not "%AZURE_OPENAI_KEY%"=="" (
    (
    echo AZURE_OPENAI_API_KEY=%AZURE_OPENAI_KEY%
    echo AZURE_OPENAI_ENDPOINT=%AZURE_OPENAI_ENDPOINT%
    echo AZURE_OPENAI_DEPLOYMENT=gpt-4
    echo LLM_PROVIDER=azure
    ) >> ".env"
) else if not "%OPENAI_KEY%"=="" (
    (
    echo OPENAI_API_KEY=%OPENAI_KEY%
    echo LLM_PROVIDER=openai
    ) >> ".env"
)

if not "%AZURE_SPEECH_KEY%"=="" (
    (
    echo AZURE_SPEECH_KEY=%AZURE_SPEECH_KEY%
    echo AZURE_SPEECH_REGION=%AZURE_SPEECH_REGION%
    ) >> ".env"
)

(
echo STRIPE_SECRET_KEY=your_stripe_secret_key_here
echo.
echo APPLE_SHARED_SECRET=your_apple_shared_secret_here
echo GOOGLE_PACKAGE_NAME=com.englishtrainer.app
echo GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"your-project-id"}
echo.
echo CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]
echo.
echo LOG_LEVEL=INFO
echo ENVIRONMENT=development
) >> ".env"

echo Configuration saved to .env
echo.
echo Next steps:
echo 1. Run test-ai-services.bat to verify your configuration
echo 2. Run start-backend.bat to start the backend
echo.

pause
