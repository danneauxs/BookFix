# BookFix  Ebook Text Processing Tool v2.x

BookFix is a modular PyQt5-based application for **interactive ebook text cleanup**, designed specifically to prepare text for **Text-to-Speech (TTS)** systems. It combines automatic rules (replacements, roman numerals, pagination, etc.) with AI-assisted review windows for ambiguous cases.

---

## Features (Current Architecture)

- **Interactive Word Choices (Homographs)**  
  AI- and rule-driven disambiguation for words like `lead`, `read`, `close`, `live`, etc., with a dedicated review window.

- **All-Caps Processing (Acronyms vs Emphasis)**  
  Detects all-caps sequences and decides whether to keep them as acronyms (NASA, FBI) or convert to normal case (shouting/emphasis).

- **Numbered Line / Number Formatting (AI)**  
  Classifies numbers as YEARS, MILITARY TIME, CURRENCY, MEASUREMENT, GENERAL, etc., and converts them to natural spoken forms for TTS.

- **Automatic Text Processing**  
  - User-defined find/replace rules (from the `data/` directory).  
  - Roman numeral conversion with AI correction of false matches.  
  - Blank line cleanup.  
  - Controlled lowercase/title-case conversions for specific words.  
  - Pagination removal for TXT and HTML/XHTML.

- **AI Review Windows**  
  Central review dialogs where you can inspect, accept, edit, or reject proposed AI changes (choices, numbers, roman), with optional reasoning shown.

- **Real-time Highlighting & Context**  
  Visual feedback and context snippets around each suggested change.

- **Modular Architecture**  
  Independent processors that all operate on the current text state; no cross-module position sharing.

- **Enhanced Unicode Handling**  
  Better support for curly quotes, special characters, and mixed encodings.

For a user-friendly walkthrough of the GUI and review windows, see `manual.md`.

---

## Installation

### Requirements

- Python 3.8+ (3.7 may work but 3.8+ is recommended)
- PyQt5
- BeautifulSoup4 (for HTML/XHTML pagination handling)

### Option 1: Recommended Quick Start

From the project root:

```bash
./install.sh
```

This will:
- Create a virtual environment in `./venv` (if missing).
- Install BookFix in editable mode with all dependencies.
- Download the required spaCy model for AI features (if configured).

### Option 2: Manual Setup

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt

# Run application
python main.py
```

On Linux/macOS you can also use:

```bash
./run.sh
```

which will activate the venv and start the GUI.

---

## Usage (High Level)

1. **Launch BookFix**  
   Use `./run.sh` or `python main.py` inside the virtual environment.

2. **Choose Default Folder (first run)**  
   On first start you may be asked to choose a default folder for text files. This becomes the starting directory for the **Browse** dialog.

3. **Load a File**  
   Click **Browse…** and select a `.txt`, `.html`, or `.xhtml` file.

4. **Configure Processing Steps**  
   Toggle the checkboxes for: Replacements, Periods, Roman, Blanklines, Lowercase, Pagination, Choices, Allcaps, Numbered.  
   - Right-click a checkbox to run **only that step**.
   - Under **Choices** you can configure AI mode and context size.

5. **Start Processing**  
   Click **Start Processing**. Steps run in this order:

   1. Replacements  
   2. Periods  
   3. Roman (with optional AI correction)  
   4. Blanklines  
   5. Lowercase  
   6. Pagination  
   7. Choices (AI review)  
   8. Allcaps (AI review)  
   9. Numbered (AI review)

6. **Review AI Suggestions**  
   For Choices, Allcaps, and Numbered, a review window opens so you can:
   - Accept/reject suggestions.  
   - Edit replacements manually.  
   - Apply decisions to all identical cases.  
   - Optionally save decisions into the learning system.

7. **Save Output**  
   When all enabled steps are finished, click **Save Output** to write the processed text to a new file.

For detailed button-by-button behavior, see `manual.md`.

---

## Configuration (data/ Directory)

### Important: `.data.txt` is deprecated

Older versions stored all configuration in a single `.data.txt` file. The current version uses **split configuration files** in the `data/` directory.

- If `data/` exists, BookFix **prefers** these files.
- `.data.txt` is only used as a **legacy fallback** when `data/` is missing.

### Files in `data/`

All files live in the `data/` directory at the project root:

- `settings.txt` – application settings (default directory, AI options, etc.).
- `replace.txt` – automatic text replacement rules (largest rule set).
- `choice.txt` – homograph/heteronym choice definitions for the Choices module.
- `skip_choice.txt` – patterns where choices should be skipped (e.g. "close to").
- `upper_to_lower.txt` – words that should be converted from ALL‑CAPS to a title‑case form.
- `cap_ignore.txt` – words to **keep** in all caps (true acronyms) during allcaps processing.
- `roman_ignore.txt` – tokens that look like Roman numerals but should never be converted.

See `data/README.txt` for migration notes from `.data.txt`.

---

## Architecture Overview

### Processors (Non-Interactive)

Located under `bookfix/processors/`:

- `automatic.py` – bulk find/replace engine.
- `periods.py` – punctuation and period spacing cleanup.
- `roman.py` / `ai_roman.py` – Roman numeral handling with AI fixups.
- `blanklines.py` – blank line and whitespace cleanup.
- `lowercase.py` – controlled title-case conversions using UPPER_TO_LOWER.
- `pagination.py` – pagination and page number removal (TXT and HTML).

### Interactive & AI-Enhanced Processors

- `choices.py` / `ai_choices.py` – homograph/word-choice processing with AI and learning.
- `allcaps.py` / `ai_allcaps.py` / `ai_caps.py` – caps sequence detection and AI review.
- `numbered.py` / `ai_numbered.py` – numbered line and TTS formatting for numbers.
- `ai/pipeline.py` – `AIProcessingPipeline` and shared `AIChangeTracker` for recording changes.
- `ai/review_window.py` – main AI changes review window used by choices, numbers, etc.
- `widgets/*.py` – specialized Qt widgets for review editors and font controls.

---

## Development Notes

- Each processor operates on the **current** text only and does not cache positions across modules.
- All AI decisions are recorded via `AIChangeTracker` and must be explicitly accepted in review windows before being committed.
- Configuration changes (ignore lists, UPPER_TO_LOWER, etc.) are written back to files under `data/`.

To add a new processor, follow the existing patterns in `bookfix/processors/` and register it in `bookfix/pipeline.py` and `bookfix/gui.py`.

---



## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Keep changes consistent with the modular pipeline and AI review model.
4. Add or update tests under `test/` where appropriate.
5. Open a pull request describing your changes and rationale.
