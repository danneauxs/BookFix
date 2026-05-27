# Bookfix Launcher Script (Windows PowerShell)
# Run with: Right-click → Run with PowerShell, or open PowerShell and run this script

$ErrorActionPreference = "Stop"

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir
Write-Host "Script directory: $ScriptDir" -ForegroundColor Green

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Virtual environment not found in $(Get-Location)" -ForegroundColor Red
    Write-Host "Please run install.ps1 first to create the virtual environment." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if activation script exists
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "Virtual environment activation script not found at $(Get-Location)\venv\Scripts\Activate.ps1" -ForegroundColor Red
    Write-Host "Virtual environment may be corrupted. Please run install.ps1 again." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
Write-Host "Starting Bookfix..." -ForegroundColor Green
Write-Host "Working directory: $(Get-Location)" -ForegroundColor Green
Write-Host "Activating virtual environment..." -ForegroundColor Green

& "venv\Scripts\Activate.ps1"

Write-Host "Virtual environment activated" -ForegroundColor Green

# Check if main.py exists
if (-not (Test-Path "main.py")) {
    Write-Host "main.py not found in current directory: $(Get-Location)" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Run the application and capture exit code
Write-Host "Starting application..." -ForegroundColor Green
& python main.py
$exitCode = $LASTEXITCODE

# Show result and pause
if ($exitCode -eq 0) {
    Write-Host "Application completed successfully." -ForegroundColor Green
} else {
    Write-Host "Application exited with error code: $exitCode" -ForegroundColor Red
}

Read-Host "Press Enter to exit"
