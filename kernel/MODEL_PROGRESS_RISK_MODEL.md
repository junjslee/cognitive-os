# Model-Progress Risk Model

**Operational summary** (load first if you have a token budget):

- The kernel's value-proposition implicitly assumes a stable gap between fluent-but-confidently-wrong substrates and the structural discipline that counters them. **That gap may close.** Substrate capability has been improving annually; the time-value of the kernel depends on the gap persisting through v1.x adoption + maturation.
- This document names the threat explicitly, declares the falsifiability conditions that would trigger pivot, and frames the kernel's response posture (workflow-discipline-over-substrate-correction; up-stack movement; graceful obsolescence as an acceptable end-state).
- Without this document, the kernel makes an UNFALSIFIABLE strategic claim ("we'll always be useful"), which is the same Doxa-shape the kernel exists to counter — applied to itself.
- v1.1 first slice (Event 81 / CP-MODEL-PROGRESS-OBSOLESCENCE-01): **threat model + repositioning + falsifiability axes + graceful-obsolescence plan**. Periodic-review cadence infrastructure (Component 6 of the CP) deferred.

---

## The threat

The kernel's central thesis: *"counter Doxa via structural forcing"* — graft what fluent language models cannot do natively (causal-consequence modeling, context-fit synthesis, active guidance, self-maintenance) onto them. The hidden assumption beneath this thesis is that **the gap between substrate capability and required cognitive shape is stable**.

Three reasons the gap may not be stable:

1. **Substrate progress.** Frontier model reasoning capability has roughly doubled annually on representative benchmarks for the last 3 years. If the kernel ships v1.x for a 2-3 year adoption window, it is plausible that mid-window substrates produce context-fit answers without scaffolding at parity with kernel-disciplined operator workflow.
2. **Architecture progress.** Multi-step reasoning frameworks, ChainOfThought-as-default, agentic frameworks with built-in episodic memory, and provider-side context-window expansion all reduce the marginal value of an external scaffold for some op-classes.
3. **Operator-side adaptation.** Operators learn to compose fluent substrates more effectively over time. The kernel's value-add per-decision drops as operator skill compounds.

None of these are predictions; they are **named threats** the kernel must hold explicit falsification conditions against.

---

## Why this matters for the kernel's thesis

The kernel claims "counters Doxa via structural forcing." That claim has a hidden monotonicity assumption: *the kernel's structural forcing remains net-positive across substrate evolution*. Without an explicit statement of when that assumption breaks, the kernel itself is making an unfalsifiable claim — which is the Doxa-shape its `kernel/FALSIFIABILITY_CONDITIONS.md` § F2 already names ASPIRATIONAL.

This document operationalizes § F2. It names what would prove the gap has closed + what the kernel does in response.

---

## Response posture

Three load-bearing reframings, each ordered from "easiest to commit to" to "hardest":

### Posture A · Workflow-discipline, not model-correction

The kernel's value is to the **operator**, not to the substrate. Even if a future substrate produces context-fit answers without scaffolding, the operator still benefits from the explicit-thinking gate (Reasoning Surface), the structured pre-execution Knowns/Unknowns/Assumptions/Disconfirmation discipline, and the auditable trajectory.

The Reasoning Surface is **operator-cognitive infrastructure** — a System-2 forcing function for the human, not just a constraint on the substrate. As substrates strengthen, the friction the kernel imposes drops in marginal cost (the substrate doesn't need scaffolding to perform), but the operator-side discipline value persists (the operator still benefits from being forced to articulate Unknowns + Disconfirmation).

**Implication for this kernel:** lean harder on operator-facing discipline framing in `README.md` and the marketing surface. De-emphasize "we make the LLM correct" framing. Emphasize "we make the operator's reasoning explicit, regardless of substrate capability."

### Posture B · Move up-stack as substrates strengthen

As substrate capability rises, the layers ABOVE the substrate become MORE valuable, not less:

- **Multi-agent orchestration** — capable substrates collaborating need accountability boundaries; the kernel's audit + provenance contract becomes the substrate-agnostic orchestration substrate.
- **Federated trust graphs** — operators delegate to substrates they trust; the kernel becomes the trust-evidence layer (per CP-FEDERATED-COGNITIVE-NETWORK-01 in `~/episteme-private/docs/cp-v1.2-federation.md`).
- **Cross-session continuity** — substrates with long-context still don't carry context-fit operator preferences across sessions; the kernel's profile + memory tier remain load-bearing.
- **Audit + accountability** — substrates may produce correct-shaped outputs without explainability; the kernel's auditable trajectory becomes the "show your work" surface that auditors and operators need regardless of substrate accuracy.

**Implication for this kernel:** v1.2+ federation + governance work isn't optional polish; it's the up-stack pivot. CP-FEDERATED-COGNITIVE-NETWORK-01 + CP-PROJECT-GOVERNANCE-CONTINUITY-01 + multi-agent coordination work are the natural next-level positioning if substrate progress closes the per-decision gap.

### Posture C · Graceful obsolescence as an acceptable end-state

If the gap genuinely closes — substrates produce context-fit answers reliably + operators internalize the discipline + up-stack value-add doesn't materialize — the kernel's honest end-state is **graceful obsolescence**, not denial.

Graceful obsolescence means:

- The kernel ships its final cycle with the auditable history of why-it-existed preserved as documentary record.
- The principles enshrined in `kernel/CONSTITUTION.md` are released as canonical operator-discipline guidance, even when no software enforces them.
- The accumulated protocols (Pillar 3 framework streams) are exported as a structured corpus for future cognitive-tooling research.

**Graceful obsolescence is preferable to dead-software-that-still-exists.** A kernel that lingers past its load-bearing window becomes process overhead with no countervailing value — exactly the cascade-theater failure mode (`kernel/FAILURE_MODES.md` mode 11) at the project-lifecycle scale.

This is not a prediction of obsolescence. It is a **declared path** so the kernel cannot rationalize indefinite extension when the evidence stops supporting it.

---

## Falsifiability axes — what would trigger pivot

Per `kernel/FALSIFIABILITY_CONDITIONS.md` § F2 ASPIRATIONAL claim, named falsification conditions for the kernel's value persistence:

### Axis 1 · Differential-demo gap closure

**Falsification condition.** A future model release shows no measurable quality gap between kernel-OFF and kernel-ON conditions on a representative benchmark drawn from operator's actual usage. Specifically: `demos/03_differential/` re-run with the new substrate produces equivalent reasoning surfaces on identical prompts.

**Measurement.** Re-run the differential demo on each major frontier-model release (Claude N+1, GPT-N+1, etc.). Compare reasoning surface fields (Knowns, Unknowns, Assumptions, Disconfirmation) for substantive equivalence — not character-equivalence but goal-equivalence.

**Action.** If gap closes → Posture A (workflow-discipline) becomes load-bearing primary positioning; Posture B (up-stack) is the growth path.

### Axis 2 · Operator-decision-quality parity

**Falsification condition.** A retrospective post-incident review across N≥10 incidents shows operator decision quality is statistically indistinguishable when the kernel was active vs when it was bypassed.

**Measurement.** Designed retrospective study; comparator: matched-context episodes pre- and post-kernel-installation OR with-and-without-kernel-active. Requires CP-EPISODIC-OUTCOME-01 (Theme 1) infrastructure.

**Action.** If parity → reframe value-prop from "improves decision quality" to "improves decision auditability + retrospective debugability." Maintain Posture A; deprioritize per-decision quality claims.

### Axis 3 · Operator-cognitive-skill drift

**Falsification condition.** Operators with extended kernel usage show MORE confidence + LESS calibration on out-of-distribution problems than baseline (cognitive-deskilling — the kernel's `kernel/FAILURE_MODES.md` mapping to Cognitive Deskilling primitive). The kernel becomes a crutch.

**Measurement.** Calibration assessments at 3-month, 6-month, 12-month checkpoints comparing operator without-kernel performance pre- and post-adoption.

**Action.** If deskilling detected → tighten the kernel's "operator must surface Unknowns" discipline; restrict auto-fill behavior; increase friction on operator-easy paths to preserve System-2 muscle.

### Axis 4 · Up-stack value confirmation

**Falsification condition.** As substrate capability rises, the kernel's auditable trajectory + provenance contract is NOT adopted as load-bearing infrastructure for multi-agent / federated / orchestration work. The up-stack pivot fails to find purchase.

**Measurement.** Adoption signal in adjacent ecosystems; external resonance signals (`~/episteme-private/docs/EXTERNAL_RESONANCE.md`); citations / forks / institutional integrations.

**Action.** If up-stack fails → Posture C (graceful obsolescence) becomes the path. Begin documenting the wind-down as the v1.x → v2.x → end-state arc.

---

## Graceful obsolescence plan

If Axes 1-4 collectively indicate the kernel's per-decision and up-stack value have both eroded:

1. **Final-cycle declaration.** Mark the next major version (e.g., v2.0 or v3.0) as the final feature cycle. Communicate publicly via README + announcement.
2. **Documentary preservation.** `kernel/CONSTITUTION.md`, `kernel/FAILURE_MODES.md`, `kernel/REFERENCES.md`, `kernel/FALSIFIABILITY_CONDITIONS.md`, `kernel/MEMORY_ARCHITECTURE.md` are released as standalone operator-discipline guidance, no software dependency.
3. **Protocol-corpus export.** All accumulated Pillar 3 framework protocols (synthesized across the kernel's lifetime) are exported as a structured research corpus — JSONL + provenance trail + decay/retention metadata.
4. **Final-state license.** The final-version code remains under AGPL-3.0-or-later in perpetuity; no relicensing.
5. **Successor-friendly handoff.** If a successor project / fork wants to carry forward the principles under different infrastructure, the kernel's evolution-contract framework supports the handoff (per `kernel/CONTINUITY_PLAN.md` succession provisions).

Graceful obsolescence is **not** abandonment. It is honest-end-of-load-bearing-life with the discipline preserved as cultural artifact.

---

## What this is NOT

- **Not a prediction.** The threats above are named, not forecasted. No probability estimate is made about which axis fires when.
- **Not a defense plan.** The kernel cannot "defend" against substrate progress. The thesis is structural — if the gap closes, the kernel pivots or sunsets.
- **Not a marketing document.** This is operator-facing strategic infrastructure. The README does not need to load this complexity.
- **Not a v1.0 RC scope item.** This is v1.1+ strategic positioning. v1.0 RC's "is this kernel useful right now" thesis is unchanged by the existence of this risk model.

---

## Periodic review cadence (deferred)

Component 6 of CP-MODEL-PROGRESS-OBSOLESCENCE-01: **quarterly relevance check** during v1.x cycle. Each review walks the four falsifiability axes, looks for trigger evidence, decides whether posture shift is warranted. Cadence infrastructure (cron / scheduled hook / manual checklist) is deferred to a follow-up Event.

The first review is scheduled for v1.1 cycle close (~3 months post-v1.0 GA, late 2026 / early 2027). Format: walk this doc; for each axis, named evidence; named decision (continue / pivot to A / pivot to B / start C).

---

## Cross-references

- [`kernel/CONSTITUTION.md`](./CONSTITUTION.md) — root claim ("the danger is confident wrongness") that this document strategically guards.
- [`kernel/FALSIFIABILITY_CONDITIONS.md`](./FALSIFIABILITY_CONDITIONS.md) § F2 — the ASPIRATIONAL kernel-value-persistence claim that this document operationalizes.
- [`kernel/KERNEL_LIMITS.md`](./KERNEL_LIMITS.md) — declared limits doc; this file extends the limits framework to TIME-bound limits.
- [`kernel/REFERENCES.md`](./REFERENCES.md) § Tetlock — base-rate discipline informs the threat-axis honesty here.
- `~/episteme-private/docs/cp-v1.1-architectural.md` § CP-MODEL-PROGRESS-OBSOLESCENCE-01 — spec source.
- `~/episteme-private/docs/cp-v1.2-federation.md` § CP-FEDERATED-COGNITIVE-NETWORK-01 — the up-stack work that operationalizes Posture B.
- `~/episteme-private/docs/EXTERNAL_RESONANCE.md` — Path B framing supports Posture B repositioning.

---

## Maintenance

This file is correct when:

- Each falsifiability axis has named measurement methodology + named action-on-trigger.
- The graceful-obsolescence plan is concrete, not aspirational.
- The quarterly review cadence is honored (Component 6).
- The action-on-trigger commitments are followed when an axis fires.

Version: v1.0 (Event 81, 2026-04-29). First slice: threat model + reposturing + falsifiability axes + graceful-obsolescence plan. Component 6 (periodic-review cadence infrastructure) deferred.
