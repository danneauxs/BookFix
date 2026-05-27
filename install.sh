#!/bin/bash

# Bookfix Installation Script
# This script sets up a Python virtual environment and installs dependencies

# Initialize status tracking
STATUS_PYTHON="unknown"
STATUS_TORCH="unknown"
STATUS_BOOKFIX="unknown"
STATUS_SPACY_TRF="unknown"
STATUS_SPACY_MD="unknown"
PYTHON_VERSION="unknown"

echo "🔧 Setting up Bookfix..."

# Detect Python command
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    # Check if it's Python 3
    if python -c "import sys; exit(0 if sys.version_info[0] == 3 else 1)" 2>/dev/null; then
        PYTHON_CMD="python"
    else
        echo "❌ Python 3 is required but only Python 2 found"
        STATUS_PYTHON="wrong_version"
        goto_summary=1
    fi
else
    echo "❌ Python is not installed or not in PATH"
    STATUS_PYTHON="not_found"
    goto_summary=1
fi

if [ -z "$goto_summary" ]; then
    echo "✅ Using Python command: $PYTHON_CMD"
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
    STATUS_PYTHON="ok"

    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "🏗️ Creating virtual environment..."
        $PYTHON_CMD -m venv venv
    else
        echo "✅ Virtual environment already exists"
    fi

    # Activate virtual environment
    echo "🔌 Activating virtual environment..."
    source venv/bin/activate

    # Upgrade pip
    echo "⬆️ Upgrading pip..."
    pip install --upgrade pip

    # Install Bookfix in editable mode (includes dependencies and spaCy model)
    echo "📦 Installing Bookfix and dependencies..."
    if pip install -e .; then
        STATUS_BOOKFIX="ok"
    else
        STATUS_BOOKFIX="failed"
    fi

    # Install CPU-only PyTorch AFTER Bookfix to ensure it is not overridden
    echo "📦 Installing PyTorch (CPU-only)..."
    if pip install torch==2.4.1 --index-url https://download.pytorch.org/whl/cpu; then
        STATUS_TORCH="ok"
    else
        STATUS_TORCH="failed"
    fi

    # Download spaCy models explicitly
    echo "📦 Downloading spaCy language models..."
    if python -m spacy download en_core_web_trf; then
        STATUS_SPACY_TRF="ok"
    else
        STATUS_SPACY_TRF="failed"
    fi

    if python -m spacy download en_core_web_md; then
        STATUS_SPACY_MD="ok"
    else
        STATUS_SPACY_MD="failed"
    fi
fi

# Print summary
echo ""
echo "========================================"
echo "  BOOKFIX INSTALLATION SUMMARY"
echo "========================================"
echo "  Python version       : $PYTHON_VERSION"
echo "  PyTorch (CPU)        : $STATUS_TORCH"
echo "  Bookfix package      : $STATUS_BOOKFIX"
echo "  spaCy trf model      : $STATUS_SPACY_TRF"
echo "  spaCy md model       : $STATUS_SPACY_MD"
echo "========================================"

# Write summary to install_log.txt
{
    echo "BOOKFIX INSTALLATION LOG"
    echo "========================================"
    echo "Installation Date: $(date)"
    echo "Python version       : $PYTHON_VERSION"
    echo "PyTorch (CPU)        : $STATUS_TORCH"
    echo "Bookfix package      : $STATUS_BOOKFIX"
    echo "spaCy trf model      : $STATUS_SPACY_TRF"
    echo "spaCy md model       : $STATUS_SPACY_MD"
    echo "========================================"
} > install_log.txt

if [ "$STATUS_TORCH" = "ok" ] && [ "$STATUS_BOOKFIX" = "ok" ] && [ "$STATUS_SPACY_TRF" = "ok" ] && [ "$STATUS_SPACY_MD" = "ok" ]; then
    echo ""
    echo "✅ Installation complete!"
    echo ""
    echo "📝 Note: Phonetic analysis was removed due to poor accuracy"
    echo "📖 See phoneticreplacement.txt for details"
    echo ""
    echo "To run Bookfix:"
    echo "  ./run.sh"
else
    echo ""
    echo "❌ Installation incomplete. Check install_log.txt for details."
fi

echo ""
echo "Log saved to: install_log.txt"
