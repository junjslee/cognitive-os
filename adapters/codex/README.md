# Codex Adapter

The Codex adapter ensures Codex CLI reads from the same shared project truth as your other tools — no separate config, no diverging context.

## What it does

`cognitive-os sync` installs shared skills into `~/.codex/skills/`.

Codex's primary context comes from:
- `AGENTS.md` — the vendor-neutral repo operating manual, present in every cognitive-os project
- `docs/*.md` — shared project memory: requirements, plan, progress, next steps, run context
- Synced skills — all `custom/` and `vendor/` skills installed globally

`cognitive-os` does not overwrite Codex system skills under `~/.codex/skills/.system`.

## Why it matters

Codex has strong native support for `AGENTS.md`-style instructions. cognitive-os takes advantage of this: every project scaffolded with `cognitive-os new-project` already has an `AGENTS.md` that reflects your global cognitive contract, workflow policy, and project-specific constraints.

This means Codex gets the same operating environment as Claude Code — it just receives it through a different delivery path. The source of truth is the same repo. The adapter is the mechanism, not the authority.

## What Codex is good for

- Codex-first implementation work
- Direct use inside Codex CLI or IDE surfaces
- The same shared repo memory with lighter tool-specific overhead

## Files managed

| Asset | Location |
|---|---|
| Shared skills | `~/.codex/skills/` |
| Project instructions | `<project>/AGENTS.md` |
| Project memory | `<project>/docs/*.md` |
