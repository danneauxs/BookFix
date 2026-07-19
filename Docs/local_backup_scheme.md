# Local Backup Scheme

BookFix uses two local recovery layers:

1. Git commits preserve source code, documentation, curated data, active choices learning, and configuration templates.
2. Dated tar snapshots preserve ignored runtime files and learning-state backups without putting large models or logs into Git.

## Normal checkpoint

Run from the project root:

```bash
git status
git add -A
git commit -m "Describe checkpoint"
python3 create_backup.py
```

Commit after each working feature or verified choices-learning cleanup. Create a tar snapshot before bulk learning changes or model changes.

## What Git tracks

- BookFix source and tests
- `data/choices.json`
- active `.ai_learning/*.json` files
- plans and documentation
- `bookfix/config/ai_config.example.json`

## What stays outside Git

- API-bearing `bookfix/config/ai_config.json`
- model weights
- `DocDNA/`, `dist/`, and `export/`
- logs, virtual environments, and generated archives

## Recovery

List checkpoints:

```bash
git log --oneline --decorate
```

Inspect an older checkpoint:

```bash
git show --stat CHECKPOINT
git diff CHECKPOINT..HEAD
```

Restore selected files without changing the rest of the worktree:

```bash
git restore --source CHECKPOINT -- bookfix data Docs
```

Restore the whole tracked project to a checkpoint only after saving current work:

```bash
git diff > /tmp/bookfix-current.patch
git restore --source CHECKPOINT --staged --worktree .
```

Recover ignored runtime state from the newest tar snapshot in `backup/` by extracting it into the project root. Recreate local AI configuration from `bookfix/config/ai_config.example.json`, then add local API settings only on the machine.

Git history is local only. No remote, push, or network backup is configured.
