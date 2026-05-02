@echo off
REM ============================================================================
REM Traffic Violation Detection System - Windows Run Script
REM ============================================================================

echo ============================================================================
echo Embedded AI-Based Traffic Violation Detection System
echo Starting on Windows...
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

REM Run the application
echo Starting Traffic Violation Detection System...
echo Press Ctrl+C to stop
echo.

python run_edge.py %*

pause
