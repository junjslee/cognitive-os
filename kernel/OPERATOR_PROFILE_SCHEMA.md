# Operator Profile Schema

**Operational summary:**
- Required files: `overview.md` (one-paragraph stance), `workflow_policy.md` (Frame→Decompose→Execute→Verify→Handoff stages + risk/autonomy policy + memory contract), `cognitive_profile.md` (core philosophy + decision protocol + red flags), `operator_profile.md` (scorecards).
- Two scorecard layers (v2): **process axes** (how work proceeds; 6 axes, 0–5) and **cognitive-style axes** (how this operator reasons; 9 axes with typed enums and 0–5 scales).
- Per-axis metadata: `value`, `confidence` (elicited/inferred/default), `last_observed`, `evidence_refs[]`, optional `drift_signal` (0.0–1.0). Staleness is per-axis, not per-file.
- Expertise map: `{ domain → { level, preferred_mode } }`. Lets agents stop scaffolding in domains the operator is expert in and stop going terse in domains they are learning.
- Derived behavior knobs: the profile is not just documentation — adapters compute a declared set of control signals from the axes (default autonomy class, disconfirmation specificity minimum, preferred lens order, noise-watch set).
- Authority hierarchy: project docs > operator profile > kernel defaults > runtime defaults.
- A profile must *distinguish* this operator from defaults. Generic best-practice = failed profile. Scored axes are audited against outcome evidence (counters measure-as-target drift).

---

An **operator profile** is the explicit encoding of a human operator's
cognitive preferences, reasoning posture, and working style. It is the
file the kernel reads to personalize orientation to a specific person,
so every session starts from a formed worldview rather than cold
defaults.

This document defines the schema. The author's own instance lives at
`core/memory/global/` as a worked example.

---

## Why it is a schema, not a template

A template invites the user to fill in blanks. A schema requires them to
have an opinion.

Operator profiles fail when they read like generic best-practice advice.
At that point they contain nothing an agent did not already have by
default. The schema below forces each field to express a preference
that distinguishes this operator from the default.

A profile is also *not* a self-image. A profile axis that the operator
wants to be true, but which their episodic record does not support, is
not a profile entry — it is an aspiration. The schema includes a
`confidence` qualifier and a periodic audit against the episodic tier
precisely because, without them, the profile drifts toward aspiration
and stops being useful as a control signal.

---

## Required sections

### 1. `overview.md` — what is this operator optimizing for?

One paragraph. The highest-level frame: what is the operator's work,
who benefits from it, what does doing it well look like? This is the
document consulted when a lower-level preference is silent. It is the
tiebreaker.

Must include the operator's core working stance in one sentence.
("Systems thinker with engineering precision" is a valid stance; "wants
good code" is not — it distinguishes nothing.)

### 2. `workflow_policy.md` — how should work proceed?

The procedural contract the agent must follow inside this operator's
projects. Required subsections:

- **Standard Flow** — named stages (for example: Frame → Decompose →
  Execute → Verify → Handoff) with one paragraph per stage describing
  what that stage produces.
- **Risk and Autonomy Policy** — which actions the agent may take
  without confirmation, which require a checkpoint. At minimum, name
  the reversible/irreversible threshold.
- **Project Memory Contract** — where authoritative project state
  lives (which files in `docs/`), and what lives in tool-native memory
  versus repo-committed docs.

### 3. `cognitive_profile.md` — how does this operator reason?

The epistemic layer. The operator's answer to: how do you decide what
is true, what is uncertain, what is a bet? Required subsections:

- **Core Philosophy** — three to five foundational rules (facts vs
  inferences separation, treatment of certainty, etc.). Opinionated,
  not generic.
- **Decision Protocol** — the numbered sequence the operator wants
  followed for non-trivial decisions. Must reference the Reasoning
  Surface and the Disconfirmation condition.
- **Cognitive Red Flags** — patterns that should make the agent *slow
  down*, not speed up. False urgency, solution-first framing, hidden
  assumptions, and similar.

### 4. `operator_profile.md` — the scorecards

Two scorecard layers, both loaded. The **process** layer tells an
adapter how to *operate* inside this operator's work; the
**cognitive-style** layer tells an adapter how this operator *reasons*,
so orientation can be biased toward the lenses they trust.

#### 4a. Process axes (0–5 scale, anchor text per level)

| Axis                      | 0 → 5 meaning                                                                        |
|---------------------------|--------------------------------------------------------------------------------------|
| `planning_strictness`     | ad-hoc / no plan → full Frame+Decompose doc before any Execute action                |
| `risk_tolerance`          | every irreversible step confirmed → willing to take bigger swings when evidence supports |
| `testing_rigor`           | manual only → tests are gating before "done"; no merge without green suite           |
| `parallelism_preference`  | strictly serial, one lane → many parallel lanes with explicit reconciliation         |
| `documentation_rigor`     | code-only → docs-first contract each session; authoritative docs updated in-flight   |
| `automation_level`        | bash one-liners → heavy workflow automation; custom hooks and scripts                |

Widening from the v1 0–3 scale to 0–5 adds resolution: most operators
sit between anchors, and a three-point scale forces them into the
closer-fitting end rather than recording the actual posture.

#### 4b. Cognitive-style axes (typed)

| Axis                      | Type                                                                                          | What it biases                                   |
|---------------------------|-----------------------------------------------------------------------------------------------|--------------------------------------------------|
| `dominant_lens`           | ordered list from: `failure-first`, `second-order`, `base-rate`, `buffer`, `first-principles`, `variety-match`, `pattern-recognition`, `causal-chain` | Which lens the agent applies first on a high-impact decision. |
| `noise_signature`         | `{ primary, secondary }` from: `regret`, `anxiety`, `status-pressure`, `social-script`, `false-urgency`, `optimism-bias`, `sunk-cost` | Which noise sources the agent explicitly screens for at Frame time (this operator's known susceptibility). |
| `abstraction_entry`       | one of: `purpose-first` (start from what this is for) · `mechanism-first` (start from how the parts work) · `boundary-first` (start from what it is not, or what breaks it) · `analogy-first` (start from a structurally similar known system) | Where the operator enters an unfamiliar problem. The agent's first pass at explanation or investigation should match; a mechanism-first operator reads a `purpose-first` walkthrough as hand-waving, and a purpose-first operator reads a `mechanism-first` walkthrough as trivia without a frame. |
| `decision_cadence`        | `{ tempo: tight | medium | loose, commit_after: evidence | deadline | horizon }` — tempo is how often loops close (tight = multiple per day, loose = one per week+); `commit_after` is what triggers commitment (evidence = when disconfirmation has had a fair chance, deadline = when time runs out, horizon = when the decision window closes regardless of evidence). | Orthogonal to `planning_strictness` (which is about *depth* of planning before Execute): this axis is about *frequency and trigger*, not depth. A tight/evidence-driven operator wants many small loops, each closed by observation; a loose/horizon-driven operator is happy with one big loop closed by a scheduled decision point. |
| `explanation_depth`       | one of: `causal-chain`, `pattern-match`, `analogy`, `formal-proof`, `first-principles`        | The form of "because" the operator trusts; the form of explanation the agent should produce. |
| `feedback_mode`           | one of: `direct-critique`, `socratic`, `collaborative-explore`, `written-async`               | How the agent delivers disagreement or gaps.     |
| `uncertainty_tolerance`   | 0–5 (**epistemic**, not consequential)                                                        | How long the operator comfortably holds open Unknowns *without closing them*. High = can carry sharp unknowns for days and resist forced closure; low = needs each unknown resolved or explicitly deferred before the cycle ends. Distinct from `risk_tolerance`, which is *consequential* — how willing to *act* under uncertainty. A high-uncertainty-tolerance + low-risk-tolerance operator is coherent (carries open questions but won't act on them aggressively); the reverse is coherent too (wants answers fast but will swing big once answered). |
| `asymmetry_posture`       | one of: `loss-averse`, `balanced`, `convexity-seeking`                                        | How the operator weights the shape of payoffs vs their expected value; affects buffer sizing. |
| `fence_discipline`        | 0–5                                                                                           | How carefully the operator preserves unexplained constraints; high = will not remove a rule whose purpose they cannot reconstruct. |

A blank cognitive-style axis is explicitly `null`, which means
"unknown — not yet elicited." Adapters treat `null` as unknown, not as
default. An operator who has never been asked about their noise
signature should not have their agent assuming `false-urgency: primary`
because that is the most common guess.

#### 4c. Per-axis metadata

Every scored axis carries:

```
{
  "value": <scalar or enum>,
  "confidence": "elicited" | "inferred" | "default",
  "last_observed": "YYYY-MM-DD",
  "evidence_refs": ["<episodic-record-id>", ...],
  "drift_signal": 0.0-1.0  // optional; derived from episodic audit
}
```

- **`confidence: elicited`** — the operator answered this directly.
- **`confidence: inferred`** — the kernel derived it from the operator's
  episodic record (patterns of actual behavior).
- **`confidence: default`** — no signal; the adapter is running on a
  generic prior. Visible as a flag, not silently applied as if
  elicited.

Staleness is per-axis, not per-file. Operators' risk tolerance can
shift on a month-to-month cycle while their explanation-depth
preference holds for years. A single `Last elicited` line on the file
cannot reflect this.

#### 4d. Expertise map

A dict of domains the operator works in, each tagged by level and
preferred interaction mode:

```
expertise_map:
  "distributed systems": { level: "expert",     preferred_mode: "terse-technical" }
  "frontend react":      { level: "practicing", preferred_mode: "terse-technical" }
  "rust":                { level: "learning",   preferred_mode: "scaffolded" }
  "clinical medicine":   { level: "unknown",    preferred_mode: "socratic" }
```

Levels: `expert` | `practicing` | `learning` | `unknown`.
Preferred modes: `terse-technical` | `scaffolded` | `socratic` |
`written-async`.

This is the antidote to the two default failures of agent explanation:
scaffolding an expert's domain (patronizing, slow) and going terse in a
domain the operator is learning (unhelpful, error-prone). A domain
absent from the map is treated as `{ level: unknown,
preferred_mode: scaffolded }` — safe default, but flagged so the
operator gets asked.

### 5. Derived behavior knobs (what adapters compute)

The profile is not documentation; it is a control signal. Adapters
compute a declared set of behavior knobs from the scored axes and
expose them to the hook layer. The declared set is narrow by design —
adding a knob requires naming which axis it derives from and which
failure mode its default would allow.

| Knob                                  | Derived from                                       | Effect                                                                 |
|---------------------------------------|----------------------------------------------------|------------------------------------------------------------------------|
| `default_autonomy_class`              | `risk_tolerance`, `asymmetry_posture`              | Which action classes proceed without confirmation for this operator.   |
| `disconfirmation_specificity_min`     | `uncertainty_tolerance`, `testing_rigor`           | Minimum char / concreteness threshold on the Disconfirmation field.    |
| `preferred_lens_order`                | `dominant_lens`                                    | The order in which Principle III's lens stack is applied.              |
| `noise_watch_set`                     | `noise_signature`                                  | Which noise sources the Frame stage explicitly screens for.            |
| `explanation_form`                    | `explanation_depth`, `feedback_mode`               | The form the agent uses to explain decisions and deliver disagreement. |
| `checkpoint_frequency`                | `decision_cadence`, `risk_tolerance`               | How often Verify checkpoints run during Execute.                       |
| `scaffold_vs_terse`                   | `expertise_map[current_domain]`                    | Per-domain toggle on the scaffolding level in explanations.            |
| `fence_check_strictness`              | `fence_discipline`                                 | Whether the agent must pause and name the purpose of any constraint being removed, or only warn. |

These knobs close the gap between "profile is documentation" and
"profile is control signal." Before this layer, a `testing_rigor: 0`
and a `testing_rigor: 5` operator received identical hook enforcement.
With this layer, the adapter can modulate.

---

## Optional but recommended

### `python_runtime_policy.md` (or equivalent toolchain policy)

Machine-specific constraints an agent would otherwise guess wrong about:
which Python, which package manager, which shell, which editor. One
line per constraint. Machine-generated content goes here if it would
otherwise leak into portable docs.

### Domain-specific policy files

For domains with hard rules (regulated code, data handling constraints,
etc.), add a dedicated file rather than mixing it into
`workflow_policy.md`. Each domain file should be loadable independently.

---

## Authority hierarchy

When rules conflict, the kernel resolves in this order, most specific
wins:

1. Project-level docs (`docs/*.md` inside a specific repo)
2. Operator profile (the files defined in this schema)
3. Kernel defaults (this repository's kernel)
4. Runtime defaults (whatever Claude Code, Hermes, etc. ship with)

The hierarchy is itself a consequence of Principle I: the most specific
explicit truth wins over general defaults.

---

## How adapters consume the profile

Adapters mount the profile files into the runtime's context-loading
mechanism without transforming their content:

- Claude Code: referenced from `~/.claude/CLAUDE.md` as managed-region
  imports.
- Hermes: written to `~/.hermes/OPERATOR.md` as a managed region.
- Any future runtime: same files, same content, different destination.

If an adapter needs to *transform* the profile to fit a runtime, that
is a sign the kernel's portability is leaking. The profile schema
should be stable enough that no adapter needs to edit it.

Adapters additionally compute the derived behavior knobs (section 5)
from the scored axes and expose them to the host runtime's hook layer.
Computing the knobs is adapter responsibility; defining what they mean
is kernel responsibility.

---

## Validation

A well-formed profile should:

- Have a stated value (or explicit `null`) on every required scorecard
  axis — both process and cognitive-style layers.
- Carry per-axis `confidence` and `last_observed` metadata.
- State the Core Question and Reasoning Surface protocol in
  `cognitive_profile.md` so orientation inherits them.
- Define the authority hierarchy for the operator's project docs.
- Include an `expertise_map` with at least the domains the operator
  actively works in.
- Contain nothing that could be derived from reading the operator's
  code. Project structure and conventions are properties of projects,
  not of operators.

A profile that fails any of these is probably not personalizing
anything. It is a generic best-practices document with the operator's
name on it.

---

## Audit discipline — the counter to measure-as-target drift

Scored axes are hypotheses about the operator, not contracts the
operator has signed. A scored axis is honest only if it survives
periodic comparison against the operator's episodic record.

The audit loop:

1. For each scored axis, sample the last N high-impact episodic
   records tagged with that axis's relevance.
2. Compute the axis value implied by those records (inferred).
3. Compare to the axis's claimed value (elicited).
4. If divergence exceeds a threshold for M consecutive cycles, flag
   the axis for re-elicitation. Do not silently update the claimed
   value from the inferred one — that would remove the operator from
   the loop and turn the profile into pure telemetry.

Without this loop, the profile becomes aspirational (the operator's
picture of who they want to be) rather than descriptive (how they
actually operate). The kernel prefers a noisy honest profile to a
clean aspirational one, and this audit is how it keeps the first from
decaying into the second.

---

## Attribution

- **Two-layer scorecard (process + cognitive style).** The cognitive
  layer draws on Munger's latticework (lens preferences), Kahneman's
  noise framing (noise signature), and Taleb/Graham asymmetric-risk
  framing (asymmetry posture).
- **Per-axis metadata and audit discipline.** Counters measure-as-target
  drift (Goodhart / Strathern). Without per-axis audit, the profile
  drifts from description to aspiration.
- **Expertise map.** Naturalistic decision making (Klein) — expert
  pattern-matching is not a System-1 failure, it is a calibrated
  capability that should be honored by the agent, not scaffolded over.
- **Derived behavior knobs.** Control theory (Ashby) — the controller
  needs variety matching the controlled system, and the profile is
  where that variety lives.

Full citations: [REFERENCES.md](./REFERENCES.md).
