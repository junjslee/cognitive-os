# Design — v1.0 · Causal-Consequence Scaffolding for the Reasoning Surface

Status: **approved (reframed)** · Drafted 2026-04-21 · Approved 2026-04-21 · Reframed 2026-04-21 · Scope: v1.0 RC upgrade of the Reasoning Surface from syntactic enforcement to causal-consequence scaffolding — grafting a causal world-model interface onto an auto-regressive engine that cannot perform one natively.

**Approval record.** Maintainer approved the eight-layer architecture on 2026-04-21 and, later the same day, approved a philosophical reframe that re-anchors the spec from "semantic governance / anti-vapor defense" to "structural forcing function for causal-consequence modeling." The reframe does not retract prior approvals — the eight layers, the three orthogonal pairs (L2+L3, L4+L6, L5+L7), the < 100 ms hot-path ceiling, and the 10% → 5% sample-rate schedule all stand. It adds two architectural pillars (Cognitive Blueprints, Append-Only Hash Chain), renames the subject of the architecture, absorbs the BYOS / skill-agnostic stance into the preamble, and expands the CP plan from 6 to 8 to absorb the new work without breaking the one-commit-per-CP discipline.

The six prior decisions carry forward unchanged:

1. **Layer 3 entity extraction → REGEX.** No LLM in the hot path. Regex is FP-averse and predictable; an LLM extractor introduces its own Goodhart surface and breaks the < 100 ms hot-path budget.
2. **Layer 4 required-for-highest-impact list.** `terraform apply`, `kubectl apply` against any context matching `prod`/`production`, `alembic upgrade`, `prisma migrate deploy`, `gh release create`. Advisory at v1.0.0-rc1, required at v1.0.1.
3. **Layer 6 storage and TTL.** `~/.episteme/state/pending_contracts.jsonl` with TTL = max declared window across open contracts. Cleanup at SessionStart.
4. **Layer 8 sample rate.** 10% for the first 30 days (calendar-from-install), then decay to 5%. Per-project override via `.episteme/spot_check_rate`.
5. **Hot-path latency.** Layers 2–4 combined < 100 ms p95 (HARD ceiling). Per-layer 50 ms p95 breach gates behind a `derived_knobs.json` toggle. Repeated breach is a governance event — name it, do not silently tune.
6. **Phase 12 + hot-path coexistence.** Both layers ship and run together. Retrospective distribution signal is structurally different from per-surface write-time signal.

Implementation proceeds against this reframed spec. Any deviation surfaces as a spec-amendment request before code lands. Per the Phase 12 discipline: any later change that relaxes a load-bearing countermeasure — the eight layers, the three orthogonal pairs, the < 100 ms ceiling, the sample-rate schedule, **the Cognitive Blueprint registry, the hash-chain scope**, the BYOS stance — is a governance change, not an implementation tweak.

**Implementation timing.** v1.0 RC code work begins in a future session — NOT today. Today closes 0.11.0 (CHANGELOG, version reconcile, MANIFEST — all already landed in commit `a78c73e`); v0.11.0 then soaks before the v1.0 RC cycle opens.

## Why this exists

An LLM is an auto-regressive pattern engine. It does not predict the consequences of its actions; it predicts the next token of a plausible-sounding plan. When two sources disagree, it defaults to the statistically-central answer — the Doxa — and presents it with the same fluency it presents a verified fact. Any agentic system built on this substrate inherits the failure: the agent cannot plan because it cannot model what its action will cause.

Every visible failure mode this kernel addresses — fluent-vacuous reasoning, hallucinated dependency resolutions, confidently-wrong irreversible ops, retroactive memory distortion — is a surface expression of that single root cause. v0.11.0's hot-path validator (`core/hooks/reasoning_surface_guard.py`) catches the most trivial expression (lazy-token blocklist + 15-character minimum + regex pattern matching). It does not catch the underlying incapacity.

A sufficiently-aware agent defeats v0.11.0's gate with fluent-vacuous content that contains no banned tokens, exceeds the length threshold, looks like a falsifiable hypothesis, and commits to nothing testable. Five real examples that pass today's gate:

1. *"if any unforeseen issue arises during deployment we will reassess our approach"*
2. *"the migration may produce unexpected behavior if edge cases are encountered"*
3. *"if the build process exhibits anomalous behavior we should investigate before proceeding"*
4. *"should monitoring detect concerning patterns we will pause and evaluate next steps"*
5. *"if results diverge from expectations we will return to first principles"*

Each is over 60 characters, contains no banned tokens, has an `if`/`should`-clause, and looks like reasoning. None names an observable. None commits to a threshold. None could be falsified by a specific event. The kernel passes them. The operator's praxis fails them — but the diagnostic misnames the disease. The fluency is not the problem. The absence of a causal-consequence model behind the fluency is the problem.

**What this spec is.** The Reasoning Surface is not a guardrail against bad output. It is the structural interface through which the kernel forces the agent to construct an auditable causal model of a specific action — decomposed along the known failure structure of that action's class — *before* the action is permitted. The eight-layer architecture is the mechanical scaffold of causal reasoning, grafted onto an engine that cannot perform it natively.

**The honest epistemic claim.** The scaffold does not make an LLM capable of causal reasoning. It makes it cheaper for the agent to perform genuine decomposition than to fake decomposition at the granularity the scaffold requires. Every layer is evaluated against that claim — not against a cheating-impossible claim. There is no uncheatable protocol. There is a protocol whose cheat-cost exceeds its honesty-cost by a factor that widens the more scaffolding is in place.

Phase 12 catches some of this retrospectively — Axis A's S2 fire-condition classifier flags the vapor pattern. But the audit fires after the action lands. The hot path is still where the causal model must be constructed. v1.0 RC is the upgrade that makes that construction mandatory, protocol-specific, and tamper-evident.

## What episteme is — and what it is not

**episteme is a cognitive and execution governance kernel. It is not a skill provider, tool provider, or agent framework.** The kernel does not give agents capabilities; it intercepts state mutation at the point of action and enforces the Reasoning Surface regardless of which external tool, MCP server, or agent framework generated the command. A `kubectl apply` from Claude Code, a `terraform plan` from a Cursor agent, a `gh pr merge` from a home-grown MCP server — the kernel does not care about provenance. It intercepts the mutation and enforces the blueprint-shaped cognitive contract before the mutation lands.

This is the **BYOS (bring-your-own-skill) stance.** The ecosystem produces skills and tools at an accelerating pace; the kernel deliberately does not compete on that axis. It owns a narrower and structurally deeper surface: the moment at which a proposed action meets reality. Whatever the tool, whatever the prompt chain, whatever the model — state mutation passes through the Reasoning Surface, or it is refused.

Two consequences of this stance the rest of the spec depends on:

- **No tool-specific code paths in validation logic.** Layers 2 through 8 operate on the surface + the pending op, not on the tool that produced them. A new skill provider integrates by having its tool calls intercepted; no adapter work is required on the kernel side.
- **No prescriptive "how to use tool X" guidance in the blueprints.** Blueprints specify required causal decomposition ("what would break if this constraint is removed?"), not tool-specific invocation patterns. An agent using `sed` and an agent using an LSP-aware refactor tool satisfy the same blueprint differently — both must satisfy it.

The kernel provides the episteme. The ecosystem provides the skills.

## Core question

*What structural protocol, when enforced at the point of state mutation, forces an LLM to generate an auditable causal-consequence model — one specific enough to be retrospectively falsified and tamper-evident after the fact — before it is allowed to proceed?*

Three sub-questions:

1. **Protocol specificity.** Is a single generic surface schema sufficient, or does the protocol need to mutate its required fields based on the causal structure of the scenario?
2. **Memory integrity.** How does the kernel know its own retrospective record is honest, given that the agent has filesystem access to the state directory?
3. **Cost discipline.** What ships in v1.0 RC at acceptable hot-path latency / compute / false-positive cost, and what defers to v1.0.x or v1.1?

## The Goodhart threat, applied to the scaffold itself

Phase 12 named Goodhart at the *audit* level. The prior v1.0 RC framing named it at the *validator* level. The reframed thesis makes the threat more legible: any fixed decomposition protocol, once known, is a target the agent can optimize for. A sufficiently-exposed blueprint becomes a form to fill rather than a model to build.

**There is no single uncheatable protocol within the current paradigm.** The defense is the composition — multiple scaffolds whose evasion strategies are mutually inconsistent, plus an integrity layer (hash chain) that makes retroactive cheat-covering detectable, plus an operator ground-truth layer (spot-check) that cannot be predicted away.

This is the spiderweb metaphor working as intended. A single thread snaps; a web holds.

## Architecture — scaffold-in-depth across orthogonal gaming costs

Eight scaffolding layers, designed so evasion strategies in adjacent layers conflict. v1.0 RC ships layers 1–4 + 6 + 8; layers 5 and 7 defer to v1.1 on infrastructure-cost grounds.

```
                      ┌─── HOT PATH (state-mutation intercept, blocking) ───┐
  Layer 1  syntactic blocklist + length          [SHIPS — current]
  Layer 2  structural specificity classifier     [SHIPS v1.0 RC — blueprint-aware]
  Layer 3  contextual grounding (project-real entities)  [SHIPS v1.0 RC — blueprint-aware entity set]
  Layer 4  falsification trace (executable verification) [SHIPS v1.0 RC — blueprint-shaped]
  Layer 5  embedding-based vapor scoring          [DEFERRED v1.1 — infra cost]
                      └─── RETROSPECTIVE / async ─┘
  Layer 6  time-bound disconfirmation contract    [SHIPS v1.0 RC — extends Phase 12; hash-chained]
  Layer 7  adversarial co-validator (second LLM)  [DEFERRED v1.1 — compute cost]
  Layer 8  operator spot-check sampling           [SHIPS v1.0 RC — blueprint-prioritized]
```

Two cross-cutting pillars sit above the layer stack and change what the layers validate:

- **Cognitive Blueprints** — scenario-polymorphic surface schemas. Selected at the hot-path entry; shape the required fields in Layers 2 / 3 / 4 / 6 / 8.
- **Append-Only Hash Chain** — tamper-evident episodic record. Binds Layer 4's write-time prediction to Layer 6's retrospective audit.

The layers composed alone defend against evasion. The pillars composed with the layers shift what "the layers are validating" from *surface shape* to *causal decomposition along a known failure structure, preserved against retroactive mutation*.

## Pillar 1 · Cognitive Blueprints — scenario-polymorphic protocols

A surface with correctly-populated fields is not equivalent to a surface that carries causal-consequence prediction. v0.11.0's validator treats them as equivalent. v1.0 RC refuses to.

**The mechanism.** The Reasoning Surface schema becomes scenario-polymorphic. The generic four-field surface (`knowns`, `unknowns`, `assumptions`, `disconfirmation`) is the fallback. When a named scenario fires, the schema mutates to a **Cognitive Blueprint** whose fields are the causal decomposition specific to that scenario's known failure class. Layers 2, 3, 4, 6, and 8 validate against the blueprint's fields when one is selected; against the generic fields when none is.

**Selection logic.** A new component — `core/hooks/_scenario_detector.py` — runs at the top of the hot path (regex + entity triggers; budget: absorbed into Layer 2's 5 ms slot). It maps `(pending_op, surface_text, project_context)` to at most one blueprint. If none fires, the generic schema applies — zero regression for existing surfaces.

### Blueprint A · Axiomatic Judgment

*Scenario: conflicting-source resolution. Source A says X, Source B says Y; the agent must pick.*

Required fields:

- `sources[]` with per-source `believability_weight` and rationale (demonstrated track record, not authority or fluency — the rationale must name an observable from the source's history)
- `conflict_axis` — what specifically disagrees (not "they conflict" but, e.g., "A claims the migration is reversible; B claims it is not")
- `decision_rule` — the named axiom being applied (e.g., "prefer reversible; prefer the source with recent-incident evidence over the source with theoretical completeness")
- `fail_condition_per_source` — the observable that would retroactively invalidate each source
- `fallback_if_both_wrong` — the irreversibility-bounded path if the decision rule produces a wrong answer

Hooks to Phase 12 Axis A (disconfirmation specificity) and the believability-weighting rule named in `COGNITIVE_SYSTEM_PLAYBOOK.md` §3 (Dalio, Radical Transparency).

### Blueprint B · Fence Reconstruction

*Scenario: removal or relaxation of an unexplained constraint. Maps to `fence_discipline` axis (operator profile: value 4, confidence inferred).*

Required fields:

- `constraint_identified` — pointer to the specific code / config / policy being removed (line-level precision)
- `origin_evidence` — git blame, doc reference, or incident record establishing **why** the constraint was imposed (not "unclear — probably legacy")
- `removal_consequence_prediction` — what breaks if the constraint is removed, named with an observable
- `reversibility_classification` — reversible (continue), irreversible (stop; escalate to Axiomatic Judgment blueprint)
- `rollback_path` — the concrete revert procedure if the prediction is wrong

Hooks to Phase 12 Axis C (fence_discipline). This is the first realized blueprint in v1.0 RC because it binds cleanly to an axis the kernel already enforces retrospectively — end-to-end example from scenario to selector to blueprint to validation to hash-chained record to Phase 12 audit.

### Blueprint C · Consequence Chain

*Scenario: irreversible or high-blast-radius operation — `terraform apply` against prod, `kubectl apply` against prod, `alembic upgrade`, `prisma migrate deploy`, `gh release create`.*

Required fields:

- `first_order_effect` with observable
- `second_order_effect` — what happens downstream of the immediate effect; named, not hand-waved
- `failure_mode_inversion` — what would cause this to fail; at least one named mode per consequence tier
- `base_rate_reference` — historical distribution of this op-class in this project (or in the operator's broader experience if project-local data is sparse)
- `margin_of_safety` — buffer if assumptions slip 30–50%; explicit statement of what becomes unacceptable at that slip

Hooks to the mental-model lattice in `COGNITIVE_SYSTEM_PLAYBOOK.md` §3 (Munger: inversion, second-order, base rates, margin of safety).

### Blueprint D · Unclassified High-Impact (catchall)

*Scenario: state-mutation op whose impact classification is "high" but whose shape matches no named blueprint.*

Required fields: the union of Consequence Chain's fields, minus any not applicable to the op-shape. This is the Goodhart-closer for blueprint-absence evasion — an agent cannot avoid blueprint enforcement by producing actions that don't match any named pattern.

### Blueprint registry governance

Blueprints live at `core/blueprints/*.yaml` (one file per blueprint). Additions require a governance event with the same discipline as profile-axis changes: named failure class, audit evidence justifying the decomposition, operator sign-off. Phase 12 audits blueprint effectiveness quarterly — which blueprints fired, how often, with what retrospective-verification rate. Blueprints with sustained low bind-rate or low verification-rate are candidates for revision or retirement.

v1.0 RC ships four blueprints: three realized (Axiomatic Judgment structure + Fence Reconstruction full implementation + Consequence Chain structure) and one catchall (Unclassified High-Impact). Full realization of Axiomatic Judgment and Consequence Chain lands in v1.0.1 with audit data justifying their final field shapes.

### How this reshapes the existing layers

| Layer | Pre-reframe behavior | Post-reframe behavior |
|---|---|---|
| L2 | Generic trigger+observable specificity | Required observables are the blueprint's fields; generic classifier applies only under fallback |
| L3 | Grep entities named in surface | Grep entities the **blueprint** names (Fence Reconstruction grounds `constraint_identified` to a real file; Consequence Chain grounds `base_rate_reference`) |
| L4 | Optional `verification_trace` | Blueprint-shaped — Consequence Chain requires verification per consequence tier; Axiomatic Judgment requires per-source check |
| L6 | Time-bound contract checker | Blueprint declares which fields are verifiable and in what window; hash-chained (pillar 2) |
| L8 | Random spot-check | Blueprint-fired surfaces sampled at a higher rate — operator calibration signal lands where the cognitive claim is largest |

### Risks named honestly

- **Blueprint proliferation.** Three realized + one catchall is the budget. Governance-gated additions only. Quarterly Phase 12 review for retirement candidates.
- **Selector Goodhart.** An agent learning which inputs trigger the hardest blueprint will shape input to avoid it. Mitigations: the Unclassified High-Impact catchall; operator spot-check includes a sample of scenario-selection outcomes; Phase 12 audits selection distribution drift.
- **Blueprint authoring cost.** Blueprints are grown from Phase 12 audit data, not imposed generically. v1.0 RC ships the three named above because each maps cleanly to a failure mode the kernel already names.

## Pillar 2 · Append-Only Hash Chain — episodic integrity

Layer 6's current design records pending contracts to `~/.episteme/state/pending_contracts.jsonl`. The file is mutable. An agent (or anyone with write access to the state directory) can edit past records to retroactively look like it predicted outcomes it actually missed. The prior honest-threat-model did not name this class. This pillar closes it.

**Mechanism.** Every episodic-tier record and every pending-contract record carries:

- `prev_hash` — SHA-256 of the previous entry's full serialized content
- `entry_hash` — SHA-256 of this entry's content (including `prev_hash`)
- Chain-head at `~/.episteme/state/chain_head.json`. In git-tracked projects, chain-head rotation commits provide a second tamper-evidence layer.

**Scope — v1.0 RC.** Episodic tier + pending contracts only. Explicitly out of scope: `derived_knobs.json` mutations, profile-axis changes, global memory files. The kernel proves the mechanism at the lowest-blast-radius surface first; expansion is a later governance decision.

**Properties this gives:**

- Retroactive mutation detected. Any edit breaks the chain downstream.
- Phase 12 audit gains a **precondition**: chain verifies, or audit refuses to proceed on the tampered range.
- L4 → L6 composition strengthens measurably. A faked `verification_trace` cannot be quietly repaired later — the original record's hash is frozen into its successor.

**Chain-reset protocol.** Legitimate state loss is real (disk failure, workstation rebuild). The kernel distinguishes:

- *Chain absent* (no `chain_head.json` or zero-entry log) — new install or legitimate reset. Genesis proceeds cleanly.
- *Chain broken* (hash mismatch mid-chain) — governance event. Operator is notified at SessionStart; audit refuses to proceed on the broken range until the operator issues a signed `chain_reset` event (itself chained into the new genesis).

**Hash choice.** SHA-256. The kernel is not defending against computational adversaries; it is defending against trivial tampering. Schema is versioned so a later upgrade to SHA-3 is a format bump, not a rewrite.

**Cost.** ~0.1 ms per hash. Writes happen async to the state dir (same as L6 today). Zero hot-path impact.

## Per-layer proposal

Each layer has the same five fields:

- **What it checks** — the validation contract.
- **How it works** — the implementation sketch.
- **How an agent evades it** — honest threat model (no layer is uncheatable).
- **Composition cost** — what evading this layer also requires from adjacent layers.
- **Cost / scope** — hot-path latency, false-positive risk, ship-window.

Where the layer is blueprint-aware, the blueprint's fields are what the layer validates; generic fallback applies when no blueprint fires.

---

### Layer 1 · syntactic blocklist + length (CURRENT, stays)

**What it checks.** `disconfirmation` and each `unknowns` entry must be ≥ 15 characters and must not contain any token from the lazy-token blocklist (`none`, `n/a`, `tbd`, `nothing`, `null`, `unknown`, `해당 없음`, `해당없음`, `없음`, `모름`, `-`, `--`, `...`).

**How it works.** Module-level regex set in `core/hooks/reasoning_surface_guard.py::_surface_missing_fields`. Length threshold modulated by `derived_knobs.json::disconfirmation_specificity_min` (Phase 9 wiring) — for the maintainer's v2 profile, 15 → 27.

**How an agent evades it.** Trivial. Produce content > the threshold without any banned token. Every fluent-vacuous example above passes.

**Composition cost.** None — this is the floor. An agent that fails Layer 1 has not even tried.

**Cost / scope.** ~0.1 ms per call. Zero false positives in well-tested operator profiles. Ships today.

---

### Layer 2 · structural specificity classifier (blueprint-aware)

**What it checks.** When a blueprint is selected, the blueprint's required fields must each satisfy the classifier: a conditional trigger (`if`/`when`/`should`/`once`/`after`/`unless`) AND a specific observable (numeric threshold, metric name, failure verb, log/dashboard reference). When no blueprint fires, the generic surface's `disconfirmation` and `unknowns` entries are classified against the same contract.

**How it works.** Extract `_classify_disconfirmation` from `src/episteme/_profile_audit.py` (Axis A S2 in Phase 12 CP3) into `core/hooks/_specificity.py` so the hot path can reuse it. The classifier is called per-field per-blueprint. Reject in PreToolUse when any required field classifies as `tautological`, `absence`, or `unknown` — with `absence` allowed to pass with a stderr advisory on non-critical fields.

**How an agent evades it.** Learn the trigger + observable vocabulary and pad it into blueprint fields. Example: *"if the metric exceeds the threshold within the time window, abort"* — has all three required elements, passes Layer 2, names nothing concrete. Layer 3 catches this via blueprint-scoped entity grounding.

**Composition cost.** An agent that evades Layer 2 by producing trigger + observable vocabulary is forced toward MORE specific language, which raises surface area for Layer 3 (blueprint entity grounding) and Layer 5 (vapor scoring). Evading Layer 2 *helps* Layer 3 catch you.

**Cost / scope.** ~5 ms (regex set against 1–2 KB of surface text) including the scenario-detector that shares this budget. Estimated FP rate < 5% on well-formed surfaces. Ships v1.0 RC.

---

### Layer 3 · contextual grounding (blueprint-aware entity set)

**What it checks.** Entities named in the surface must EXIST in the project. When a blueprint fires, the entities checked are the blueprint's named entities — Fence Reconstruction must ground `constraint_identified` (real file, real line); Consequence Chain must ground `base_rate_reference` (real incident record, real telemetry query); Axiomatic Judgment must ground each `sources[].rationale` observable.

**How it works.** Best-effort grep of the project working tree. Entity extraction is regex-based (not LLM): numeric units, snake_case identifiers, file paths, environment variables, service names, git-object references. For each, check `git ls-files | xargs grep -l`. Failure to ground is a *warning* when project context is sparse; the gate fires only when ≥ 2 grounded entities are found AND the named-but-not-found ratio exceeds 50%. Fresh repos emit no false positives.

**How an agent evades it.** Either (a) reference the project's real entities honestly, or (b) introduce real entities that match its claim (write a fake test, add a fake metric). Path (a) is the honest path — the cognitive work happened. Path (b) is detectable by the stateful interceptor (v0.10) AND by Layer 8.

**Composition cost.** Evading Layer 3 dishonestly leaves at least two traceable artifacts. Evading Layer 3 honestly IS the goal.

**Cost / scope.** ~50 ms cold cache; ~5 ms warm. FP-averse gating. Ships v1.0 RC.

---

### Layer 4 · falsification-trace requirement (blueprint-shaped)

**What it checks.** The Reasoning Surface schema gains `verification_trace`. When a blueprint is active, the trace shape is blueprint-specific. Generic shape:

```json
{
  "verification_trace": {
    "command": "kubectl logs -n prod canary | grep 'p95.*latency' | tail -100",
    "or_dashboard": "https://grafana.internal/d/api-latency",
    "or_test": "tests/test_canary.py::test_p95_under_threshold",
    "window_seconds": 600,
    "threshold_observable": "p95 > 400"
  }
}
```

Blueprint-specific shapes:

- **Consequence Chain** — one verification per consequence tier (first-order, second-order, failure-mode). Separate windows allowed.
- **Axiomatic Judgment** — one verification per source's `fail_condition`. Validates the source's believability-weight against an observable.
- **Fence Reconstruction** — verification is the `rollback_path` executed as a smoke test in a reversible context (not against prod).

When `verification_trace` is present, the validator parses it and checks that at least one of `command` / `or_dashboard` / `or_test` is non-empty AND specific (executable, parseable URL, or test-id format). When absent on a high-impact op, stderr advisory ("recommend declaring verification_trace") without block — backward compatibility for v0.11.0 surfaces.

By v1.0.1, `verification_trace` becomes required for the highest-impact ops (`terraform apply`, `kubectl apply` against prod, db migrations).

**How an agent evades it.** Write a fake command. The hot path can't run it at write time (side effect). Layer 6 (time-bound contract, hash-chained) checks whether the named command was actually run within the declared window. Write-time vapor becomes audit-time failure.

**Composition cost.** Faking `verification_trace` at Layer 4 commits the agent to a Layer 6 violation — the named command must show up in the agent's bash history within the declared window, or the surface is retrospectively invalidated. The pillar-2 hash chain makes retroactive repair impossible.

**Cost / scope.** ~1 ms parse + structural check. Non-breaking additive schema. Ships v1.0 RC.

---

### Layer 5 · embedding-based vapor scoring (DEFERRED v1.1)

**What it checks.** Each surface field is embedded by a small local model. The embedding is compared to a corpus of known-good surfaces and known-bad surfaces. Surfaces whose embeddings fall outside the known-good distribution by > N sigma are flagged.

**How it works.** Bundle a small sentence-transformer model (`all-MiniLM-L6-v2` or similar, ~80 MB) with the kernel; compute embedding for `core_question` + `disconfirmation` + concatenated `unknowns` (or the blueprint-specific equivalent fields); cosine-similarity against a known-good centroid; reject if score < threshold.

**How an agent evades it.** Produce embeddings near the centroid. Mitigation: the corpus *grows* with the operator's accepted surfaces over time — operator-specific centroid not knowable from public training data.

**Composition cost.** An agent whose surfaces pass Layer 5 by producing high specificity and varied vocabulary has done much of what Layers 2, 3, 4 wanted — Layer 5 is partially redundant with the lower layers, which is defense in depth working.

**Cost / scope.** ~200 ms per call. Adds ~80 MB to the install footprint. Defers to v1.1 unless an acceptable-cost embedding API path is found.

---

### Layer 6 · time-bound disconfirmation contract (hash-chained)

**What it checks.** When `verification_trace.window_seconds` is declared, the kernel records a *pending contract* in `~/.episteme/state/pending_contracts.jsonl` with the full blueprint surface snapshot. **Each record is chained** (pillar 2). After the window expires, an async checker (cron or SessionStart hook) verifies: was the named command executed (stateful interceptor records)? Did the named test run? Did the dashboard get viewed (browser-extension hook, optional)? If none of the verification methods fired, the surface is retrospectively tagged `disconfirmation_unverified` in the episodic tier (also hash-chained).

`disconfirmation_unverified` records feed Phase 12 — the audit counts unverified-rate per axis per blueprint and surfaces it as drift if it exceeds threshold. Phase 12 refuses to audit across a broken chain range.

**How an agent evades it.** Run the named command performatively (`echo "kubectl logs..." && true`). Mitigations: (a) Layer 6 checks for command + non-zero output + recency; an echoed command produces no real output; (b) cross-reference with project telemetry — if `kubectl logs` was named and actual logs were produced, real check fired; (c) the hash chain prevents retroactive "I actually did run it" edits after the window expires.

**Composition cost.** Layer 6 makes Layer 4 verifiable. Without Layer 6, Layer 4 is just another schema field. Together with the hash chain, they form a write-time-commit + audit-time-verify + tamper-evident contract.

**Cost / scope.** ~0 ms hot path (write pending contract record + one hash). Async check runs at SessionStart or via cron. Ships v1.0 RC as an extension to the Phase 12 audit pipeline.

---

### Layer 7 · adversarial co-validator (DEFERRED v1.1+)

**What it checks.** A second LLM (different model family — ideally a small open-weights model the operator runs locally) reads the surface and answers: *"if the agent that wrote this were trying to make it look good without actually thinking, how would they have written it? Show me a fluent-vacuous variant."* The adversarial variant is compared to the actual surface (via Layer 5's embedding similarity). Too-similar surfaces are rejected with the adversarial variant attached as evidence.

**How an agent evades it.** Produce a surface that doesn't pattern-match "trying to look good." This requires actually committing to a falsifiable hypothesis — exactly what the kernel wants.

**Composition cost.** Layer 7 is the strongest semantic gate but also the most expensive. Most useful in adversarial settings (CTF-like, security review). For day-to-day praxis, Layers 2 + 3 + 4 + 6 cover ~90% of evasion shapes at a fraction of the compute.

**Cost / scope.** ~2–5 seconds per call. $0.001–$0.01 per check. Defers to v1.1; possibly never default-enabled.

---

### Layer 8 · operator spot-check sampling (blueprint-prioritized)

**What it checks.** A configurable percentage of high-impact surfaces is flagged for explicit operator review even when they pass Layers 1–4. Default rate: 10% for the first 30 days from install (calendar-from-install), then decay to 5%. Blueprint-fired surfaces sampled at 2× the base rate — the operator's calibration signal lands where the cognitive claim is largest. Selection decisions (which blueprint fired for which op) are themselves spot-checked at a lower rate to cover selector-Goodhart.

Flagged surfaces queue to `~/.episteme/state/spot_check_queue.jsonl` (hash-chained). SessionStart presents them at the start of the next session ("3 surfaces flagged for review since last session — `episteme review`"). Operator verdicts (real / vapor / wrong-blueprint) train per-operator tuning over time.

**How an agent evades it.** Cannot. The operator is the ground truth. Sampling is random; the agent cannot predict which surfaces get reviewed.

**Composition cost.** Layer 8 is the calibration layer for all the others. Operator verdicts tune thresholds in Layers 2, 3, 5 and adjust blueprint bind-rates — making the system self-correcting against drift in either direction.

**Cost / scope.** ~0 ms hot path (queue write + hash). Operator burden: ~5% of high-impact surfaces × 30 seconds review = a few minutes per session for a maintainer doing ~10 high-impact ops/day. Ships v1.0 RC; sample rate configurable per-project.

## Why these layers compose well

The orthogonality test: for each pair of adjacent layers, can a single evasion strategy defeat both?

| Pair | Aligned strategy? | Mutually inconsistent? |
|---|---|---|
| L1 + L2 | Yes (verbose + has trigger+observable) | No |
| L2 + L3 | **No — verbose specific text is more grep-able for blueprint-named entities** | **Yes** ← orthogonality |
| L3 + L4 | Partial (real entities help, but L4 needs executable command) | Partial |
| L4 + L6 | **No — fake command at L4 produces L6 violation at audit time; hash chain closes retroactive repair** | **Yes** ← orthogonality |
| L5 + L7 | **No — embedding-near-centroid surfaces look like "trying to look good"** | **Yes** ← orthogonality |
| L6 + L8 | Mostly orthogonal (audit signal vs operator ground truth) | Mostly |
| Blueprint-selector + L8 (selection sample) | **No — an agent that games the selector gets sampled on its selection choice, not just its surface content** | **Yes** ← new orthogonality introduced by pillar 1 |

The three original orthogonal pairs (L2+L3, L4+L6, L5+L7) remain load-bearing. The reframe adds a fourth orthogonality axis (selector vs spot-check) that the pillar creates.

An agent that wants to evade everything has to:

- Select the hardest-to-fake blueprint for the action (defeats selector-Goodhart)
- Be specific (defeats L2)
- Reference real project entities per the blueprint's required grounding (defeats L3)
- Commit to executable verification per consequence tier (defeats L4)
- Actually execute the verification within the window (defeats L6)
- Not mutate the record afterwards to cover a miss (defeats the hash chain)
- Produce varied semantic content (defeats L5)
- Avoid pattern-matching "performance of specificity" (defeats L7)
- Hope it's not in the spot-check sample (defeats L8 statistically; ground-truth eventually catches if not this sample, the next)

By the time an agent does all of this, it has approximately performed the causal decomposition the kernel was trying to enforce. **That is the entire goal.** Not "make cheating impossible" — make cheating cost more than honesty, and make retroactive cheat-covering detectable.

## What ships in v1.0 RC

**Hot-path additions (block at PreToolUse):**

- Scenario detector + blueprint selector + blueprint registry scaffold (`core/blueprints/`).
- Layer 2 — structural specificity classifier, blueprint-aware (extracted from Phase 12 to `core/hooks/_specificity.py`).
- Layer 3 — contextual grounding, blueprint-aware entity set.
- Layer 4 — `verification_trace` schema field, blueprint-shaped (optional in v1.0; required for highest-impact ops in v1.0.1).
- Blueprint B — **Fence Reconstruction**, fully realized end-to-end (selector → blueprint → Layer 2/3/4 validation → hash-chained Layer 6 record → Phase 12 audit input).

**Async additions (retrospective):**

- Layer 6 — time-bound contract checker with append-only hash chain, plumbed into Phase 12's audit pipeline.
- Layer 8 — spot-check sampling + operator review CLI (`episteme review`), blueprint-prioritized.

**Stays as-is:**

- Layer 1 — current syntactic + length validator.

**Ships as structure only, full realization in v1.0.1:**

- Blueprints A (Axiomatic Judgment) and C (Consequence Chain) — schemas land in `core/blueprints/` and the selector can fire them, but field-level validation for these two blueprints is a stub returning advisory until v1.0.1 audit data justifies the final shapes.
- Blueprint D (Unclassified High-Impact catchall) — structure ships; fires for any high-impact op that doesn't match A/B/C.

**Deferred to v1.1:**

- Layer 5 — embedding-based vapor scoring (infra + footprint cost).
- Layer 7 — adversarial co-validator (compute cost + only useful in adversarial settings).

## Implementation sequencing

Eight commits, mirroring the Phase 12 checkpoint discipline. Each checkpoint pauses for review. Tests stay green at every commit.

1. **CP1 — extract `_specificity.py`.** Move `_classify_disconfirmation` from `src/episteme/_profile_audit.py` to `core/hooks/_specificity.py`. Phase 12 imports from the new module; behavior unchanged.
2. **CP2 — scenario detector + blueprint registry.** New `core/hooks/_scenario_detector.py`. New `core/blueprints/` directory with generic-fallback blueprint plus registry loader. No behavior change — detector always returns "generic" until CP5 wires Fence Reconstruction. Tests cover registry load + generic fallback.
3. **CP3 — Layer 2 in the hot path.** `reasoning_surface_guard.py` calls `_classify_disconfirmation` against the selected blueprint's fields (generic for now). Rejects on `tautological` / `unknown`; advisory on `absence`. New test class.
4. **CP4 — Layer 3 contextual grounding.** New `core/hooks/_grounding.py`. Blueprint-aware entity extraction + project grep. FP-averse gating. New test class.
5. **CP5 — Blueprint B (Fence Reconstruction), realized end-to-end.** Populate `core/blueprints/fence_reconstruction.yaml`; wire scenario detector to fire it on constraint-removal patterns (git-diff signature + lexicon hits); Layer 2 / 3 validation against its fields. This is the working end-to-end example the reframe demands. New test class covering scenario firing, blueprint selection, field validation, and fallback behavior.
6. **CP6 — Layer 4 verification_trace schema.** Update `core/schemas/reasoning-surface/...`; optional field; structural validation; blueprint-shaped variants for Fence Reconstruction. Advisory for highest-impact ops; required lands in v1.0.1. Schemas for Axiomatic Judgment and Consequence Chain land as stubs; their blueprint validation is advisory-only at RC.
7. **CP7 — Layer 6 time-bound contract + hash chain.** New `core/hooks/_pending_contracts.py` with chain implementation. Write at PreToolUse when `verification_trace` declared; check at SessionStart; tag `disconfirmation_unverified`. Phase 12 audit input gains chain-verification precondition. New test class covering chain integrity, chain-absent genesis, chain-broken governance event, and chain-reset protocol.
8. **CP8 — Layer 8 spot-check sampling.** Configurable rate (default 10% → 5%) at PreToolUse; blueprint-fired surfaces sampled at 2× base; queue to `spot_check_queue.jsonl` (hash-chained); new `episteme review` CLI; SessionStart surface. Operator verdicts training into per-operator tuning is scoped out of CP8 — lands in v1.0.1.

## Honest threat model — what STILL evades after v1.0

Per Phase 12's discipline of naming what the system does NOT cover:

1. **Coordinated multi-call evasion.** An agent splits a high-impact op into many low-impact ops, each with bare-minimum surfaces, evading the high-impact gate per call. Mitigation: stateful interceptor (v0.10) catches some; Layer 6 retrospective audit can detect patterns. Truly mitigating requires session-level surface aggregation — out of v1.0 RC scope.

2. **Operator collusion.** If the operator stops doing real spot-checks (Layer 8) and rubber-stamps everything, the calibration loop poisons. The operator is the ground truth; there is no recourse if ground truth is corrupted. This is by design.

3. **Adversarial-trained agent.** An agent specifically trained on bypassing episteme's validators is a different threat class. Mitigation: Layer 7 (deferred). Full defense requires a closed-system runtime or a different threat model entirely.

4. **High-volume noise drowning the signal.** An agent producing 10× the normal surface volume saturates Layer 8's sample budget and Phase 12's audit windows. Mitigation: Layer 6 records contracts independently; spot-check rate scales with volume. Not a hard solve.

5. **Semantic Goodhart on Layer 5 / Layer 7.** Once the embedding model or adversarial co-validator is known, the agent can be fine-tuned against it. Mitigation: rotate the embedding model on each kernel release; never publish the adversarial co-validator's weights. Ongoing arms race; the kernel cannot win it permanently, only stay ahead.

6. **Memory poisoning via retroactive state mutation.** *[Closed by pillar 2 — hash chain.]* An agent edits `~/.episteme/state/*.jsonl` to look like it predicted outcomes it actually missed. Chain verification breaks on any such edit; Phase 12 refuses to audit across broken ranges.

7. **Blueprint-absence evasion.** An agent produces actions that don't match any named blueprint so validation falls to generic schema. *[Closed by Blueprint D — Unclassified High-Impact catchall.]* Any op classified as high-impact receives max-rigor fields by default.

8. **Blueprint-selector gaming.** An agent learns which inputs trigger the hardest blueprint and shapes input to avoid it. Partially closed by Layer 8 sampling a percentage of selection outcomes, and by Phase 12 auditing selection distribution drift over time. New Goodhart surface introduced knowingly by pillar 1.

9. **Offline chain attack.** An adversary with FS access edits the chain *and* the chain-head atomically — a coordinated rewrite. Mitigation outside v1.0 RC scope: cryptographic signing of chain-head rotations. For v1.0 RC, chain-head committed to git in git-tracked projects provides second-layer evidence; accepting that non-git workflows remain vulnerable to this specific attack.

This section is load-bearing. Any later change to v1.0 RC scope that claims to close one of these without explicit mitigation is a governance change, not an implementation tweak.

## Non-goals

- **Provably uncheatable validation.** Out of scope. The honest claim is "evasion costs more than honesty, and retroactive cheat-covering is detectable," not "evasion is impossible."
- **Real-time LLM-based validation in the hot path.** Latency cost too high for v1.0 RC. Layer 7 is async-only.
- **Operator profile mutations from spot-check verdicts.** Verdicts inform threshold tuning per project, never auto-edit the global operator profile.
- **Replacing Phase 12.** v1.0 RC extends the retrospective loop; it does not substitute for it. Both ship and run together.
- **Cross-operator validation.** Multi-operator coordination is on the deferred multi-operator roadmap; v1.0 RC stays single-operator like v0.11.0.
- **Providing tools, skills, or agent capabilities.** *[BYOS constraint.]* The kernel intercepts state mutation regardless of source. It does not ship tools, skill libraries, MCP servers, or agent frameworks. Skill provision is the ecosystem's concern; cognitive and execution governance is the kernel's.
- **Tool-specific validation code paths.** Layers 2–8 operate on the surface + pending op, never on the tool that produced them. A new skill provider integrates transparently.
- **Expanding the hash chain to `derived_knobs.json` or profile-axis changes.** Explicitly out of scope for v1.0 RC. Chain scope is episodic tier + pending contracts only; expansion is a later governance decision after the core mechanism is proven.

## Verification — v1.0 RC is "done" when

- All eight checkpoints land with paused-review-before-commit discipline.
- Test suite stays green at every commit (304 today; CP1 holds; CP2–CP8 each add ~15–25 tests).
- Hot-path latency profile shows p95 < 100 ms added by Layers 2–4 + scenario detector combined.
- Five fluent-vacuous evasion examples from "Why this exists" are now blocked at write time by some combination of Layers 2–4 + Fence Reconstruction blueprint where applicable.
- End-to-end dogfood on a real constraint-removal op fires Fence Reconstruction, produces a blueprint-populated surface, writes a hash-chained record, and is available to Phase 12 audit input. If this end-to-end example does not work, CP5 failed regardless of what the tests show.
- Phase 12 audit dogfood shows `disconfirmation_unverified` rate < 10% on the maintainer's tier after 30 days of Layer 6 active. Above 10% means the kernel is enforcing contracts the operator isn't honoring — either tighten the operator's discipline or relax the contract; the audit surfaces the gap.
- Chain verification succeeds across the full RC soak window. Any chain-broken event during the soak is investigated and root-caused before GA.
- Layer 8 spot-check delivers ≥ 1 actionable operator verdict per week of normal use over the RC soak. Below this, sample rate is too low; above 5/week, sample rate is too high (operator burden).
- This document remains `approved (reframed)` through RC; any further philosophical shift is a new spec amendment.

## What this spec does NOT cover

- Implementation-level code (function bodies, exact regex patterns, full test fixtures). Those emerge during the checkpoint sequence, traceable back to this spec.
- Final field shapes for Blueprints A (Axiomatic Judgment) and C (Consequence Chain). Structure ships in RC; full realization in v1.0.1 with audit data.
- The Layer 5 corpus assembly (which surfaces count as known-good?). Deferred along with Layer 5 itself.
- The Layer 7 adversarial-co-validator model choice. Deferred along with Layer 7.
- Hash-chain signing for chain-head rotations. v1.0 RC uses plain SHA-256 chaining + optional git co-commit. Cryptographic signing is a post-GA hardening step.
- Performance optimization beyond the worst-case latency budget. Out-of-scope until profile data exists.
- v1.0 GA scope. v1.0 RC is the gate; GA is `v1.0.0` after the soak window confirms the engineering AND cognitive-adoption gates.

---

## Review checklist for the maintainer

Before considering this spec fully settled:

1. The reframed thesis — "structural forcing function for causal-consequence modeling, grafted onto an engine that cannot perform one natively" — is the correct level of claim. If "grafting a causal world model" overclaims, name the weaker version you'd prefer before implementation.
2. The BYOS stance is absorbed correctly in the preamble — episteme intercepts, does not provide. If a future skill-adjacent feature is proposed, it's a governance event.
3. The four blueprints (A Axiomatic Judgment, B Fence Reconstruction, C Consequence Chain, D Unclassified catchall) are the right starting set. Additions are governance-gated.
4. Fence Reconstruction is the right end-to-end example for RC because it binds to an existing audit axis. If another blueprint would give a stronger end-to-end demonstration, name it before CP5.
5. The hash-chain scope (episodic tier + pending contracts only) is correctly bounded. Expansion to `derived_knobs.json` or profile-axis changes is a later governance decision, not a scope creep.
6. The eight v1.0 RC checkpoints are sized at one logical commit each. If any feels too large, it gets split before implementation.
7. The honest threat model names every evasion class you can think of after reading. New ones join the list rather than being silently countered.
8. The "make cheating cost more than honesty, and make retroactive cheat-covering detectable" framing is correct. If you believe an uncheatable protocol is achievable within v1.0 RC scope, this spec needs to be rebuilt around that claim.

Once these are settled, implementation begins as v1.0.0-rc1 work after 0.11.0 soak + tag.
