#!/usr/bin/env python3
"""PostToolUse hook — auto-format files after Write / Edit / MultiEdit.

Runs ruff for .py files (Conda base) and prettier for JS/TS/JSON/CSS
(only if prettier is already on PATH — does not install it).
Always exits 0 so a formatter error never blocks Claude.
"""
import json
import subprocess
import sys
from pathlib import Path

CONDA_PREFIX = "/Users/junlee/miniconda3"


def get_file_path(payload: dict) -> str | None:
    """All of Write, Edit, and MultiEdit have a top-level file_path."""
    tool_input = payload.get("tool_input", {})
    if isinstance(tool_input, dict):
        return tool_input.get("file_path") or None
    return None


def format_python(path: Path) -> None:
    ruff = Path(CONDA_PREFIX) / "bin" / "ruff"
    cmd = [str(ruff), "format", "--quiet", str(path)]
    if not ruff.exists():
        cmd = ["ruff", "format", "--quiet", str(path)]
    subprocess.run(cmd, capture_output=True)


def format_js(path: Path) -> None:
    # Only run if prettier is available; don't install via npx.
    result = subprocess.run(["which", "prettier"], capture_output=True)
    if result.returncode == 0:
        subprocess.run(["prettier", "--write", str(path)], capture_output=True)


def main() -> int:
    raw = sys.stdin.read().strip()
    if not raw:
        return 0
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return 0

    fp = get_file_path(payload)
    if not fp:
        return 0

    p = Path(fp)
    if not p.exists():
        return 0

    ext = p.suffix.lower()
    if ext == ".py":
        format_python(p)
    elif ext in {".js", ".ts", ".jsx", ".tsx", ".json", ".css"}:
        format_js(p)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
