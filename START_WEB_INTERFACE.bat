@echo off
REM ============================================================================
REM Traffic Violation Detection System - Quick Start Web Interface
REM ============================================================================

echo.
echo ============================================================================
echo    TRAFFIC VIOLATION DETECTION SYSTEM - WEB INTERFACE
echo ============================================================================
echo.
echo Starting web server...
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo.
    echo Please run setup_windows.bat first to install dependencies.
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Start the web server
echo Web Interface will be available at:
echo.
echo    ╔════════════════════════════════════════╗
echo    ║  http://127.0.0.1:8080                 ║
echo    ╚════════════════════════════════════════╝
echo.
echo Opening browser in 3 seconds...
echo.
echo Press Ctrl+C to stop the server
echo.
echo ============================================================================
echo.

REM Wait 3 seconds then open browser
timeout /t 3 /nobreak >nul
start http://127.0.0.1:8080

REM Start the server
python web_server.py --host 127.0.0.1 --port 8080

pause
