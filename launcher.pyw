#!/usr/bin/env python3
"""
BookFix Windows Launcher
First-run: installs PyTorch, spaCy, and language models (~1.4 GB)
Subsequent runs: launches BookFix immediately
Uses console output (no tkinter dependency).
"""
import sys
import os
import subprocess
from pathlib import Path


INSTALL_DIR = Path(__file__).resolve().parent
BUNDLED_PYTHON = INSTALL_DIR / "python" / "python.exe"
BUNDLED_PYTHONW = INSTALL_DIR / "python" / "pythonw.exe"
MAIN_PY = INSTALL_DIR / "main.py"
REQUIREMENTS_TXT = INSTALL_DIR / "requirements.txt"
SETUP_MARKER = INSTALL_DIR / ".setup_complete"
NOCONSOLE = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def run_cmd(cmd, label=""):
    """Run a command with streaming output."""
    if label:
        print(f"  {label}...")
        sys.stdout.flush()
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        creationflags=NOCONSOLE if sys.platform == "win32" else 0
    )
    for line in proc.stdout:
        line = line.strip()
        if line:
            print(f"    {line[:120]}")
    proc.wait()
    return proc


def run_setup():
    """Run first-time setup with console output."""
    print()
    print("=" * 60)
    print("  BookFix First-Time Setup")
    print("=" * 60)
    print()
    print("This will download PyTorch, spaCy, and language models (~1.4 GB).")
    print("It may take 5-10 minutes depending on your internet speed.")
    print()

    print("[1/5] Upgrading pip...")
    r = run_cmd(
        [str(BUNDLED_PYTHON), "-m", "pip", "install", "--upgrade", "pip"],
        "Upgrading pip"
    )
    if r.returncode != 0:
        print("  Warning: pip upgrade failed, continuing...")

    print("[2/5] Installing PyTorch (CPU-only, ~800 MB)...")
    r = run_cmd(
        [str(BUNDLED_PYTHON), "-m", "pip", "install", "torch==2.4.1",
         "--index-url", "https://download.pytorch.org/whl/cpu"],
        "Installing PyTorch"
    )
    if r.returncode != 0:
        print("  FAILED: PyTorch installation failed. Check internet connection.")
        input("\nPress Enter to exit...")
        return False

    print("[3/5] Installing remaining requirements...")
    if REQUIREMENTS_TXT.exists():
        r = run_cmd(
            [str(BUNDLED_PYTHON), "-m", "pip", "install", "-r", str(REQUIREMENTS_TXT)],
            "Installing requirements"
        )
        if r.returncode != 0:
            print("  Warning: some requirements had issues, continuing...")
    else:
        print("  Warning: requirements.txt not found, skipping...")

    print("[4/5] Downloading spaCy language model (en_core_web_trf)...")
    r = run_cmd(
        [str(BUNDLED_PYTHON), "-m", "spacy", "download", "en_core_web_trf"],
        "Downloading en_core_web_trf"
    )
    if r.returncode != 0:
        print("  Warning: trf model had issues, continuing...")

    print("[5/6] Downloading spaCy language model (en_core_web_md)...")
    r = run_cmd(
        [str(BUNDLED_PYTHON), "-m", "spacy", "download", "en_core_web_md"],
        "Downloading en_core_web_md"
    )
    if r.returncode != 0:
        print("  FAILED: Could not download en_core_web_md.")
        input("\nPress Enter to exit...")
        return False

    print("[6/6] Downloading spaCy language model (en_core_web_sm)...")
    r = run_cmd(
        [str(BUNDLED_PYTHON), "-m", "spacy", "download", "en_core_web_sm"],
        "Downloading en_core_web_sm"
    )
    if r.returncode != 0:
        print("  Warning: sm model had issues, continuing...")

    SETUP_MARKER.write_text("ok")
    print()
    print("=" * 60)
    print("  Setup complete! Launching BookFix...")
    print("=" * 60)
    print()
    return True


def main():
    if not MAIN_PY.exists():
        print(f"ERROR: main.py not found at: {MAIN_PY}")
        input("\nPress Enter to exit...")
        return 1

    if not BUNDLED_PYTHON.exists():
        print()
        print("=" * 60)
        print("  BookFix Install Error")
        print("=" * 60)
        print()
        print("python.exe not found in the install directory.")
        print("Please reinstall BookFix.")
        print()
        input("Press Enter to exit...")
        return 1

    if not SETUP_MARKER.exists():
        success = run_setup()
        if not success:
            return 1

    os.chdir(str(INSTALL_DIR))
    subprocess.run(
        [str(BUNDLED_PYTHONW), str(MAIN_PY)],
        creationflags=NOCONSOLE if sys.platform == "win32" else 0
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
