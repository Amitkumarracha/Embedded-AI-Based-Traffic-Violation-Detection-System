@echo off
REM ============================================================================
REM Traffic Violation Detection System - Windows Setup Script
REM ============================================================================

echo ============================================================================
echo Embedded AI-Based Traffic Violation Detection System
echo Windows Setup Script
echo ============================================================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.9 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [1/6] Python found
python --version

REM Create virtual environment
echo.
echo [2/6] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)

REM Activate virtual environment
echo.
echo [3/6] Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo [4/6] Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo.
echo [5/6] Installing dependencies...
echo This may take several minutes...
pip install -r requirements_windows.txt

REM Create necessary directories
echo.
echo [6/6] Creating project directories...
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "evidence" mkdir evidence

echo.
echo ============================================================================
echo Setup Complete!
echo ============================================================================
echo.
echo Next steps:
echo 1. Activate virtual environment: venv\Scripts\activate
echo 2. Test camera: python scripts\test_camera.py
echo 3. Run the system: python run_edge.py
echo.
echo For video file testing: python run_edge.py --video path\to\video.mp4
echo For headless mode: python run_edge.py --no-display
echo.
pause
