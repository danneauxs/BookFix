@echo off
setlocal enabledelayedexpansion

echo Script directory: %cd%
echo Starting Bookfix...

REM Change to script directory
cd /d "%~dp0"
echo Working directory: %cd%

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found in %cd%
    echo Please run install.bat first to create the virtual environment.
    pause
    exit /b 1
)

REM Check if activation script exists
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment activation script not found
    echo Virtual environment may be corrupted. Please run install.bat again.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Failed to activate virtual environment
    pause
    exit /b 1
)

echo Virtual environment activated

REM Check if main.py exists
if not exist "main.py" (
    echo main.py not found in current directory: %cd%
    pause
    exit /b 1
)

REM Run the application
echo Starting application...
python main.py
set EXITCODE=!errorlevel!

REM Show result
if !EXITCODE! equ 0 (
    echo Application completed successfully.
) else (
    echo Application exited with error code: !EXITCODE!
)

pause
