# BookFix Windows Installer — Build Instructions

## Prerequisites (install once)

1. **Python 3.12** — https://www.python.org/downloads/release/python-3128/
2. **Inno Setup 6** — https://jrsoftware.org/isdl.php
3. **7-Zip** — https://www.7-zip.org/

## Build

```powershell
# Open PowerShell, navigate to this folder
cd build/windows

# Run the build script
.\build_installer.ps1
```

The script will:
1. Download Python 3.12.8 embeddable (~30 MB, cached locally)
2. Enable pip in the embeddable distribution
3. Stage all source files (bookfix/, data/, launcher.pyw, main.py, etc.)
4. Run Inno Setup to produce `output/BookFix-Setup-2.0.0.exe`

## Output

`build/windows/output/BookFix-Setup-2.0.0.exe`

## What the installer does

- Installs to `%LOCALAPPDATA%\BookFix\`
- Bundles Python 3.12 embeddable + pip + all source files
- Creates Start Menu and (optionally) Desktop shortcuts
- **First run** of the app: downloads PyTorch CPU + spaCy models (~1.4 GB)
- **Subsequent runs**: launches instantly

## Dev testing

To test the launcher without building the installer (requires system Python):
```
run_dev.bat
```
