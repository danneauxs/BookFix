# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ⚠️ CRITICAL RULES - READ FIRST

### Token efficiency

Respond like smart caveman. Cut all filler, keep technical substance.

- Drop articles (a, an, the), filler (just, really, basically, actually).
- Drop pleasantries (sure, certainly, happy to).
- No hedging. Fragments fine. Short synonyms.
- Technical terms stay exact. Code blocks unchanged.
- Pattern: [thing] [action] [reason]. [next step].

### 1. ALWAYS USE THE VIRTUAL ENVIRONMENT

**EVERY SINGLE BASH COMMAND MUST BE RUN IN THE VENV.**

```bash
source venv/bin/activate && command_here
```

**NEVER run commands like:**

- `python` without first activating venv
- `pip install` outside the venv (even if you think you need to)
- Any command that could touch the system Python

Everything must stay isolated in `/home/danno/MyApps/BookFix/venv/`

### 2. NEVER MODIFY THE OS

No `sudo`, no `apt`/`brew`, no system-wide `pip install`, no modification of system paths or environment variables.

### 3. CHECK REQUIREMENTS FIRST

Before installing anything: check `requirements.txt`, then `source venv/bin/activate && pip list`. If missing, ask the user or add to `requirements.txt`.

---

## Project Overview

BookFix is a PyQt5-based modular ebook text processing application designed to prepare texts for Text-to-Speech (TTS) systems. It combines automatic rules (replacements, roman numerals, pagination, etc.) with AI-assisted interactive review for ambiguous cases (homographs, all-caps, numbers).

## Quick Start Commands

```bash
./run.sh                         # RECOMMENDED: activates venv and launches GUI
source venv/bin/activate && python main.py   # Manual equivalent
```

### Running Tests

```bash
source venv/bin/activate

# Top-level test scripts (headless/integration)
python test_pipeline.py
python test_batch_limit.py
python test_sound_effects.py
python test_scoring.py
python test_ai_choices.py
python test_headless_gui.py

# Structured tests in test/ directory
cd test && python -m pytest                  # Run all structured tests
python -m pytest test/test_mc_roman.py       # Single test file
python -m pytest test/test_filter_stages.py
```

### Installation (One-time Setup)

```bash
./install.sh                     # Creates venv, installs deps, downloads spaCy models

# Manual equivalent:
python3 -m venv venv
source venv/bin/activate
pip install -e .                 # Installs BookFix and all dependencies
```

**Note:** The homograph engine (`PipelineOrchestrator`) requires `en_core_web_md` (medium spaCy model). Basic features use `en_core_web_sm`. Both are installed via `pip install -e .` or `./install.sh`.

---

## Architecture Overview

### Core Processing Pipeline

The application processes text through **independent processors** in a strict order (defined in `bookfix/pipeline.py`):

1. **Automatic** (run by `pipeline.py`): `replacements` → `periods` → `roman` → `blanklines` → `lowercase` → `pagination`
2. **Interactive** (triggered by GUI buttons): `choices` → `allcaps` → `numbered`

Interactive processors are **not** run by `pipeline.py` — they are triggered by `bookfix/gui.py` and wait for user input before proceeding.

### Key Data Flow

- **`bookfix/context.py:BookfixContext`** — Central dataclass: holds `text`, `original_text`, configuration lists (`cap_ignore`, `roman_ignore`, `skip_choice`), `choice_definitions`, `replacements`, `ai_config`, and change history.
- **`bookfix/pipeline.py:run_processing()`** — Runs automatic processors sequentially; skips interactive ones.
- **`bookfix/gui.py:BookfixMainWindow`** — PyQt5 main window; coordinates file loading, automatic pipeline, and interactive processor buttons.

### Module Independence Principle

**Critical:** Each processor operates with **no shared state** between modules.

1. Processors receive the **current text** from context at call time — never cached text.
2. Position calculations always use the current text state.
3. When text changes, the next processor gets updated text automatically.

**Why this matters:** If a processor caches text or positions, subsequent processors will calculate wrong positions, breaking highlighting and editing.

### Homograph Disambiguation Engine

A newer, deterministic engine lives in `bookfix/` alongside the pipeline:

- **`bookfix/lexicon_loader.py:LexiconLoader`** — Loads `data/choices.json` and provides homograph lookups.
- **`bookfix/feature_extractor.py:FeatureExtractor`** — Extracts POS, contextual, and semantic features using spaCy `en_core_web_md`.
- **`bookfix/scoring_engine.py:ScoringEngine`** — Combines features with weighted scoring for deterministic homograph resolution.
- **`bookfix/pipeline_orchestrator.py:PipelineOrchestrator`** — Pre-loads all components; use `process_homograph(context_before, word, context_after)` as the main entry point.

This engine is separate from the interactive `choices.py` processor and is used for batch/non-interactive disambiguation.

### AI Integration

- **`bookfix/ai/service.py`** — Unified AI provider interface (Gemini, OpenAI, Claude); selected via `ai_config`.
- **`bookfix/ai/learning_storage.py`** — Persists learned patterns from user decisions across sessions.
- **`bookfix/ai/pos_tagger.py`** / **`bert_pos_tagger.py`** — POS tagging for context-aware decisions.
- **`bookfix/processors/ai_allcaps.py`** — Batches caps processing in groups of 20 (`CAPS_BATCH_SIZE = 20`) to avoid token limits.
- **`bookfix/processors/ai_roman.py`** — AI-assisted roman numeral validation; falls back to `roman.py` if AI init fails.
- **`bookfix/ai/review_window.py`** / **`change_dialog.py`** — UI dialogs for reviewing and accepting/rejecting AI suggestions.

### Standard Processor Patterns

**Automatic processor:**

```python
def process(self, ctx: BookfixContext) -> BookfixContext:
    ctx.text = modified_text
    return ctx
```

**Interactive processor:**

```python
def __init__(self):
    self.current_text: str = ""    # Always use fresh text
    self.text_edit_widget = None   # Set by GUI before process() is called

def process(self, ctx: BookfixContext):
    self.current_text = ctx.text   # Get current state
    # Find matches, apply highlighting, wait for user, update ctx.text
```

## Configuration

All config lives in `data/`:

- **`data/choices.json`** — Single source of truth for homograph definitions (replaces legacy `.data.txt`)
- **`data/replace.txt`** — Find/replace rules for `AutomaticReplacementProcessor`
- **`data/cap_ignore.txt`** — Acronyms/words to keep capitalized
- **`data/roman_ignore.txt`** — Strings to skip during roman numeral processing
- **`data/skip_choice.txt`** — Words to skip during homograph processing
- **`data/settings.txt`** — Application settings

Config is loaded into `BookfixContext` at startup. The application **does not auto-reload** config changes mid-session.

## DocDNA

This project has a `DocDNA/` folder. See global `~/.claude/CLAUDE.md` for full usage instructions.

DocDNA location: `BookFix/DocDNA/`
Database: `BookFix/DocDNA/docdna.db`

```bash
docdna-query /home/danno/MyApps/BookFix --function <name>
docdna-query /home/danno/MyApps/BookFix --search "<text>"
```

## Key Files Reference

| File                               | Purpose                                                 |
| ---------------------------------- | ------------------------------------------------------- |
| `main.py`                          | Application entry point                                 |
| `bookfix/gui.py`                   | PyQt5 main window                                       |
| `bookfix/pipeline.py`              | Automatic processing orchestration                      |
| `bookfix/context.py`               | Central data structure (`BookfixContext`)               |
| `bookfix/pipeline_orchestrator.py` | Homograph engine coordinator                            |
| `bookfix/scoring_engine.py`        | Weighted homograph scoring                              |
| `bookfix/feature_extractor.py`     | spaCy-based feature extraction                          |
| `bookfix/lexicon_loader.py`        | `data/choices.json` loader                              |
| `bookfix/processors/*.py`          | All processing modules                                  |
| `bookfix/ai/`                      | AI service, learning, review dialogs                    |
| `bookfix/widgets/`                 | Custom Qt widgets (editors, font controls)              |
| `data/choices.json`                | Homograph definitions                                   |
| `logs/`                            | Log analysis scripts (`caps.py`, `verify_decisions.py`) |

## Important Gotchas

1. **Position Caching**: Never store positions from a previous text state. Always recalculate in the current text.

2. **Text Widget Synchronization**: Interactive processors must update both the Qt text widget and `ctx.text`. The GUI auto-syncs after the processor completes.

3. **Interactive vs Automatic**: `pipeline.py` only runs automatic steps. Interactive steps are triggered by GUI buttons. Check `interactive_steps` in `pipeline.py`.

4. **Unicode Handling**: Use UTF-8 safe methods. Handle curly quotes (U+201C/U+201D) separately from straight quotes.

5. **AI Processor Fallback**: AI processors (`ai_roman.py`, `ai_allcaps.py`) fall back to rule-based versions if AI initialization fails — always preserve the fallback path.

6. **spaCy Model Size**: `PipelineOrchestrator` requires `en_core_web_md` (not `en_core_web_sm`) for semantic similarity scoring.

## Adding a New Processor

1. Create `bookfix/processors/new_processor.py` with the standard pattern above.
2. Register in `bookfix/pipeline.py`: add to `get_available_processors()` and `processing_order`.
3. For interactive processors: add a button in `bookfix/gui.py` and add the name to `interactive_steps`.
4. Test with top-level test scripts or add a file to `test/`.
