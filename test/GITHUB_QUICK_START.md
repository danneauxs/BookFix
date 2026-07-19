# BookFix GitHub Release — Quick Start Guide

**TL;DR:** Everything you need to know to create a production GitHub package in 15 minutes.

---

## The 4 Key Documents

| Document | Purpose | When to Use |
|----------|---------|-----------|
| **GITHUB_DISTRIBUTION_ANALYSIS.md** | Complete inventory of all files, dependencies, structure | Reference only - detailed specs |
| **GITHUB_DEPLOYMENT_CHECKLIST.md** | Step-by-step checklist before release | Follow this before publishing |
| **create_github_distribution.sh** | Automated script to build production ZIP | Run this to create the package |
| **GITHUB_QUICK_START.md** | This document - quick reference | You are here |

---

## 3-Step Release Process

### Step 1: Verify Code is Ready (5 min)
```bash
# Run from project root
cd ~/MyApps/BookFix

# Test installation locally
./install.sh
./run.sh
# Test: load file → process → export (should work perfectly)

# Verify no uncommitted changes
git status
# Should show only normal untracked files, nothing changed
```

### Step 2: Create Distribution Package (2 min)
```bash
# From project root
chmod +x create_github_distribution.sh
./create_github_distribution.sh 1.0.0

# This creates:
# - dist/BookFix-v1.0.0.zip (3.6 MB)
# - dist/BookFix-v1.0.0-full.zip (9.3 MB with learning data)
```

### Step 3: Upload to GitHub (3 min)
```bash
# Go to: https://github.com/YOUR_USERNAME/BookFix/releases/new
# Tag: v1.0.0
# Title: BookFix v1.0.0
# Upload both ZIP files
# Publish
```

---

## What's Included/Excluded

### ✅ INCLUDED (Everything Users Need)
- `bookfix/` — 61 Python files (22,399 lines)
- `data/` — 11 configuration files
- `prompts/` — 10 LLM template files
- `.ai_learning/` — 5.7 MB of learned patterns (optional)
- Install/run scripts for Linux, macOS, Windows
- Complete documentation (README, LICENSE, CLAUDE.md)
- Test suite

### ❌ EXCLUDED (Cleanup)
- `venv/` — too large, users install via `pip`
- `export/`, `DocDNA/` — development only
- All logs, backups, cache
- `.git/` history
- Model archives

**Total Size:** 3.6 MB (core) or 9.3 MB (with learning data)

---

## File Inventory Snapshot

| Directory | Files | Size | Status |
|-----------|-------|------|--------|
| bookfix/ | 61 | 2.4 MB | ✅ Required |
| data/ | 11 | 964 KB | ✅ Required |
| prompts/ | 10 | 76 KB | ✅ Required |
| .ai_learning/ | 8 | 5.7 MB | ⭕ Included (optional) |
| root scripts | 9 | 20 KB | ✅ Required |
| documentation | 4 | 45 KB | ✅ Required |
| **TOTAL** | ~103 | **~9.3 MB** | ✅ |

---

## Critical Files (NEVER Omit)

These 15 files are the absolute minimum for the application to work:

```
1. main.py                              (entry point)
2. setup.py                             (installer)
3. requirements.txt                     (dependencies)
4. install.sh, install.bat, install.ps1 (setup scripts)
5. run.sh, run.bat, run.ps1             (launcher scripts)
6. README.md                            (documentation)
7. LICENSE                              (legal)
8. bookfix/pipeline.py                  (orchestrator)
9. bookfix/gui.py                       (UI)
10. bookfix/context.py                  (data structure)
11. data/choices.json                   (homograph dict)
12. data/replace.txt                    (rules)
13. bookfix/ai/service.py               (AI interface)
14. bookfix/processors/rules_processor.py (number processing)
15. bookfix/ai/hybrid_deciders.py       (homograph logic)
```

---

## Installation Flow for Users

After user downloads ZIP:

```bash
# Step 1: Extract
unzip BookFix-v1.0.0.zip
cd BookFix

# Step 2: Install (one-time)
./install.sh                    # Creates venv, installs deps, downloads models
# Takes: ~5 minutes

# Step 3: Run (every time)
./run.sh
# GUI launches immediately
```

**That's it.** No conda, no Docker, no system packages. Just Python + pip.

---

## Python Dependency List

12 packages, all pinned to exact versions (see `requirements.txt`):

```
beautifulsoup4==4.14.2      (HTML parsing)
g2p_en==2.1.0               (G2P phonetic)
matplotlib==3.10.7          (Plotting)
nltk==3.9.2                 (NLP library)
num2words==0.5.14           (Number formatting)
numpy==2.3.4                (Math)
pandas==2.3.3               (Data frames)
pygame==2.6.1               (Audio)
PyQt5==5.15.11              (GUI framework)
PyQt5_sip==12.17.0          (Qt bindings)
Requests==2.32.5            (HTTP)
spacy==3.8.7                (NLP models)

# Downloaded during install (not in repo):
spacy en_core_web_md        (~40 MB)
spacy en_core_web_sm        (~14 MB, fallback)
```

---

## Platform-Specific Notes

### Linux/macOS
- Use `.sh` scripts
- Requires: `python3`, `bash`
- Tested on: Ubuntu 20.04+, macOS 10.14+

### Windows
- Use `.bat` (Command Prompt) OR `.ps1` (PowerShell)
- Requires: Python 3.10+ in PATH
- Note: PowerShell may have execution policy issues → `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

---

## Directory Structure (for GitHub)

```
BookFix/
├── README.md                (START HERE)
├── LICENSE
├── CLAUDE.md                (Developer guide)
├── main.py
├── setup.py
├── requirements.txt
├── install.sh / .bat / .ps1
├── run.sh / .bat / .ps1
├── .gitignore
├── bookfix/                 (61 files)
├── data/                    (11 files)
├── prompts/                 (10 files)
├── .ai_learning/            (8 files, 5.7 MB)
├── Docs/                    (optional)
├── test/                    (optional)
└── .git/                    (GitHub manages)
```

---

## Common Questions

### Q: Should I include `.ai_learning/` folder?
**A:** Yes, recommended. It's 5.7 MB of pre-trained patterns that improve accuracy immediately. Users can regenerate it if needed.

### Q: What about the large spaCy model (en_core_web_md)?
**A:** NOT included in repo. Downloaded during `pip install -e .` (automatic via `setup.py`).

### Q: Can users use a lighter spaCy model?
**A:** Yes, but `en_core_web_md` is needed for semantic similarity in homograph disambiguation. `en_core_web_sm` is a fallback.

### Q: Does this need Docker?
**A:** No. Just Python 3.10+ and the install script.

### Q: How big is the final installation?
**A:** ~800 MB on disk after install (mostly venv + spaCy model).

### Q: Can I install without the venv?
**A:** Not recommended. The venv isolates dependencies and prevents conflicts with system Python.

### Q: What if the spaCy download fails?
**A:** Manual fallback: `python -m spacy download en_core_web_md` (included in install script with error handling).

---

## Pre-Release Checklist (5 Minutes)

Before running `create_github_distribution.sh`:

- [ ] `git status` shows clean repo (only untracked files)
- [ ] `./install.sh` runs without errors
- [ ] `./run.sh` launches GUI successfully
- [ ] Load a test document and process it
- [ ] No `.log` or `.bak` files in root
- [ ] `requirements.txt` has all dependencies pinned
- [ ] `setup.py` includes spaCy model download
- [ ] `README.md` has clear installation instructions
- [ ] `LICENSE` is present and correct

---

## Create the Distribution (One Command)

```bash
cd ~/MyApps/BookFix
chmod +x create_github_distribution.sh
./create_github_distribution.sh 1.0.0
```

**Output:**
```
dist/BookFix-v1.0.0.zip          (3.6 MB, core package)
dist/BookFix-v1.0.0-full.zip     (9.3 MB, with learning data)
```

---

## GitHub Release Steps

1. Go to: https://github.com/YOUR_USERNAME/BookFix
2. Click: "Releases" → "Draft a new release"
3. Fill in:
   - **Tag:** v1.0.0
   - **Title:** BookFix v1.0.0
   - **Description:** [Copy from CHANGELOG or README]
4. **Attach files:** Upload both ZIP files
5. **Publish release**

---

## After Release

### Promote Your Release
- Post on Reddit: r/Python, r/ebook, r/audiobooks
- Post on GitHub Discussions
- Add to product hunt (if applicable)
- Update any relevant documentation that links to download

### Monitor
- Watch for GitHub issues
- Respond quickly to installation problems
- Collect user feedback
- Plan v1.1.0 improvements

---

## Version Numbering

Use semantic versioning:

```
v1.0.0 — Initial release
v1.1.0 — New feature (backwards compatible)
v1.0.1 — Bug fix
v2.0.0 — Breaking changes
```

---

## File Sizes Reference

Useful for debugging/understanding the package:

```
bookfix/gui.py              ~62 KB  (largest single file)
bookfix/ai/review_window.py ~71 KB  (UI dialogs)
data/choices.json           ~35 KB  (homograph dictionary)
.ai_learning/choices_learning.json  ~4 MB  (learned patterns)
.ai_learning/numbers_learning.json  ~670 KB
data/replace.txt            ~14 KB
prompts/                    ~76 KB total
```

---

## Backup Current State

Before starting the release process:

```bash
# Save current state
cd ~/MyApps/BookFix
git tag -a pre-release-$(date +%Y%m%d) -m "Backup before release"
git push origin --tags
```

---

## One-Line Summary

> **BookFix is a 22,399-line Python PyQt5 application for preparing ebooks for text-to-speech. Distribution is clean: 3.6 MB core package with all dependencies pinned, runs on Python 3.10-3.12, installs in one command.**

---

## Quick Links

- **Main Analysis:** `GITHUB_DISTRIBUTION_ANALYSIS.md`
- **Full Checklist:** `GITHUB_DEPLOYMENT_CHECKLIST.md`
- **Build Script:** `create_github_distribution.sh`
- **Project Docs:** `README.md`, `CLAUDE.md`
- **Data Config:** `data/choices.json`, `data/replace.txt`
- **Tests:** `test/` directory

---

**Next Step:** Run the distribution script and upload to GitHub. See you on the other side! 🚀

