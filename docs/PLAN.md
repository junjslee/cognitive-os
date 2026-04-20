# Plan

Current active plan for episteme development.

**Core Question (this cycle):** Now that identity migration (cognitive-os → episteme) is closed, which kernel-limits gap do we close next to increase the kernel's enforceable scope?

**Constraint regime:**
- Allowed: augmenting kernel docs, README, issue templates, ops docs, schema additions that extend (not reframe) existing invariants
- Forbidden: modifying `templates/` or `labs/` scaffolds; breaking kernel invariants without Evolution Contract
- Kernel changes require `kernel/CHANGELOG.md` entry first

---

## Closed milestones

### 0.8.1 — Strict-by-default enforcement — complete
- Flipped `reasoning_surface_guard.py` default from advisory to strict (blocking).
- Added semantic validator: lazy-token blocklist (`none`, `n/a`, `tbd`, `해당 없음`, `없음`, ...) + min-length thresholds (≥ 15 chars on disconfirmation and each unknown).
- Added command-text normalization to catch bypass shapes (`subprocess.run(['git','push'])`, `os.system('git push')`, `sh -c 'npm publish'`).
- `episteme inject` now writes `advisory-surface` marker only under `--no-strict`; strict is the default no-op.
- Block-mode stderr leads with `"Execution blocked by Episteme Strict Mode. Missing or invalid Reasoning Surface."`
- Test coverage expanded to 17 cases (strict defaults, lazy-token rejection, short-string rejection, 3 bypass vectors).
- See `kernel/CHANGELOG.md` 0.8.1 entry and `docs/PROGRESS.md` 0.8.1 block.

### 0.8.0 — Identity migration (cognitive-os → episteme) — complete
- Python package, runtime dir, env vars, GitHub repo, plugin/marketplace manifests, `pyproject.toml` all aligned to `episteme`.
- Dynamic Python runtime (no hard Conda dependency).
- `v0.8.0` tagged and pushed; marketplace install verified end-to-end.
- See `kernel/CHANGELOG.md` 0.8.0 entry and `docs/PROGRESS.md` 0.8.0 block.

### 0.7.0 — Real enforcement — complete
- Audit log, `episteme inject`, strict blocking.

### 0.6.0 — Epistemic control plane positioning — complete
- DbC + feedforward + OPA framing; README governance rewrite; ops docs seeded.

---

## Active milestone: 0.9.0 — Kernel-limits gap closure (proposed, not yet scoped)

### Goal
Close the two cheapest gaps in `kernel/KERNEL_LIMITS.md` that turn the kernel from advisory into self-observing.

### Candidate phases (priority order)

| Phase | Scope | Gap | Status |
|-------|-------|-----|--------|
| 1 | Calibration telemetry stub — append-only `decisions/*.md` log capturing predicted vs observed outcomes | A | not started |
| 2 | `last_elicited` timestamp field in operator profile schema + adapter prompt when stale | B | not started |
| 3 | Replace ASCII control-plane diagram in `README.md` with SVG asset | — | not started |
| 4 | `tacit-call` decision marker in Reasoning Surface schema | D | not started |
| 5 | Cynefin domain classification field in `reasoning-surface.json` | — | not started |

### Open assumptions
- Gap A (calibration) is cheaper than Gap C (multi-operator) and produces more immediate feedback signal — unverified against operator cost.
- SVG replacement is cosmetic but unblocks the README's legibility claim for enterprise readers.

---

## Deferred to later milestones

- Multi-operator mode (Gap C) — requires profile schema rework.
- Cross-runtime MCP proxy daemon (noted in 0.7.0 CHANGELOG rationale) — larger architectural bet; not scoped until calibration telemetry produces data worth proxying.
