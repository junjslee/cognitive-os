# Cursor Adapter

The Cursor adapter extends cognitive-os's shared skill library into Cursor's environment, so the skills you use in Claude Code or Codex are also available during editing and review sessions in Cursor.

## What it does

`cognitive-os sync` installs shared skills into `~/.cursor/skills/`.

It does not modify Cursor's built-in managed skills in `~/.cursor/skills-cursor/`.

Project repos rely on:
- `AGENTS.md` — the vendor-neutral operating manual that Cursor can reference for project context
- `docs/*.md` — shared project memory
- Optional project `.cursor/skills/` if you add repo-specific skills later

## Why it matters

Cursor's strengths are editing, diff review, and navigation. cognitive-os treats it as the editing and inspection surface — not the primary runtime authority. That separation is intentional.

When you're doing a careful review pass in Cursor, your skills and project docs are available. But the source of truth for what the project is building, what decisions were made, and what the next step is — that lives in the repo docs, governed by cognitive-os. Cursor reads from that, not the other way around.

## What Cursor is good for

- Editing and diff review
- Navigation and inspection
- Skill-assisted refactoring

## Files managed

| Asset | Location |
|---|---|
| Shared skills | `~/.cursor/skills/` |
| Project instructions | `<project>/AGENTS.md` |
| Project memory | `<project>/docs/*.md` |
