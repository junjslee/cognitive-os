# The Epistemic Posture — narrative spine

What this kernel installs is an *epistemic posture* — a structured way of holding
oneself before, during, and after a decision. Other documents describe its parts
([`POSTURE.md`](./POSTURE.md), [`kernel/CONSTITUTION.md`](../kernel/CONSTITUTION.md),
[`kernel/REASONING_SURFACE.md`](../kernel/REASONING_SURFACE.md)). This one names
the spine they hang from — **the structural axis every diagram, demo, and
artifact in the repository renders onto.**

---

## 1 · The triad as structural spine

Three ancient Greek concepts describe the strata the posture operates on:

- **Doxa** (δόξα) — common opinion, appearance, unexamined belief. What fluent
  output produces by default. The nine named failure modes in
  [`kernel/FAILURE_MODES.md`](../kernel/FAILURE_MODES.md) are a taxonomy of
  *doxa mistaking itself for episteme*.
- **Episteme** (ἐπιστήμη) — justified knowledge. In Plato, *doxa + logos
  (account) + aletheia (unconcealment)*. Structurally: what the kernel demands
  before irreversible action. The repo's namesake.
- **Praxis** (πρᾶξις) — informed action; doing-with-understanding. Effects
  that land with their authorizing discipline intact. The four canonical
  artifacts (reasoning-surface / decision-trace / verification / handoff) are
  its visible form.

This is not decoration. The three strata map directly to the three layers of
[`docs/assets/architecture_v2.svg`](./assets/architecture_v2.svg): doxa is the
agent runtime's default output; episteme is the control plane that interposes;
praxis is what lands as effect. The Greek gives the vocabulary; the layers
give the mechanism.

## 2 · The grain (결 · gyeol) — working the texture of the discipline

The triad stratifies, but the posture also *moves*. Korean aesthetic-philosophy
names this motion **결** (*gyeol*) — grain, as in the grain of wood or stone:
the latent pattern-structure inside matter that, when followed, yields coherent
form. When cut against, it fractures.

The Reasoning Surface's field ordering — Knowns → Unknowns → Assumptions →
Disconfirmation — is the 결 of epistemic discipline: *settled → open →
provisional → falsification-condition*. Three postures relative to the grain:

- **Cutting across the grain** — `"disconfirmation": "None"`. The surface
  fractures; the validator catches it. The shallowest failure.
- **Running the grain's surface without penetration** —
  `"disconfirmation": "the system could have bugs we haven't found"`.
  48 characters; passes the hot path; semantically vacuous. *Fluent-vacuous* —
  doxa wearing the shape of episteme.
- **Working with the grain** — `"disconfirmation": "if query-log analysis
  shows >60% of failed searches are typo-driven, semantic search is wrong —
  fuzzy match is the fix"`. Concrete; falsifiable; pre-committed pivot.

Only the third is the posture. The triad names *which stratum* we are in;
결 names *whether we are working with the discipline or faking it*.

## 3 · The doxa stratum — what enters

Before discipline, an LLM's output is doxa: confident, fluent, pattern-matched
against its training distribution. This is what the posture interposes on. The
failure surface is cataloged in [`kernel/FAILURE_MODES.md`](../kernel/FAILURE_MODES.md)
as nine named modes — each a specific way doxa mistakes itself for episteme:

- **1–6** (Kahneman-derived): WYSIATI, question substitution, anchoring,
  narrative fallacy, planning fallacy, overconfidence.
- **7–9** (governance-derived): constraint removal without understanding
  (Fence-Check), measure-as-target drift (Goodhart), controller-variety
  mismatch (Ashby).

Each named mode is the specific doxa-pattern one kernel artifact counters.
WYSIATI is countered by the Unknowns field of the Reasoning Surface. Question
substitution is countered by the Core Question requirement. Measure-as-target
is countered by the profile-audit loop (phase 12, shipped at v0.11.0 — see
§4, §7). v1.0 RC adds two more governance-layer doxa-patterns — *framework-
as-Doxa* (synthesized protocols collapsing back into averaged wisdom) and
*cascade-theater* (Blueprint D's `blast_radius_map[]` padded with
`not-applicable` entries) — with countermeasures named in
[`kernel/KERNEL_LIMITS.md`](../kernel/KERNEL_LIMITS.md) and
[`docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md`](./DESIGN_V1_0_SEMANTIC_GOVERNANCE.md).

A kernel that lists *what it provides* without listing *what it opposes*
cannot be evaluated. The doxa stratum is the ledger of what is opposed.

## 4 · The episteme stratum — what the kernel demands

Episteme here is not aspiration; it is a set of machine-enforceable discipline
checks applied between doxa and praxis. Four roles.

**Texture of thought** — *what questions get asked; what unknowns get named*:
- [`Reasoning Surface`](../kernel/REASONING_SURFACE.md) — Core Question +
  Knowns / Unknowns / Assumptions / Disconfirmation, validated structurally
  before high-impact actions.
- `core/hooks/_derived_knobs.py` (phase 9) — the operator profile's
  cognitive-style axes modulate `disconfirmation_specificity_min` and sibling
  thresholds. The profile is not documentation; it is control signal.

**Texture of action** — *which options are admitted; which are pre-rejected*:
- `core/hooks/reasoning_surface_guard.py` — strict-mode default; exit 2 on
  missing or invalid surface; normalized command matching across
  `subprocess.run` / `os.system` / `sh -c` shapes.
- `core/hooks/state_tracker.py` — persists sha256 + ts of agent-written files
  to `~/.episteme/state/session_context.json`; deep-scans on execute. Closes
  write-then-execute bypass *across* tool calls.

**Rationale** — *the because-chain from signal to decision*:
- Decision trace (canonical form in
  [`demos/01_attribution-audit/decision-trace.md`](../demos/01_attribution-audit/decision-trace.md))
  — options considered, because-chain, rejection conditions, load-bearing
  concepts named.
- `core/hooks/calibration_telemetry.py` — pre-call prediction paired with
  post-call exit code by `correlation_id`. Local-only JSONL.

**Memory discipline** — *what the kernel remembers of its own past reasoning*
(see [`kernel/MEMORY_ARCHITECTURE.md`](../kernel/MEMORY_ARCHITECTURE.md)):
- `core/hooks/episodic_writer.py` (phase 10) — high-impact Bash pattern-matches
  appended to `~/.episteme/memory/episodic/YYYY-MM-DD.jsonl`.
- `src/episteme/_memory_promote.py` (phase 11) — clusters episodic records by
  `(domain_marker, primary_pattern)`, emits deterministic proposals to the
  reflective tier.
- **Profile-audit loop (phase 12, shipped at v0.11.0).** Compares claimed
  profile axes against episodic praxis and semantic proposals. Flags drift
  as re-elicitation at SessionStart. Its slot in the control-plane diagram
  is solid, not dashed — the circuit is closed at the v0.11.0 level.

Each component is the operational form of one principle from
[`kernel/CONSTITUTION.md`](../kernel/CONSTITUTION.md), applied to one failure
mode from [`kernel/FAILURE_MODES.md`](../kernel/FAILURE_MODES.md). No
component exists for its own sake.

## 5 · The praxis stratum — what lands

Praxis is action with its authorizing understanding intact. The stateful
interceptor exists because *fake praxis* — hidden `git push` dressed as
file-write — is the specific failure the kernel guards against at this
boundary.

The four canonical artifacts are the visible form of real praxis:

- **`reasoning-surface.json`** — the posture entering the action.
- **`decision-trace.md`** — options considered, rejected-with-conditions,
  because-chain.
- **`verification.md`** — each assumption graded; each disconfirmation
  checked; residual unknowns kept honest.
- **`handoff.md`** — what shipped; what was pre-rejected and why; what the
  next session must not re-litigate.

An agent operating inside the posture emits these four. An agent operating
outside it does not. This is the testable property. A diff of `.episteme/`
after a work session is a literal render of the posture's output.

## 6 · Kernel limit, stated honestly

The kernel enforces **structural discipline in the hot path**: the field
exists, has content, meets length, normalizes past the pattern set. It does
*not* catch fluent-vacuous-but-structurally-valid surfaces in the hot path.
A sufficiently-trained LLM can emit a 48-character disconfirmation that says
nothing and passes every validator.

That gap is closed **over time**, not at write:

- The episodic tier logs every high-impact action paired with its surface.
- The semantic promoter clusters by outcome; a disconfirmation pattern that
  never fires across N uses is detectable as drift.
- The profile-audit loop (phase 12, shipped at v0.11.0) completes the
  v0.11 circuit — claimed specificity vs. actual specificity, per axis.

*Structural discipline in the hot path; semantic quality over time* — true
at v0.11.0. **v1.0 RC tightens "structural discipline in the hot path"
further** by making the surface scenario-polymorphic: the four-field shape
becomes a fallback, and four named blueprints (Axiomatic Judgment / Fence
Reconstruction / Consequence Chain / Architectural Cascade & Escalation)
shape the required fields in the hot path when their scenarios fire. The
semantic-quality-over-time axis gains a peer — context-fit protocol
synthesis + active operator guidance + continuous architectural self-
maintenance, all hash-chained, all surveyed in §7.5. See
[`kernel/KERNEL_LIMITS.md`](../kernel/KERNEL_LIMITS.md) for the full
declared set of limits.

## 7 · What v0.11.0 closed

The profile-audit loop shipped at v0.11.0 — the kernel's act of
**episteme auditing praxis to detect when a claimed axis has drifted into
doxa**. The operator profile's axes are beliefs-about-self; the episodic
tier is the record of actual action; drift between them means the belief is
no longer warranted by evidence. The loop surfaces drift as a re-elicitation
prompt at SessionStart — not a silent trust in prior claims. The v0.11
circuit is closed.

## 7.5 · What v1.0 RC opens — protocol synthesis, active guidance, continuous self-maintenance

The v1.0 RC cycle (spec: [`docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md`](./DESIGN_V1_0_SEMANTIC_GOVERNANCE.md),
status *approved (reframed, third pass)* 2026-04-21) grafts three jobs the
auto-regressive substrate cannot perform natively onto the kernel, beyond
the per-action causal-consequence decomposition v0.11.0 already enforces.
Each job anchored to a named structural pillar:

- **Pillar 1 · Cognitive Blueprints** — scenario-polymorphic surface
  schemas. Four named blueprints (A Axiomatic Judgment, B Fence
  Reconstruction, C Consequence Chain, D Architectural Cascade &
  Escalation) plus a generic maximum-rigor fallback for high-impact ops
  that match no named scenario. The four-field surface is the fallback
  only; blueprints shape the required fields when their scenarios fire.
- **Pillar 2 · Append-Only Hash Chain** — tamper-evident episodic and
  framework records. Closes a previously unaddressed doxa class: an agent
  with filesystem access cannot silently rewrite its own predictions to
  pretend it got right what it actually got wrong.
- **Pillar 3 · Framework Synthesis & Active Guidance** — context-indexed
  protocols extracted from conflicting sources (Axiomatic Judgment),
  constraint removals (Fence Reconstruction), and architectural cascades
  (Blueprint D), written to a hash-chained framework, and surfaced
  proactively as operator guidance at future matching decisions. The
  framework is the living thinking framework the operator's *ultimate
  why* asked for; guidance is advisory, never blocking.

**Blueprint D** earns its own line: it fires whenever the agent discovers a
flaw, vulnerability, stale artifact, config gap, or core-logic drift
mid-work. It forces three cognitive moves — patch-vs-refactor evaluation,
symmetric cascade synchronization across the full blast radius (CLI /
config / schemas / hooks / visualizations / docs / tests / generated
artifacts / external surfaces), and continuous digging & logging of
adjacent discoveries into the framework. Without it, the agent defaults to
the cheapest local patch and the codebase decays under its own edits.

The posture sharpens, not widens. The triad is unchanged: doxa enters,
episteme interposes, praxis lands. The grain is unchanged. The
control-plane diagram's phase-12 dashed stroke solidifies (v0.11.0); four
v1.0 RC additions get their own dashed strokes (blueprint selector /
cascade detector / hash chain / framework query) until CP1-CP10 land.

---

## Read next

- [`docs/assets/system-overview.svg`](./assets/system-overview.svg) — Figure 1:
  structural stratification of the posture (product shape).
- [`docs/assets/architecture_v2.svg`](./assets/architecture_v2.svg) — Figure 2:
  control-plane interposition at the tool-call boundary (runtime shape).
- [`demos/03_differential/`](../demos/03_differential/) — doxa vs. episteme on
  the same prompt, with the four canonical artifacts committed.
- [`scripts/demo_posture.sh`](../scripts/demo_posture.sh) — the 75-second
  cinematic differential (the posture in motion).
