#!/usr/bin/env python3
"""
Checkpoint hook — wired to Stop and SubagentStop events.
Creates a git checkpoint commit whenever Claude finishes a turn and there
are uncommitted changes. Always exits 0 so it never blocks Claude.
Checkpoint commits use --no-verify to bypass pre-commit hooks that may
reject work-in-progress state (lint, type checks, etc.).
"""
import datetime
import subprocess
from pathlib import Path


def _run(args: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, capture_output=True, text=True, cwd=str(cwd))


def main() -> int:
    cwd = Path.cwd()

    result = _run(["git", "rev-parse", "--show-toplevel"], cwd=cwd)
    if result.returncode != 0:
        return 0

    git_root = Path(result.stdout.strip())

    status = _run(["git", "status", "--porcelain"], cwd=git_root)
    if status.returncode != 0 or not status.stdout.strip():
        return 0

    _run(["git", "add", "-A"], cwd=git_root)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    _run(["git", "commit", "--no-verify", "-m", f"chkpt: {timestamp}"], cwd=git_root)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
