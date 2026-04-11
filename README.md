# Agent OS

`agent-os` is the source of truth for the user's development and research agent workflow.

It defines:
- global memory
- curated shared skills
- Claude subagents
- project templates
- sync rules for Claude, Codex, and Cursor
- a CLI that always runs local Python work in Conda `base`

## Runtime Policy
- Local Python-backed `agent-os` commands must run in `conda base`
- Homebrew Python is not the supported runtime for `agent-os`
- Claude, Cursor, Git, and other non-Python tools stay outside Conda

## Commands
- `agent-os doctor`
- `agent-os sync`
- `agent-os bootstrap [path]`
- `agent-os worktree <type> <name...>`
- `agent-os start [claude|cursor|codex]`

## Structure
- `core/`: memory, hooks, subagents, policy
- `skills/vendor/`: curated upstream skills
- `skills/house/`: custom operating skills
- `templates/project/`: reusable repo scaffold
- `adapters/`: tool-specific runtime notes
- `docs/`: architecture and operating-system-level reference docs
- `src/agent_os/`: CLI implementation

## Source Of Truth
- Edit files in this repo
- Run `agent-os sync`
- Use `agent-os bootstrap` in each project repo
- Architecture reference: `docs/AGENT_OS_ARCHITECTURE.md`

## Private Experimental Layer
`agent-os` can also host private, unsynced experimental skills.

These are intended for local lab work only:
- they are not part of normal `agent-os sync`
- they are not installed into Codex or Cursor
- they are enabled on demand for Claude only
- they should operate on lab copies, not live skills

Use:
- `agent-os private-skill status <name> --tool claude`
- `agent-os private-skill enable <name> --tool claude`
- `agent-os private-skill disable <name> --tool claude`
