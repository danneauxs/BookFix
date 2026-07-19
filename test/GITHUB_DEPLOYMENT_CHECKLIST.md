# BookFix GitHub Deployment Checklist

Use this checklist to prepare BookFix for GitHub release.

---

## Phase 1: Pre-Release Preparation

### Code Quality & Testing
- [ ] Run all tests pass: `cd test && pytest` (or `python -m pytest`)
- [ ] Run top-level test scripts successfully
  - [ ] `python test_pipeline.py`
  - [ ] `python test_ai_choices.py`
  - [ ] `python test_headless_gui.py`
  - [ ] `python test_batch_limit.py`
  - [ ] `python test_learning.py`
- [ ] Verify application launches: `./run.sh` (Linux/macOS) or `run.bat` (Windows)
- [ ] Test basic workflow: load file → process → review → export
- [ ] No uncommitted changes: `git status` is clean

### Code & Documentation Standards
- [ ] Every `.py` file has proper docstrings (per CLAUDE.md)
- [ ] No TODO comments that are not actionable
- [ ] Dead code removed (check via: `docdna-query . --dead-code`)
- [ ] All imports are used and properly organized
- [ ] No hardcoded paths (use `config/` directory)
- [ ] No debug print statements left behind
- [ ] Logging is appropriate level (DEBUG, INFO, ERROR)

### Configuration Files
- [ ] `data/choices.json` — all 23 homographs defined
- [ ] `data/replace.txt` — complete replacement rules
- [ ] `data/cap_ignore.txt` — all acronyms listed
- [ ] `data/roman_ignore.txt` — exceptions documented
- [ ] `data/skip_choice.txt` — skip patterns defined
- [ ] `data/settings.txt` — default settings present
- [ ] `bookfix/config/ai_config.json` — template is valid JSON

### Dependency Verification
- [ ] `requirements.txt` has all pinned versions (e.g., `PyQt5==5.15.11`)
- [ ] `setup.py` lists same dependencies as `requirements.txt`
- [ ] `setup.py` includes `spacy download en_core_web_md` in post-install
- [ ] All dependencies tested on Python 3.10, 3.11, 3.12 (if CI available)
- [ ] No system-level dependencies required (no `apt`, `brew`, etc.)

### Installation Scripts
- [ ] `install.sh` works on Linux/macOS
  - [ ] Creates venv correctly
  - [ ] Activates venv
  - [ ] Installs dependencies
  - [ ] Downloads spaCy model
- [ ] `install.bat` works on Windows (CMD)
  - [ ] Creates venv correctly
  - [ ] Activates venv
  - [ ] Installs dependencies
  - [ ] Downloads spaCy model
- [ ] `install.ps1` works on Windows (PowerShell)
  - [ ] Creates venv correctly
  - [ ] Activates venv
  - [ ] Installs dependencies
  - [ ] Downloads spaCy model

### Launch Scripts
- [ ] `run.sh` works on Linux/macOS
  - [ ] Activates venv
  - [ ] Launches GUI successfully
  - [ ] No error messages
- [ ] `run.bat` works on Windows (CMD)
  - [ ] Activates venv
  - [ ] Launches GUI successfully
  - [ ] No error messages
- [ ] `run.ps1` works on Windows (PowerShell)
  - [ ] Activates venv
  - [ ] Launches GUI successfully
  - [ ] No error messages

---

## Phase 2: Documentation & README

### README.md
- [ ] Project description is clear and compelling
- [ ] Features list is accurate and complete
- [ ] Quick start instructions work as written
- [ ] Installation section covers all platforms (Linux, macOS, Windows)
- [ ] Screenshots or demo video (optional but recommended)
- [ ] Troubleshooting section addresses common issues
- [ ] "Building from source" section included
- [ ] License is clearly stated
- [ ] Contributing guidelines link

### CLAUDE.md
- [ ] Project overview is accurate
- [ ] Architecture overview matches current code
- [ ] Key files reference is up-to-date
- [ ] Configuration section lists all data files
- [ ] Important gotchas are documented
- [ ] Processor addition guide is clear
- [ ] Token efficiency rules are clear

### Other Documentation
- [ ] `manual.md` — user guide is complete
- [ ] `Docs/RuleFlowchart.md` — processing flow diagram
- [ ] `Docs/choiceHowTo.txt` — homograph workflow explained
- [ ] `LICENSE` — appropriate license file present

### Create CONTRIBUTING.md (NEW)
- [ ] Contribution guidelines
- [ ] Code style requirements
- [ ] Testing requirements for PRs
- [ ] How to report bugs
- [ ] How to suggest features

---

## Phase 3: File & Directory Cleanup

### Remove Files That Should NOT Be Included
- [ ] `venv/` — not needed, installed by user
- [ ] `export/` — development copy only
- [ ] `DocDNA/` — can be regenerated
- [ ] `roberta_homograph_model/` — development only
- [ ] All `*.log` files in root and subdirectories
- [ ] All `*.bak`, `*.backup`, `*~` files
- [ ] `project_state.json` — user session state
- [ ] `.ai_learning/*.~` — backup files
- [ ] Session transcripts (`session-ses_*.md`)
- [ ] Old archives (`BookFix*.tar.gz`)
- [ ] Test input directories (e.g., `input_text/`, `hold/`)
- [ ] IDE cache directories (`.vscode/`, `.idea/`, `.opencode/`)
- [ ] Claude Code config (`.mcp.json`, `.claude/`)

### Verify Directory Structure is Clean
```bash
# Run this to see what would be excluded
find . -maxdepth 1 -type f \( -name "*.log" -o -name "*.bak" -o -name "*~" \) -ls

# Run this to check for large files that shouldn't be there
find . -maxdepth 1 -type f -size +10M -ls
```

### .gitignore Verification
- [ ] `.gitignore` has `venv/`
- [ ] `.gitignore` has `export/`
- [ ] `.gitignore` has `*.log`
- [ ] `.gitignore` has `*.bak`, `*~`
- [ ] `.gitignore` has `__pycache__/`
- [ ] `.gitignore` has `project_state.json`
- [ ] `.gitignore` has `.ai_learning/` (if not including learning data) OR `.ai_learning/*.~` (if including)

---

## Phase 4: GitHub Repository Setup

### Repository Creation
- [ ] GitHub account ready
- [ ] Repository name chosen: `BookFix` (recommended)
- [ ] Repository visibility: Public
- [ ] Description: "Ebook text processor for Text-to-Speech preparation"
- [ ] Add topics: `ebook`, `text-processing`, `tts`, `python`, `pyqt5`
- [ ] Initialize with `.gitignore` (Python template)

### Initial Commit
- [ ] Clone repository locally
- [ ] Copy all BookFix files (use script below)
- [ ] Verify `.gitignore` is present
- [ ] First commit: "Initial commit: BookFix v1.0.0"
  ```bash
  git add .
  git commit -m "Initial commit: BookFix v1.0.0"
  git push -u origin main
  ```

### Repository Metadata
- [ ] Add description in repo settings
- [ ] Add repository homepage link (if applicable)
- [ ] Set up branch protection for `main`:
  - [ ] Require pull request reviews
  - [ ] Require status checks to pass
- [ ] Set up labels for issues (bug, enhancement, documentation, etc.)

### Branch Structure
- [ ] `main` — stable releases
- [ ] `develop` — development branch (optional)
- [ ] Protect `main` from direct pushes (use pull requests)

---

## Phase 5: Create Distribution Package

### Run Distribution Script
```bash
chmod +x create_github_distribution.sh
./create_github_distribution.sh 1.0.0
```

This creates:
- `dist/BookFix-v1.0.0.zip` (core package, ~3.6 MB)
- `dist/BookFix-v1.0.0-full.zip` (with learning data, ~9.3 MB)

### Verify Package Contents
- [ ] Core ZIP contains:
  - [ ] `main.py`, `setup.py`, `requirements.txt`
  - [ ] Install and run scripts (6 files)
  - [ ] `bookfix/` directory (61 Python files)
  - [ ] `data/` directory (11 files)
  - [ ] `prompts/` directory (10 files)
  - [ ] Documentation (README.md, LICENSE, CLAUDE.md)
  - [ ] `.gitignore`
  - [ ] NO venv, logs, export, or backups
- [ ] Full ZIP includes `.ai_learning/` data (5.7 MB)

### Test Installation from ZIP
- [ ] Extract core ZIP to temp directory
- [ ] Run `./install.sh` (Linux/macOS)
- [ ] Verify GUI launches: `./run.sh`
- [ ] Test basic workflow
- [ ] Verify no errors in logs
- [ ] Clean up temp directory

---

## Phase 6: GitHub Release

### Create GitHub Release
- [ ] Go to: https://github.com/username/BookFix/releases/new
- [ ] Set tag: `v1.0.0`
- [ ] Set title: "BookFix v1.0.0"
- [ ] Add release notes:
  ```markdown
  ## What's New
  - Initial public release
  - [Feature list from README]
  
  ## Installation
  Download BookFix-v1.0.0.zip, extract, run install.sh or install.bat
  
  ## Requirements
  - Python 3.10, 3.11, or 3.12
  - ~1 GB disk space (venv + dependencies)
  
  ## Files
  - **BookFix-v1.0.0.zip** (3.6 MB) — Core package
  - **BookFix-v1.0.0-full.zip** (9.3 MB) — Includes pre-trained learning data
  
  ## Checksums
  [Add if desired for security]
  ```
- [ ] Upload `dist/BookFix-v1.0.0.zip`
- [ ] Upload `dist/BookFix-v1.0.0-full.zip` (optional)
- [ ] Mark as "Latest release"
- [ ] Publish release

### Create GitHub Wiki (Optional)
- [ ] Homepage — Project overview
- [ ] Installation — Platform-specific guides
- [ ] Quick Start — Step-by-step walkthrough
- [ ] Configuration — Data files guide
- [ ] Architecture — System design
- [ ] Contributing — Developer guide
- [ ] FAQ — Common questions and answers

---

## Phase 7: Continuous Integration (Optional but Recommended)

### GitHub Actions Setup
Create `.github/workflows/test.yml`:
- [ ] Tests run on Python 3.10, 3.11, 3.12
- [ ] Run test suite on pull requests
- [ ] Check code formatting (black, ruff)
- [ ] Verify installation process works

Create `.github/workflows/lint.yml`:
- [ ] Run ruff linter
- [ ] Check for type hints (optional)
- [ ] Verify no hardcoded secrets

---

## Phase 8: Post-Release

### Announcement
- [ ] Post on GitHub Discussions
- [ ] Announce on relevant forums/communities
- [ ] Submit to Python Package Index (PyPI) if desired
- [ ] Create social media announcement (if applicable)

### Maintenance
- [ ] Set up issue templates (GitHub)
- [ ] Set up pull request template
- [ ] Respond to initial issues quickly
- [ ] Consider a roadmap for v1.1.0 features
- [ ] Set up security reporting process

### Documentation Updates
- [ ] Update README with download link
- [ ] Add CI/CD badge if using GitHub Actions
- [ ] Add license badge
- [ ] Add Python version badge

---

## Quick Reference: Files to Verify

### Must Include (Critical)
```
✅ main.py
✅ setup.py
✅ requirements.txt
✅ install.sh, install.bat, install.ps1
✅ run.sh, run.bat, run.ps1
✅ README.md
✅ LICENSE
✅ CLAUDE.md
✅ bookfix/  (entire directory)
✅ data/     (entire directory)
✅ prompts/  (entire directory)
```

### Should Include (Recommended)
```
⭕ .ai_learning/  (learning data, optional)
⭕ Docs/           (documentation)
⭕ test/           (test suite)
⭕ manual.md       (user guide)
```

### Must Exclude (Critical)
```
❌ venv/
❌ export/
❌ DocDNA/
❌ roberta_homograph_model/
❌ *.log files
❌ *.bak, *.backup, *~ files
❌ __pycache__/ directories
❌ .pytest_cache/
❌ .git/ directory (handled by GitHub)
❌ project_state.json
❌ .mcp.json, .opencode.json
❌ session-ses_*.md files
```

---

## Verification Script

Run this to check everything is ready:

```bash
#!/bin/bash

echo "BookFix Release Readiness Check"
echo "==============================="
echo ""

# Check critical files
echo "Critical files:"
for file in main.py setup.py requirements.txt install.sh run.sh README.md LICENSE CLAUDE.md; do
    if [ -f "$file" ]; then
        echo "✓ $file"
    else
        echo "✗ $file (MISSING)"
    fi
done

# Check directories
echo ""
echo "Directory structure:"
for dir in bookfix data prompts; do
    if [ -d "$dir" ]; then
        count=$(find "$dir" -type f | wc -l)
        echo "✓ $dir/ ($count files)"
    else
        echo "✗ $dir/ (MISSING)"
    fi
done

# Check for excluded files
echo ""
echo "Excluded files check:"
excluded_count=$(find . -maxdepth 1 -type f \( -name "*.log" -o -name "*.bak" -o -name "*~" -o -name "*.tar.gz" \) | wc -l)
if [ "$excluded_count" -eq 0 ]; then
    echo "✓ No excluded files in root"
else
    echo "✗ Found $excluded_count excluded files (should be 0)"
    find . -maxdepth 1 -type f \( -name "*.log" -o -name "*.bak" -o -name "*~" \) -ls
fi

# Check .gitignore
echo ""
echo ".gitignore check:"
if grep -q "venv/" .gitignore; then
    echo "✓ venv/ is ignored"
else
    echo "✗ venv/ not in .gitignore"
fi

if grep -q "*.log" .gitignore; then
    echo "✓ *.log is ignored"
else
    echo "✗ *.log not in .gitignore"
fi

echo ""
echo "✅ Ready to create distribution package"
```

---

## Final Sign-Off

- [ ] Project lead reviewed release
- [ ] All tests passing
- [ ] README is clear and accurate
- [ ] Installation tested on all platforms
- [ ] Distribution ZIP verified
- [ ] GitHub repository set up correctly
- [ ] Release published on GitHub

---

**Ready to Release! 🚀**

Timestamp: ________________  
Released by: ________________  
Version: v1.0.0  
Date: ________________

