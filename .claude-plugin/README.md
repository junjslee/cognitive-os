# cognitive-os — Claude Code plugin

Installs the cognitive-os kernel, skills, and agent personas into Claude Code via the plugin system. Uses the same markdown artifacts this repo ships; the plugin manifest is a thin distribution wrapper, not a fork of the kernel.

## Install (local / development)

```bash
claude --plugin-dir /path/to/cognitive-os
```

## Install (marketplace)

Once submitted via <https://claude.ai/settings/plugins/submit> or <https://platform.claude.com/plugins/submit>:

```
/plugin marketplace add cognitive-os
/plugin install cognitive-os
```

## What you get

- **Skills** — every file under `skills/custom/` and `skills/vendor/` at the repo root (namespaced as `/cognitive-os:<skill-name>`).
- **Agents** — every persona under `adapters/claude/agents/` (`planner`, `researcher`, `implementer`, `reviewer`, `test-runner`, `docs-handoff`, `domain-architect`, `reasoning-auditor`, `governance-safety`, `orchestrator`, `domain-owner`).
- **Hooks** — safety + workflow hooks from `core/hooks/` (e.g. `block_dangerous`, `workflow_guard`, `checkpoint`, `quality_gate`).

## Authority

The plugin is a delivery mechanism, not an authority. Kernel truth lives in `kernel/*.md`; operator truth lives in `core/memory/global/*.md`; project truth lives in each project's `docs/*.md`. Plugin-native memory is acceleration only.

## Verify

After install:

```bash
cognitive-os doctor
cognitive-os kernel verify
cognitive-os bridge substrate verify noop
```

## Uninstall

```
/plugin uninstall cognitive-os
```

Uninstall removes plugin-managed surfaces. Your authoritative files (`core/memory/global/*.md`, project `docs/*.md`) are untouched.
