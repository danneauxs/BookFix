@echo off
REM BookFix - Run directly from source (for development/testing on Windows)
REM This runs the launcher using the system Python (no build required)
cd /d "%~dp0..\.."
echo Working directory: %cd%
if not exist "venv" (
    echo First run: setting up virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -e .
    pip install torch==2.4.1 --index-url https://download.pytorch.org/whl/cpu
    python -m spacy download en_core_web_trf
    python -m spacy download en_core_web_md
) else (
    call venv\Scripts\activate.bat
)
python launcher.pyw
pause
