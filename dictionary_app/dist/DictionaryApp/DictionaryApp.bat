@echo off
REM Dictionary App Launcher for Windows

REM Get the directory where this script is located
set DIR=%~dp0

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python 3 is required but not installed.
    echo Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "%DIR%venv" (
    echo Creating virtual environment...
    python -m venv "%DIR%venv"
    
    echo Installing core dependencies...
    "%DIR%venv\Scripts\pip" install -q -r "%DIR%requirements.txt"
    
    echo Installing plugin dependencies...
    REM Install dependencies for each plugin that has requirements.txt
    for /d %%d in ("%DIR%plugins\*") do (
        if exist "%%d\requirements.txt" (
            echo Installing dependencies for %%~nxd plugin...
            "%DIR%venv\Scripts\pip" install -q -r "%%d\requirements.txt"
        )
    )
    
    echo All dependencies installed!
)

REM Run the app
echo Starting Dictionary App...
"%DIR%venv\Scripts\python" "%DIR%run_app.py"
pause
