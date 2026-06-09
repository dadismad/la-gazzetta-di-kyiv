#!/usr/bin/env python3
"""safe_git.py — Pre-commit check + auto-backup before destructive Git operations.
Call before: git checkout, git reset, git revert, or any branch switch.
"""
import os
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import shutil

PROJECT = Path(__file__).resolve().parent
BACKUP_DIR = PROJECT / ".backup"

def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=str(PROJECT))

def has_uncommitted():
    """Check for uncommitted changes (staged + unstaged)."""
    r = run("git status --porcelain")
    return bool(r.stdout.strip()), r.stdout.strip()

def backup_uncommitted():
    """Copy all modified/new files from git status to .backup/<timestamp>/."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    dest = BACKUP_DIR / ts
    dest.mkdir(parents=True, exist_ok=True)

    r = run("git status --porcelain")
    count = 0
    for line in r.stdout.strip().split("\n"):
        if not line:
            continue
        # Format: XY filename (X=staged status, Y=unstaged status)
        status = line[:2]
        fname = line[3:].strip().strip('"')
        if not fname:
            continue

        src = PROJECT / fname
        if not src.exists():
            continue

        dst = dest / fname
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(src), str(dst))
        count += 1

    return str(dest), count

def main():
    dirty, status_out = has_uncommitted()

    if not dirty:
        print("✓ Working tree clean — safe to proceed.")
        return 0

    print("╔══════════════════════════════════════════╗")
    print("║  ⚠ UNCOMMITTED CHANGES DETECTED         ║")
    print("╠══════════════════════════════════════════╣")
    for line in status_out.strip().split("\n")[:15]:
        print(f"║  {line}")
    if len(status_out.strip().split("\n")) > 15:
        print(f"║  ... and {len(status_out.strip().split(chr(10))) - 15} more")
    print("╚══════════════════════════════════════════╝")

    print(f"\n  Auto-backing up to .backup/ ...")
    dest, count = backup_uncommitted()
    print(f"  ✓ {count} files backed up to {dest}")

    print(f"\n  Operation blocked — commit or stash before destructive Git ops.")
    print(f"  Backup saved: {dest}")
    return 1

if __name__ == "__main__":
    sys.exit(main())
