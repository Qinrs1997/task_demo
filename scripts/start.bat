@echo off
setlocal

cd /d "%~dp0\.."

set "STARTUP_CONFIG=config\startup.env"
if not exist "%STARTUP_CONFIG%" (
    echo [ERROR] Missing startup config: %STARTUP_CONFIG%
    exit /b 1
)

for /f "usebackq eol=# tokens=1,* delims==" %%A in ("%STARTUP_CONFIG%") do (
    if not "%%A"=="" if not defined %%A set "%%A=%%B"
)

if "%APP_HOST%"=="" goto missing_config
if "%APP_PORT%"=="" goto missing_config
if "%APP_RELOAD%"=="" goto missing_config
if "%KILL_PORT_ON_START%"=="" goto missing_config
if "%UVICORN_ACCESS_LOG%"=="" goto missing_config
if "%CONDA_ENV_NAME%"=="" goto missing_config
if "%PYTHON_VERSION%"=="" goto missing_config
if "%CONDA_CHANNEL_ARGS%"=="" goto missing_config
if "%UVICORN_ENV_FILE%"=="" goto missing_config

if not exist "%UVICORN_ENV_FILE%" (
    if exist ".env.example" (
        echo [INFO] Creating %UVICORN_ENV_FILE% from .env.example
        copy ".env.example" "%UVICORN_ENV_FILE%" >nul
    )
)

echo.
echo ========================================
echo   Task Management API
echo ========================================
echo   Config:    %STARTUP_CONFIG%
echo   App env:   %UVICORN_ENV_FILE%
echo   Conda env: %CONDA_ENV_NAME%
echo   Python:    %PYTHON_VERSION%
echo   Host:      %APP_HOST%
echo   Port:      %APP_PORT%
echo   Reload:    %APP_RELOAD%
echo   Kill port: %KILL_PORT_ON_START%
echo   Access log:%UVICORN_ACCESS_LOG%
echo ========================================

where conda >nul 2>&1
if errorlevel 1 (
    echo [ERROR] conda was not found in PATH.
    echo Please open Anaconda Prompt, or initialize conda for PowerShell/CMD.
    exit /b 1
)

call conda env list | findstr /R /C:"^%CONDA_ENV_NAME% " >nul 2>&1
if errorlevel 1 (
    echo [INFO] Creating conda environment: %CONDA_ENV_NAME%
    call conda create -y -n "%CONDA_ENV_NAME%" python=%PYTHON_VERSION% %CONDA_CHANNEL_ARGS%
    if errorlevel 1 (
        echo [ERROR] Failed to create conda environment.
        exit /b 1
    )
)

call conda run -n "%CONDA_ENV_NAME%" python -c "import fastapi, uvicorn, sqlalchemy, aiosqlite" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing dependencies into %CONDA_ENV_NAME%...
    call conda run -n "%CONDA_ENV_NAME%" python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies.
        exit /b 1
    )
)

call :free_port
if errorlevel 1 exit /b 1

set "UVICORN_ENV_ARGS="
if exist "%UVICORN_ENV_FILE%" set "UVICORN_ENV_ARGS=--env-file %UVICORN_ENV_FILE%"
set "UVICORN_ACCESS_LOG_ARGS="
if /I "%UVICORN_ACCESS_LOG%"=="false" set "UVICORN_ACCESS_LOG_ARGS=--no-access-log"

echo [OK] Starting server
echo   API:  http://%APP_HOST%:%APP_PORT%/api/v1/tasks
echo   UI:   http://%APP_HOST%:%APP_PORT%/ui/
echo   Docs: http://%APP_HOST%:%APP_PORT%/docs
echo.

if /I "%APP_RELOAD%"=="true" (
    call conda run -n "%CONDA_ENV_NAME%" python -m uvicorn app.main:app --host %APP_HOST% --port %APP_PORT% --reload %UVICORN_ENV_ARGS% %UVICORN_ACCESS_LOG_ARGS%
) else (
    call conda run -n "%CONDA_ENV_NAME%" python -m uvicorn app.main:app --host %APP_HOST% --port %APP_PORT% %UVICORN_ENV_ARGS% %UVICORN_ACCESS_LOG_ARGS%
)

endlocal
exit /b %ERRORLEVEL%

:missing_config
echo [ERROR] Missing required startup config.
echo Please edit %STARTUP_CONFIG%
exit /b 1

:free_port
set "PORT_IN_USE="
for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":%APP_PORT% " ^| findstr "LISTENING"') do (
    if not "%%P"=="0" (
        set "PORT_IN_USE=1"
        if /I "%KILL_PORT_ON_START%"=="true" (
            echo [WARN] Port %APP_PORT% is in use. Killing PID %%P...
            taskkill /F /T /PID %%P >nul 2>&1
        ) else (
            echo [ERROR] Port %APP_PORT% is already in use by PID %%P.
            echo Set KILL_PORT_ON_START=true in %STARTUP_CONFIG% or change APP_PORT.
            exit /b 1
        )
    )
)
if defined PORT_IN_USE (
    timeout /t 2 /nobreak >nul
    netstat -ano | findstr ":%APP_PORT% " | findstr "LISTENING" >nul 2>&1
    if not errorlevel 1 (
        echo [ERROR] Port %APP_PORT% is still in use after cleanup.
        exit /b 1
    )
)
exit /b 0
