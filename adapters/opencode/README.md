# opencode Adapter

[opencode](https://opencode.ai) (anomalyco/opencode, ~143k stars) is an open-source,
provider-agnostic AI coding agent. It uses `.opencode/agents/` for per-project agent
definitions and `~/.config/opencode/agents/` for global ones.

`cognitive-os sync` installs a governance agent at:

```
~/.config/opencode/agents/cognitive-os-governance.md
```

## What it does

The governance agent is a global subagent that opencode can invoke in any session.
It carries your cognitive profile, workflow policy, and the full operator identity
contract -- the same content synced to Claude Code and Hermes.

opencode's `{file:path}` syntax is used to reference your OPERATOR.md if Hermes is
installed, keeping the content in sync without duplication. If Hermes is not installed,
the governance agent inlines the profile sections directly.

## How opencode loads agents

- **Global agents** live in `~/.config/opencode/agents/` and are available across all projects.
- **Per-project agents** live in `.opencode/agents/` in the project root.
- Agents are markdown files with YAML frontmatter (description, mode, model, tools).
- Subagents can be invoked via `@agent-name` in any opencode session.

To invoke the cognitive-os governance agent explicitly:

```
@cognitive-os-governance what is my current operator profile?
```

## Per-project bootstrap

When you run `cognitive-os bootstrap` or `cognitive-os new-project`, the project
scaffold includes an `AGENTS.md` at the repo root. opencode respects AGENTS.md as
its primary project-level behavioral contract -- the same file Codex uses.

No per-project adapter file is required beyond AGENTS.md.

## oh-my-openagent (omo) compatibility

oh-my-openagent (code-yeongyu/oh-my-openagent, ~51k stars) is a community enhancement
layer on top of opencode. If omo is installed at `~/.omo/`, `cognitive-os sync` also
copies agents and skills there. The governance contract is the same; only the delivery
directory differs.
