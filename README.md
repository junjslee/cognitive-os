# Agent OS

`agent-os` is the source of truth for your development and research agent workflow.

It defines global memory, curated skills, Claude subagents, project templates, and
sync rules for Claude Code, Codex, Cursor, and Hermes — all managed from one place.

## Install

```bash
cd ~/agent-os
pip install -e .          # installs the agent-os CLI into Conda base
agent-os doctor           # verify runtime wiring
agent-os sync             # push everything to Claude, Codex, Cursor, and Hermes
```

> Set `AGENT_OS_CONDA_ROOT` to override the default Conda path (`~/miniconda3`).

## Commands

| Command | What it does |
|---|---|
| `agent-os doctor` | Verify Conda base, tools, and runtime wiring |
| `agent-os sync` | Push memory, agents, skills, hooks to all tool surfaces |
| `agent-os update` | Pull the latest agent-os from git |
| `agent-os validate` | Check manifest — every declared skill must have a SKILL.md |
| `agent-os list` | Show installed agents, skills, plugins, and active hooks |
| `agent-os new-project [path]` | Scaffold a new project with standard docs and .claude config |
| `agent-os bootstrap [path]` | Alias for new-project |
| `agent-os worktree <type> <name>` | Create a git worktree for a bounded task |
| `agent-os start [claude\|cursor\|codex]` | Open the preferred agent surface |
| `agent-os private-skill <enable\|disable\|status> <name>` | Manage local experimental skills |

## Structure

```
core/
  memory/global/     global memory files loaded into every Claude session
  hooks/             Python scripts for Claude Code lifecycle events
  agents/            agent persona definitions (planner, implementer, reviewer …)
skills/
  vendor/            curated upstream skills (swing-*, create-prd …)
  custom/            your own operating skills (repo-bootstrap, worktree-split …)
  private/           local experimental skills — never synced globally
templates/project/   standard scaffold for new repos
adapters/            tool-specific runtime notes (claude, codex, cursor, hermes)
src/agent_os/        CLI implementation
docs/                architecture reference
labs/                skill development lab
```

## Runtime Policy

- Local Python-backed `agent-os` commands run in Conda `base`
- Homebrew Python is not the supported runtime
- Claude Code, Cursor, Git, and other non-Python tools stay outside Conda
- Set `AGENT_OS_CONDA_ROOT` to point at a non-default Conda install

## Workflow

1. Edit files in this repo
2. Run `agent-os sync`
3. Use `agent-os new-project` in each project repo

## Private Experimental Skills

Skills under `skills/private/` are never synced globally. Enable on demand for Claude only:

```bash
agent-os private-skill enable <name> --tool claude
agent-os private-skill disable <name> --tool claude
agent-os private-skill status <name> --tool claude
```

## Is This Publishable?

The structure and CLI are intentionally generic. To publish your fork:
- Replace `core/memory/global/*.md` with template placeholders (they contain personal info)
- Set `AGENT_OS_CONDA_ROOT` or adjust the default in `cli.py` for different Conda layouts
- Remove or gitignore `~/.hermes/OPERATOR.md` if you prefer not to share operator context
