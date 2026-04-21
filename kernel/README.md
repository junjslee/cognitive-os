# The Cognitive Kernel

The canonical specification of episteme.

Pure markdown. No code. No tooling. Nothing vendor-specific.

The kernel defines **how an agent should think** — before any platform,
framework, or adapter gets involved. Everything else in this repository
(the CLI, the hooks, the adapters, the skills) exists to deliver this
kernel into a specific runtime.

If the kernel is sound, the adapters are small. If an adapter starts
growing, the fix is in the kernel's portability, not in more adapter code.

## The ultimate why — a living thinking framework, not a stateless guardrail

An operator drowning in conflicting sources (Stack Overflow, vendor docs,
teammate folklore, LLM-synthesized "best practice") cannot reliably
distinguish which source fits THIS context — and a stock auto-regressive
LLM will not do it for them. Each conflicting pair of cases hides a
context-dependent protocol ("in context X, do Y because Z"); extracting
the protocol requires modeling *why* the sources conflict, not averaging
them. The kernel exists to force the extraction — and, over time, to
build a **living thinking framework** that synthesizes accumulated
context-fit protocols, surfaces them proactively as operator guidance at
the point of future decisions, and maintains its own architectural
coherence as the agent edits the system. Four jobs: per-action causal
decomposition, per-case protocol synthesis, active guidance at future
decisions, continuous self-maintenance. Full specification (v1.0 RC):
[`../docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md`](../docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md).

## BYOS — bring your own skill

episteme is a **cognitive and execution governance kernel**. It is not a
skill provider, tool provider, or agent framework. The kernel does not
give agents capabilities; it intercepts state mutation at the point of
action and enforces the Reasoning Surface regardless of which external
tool, MCP server, or agent framework generated the command. A
`kubectl apply` from Claude Code, a `terraform plan` from a Cursor agent,
a `gh pr merge` from a home-grown MCP server — the kernel does not care
about provenance. It intercepts the mutation and enforces the
blueprint-shaped cognitive contract before the mutation lands. The
ecosystem provides the skills; the kernel provides the episteme.

---

## Files

- **[CONSTITUTION.md](./CONSTITUTION.md)** — the north-star document.
  Root claim, failure modes being addressed, the four principles, and what
  follows from them.

- **[REASONING_SURFACE.md](./REASONING_SURFACE.md)** — the operational
  protocol that operationalizes Principle I (Explicit > Implicit). The
  minimum viable explicitness required before any consequential action.

- **[FAILURE_MODES.md](./FAILURE_MODES.md)** — the named failure modes the
  kernel is built against, mapped to the specific artifact that counters
  each one. Nine at v0.11.0 (six Kahneman-derived + three governance-layer:
  Fence-Check / Goodhart / Ashby); two more land with v1.0 RC
  (framework-as-Doxa, cascade-theater).

- **[OPERATOR_PROFILE_SCHEMA.md](./OPERATOR_PROFILE_SCHEMA.md)** — the
  schema for encoding an operator's cognitive preferences so they travel
  with the agent across tools and sessions. Two scorecard layers (process
  + cognitive-style), per-axis metadata, expertise map, and the derived
  behavior knobs adapters compute from the axes.

- **[MEMORY_ARCHITECTURE.md](./MEMORY_ARCHITECTURE.md)** — the memory
  contract. Five tiers (working / episodic / semantic / procedural /
  reflective), retrieval by situation-match, gated promotion from
  episodic through semantic to profile-drift proposal, and declared
  forgetting per tier. The layer that turns a session-bound agent into an
  operator-persistent one.

- **[REFERENCES.md](./REFERENCES.md)** — external sources that informed
  the kernel's contents. The kernel body does not import jargon from these
  sources; concepts are described in the kernel's own vocabulary. This
  file is the attribution trail for readers who want to go deeper.

- **[HOOKS_MAP.md](./HOOKS_MAP.md)** — mapping from kernel invariants to
  runtime hooks that enforce them. Also documents the Reasoning Surface
  state file and the integrity manifest commands.

- **MANIFEST.sha256** — sha256 digest of every managed kernel file.
  `episteme kernel verify` detects drift; `episteme kernel update`
  regenerates after intentional edits. `episteme doctor` surfaces
  drift as a non-blocking warning.

---

## How the kernel is delivered

An adapter is a thin shim that injects kernel files into a runtime's
native context-loading mechanism:

- Claude Code: concatenated into `CLAUDE.md` or referenced from global
  memory.
- Hermes: mounted as `OPERATOR.md`.
- Any future runtime: same files, different destination.

The kernel does not care which runtime loads it. The runtime does not
know what the kernel contains. That decoupling is the point.

---

## What lives here vs. elsewhere

- **kernel/** — portable spec. Markdown only. Vendor-neutral.
- **adapters/** — per-runtime delivery. Should be tiny (<100 LOC each).
- **core/memory/global/** — the *author's* personal instance of the
  operator profile, using the schema defined here.
- **docs/** — project-level documentation about the system itself
  (architecture notes, contract docs, PRDs). Not kernel.
