# Bookfix Installation Script (Windows PowerShell)
# Run with: Right-click → Run with PowerShell, or open PowerShell and run this script

$ErrorActionPreference = "Stop"

Write-Host "Setting up Bookfix..." -ForegroundColor Green

# Detect Python
$PythonCmd = $null
if (Get-Command python3 -ErrorAction SilentlyContinue) {
    $PythonCmd = "python3"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    # Verify it's Python 3
    $version = & python --version 2>&1
    if ($version -match "Python 3") {
        $PythonCmd = "python"
    } else {
        Write-Host "Python 3 is required but only Python 2 found" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "Python is not installed or not in PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Using Python command: $PythonCmd" -ForegroundColor Green

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Green
    & $PythonCmd -m venv venv
} else {
    Write-Host "Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
& "venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Green
& python -m pip install --upgrade pip

# Install Bookfix in editable mode
Write-Host "Installing Bookfix and dependencies..." -ForegroundColor Green
& pip install -e .

# Install CPU-only PyTorch AFTER Bookfix to ensure it is not overridden
Write-Host "Installing PyTorch (CPU-only)..." -ForegroundColor Green
& pip install torch==2.4.1 --index-url https://download.pytorch.org/whl/cpu

# Download spaCy models explicitly
Write-Host "Downloading spaCy language models..." -ForegroundColor Green
& python -m spacy download en_core_web_trf
& python -m spacy download en_core_web_md

Write-Host "Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To run Bookfix:" -ForegroundColor Green
Write-Host "  .\run.ps1" -ForegroundColor Cyan

Read-Host "Press Enter to exit"
