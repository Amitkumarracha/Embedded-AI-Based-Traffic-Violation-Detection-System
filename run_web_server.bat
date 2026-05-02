@echo off
REM ============================================================================
REM Traffic Violation Detection System - Web Server Launcher
REM ============================================================================

echo ============================================================================
echo Traffic Violation Detection System - Web Interface
echo ============================================================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup_windows.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if .env exists
if not exist ".env" (
    echo [WARNING] .env file not found, using default settings
)

REM Start the web server
echo Starting web server...
echo.
echo Web Interface will be available at:
echo   http://127.0.0.1:8000
echo.
echo Press Ctrl+C to stop the server
echo.

python web_server.py --host 127.0.0.1 --port 8000

pause
