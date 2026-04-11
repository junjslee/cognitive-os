# Hermes Adapter

`agent-os sync` automatically detects Hermes at `~/.hermes/` and syncs if installed.

## What Gets Synced

| Asset | Destination |
|---|---|
| All managed skills | `~/.hermes/skills/<name>/` |
| Operator context | `~/.hermes/OPERATOR.md` |

## OPERATOR.md

A composite of your three global memory files (overview, operator_profile, workflow_policy).
Hermes does not auto-load it — reference it from `~/.hermes/SOUL.md` if you want Hermes
to carry your operator context:

```markdown
<!-- in ~/.hermes/SOUL.md -->
You are a technical AI assistant working with the operator described below.

{{read ~/agent-os/core/memory/global/operator_profile.md}}
{{read ~/agent-os/core/memory/global/workflow_policy.md}}
```

## Skills

Hermes uses the [agentskills.io](https://agentskills.io) format — the same `SKILL.md`
layout agent-os already uses. All `custom/` and `vendor/` skills sync directly.

## Hooks

Hermes has its own `~/.hermes/hooks/` directory. Claude Code hooks (`block_dangerous.py`,
`checkpoint.py`, etc.) are Claude-specific — they do not transfer to Hermes. To replicate
safety behavior in Hermes, configure its built-in command approval system in `config.yaml`.
