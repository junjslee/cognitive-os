from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
HOME = Path.home()
CONDA_ROOT = Path(os.environ.get("AGENT_OS_CONDA_ROOT", str(HOME / "miniconda3")))
EXPECTED_BASE_PREFIX = str(CONDA_ROOT)
RUNTIME_MANIFEST = json.loads((REPO_ROOT / "core" / "runtime_manifest.json").read_text(encoding="utf-8"))
HARNESSES_DIR = REPO_ROOT / "core" / "harnesses"


# ---------------------------------------------------------------------------
# Shell / process helpers
# ---------------------------------------------------------------------------

def _run(
    args: list[str],
    *,
    check: bool = True,
    capture_output: bool = True,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        check=check,
        text=True,
        capture_output=capture_output,
        cwd=str(cwd) if cwd else None,
    )


def _command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def _write_text(path: Path, content: str, *, executable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        if existing == content:
            if executable:
                path.chmod(path.stat().st_mode | 0o111)
            return
    path.write_text(content, encoding="utf-8")
    if executable:
        path.chmod(path.stat().st_mode | 0o111)


def _copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _copy_tree(src: Path, dst: Path) -> None:
    for file_path in src.rglob("*"):
        if file_path.is_dir():
            continue
        rel = file_path.relative_to(src)
        _copy_file(file_path, dst / rel)


def _replace_tokens(content: str, mapping: dict[str, str]) -> str:
    rendered = content
    for key, value in mapping.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered


def _today() -> str:
    return date.today().isoformat()


# ---------------------------------------------------------------------------
# Machine context — cross-platform (macOS + Linux)
# ---------------------------------------------------------------------------

def _sysctl(name: str) -> str:
    try:
        return _run(["sysctl", "-n", name]).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _sw_vers(flag: str) -> str:
    try:
        return _run(["sw_vers", flag]).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _linux_mem_gb() -> str:
    try:
        with open("/proc/meminfo", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("MemTotal:"):
                    kb = int(line.split()[1])
                    return str(kb // 1024 // 1024)
    except (OSError, ValueError, IndexError):
        pass
    return "unknown"


def _linux_cpu() -> str:
    try:
        with open("/proc/cpuinfo", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except (OSError, IndexError):
        pass
    try:
        out = _run(["lscpu"]).stdout
        for line in out.splitlines():
            if "model name" in line.lower():
                return line.split(":", 1)[1].strip()
    except (subprocess.CalledProcessError, FileNotFoundError, IndexError):
        pass
    return "unknown"


def _linux_os_version() -> str:
    try:
        with open("/etc/os-release", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("PRETTY_NAME="):
                    return line.split("=", 1)[1].strip().strip('"')
    except (OSError, IndexError):
        pass
    try:
        return _run(["uname", "-sr"]).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _tool_version(cmd: list[str], *, first_line: bool = False) -> str:
    try:
        output = _run(cmd).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "not installed"
    if first_line:
        return output.splitlines()[0] if output else "unknown"
    return output or "unknown"


def _machine_context() -> dict[str, str]:
    is_macos = platform.system() == "Darwin"
    if is_macos:
        mem_bytes = _sysctl("hw.memsize")
        mem_gb = str(int(mem_bytes) // 1024 // 1024 // 1024) if mem_bytes.isdigit() else "unknown"
        cpu = _sysctl("machdep.cpu.brand_string")
        os_version = _sw_vers("-productVersion")
        os_build = _sw_vers("-buildVersion")
    else:
        mem_gb = _linux_mem_gb()
        cpu = _linux_cpu()
        os_version = _linux_os_version()
        try:
            os_build = _run(["uname", "-r"]).stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            os_build = "unknown"
    return {
        "DATE": _today(),
        "HOME_PATH": str(HOME),
        "CONDA_ROOT": str(CONDA_ROOT),
        "OS_VERSION": os_version,
        "OS_BUILD": os_build,
        "CPU": cpu,
        "MEM_GB": mem_gb,
        "ARCH": platform.machine(),
        "SHELL": os.environ.get("SHELL", "unknown"),
        "CLAUDE_VERSION": _tool_version(["claude", "--version"]),
        "CURSOR_VERSION": _tool_version(["cursor", "--version"], first_line=True),
        "GIT_VERSION": _tool_version(["git", "--version"]),
        "NODE_VERSION": _tool_version(["node", "-v"]),
        "NPM_VERSION": _tool_version(["npm", "-v"]),
        "PYTHON_POLICY": f"All local Python-backed agent-os commands run in Conda base at {CONDA_ROOT}.",
    }


# ---------------------------------------------------------------------------
# Asset helpers
# ---------------------------------------------------------------------------

def _load_template(rel_path: str) -> str:
    return (REPO_ROOT / "templates" / "project" / rel_path).read_text(encoding="utf-8")


def _managed_skills() -> list[Path]:
    selected = set(RUNTIME_MANIFEST["vendor_skills"] + RUNTIME_MANIFEST["custom_skills"])
    candidates = list((REPO_ROOT / "skills" / "vendor").glob("*/SKILL.md")) + list(
        (REPO_ROOT / "skills" / "custom").glob("*/SKILL.md")
    )
    skill_dirs: list[Path] = []
    for skill_file in candidates:
        skill_dir = skill_file.parent
        if skill_dir.name in selected:
            skill_dirs.append(skill_dir)
    return sorted(skill_dirs, key=lambda p: p.name)


def _resolve_memory_file(name: str) -> Path:
    """Return the personal file if it exists, else fall back to the example."""
    personal = REPO_ROOT / "core" / "memory" / "global" / f"{name}.md"
    if personal.exists():
        return personal
    return REPO_ROOT / "core" / "memory" / "global" / f"{name}.example.md"


# ---------------------------------------------------------------------------
# init
# ---------------------------------------------------------------------------

def _init_memory() -> int:
    """Bootstrap personal memory files from *.example.md templates."""
    memory_dir = REPO_ROOT / "core" / "memory" / "global"
    names = ["overview", "operator_profile", "workflow_policy", "python_runtime_policy"]

    created: list[str] = []
    skipped: list[str] = []

    for name in names:
        personal = memory_dir / f"{name}.md"
        example = memory_dir / f"{name}.example.md"
        if personal.exists():
            skipped.append(f"{name}.md")
            continue
        if not example.exists():
            print(f"Warning: {name}.example.md not found, skipping.", file=sys.stderr)
            continue
        shutil.copy2(example, personal)
        created.append(f"{name}.md")

    if created:
        print("Created personal memory files:")
        for f in created:
            print(f"  core/memory/global/{f}")
        print("\nEdit these files with your personal context, then run `agent-os sync`.")
    if skipped:
        print(f"Already present (not overwritten): {', '.join(skipped)}")
    if not created and not skipped:
        print("Nothing to do.")
    return 0


# ---------------------------------------------------------------------------
# sync
# ---------------------------------------------------------------------------

def _render_user_claude_md() -> str:
    imports = "\n".join(
        f"@{_resolve_memory_file(name)}"
        for name in ["overview", "operator_profile", "workflow_policy", "python_runtime_policy"]
    )
    return (
        "# Agent OS Global Memory\n\n"
        "This file is generated by `agent-os sync`.\n"
        "Edit the source of truth in `~/agent-os/core/memory/global/`.\n\n"
        f"{imports}\n"
    )


def _agent_os_settings() -> dict:
    hooks_dir = REPO_ROOT / "core" / "hooks"
    py = f"{CONDA_ROOT}/bin/python"

    def hook_cmd(script: str, *, async_: bool = False) -> dict:
        h: dict = {"type": "command", "command": f"{py} {hooks_dir / script}"}
        if async_:
            h["async"] = True
        return h

    checkpoint_cmd = f"{py} {hooks_dir / 'checkpoint.py'}"

    return {
        "permissions": {
            "deny": [
                "Read(./.env)",
                "Read(./.env.*)",
                "Read(./secrets/**)",
                "Read(./**/*.pem)",
                "Read(./**/*.key)",
                "Read(./**/.npmrc)",
            ]
        },
        "hooks": {
            "SessionStart": [
                {"hooks": [hook_cmd("session_context.py")]}
            ],
            "PreToolUse": [
                {
                    "matcher": "Bash",
                    "hooks": [hook_cmd("block_dangerous.py")],
                }
            ],
            "PostToolUse": [
                {
                    "matcher": "Write|Edit|MultiEdit",
                    "hooks": [hook_cmd("format.py", async_=True)],
                },
                {
                    "matcher": "Write|Edit|MultiEdit",
                    "hooks": [hook_cmd("test_runner.py")],
                },
            ],
            "PermissionRequest": [
                {
                    "matcher": "Read|Glob|Grep",
                    "hooks": [{"type": "command", "command": "echo '{\"decision\":\"allow\"}'"}],
                }
            ],
            "PreCompact": [
                {"hooks": [hook_cmd("precompact_backup.py", async_=True)]}
            ],
            "Stop": [
                {"hooks": [hook_cmd("quality_gate.py")]},
                {"hooks": [{"type": "command", "command": checkpoint_cmd}]},
            ],
            "SubagentStop": [
                {"hooks": [{"type": "command", "command": checkpoint_cmd}]}
            ],
        },
    }


def _merge_claude_settings(existing: dict, agent_os: dict) -> dict:
    """Merge agent_os settings into existing without removing anything.

    - permissions.deny: union (no duplicates)
    - hooks.<event>: append agent-os entries whose commands aren't already present
    - All other existing keys: preserved untouched
    """
    import copy
    merged = copy.deepcopy(existing)

    deny = merged.setdefault("permissions", {}).setdefault("deny", [])
    for rule in agent_os.get("permissions", {}).get("deny", []):
        if rule not in deny:
            deny.append(rule)

    for event, entries in agent_os.get("hooks", {}).items():
        existing_entries = merged.setdefault("hooks", {}).setdefault(event, [])
        registered_cmds: set[str] = set()
        for entry in existing_entries:
            for h in entry.get("hooks", []):
                registered_cmds.add(h.get("command", ""))
        for entry in entries:
            new_cmds = {h.get("command", "") for h in entry.get("hooks", [])}
            if not new_cmds.issubset(registered_cmds):
                existing_entries.append(entry)

    return merged


def _sync_hermes_runtime() -> bool:
    """Sync skills and operator context to Hermes if installed.

    Returns True if Hermes was found and synced, False if not installed.
    """
    hermes_root = HOME / ".hermes"
    if not hermes_root.exists():
        return False

    # Skills — Hermes uses agentskills.io format (same as our SKILL.md layout)
    skills_dst = hermes_root / "skills"
    for skill_dir in _managed_skills():
        _copy_tree(skill_dir, skills_dst / skill_dir.name)

    # Operator context composite — always regenerated from source
    operator_md = hermes_root / "OPERATOR.md"
    sections: list[str] = [
        "# Operator Context\n\n"
        "Generated by `agent-os sync`. "
        "Edit sources in `~/agent-os/core/memory/global/`.\n\n"
    ]
    for mem_file in [
        REPO_ROOT / "core" / "memory" / "global" / "overview.md",
        REPO_ROOT / "core" / "memory" / "global" / "operator_profile.md",
        REPO_ROOT / "core" / "memory" / "global" / "workflow_policy.md",
    ]:
        if mem_file.exists():
            sections.append(mem_file.read_text(encoding="utf-8").rstrip() + "\n\n")
    _write_text(operator_md, "".join(sections))

    # SOUL.md — Hermes's session-start context loader. Write once; user owns it after that.
    soul_path = hermes_root / "SOUL.md"
    if not soul_path.exists():
        soul_content = (
            "# Hermes Soul\n\n"
            "You are a technical AI assistant working with the operator described below.\n"
            "Load this context at the start of every session.\n\n"
            f"{{{{read {operator_md}}}}}\n"
        )
        _write_text(soul_path, soul_content)
        print(f"  - Created Hermes SOUL.md: {soul_path}")

    return True


def _sync_user_runtime() -> None:
    claude_root = HOME / ".claude"
    cursor_root = HOME / ".cursor" / "skills"
    codex_root = HOME / ".codex" / "skills"

    _write_text(claude_root / "CLAUDE.md", _render_user_claude_md())

    # Merge agent-os settings into existing settings.json rather than replace,
    # so plugin-installed hooks and keys are preserved across syncs.
    settings_path = claude_root / "settings.json"
    agent_os = _agent_os_settings()
    if settings_path.exists():
        try:
            existing = json.loads(settings_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {}
    else:
        existing = {}
    merged = _merge_claude_settings(existing, agent_os)
    _write_text(settings_path, json.dumps(merged, indent=2) + "\n")

    for agent_file in (REPO_ROOT / "core" / "agents").glob("*.md"):
        _copy_file(agent_file, claude_root / "agents" / agent_file.name)

    for skill_dir in _managed_skills():
        _copy_tree(skill_dir, claude_root / "skills" / skill_dir.name)
        _copy_tree(skill_dir, cursor_root / skill_dir.name)
        _copy_tree(skill_dir, codex_root / skill_dir.name)

    hermes_synced = _sync_hermes_runtime()

    print("Synced user runtime:")
    print(f"  - Claude: {claude_root}")
    print(f"  - Cursor skills: {cursor_root}")
    print(f"  - Codex skills: {codex_root}")
    if hermes_synced:
        print(f"  - Hermes: {HOME / '.hermes'}")


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------

def _list_runtime() -> None:
    claude_root = HOME / ".claude"

    print("=== Agents ===")
    agents_dir = claude_root / "agents"
    if agents_dir.exists():
        for f in sorted(agents_dir.glob("*.md")):
            print(f"  {f.stem}")
    else:
        print("  (none)")

    print("\n=== Skills ===")
    skills_dir = claude_root / "skills"
    managed = {p.name for p in _managed_skills()}
    if skills_dir.exists():
        for d in sorted(skills_dir.iterdir()):
            if d.is_dir():
                tag = " [agent-os]" if d.name in managed else " [external]"
                print(f"  {d.name}{tag}")
    else:
        print("  (none)")

    print("\n=== Plugins ===")
    installed_json = claude_root / "plugins" / "installed_plugins.json"
    if installed_json.exists():
        data = json.loads(installed_json.read_text(encoding="utf-8"))
        for name in sorted(data.get("plugins", {}).keys()):
            print(f"  {name}")
    else:
        print("  (none)")

    print("\n=== Hooks (global settings.json) ===")
    settings_path = claude_root / "settings.json"
    if settings_path.exists():
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
        for event, entries in settings.get("hooks", {}).items():
            for entry in entries:
                matcher = entry.get("matcher", "*")
                for h in entry.get("hooks", []):
                    cmd = h.get("command", "")
                    short = cmd.split("/")[-1] if "/" in cmd else cmd
                    print(f"  {event} [{matcher}] → {short}")


# ---------------------------------------------------------------------------
# private-skill
# ---------------------------------------------------------------------------

def _private_skill_source(name: str) -> Path:
    return REPO_ROOT / "skills" / "private" / name


def _private_skill_install_path(name: str, tool: str) -> Path:
    if tool != "claude":
        raise ValueError(f"unsupported private skill tool: {tool}")
    return HOME / ".claude" / "skills" / name


def _private_skill(action: str, name: str, tool: str) -> int:
    if tool != "claude":
        print(f"Private skills currently support only Claude. Unsupported tool: {tool}", file=sys.stderr)
        return 1

    source = _private_skill_source(name)
    install_path = _private_skill_install_path(name, tool)
    source_skill = source / "SKILL.md"
    installed = install_path.exists()

    if action == "status":
        print(f"Private skill: {name}")
        print(f"Tool: {tool}")
        print(f"Source: {source}")
        print(f"Install path: {install_path}")
        print(f"Source status: {'present' if source_skill.exists() else 'missing SKILL.md'}")
        print(f"Installed: {'yes' if installed else 'no'}")
        return 0

    if not source_skill.exists():
        print(f"Private skill source missing: {source_skill}", file=sys.stderr)
        return 1

    if action == "enable":
        if install_path.exists():
            shutil.rmtree(install_path)
        _copy_tree(source, install_path)
        print(f"Enabled private skill '{name}' for {tool}: {install_path}")
        return 0

    if action == "disable":
        if install_path.exists():
            shutil.rmtree(install_path)
            print(f"Disabled private skill '{name}' for {tool}: removed {install_path}")
        else:
            print(f"Private skill '{name}' is already absent for {tool}: {install_path}")
        return 0

    print(f"Unsupported private-skill action: {action}", file=sys.stderr)
    return 1


# ---------------------------------------------------------------------------
# doctor
# ---------------------------------------------------------------------------

def _doctor() -> int:
    failures: list[str] = []
    print("Agent OS doctor")
    print(f"Repo root: {REPO_ROOT}")
    print(f"Expected Conda root: {CONDA_ROOT}")

    conda_bin = CONDA_ROOT / "bin" / "conda"
    if not conda_bin.exists():
        failures.append(f"missing conda binary at {conda_bin}")
    else:
        print(f"[ok] conda binary: {conda_bin}")

    try:
        envs = _run([str(conda_bin), "info", "--envs"]).stdout
        if re.search(r"^base\s+", envs, re.MULTILINE):
            print("[ok] conda base environment exists")
        else:
            failures.append("conda base environment not found")
    except subprocess.CalledProcessError as exc:
        failures.append(f"failed to inspect conda envs: {exc}")

    try:
        probe = _run(
            [
                str(conda_bin),
                "run",
                "-n",
                "base",
                "python",
                "-c",
                "import json,sys; print(json.dumps({'executable': sys.executable, 'prefix': sys.prefix}))",
            ]
        ).stdout.strip()
        if probe:
            payload = json.loads(probe.splitlines()[-1])
            executable = payload["executable"]
            prefix = payload["prefix"]
            if EXPECTED_BASE_PREFIX not in executable or EXPECTED_BASE_PREFIX not in prefix:
                failures.append(
                    f"conda base python did not resolve under {EXPECTED_BASE_PREFIX}: "
                    f"executable={executable} prefix={prefix}"
                )
            else:
                print(f"[ok] conda base python: {executable}")
        else:
            failures.append("conda run probe returned no output")
    except (subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        failures.append(f"failed to run conda base python probe: {exc}")

    # Core tools — required on every machine
    for tool in ["claude", "git", "jq"]:
        if _command_exists(tool):
            print(f"[ok] tool available: {tool}")
        else:
            failures.append(f"missing tool: {tool}")

    # Local-only tools — expected on a dev workstation, not on remote servers or clusters
    for tool in ["cursor"]:
        if _command_exists(tool):
            print(f"[ok] tool available: {tool}")
        else:
            print(f"[info] local-only tool not installed: {tool} (not required on remote machines)")

    # Optional tools
    for tool in ["tmux", "gh", "codex"]:
        state = "present" if _command_exists(tool) else "not installed"
        print(f"[info] optional tool {tool}: {state}")

    if failures:
        print("\nDoctor failed:")
        for item in failures:
            print(f"  - {item}")
        return 1

    print("\nDoctor passed.")
    return 0


# ---------------------------------------------------------------------------
# worktree / start / validate / update
# ---------------------------------------------------------------------------

def _current_repo_root(cwd: Path) -> Path:
    try:
        output = _run(["git", "rev-parse", "--show-toplevel"], cwd=cwd).stdout.strip()
    except subprocess.CalledProcessError:
        return cwd.resolve()
    return Path(output)


def _resolve_bootstrap_target(path_arg: str) -> Path:
    candidate = Path(path_arg).expanduser()
    if path_arg == ".":
        return _current_repo_root(Path.cwd())
    return candidate.resolve()


def _worktree(task_type: str, task_name: list[str], base_ref: str | None, cwd: Path) -> int:
    repo_root = _current_repo_root(cwd)
    if not (repo_root / ".git").exists():
        print(f"Not a git repository: {repo_root}", file=sys.stderr)
        return 1

    slug = re.sub(r"[^a-z0-9]+", "-", " ".join(task_name).lower()).strip("-")
    if not slug:
        print("Unable to derive worktree slug.", file=sys.stderr)
        return 1

    branch_name = f"{task_type}/{slug}"
    parent_dir = repo_root.parent
    worktree_path = parent_dir / f"{repo_root.name}__{task_type}-{slug}"

    if not base_ref:
        base_ref = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_root).stdout.strip()

    branch_exists = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch_name}"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    ).returncode == 0

    if branch_exists:
        _run(["git", "worktree", "add", str(worktree_path), branch_name], cwd=repo_root, capture_output=False)
    else:
        _run(
            ["git", "worktree", "add", "-b", branch_name, str(worktree_path), base_ref],
            cwd=repo_root,
            capture_output=False,
        )

    print(f"Created worktree: {worktree_path}")
    print(f"Branch: {branch_name}")
    return 0


def _start(tool: str, cwd: Path) -> int:
    if tool == "claude":
        os.execvp("claude", ["claude"])
    if tool == "cursor":
        os.execvp("cursor", ["cursor", str(cwd)])
    if tool == "codex":
        if _command_exists("codex"):
            os.execvp("codex", ["codex"])
        print("Codex CLI is not installed on PATH. Use Codex where available and rely on AGENTS.md plus synced skills.")
        return 1
    print(f"Unsupported tool: {tool}", file=sys.stderr)
    return 1


def _validate_manifest() -> int:
    failures: list[str] = []
    warnings: list[str] = []

    all_declared = RUNTIME_MANIFEST["vendor_skills"] + RUNTIME_MANIFEST["custom_skills"]

    for bucket in ("vendor", "custom"):
        key = f"{bucket}_skills"
        for name in RUNTIME_MANIFEST[key]:
            skill_md = REPO_ROOT / "skills" / bucket / name / "SKILL.md"
            if not skill_md.exists():
                failures.append(f"[{bucket}] '{name}' declared in manifest but SKILL.md not found at {skill_md}")
            else:
                print(f"[ok] [{bucket}] {name}")

    for bucket in ("vendor", "custom"):
        bucket_dir = REPO_ROOT / "skills" / bucket
        if not bucket_dir.exists():
            continue
        for skill_dir in sorted(bucket_dir.iterdir()):
            if skill_dir.is_dir() and skill_dir.name not in all_declared:
                warnings.append(f"[{bucket}] '{skill_dir.name}' directory exists but is not in manifest")

    agents_dir = REPO_ROOT / "core" / "agents"
    if agents_dir.exists():
        for f in sorted(agents_dir.glob("*.md")):
            print(f"[ok] [agent] {f.stem}")
    else:
        failures.append("core/agents/ directory missing")

    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  ! {w}")

    if failures:
        print("\nValidation failed:")
        for f in failures:
            print(f"  x {f}")
        return 1

    print("\nValidation passed.")
    return 0


def _update() -> int:
    if not (REPO_ROOT / ".git").exists():
        print("agent-os repo has no .git directory — cannot update.", file=sys.stderr)
        return 1
    try:
        result = _run(["git", "pull", "--ff-only"], cwd=REPO_ROOT, capture_output=False)
        return result.returncode
    except subprocess.CalledProcessError as exc:
        print(f"Update failed: {exc}", file=sys.stderr)
        return 1


# ---------------------------------------------------------------------------
# Harness system
# ---------------------------------------------------------------------------

def _load_harnesses() -> dict[str, dict]:
    """Load all harness definitions from core/harnesses/."""
    harnesses: dict[str, dict] = {}
    if not HARNESSES_DIR.exists():
        return harnesses
    for json_file in sorted(HARNESSES_DIR.glob("*.json")):
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
            harnesses[data["name"]] = data
        except (json.JSONDecodeError, KeyError):
            pass
    return harnesses


def _collect_project_signals(project_root: Path) -> tuple[str, set[str]]:
    """Return (dependency_text, directory_name_set) for a project root.

    Reads dependency/manifest files for import signatures, and walks one level
    of subdirectories for directory-name signals. Kept shallow and fast.
    """
    dep_files = [
        "requirements.txt", "requirements-dev.txt", "requirements_dev.txt",
        "pyproject.toml", "setup.py", "setup.cfg", "package.json",
        "Pipfile", "environment.yml", "environment.yaml",
    ]
    dep_parts: list[str] = []
    for name in dep_files:
        p = project_root / name
        if p.exists():
            try:
                dep_parts.append(p.read_text(encoding="utf-8", errors="ignore"))
            except OSError:
                pass
    dep_text = "\n".join(dep_parts).lower()

    dir_names: set[str] = set()
    try:
        for item in project_root.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                dir_names.add(item.name)
                try:
                    for subitem in item.iterdir():
                        if subitem.is_dir() and not subitem.name.startswith("."):
                            dir_names.add(subitem.name)
                except OSError:
                    pass
    except OSError:
        pass

    return dep_text, dir_names


def _score_harness(
    harness: dict,
    project_root: Path,
    dep_text: str,
    dir_names: set[str],
) -> tuple[int, list[str]]:
    """Score a harness against collected project signals.

    Weights: import signature = 3, file pattern = 2, directory = 1, config file = 1.
    Returns (score, list_of_matched_signal_descriptions).
    """
    score = 0
    signals: list[str] = []
    detection = harness.get("detection", {})

    # Import signatures in dependency manifests — strongest signal
    for sig in detection.get("import_signatures", []):
        if sig.lower() in dep_text:
            score += 3
            signals.append(f"dependency: {sig}")

    # File patterns — concrete structural evidence (early-exit after 3 matches)
    for pattern in detection.get("file_patterns", []):
        matches: list[Path] = []
        try:
            for m in project_root.glob(pattern):
                matches.append(m)
                if len(matches) >= 3:
                    break
        except (OSError, ValueError):
            continue
        if matches:
            score += 2
            signals.append(f"file: {pattern} ({len(matches)}{'+ ' if len(matches) >= 3 else ' '}found)")

    # Directory names — contextual hint
    for dname in detection.get("directory_names", []):
        if dname in dir_names:
            score += 1
            signals.append(f"directory: {dname}/")

    # Config files at project root — specific but weak
    for config in detection.get("config_files", []):
        if (project_root / config).exists():
            score += 1
            signals.append(f"config: {config}")

    return score, signals


def _detect_project_harness(project_root: Path) -> list[tuple[str, int, list[str]]]:
    """Detect the most likely harness type for a project.

    Returns a list of (harness_name, score, signals) sorted by score descending,
    excluding the generic fallback (which is always available via `harness apply`).
    """
    harnesses = _load_harnesses()
    if not harnesses:
        return []
    dep_text, dir_names = _collect_project_signals(project_root)
    results: list[tuple[str, int, list[str]]] = []
    for name, harness in harnesses.items():
        if name == "generic":
            continue
        score, signals = _score_harness(harness, project_root, dep_text, dir_names)
        results.append((name, score, signals))
    results.sort(key=lambda x: x[1], reverse=True)
    return results


def _render_harness_md(harness: dict) -> str:
    """Render the HARNESS.md content for a given harness definition."""
    name = harness["name"]
    label = harness["label"]
    description = harness["description"]
    profile = harness["execution_profile"]
    profile_desc = harness.get("profile_description", "")
    workflow_notes = harness.get("workflow_notes", [])
    safety_notes = harness.get("safety_notes", [])
    agents = harness.get("recommended_agents", [])
    skills = harness.get("recommended_skills", [])

    lines: list[str] = [
        f"# Project Harness: {label}",
        "",
        f"Generated by `agent-os harness apply {name}`.",
        "Edit this file to customize the operating context for this project.",
        "",
        f"> {description}",
        "",
        "---",
        "",
        "## Execution Profile",
        "",
        f"`{profile}`" + (f" — {profile_desc}" if profile_desc else ""),
        "",
    ]

    if workflow_notes:
        lines += ["## Workflow Notes", ""]
        for note in workflow_notes:
            lines.append(f"- {note}")
        lines.append("")

    if safety_notes:
        lines += ["## Safety", ""]
        for note in safety_notes:
            lines.append(f"- {note}")
        lines.append("")

    if agents:
        lines += ["## Recommended Agents", ""]
        lines.append("`" + "` · `".join(agents) + "`")
        lines.append("")

    if skills:
        lines += ["## Recommended Skills", ""]
        lines.append("`" + "` · `".join(skills) + "`")
        lines.append("")

    return "\n".join(lines)


def _apply_harness_run_context(harness: dict, project_root: Path) -> bool:
    """Append harness-specific content to docs/RUN_CONTEXT.md if it exists.

    Skips silently if the file is absent or the section is already present.
    Returns True if the file was modified.
    """
    additions = harness.get("run_context_additions", [])
    if not additions:
        return False
    run_context_path = project_root / "docs" / "RUN_CONTEXT.md"
    if not run_context_path.exists():
        return False
    current = run_context_path.read_text(encoding="utf-8")
    header = next((line for line in additions if line.startswith("## ")), None)
    if header and header in current:
        return False
    extra = "\n" + "\n".join(additions) + "\n"
    _write_text(run_context_path, current.rstrip() + "\n" + extra)
    return True


def _apply_harness(harness_name: str, project_root: Path, *, force: bool = False) -> int:
    """Write HARNESS.md and extend RUN_CONTEXT.md for the given harness type."""
    harnesses = _load_harnesses()
    if harness_name not in harnesses:
        available = ", ".join(sorted(harnesses.keys()))
        print(f"Unknown harness: '{harness_name}'. Available: {available}", file=sys.stderr)
        return 1

    harness = harnesses[harness_name]
    harness_path = project_root / "HARNESS.md"

    if harness_path.exists() and not force:
        print(f"HARNESS.md already exists in {project_root}. Use --force to overwrite.")
        return 1

    _write_text(harness_path, _render_harness_md(harness))
    print(f"Applied harness '{harness_name}' to {project_root}")
    print(f"  - Created HARNESS.md")

    if _apply_harness_run_context(harness, project_root):
        print(f"  - Updated docs/RUN_CONTEXT.md with {harness_name} context")

    return 0


def _list_harnesses() -> None:
    harnesses = _load_harnesses()
    if not harnesses:
        print("No harnesses found in core/harnesses/")
        return
    print("Available harnesses:")
    print()
    for name, harness in sorted(harnesses.items()):
        description = harness.get("description", "")
        print(f"  {name:<22} {description}")
    print()
    print("Apply: agent-os harness apply <name> [path]")
    print("Detect best fit: agent-os detect [path]")


# ---------------------------------------------------------------------------
# bootstrap / new-project
# ---------------------------------------------------------------------------

def _bootstrap_project(project_root: Path, *, harness_name: str | None = None) -> None:
    project_root.mkdir(parents=True, exist_ok=True)
    mapping = _machine_context()
    mapping["PROJECT_ROOT"] = str(project_root)

    template_files = [
        "AGENTS.md",
        "CLAUDE.md",
        "docs/REQUIREMENTS.md",
        "docs/PLAN.md",
        "docs/PROGRESS.md",
        "docs/RUN_CONTEXT.md",
        "docs/NEXT_STEPS.md",
        ".claude/settings.json",
    ]
    created: list[str] = []
    preserved: list[str] = []
    for rel_path in template_files:
        target = project_root / rel_path
        if target.exists():
            preserved.append(rel_path)
            continue
        content = _replace_tokens(_load_template(rel_path), mapping)
        _write_text(target, content)
        created.append(rel_path)

    settings_local = project_root / ".claude" / "settings.local.json"
    if not settings_local.exists():
        _write_text(settings_local, "{}\n")
        created.append(".claude/settings.local.json")

    gitignore_path = project_root / ".gitignore"
    ignore_line = ".claude/settings.local.json"
    if gitignore_path.exists():
        current = gitignore_path.read_text(encoding="utf-8")
        if ignore_line not in current.splitlines():
            extra = current + ("\n" if not current.endswith("\n") else "") + ignore_line + "\n"
            _write_text(gitignore_path, extra)
    else:
        _write_text(gitignore_path, ignore_line + "\n")
        created.append(".gitignore")

    print(f"Bootstrapped project scaffold in {project_root}")
    if created:
        print("Created:")
        for item in created:
            print(f"  - {item}")
    if preserved:
        print("Preserved existing:")
        for item in preserved:
            print(f"  - {item}")

    # Harness: auto-detect or apply named harness
    if harness_name:
        resolved = harness_name
        if harness_name == "auto":
            results = _detect_project_harness(project_root)
            if results and results[0][1] > 2:
                resolved = results[0][0]
                print(f"\nAuto-detected harness: {resolved} (score {results[0][1]})")
            else:
                resolved = "generic"
                print("\nNo strong harness signal detected — applying generic.")
        print()
        _apply_harness(resolved, project_root)


# ---------------------------------------------------------------------------
# Parser and main
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Agent OS cross-tool runtime manager")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Bootstrap personal memory files from *.example.md templates")
    sub.add_parser("doctor", help="Verify runtime wiring — Conda, core tools, optional tools")
    sub.add_parser("sync", help="Sync managed runtime assets into Claude, Codex, Cursor, and Hermes")
    sub.add_parser("update", help="Pull the latest agent-os from git")
    sub.add_parser("list", help="Show installed agents, skills, plugins, and active hooks")
    sub.add_parser("validate", help="Check manifest integrity — every declared skill must have a SKILL.md")

    for cmd in ("bootstrap", "new-project"):
        p = sub.add_parser(cmd, help="Scaffold the standard project structure")
        p.add_argument("path", nargs="?", default=".")
        p.add_argument(
            "--harness",
            metavar="TYPE",
            help="Apply a harness after scaffolding. Use 'auto' to detect from repo contents.",
        )

    detect = sub.add_parser("detect", help="Detect the best harness type for a project")
    detect.add_argument("path", nargs="?", default=".")

    harness_cmd = sub.add_parser("harness", help="Manage project harnesses")
    harness_sub = harness_cmd.add_subparsers(dest="harness_action", required=True)
    harness_sub.add_parser("list", help="List available harness types")
    h_apply = harness_sub.add_parser("apply", help="Apply a harness to a project")
    h_apply.add_argument("type", help="Harness type (ml-research, python-library, web-app, data-pipeline, generic)")
    h_apply.add_argument("path", nargs="?", default=".")
    h_apply.add_argument("--force", action="store_true", help="Overwrite an existing HARNESS.md")

    worktree = sub.add_parser("worktree", help="Create a git worktree for a bounded task")
    worktree.add_argument("task_type")
    worktree.add_argument("task_name", nargs="+")
    worktree.add_argument("--base", dest="base_ref")

    private_skill = sub.add_parser("private-skill", help="Enable or disable a private experimental skill")
    private_skill.add_argument("action", choices=["enable", "disable", "status"])
    private_skill.add_argument("name")
    private_skill.add_argument("--tool", default="claude")

    start = sub.add_parser("start", help="Start the preferred agent surface")
    start.add_argument("tool", nargs="?", default="claude", choices=["claude", "cursor", "codex"])

    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.command == "init":
        return _init_memory()
    if args.command == "doctor":
        return _doctor()
    if args.command == "sync":
        _sync_user_runtime()
        return 0
    if args.command == "update":
        return _update()
    if args.command == "list":
        _list_runtime()
        return 0
    if args.command == "validate":
        return _validate_manifest()
    if args.command in ("bootstrap", "new-project"):
        _bootstrap_project(
            _resolve_bootstrap_target(args.path),
            harness_name=getattr(args, "harness", None),
        )
        return 0
    if args.command == "detect":
        project_root = _resolve_bootstrap_target(args.path)
        print(f"Analyzing {project_root} ...")
        print()
        results = _detect_project_harness(project_root)
        if not results or results[0][1] == 0:
            print("No harness signals detected. Apply the generic harness or specify one explicitly.")
            print("  agent-os harness apply generic .")
            return 0
        print("Harness scores:")
        print()
        for i, (name, score, signals) in enumerate(results):
            if score == 0:
                continue
            marker = "  ← recommended" if i == 0 and score > 2 else ""
            print(f"  {name:<22} score {score}{marker}")
            for sig in signals[:6]:
                print(f"    · {sig}")
        print()
        best_name, best_score, _ = results[0]
        if best_score > 2:
            print(f"Recommended: {best_name}")
            print(f"  agent-os harness apply {best_name} {args.path}")
        else:
            print("Low confidence — review scores above and choose manually.")
            print("  agent-os harness list")
        return 0
    if args.command == "harness":
        if args.harness_action == "list":
            _list_harnesses()
            return 0
        if args.harness_action == "apply":
            return _apply_harness(
                args.type,
                _resolve_bootstrap_target(args.path),
                force=args.force,
            )
        return 0
    if args.command == "worktree":
        return _worktree(args.task_type, args.task_name, args.base_ref, Path.cwd())
    if args.command == "private-skill":
        return _private_skill(args.action, args.name, args.tool)
    if args.command == "start":
        return _start(args.tool, Path.cwd())
    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
