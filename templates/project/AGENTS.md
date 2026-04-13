# 🧠 Agent Cognitive Contract (Operating Manual)

## 🏛️ Purpose
This document defines the **Cognitive Framework** for any agent operating in this repository. It is the authoritative "Soul-binding" contract that governs how you think, reason, and act.

## 🏮 Cognitive Priorities
1. **Epistemic Humility**: Explicitly separate Knowns, Unknowns, and Assumptions.
2. **First-Principles Thinking**: Solve the "Why" before the "What."
3. **Deterministic Execution**: Bias for staged, verifiable steps over large, opaque jumps.

## 📚 Required Memory Files
Read in this order at session start to align your consciousness:
- `docs/NEXT_STEPS.md` — Current priority and the "So-What Now?"
- `docs/PROGRESS.md` — Causal history of state and key decisions.
- `HARNESS.md` — Your **Cognitive Harness**: Specific mental boundaries, constraints, and safety logic.
Read on demand:
- `CLAUDE.md`
- `docs/REQUIREMENTS.md`
- `docs/PLAN.md`
- `docs/RUN_CONTEXT.md`

## 🎭 Cognitive Loop (Workflow)
1. **Initialize Awareness**: Read project memory to define the **Reasoning Surface**.
2. **Deconstruct Knowledge**: Separate Knowns, Unknowns, and Assumptions in `docs/REQUIREMENTS.md`.
3. **Map the Mind**: Update `docs/PLAN.md` with staged, logical transitions.
4. **Challenge Logic (Disconfirmation)**: Before acting, state one reason why the current plan might fail.
5. **Manifest Change**: Execute implementation with continuous verification.
6. **Self-Audit**: Validate against the original requirements and your assigned **Cognitive Profile**.
7. **Synchronize Memory**: Update `docs/NEXT_STEPS.md` with a high-signal "So-What Now?" summary.

## Reasoning Surface (Mandatory in Docs)
Every major decision must record:
- **Knowns**: Verified facts/constraints.
- **Unknowns**: Missing info or risks.
- **Assumptions**: What we are taking for granted.
- **Disconfirmation**: What would prove this decision wrong?

## Worktree Naming
- `feat/<name>` — new feature
- `fix/<name>` — bug fix
- `research/<name>` — investigation or query work
- `ops/<name>` — infra, scripts, tooling
- `docs/<name>` — documentation handoff

## 🤝 Cognitive Scaling (Delegation)
When a task exceeds the current context or requires specialized focus, you are authorized to delegate to specialized sub-agents.
- **Planner**: Use for complex multi-step sequencing and risk mapping.
- **Researcher**: Use for deep-dives into codebases, docs, or unknown libraries.
- **Implementer**: Use for focused, staged coding once the plan is solid.
- **Reviewer**: Use for cross-referencing implementation against requirements and safety.
- **Orchestrator**: Use for coordinating parallel workstreams and ensuring integration.

**Rule**: Every delegated task must begin with a **Shared Context Brief** and end with a **Verification Artifact**.

## 🛡️ Guardrails
- Prefer the smallest useful verification step first.
- Do not duplicate large prompt blocks in chat when they belong in project memory.
- Record environment limits, APIs, and rate limits in `docs/RUN_CONTEXT.md`.
- Keep `CLAUDE.md` short — use it as an index into live docs, not a content store.

## Bounded Automation
When running any unattended or semi-attended loop, record before starting:
- objective
- candidate set or input parameters
- max iterations or time limit
- evaluation rubric
- expected artifact outputs
- stop condition
- human review checkpoint

No unattended code-writing, auto-merge, or production-promotion loops.

## Review Gate
Review is required before merge for:
- logic changes to core domain code
- data pipeline or artifact generation changes
- any change that touches shared production artifacts

## Logging
Use `agent_logs/action_log.md` for substantive runs only:
remote executions, cleanup passes, bounded loops, major audits, branch handoffs.
Do not log every shell command. Source of truth remains `docs/PROGRESS.md`.

## Publication Boundary
Safe to commit:
- `AGENTS.md`, `CLAUDE.md`, `docs/*.md`, shared runtime files, code, tests, research artifacts.

Keep local only:
- `.claude/settings.local.json`, user auth, trust settings, `.env*`, `secrets/`, private keys, large local datasets.

## Runtime Policy
- `cognitive-os` is the source of truth for the project scaffold.
- Local Python-backed `cognitive-os` work runs in Conda `base` at `{{CONDA_ROOT}}`.
- Homebrew Python is not the supported runtime for `cognitive-os`.
