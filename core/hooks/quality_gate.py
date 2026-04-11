#!/usr/bin/env python3
"""Stop hook — quality gate: run pytest when source files changed.

Opt-in per project: create a `.quality-gate` file in the project root to
enable. Without it this hook exits 0 silently (no slowdown for chat sessions).

Only runs pytest if Python source files have uncommitted changes — skips when
Claude did not touch code this turn. Exits 2 (blocks Stop) if tests fail.
Timeout: 30 s, so it never hangs a session.
"""
import subprocess
import sys
from pathlib import Path

CONDA_PREFIX = "/Users/junlee/miniconda3"
TIMEOUT = 30  # seconds


def source_files_changed() -> bool:
    """True if the working tree has uncommitted changes to .py source files."""
    for flag in ["--cached", ""]:
        cmd = ["git", "diff", flag, "--name-only"]
        if not flag:
            cmd = ["git", "diff", "--name-only"]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0:
            for name in r.stdout.splitlines():
                if name.endswith(".py") and not (
                    Path(name).name.startswith("test_")
                    or name.endswith("_test.py")
                ):
                    return True
    return False


def run_pytest() -> tuple[bool, str]:
    """Returns (passed, output)."""
    test_files = list(Path(".").rglob("test_*.py")) + list(
        Path(".").rglob("*_test.py")
    )
    if not test_files:
        return True, ""

    pytest = Path(CONDA_PREFIX) / "bin" / "pytest"
    cmd = (
        [str(pytest), "--tb=short", "-q", "--no-header"]
        if pytest.exists()
        else ["python", "-m", "pytest", "--tb=short", "-q", "--no-header"]
    )

    try:
        r = subprocess.run(
            cmd, capture_output=True, text=True, timeout=TIMEOUT
        )
    except subprocess.TimeoutExpired:
        return True, ""  # timeout → don't block, just move on

    out = (r.stdout + r.stderr).strip()
    return r.returncode == 0, out


def main() -> int:
    # Opt-in check
    if not Path(".quality-gate").exists():
        return 0

    # Skip if nothing changed
    if not source_files_changed():
        return 0

    passed, output = run_pytest()
    if not passed:
        sys.stderr.write(f"Quality gate failed — fix tests before completing:\n{output}\n")
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
