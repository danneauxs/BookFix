<#
.SYNOPSIS
    Builds the BookFix Windows installer.
.DESCRIPTION
    Downloads Python 3.12 embeddable, configures it for pip,
    stages all files, and runs Inno Setup to produce BookFix-Setup.exe.
.EXAMPLE
    .\build_installer.ps1
#>

param(
    [string]$ProjectRoot = (Resolve-Path "$PSScriptRoot\..\..").Path
)

$ErrorActionPreference = "Stop"

$BuildDir          = $PSScriptRoot
$StageDir          = "$BuildDir\build_stage"
$OutputDir         = "$BuildDir\output"
$PythonVersion     = "3.12.8"
$PythonZip         = "$BuildDir\python-$PythonVersion-embed-amd64.zip"
$PythonUrl         = "https://www.python.org/ftp/python/$PythonVersion/python-$PythonVersion-embed-amd64.zip"

# ---------- Find tools ----------
function Find-Tool {
    param([string]$Name, [string[]]$Paths)
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    foreach ($p in $Paths) {
        if (Test-Path $p) { return $p }
    }
    return $null
}

$ISCC  = Find-Tool "ISCC.exe" @(
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles}\Inno Setup 6\ISCC.exe"
)
$SevenZip = Find-Tool "7z" @("${env:ProgramFiles}\7-Zip\7z.exe")

Write-Host "=== BookFix Windows Installer Builder ===" -ForegroundColor Cyan
Write-Host ""

if (-not $ISCC) {
    Write-Host "ERROR: Inno Setup 6 not found." -ForegroundColor Red
    Write-Host "Download from: https://jrsoftware.org/isdl.php" -ForegroundColor Yellow
    exit 1
}
Write-Host "  Inno Setup : $ISCC" -ForegroundColor Green

if (-not $SevenZip) {
    Write-Host "ERROR: 7-Zip not found." -ForegroundColor Red
    Write-Host "Download from: https://www.7-zip.org/" -ForegroundColor Yellow
    exit 1
}
Write-Host "  7-Zip      : $SevenZip" -ForegroundColor Green

# ---------- Clean and create staging ----------
Write-Host "`n[1] Staging source files..." -ForegroundColor Yellow
if (Test-Path $StageDir) { Remove-Item -Recurse -Force $StageDir }
New-Item -ItemType Directory -Force -Path "$StageDir\output" | Out-Null

Copy-Item "$ProjectRoot\main.py"             "$StageDir\"
Copy-Item "$ProjectRoot\launcher.pyw"        "$StageDir\"
Copy-Item "$ProjectRoot\requirements.txt"    "$StageDir\"
Copy-Item "$ProjectRoot\README.md"          "$StageDir\"
Copy-Item -Recurse "$ProjectRoot\bookfix"    "$StageDir\bookfix"
Copy-Item -Recurse "$ProjectRoot\data"       "$StageDir\data"
Copy-Item -Recurse "$ProjectRoot\prompts"    "$StageDir\prompts"
Copy-Item "$BuildDir\installer.iss"          "$StageDir\"

Write-Host "  -> $StageDir" -ForegroundColor Green

# ---------- Download Python embeddable ----------
Write-Host "`n[2] Downloading Python $PythonVersion embeddable..." -ForegroundColor Yellow
if (-not (Test-Path $PythonZip)) {
    Write-Host "  Downloading from python.org..."
    Invoke-WebRequest -Uri $PythonUrl -OutFile $PythonZip
}
Write-Host "  $PythonZip ($([math]::Round((Get-Item $PythonZip).Length / 1MB, 1)) MB)" -ForegroundColor Green

# ---------- Extract and configure ----------
Write-Host "`n[3] Extracting and configuring Python..." -ForegroundColor Yellow
$PythonStage = "$StageDir\python"
New-Item -ItemType Directory -Force -Path $PythonStage | Out-Null
& $SevenZip x "$PythonZip" -o"$PythonStage" -y | Out-Null

# Enable site-packages in ._pth file
$PthFile = Get-ChildItem "$PythonStage\*._pth" | Select-Object -First 1
if ($PthFile) {
    (Get-Content $PthFile.FullName) -replace '#import site', 'import site' | Set-Content $PthFile.FullName
    Write-Host "  Enabled site import in $($PthFile.Name)" -ForegroundColor Green
}

# Install pip
$GetPip = "$BuildDir\get-pip.py"
if (-not (Test-Path $GetPip)) {
    Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile $GetPip
}
& "$PythonStage\python.exe" $GetPip --no-warn-script-location 2>&1 | Out-Null
Write-Host "  pip installed" -ForegroundColor Green

# ---------- Verify Python ----------
Write-Host "`n[4] Verifying Python..." -ForegroundColor Yellow
$ver = & "$PythonStage\python.exe" --version
Write-Host "  $ver" -ForegroundColor Green

# ---------- Build installer ----------
Write-Host "`n[5] Building installer..." -ForegroundColor Yellow
Push-Location $StageDir
try {
    & $ISCC "installer.iss" /O"$OutputDir"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Inno Setup failed (exit code $LASTEXITCODE)" -ForegroundColor Red
        exit 1
    }
} finally {
    Pop-Location
}

# ---------- Done ----------
Write-Host "`n=== Build complete! ===" -ForegroundColor Cyan
Get-ChildItem "$OutputDir\*.exe" | ForEach-Object {
    Write-Host "  $($_.Name)  —  $([math]::Round($_.Length / 1MB, 1)) MB" -ForegroundColor Green
}
