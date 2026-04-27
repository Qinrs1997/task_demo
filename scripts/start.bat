@echo off
setlocal

cd /d "%~dp0\.."

if "%APP_HOST%"=="" set "APP_HOST=127.0.0.1"
if "%APP_PORT%"=="" set "APP_PORT=8000"
if "%APP_RELOAD%"=="" set "APP_RELOAD=true"
if "%CONDA_ENV_NAME%"=="" set "CONDA_ENV_NAME=task_demo"
if "%PYTHON_VERSION%"=="" set "PYTHON_VERSION=3.10"
if "%CONDA_CHANNEL_ARGS%"=="" set "CONDA_CHANNEL_ARGS=--override-channels -c https://repo.anaconda.com/pkgs/main"

echo.
echo ========================================
echo   Task Management API
echo ========================================
echo   Conda env: %CONDA_ENV_NAME%
echo   Python:    %PYTHON_VERSION%
echo   Host:      %APP_HOST%
echo   Port:      %APP_PORT%
echo   Reload:    %APP_RELOAD%
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
        echo [TIP] If your conda mirror is unavailable, try:
        echo       set CONDA_CHANNEL_ARGS=--override-channels -c https://repo.anaconda.com/pkgs/main
        echo       scripts\start.bat
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

netstat -ano | findstr ":%APP_PORT% " | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo [WARN] Port %APP_PORT% is already in use.
    echo Change the port with: set APP_PORT=8001
    exit /b 1
)

echo [OK] Starting server
echo   API:  http://%APP_HOST%:%APP_PORT%/api/v1/tasks
echo   UI:   http://%APP_HOST%:%APP_PORT%/ui/
echo   Docs: http://%APP_HOST%:%APP_PORT%/docs
echo.

if /I "%APP_RELOAD%"=="true" (
    call conda run -n "%CONDA_ENV_NAME%" python -m uvicorn app.main:app --host %APP_HOST% --port %APP_PORT% --reload
) else (
    call conda run -n "%CONDA_ENV_NAME%" python -m uvicorn app.main:app --host %APP_HOST% --port %APP_PORT%
)

endlocal
