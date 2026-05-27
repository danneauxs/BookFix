@echo off
setlocal enabledelayedexpansion

set STATUS_VCREDIST=unknown
set STATUS_PYTHON=unknown
set STATUS_TORCH=unknown
set STATUS_BOOKFIX=unknown
set STATUS_SPACY_TRF=unknown
set STATUS_SPACY_MD=unknown
set PYTHON_VERSION=unknown

echo Setting up Bookfix...

REM Install Visual C++ Redistributable 2022 x64
echo Checking Visual C++ Redistributable 2022...
reg query "HKLM\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64" >nul 2>&1
if errorlevel 1 (
    echo Downloading Visual C++ Redistributable 2022...
    powershell -Command "Invoke-WebRequest -Uri 'https://aka.ms/vs/17/release/vc_redist.x64.exe' -OutFile '%TEMP%\vc_redist.x64.exe'"
    if exist "%TEMP%\vc_redist.x64.exe" (
        echo Installing Visual C++ Redistributable 2022...
        "%TEMP%\vc_redist.x64.exe" /install /quiet /norestart
        del "%TEMP%\vc_redist.x64.exe" >nul 2>&1
        echo VC++ Redistributable installed
        set STATUS_VCREDIST=installed
    ) else (
        echo VC++ Redistributable download failed
        set STATUS_VCREDIST=download_failed
    )
) else (
    echo VC++ Redistributable already installed
    set STATUS_VCREDIST=already_present
)

REM Detect Python
where python >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    set STATUS_PYTHON=not_found
    goto show_summary
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set VERSION=%%i
echo Using Python: !VERSION!

REM Check Python version - must be 3.10-3.12
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYVER=%%v
for /f "tokens=1,2 delims=." %%a in ('echo !PYVER!') do (
    set MAJOR=%%a
    set MINOR=%%b
)

if !MINOR! GEQ 13 (
    echo Python !PYVER! is not supported.
    echo Required: Python 3.10, 3.11, or 3.12
    echo Reason: pinned packages have no pre-built wheels for Python 3.13+
    echo.
    echo Download Python 3.12 from: https://www.python.org/downloads/release/python-3128/
    set STATUS_PYTHON=unsupported_version
    goto show_summary
)
echo Python version OK: !PYVER!
set PYTHON_VERSION=!PYVER!
set STATUS_PYTHON=ok

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment
        goto show_summary
    )
) else (
    echo Virtual environment already exists
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Failed to activate virtual environment
    goto show_summary
)

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo Failed to upgrade pip
    goto show_summary
)

REM Install Bookfix
echo Installing Bookfix and dependencies...
pip install -e .
if errorlevel 1 (
    echo Failed to install Bookfix
    set STATUS_BOOKFIX=failed
    goto show_summary
)
set STATUS_BOOKFIX=ok

REM Install CPU-only PyTorch AFTER Bookfix to ensure it is not overridden
echo Installing PyTorch CPU-only...
pip install torch==2.4.1 --index-url https://download.pytorch.org/whl/cpu
if errorlevel 1 (
    echo Failed to install PyTorch
    set STATUS_TORCH=failed
    goto show_summary
)
set STATUS_TORCH=ok

REM Download spaCy models
echo Downloading spaCy language models...
python -m spacy download en_core_web_trf
if errorlevel 1 (
    echo Failed to download en_core_web_trf
    set STATUS_SPACY_TRF=failed
    goto show_summary
)
set STATUS_SPACY_TRF=ok

python -m spacy download en_core_web_md
if errorlevel 1 (
    echo Failed to download en_core_web_md
    set STATUS_SPACY_MD=failed
    goto show_summary
)
set STATUS_SPACY_MD=ok

:show_summary

echo.
echo ========================================
echo   BOOKFIX INSTALLATION SUMMARY
echo ========================================
echo   Python version       : !PYTHON_VERSION!
echo   VC++ Redistributable : !STATUS_VCREDIST!
echo   PyTorch CPU          : !STATUS_TORCH!
echo   Bookfix package      : !STATUS_BOOKFIX!
echo   spaCy trf model      : !STATUS_SPACY_TRF!
echo   spaCy md model       : !STATUS_SPACY_MD!
echo ========================================

REM Write summary to install_log.txt
(
    echo BOOKFIX INSTALLATION LOG
    echo ========================================
    echo Installation Date: %DATE% %TIME%
    echo Python version       : !PYTHON_VERSION!
    echo VC++ Redistributable : !STATUS_VCREDIST!
    echo PyTorch CPU          : !STATUS_TORCH!
    echo Bookfix package      : !STATUS_BOOKFIX!
    echo spaCy trf model      : !STATUS_SPACY_TRF!
    echo spaCy md model       : !STATUS_SPACY_MD!
    echo ========================================
) > install_log.txt

if !STATUS_TORCH! == ok if !STATUS_BOOKFIX! == ok if !STATUS_SPACY_TRF! == ok if !STATUS_SPACY_MD! == ok (
    echo.
    echo Installation complete!
    echo.
    echo To run Bookfix:
    echo   run.bat
) else (
    echo.
    echo Installation incomplete. Check install_log.txt for details.
)

echo.
echo Log saved to: install_log.txt
echo.
pause
