#!/bin/bash
# BookFix Windows Installer Builder
# Builds the Windows .exe installer from Linux using wine + Inno Setup
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BUILD_DIR="$SCRIPT_DIR"
STAGE_DIR="$BUILD_DIR/build_stage"
OUTPUT_DIR="$BUILD_DIR/output"
PYTHON_VERSION="3.12.8"
PYTHON_ARCH="amd64"  # 64-bit required for PyTorch
PYTHON_ZIP="$BUILD_DIR/python-$PYTHON_VERSION-embed-$PYTHON_ARCH.zip"
PYTHON_URL="https://www.python.org/ftp/python/$PYTHON_VERSION/python-$PYTHON_VERSION-embed-$PYTHON_ARCH.zip"

WINEPREFIX="${WINEPREFIX:-$HOME/.wine-bookfix64}"
WINEARCH="win64"
export WINEPREFIX WINEARCH

echo "=== BookFix Windows Installer Builder ==="
echo ""

# ---------- Prerequisites ----------
echo "[1] Checking prerequisites..."

# Find wine64 binary
WINE64=""
if command -v wine64 &> /dev/null; then
    WINE64="wine64"
elif [ -x "/usr/lib/wine/wine64" ]; then
    WINE64="/usr/lib/wine/wine64"
else
    echo "ERROR: wine64 not found. Install with: sudo apt install wine64"
    exit 1
fi
echo "  wine64 found: $($WINE64 --version)"

# Initialize wine prefix if needed
if [ ! -f "$WINEPREFIX/system.reg" ]; then
    echo "  Initializing 64-bit wine prefix..."
    WINEPREFIX="$WINEPREFIX" WINEARCH="$WINEARCH" $WINE64 wineboot --init 2>/dev/null || true
fi

if [ ! -f "$WINEPREFIX/drive_c/Program Files/Inno Setup 6/ISCC.exe" ]; then
    echo "  Installing Inno Setup 6 via wine64..."
    wget -q "https://jrsoftware.org/download.php/is.exe" -O /tmp/is.exe
    WINEPREFIX="$WINEPREFIX" $WINE64 /tmp/is.exe /VERYSILENT /SUPPRESSMSGBOXES /NORESTART \
        /DIR="C:\\Program Files\\Inno Setup 6" 2>/dev/null
    rm /tmp/is.exe
    echo "  Inno Setup 6 installed"
else
    echo "  Inno Setup 6: already installed"
fi

# ---------- Stage source files ----------
echo ""
echo "[2] Staging source files..."

rm -rf "$STAGE_DIR"
mkdir -p "$STAGE_DIR/output"

cp "$PROJECT_ROOT/main.py" "$STAGE_DIR/"
cp "$PROJECT_ROOT/launcher.pyw" "$STAGE_DIR/"
cp "$PROJECT_ROOT/requirements.txt"    "$STAGE_DIR/"
cp "$PROJECT_ROOT/README.md"          "$STAGE_DIR/"
cp -r "$PROJECT_ROOT/bookfix"    "$STAGE_DIR/bookfix"
cp -r "$PROJECT_ROOT/data" "$STAGE_DIR/data"
cp -r "$PROJECT_ROOT/prompts" "$STAGE_DIR/prompts"
cp "$BUILD_DIR/installer.iss" "$STAGE_DIR/"
echo "  -> $STAGE_DIR"

# ---------- Download Python embeddable ----------
echo ""
echo "[3] Downloading Python $PYTHON_VERSION embeddable ($PYTHON_ARCH)..."

if [ ! -f "$PYTHON_ZIP" ]; then
    wget -q --show-progress "$PYTHON_URL" -O "$PYTHON_ZIP"
    echo "  Downloaded to: $PYTHON_ZIP"
else
    echo "  Already cached: $PYTHON_ZIP"
fi

# ---------- Extract and configure ----------
echo ""
echo "[4] Extracting and configuring Python..."

PYTHON_STAGE="$STAGE_DIR/python"
mkdir -p "$PYTHON_STAGE"
unzip -qo "$PYTHON_ZIP" -d "$PYTHON_STAGE"

# Enable site-packages in ._pth file
PTH_FILE=$(ls "$PYTHON_STAGE"/*._pth 2>/dev/null | head -1)
if [ -n "$PTH_FILE" ]; then
    sed -i 's/^#import site/import site/' "$PTH_FILE"
    echo "  Enabled site import in $(basename "$PTH_FILE")"
fi

# Install pip
GET_PIP="$BUILD_DIR/get-pip.py"
if [ ! -f "$GET_PIP" ]; then
    wget -q "https://bootstrap.pypa.io/get-pip.py" -O "$GET_PIP"
fi
WINEPREFIX="$WINEPREFIX" $WINE64 "$PYTHON_STAGE/python.exe" "$GET_PIP" --no-warn-script-location 2>/dev/null
echo "  pip installed"

# Install certifi for SSL certificates
WINEPREFIX="$WINEPREFIX" $WINE64 "$PYTHON_STAGE/python.exe" -m pip install certifi --no-warn-script-location 2>/dev/null
echo "  certifi installed (SSL certificates)"

# Verify
python_ver=$(WINEPREFIX="$WINEPREFIX" $WINE64 "$PYTHON_STAGE/python.exe" --version 2>/dev/null)
echo "  $python_ver"

# ---------- Build ----------
echo ""
echo "[5] Building installer..."

pushd "$STAGE_DIR" > /dev/null
WINEPREFIX="$WINEPREFIX" $WINE64 "C:\\Program Files\\Inno Setup 6\\ISCC.exe" "installer.iss" /O"$OUTPUT_DIR" 2>&1
popd > /dev/null

# ---------- Done ----------
echo ""
echo "=== Build complete! ==="
ls -lh "$OUTPUT_DIR"/*.exe 2>/dev/null || echo "  No .exe found in output/"
