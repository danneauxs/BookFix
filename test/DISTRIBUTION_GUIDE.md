# numtest Distribution Guide

## Package Overview

`numtest_standalone.zip` (88 KB) is a complete, self-contained number processing tool that can be distributed to other users.

**Key Facts:**
- ✓ No dependencies on parent BookFix project
- ✓ Works on Linux, macOS, Windows
- ✓ Requires only Python 3.8+ (no system packages)
- ✓ Ready to zip and share

## Distribution Package Contents

```
numtest_standalone/
├── process_numbers.py              (main entry point)
├── rules_processor.py              (rule-based number classification)
├── review_window.py                (PyQt5 review UI)
├── ai_numbered_processor.py        (AI number formatting)
├── numbered_processor.py           (core processor)
├── bookfix_logging.py              (logging utilities)
├── paths.py                        (path helpers)
├── ai/                             (self-contained AI service)
│   ├── service.py                  (unified AI interface)
│   ├── numbers_analyzer.py
│   ├── numbers_learning.py
│   ├── pos_tagger.py
│   ├── change_tracker.py
│   └── __init__.py
├── prompts/                        (number formatting templates)
│   ├── number_classification.txt
│   ├── number_classification_batch.txt
│   ├── number_formatting.txt
│   ├── numbered_line.txt
│   └── page_number.txt
├── ai_config.json                  (AI provider config)
├── requirements.txt                (pip dependencies)
├── install.sh / install.bat        (setup scripts)
├── run.sh / run.bat                (launcher scripts)
├── test_numbers_with_ai.sh / .bat  (interactive menu)
├── README.md                       (user documentation)
├── logs/                           (runtime output directory)
└── .ai_learning/                   (learning data storage)
```

## How to Distribute

### Option 1: Send the ZIP file directly
```bash
# Users simply unzip and run:
unzip numtest_standalone.zip
cd numtest_standalone
./install.sh    # Linux/macOS
# or
install.bat     # Windows
```

### Option 2: Upload to file sharing service
- GitHub Releases
- Google Drive
- Dropbox
- Your own web server

### Option 3: Create an installer script
Users can download and run in one step:
```bash
curl https://your-host/install-numtest.sh | bash
```

## User Setup Instructions

### Linux / macOS Users
```bash
# 1. Extract the package
unzip numtest_standalone.zip
cd numtest_standalone

# 2. Install dependencies (one-time)
./install.sh

# 3. Run the number processor
./run.sh input_file.txt --review
./run.sh input_file.txt --dry-run
```

### Windows Users
```bat
# 1. Extract the package
# (Right-click ZIP → Extract All)
# Open Command Prompt in the numtest_standalone folder

# 2. Install dependencies (one-time)
install.bat

# 3. Run the number processor
run.bat input_file.txt --review
run.bat input_file.txt --dry-run
```

## What Users Need

**Required:**
- Python 3.8 or later
- pip (included with Python 3.8+)

**Optional:**
- Ollama (for AI number formatting)
  - Or configure ai_config.json to use cloud providers (OpenAI, Gemini, Groq, etc.)

## Verification Checklist

✓ Package has been tested with fresh Python venv
✓ All imports work without parent BookFix directory
✓ Installation script downloads spaCy model
✓ Both Linux and Windows launchers included
✓ AI service is self-contained
✓ Configuration is included (ai_config.json)
✓ Complete documentation (README.md)
✓ 27 files, 88 KB compressed

## Testing the Package

To verify the package works on a new system:

```bash
# Extract to a clean location
unzip numtest_standalone.zip
cd numtest_standalone

# Run install
./install.sh

# Create a test file
cat > test.txt << 'EOF'
The temperature is 72 degrees. He was born in 1965.
EOF

# Test dry run
./run.sh test.txt --dry-run

# Should produce: logs/test_number_proposals.txt with number proposals
```

## Troubleshooting

**"command not found: ./run.sh"** (Linux/macOS)
- Make sure you extracted the ZIP file and are in the numtest_standalone directory
- On macOS, you may need to allow execution: `chmod +x *.sh`

**"python is not recognized"** (Windows)
- Python may not be in PATH. Run the full path: `C:\Python38\python.exe --version`
- Or reinstall Python with "Add Python to PATH" option checked

**"No module named 'spacy'"**
- Run `./install.sh` (or `install.bat`) first to install dependencies

**AI mode not working**
- Ensure Ollama is running: `ollama serve` in another terminal
- Or edit `ai_config.json` to use a cloud provider

## Size Notes

- Uncompressed: ~240 KB
- Compressed: 88 KB
- With venv after `./install.sh`: ~800 MB (most of this is spaCy model + Python packages)

The package itself is small; the venv created during installation is what takes most space.

## Future Integration

Once numtest is stable, it can be re-integrated into the main BookFix program. The modular design makes this straightforward — the entire `numtest/` directory can be imported as a submodule or merged into the main pipeline.

## Support

If users encounter issues:
1. Check the README.md included in the package
2. Verify Python version: `python --version` (should be 3.8+)
3. Ensure `./install.sh` completed without errors
4. Try the `--dry-run` mode to test without making changes

## Changelog

**Current Version:** 2026-05-18

**Key Features:**
- Rule-based number classification (spaCy NER + custom rules)
- AI-assisted formatting via Ollama, OpenAI, Gemini, Groq, etc.
- Interactive PyQt5 review window
- Multi-platform support (Linux, macOS, Windows)
- Completely standalone (no parent project dependencies)
- User learning patterns stored in `.ai_learning/`

**Next Steps for Integration:**
- Performance optimization for large files
- Batch processing improvements
- Re-integration into main BookFix GUI
