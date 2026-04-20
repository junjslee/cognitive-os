# Next Steps

Exact next actions, in priority order. Update this file at every handoff.

---

## Immediate (0.9.0 entry)

1. **Scope phase 1 of 0.9.0** — calibration telemetry stub (Gap A): decide append-only file layout (`decisions/YYYY-MM-DD-slug.md`?) and minimum fields (predicted outcome, disconfirmation condition, observed outcome, delta).
2. **Replace ASCII control-plane diagram** in `README.md` with SVG. Concept already defined; asset production only.
3. **Add `last_elicited` timestamp** to operator profile schema (Gap B). Lowest-risk schema extension — additive field, no adapter break.
4. **Record a 30-second asciinema** of demo 03 showing strict-mode blocking `git push` until the Reasoning Surface is valid. Embed in README above the SVG. Closes the "show, don't tell" adoption gap identified in the 0.8.1 audit.

## Short-term (0.9.0 remainder)

- `tacit-call` decision marker in Reasoning Surface schema (Gap D)
- Cynefin domain classification field in `reasoning-surface.json` (companion to KERNEL_LIMITS.md addition)

## Medium-term (roadmap)

- Multi-operator mode design (Gap C) — deferred past 0.9.0; requires profile schema rework.
- Cross-runtime MCP proxy daemon — blocked on calibration telemetry data.

## New — architectural bypass vectors surfaced in 0.8.1 (deferred)

Discovered during Phase 3 opportunistic audit of `reasoning_surface_guard.py`. The guard now normalizes quote/bracket separators, which catches the most common bypasses (`subprocess.run(['git','push'])`, `os.system('git push')`, `sh -c '…'`). These remain open:

1. **Shell script files calling high-impact ops.** An agent that writes `./deploy.sh` where the script internally runs `git push` is not caught by a text-matching hook. A fix would require reading the target script before executing; that requires either filesystem-aware interception or an ahead-of-time script scanner. Out of scope for a hook-local patch.
2. **Write-then-execute patterns.** An agent writes `run.sh` via `Write`, then runs it via `Bash`. Individually, neither call is a high-impact pattern. Requires cross-call state persisted between `PreToolUse` invocations — not achievable in a stateless single-call hook. Candidate for 0.9.0+ if the cross-runtime MCP proxy daemon lands.
3. **Bash variable indirection.** `CMD="git push" && $CMD` is not caught; the normalizer handles separators, not substitution. Closing this would require a lightweight shell parser (risks correctness regressions) or a deny-by-default policy on `eval`/`$()`/backticks (breaks legitimate automation). Deferred pending cost/benefit review.
4. **Calibration telemetry still open (Gap A).** Without a feedback loop that records predicted vs. observed outcomes, episteme cannot *prove* its claims over time. This is the load-bearing gap for making the cognitive contract verifiable, not just enforceable. Keep as 0.9.0 phase 1 priority.

---

## Closed in 0.8.1
- **Strict mode is default.** Missing / stale / incomplete / lazy Reasoning Surface → exit 2 (block). Opt out per-project via `.episteme/advisory-surface`.
- **Semantic validator shipped.** Lazy-token blocklist + 15-char minimums on `disconfirmation` and each `unknowns` entry. `"disconfirmation": "None"` and `"해당 없음"` no longer pass.
- **Command normalization closes three bypass shapes.** `subprocess.run(['git','push'])`, `os.system('git push')`, `sh -c 'npm publish'` all trip the same regex patterns as bare shell.
- **Block-mode stderr upgraded.** `"Execution blocked by Episteme Strict Mode. Missing or invalid Reasoning Surface."` + concrete validator reasons + advisory-mode opt-out pointer.
- **`episteme inject` reworked.** Default is no-marker (strict is default); `--no-strict` writes `advisory-surface` explicitly.
- **Test coverage 9 → 17 cases** (all passing, full suite 68 passed).
- **README lede rewritten** — removed the "advisory by default" hedge; now reflects shipped reality.

## Closed in 0.8.0
- Remove compat symlink `/Users/junlee/cognitive-os`
- Verify `/plugin marketplace add junjslee/episteme` resolves (user confirmed in-session)
- Tag + push `v0.8.0`
- Reconcile `pyproject.toml`, `plugin.json`, `marketplace.json` versions
- Add `kernel/CHANGELOG.md` 0.8.0 entry
