#!/usr/bin/env python3
"""PostToolUse hook — runs tests when a test file is written or edited.

Only fires if the written file is itself a test file (test_*.py, *_test.py,
*.test.ts, *.spec.ts, etc.). Runs just that file, not the full suite.
Exits 1 on failure (non-blocking) so Claude sees the results without stopping.
"""
import json
import subprocess
import sys
from pathlib import Path

CONDA_PREFIX = Path(sys.executable).parent.parent
TIMEOUT = 60  # seconds


def get_file_path(payload: dict) -> str | None:
    tool_input = payload.get("tool_input", {})
    if isinstance(tool_input, dict):
        return tool_input.get("file_path") or None
    return None


def is_test_file(path: str) -> bool:
    p = Path(path)
    name = p.name
    return (
        name.startswith("test_")
        or name.endswith("_test.py")
        or ".test." in name
        or ".spec." in name
    )


def run_python_tests(path: str) -> tuple[bool, str]:
    pytest = CONDA_PREFIX / "bin" / "pytest"
    cmd = (
        [str(pytest), "--tb=short", "-q", "--no-header", path]
        if pytest.exists()
        else ["python", "-m", "pytest", "--tb=short", "-q", "--no-header", path]
    )
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        return False, "timed out"
    return r.returncode == 0, (r.stdout + r.stderr).strip()


def run_js_tests(path: str) -> tuple[bool, str]:
    # jest if available, otherwise vitest
    for runner in ["jest", "vitest"]:
        result = subprocess.run(["which", runner], capture_output=True)
        if result.returncode == 0:
            try:
                r = subprocess.run(
                    [runner, path], capture_output=True, text=True, timeout=TIMEOUT
                )
            except subprocess.TimeoutExpired:
                return False, "timed out"
            return r.returncode == 0, (r.stdout + r.stderr).strip()
    return True, ""  # no runner found, skip silently


def main() -> int:
    raw = sys.stdin.read().strip()
    if not raw:
        return 0
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return 0

    fp = get_file_path(payload)
    if not fp or not is_test_file(fp):
        return 0

    p = Path(fp)
    ext = p.suffix.lower()

    if ext == ".py":
        passed, output = run_python_tests(fp)
    elif ext in {".ts", ".js", ".tsx", ".jsx"}:
        passed, output = run_js_tests(fp)
    else:
        return 0

    if not passed:
        sys.stderr.write(f"Tests failed [{p.name}]:\n{output}\n")
        return 1  # non-blocking — Claude sees it but isn't stopped
    else:
        sys.stdout.write(f"Tests passed [{p.name}]\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
