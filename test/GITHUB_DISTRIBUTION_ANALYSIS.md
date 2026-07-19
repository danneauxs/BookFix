# BookFix GitHub Distribution Package Analysis
**Generated:** 2026-06-21  
**Project:** BookFix - Ebook Text Processing for TTS  
**Status:** Complete deployment inventory for production release

---

## Executive Summary

BookFix is a PyQt5-based ebook text processor for Text-to-Speech preparation. Total codebase: **22,399 lines of Python code** across 61 files. This document provides the complete file inventory for creating a production-ready GitHub distribution package.

**Key constraint:** Virtual environment and AI models (spaCy, RoBERTa) are downloaded during `install`, not included in the repo.

---

## 1. ROOT-LEVEL FILES TO INCLUDE

### Required
| File | Purpose | Size | Status |
|------|---------|------|--------|
| `main.py` | Application entry point | 1.6 KB | ✅ Required |
| `requirements.txt` | Python dependencies | 399 B | ✅ Required |
| `setup.py` | Package installer with post-install spaCy download | 2.1 KB | ✅ Required |
| `run.sh` | Unix/Linux/macOS launcher | 1.8 KB | ✅ Required |
| `install.sh` | Unix/Linux/macOS installer | 1.4 KB | ✅ Required |
| `run.bat` | Windows CMD launcher | 1.2 KB | ✅ Required |
| `run.ps1` | Windows PowerShell launcher | 2.0 KB | ✅ Required |
| `install.bat` | Windows CMD installer | 5.0 KB | ✅ Required |
| `install.ps1` | Windows PowerShell installer | 2.2 KB | ✅ Required |
| `README.md` | Project overview & quick start | 12 KB | ✅ Required |
| `LICENSE` | Project license (Apache 2.0) | 11.2 KB | ✅ Required |
| `CLAUDE.md` | Development guidelines for Claude Code | 10 KB | ✅ Required |

### Documentation (Recommended)
| File | Purpose | Status |
|------|---------|--------|
| `AGENTS.md` | Agent integration guide | ⭕ Optional |
| `manual.md` | User manual | ⭕ Optional |
| `GEMINI.md` | Gemini API integration notes | ⭕ Optional |
| `WARP.md` | Project history/evolution | ⭕ Optional |

### DO NOT INCLUDE
- `project_state.json` (session tracking, user-specific)
- `CountCodeLines.py` (development utility)
- `.aider.chat.history.md` (Aider IDE history)
- `.mcp.json`, `.opencode.json` (Claude Code local config)
- `session-ses_*.md` (session transcripts)
- All `.txt` test files in root (local testing only)
- All `.bak`, `.~` backup files
- `BookFix052526fINAL.tar.gz` (old archive)

---

## 2. BOOKFIX PACKAGE DIRECTORY

Complete Python module structure. All files are required unless marked.

### Directory Tree
```
bookfix/
├── __init__.py                          (pkg marker)
├── context.py                           (BookfixContext dataclass - CRITICAL)
├── pipeline.py                          (Automatic processor orchestration)
├── gui.py                               (PyQt5 main window)
├── logging.py                           (Application logging setup)
├── lexicon_loader.py                    (choices.json loader)
├── datafile.py                          (Data file utilities)
│
├── config/
│   ├── ai_config.json                   (AI provider config template)
│   ├── ai_config.json~                  (EXCLUDE: backup)
│   └── ai_config.json (copy)            (EXCLUDE: backup)
│
├── processors/                          (Automatic + interactive text processors)
│   ├── __init__.py
│   ├── automatic.py                     (Orchestrates automatic stages)
│   ├── blanklines.py                    (Blank line normalization)
│   ├── periods.py                       (Period handling)
│   ├── roman.py                         (Roman numeral processing)
│   ├── pagination.py                    (Page number handling)
│   ├── lowercase.py                     (Lowercase conversion)
│   ├── choices.py                       (Interactive: homograph selection)
│   ├── allcaps.py                       (Caps word identification)
│   ├── numbered.py                      (Number word formatting)
│   ├── ai_choices.py                    (AI-assisted homograph review)
│   ├── ai_allcaps.py                    (AI-assisted caps processing)
│   ├── ai_numbered.py                   (AI-assisted number formatting)
│   ├── ai_fragment.py                   (Fragment detection)
│   ├── ai_page.py                       (Page marker detection)
│   ├── rules_processor.py                (Currency/number rule engine)
│   ├── review_changes.log                (EXCLUDE: runtime log)
│   └── __pycache__/                     (EXCLUDE: compiled bytecode)
│
├── ai/                                  (AI integration & learning)
│   ├── __init__.py
│   ├── service.py                       (Unified AI provider interface: Claude/Gemini/OpenAI)
│   ├── pos_tagger.py                    (POS tagging wrapper)
│   ├── pos_dictionary.py                (POS-based rule dictionary)
│   ├── bert_pos_tagger.py               (RoBERTa POS tagging)
│   ├── hybrid_deciders.py               (Deterministic homograph deciders - 23 functions)
│   ├── learning_storage.py              (Learned patterns persistence)
│   ├── learning_analyzer.py             (Learning pattern analysis)
│   ├── caps_learning.py                 (Caps case learning)
│   ├── choices_learning.py              (Homograph learning)
│   ├── keyword_learning.py              (Keyword extraction)
│   ├── numbers_learning.py              (Number pattern learning)
│   ├── change_tracker.py                (Change history tracking)
│   ├── review_window.py                 (Interactive review dialog - PyQt5)
│   ├── change_dialog.py                 (Change detail dialog - PyQt5)
│   ├── edit_dialog.py                   (Edit dialog - PyQt5)
│   ├── review_editor.py                 (Review text editor)
│   ├── replace_dialog.py                (Replacement dialog)
│   ├── number_review_window.py          (Number review UI - PyQt5)
│   ├── tracker.py                       (Change tracking utilities)
│   ├── pipeline.py                      (AI processor pipeline)
│   │
│   └── analyzers/                       (LLM prompt builders)
│       ├── __init__.py
│       ├── base.py                      (Base analyzer class)
│       ├── homograph.py                 (Homograph analysis prompts)
│       ├── caps.py                      (Caps analysis prompts)
│       ├── numbers.py                   (Number analysis prompts)
│       ├── roman.py                     (Roman numeral analysis prompts)
│       ├── fragments.py                 (Fragment analysis prompts)
│       ├── pages.py                     (Page marker analysis prompts)
│       └── __pycache__/                 (EXCLUDE)
│
├── widgets/                             (Custom PyQt5 widgets)
│   ├── __init__.py
│   ├── font_controls.py                 (Font selection widget)
│   ├── caps_review_editor.py            (Caps review text editor)
│   ├── choices_editor.py                (Homograph choices editor)
│   │
│   └── backup_removed/                  (EXCLUDE: deprecated components)
│       └── caps_editor.py
│
├── dialogs/                             (UI dialogs)
│   ├── __init__.py
│   └── heteronym_manager.py             (Homograph definition editor)
│
├── loggers/                             (Logging module)
│   ├── __init__.py
│   └── processor_logger.py              (Per-processor logging)
│
├── logs/                                (EXCLUDE: runtime logs)
├── gui_debug.log                        (EXCLUDE: debug log)
├── gui.py~                              (EXCLUDE: backup)
├── gui.py.bak                           (EXCLUDE: backup)
├── __pycache__/                         (EXCLUDE: compiled bytecode)
├── dependency_rules.json                (EXCLUDE: internal only)
├── learned_rules.json                   (EXCLUDE: runtime generated)
├── matches.txt                          (EXCLUDE: debug output)
└── spacy.txt                            (EXCLUDE: debug output)
```

**Subdirectory Count:** 10 directories, 61 active Python files

---

## 3. DATA DIRECTORY

Configuration and reference data files. **ALL REQUIRED.**

```
data/
├── choices.json                         (Master homograph definitions - 23 words)
├── choices.json~                        (EXCLUDE: backup)
├── choices (copy).json                  (EXCLUDE: backup)
├── replace.txt                          (Find/replace rules)
├── cap_ignore.txt                       (Capitalization exceptions)
├── roman_ignore.txt                     (Roman numeral exceptions)
├── skip_choice.txt                      (Words to skip in homograph processing)
├── settings.txt                         (User application settings template)
├── upper_to_lower.txt                   (Caps normalization rules)
├── choices_labels.json                  (Homograph display labels)
├── README.txt                           (Data directory guide)
├── dependency_rules.json                (Internal rule structure)
├── weights.json                         (Scoring weights)
│
├── Legacy/Excluded Files (DO NOT INCLUDE):
├── ASR*.tar.gz                          (Old model archives)
├── sentences_by_homograph.json          (Training data snapshot)
├── training_data.json                   (Training data snapshot)
├── *.json~                              (Backups)
├── *.txt~ or *.txt.bak                  (Backups)
├── choice*.txt                          (Legacy files)
├── choice*.json (copy)                  (Legacy files)
└── suggestion_ignore.txt                (Legacy, deprecated)
```

**Critical Files:** 11 required  
**Size:** ~964 KB

---

## 4. PROMPTS DIRECTORY

LLM prompt templates for AI processors.

```
prompts/
├── homograph_batch.txt                  (Batch homograph analysis)
├── homograph_with_reasoning.txt         (Homograph with reasoning)
├── homograph_simple_contextualized.txt  (Contextualized homograph)
├── caps_sequence_batch.txt              (Batch caps processing)
├── number_classification_batch.txt      (Batch number classification)
├── roman_conversion_batch.txt           (Batch roman conversion)
├── numbered_line.txt                    (Single numbered line)
├── number_formatting.txt                (Number formatting)
├── line_fragment.txt                    (Fragment detection)
├── page_number.txt                      (Page marker detection)
│
├── Legacy (may exclude):
├── homograph_batch (copy).txt           (EXCLUDE)
├── homograph_gemini_cli.txt             (EXCLUDE: CLI specific)
├── homograph_simple.txt                 (EXCLUDE: superseded)
├── allcaps_sequence_old.txt             (EXCLUDE: superseded)
└── other legacy                         (EXCLUDE)
```

**Active Files:** 10  
**Size:** ~76 KB

---

## 5. AI LEARNING DIRECTORY

Learned patterns and dictionaries. **OPTIONAL but RECOMMENDED**.

```
.ai_learning/
├── choices_pos_dictionary.json          (POS rules for 23 homographs - CRITICAL if included)
├── choices_learning.json                (Learned homograph patterns - 4 MB)
├── caps_learning.json                   (Learned caps patterns - 566 KB)
├── numbers_learning.json                (Learned number patterns - 670 KB)
├── caps_patterns.json                   (Caps pattern summary)
├── choices_patterns.json                (Homograph pattern summary)
├── numbers_context_keywords.json        (Number context keywords)
├── context_keywords.json                (General context keywords)
├── numbers_classification_patterns.json (Number patterns)
│
└── Backups (EXCLUDE):
└── *.json~                              (Backups)
```

**Recommendation:**
- **Include** `choices_pos_dictionary.json` (required for homograph engine)
- **Include** all other JSON files for better out-of-box performance
- **May exclude** the large \*.json files if wanting a minimal distribution
- **Always exclude** backup (\*~) files

**Size if included:** 5.7 MB  
**Size if minimal:** ~100 KB (pos_dictionary only)

---

## 6. DOCDNA DIRECTORY (Optional)

DocDNA is an AI code analysis tool. Include only if you want to include pre-indexed codebase documentation.

```
DocDNA/
├── docdna.db                            (SQLite database with full code analysis)
├── docdna_query.py                      (Query CLI tool)
├── ai_config.json                       (DocDNA config)
├── generation_metadata.json             (Index metadata)
├── code_details/
│   ├── architecture_analysis.json
│   ├── functions_by_file.json
│   └── code_patterns.md
├── ai_instant/
│   ├── agents_integration.json
│   ├── function_locator.json
│   └── pattern_groups.json
└── developer_focus/
    ├── code_patterns.md
    ├── project_overview.md
    └── (other documentation)
```

**Size:** Very large (compressed: ~50+ MB indexed codebase)  
**Recommendation:** **EXCLUDE for GitHub** — include only if distributing with MCP integration  
**Alternative:** Users can run `docdna-sync` after cloning to regenerate

---

## 7. DOCS DIRECTORY (Optional)

User-facing and technical documentation.

```
Docs/
├── RuleFlowchart.md                     (Processing rule flow diagram)
├── RuleFlowchart.txt                    (Text version of flowchart)
└── choiceHowTo.txt                      (Homograph workflow guide)
```

**Recommendation:** **INCLUDE** for user documentation

---

## 8. TEST DIRECTORY

Unit and integration tests (optional for GitHub but recommended).

```
test/
├── test_mc_roman.py                     (Roman numeral tests)
├── test_filter_stages.py                (Filter stage tests)
├── (other test files as added)
```

**Root-level test files to handle:**
```
Root Level (EXCLUDE from main distribution):
├── test_pipeline.py                     (Runnable script)
├── test_ai_choices.py                   (Runnable script)
├── test_headless_gui.py                 (Runnable script)
├── test_batch_limit.py                  (Runnable script)
├── test_learning.py                     (Runnable script)
├── test_scoring.py                      (Runnable script)
├── test_caps_single_letter.py           (Runnable script)
├── test_integration_numbered.py         (Runnable script)
├── test_number_review_ui.py             (Runnable script)
├── test_roberta_homograph.py            (Runnable script)
├── test_sound_effects.py                (Runnable script)
└── test_*.bak                           (EXCLUDE)
```

**Recommendation:** Move root test files into `test/` directory OR create a `tests/` folder with proper test discovery

---

## 9. EXPORT DIRECTORY

Auto-generated export copy (development only).

**Recommendation:** **EXCLUDE from GitHub** — this is a development artifact

```
export/                                  (DO NOT INCLUDE)
├── bookfix/                             (Synced copy)
├── data/                                (Synced copy)
├── DocDNA/                              (Synced copy)
├── prompts/                             (Synced copy)
├── install.sh, run.sh, etc.             (Synced copies)
└── (other exports)
```

---

## 10. PYTHON DEPENDENCIES

### requirements.txt Content

```
beautifulsoup4==4.14.2
g2p_en==2.1.0
matplotlib==3.10.7
nltk==3.9.2
num2words==0.5.14
numpy==2.3.4
pandas==2.3.3
pygame==2.6.1
PyQt5==5.15.11
PyQt5_sip==12.17.0
Requests==2.32.5
spacy==3.8.7
```

### Downloaded During Install (NOT in repo)

**spaCy Models** (downloaded by `setup.py` post-install):
- `en_core_web_md` (required, ~40 MB)
- `en_core_web_sm` (fallback, ~14 MB)

**NLTK Data** (may be downloaded by `nltkdownload` or manually):
- `punkt` tokenizer
- `wordnet` lemmatizer

**Notes:**
- No `torch`, `tensorflow`, or heavy ML frameworks (uses spaCy's bundled models)
- RoBERTa model weights in `roberta_homograph_model/` are optional (development only)

---

## 11. FILES THAT MUST ABSOLUTELY BE EXCLUDED

### Runtime Artifacts
```
venv/                                   (Virtual environment - 300+ MB)
__pycache__/                            (Compiled Python bytecode)
*.pyc, *.pyo, *.pyd                     (Python compiled files)
.pytest_cache/                          (pytest cache)
.tox/                                   (tox cache)
.ruff_cache/                            (Ruff linter cache)
```

### Logs & Temporary Files
```
logs/                                   (Runtime logs)
*.log, *.log~                           (Log files)
bookfix_ai_debug.log*                   (Debug logs)
bookfix_execution.log                   (Execution logs)
bookfix_position_debug.log              (Position debug)
caps.log                                (Caps processing log)
*.tmp, *.temp                           (Temp files)
terminal.txt                            (Debug output)
```

### Backups & IDE Files
```
*.bak, *.backup, *.~                    (Backup files)
.aider*                                 (Aider IDE files)
.vscode/                                (VS Code settings)
.idea/                                  (JetBrains IDE settings)
*.swp, *.swo                            (Vim swap files)
.DS_Store                               (macOS metadata)
Thumbs.db                               (Windows metadata)
```

### Development & Test Artifacts
```
bookfix.egg-info/                       (Build artifacts)
build/, dist/                           (Build output)
.git/                                   (Git history - use `.gitkeep` if needed)
.claude/                                (Claude Code user config)
.opencode/                              (OpenCode config)
.aider.tags.cache.v4/                  (Aider cache)
backup/                                 (Local backups)
hold/                                   (Development holds)
input_text/                             (Test input)
```

### Session/State Files
```
project_state.json                      (User session state)
session-ses_*.md                        (Session transcripts)
.mcp.json                               (Claude MCP config)
opencode.json                           (OpenCode config)
```

### Large Archives & Old Releases
```
BookFix052526fINAL.tar.gz               (Obsolete archive)
roberta_homograph_model_full/           (Development model)
```

---

## 12. .GITIGNORE ALIGNMENT

The existing `.gitignore` is mostly correct. Verify these are ignored:

```
# Already in .gitignore:
venv/, env/, ENV/
__pycache__/, *.py[cod], *$py.class
.Python, build/, develop-eggs/, dist/
.eggs/, lib/, lib64/, parts/
wheels/, *.egg-info/, .installed.cfg, *.egg
htmlcov/, .tox/, .nox/, .coverage, .pytest_cache/
.env, .venv
.vscode/, .idea/, *.swp, *.swo, *~
.DS_Store, Thumbs.db
*.log, logs/
*.bak, *.backup, *~
*.tmp, *.temp, temp/, tmp/
.aider*, test_*.py, check_*.py
bookfix/config/ai_config.json
bookfix_execution.log
BookFix052526fINAL.tar.gz, *.tar.gz

# May need to verify excluded:
.ai_learning/               (Currently NOT ignored - see recommendation below)
export/                     (Currently NOT ignored - should be)
```

**Recommendation:** Update `.gitignore` to add:
```
export/
.ai_learning/               (if not including in distribution)
or
.ai_learning/*.json~        (if including, exclude only backups)
```

---

## 13. COMPLETE PRODUCTION ZIP STRUCTURE

### Recommended GitHub Release Package Structure

```
BookFix-v1.0.0/
├── main.py                              ✅
├── requirements.txt                     ✅
├── setup.py                             ✅
├── install.sh                           ✅
├── install.bat                          ✅
├── install.ps1                          ✅
├── run.sh                               ✅
├── run.bat                              ✅
├── run.ps1                              ✅
│
├── README.md                            ✅
├── LICENSE                              ✅
├── CLAUDE.md                            ✅
├── manual.md                            ⭕ (optional)
│
├── bookfix/                             ✅ (entire directory)
│   ├── __init__.py
│   ├── *.py                             (All .py files)
│   ├── config/ai_config.json            (Template)
│   ├── processors/                      (All .py files, no logs)
│   ├── ai/                              (All .py files, no logs)
│   ├── widgets/                         (All .py files)
│   ├── dialogs/                         (All .py files)
│   ├── loggers/                         (All .py files)
│   └── analyzers/                       (All .py files)
│
├── data/                                ✅ (entire directory)
│   ├── choices.json
│   ├── replace.txt
│   ├── cap_ignore.txt
│   ├── roman_ignore.txt
│   ├── skip_choice.txt
│   ├── settings.txt
│   ├── upper_to_lower.txt
│   ├── choices_labels.json
│   ├── README.txt
│   └── weights.json
│
├── prompts/                             ✅ (active files only)
│   ├── homograph_batch.txt
│   ├── homograph_with_reasoning.txt
│   ├── (other active prompts)
│   └── ⛔ NO legacy or obsolete files
│
├── .ai_learning/                        ⭕ (CONDITIONAL)
│   ├── choices_pos_dictionary.json      ✅ (REQUIRED if included)
│   ├── choices_learning.json            ✅ (performance)
│   ├── caps_learning.json               ✅ (performance)
│   ├── numbers_learning.json            ✅ (performance)
│   └── (other .json files)              ✅
│
├── Docs/                                ⭕ (optional but recommended)
│   ├── RuleFlowchart.md
│   └── choiceHowTo.txt
│
├── test/                                ⭕ (optional but recommended)
│   └── test_*.py                        (structured tests)
│
├── .gitignore                           ✅
└── .git/                                ✅ (GitHub will create)
```

---

## 14. FILE COUNT & SIZE SUMMARY

### Core Package
| Component | Files | Size | Status |
|-----------|-------|------|--------|
| Root scripts & config | 9 | ~20 KB | ✅ Required |
| Documentation | 4 | ~45 KB | ✅ Required |
| bookfix/ package | 61 | ~2.4 MB | ✅ Required |
| data/ | 11 | 964 KB | ✅ Required |
| prompts/ | 10 | 76 KB | ✅ Required |
| Docs/ | 3 | ~30 KB | ⭕ Optional |
| test/ | ~10 | ~50 KB | ⭕ Optional |
| **TOTAL (Core)** | **~95** | **~3.6 MB** | ✅ |

### With AI Learning (Recommended)
| Component | Files | Size |
|-----------|-------|------|
| Core package (above) | 95 | 3.6 MB |
| .ai_learning/ | 8 | 5.7 MB |
| **TOTAL (Full)** | **~103** | **~9.3 MB** |

### Excluded from Repo
| Component | Size | Reason |
|-----------|------|--------|
| venv/ | ~500 MB | Virtual environment |
| DocDNA/ | ~100+ MB | Code analysis database |
| roberta_homograph_model/ | ~500 MB | Development model |
| Logs & caches | ~2 GB | Runtime artifacts |
| export/ | ~10 MB | Development copy |
| Archives & backups | ~1 GB | Legacy artifacts |
| **TOTAL EXCLUDED** | **~2+ GB** | Development only |

---

## 15. INSTALLATION FLOW FOR USERS

### Unix/Linux/macOS
```bash
git clone https://github.com/username/BookFix.git
cd BookFix
./install.sh                    # Creates venv, installs deps, downloads spaCy models
./run.sh                        # Launches GUI
```

### Windows (Command Prompt)
```cmd
git clone https://github.com/username/BookFix.git
cd BookFix
install.bat                     # Creates venv, installs deps, downloads spaCy models
run.bat                         # Launches GUI
```

### Windows (PowerShell)
```powershell
git clone https://github.com/username/BookFix.git
cd BookFix
.\install.ps1                   # Creates venv, installs deps, downloads spaCy models
.\run.ps1                       # Launches GUI
```

### Manual Installation
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .          # Installs BookFix + all dependencies + spaCy model
python main.py            # Launches application
```

---

## 16. CRITICAL FILES THAT MUST NEVER BE OMITTED

These files are absolutely essential for the application to function:

| File | Why Critical |
|------|--------------|
| `main.py` | Application entry point |
| `setup.py` | Defines dependencies & post-install spaCy download |
| `requirements.txt` | Fallback dependency list |
| `bookfix/context.py` | Central data structure for entire pipeline |
| `bookfix/pipeline.py` | Orchestrates automatic processing |
| `bookfix/gui.py` | PyQt5 UI (largest file, 62 KB) |
| `bookfix/processors/*.py` | All 18 processor implementations |
| `bookfix/ai/service.py` | Unified AI provider interface |
| `bookfix/ai/hybrid_deciders.py` | 23 homograph decision functions |
| `data/choices.json` | Homograph dictionary (23 words) |
| `data/replace.txt` | Find/replace rules |
| `data/cap_ignore.txt` | Acronym exceptions |
| `run.sh`, `run.bat`, `run.ps1` | User-facing launchers |
| `install.sh`, `install.bat`, `install.ps1` | User-facing installers |

---

## 17. ZIP CREATION COMMAND

### For GitHub Release (Recommended)
```bash
#!/bin/bash
# Create production-ready zip for GitHub

REPO_DIR="/home/danno/MyApps/BookFix"
OUTPUT="BookFix-v1.0.0-production.zip"

# Create temp staging directory
mkdir -p /tmp/bookfix-staging/BookFix

# Copy all required files
cd "$REPO_DIR"

# Core files
cp -v main.py setup.py requirements.txt /tmp/bookfix-staging/BookFix/
cp -v install.sh run.sh install.bat run.bat install.ps1 run.ps1 /tmp/bookfix-staging/BookFix/

# Documentation
cp -v README.md LICENSE CLAUDE.md /tmp/bookfix-staging/BookFix/
cp -v manual.md /tmp/bookfix-staging/BookFix/  # Optional

# Code package
cp -rv bookfix/ /tmp/bookfix-staging/BookFix/
# Exclude unwanted files within bookfix:
find /tmp/bookfix-staging/BookFix/bookfix -name "*.bak" -o -name "*.~" -o -name "__pycache__" -o -name "*.log" | xargs rm -rf

# Data files
cp -rv data/ /tmp/bookfix-staging/BookFix/
# Exclude backups within data:
find /tmp/bookfix-staging/BookFix/data -name "*.bak" -o -name "*.~" -o -name "*.tar.gz" | xargs rm -f

# Prompts
cp -rv prompts/ /tmp/bookfix-staging/BookFix/
# Remove legacy prompts only if desired
# find /tmp/bookfix-staging/BookFix/prompts -name "*old*" -o -name "*deprecated*" | xargs rm -f

# Optional: AI Learning
cp -rv .ai_learning/ /tmp/bookfix-staging/BookFix/
find /tmp/bookfix-staging/BookFix/.ai_learning -name "*.~" | xargs rm -f

# Optional: Documentation
cp -rv Docs/ /tmp/bookfix-staging/BookFix/

# Git config (optional - GitHub will create this)
cp -v .gitignore /tmp/bookfix-staging/BookFix/

# Create final zip
cd /tmp/bookfix-staging
zip -r "$REPO_DIR/$OUTPUT" BookFix/ -x \
  "BookFix/.git/*" \
  "BookFix/venv/*" \
  "BookFix/export/*" \
  "BookFix/.opencode/*" \
  "BookFix/.ruff_cache/*" \
  "BookFix/.pytest_cache/*" \
  "BookFix/*/.pytest_cache/*" \
  "BookFix/logs/*" \
  "BookFix/bookfix/logs/*" \
  "BookFix/bookfix/processors/logs/*"

echo "✅ Created: $REPO_DIR/$OUTPUT"
ls -lh "$REPO_DIR/$OUTPUT"
```

---

## 18. GITHUB REPOSITORY SETUP CHECKLIST

- [ ] Create repository on GitHub
- [ ] Clone locally
- [ ] Add `.gitignore` (verify excludes venv, logs, exports, etc.)
- [ ] Add `README.md` with quick-start and screenshots
- [ ] Add `LICENSE` (Apache 2.0 or your choice)
- [ ] Add `CLAUDE.md` for contributor guidelines
- [ ] Organize `test/` directory with pytest-compatible structure
- [ ] Add `CONTRIBUTING.md` for contributors
- [ ] Create GitHub Actions workflow for CI/CD (optional but recommended):
  - Test suite on Python 3.10, 3.11, 3.12
  - Check formatting (black, ruff)
  - Verify installation process
- [ ] Create GitHub Release with zip file
- [ ] Add tags (e.g., `v1.0.0`)
- [ ] Update `setup.py` version to match release
- [ ] Pin dependencies in `requirements.txt` (already done)

---

## 19. FINAL DISTRIBUTION CHECKLIST

Before creating the production zip:

### Must Have ✅
- [ ] All Python files in `bookfix/` (61 files)
- [ ] All data files in `data/` (11 critical files)
- [ ] Prompt templates in `prompts/` (10 active files)
- [ ] All install/run scripts (6 files: .sh, .bat, .ps1)
- [ ] `main.py`, `setup.py`, `requirements.txt`
- [ ] `README.md`, `LICENSE`, `CLAUDE.md`
- [ ] `.gitignore`

### Strongly Recommended ⭕
- [ ] All files in `.ai_learning/` (5.7 MB additional learning data)
- [ ] Documentation in `Docs/`
- [ ] Test suite in `test/` directory
- [ ] `manual.md` user guide

### Optional ⭕
- [ ] `AGENTS.md`, `GEMINI.md` (developer notes)
- [ ] `WARP.md` (project history)

### Must Exclude ❌
- [ ] `venv/` directory
- [ ] `DocDNA/` directory
- [ ] `export/` directory
- [ ] `roberta_homograph_model/` directory
- [ ] All `*.log`, `*.bak`, `*.~` files
- [ ] All `__pycache__/`, `.pytest_cache/`
- [ ] `project_state.json`, session files
- [ ] `.mcp.json`, `.opencode.json`, `.claude/`
- [ ] Large archives (`.tar.gz`)

---

## 20. RECOMMENDED GITHUB REPO STRUCTURE

```
BookFix/
├── .github/
│   └── workflows/
│       ├── test.yml                     (Run tests on PR)
│       ├── lint.yml                     (Run linters)
│       └── release.yml                  (Build release packages)
│
├── .gitignore                           ✅
├── README.md                            ✅
├── LICENSE                              ✅
├── CONTRIBUTING.md                      (Contributor guide)
├── CLAUDE.md                            ✅
│
├── main.py                              ✅
├── setup.py                             ✅
├── requirements.txt                     ✅
├── pyproject.toml                       (Optional: modern Python config)
│
├── install.sh                           ✅
├── install.bat                          ✅
├── install.ps1                          ✅
├── run.sh                               ✅
├── run.bat                              ✅
├── run.ps1                              ✅
│
├── bookfix/                             ✅
├── data/                                ✅
├── prompts/                             ✅
├── .ai_learning/                        ⭕ (CONDITIONAL)
├── Docs/                                ⭕
├── test/                                ⭕
│
└── docs/                                (Optional: GitHub Pages)
    ├── index.md
    └── architecture.md
```

---

## SUMMARY TABLE: What to Include

| Item | Include? | Why |
|------|----------|-----|
| All `.py` files | ✅ Yes | Core application |
| `data/` directory | ✅ Yes | Configuration data |
| `prompts/` directory | ✅ Yes | LLM templates |
| `.ai_learning/` | ⭕ Conditional | Learning data (5.7 MB) |
| `Docs/` | ⭕ Optional | User documentation |
| `test/` | ⭕ Optional | Test suite |
| Install/run scripts | ✅ Yes | User setup |
| `venv/` | ❌ No | Too large, installed by user |
| `export/` | ❌ No | Development artifact |
| `DocDNA/` | ❌ No | Too large, regenerable |
| Logs | ❌ No | Runtime only |
| Backups/cache | ❌ No | Not needed |

---

**End of Analysis Document**

Generated by Claude Code  
For: GitHub production release  
Date: 2026-06-21
