@echo off
chcp 65001 >nul
setlocal

cd /d "%~dp0\.."

if not defined APP_HOST set "APP_HOST=127.0.0.1"
if not defined APP_PORT set "APP_PORT=8000"

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo   Task Management API
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
)

python -c "import fastapi, uvicorn, sqlalchemy, aiosqlite" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Installing dependencies...
    python -m pip install -r requirements.txt
)

echo [OK] Starting server
echo   API:  http://%APP_HOST%:%APP_PORT%/api/v1/tasks
echo   UI:   http://%APP_HOST%:%APP_PORT%/ui/
echo   Docs: http://%APP_HOST%:%APP_PORT%/docs
echo.

python -m uvicorn app.main:app --host %APP_HOST% --port %APP_PORT% --reload

endlocal
